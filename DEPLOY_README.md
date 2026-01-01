# Slack Bot AWS Lambda Deployment Guide

このドキュメントは、Socket Modeで動作していたSlack BotをAWS Lambda + API Gateway (Events API) 環境へ移行・デプロイするための手順書です。

## 1. 事前準備

### 必要なファイル
- `lambda_function.py`: Lambda関数のエントリーポイント
- `requirements.txt`: 依存ライブラリリスト
- `slack_handler.py`: 既存のボットロジック
- `bibtex/`: 依存モジュールディレクトリ
- `resources/`: リソースファイルディレクトリ

### AWS アカウント
AWSコンソールへのアクセス権限が必要です。

## 2. デプロイパッケージの作成

LambdaにアップロードするためのZIPファイルを作成します。

```bash
# 作業用ディレクトリの作成
mkdir -p package

# 依存ライブラリのインストール
pip install -r requirements.txt -t package

# ソースコードのコピー
cp lambda_function.py package/
cp slack_handler.py package/
cp -r bibtex package/
cp -r resources package/

# ZIP化
cd package
zip -r ../deployment_package.zip .
cd ..
```

## 3. AWS Lambda関数の作成

1. AWSコンソールで **Lambda** を開く。
2. 「関数の作成」をクリック。
3. 設定:
   - **関数名**: `bib-bot-function` (任意)
   - **ランタイム**: `Python 3.13` (または 3.9以降)
   - **アーキテクチャ**: `x86_64`
4. 「関数の作成」をクリック。

### コードのアップロード
1. 「コード」タブで「アップロード元」→「.zipファイル」を選択。
2. 作成した `deployment_package.zip` をアップロード。

### 設定変更
1. **設定**タブ → **一般設定** → 「編集」:
   - **タイムアウト**: `1分` 以上に設定 (推奨: 30秒〜1分。処理内容によるが最大15分まで可能)
   - **メモリ**: 必要に応じて調整 (デフォルト128MBで動作確認し、遅ければ増やす)
2. **設定**タブ → **環境変数** → 「編集」:
   - `SLACK_BOT_TOKEN`: `xoxb-` から始まるボットトークン
   - `SLACK_SIGNING_SECRET`: Slack AppのBasic InformationにあるSigning Secret

## 4. API Gatewayの設定

1. AWSコンソールで **API Gateway** を開く。
2. 「APIを作成」→ **HTTP API** (または REST API) を選択。
   - ここでは設定が簡単な **HTTP API** を推奨。
3. **統合**:
   - 「統合を追加」→ Lambdaを選択。
   - 作成したLambda関数 (`bib-bot-function`) を指定。
4. **ルートを設定**:
   - メソッド: `POST`
   - リソースパス: `/slack/events` (任意)
   - 統合ターゲット: 先ほどのLambda統合を選択。
5. 「作成」をクリック。
6. 作成されたAPIの **Invoke URL** (例: `https://xyz.execute-api.ap-northeast-1.amazonaws.com`) をメモする。
   - エンドポイントURLは `Invoke URL` + `/slack/events` となる。

## 5. Slack Appの設定変更

Slack Developer Console (https://api.slack.com/apps) で設定を変更します。

1. 対象のアプリを選択。
2. **Socket Mode**:
   - `Enable Socket Mode` を **OFF** にする (Disable)。
3. **Event Subscriptions**:
   - `Enable Events` を **ON** にする。
   - **Request URL** に、API GatewayのエンドポイントURL (`https://.../slack/events`) を入力。
   - Verified と表示されればOK (Lambdaが正しくChallengeを返している)。
   - **Subscribe to bot events** に以下が追加されているか確認:
     - `app_mention`
     - `message.channels` (必要に応じて)
     - `message.im` (必要に応じて)
4. **OAuth & Permissions**:
   - Scopes に `app_mention`, `chat:write` など必要な権限があるか確認。
   - 変更があった場合は「Reinstall to Workspace」を実行。

## 6. 動作確認

Slack上でボットに対してメンションを送るか、DMを送信して動作を確認してください。
CloudWatch Logs でログを確認し、エラーが出ていないかチェックします。
