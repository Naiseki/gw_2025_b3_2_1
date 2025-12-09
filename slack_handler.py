# slack_handler.py

from bibtex.simplify import simplify_bibtex_entry

def handle_message(event, say, client):
    """DM またはメンションされたメッセージを BibTeX 変換。"""
    if event.get("subtype") == "bot_message":
        return

    channel = event.get("channel")
    user = event.get("user")
    text = event.get("text", "") or ""

    if not user or not channel:
        return

    bot_user_id = client.auth_test()["user_id"]
    is_dm = channel.startswith("D")
    is_mentioned = f"<@{bot_user_id}>" in text

    if not (is_dm or is_mentioned):
        return

    raw_bib = text.strip()
    if not raw_bib:
        return

    new_key = "KEY"
    simplified = simplify_bibtex_entry(raw_bib, new_key)
    say(f"```{simplified}```")