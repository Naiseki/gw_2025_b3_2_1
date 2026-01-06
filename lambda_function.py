import os
import json
import logging
import base64
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from slack_handler import handle_message

# ロガー設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数の取得
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

# グローバルスコープで初期化
if SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET:
    client = WebClient(token=SLACK_BOT_TOKEN)
    signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)
else:
    client = None
    signature_verifier = None
    logger.warning("SLACK_BOT_TOKEN または SLACK_SIGNING_SECRET が設定されていません。")

def lambda_handler(event, context):
    """
    Slack Events API用のAWS Lambdaハンドラー
    API Gateway 1.0および2.0のペイロード形式をサポート
    """
    
    # ペイロード形式の判定（1.0 vs 2.0）
    if "version" in event and event["version"] == "2.0":
        # API Gateway HTTP API 2.0形式
        headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
        body = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
    else:
        # API Gateway REST API 1.0形式
        headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
        body = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
    
    # Base64デコード
    if is_base64:
        body = base64.b64decode(body).decode("utf-8")
    
    # リトライ制御
    if "x-slack-retry-num" in headers:
        logger.info(f"リトライリクエストを受信: {headers['x-slack-retry-num']}")
        return {"statusCode": 200, "body": "OK"}
    
    # 署名検証
    if not signature_verifier:
        logger.error("SignatureVerifierが初期化されていません。")
        return {"statusCode": 500, "body": "Internal Server Error"}
    
    timestamp = headers.get("x-slack-request-timestamp", "")
    signature = headers.get("x-slack-signature", "")
    
    if not timestamp or not signature:
        logger.warning(f"署名またはタイムスタンプがありません。ヘッダー: {list(headers.keys())}")
        return {"statusCode": 401, "body": "Unauthorized"}
    
    if not signature_verifier.is_valid(body, timestamp, signature):
        logger.warning("署名検証に失敗しました。")
        return {"statusCode": 401, "body": "Unauthorized"}
    
    # ボディのパース
    try:
        event_data = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"JSONボディのパースに失敗: {e}")
        return {"statusCode": 400, "body": "Bad Request"}
    
    # URL Verification Challenge
    if event_data.get("type") == "url_verification":
        logger.info("URL検証チャレンジを受信。")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": event_data.get("challenge")
        }
    
    # イベント処理
    if event_data.get("type") == "event_callback":
        inner_event = event_data.get("event", {})
        event_type = inner_event.get("type")
        channel = inner_event.get("channel", "unknown")
        user = inner_event.get("user", "unknown")
        
        # Bot自身のメッセージは無視
        if inner_event.get("bot_id"):
            logger.info("ボットメッセージを無視")
            return {"statusCode": 200, "body": "OK"}
        
        logger.info(f"イベント受信: {event_type}, ユーザー: {user}, チャンネル: {channel}")
        
        if event_type in ["app_mention", "message"]:
            # メッセージ送信関数の定義
            def say(text, **kwargs):
                try: 
                    if not channel or channel == "unknown":
                        logger.warning("イベントにチャンネルIDが見つかりません。")
                        return

                    # チャンネルの場合はスレッド返信、DMの場合は通常送信
                    is_dm = channel.startswith("D")
                    thread_ts = inner_event.get("ts") if not is_dm else None
                    
                    # チャンネルの場合はスレッドに返信する
                    if thread_ts and "thread_ts" not in kwargs:
                        kwargs["thread_ts"] = thread_ts

                    client.chat_postMessage(channel=channel, text=text, **kwargs)
                except Exception as e:
                    logger.error(f"メッセージ送信エラー: {e}", exc_info=True)

            try:
                # メッセージ処理の呼び出し
                handle_message(inner_event, say, client)
            except Exception as e:
                say(f"{e.__class__.__name__} エラーが発生しました😢")
                logger.error(f"handle_messageでエラー: {e}", exc_info=True)
                return {"statusCode": 200, "body": "OK"}
    
    return {"statusCode": 200, "body": "OK"}