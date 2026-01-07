# *bib_bot*

# 概要
Slack上でBibTeXを綺麗に整形して返信してくれるボットです。
論文執筆や文献管理を効率化します。
- **簡単操作**: BibTeXをコピペして送るだけ。
- **柔軟な出力**: オプション（`-s`, `-l`）で会議名の長さを調整可能。
- **一括整形**: 複数のエントリも一度に処理。

# 目次
- [使い方（利用者向け）](#使い方利用者向け)
- [Slack Appの作成（開発者向け）](#slack-appの作成開発者向け)
- [AWSへのデプロイ（開発者向け）](#awsへのデプロイ開発者向け)

# 使い方（利用者向け）
bib_bot をインストール済みワークスペースで利用する方法です。
## 導入
### DM
`ホーム` → `App` → `管理する` → `アプリをブラウズする` → `bib_bot` を検索して追加

### チャンネル
`右上三点リーダー` → `チャンネル詳細を開く` → `インテグレーション` → `アプリを追加する` → `bib_bot` を検索して追加
## 使い方
ACLやarXivなどのサイトからBibTeXをコピペして送信します。
### DM
BibTeX本文をそのまま送信

例:
```bash
@inproceedings{...,
    title = "...",
    author = "...",
    booktitle = "...",
    year = "2020",
    publisher = "...",
    url = "https://...",
    pages = "100--110",
    abstract = "..."
}
```
### チャンネル
メンションしてBibTeX本文を送信 @bib_bot

例:
```bash
@bib_bot
@inproceedings{...,
    title = "...",
    author = "...",
    booktitle = "...",
    year = "2020",
    publisher = "...",
    url = "https://...",
    pages = "100--110",
    abstract = "..."
}
```
### オプション
BibTeXの前にオプションをつけることで，論文誌/国際会議名の出力を制御できます。
- `-s (--short)`: 省略形のみ出力
- `-l (--long)`: 原形のみ出力
- `オプション無し`: 原形，省略形ともに出力

例:
```bash
-s @inproceedings{...,
    title = "...",
    author = "...",
    booktitle = "...",
    year = "2020",
    publisher = "...",
    url = "https://...",
    pages = "100--110",
    abstract = "..."
}
```

### 一括整形
複数のBibTeXエントリを一括で送信して、整形できます。

例:
```bash
% EXAMPLE
@inproceedings{...,
    title = "...",
    author = "...",
    booktitle = "...",
    year = "2020",
    publisher = "...",
    url = "https://...",
    pages = "100--110",
    abstract = "..."
}

% SAMPLE
@misc{...,
      title={...}, 
      author={...},
      year={2023},
      eprint={...},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/...}, 
}
```

# Slack Appの作成（開発者向け）
ワークスペースにボットをインストールする方法です。
## 1. Slack API 管理画面へアクセス

1.  Slack にログインした状態で [https://api.slack.com/apps](https://api.slack.com/apps) にアクセス
2.  **「Create New App」** をクリック
3.  **「From scratch」** を選択
4.  App Name に `bib_bot`、Development Workspace に対象ワークスペースを設定して **「Create App」** をクリック

## 2. Bot Token Scopes（権限）を設定

1.  左メニューから **「OAuth & Permissions」** を選択
    
2.  **Bot Token Scopes** の **「Add an OAuth Scope」** をクリック
    
3.  追加するスコープを以下のように設定する  

| スコープ | 用途 |
|---|---|
| `app_mentions:read` | bot へのメンションを受け取る |
| `chat:write` | メッセージの送信 |
| `im:history` | DM のメッセージ履歴の読み取り |
| `users:read` | ユーザー情報の読み取り |

> ※ 必要に応じて今後追加・変更できます。

## 3. App の表示名・ユーザー名を設定

1.  左メニューから **「App Home」** をクリック
    
2.  Display Name に `bib_bot`、Default Username に `bib_bot` を入力  
    → Slack 上での見た目・bot 名として使われます。

## 4. ワークスペースへのインストール

1.  左メニューから **「Install App」** を選択
    
2.  **「Install App to Workspace」** をクリック  
    → Slack が権限リクエストを表示します
    
3.  権限画面で内容を確認し **「許可する」** をクリック  
    → インストールが完了し OAuth トークンが発行されます。

# AWSへのデプロイ（開発者向け）
AWS Lambda + Events API 環境 + GitHub Actions でデプロイする手順です。

## 1. 事前準備
### AWS アカウント
AWSコンソールへのアクセス権限が必要です。

## 2. AWS Lambda関数の作成

1. AWSコンソールで **Lambda** を開く。

2. 「関数の作成」をクリック。

3. 設定:

-  **関数名**: `bib_bot-fn` (任意)

-  **ランタイム**: `Python 3.13`

-  **アーキテクチャ**: `x86_64`

4. 「関数の作成」をクリック。

  

### 設定変更

  

1.  **設定**タブ → **一般設定** → 「編集」:

-  **タイムアウト**: `1分` 以上に設定 (推奨: 30秒〜1分。処理内容によるが最大15分まで可能)

-  **メモリ**: 必要に応じて調整 (デフォルト128MBで動作確認し、遅ければ増やす)

2.  **設定**タブ → **環境変数** → 「編集」:

-  `SLACK_BOT_TOKEN`: `xoxb-` から始まるボットトークン

-  `SLACK_SIGNING_SECRET`: Slack AppのBasic InformationにあるSigning Secret

## 3. API Gatewayの設定

1. AWSコンソールで **API Gateway** を開く。

2. 「APIを作成」→ **HTTP API** (または REST API) を選択。

- ここでは設定が簡単な **HTTP API** を推奨。

3.  **統合**:

- 「統合を追加」→ Lambdaを選択。

- 作成したLambda関数 (`bib_bot-fn`) を指定。

4.  **ルートを設定**:

- メソッド: `POST`

- リソースパス: `/slack/events` (任意)

- 統合ターゲット: 先ほどのLambda統合を選択。

5. 「作成」をクリック。

6. 作成されたAPIの **Invoke URL** (例: `https://xyz.execute-api.ap-northeast-1.amazonaws.com`) をメモする。


## 4. OIDC プロバイダの設定

GitHub Actions から AWS への安全なアクセスのため、OIDC プロバイダを追加します。

1.  AWS Management Console の **IAM → Identity providers**
    
2.  **Add provider**
    
3.  以下を指定： 
```text
Provider type: OpenID Connect  
Provider URL: https://token.actions.githubusercontent.com  
Audience: sts.amazonaws.com
```

## 5. デプロイ用 IAM ロールを作成

このロールは GitHub Actions が Lambda にデプロイする際に引き受けます。

1.  **IAM → Roles → Create role**
    
2.  **Trusted entity type**: Web identity
    
3.  **Identity provider**: Step 4 で作成した OIDC プロバイダ
    
4.  **Audience**: `sts.amazonaws.com`
    
5.  **GitHub org/repo**, branch は必要に応じて制限して OK
    
6.  **Permissions** は一旦 _空_ でロールを作成
    

----------

## 6. IAM にインラインポリシーを追加

先ほど作成したロールに Lambda 更新権限を付与します。

1.  作成したロールを開く
    
2.  **Permissions → Add inline policy**
    
3.  JSON で以下の最低権限だけを許可：
    

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:GetFunctionConfiguration"
      ],
      "Resource": "arn:aws:lambda:YOUR_REGION:YOUR_ACCOUNT_ID:function:bib_bot-fn"
    }
  ]
}

