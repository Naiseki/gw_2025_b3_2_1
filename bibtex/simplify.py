from typing import Callable

import bibtexparser
from bibtexparser.middlewares.fieldkeys import NormalizeFieldKeys
from bibtexparser.middlewares.middleware import Middleware
from bibtexparser.middlewares.parsestack import default_parse_stack
from bibtexparser.model import Entry as BibtexEntry

from .arxiv_parser import ArxivParser
from .article_parser import ArticleParser
from .inproceedings_parser import InproceedingsParser
from .utils import BaseParser, EntryData


def _build_parse_stack() -> list[Middleware]:
    stack = default_parse_stack(allow_inplace_modification=True)
    stack.append(NormalizeFieldKeys())
    return stack


def _parse_bibtex_entry(raw_bib: str) -> BibtexEntry:
    parse_stack = _build_parse_stack()
    try:
        library = bibtexparser.parse_string(raw_bib, parse_stack=parse_stack)
    except Exception as exc:
        raise ValueError("BibTeXエントリの解析に失敗しました。") from exc

    if not library.entries:
        raise ValueError("BibTeXエントリが見つかりません。")

    return library.entries[0]


def _normalize_entry(entry: BibtexEntry) -> EntryData:
    normalized_entry: EntryData = {
        "entrytype": entry.entry_type.lower(),
        "id": entry.key,
    }
    for field in entry.fields:
        value = field.value
        normalized_entry[field.key.lower()] = value.strip() if isinstance(value, str) else str(value)
    return normalized_entry


def detect_source(entry: BibtexEntry, entry_data: EntryData, raw_bib: str) -> str:
    raw_lower = raw_bib.lower()
    entry_type = entry_data.get("entrytype", entry.entry_type).lower()

    if entry_data.get("eprint") or "arxiv" in raw_lower:
        return "arxiv"
    if entry_type == "inproceedings" or "@inproceedings" in raw_lower:
        return "inproceedings"
    if entry_type == "article" or "@article" in raw_lower:
        return "article"

    raise ValueError("対応していないBibTeXエントリです🙇‍♂️")


_PARSERS: dict[str, BaseParser] = {
    "article": ArticleParser(),
    "inproceedings": InproceedingsParser(),
    "arxiv": ArxivParser(),
}


def simplify_bibtex_entry(
    raw_bib: str,
    new_key: str | None = None,
    booktitle_mode: str = "both",
    warning_callback: Callable[[str], None] | None = None,
) -> str:
    entry = _parse_bibtex_entry(raw_bib)
    entry_data = _normalize_entry(entry)
    source = detect_source(entry, entry_data, raw_bib)
    parser = _PARSERS[source]
    key = new_key or entry_data.get("id")
    if not key:
        raise ValueError("BibTeXエントリのキーが見つかりません。")

    return parser.parse(entry_data, key, booktitle_mode=booktitle_mode, warning_callback=warning_callback)
