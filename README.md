# Bib整形ボット
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

例:
- `SLACK_BOT_TOKEN=xoxb-...`
- `SLACK_APP_TOKEN=xapp-...`
- `SLACK_CHANNEL=...`

## 実行
```bash
uv run app.py
```

## 使い方
- DM: BibTeXエントリ本文をそのまま送信
- チャンネル: `@<ボット名> <BibTeX本文>`
- レスポンスは整形済みBibTeXが返されます。

## 注意点
- ドキュメント内で参照されるキーの名前は固定値 `"KEY"` です。この部分は自由に変更してください。

## トラブルシュート
- ボットが反応しない: トークンスコープ、イベント購読、Socket Mode、ワークスペースへのインストール状況を確認
- ImportError: `python-dotenv`（import名は `dotenv`）および `bibtex.simplify` の導入を確認
- 返信できない: `chat:write` の付与とBotのチャンネル参加を確認
