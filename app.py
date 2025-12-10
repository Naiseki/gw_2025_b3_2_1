# app.py

import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

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
    except Exception as e:
        say(f"{e.__class__.__name__} 予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    try:
        handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
        handler.start()
    except APIError as e:
        print(f"Slack APIエラーが発生しました: {e.response['error']}")
    except Exception as e:
        print(f"アプリの起動中にエラーが発生しました: {e}")