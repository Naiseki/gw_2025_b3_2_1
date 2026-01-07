# slack_handler.py

import logging
from bibtex.simplify import simplify_bibtex_entry
import re

def parse_options_and_extract_bib(text):
    """オプションを解析し、raw_bibを構築する。"""
    text = text.replace("```", "").strip()

    before_at, at_and_after = "", ""
    if "@" in text:
        at_index = text.index("@")
        before_at = text[:at_index]
        at_and_after = text[at_index:]
    else:
        before_at = text
        at_and_after = ""

    
    # オプション解析: -s で短縮形、-l で正式名称、何もなしで両方表示
    # オプションは @の前に書かないといけない
    short_pattern = r"(^|\s)(-s|--short)(\s|$)"
    long_pattern = r"(^|\s)(-l|--long)(\s|$)"

    has_short = bool(re.search(short_pattern, before_at))
    has_long = bool(re.search(long_pattern, before_at))
    
    # abbreviation_mode: "short", "long", "both"
    if has_short:
        abbreviation_mode = "short"
    elif has_long:
        abbreviation_mode = "long"
    else:
        abbreviation_mode = "both"
    
    # オプションを filtered_before_at から削除
    cleaned_before_at = re.sub(short_pattern, r"\1\3", before_at)
    cleaned_before_at = re.sub(long_pattern, r"\1\3", cleaned_before_at).strip()

    # raw_bibを構築 (掃除した before_at を結合)
    raw_bib = (cleaned_before_at + "\n" + at_and_after).strip()
    
    return abbreviation_mode, raw_bib


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

    # オプション解析とbib抽出
    abbreviation_mode, bib = parse_options_and_extract_bib(text)

    try:
        simplified = simplify_bibtex_entry(bib, abbreviation_mode=abbreviation_mode, warning_callback=say)
        say(f"```{simplified}```")
    except ValueError as e:
        say(f"{e.__class__.__name__} {str(e)}")
        logging.warning("BibTeX 整形に失敗しました: %s", str(e))