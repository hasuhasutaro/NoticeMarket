import json


def load_items_json(filepath="items.json"):
    """items.jsonを読み込んでリストを返す"""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f).get("items", [])
    except Exception:
        return []


def itemid_to_name_map(items=None):
    """itemid→nameの辞書を返す"""
    if items is None:
        items = load_items_json()
    return {str(item["id"]): item["name"] for item in items}


def name_to_itemid_map(items=None):
    """name→itemidの辞書を返す"""
    if items is None:
        items = load_items_json()
    return {item["name"]: str(item["id"]) for item in items}


def item_candidates(items=None):
    if items is None:
        items = load_items_json()
    return [f"[T{item.get('tier','')} {item.get('rarityStr','')}]{item['name']} ({item['id']})" for item in items]


def extract_itemid_from_candidate(candidate):
    """候補文字列からitemidを抽出"""
    if "(" in candidate and ")" in candidate:
        return candidate.split("(")[-1].split(")")[0].strip()
    return None


def make_condition_display_entries(cond_list, itemid_list, get_item_data_by_id):
    result = []
    for idx, entry in enumerate(cond_list):
        itemid = None
        if itemid_list and idx < len(itemid_list):
            itemid = itemid_list[idx]
        tier = ""
        rarity = ""
        if itemid:
            item_data = get_item_data_by_id(str(itemid))
            if item_data:
                tier = item_data.get("tier", "")
                rarity = item_data.get("rarityStr", "")
        display_entry = f"[T{tier} {rarity}] {entry}"
        result.append(display_entry)
    return result
