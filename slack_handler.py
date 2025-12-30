# slack_handler.py

from bibtex.simplify import simplify_bibtex_entry
import re

def handle_message(event, say, client):
    """DM またはメンションされたメッセージを BibTeX 変換。"""

    # ボットのメッセージは無視
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

    # メンションされていたら@idの部分をtextから削除
    if is_mentioned:
        text = re.sub(rf"<@{bot_user_id}>", "", text).strip()

    text = text.strip().strip("`")

    # オプション解析: -s で短縮形、-l で正式名称、何もなしで両方表示
    # オプションは @の前に書かないといけない
    before_at, at_and_after = "", ""
    if "@" in text:
        at_index = text.index("@")
        before_at = text[:at_index]
        at_and_after = text[at_index:]
    else:
        before_at = text
        at_and_after = ""

    has_short = bool(re.search(r'(^|\s)-s(\s|$)', before_at) or re.search(r'(^|\s)--short(\s|$)', before_at))
    has_long = bool(re.search(r'(^|\s)-l(\s|$)', before_at) or re.search(r'(^|\s)--long(\s|$)', before_at))
    
    # booktitle_mode: "short", "long", "both"
    if has_short:
        booktitle_mode = "short"
    elif has_long:
        booktitle_mode = "long"
    else:
        booktitle_mode = "both"
    
    # raw_bibを構築
    raw_bib = at_and_after.strip()
    if not raw_bib:
        say("有効なBibTeXエントリが見つかりませんでした🥶")
        return

    try:
        simplified = simplify_bibtex_entry(raw_bib, booktitle_mode=booktitle_mode, warning_callback=say)
        say(f"```{simplified}```")
    except ValueError as e:
        say(f"{e.__class__.__name__} {str(e)}")