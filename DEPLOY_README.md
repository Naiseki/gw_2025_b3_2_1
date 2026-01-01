# Slack Bot AWS Lambda Deployment Guide（GitHub Actions 版）

このドキュメントは、Slack Bot（Events API / HTTP API Gateway）を **AWS Lambda に GitHub Actions で自動デプロイする方法**をまとめた手順書です。

従来の「ローカルで ZIP を作って手動アップロードする方式」は廃止し、
**`git push main` だけで Lambda が更新される構成**を前提としています。

---

## 1. 前提構成

### 使用技術

* AWS Lambda（Python）
* API Gateway（HTTP API）
* Slack Events API（Socket Mode 不使用）
* GitHub Actions（OIDC 認証）
* uv + pyproject.toml / uv.lock

### リポジトリ構成

```
.
├ lambda_function.py      # Lambda エントリーポイント
├ slack_handler.py        # Slack Bot ロジック
├ load_resource.py        # リソース読み込み補助
├ pyproject.toml          # 依存定義
├ uv.lock                 # 依存ロックファイル（必須）
├ bibtex/                 # 依存モジュール
├ resources/              # リソースファイル
└ .github/workflows/
   └ deploy-lambda.yml    # GitHub Actions
```

※ `requirements.txt` は使用しません。

---

## 2. AWS 側の初期設定（初回のみ）

### 2.1 Lambda 関数の作成

* 関数名: `bib-bot-function`
* ランタイム: **Python 3.13**
* アーキテクチャ: `x86_64`

※ API Gateway / Slack App との接続設定は従来どおりで変更不要。

---

### 2.2 Lambda 環境変数

Lambda の **設定 → 環境変数** に以下を設定しておきます。

* `SLACK_BOT_TOKEN`
* `SLACK_SIGNING_SECRET`

※ GitHub Actions 側には Slack のシークレットは置きません。

---

### 2.3 GitHub Actions 用 IAM ロール（OIDC）

GitHub Actions から Lambda にデプロイするため、
OIDC を使用した IAM ロールを作成します。

#### 必要な権限（最小構成）

```json
{
  "Effect": "Allow",
  "Action": [
    "lambda:UpdateFunctionCode",
    "lambda:UpdateFunctionConfiguration"
  ],
  "Resource": "arn:aws:lambda:ap-northeast-1:*:function:bib-bot-function"
}
```

#### 信頼ポリシー

* GitHub OIDC プロバイダーを使用
* 対象リポジトリ・ブランチ（`main`）を制限することを推奨

---

## 3. GitHub 側の設定

### 3.1 GitHub Secrets

リポジトリの **Settings → Secrets and variables → Actions** に以下を登録します。

| Name                 | Value            |
| -------------------- | ---------------- |
| `AWS_ROLE_TO_ASSUME` | IAM ロールの ARN     |
| `AWS_REGION`         | `ap-northeast-1` |

---

## 4. GitHub Actions によるデプロイ

### 4.1 ワークフロー

`.github/workflows/deploy-lambda.yml` に以下のワークフローを配置します。

* `main` ブランチへの push をトリガー
* uv + uv.lock を使用して依存を解決
* Lambda 用 ZIP を生成
* 不要ファイルを削除してサイズ最適化
* AWS Lambda に自動デプロイ

※ ワークフローの詳細は YAML ファイルを参照してください。

---

### 4.2 デプロイ時に行われる処理

GitHub Actions 内で以下が自動実行されます。

1. Python 3.13 環境の準備
2. uv による依存インストール（`--no-dev`）
3. アプリコード・リソースのコピー
4. 不要ファイル削除

   * `package/bin`
   * `__pycache__`
   * `*.pyc`, `*.pyo`
   * `*.dist-info`
   * `tests`, `.pytest_cache`
5. 最大圧縮 ZIP の作成
6. `aws lambda update-function-code` によるデプロイ

---

## 5. ZIP サイズ最適化について

Lambda 実行に不要なファイルはすべて除外しています。

削除対象：

* `package/bin`（CLI ツール用、Lambda では不要）
* `__pycache__`
* `*.pyc`, `*.pyo`
* `*.dist-info`（pip 管理情報）

これにより ZIP サイズを大幅に削減し、
Lambda の 50MB 制限に余裕を持たせています。

---

## 6. デプロイ方法

```bash
git push origin main
```

これだけで Lambda 関数が更新されます。

* API Gateway の URL は変わりません
* Slack App の設定変更は不要です

---

## 7. 動作確認

* Slack でボットにメンション / DM を送信
* AWS CloudWatch Logs でエラーが出ていないか確認

---

## 8. 補足

* `uv.lock` は必ずコミットしてください（再現性確保のため）
* dev 用ブランチでは deploy を走らせない運用を推奨
* 依存が重くなった場合は Lambda Layer 化も検討可能

---

## 9. まとめ

* 手動 ZIP アップロードは不要
* ローカルと CI の依存解決は完全一致
* セキュアな OIDC 認証
* `git push` だけで本番反映

この構成を **正式なデプロイ手順**とします。
