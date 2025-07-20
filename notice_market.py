import asyncio
import platform
from config import load_settings, load_search_conditions
from utils import clear_console
from display import print_items
from scraper import fetch_and_parse

if platform.system() == "Windows":
    import msvcrt

async def scrape_market(interval_sec):
    search_conditions = load_search_conditions()
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            item_ids = list(search_conditions.keys())
            colors = []
            for item_id in item_ids:
                cond = search_conditions[item_id]
                max_price = cond.get("price", cond if isinstance(cond, int) else 0)
                color = cond.get("color", "reset")
                min_quantity = cond.get("min_quantity", 1)
                colors.append(color)
                tasks.append(fetch_and_parse(item_id, max_price, color, min_quantity, session))
            notify_lists = await asyncio.gather(*tasks)
            all_results = []
            color_map = []
            for idx, item_id in enumerate(item_ids):
                notify_items = notify_lists[idx]
                color = colors[idx]
                def parse_int(val):
                    try:
                        return int(val)
                    except:
                        return 0
                sorted_items = sorted(
                    notify_items,
                    key=lambda x: (
                        x[1] if isinstance(x[1], int) else float('inf'),
                        -parse_int(x[2])
                    )
                )
                for item in sorted_items:
                    all_results.append(item)
                    color_map.append(color)
            print_items(all_results, interval_sec, color_map)
    except Exception as e:
        print_items([[f"Error: {e}", 0, "-", "-"]], interval_sec, ["reset"])

async def main():
    clear_console()
    while True:
        r_pressed = False
        settings = load_settings()
        interval_sec = settings.get("interval_sec", 5)
        if platform.system() == "Windows":
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in [b'R', b'r']:
                    r_pressed = True
        if r_pressed:
            print("\n--- 検索条件ファイルを再読込しました ---")
        await scrape_market(interval_sec)
        await asyncio.sleep(interval_sec)

if __name__ == "__main__":
    asyncio.run(main())import time
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://bitjita.com/"
INTERVAL_SEC = 10

def scrape_and_print():
    try:
        response = requests.get(TARGET_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # サイト構造に応じて主要情報を抽出
        title = soup.title.string if soup.title else "No title"
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {title}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Start scraping {TARGET_URL} every {INTERVAL_SEC} seconds...")
    while True:
        scrape_and_print()
        time.sleep(INTERVAL_SEC)
