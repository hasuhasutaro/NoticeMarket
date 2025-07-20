# notificationMarcket.exe 使い方

## 概要
Bitjitaマーケットの指定アイテムを定期監視し、指定価格以下の出品を色付きでCUI表示するツールです。

## 実行方法
1. `dist/notice_market.exe` をダブルクリック、またはコマンドプロンプト/PowerShellで実行
   ```sh
   dist\notice_market.exe
   ```
   ※ Pythonや追加インストール不要

2. 設定ファイルを編集
   - `search_conditions.json` で監視アイテムID・通知価格（設定価格以下が通知される）・表示色を設定
     ```json
     {
       "3210037": {"price": 2, "color": "#FF0000"},
       "2097987865": {"price": 75, "color": "#00FF00"}
     }
     ```
     - `color` は色名（red, green, ...）またはHEX（#RRGGBB）で指定可能
   - `settings.json` で更新間隔（秒）を設定（正常に動作しない）
     ```json
     { "interval_sec": 5 }
     ```

## 画面操作
- 表示は自動更新（設定間隔ごと）
- `R`キーで検索条件ファイルを再読込
- Ctrl+Cで終了

## 注意事項
- 初回起動時、設定ファイルがなければ自動生成されます
- 色付き表示は一部ターミナルで非対応の場合あり
- 監視対象IDはBitjitaマーケットのURLから取得してください
