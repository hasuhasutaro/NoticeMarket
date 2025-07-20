# NotificationMarket

BitjitaマーケットプレイスのAPIからアイテム情報・マーケット情報を取得し、GUIで表示・検索・ソート・条件絞り込みができるWindows用アプリケーションです。

## 特徴
- Python + tkinter製のシンプルなデスクトップアプリ
- APIから最新のアイテム一覧・マーケット情報を取得
- 条件（最大価格・最小個数）で絞り込み検索
- 条件はGUIから追加・削除・編集可能
- 条件一覧やサジェスト候補にTier/レアリティも表示
- 条件・設定はローカルJSONファイルに保存
- items.jsonがなければ初回起動時に自動生成
- market_app.exeとして単体実行可能

## 使い方
1. `market_app.exe`を実行
2. 初回起動時はAPIからitems.jsonを自動生成
3. 上部のフォームでアイテム名・最大価格・最小個数を入力し「条件追加」
4. 条件一覧から選択して「条件削除」や「選択解除」も可能
5. マーケット情報は2秒ごとに自動更新
6. 条件パネルはトグルボタンで非表示/再表示可能

## ファイル構成
- market_app.py ... メインアプリ本体
- ensure_items_json.py ... items.json自動生成スクリプト
- api.py ... APIアクセス用
- utils.py ... 補助関数
- search_conditions.py ... 条件の保存・読込
- items.json ... アイテム一覧データ
- search_conditions.json ... 検索条件データ
- settings.json ... 最大表示件数などの設定
- dist/market_app.exe ... ビルド済み実行ファイル

## ビルド方法
1. Python 3.8以降をインストール
2. 必要なパッケージをインストール
   ```
   pip install -r requirements.txt
   ```
3. PyInstallerでビルド
   ```
   pyinstaller --onefile --noconsole market_app.py
   ```
   dist/market_app.exe が生成されます

## 注意
- API仕様やレスポンス形式はBitjitaの仕様に依存します
- items.json, search_conditions.json, settings.jsonは同じディレクトリに配置してください

## ライセンス
MIT License
