import re
from typing import Callable
from collections import defaultdict

import bibtexparser
from bibtexparser.middlewares.fieldkeys import NormalizeFieldKeys
from bibtexparser.middlewares.middleware import Middleware
from bibtexparser.middlewares.parsestack import default_parse_stack
from bibtexparser.middlewares.latex_encoding import LatexEncodingMiddleware
from bibtexparser.middlewares.latex_encoding import LatexDecodingMiddleware
from bibtexparser.library import Library
from bibtexparser.model import Entry as BibtexEntry
from bibtexparser.model import DuplicateFieldKeyBlock
from bibtexparser.model import ParsingFailedBlock
from bibtexparser.writer import BibtexFormat

from .middleware.quotestylemiddleware import QuoteStyleMiddleware
from .middleware.formatter import BibTeXFormatterMiddleware
from .middleware.title_formatter import TitleFormatterMiddleware


_LONGEST_FIELD_FOR_DUPES = {"booktitle", "journal"}


def _build_parse_stack() -> list[Middleware]:
    """パーススタックを構築する。"""
    stack: list[Middleware] = default_parse_stack(allow_inplace_modification=True)
    stack.append(NormalizeFieldKeys())
    stack.append(LatexDecodingMiddleware())
    return stack


def deduplicate_entry(entry_str: str, duplicate_keys: list[str]) -> str:
    """重複フィールドを解消する。各フィールドについて最も長い値を採用する。
    Args:
        entry_str: BibTeXエントリ文字列
        duplicate_keys: 重複しているフィールドキーのリスト
    Returns:
        重複フィールドを解消したBibTeXエントリ文字列
    """
    keys = "|".join(map(re.escape, duplicate_keys))

    pattern = re.compile(
        rf'\b({keys})\b\s*=\s*(?:"(.*?)"|{{(.*?)}})\s*,',
        re.IGNORECASE | re.DOTALL,
    )

    matches = list(pattern.finditer(entry_str))
    if not matches:
        return entry_str

    # key ごとに一番長い value を選ぶ
    best_by_key = {}
    spans_to_remove = []

    for m in matches:
        key = m.group(1).lower()
        value = m.group(2) if m.group(2) is not None else m.group(3)
        value = value.strip()

        spans_to_remove.append(m.span())

        if key not in best_by_key or len(value) > len(best_by_key[key]):
            best_by_key[key] = value

    # 元の entry_str から重複フィールドをすべて削除（後ろから）
    new_entry_str = entry_str
    for start, end in sorted(spans_to_remove, reverse=True):
        new_entry_str = new_entry_str[:start] + new_entry_str[end:]

    # 採用したフィールドを 1 回だけ追加（末尾手前）
    insert_pos = new_entry_str.rfind("}")
    if insert_pos == -1:
        return entry_str  # 念のため

    fields_str = ""
    for key, value in best_by_key.items():
        fields_str += f"  {key} = {{{value}}},\n"

    new_entry_str = (
        new_entry_str[:insert_pos]
        + fields_str
        + new_entry_str[insert_pos:]
    )

    return new_entry_str


def _needs_dedup(block: ParsingFailedBlock) -> bool:
    """重複フィールドの解消が必要かどうかを判定する。"""
    if not isinstance(block, DuplicateFieldKeyBlock):
        return False
    normalized_keys = {k.lower() for k in block.duplicate_keys}
    if normalized_keys & _LONGEST_FIELD_FOR_DUPES:
        return True
    return False


def _parse_bibtex_entries(raw_bib: str) -> Library:
    """BibTeXエントリをパースしてLibraryオブジェクトを返す。"""
    parse_stack = _build_parse_stack()
    library = bibtexparser.parse_string(raw_bib, parse_stack=parse_stack)

    for block in library.failed_blocks:
        if _needs_dedup(block):
            modified_entry = deduplicate_entry(block.raw, block.duplicate_keys)
            print("重複フィールドを解消したエントリを再解析中...")
            print("modified_entry:", modified_entry)
            modified_library = bibtexparser.parse_string(modified_entry, parse_stack=parse_stack)
            library.add(modified_library.entries)

    library.remove(library.failed_blocks)

    if not library.entries:
        raise ValueError("有効なBibTeXエントリが見つかりません🥶")

    return library


def simplify_bibtex_entry(
    raw_bib: str,
    new_key: str | None = None,
    booktitle_mode: str = "both",
    warning_callback: Callable[[str], None] | None = None,
) -> str:
    """BibTeXエントリを簡略化して返す。
    Args:
        raw_bib: 元のBibTeXエントリ文字列
        new_key: 新しいエントリキー。Noneの場合は元のキーを使用。
        booktitle_mode: "short"（短縮形）, "long"（正式名称）, "both"（両方）
        warning_callback: 警告メッセージを通知するコールバック関数
    返り値:
        簡略化されたBibTeXエントリ文字列
    """

    library = _parse_bibtex_entries(raw_bib)
    format = BibtexFormat()
    format.trailing_comma = True
    result = bibtexparser.write_string(
        library, 
        unparse_stack=[
            TitleFormatterMiddleware(), 
            BibTeXFormatterMiddleware(abbreviation_mode=booktitle_mode), 
            LatexEncodingMiddleware(enclose_urls=False), 
            QuoteStyleMiddleware()
        ], 
        bibtex_format=format
    )
    return result