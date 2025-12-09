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
    handle_message(event, say, client)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()