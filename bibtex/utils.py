# bibtex/utils.py

import re
from abc import ABC, abstractmethod
from titlecase import titlecase

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

    return titlecase(raw_title, callback=small_word_callback)


def extract_field(raw_bib: str, field: str) -> str:
    """field をダブルクオート・波括弧双方から抽出する。"""
    p1 = rf'{field}\s*=\s*"([^"]+)"'
    p2 = rf'{field}\s*=\s*{{([^}}]+)}}'
    for p in (p1, p2):
        m = re.search(p, raw_bib, re.DOTALL)
        if m:
            return m.group(1).strip()
    return ""


def build_short_booktitle(long_booktitle: str) -> str:
    """括弧内の略称から Proc. of ... を生成する（ACL向け）。"""
    short_booktitle = "Proceedings"
    match = re.search(r'\((?:\{)?([A-Za-z][A-Za-z0-9\s\-/]+)', long_booktitle)
    if match:
        parts = re.split(r'[-/\s]+', match.group(1))
        parts = [p.upper() for p in parts if p and not p.isdigit()]
        if parts:
            if len(parts) > 1:
                parts = sorted(parts)
            short_booktitle = f"Proc. of {'-'.join(parts)}"
    return short_booktitle


def format_authors(raw_author: str, threshold: int = 10, line_break_after_and: bool = False) -> str:
    """著者数が threshold 以上なら先頭のみ、それ未満なら全員を返す。"""
    authors = [a.strip() for a in re.split(r"\s+and\s+", raw_author) if a.strip()]
    if not authors:
        return ""
    if len(authors) >= threshold:
        return authors[0]
    return " and\n      ".join(authors) if line_break_after_and else " and ".join(authors)


class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both") -> str:
        """raw_bib を整形して返す。
        
        Args:
            booktitle_mode: "short"（短縮形）, "long"（正式名称）, "both"（両方）
        """
        ...