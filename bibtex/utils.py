# bibtex/utils.py

import re
from abc import ABC, abstractmethod
from typing import Callable
from titlecase import titlecase
from load_resource import load_journal_name_dict

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "en", "for",
    "if", "in", "of", "on", "or", "the", "to", "v", "vs", "via", "with",
}

def strip_all_braces(text: str) -> str:
    while re.search(r'{[^{}]*}', text):
        text = re.sub(r'{([^{}]*)}', r'\1', text)
    return text


def normalize_title(raw_title: str) -> str:
    """BibTeX の {A} 指定を外しつつ titlecase を適用する。"""
    raw_title = strip_all_braces(raw_title)

    def small_word_callback(word, **kwargs):
        index = kwargs.get("index", 0)
        words = kwargs.get("words", [])
        if 0 < index < len(words) - 1 and word.lower() in SMALL_WORDS:
            return word.lower()
        return word

    return titlecase(raw_title)


def extract_field(raw_bib: str, field: str) -> str:
    """field をダブルクオート・波括弧双方から抽出する。"""
    p1 = rf'{field}\s*=\s*"([^"]+)"'
    p2 = rf'{field}\s*=\s*{{([^}}]+)}}'
    for p in (p1, p2):
        m = re.search(p, raw_bib, re.DOTALL)
        if m:
            return m.group(1).strip()
    return ""


def build_short_booktitle(long_booktitle: str, warning_callback: Callable[[str], None] | None = None) -> str:
    conf = _get_short_conference_name(long_booktitle, warning_callback)
    return f"Proc. of {conf}" if conf else "Proceedings"

def _get_short_conference_name(long_booktitle: str, warning_callback: Callable[[str], None] | None = None) -> str:
    if not long_booktitle:
        return ""

    journal_name_dict = load_journal_name_dict()
    if not journal_name_dict:
        raise ValueError("論文誌名辞書の読み込みに失敗しました。")

    # 1. まず辞書で探す
    if long_booktitle in journal_name_dict:
        return journal_name_dict[long_booktitle]

    words = long_booktitle.split()
    booktitle_words = []
    if words and words[0].lower() == "proceedings" and len(words) > 4:
        # Proceedings of the Nst を除いた会議名の部分を使う
        booktitle_words = words[4:]

    conf = " ".join(booktitle_words)
    # 2. 会議名でも辞書を引く
    if conf in journal_name_dict:
        return journal_name_dict[conf]

    if warning_callback:
        warning_callback("*! ! ! 会議名が辞書に見つからなかったため、イニシャルで短縮形を作成します。*\n*これは大いに間違っている可能性があります。*")

    # イニシャルで短縮形を作成
    initials = ''.join(word[0] for word in booktitle_words if word and word[0].isupper())
    return initials

def build_short_journal(long_journal: str) -> str:
    """括弧内の略称から短縮形ジャーナル名を生成する。"""
    short_journal = long_journal
    match = re.search(r'\((?:\{)?([A-Za-z][A-Za-z0-9\s\-/]+)', long_journal)
    if match:
        parts = re.split(r'[-/\s]+', match.group(1))
        parts = [p.upper() for p in parts if p and not p.isdigit()]
        if parts:
            if len(parts) > 1:
                parts = sorted(parts)
            short_journal = '-'.join(parts)
    return short_journal


def format_authors(raw_author: str, line_break_after_and: bool = False) -> str:
    """著者数が threshold 以上なら先頭のみ、それ未満なら全員を返す。"""
    authors = [a.strip() for a in re.split(r"\s+and\s+", raw_author) if a.strip()]
    if not authors:
        return ""
    if line_break_after_and:
        return " and\n      ".join(authors)
    return " and ".join(authors)

def find_missing_fields(raw_bib: str, fields: list[str]) -> list[str]:
    """指定されたフィールドがすべて存在するかを確認する。"""
    missing_fields = []
    for field in fields:
        if not re.search(rf"\b{field}\s*=", raw_bib):
            missing_fields.append(field)
    return missing_fields


class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both") -> str:
        """raw_bib を整形して返す。
        
        Args:
            booktitle_mode: "short"（短縮形）, "long"（正式名称）, "both"（両方）
        """
        ...
    
    def check_required_fields(self, raw_bib: str, required_fields: list[str]) -> None:
        missing_fields = find_missing_fields(raw_bib, required_fields)
        if missing_fields:
            raise ValueError(f"必要なフィールドがありません: {', '.join(missing_fields)}")

    def get_fields(self, raw_bib: str, fields: list[str]) -> dict[str, str]:
        result = {}
        for field in fields:
            data = extract_field(raw_bib, field)
            if data:
                result[field] = data
            else:
                raise ValueError(f"フィールド '{field}' の値が見つかりません。")
        return result