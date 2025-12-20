# bib_bot
NLP研究室 B3グループワーク第2回グループ1

## 概要
Slack上でBibTeXを整形して返すボットです。DMまたはメンションされたメッセージを受け取り、整形した結果を返信します。

## 動作
- DM: 送られたテキスト全体をBibTeXとして処理
- チャンネル: ボットがメンションされたメッセージのみ処理
- ボットの投稿は無視

## 環境変数（.env）
- `SLACK_BOT_TOKEN`: xoxb- で始まるBot Token
- `SLACK_APP_TOKEN`: xapp- で始まるApp-Level Token
- `SLACK_CHANNEL`: メッセージを送信するSlackチャンネルID
- `HEALTHCHECKS_URL`: healthchecks.io の ping 用 URL。未設定の場合は通知は行われません。
- `HEALTHCHECKS_INTERVAL`: ping の実行間隔（秒）。デフォルトは `1800`（30分）。

例:
- `SLACK_BOT_TOKEN=xoxb-...`
- `SLACK_APP_TOKEN=xapp-...`
- `SLACK_CHANNEL=...`
- `HEALTHCHECKS_URL=https://hc-ping.com/...`
- `HEALTHCHECKS_INTERVAL=1800`

## 実行
```bash
uv run app.py
```

## 使い方
ACLやarXivなどのサイトからBibTexをコピペして送信します。
- DM: BibTeX本文をそのまま送信
- チャンネル: `@<ボット名> <BibTeX本文>`
- レスポンスは整形済みBibTeXが返されます。
### オプション
BibTeXの前にオプションをつけることで，論文誌/国際会議の出力を制御できます。
- `-s (--short)`: 省略形のみ出力
- `-l (--long)`: 原形のみ出力
- `オプション無し`: 原形，省略形ともに出力

例:
```bash
-s @inproceedings{...,
    title = "...",
    author = "...",
    editor = "...",
    booktitle = "...",
    year = "2020",
    publisher = "...",
    url = "https://...",
    pages = "100--110",
    abstract = "..."
}
```
