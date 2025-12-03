# ============================== Imports & Constants ==============================

import os
import re
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from titlecase import titlecase

SMALL_WORDS = {  # ACLスタイルの小文字単語
    "a", "an", "and", "as", "at", "but", "by", "en", "for",
    "if", "in", "of", "on", "or", "the", "to", "v", "vs", "via", "with",
}

# ============================== Helper Functions ==============================

def normalize_title(raw_title: str) -> str:
    """BibTeX の {A} 指定を外しつつ titlecase を適用する。"""
    raw_title = re.sub(r'{([A-Za-z])}', r'\1', raw_title)

    def small_word_callback(word, **kwargs):
        index = kwargs.get("index", 0)
        words = kwargs.get("words", [])
        if 0 < index < len(words) - 1 and word.lower() in SMALL_WORDS:
            return word.lower()
        return word

    return titlecase(raw_title, callback=small_word_callback)


def extract_field(raw_bib: str, field: str) -> str:
    """fieldsをダブルクオート・波括弧双方から抽出する。"""
    pattern_double = rf'{field}\s*=\s*"([^"]+)"'
    pattern_brace = rf'{field}\s*=\s*{{([^}}]+)}}'
    for pattern in (pattern_double, pattern_brace):
        match = re.search(pattern, raw_bib, re.DOTALL)
        if match:
            return match.group(1).strip()
    return ""


def build_short_booktitle(long_booktitle: str) -> str:
    """括弧内の略称から Proc. of ... を生成する。"""
    short_booktitle = "Proceedings"
    match = re.search(r'\((?:\{)?([A-Za-z][A-Za-z0-9\s\-/]+)(?:[^)]*)\)\s*$', long_booktitle)
    if match:
        raw_parts = re.split(r'[-/\s]+', match.group(1))
        parts = []
        for part in raw_parts:
            if not part:
                continue
            part_upper = part.upper()
            if re.fullmatch(r'\d+', part_upper):
                continue
            parts.append(part_upper)
        if parts:
            if len(parts) > 1:
                parts = sorted(parts)
            short_booktitle = f"Proc. of {'-'.join(parts)}"
    else:  # フォールバック
        if "LREC" in long_booktitle:
            short_booktitle = "Proc. of LREC"
        elif "TSAR" in long_booktitle:
            short_booktitle = "Proc. of TSAR"
        elif "ACL" in long_booktitle:
            short_booktitle = "Proc. of ACL"
        elif "EMNLP" in long_booktitle:
            short_booktitle = "Proc. of EMNLP"
    return short_booktitle

# ============================== BibTeX Simplification ==============================

def simplify_bibtex_entry(raw_bib: str, new_key: str) -> str:
    """ACL系 BibTeX を Slack 用カスタム形式へ整形する。"""
    title = extract_field(raw_bib, "title") or "Unknown Title"
    title = normalize_title(title)

    author = extract_field(raw_bib, "author")
    long_booktitle = extract_field(raw_bib, "booktitle")
    long_booktitle_clean = re.sub(r'\s*\([^)]*\)\s*$', '', long_booktitle).strip()
    short_booktitle = build_short_booktitle(long_booktitle)

    year = extract_field(raw_bib, "year")
    pages = extract_field(raw_bib, "pages")
    url = extract_field(raw_bib, "url").rstrip("/")

    lines = ["@inproceedings{KEY,"]
    if title:
        lines.append(f"    title = {{{{{title}}}}},")
    if author:
        lines.append(f"    author = \"{author}\",")
    if short_booktitle:
        lines.append(f"    booktitle = \"{short_booktitle}\",")
    if long_booktitle_clean:
        lines.append(f"    booktitle = \"{long_booktitle_clean}\",")
    if year:
        lines.append(f"    year = \"{year}\",")
    if pages:
        lines.append(f"    pages = \"{pages}\",")
    if url:
        lines.append(f"    url = \"{url}\",")

    lines.append("}")
    return "\n".join(lines)

# ============================== Slack Bot Setup ==============================

load_dotenv()
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.event("message")
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

    cleaned = text.strip()
    first_line, _, rest = cleaned.partition("\n")
    new_key = first_line.strip() or new_key
    raw_bib = rest.strip()
    simplified = simplify_bibtex_entry(raw_bib, new_key)
    say(f"```{simplified}```")

# ============================== Entry Point ==============================

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()