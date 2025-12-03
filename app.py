from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from titlecase import titlecase
import os
import re

def normalize_title(raw_title: str) -> str:
    # {J}apanese -> Japanese のように1文字波括弧を除く
    raw_title = re.sub(r'{([A-Za-z])}', r'\1', raw_title)

    # titlecase.com 風に Title Case 化
    tc = titlecase(raw_title)

    return tc

def simplify_bibtex_entry(raw_bib: str, new_key: str) -> str:
    """
    ACL風BibTeX (@inproceedings ...) を
    カスタム形式に変換する。
    new_key に {SNOW-T15, SNOW-T23, JADES, ...} を渡す想定。
    """

    # --- title ---
    m = re.search(r'title\s*=\s*"([^"]+)"', raw_bib, re.DOTALL)
    if not m:
        m = re.search(r'title\s*=\s*{([^}]+)}', raw_bib, re.DOTALL)

    title = m.group(1).strip() if m else "Unknown Title"

    # ← ここで title を titlecase.com 風にする！
    title = normalize_title(title)

    # --- author ---
    author = ""
    m = re.search(r'author\s*=\s*"([^"]+)"', raw_bib, re.DOTALL)
    if not m:
        m = re.search(r'author\s*=\s*{([^}]+)}', raw_bib, re.DOTALL)
    if m:
        author = m.group(1).strip()

    # --- booktitle (元のやつ) ---
    long_booktitle = ""
    m = re.search(r'booktitle\s*=\s*"([^"]+)"', raw_bib, re.DOTALL)
    if not m:
        m = re.search(r'booktitle\s*=\s*{([^}]+)}', raw_bib, re.DOTALL)
    if m:
        long_booktitle = m.group(1).strip()

    # booktitle 長い版から末尾の括弧 (...) を消してロング版とする
    long_booktitle_clean = re.sub(r'\s*\([^)]*\)\s*$', '', long_booktitle).strip()

    # --- 短い booktitle を推定 ---
    # 末尾の括弧から略称を拾う。例:
    #   "(TSAR-2022)" -> "TSAR"
    #   "({LREC} 2018)" -> "LREC"
    short_booktitle = "Proceedings"
    m = re.search(r'\((?:\{)?([A-Za-z]+)(?:[^)]*)\)\s*$', long_booktitle)
    if m:
        acronym = m.group(1)
        short_booktitle = f"Proc. of {acronym}"
    else:
        # 括弧から取れない場合の雑なフォールバック
        if "LREC" in long_booktitle:
            short_booktitle = "Proc. of LREC"
        elif "TSAR" in long_booktitle:
            short_booktitle = "Proc. of TSAR"
        elif "ACL" in long_booktitle:
            short_booktitle = "Proc. of ACL"
        elif "EMNLP" in long_booktitle:
            short_booktitle = "Proc. of EMNLP"

    # --- year ---
    year = ""
    m = re.search(r'year\s*=\s*"([^"]+)"', raw_bib)
    if not m:
        m = re.search(r'year\s*=\s*{([^}]+)}', raw_bib)
    if m:
        year = m.group(1).strip()

    # --- pages (あれば使う) ---
    pages = ""
    m = re.search(r'pages\s*=\s*"([^"]+)"', raw_bib)
    if not m:
        m = re.search(r'pages\s*=\s*{([^}]+)}', raw_bib)
    if m:
        pages = m.group(1).strip()

    # --- url ---
    url = ""
    m = re.search(r'url\s*=\s*"([^"]+)"', raw_bib)
    if not m:
        m = re.search(r'url\s*=\s*{([^}]+)}', raw_bib)
    if m:
        url = m.group(1).strip().rstrip("/")

    # --- 出力組み立て ---
    lines = []
    lines.append(f"@inproceedings{{{new_key},")
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
   
load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.event("message")
def handle_message(event, say, client):
    # Bot 自身のメッセージは無視
    if event.get("subtype") == "bot_message":
        return

    channel = event.get("channel")
    user = event.get("user")
    text = event.get("text", "") or ""

    # 念のため user がない特殊メッセージもスキップ
    if not user or not channel:
        return

    # Bot のユーザーIDを取得
    bot_user_id = client.auth_test()["user_id"]

    is_dm = channel.startswith("D")
    is_mentioned = f"<@{bot_user_id}>" in text

    # DM なら無条件で反応、チャンネルではメンションされたときだけ反応
    if not (is_dm or is_mentioned):
        return
       
    cleaned = text.strip()
    first_line, _, rest = cleaned.partition("\n")
    new_key = first_line.strip()
    raw_bib = rest.strip()
    simplified = simplify_bibtex_entry(raw_bib, new_key)
    say(f"```{simplified}```")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()