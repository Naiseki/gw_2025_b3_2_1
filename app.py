import os
import sys
import time
import logging
import threading
import urllib.request
import urllib.error
from typing import Any
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from slack_handler import handle_message
from logging.handlers import RotatingFileHandler


# =========================
# 初期化
# =========================

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))


# =========================
# Logging
# =========================

def setup_logging() -> None:
    log_file = os.getenv("LOG_FILE", "bib_bot.log")
    max_bytes = 10 * 1024 * 1024  # 10MB
    backup_count = 5

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


# =========================
# Slack Event Handler
# =========================

@app.event("app_mention")
def on_mention(event: Any, say: Any, client: Any) -> None:
    try:
        logging.info("Mention event received. ID=%s, subtype=%s", event.get("user", "unknown"), event.get("subtype", "none"))
        handle_message(event, say, client)
    except (MemoryError, RecursionError) as e:
        # プロセス破壊の可能性が高いエラーは即終了
        logging.critical("致命的エラー: %s", e, exc_info=True)
        logging.shutdown()
        os._exit(1)
    except Exception as e:
        safe_say(say, f"{e.__class__.__name__} 予期しないエラーが発生しました: {e}")


@app.event("message")
def on_message(event: Any, say: Any, client: Any) -> None:
    try:
        logging.info("Message event received. ID=%s, subtype=%s", event.get("user", "unknown"), event.get("subtype", "none"))
        handle_message(event, say, client)
    except (MemoryError, RecursionError) as e:
        # プロセス破壊の可能性が高いエラーは即終了
        logging.critical("致命的エラー: %s", e, exc_info=True)
        logging.shutdown()
        os._exit(1)
    except Exception as e:
        safe_say(say, f"{e.__class__.__name__} 予期しないエラーが発生しました: {e}")


def safe_say(say: Any, message: str) -> None:
    try:
        say(message)
    except Exception as e:
        logging.warning("%s Slack 送信失敗: %s", e.__class__.__name__, e)


# =========================
# Healthchecks
# =========================

def ping_healthchecks(url: str, timeout: int = 10) -> None:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout):
            pass
    except Exception as e:
        logging.warning("Healthchecks ping 失敗: %s", e)


# =========================
# Slack接続確認 → Healthchecks
# =========================

def slack_heartbeat(
    client,
    hc_url: str | None,
    interval: int = 1800,
    retries: int = 3,
    retry_interval: int = 15,
) -> None:
    """
    - Slack Web API が retries 回以内に成功すれば healthchecks.io に ping
    - retries 回連続失敗したら半死と判断してプロセス終了
    """
    while True:
        for i in range(retries):
            try:
                client.api_test()
                if hc_url:
                    ping_healthchecks(hc_url)
                break
            except Exception as e:
                logging.warning("Slack heartbeat 失敗 (%d/%d): %s", i + 1, retries, e)
                time.sleep(retry_interval)
        else:
            logging.critical("Slack 接続が復旧しません。プロセスを終了します。")
            logging.shutdown()
            os._exit(1)

        # 次の heartbeat まで待機
        time.sleep(interval)



# =========================
# Main
# =========================

if __name__ == "__main__":
    setup_logging()

    # Socket Mode 再接続用バックオフ変数
    retry_count = 0
    max_retries = 5
    backoff_factor = 2
    base_sleep = 1
    last_failure_time = 0
    retries_reset_duration = 600  # 10分

    # Healthchecks 設定
    hc_url = os.getenv("HEALTHCHECKS_URL")
    hc_interval = int(os.getenv("HEALTHCHECKS_INTERVAL", "1800"))

    # Slack heartbeat スレッド起動
    if hc_url:
        t = threading.Thread(
            target=slack_heartbeat,
            daemon=True,
            args=(app.client, hc_url, hc_interval),
            name="slack-heartbeat",
        )
        t.start()
        logging.info("Slack heartbeat 開始")

    # Socket Mode 再接続ループ（完全切断用）
    while True:
        try:
            handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
            handler.start()
            break
        except (ConnectionResetError, BrokenPipeError) as e:
            if time.time() - last_failure_time > retries_reset_duration:
                retry_count = 0  # リトライカウントリセット
            last_failure_time = time.time()

            retry_count += 1
            if retry_count > max_retries:
                logging.critical("再接続失敗が続いたため終了: %s", e)
                break

            sleep_time = base_sleep * (backoff_factor ** (retry_count - 1))
            logging.warning(
                "Socket 切断 (%d/%d)。%ds 後に再接続します: %s",
                retry_count,
                max_retries,
                sleep_time,
                e,
            )
            time.sleep(sleep_time)
        except SlackApiError as e:
            logging.critical("Slack API エラー: %s", e)
            break
        except (MemoryError, RecursionError) as e:
            # プロセス破壊の可能性が高いエラーは即終了
            logging.critical("致命的エラー: %s", e, exc_info=True)
            logging.shutdown()
            os._exit(1)
        except Exception as e:
            logging.critical("起動中に予期しないエラー: %s", e, exc_info=True)
            break

    logging.info("プロセス終了")
    logging.shutdown()