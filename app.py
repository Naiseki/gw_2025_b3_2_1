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
    except OSError as e:
        say(f"{e.__class__.__name__} エラーが発生しました: {e}")
    except AttributeError as e:
        say(f"{e.__class__.__name__} 属性エラーが発生しました: {e}")
    except NameError as e:
        say(f"{e.__class__.__name__} 名前エラーが発生しました: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()