import asyncio
import aiohttp
from bs4 import BeautifulSoup
from tabulate import tabulate
import os
import platform
import sys
import re
import datetime
from colorama import init, Cursor
init()
import json
if platform.system() == "Windows":
    import msvcrt

# 監視するマーケットアイテムIDと上限金額を指定
SEARCH_CONDITION_PATH = "search_conditions.json"
SETTINGS_PATH = "settings.json"

def ensure_settings():
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({"interval_sec": 5}, f, ensure_ascii=False, indent=2)

def load_settings():
    ensure_settings()
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"interval_sec": 5}

def ensure_search_conditions():
    if not os.path.exists(SEARCH_CONDITION_PATH):
        # デフォルト値で生成（新形式）
        with open(SEARCH_CONDITION_PATH, "w", encoding="utf-8") as f:
            json.dump({"3210037": {"price": 10000, "color": "red"}}, f, ensure_ascii=False, indent=2)

def load_search_conditions():
    ensure_search_conditions()
    try:
        with open(SEARCH_CONDITION_PATH, encoding="utf-8") as f:
            data = json.load(f)
            # 旧形式対応: intならpriceのみ
            for k, v in data.items():
                if isinstance(v, int):
                    data[k] = {"price": v, "color": "reset"}
            return data
    except Exception:
        return {}

def get_market_urls(search_conditions):
    return [f"https://bitjita.com/market/item/{item_id}?hasOrders=true" for item_id in search_conditions.keys()]


# CUI画面クリア関数
def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def hex_to_ansi256(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return '\033[0m'
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    # 256色変換
    ansi = 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)
    return f'\033[38;5;{ansi}m'

# 出品リストをグラフィカルに表示
def print_items(items, interval_sec, color_map=None):
    print(Cursor.POS(0, 0), end="")
    print("\n=== マーケット監視: 通知対象出品 ===")
    print(f"検索条件ファイル: {SEARCH_CONDITION_PATH}")
    print(f"設定ファイル: {SETTINGS_PATH}")
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"最終更新日時: {now}")
    ansi_colors = {
        "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m", "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m", "reset": "\033[0m"
    }
    if items and items[0][0] != "":
        headers = ["アイテム名", "価格", "数量", "場所"]
        # 色付け用にテーブルデータを加工
        colored_items = []
        for idx, row in enumerate(items):
            color_val = color_map[idx] if color_map and idx < len(color_map) else "reset"
            if re.match(r"^#[0-9A-Fa-f]{6}$", color_val):
                color = hex_to_ansi256(color_val)
            else:
                color = ansi_colors.get(color_val, "\033[0m")
            colored_row = list(row)
            colored_row[0] = color + str(row[0]) + ansi_colors["reset"]
            colored_items.append(colored_row)
        table = tabulate(colored_items, headers=headers, tablefmt="github", stralign="left", numalign="right")
        print(table)
    else:
        print("通知対象の出品はありません。")
    print(f"\n({interval_sec}秒ごとに自動更新)")
    print("R：　検索条件更新（ファイル再読込）")


async def scrape_market(interval_sec):
    search_conditions = load_search_conditions()
    async def fetch_and_parse(item_id, max_price, color, session):
        url = f"https://bitjita.com/market/item/{item_id}?hasOrders=true"
        try:
            async with session.get(url) as response:
                html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            notify_items = []
            sell_orders_header = soup.find(string=lambda t: t and 'Sell Orders' in t)
            if sell_orders_header:
                table = sell_orders_header.find_parent().find_next('table')
                if table:
                    for row in table.find_all('tr'):
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            import re
                            name = cols[0].get_text(strip=True)
                            # 先頭2文字が大文字でEssentialが含まれる場合は除去
                            if 'Essential' in name:
                                name = re.sub(r'^[A-Z]{2}', '', name)
                            quantity = cols[1].get_text(strip=True)
                            price_text = cols[2].get_text(strip=True)
                            location = cols[3].get_text(strip=True)
                            try:
                                price = int(price_text.replace('C', '').replace(',', '').strip())
                            except:
                                price = 0
                            if price <= int(max_price):
                                notify_items.append([name, price, quantity, location])
                else:
                    next_elem = sell_orders_header.find_parent().find_next_sibling()
                    found = False
                    while next_elem:
                        text = next_elem.get_text(" ", strip=True)
                        if "|" in text:
                            parts = [p.strip() for p in text.split("|")]
                            if len(parts) >= 5:
                                name, quantity, price_text, location, seller = parts[:5]
                                try:
                                    price = int(price_text.replace('C', '').replace(',', '').strip())
                                except:
                                    price = 0
                                if price <= int(max_price):
                                    notify_items.append([name, price, quantity, location])
                                    found = True
                        next_elem = next_elem.find_next_sibling()
            return notify_items
        except Exception as e:
            return [[f"Error: {e}", 0, "-", "-"]]

    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            item_ids = list(search_conditions.keys())
            colors = []
            for item_id in item_ids:
                cond = search_conditions[item_id]
                max_price = cond.get("price", cond if isinstance(cond, int) else 0)
                color = cond.get("color", "reset")
                colors.append(color)
                tasks.append(fetch_and_parse(item_id, max_price, color, session))
            notify_lists = await asyncio.gather(*tasks)
            all_results = []
            color_map = []
            for idx, item_id in enumerate(item_ids):
                notify_items = notify_lists[idx]
                color = colors[idx]
                # 価格昇順、同価格なら数量降順でソート
                def parse_int(val):
                    try:
                        return int(val)
                    except:
                        return 0
                sorted_items = sorted(
                    notify_items,
                    key=lambda x: (
                        x[1] if isinstance(x[1], int) else float('inf'),
                        -parse_int(x[2])  # 数量降順
                    )
                )
                for item in sorted_items:
                    all_results.append(item)
                    color_map.append(color)
            print_items(all_results, interval_sec, color_map)
    except Exception as e:
        print_items([[f"Error: {e}", 0, "-", "-"]], interval_sec, ["reset"])

async def main():
    reload_flag = False
    clear_console()  # 初回のみ画面クリア
    while True:
        r_pressed = False
        settings = load_settings()
        interval_sec = settings.get("interval_sec", 5)
        if platform.system() == "Windows":
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in [b'R', b'r']:
                    r_pressed = True
        else:
            pass
        if r_pressed:
            print("\n--- 検索条件ファイルを再読込しました ---")
            reload_flag = True
        await scrape_market(interval_sec)
        await asyncio.sleep(interval_sec)

if __name__ == "__main__":
    asyncio.run(main())
