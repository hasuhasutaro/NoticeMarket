# Copilot Instructions for notificationMarcket

このプロジェクトはAPIから取得したデータをGUIで表示・ソート・条件検索するWindowsアプリケーションです。
実行するとウィンドウが表示され、APIからアイテム情報を取得して表示します。
APIはBitjitaのマーケットプレイスからアイテム情報を取得します。

言語はPythonで、GUIはtkinterを使用しています。

## 機能
- ボタンまたは初回起動時に最新のアイテム一覧を取得し、データをローカルに保存します。
  - `https://bitjita.com/api/items ` からアイテム情報を取得し、ローカルの `items.json` に保存します。

- マーケット情報を2秒間隔で取得し、表示します。
  - `https://bitjita.com/api/market` からマーケット情報を取得します。
  - アイテム名、Tier、レア度、価格、数量、場所を表示
    - [アイテム名またはアイテムid・価格・数量]での絞り込み検索(複数可能)
    - フィルタリング対象のアイテムの最新状態を一定時間ごとに取得し、フィルタリングして表示する(条件以外のアイテムは非表示)
    - アイテム名の色分け表示（レア度に応じて）
    - 同じ価格で複数のアイテムがある場合、数量の多い順に表示
    - 絞り込み検索条件は `search_conditions.json` に保存され、アプリ起動時に読み込みます。
      `search_conditions.json` の例:
      ```json
      {
          "3210037": {"max_price": 10, "min_quantity": 5},
          "2097987865": {"max_price": 75, "min_quantity": 10}
      }
      ```
    - GUIから絞り込み条件を追加・削除可能

## 開発について
- Todoを作成しながら開発を進めています。
　書き方の例
  - [ ] アイテム情報の取得APIを実装する
  - [ ] GUIのレイアウトを整える
  - [ ] 絞り込み検索機能を実装する

## APIの応答形式
### アイテム情報
```json
sellOrders: [
    {
        "id": "432345564271709672",
        "entityId": "432345564274546567",
        "ownerEntityId": "216172782159743920",
        "claimEntityId": "432345564271709672",
        "itemId": 1210037,
        "itemType": 0,
        "priceThreshold": "1",
        "quantity": "14",
        "timestamp": "1752767797393213",
        "storedCoins": "0",
        "createdAt": "2025-07-19T22:21:21.586119+00:00",
        "updatedAt": "2025-07-19T22:21:21.586119+00:00",
        "claimName": "Brudenshire",
        "ownerUsername": "BlueElephant",
        "regionId": 6,
        "regionName": "Tessavar",
        "itemName": "Beginner's Stone Carvings",
        "itemDescription": "Writing and images carved in a stone from the ancient civilization. A scholar might be able to decipher some valuable information from this at a Research Desk.",
        "itemTier": 1,
        "itemTag": "Ancient Hieroglyphs",
        "itemRarity": 1,
        "itemRarityStr": "Common",
        "iconAssetName": "GeneratedIcons/Items/StoneCarvings"
    }
]
``` 
### マーケット情報
```json
items: [
    {
        "id": "432345564271709672",
        "entityId": "432345564274546567",
        "ownerEntityId": "216172782159743920",
        "claimEntityId": "432345564271709672",
        "itemId": 1210037,
        "itemType": 0,
        "priceThreshold": "1",
        "quantity": "14",
        "timestamp": "1752767797393213",
        "storedCoins": "0",
        "createdAt": "2025-07-19T22:21:21.586119+00:00",
        "updatedAt": "2025-07-19T22:21:21.586119+00:00",
        "claimName": "Brudenshire",
        "ownerUsername": "BlueElephant",
        "regionId": 6,
        "regionName": "Tessavar",
        "itemName": "Beginner's Stone Carvings",
        "itemDescription": "Writing and images carved in a stone from the ancient civilization. A scholar might be able to decipher some valuable information from this at a Research Desk.",
        "itemTier": 1,
        "itemTag": "Ancient Hieroglyphs",
        "itemRarity": 1,
        "itemRarityStr": "Common",
        "iconAssetName": "GeneratedIcons/Items/StoneCarvings"
    }
]
```