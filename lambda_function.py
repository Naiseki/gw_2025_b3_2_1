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
    logger.warning("SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET is not set.")

def lambda_handler(event, context):
    """
    AWS Lambda Handler for Slack Events API
    Supports both API Gateway 1.0 and 2.0 payload formats
    """
    # デバッグログ
    logger.info(f"Event version: {event.get('version', 'unknown')}")
    
    # ペイロード形式の判定（1.0 vs 2.0）
    if 'version' in event and event['version'] == '2.0':
        # API Gateway HTTP API 2.0形式
        headers = {k.lower(): v for k, v in event.get('headers', {}).items()}
        body = event.get('body', '')
        is_base64 = event.get('isBase64Encoded', False)
    else:
        # API Gateway REST API 1.0形式
        headers = {k.lower(): v for k, v in event.get('headers', {}).items()}
        body = event.get('body', '')
        is_base64 = event.get('isBase64Encoded', False)
    
    # Base64デコード
    if is_base64:
        body = base64.b64decode(body).decode('utf-8')
    
    logger.info(f"Headers count: {len(headers)}")
    logger.info(f"Body length: {len(body)}")
    
    # リトライ制御
    if 'x-slack-retry-num' in headers:
        logger.info(f"Retry request received: {headers['x-slack-retry-num']}")
        return {'statusCode': 200, 'body': 'OK'}
    
    # 署名検証
    if not signature_verifier:
        logger.error("SignatureVerifier is not initialized.")
        return {'statusCode': 500, 'body': 'Internal Server Error'}
    
    timestamp = headers.get('x-slack-request-timestamp', '')
    signature = headers.get('x-slack-signature', '')
    
    if not timestamp or not signature:
        logger.warning(f"Missing signature or timestamp. Headers: {list(headers.keys())}")
        return {'statusCode': 401, 'body': 'Unauthorized'}
    
    if not signature_verifier.is_valid(body, timestamp, signature):
        logger.warning("Invalid signature verification failed.")
        return {'statusCode': 401, 'body': 'Unauthorized'}
    
    # ボディのパース
    try:
        event_data = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON body: {e}")
        return {'statusCode': 400, 'body': 'Bad Request'}
    
    # URL Verification Challenge
    if event_data.get('type') == 'url_verification':
        logger.info("URL verification challenge received.")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': event_data.get('challenge')
        }
    
    # イベント処理
    if event_data.get('type') == 'event_callback':
        inner_event = event_data.get('event', {})
        event_type = inner_event.get('type')
        
        # Bot自身のメッセージは無視
        if inner_event.get('bot_id'):
            logger.info("Ignoring bot message")
            return {'statusCode': 200, 'body': 'OK'}
        
        logger.info(f"Event received: {event_type}, User: {inner_event.get('user')}")
        
        if event_type in ['app_mention', 'message']:
            try:
                # say関数の定義
                def say(text, **kwargs):
                    channel = inner_event.get('channel')
                    
                    if not channel:
                        logger.warning("Channel ID not found in event.")
                        return
                    
                    client.chat_postMessage(
                        channel=channel,
                        text=text,
                        **kwargs
                    )
                
                # メッセージ処理の呼び出し
                handle_message(inner_event, say, client)
                
            except Exception as e:
                logger.error(f"Error in handle_message: {e}", exc_info=True)
                return {'statusCode': 200, 'body': 'OK'}
    
    return {'statusCode': 200, 'body': 'OK'}