# slack_handler.py

from bibtex.simplify import simplify_bibtex_entry
import re

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
    first_line = text.splitlines()[0]
    has_short = bool(re.search(r'(^|\s)-s(\s|$)', first_line) or re.search(r'(^|\s)--short(\s|$)', first_line))
    has_long = bool(re.search(r'(^|\s)-l(\s|$)', first_line) or re.search(r'(^|\s)--long(\s|$)', first_line))
    
    # booktitle_mode: "short", "long", "both"
    if has_short:
        booktitle_mode = "short"
    elif has_long:
        booktitle_mode = "long"
    else:
        booktitle_mode = "both"
    
    
    # オプションをfirst_lineから削除
    cleaned_first_line = re.sub(r'(^|\s)--short(\s|$)', r'\1\2', first_line)
    cleaned_first_line = re.sub(r'(^|\s)-s(\s|$)', r'\1\2', cleaned_first_line)
    cleaned_first_line = re.sub(r'(^|\s)--long(\s|$)', r'\1\2', cleaned_first_line)
    cleaned_first_line = re.sub(r'(^|\s)-l(\s|$)', r'\1\2', cleaned_first_line).strip()
    
    # 残りの行を取得
    remaining_lines = "\n".join(text.splitlines()[1:]) if len(text.splitlines()) > 1 else ""
    
    # raw_bibを構築
    raw_bib = cleaned_first_line + ("\n" + remaining_lines if remaining_lines else "").strip()
    if not raw_bib:
        say("有効なBibTeXエントリが見つかりませんでした。")
        return

    new_key = "KEY"
    simplified = simplify_bibtex_entry(raw_bib, new_key, booktitle_mode=booktitle_mode)
    say(f"```{simplified}```")