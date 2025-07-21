# 定数管理
COLUMNS = (
    "itemName",
    "itemTier",
    "itemRarityStr",
    "priceThreshold",
    "quantity",
    "regionName"
)

COLUMN_LABELS = {
    "itemName": "アイテム名",
    "itemTier": "Tier",
    "itemRarityStr": "レア度",
    "priceThreshold": "価格",
    "quantity": "数量",
    "regionName": "場所"
}

COLUMN_WIDTHS = {
    "itemName": 260,
    "itemTier": 50,
    "itemRarityStr": 80,
    "priceThreshold": 70,
    "quantity": 70,
    "regionName": 120
}

COLUMN_ANCHORS = {
    "itemName": None,
    "itemTier": "center",
    "itemRarityStr": "center",
    "priceThreshold": "e",
    "quantity": "e",
    "regionName": None
}

BG_COLORS = ["#23272a", "#181a1b"]
FG_COLOR = "#f5f6fa"
