# app.py

import os
import sys
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import time
import logging
from slack_sdk.errors import SlackApiError as APIError

from slack_handler import handle_message

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.event("message")
def message_event(event, say, client):
    try:
        handle_message(event, say, client)
    except ValueError as e:
        say(f"{e.__class__.__name__} 不正な値が指定されました: {e}")
    except NameError as e:
        say(f"{e.__class__.__name__} 未定義の変数/関数が使用されました: {e}")
    except RuntimeError as e:
        say(f"{e.__class__.__name__} 実行時に問題が発生しました: {e}")
    except (MemoryError, RecursionError) as e:
        # 致命的エラーはログを残してプロセスを終了する
        logging.critical("致命的エラーが発生しました: %s", e, exc_info=True)
        sys.exit(1)
    except Exception as e:
        say(f"{e.__class__.__name__} 予期しないエラーが発生しました: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", filename="bib_bot.log")
    retry_count = 0
    max_retries = 5
    backoff_factor = 2
    base_sleep = 1

    while True:
        try:
            handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
            # handler.start() はブロッキング呼び出しなので、ここで接続が維持される
            handler.start()
            break
        except APIError as e:
            # Slack API エラーは致命的とみなしてログを出して終了
            err_msg = getattr(e, "response", {}).get("error", str(e))
            logging.error(f"Slack APIエラーが発生しました: {err_msg}")
            break
        except (ConnectionResetError, BrokenPipeError) as e:
            retry_count += 1
            if retry_count > max_retries:
                logging.error(f"ソケットエラーが繰り返し発生しました: {e}。再試行を中止します。")
                break
            sleep_time = base_sleep * (backoff_factor ** (retry_count - 1))
            logging.warning(f"ソケット接続がリセットされました (試行 {retry_count}/{max_retries})。{sleep_time}s 後に再接続します: {e}")
            time.sleep(sleep_time)
            continue
        except (MemoryError, RecursionError) as e:
            # 致命的エラー発生時はログを残して直ちに終了
            logging.critical("致命的エラーが発生しました: %s", e, exc_info=True)
            os._exit(1)
        except KeyboardInterrupt:
            logging.info("停止シグナルを受け取りました。終了します。")
            break
        except Exception as e:
            logging.error(f"アプリの起動中にエラーが発生しました: {e}")
            break
        else:
            retry_count = 0  # 成功した場合はリトライカウントをリセット