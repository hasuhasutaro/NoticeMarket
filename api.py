import requests

ITEMS_API_URL = "https://bitjita.com/api/items"
MARKET_API_URL = "https://bitjita.com/api/market"
MARKET_ITEM_API_URL = "https://bitjita.com/api/market/items/{}"


def fetch_items():
    """APIからアイテム情報を取得し、データを返す"""
    response = requests.get(ITEMS_API_URL)
    response.raise_for_status()
    return response.json()


def fetch_market():
    """APIからマーケット情報を取得し、データを返す（全件）"""
    response = requests.get(MARKET_API_URL)
    response.raise_for_status()
    return response.json()


def fetch_market_item(itemid):
    """APIから特定アイテムIDのマーケット情報を取得し、データを返す"""
    url = MARKET_ITEM_API_URL.format(itemid)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
