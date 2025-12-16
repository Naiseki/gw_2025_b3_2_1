# bibtex/utils.py

import re
from abc import ABC, abstractmethod
from typing import Callable
from titlecase import titlecase
from load_resource import load_journal_name_dict

def strip_all_braces(text: str) -> str:
    while re.search(r'{[^{}]*}', text):
        text = re.sub(r'{([^{}]*)}', r'\1', text)
    return text


def normalize_title(raw_title: str) -> str:
    """BibTeX の {A} 指定を外しつつ titlecase を適用する。"""
    raw_title = strip_all_braces(raw_title)
    return titlecase(raw_title)


def extract_field(raw_bib: str, field: str) -> str:
    """field をダブルクオート・波括弧双方から抽出する（大文字小文字を無視）。"""
    field_esc = re.escape(field)
    p1 = rf'\b{field_esc}\s*=\s*"([^"]+)"'
    p2 = rf'\b{field_esc}\s*=\s*{{([^}}]+)}}'
    for p in (p1, p2):
        m = re.search(p, raw_bib, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def build_short_booktitle(long_booktitle: str, warning_callback: Callable[[str], None] | None = None) -> str:
    conf = _get_short_conference_name(long_booktitle, warning_callback)
    return f"Proc. of {conf}" if conf else ""


def _get_short_conference_name(long_booktitle: str, warning_callback: Callable[[str], None] | None = None) -> str:
    if not long_booktitle:
        return ""

    journal_name_dict = load_journal_name_dict()
    if not journal_name_dict:
        raise ValueError("論文誌名辞書の読み込みに失敗しました。")

    long_booktitle = long_booktitle.translate(str.maketrans("", "", ",.")).strip()

    pattern = r'''
    ^
    (?:In\s+)?                      # optional "In "
    (?:Proceedings|Proc\.)          # Proceedings / Proc.
    \s+of\s+                        # " of "
    (?:the\s+)?                     # optional "the "
    (?:                             
        \d{4}                        # year
    | \d+(?:st|nd|rd|th)           # ordinal
    )?
    \s*
    '''

    # Proceedings ... of 20xx などの前置きを削除
    long_booktitle = re.sub(pattern, '', long_booktitle, flags=re.IGNORECASE | re.VERBOSE)


    # 1. まず辞書で探す
    if long_booktitle in journal_name_dict:
        return journal_name_dict[long_booktitle]

    if warning_callback:
        warning_callback("*! ! ! 会議名が辞書に見つからなかったため、イニシャルで省略形を作成します。*\n*これは間違っている可能性が大いにあります。*")

    # 2. イニシャルで短縮形を作成
    initials = "".join(word[0] for word in booktitle_words if word and word[0].isupper())
    return initials


def build_short_journal(long_journal: str, warning_callback: Callable[[str], None] | None = None) -> str:
    if not long_journal:
        return ""
    journal_name_dict = load_journal_name_dict()
    if not journal_name_dict:
        raise ValueError("論文誌名辞書の読み込みに失敗しました。")

    long_journal = long_journal.translate(str.maketrans("", "", ",.")).strip()
    # Vol.XX などの部分を削除
    long_journal = re.sub(
        r'\s+(?:Vol(?:ume)?|No|Issue)\.?\s*\d+|\s*\(\d{4}\)',
        '',
        long_journal,
        flags=re.IGNORECASE
    ).strip()

    # まず辞書で探す
    if long_journal in journal_name_dict:
        return journal_name_dict[long_journal]

    if warning_callback:
        warning_callback("*! ! ! ジャーナル名が辞書に見つからなかったため、イニシャルで省略形を作成します。*\n*これは間違っている可能性が大いにあります。*")
    """括弧内の略称から省略形ジャーナル名を生成する。"""
    words = long_journal.split()
    initials = "".join(word[0] for word in words if word and word[0].isupper())
    return initials


def format_authors(raw_author: str, line_break_after_and: bool = False) -> str:
    """著者数が threshold 以上なら先頭のみ、それ未満なら全員を返す。"""
    authors = [a.strip() for a in re.split(r"\s+and\s+", raw_author) if a.strip()]
    if not authors:
        return ""
    if line_break_after_and:
        return " and\n      ".join(authors)
    return " and ".join(authors)


class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both") -> str:
        """raw_bib を整形して返す。
        
        Args:
            booktitle_mode: "short"（短縮形）, "long"（正式名称）, "both"（両方）
        """
        ...


    def get_fields(self, raw_bib: str, fields: list[tuple[str, bool]]) -> dict[str, str]:
        """ 
        fields で指定されたフィールドを抽出する。必須フィールドが欠けている場合は例外を投げる。
        Args:
            raw_bib: BibTeX エントリの文字列
            fields: (フィールド名, 必須かどうか) のタプルのリスト
        Returns:
            フィールド名をキー、抽出した値を値とする辞書
        """
        result = {}
        missing_fields = []
        for field, required in fields:
            data = extract_field(raw_bib, field)
            if data:
                result[field] = data
            elif required:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"必要なフィールドの値がありません: {', '.join(missing_fields)}")

        return result