```

> ※ リソース ARN は自身の関数に置き換えてください。
> 
## 7. GitHub リポジトリに Secrets を追加

GitHub 側でデプロイに必要な値を設定します：
| Secret 名 | 内容 |
| ---------------------------- | -------------------------------- |
| `AWS_REGION` | Lambda のリージョン（例: ap-northeast-1） |
| `AWS_ROLE_PROD` | Step 5 で作成したロールの ARN（本番用） |
| `AWS_ROLE_TEST` | Step 5 で作成したロールの ARN（テスト用）|

## 8. Slack Appの設定変更

Slack Developer Console ([https://api.slack.com/apps](https://api.slack.com/apps)) で設定を変更します。


1. 対象のアプリを選択。

2.  **Socket Mode**:

-  `Enable Socket Mode` を **OFF** にする (Disable)。

3.  **Event Subscriptions**:

-  `Enable Events` を **ON** にする。

-  **Request URL** に、Step 3 で取得したAPI GatewayのエンドポイントURL (`https://.../slack/events`) を入力。

- Verified と表示されればOK (Lambdaが正しくChallengeを返している)。
- 変更があった場合は「Reinstall to Workspace」を実行。

## 9. GitHub Actions でデプロイ

このプロジェクトでは、GitHub Actions を使用して手動でスクリプトを実行できます。

### 実行手順

1. GitHub リポジトリのトップページ上部にある **[Actions]** タブをクリックします。
2. 左側のサイドバーにある **[All workflows]** 一覧から、`Deploy Slack Bot Lambda`を選択します。
3. 画面右側に表示される青いバーの **[Run workflow]** ボタンをクリックします。
4. 使用するブランチ、デプロイ先、Lambda関数名を指定し、緑色の **[Run workflow]** ボタンをクリックすると実行が開始されます。

> ※ 実行が開始されると、一覧のトップに新しいジョブが表示されます。クリックすると詳細なログを確認できます。

## 10. 動作確認

Slack上でボットに対してメンションを送るか、DMを送信して動作を確認してください。

CloudWatch Logs でログを確認し、エラーが出ていないかチェックします。
