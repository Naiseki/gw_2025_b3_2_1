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


README_URL = "https://github.com/Naiseki/gw_2025_b3_2_1/blob/main/README.md"


def _build_parse_stack() -> list[Middleware]:
    """パーススタックを構築する。"""
    stack: list[Middleware] = default_parse_stack(allow_inplace_modification=True)
    stack.append(NormalizeFieldKeys())
    # stack.append(LatexDecodingMiddleware())
    return stack


def _parse_bibtex_entries(raw_bib: str, warning_callback: Callable[[str], None] | None = None) -> Library:
    """BibTeXエントリをパースしてLibraryオブジェクトを返す。"""
    parse_stack = _build_parse_stack()
    library = bibtexparser.parse_string(raw_bib, parse_stack=parse_stack, allow_duplicate_fields=True)

    if library.failed_blocks:
        if warning_callback:
            warning_message = "BibTeXの解析に失敗しました🥶\n失敗したブロック:\n\n" + "\n\n".join(block.raw for block in library.failed_blocks)
            warning_callback(warning_message)
        library.remove(library.failed_blocks)
        if not library.entries:
            raise ValueError("BibTeX解析エラー")

    if not library.entries:
        raise ValueError(f"有効なBibTeXエントリが見つかりませんでした🤔\n使い方の詳細は {README_URL} をご覧下さい")

    return library


def simplify_bibtex_entry(
    raw_bib: str,
    new_key: str | None = None,
    abbreviation_mode: str = "both",
    warning_callback: Callable[[str], None] | None = None,
) -> str:
    """BibTeXエントリを簡略化して返す。
    Args:
        raw_bib: 元のBibTeXエントリ文字列
        new_key: 新しいエントリキー。Noneの場合は元のキーを使用。
        abbreviation_mode: "short"（短縮形）, "long"（正式名称）, "both"（両方）
        warning_callback: 警告メッセージを通知するコールバック関数
    返り値:
        簡略化されたBibTeXエントリ文字列
    """

    if not raw_bib:
        raise ValueError(f"有効なBibTeXエントリが見つかりませんでした😰\n使い方の詳細は {README_URL} をご覧下さい")

    library = _parse_bibtex_entries(raw_bib, warning_callback=warning_callback)
    format = BibtexFormat()
    format.trailing_comma = True
    format.block_separator = "\n"
    format.indent = "    "
    result = bibtexparser.write_string(
        library, 
        unparse_stack=[
            TitleFormatterMiddleware(), 
            BibTeXFormatterMiddleware(abbreviation_mode=abbreviation_mode, warning_callback=warning_callback), 
            # LatexEncodingMiddleware(enclose_urls=False), 
            QuoteStyleMiddleware()
        ], 
        bibtex_format=format
    )
    return result