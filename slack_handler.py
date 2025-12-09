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

    # オプション解析: -s または --short で短縮形booktitleを使用（デフォルトは正式名称）
    # 単語境界をチェックして誤検出を防ぐ
    import re
    use_short = bool(re.search(r'(^|\s)-s(\s|$)', text) or re.search(r'(^|\s)--short(\s|$)', text))
    raw_bib = re.sub(r'(^|\s)--short(\s|$)', r'\1\2', text)
    raw_bib = re.sub(r'(^|\s)-s(\s|$)', r'\1\2', raw_bib).strip()
    if not raw_bib:
        return

    new_key = "KEY"
    simplified = simplify_bibtex_entry(raw_bib, new_key, use_short=use_short)
    say(f"```{simplified}```")