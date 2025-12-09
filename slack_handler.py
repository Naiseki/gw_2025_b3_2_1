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

    # オプション解析: -s で短縮形、-l で正式名称、何もなしで両方表示
    # 単語境界をチェックして誤検出を防ぐ
    import re
    has_short = bool(re.search(r'(^|\s)-s(\s|$)', text) or re.search(r'(^|\s)--short(\s|$)', text))
    has_long = bool(re.search(r'(^|\s)-l(\s|$)', text) or re.search(r'(^|\s)--long(\s|$)', text))
    
    # booktitle_mode: "short", "long", "both"
    if has_short:
        booktitle_mode = "short"
    elif has_long:
        booktitle_mode = "long"
    else:
        booktitle_mode = "both"
    
    # オプションをテキストから削除
    raw_bib = re.sub(r'(^|\s)--short(\s|$)', r'\1\2', text)
    raw_bib = re.sub(r'(^|\s)-s(\s|$)', r'\1\2', raw_bib)
    raw_bib = re.sub(r'(^|\s)--long(\s|$)', r'\1\2', raw_bib)
    raw_bib = re.sub(r'(^|\s)-l(\s|$)', r'\1\2', raw_bib).strip()
    if not raw_bib:
        return

    new_key = "KEY"
    simplified = simplify_bibtex_entry(raw_bib, new_key, booktitle_mode=booktitle_mode)
    say(f"```{simplified}```")