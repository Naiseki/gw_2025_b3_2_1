import re
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
        raise ValueError("BibTeXエントリが見つかりません。\n失敗フィールド:", library.failed_blocks[0].raw)

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
    if "arXiv" in raw_bib:
        return "arxiv"
    raw_lower = raw_bib.lower()
    entry_type = entry_data.get("entrytype", entry.entry_type).lower()
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

_SKIP_ENTRY_TYPES = {"comment", "string", "preamble"}
_ENTRY_PATTERN = re.compile(r"@(?P<type>[A-Za-z]+)\s*{", re.IGNORECASE)


def _extract_entry_blocks(raw_bib: str) -> list[tuple[int, int, str, str]]:
    blocks: list[tuple[int, int, str, str]] = []
    pos = 0
    while True:
        match = _ENTRY_PATTERN.search(raw_bib, pos)
        if not match:
            break

        start = match.start()
        brace_pos = match.end() - 1
        depth = 0
        idx = brace_pos
        while idx < len(raw_bib):
            ch = raw_bib[idx]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = idx
                    break
            idx += 1
        else:
            raise ValueError("BibTeXエントリの解析に失敗しました。")

        block = raw_bib[start : end + 1]
        entry_type = match.group("type").lower()
        blocks.append((start, end + 1, block, entry_type))
        pos = end + 1

    return blocks


def _simplify_single_entry(
    entry_block: str,
    key_override: str | None,
    booktitle_mode: str,
    warning_callback: Callable[[str], None] | None,
) -> str:
    entry = _parse_bibtex_entry(entry_block)
    entry_data = _normalize_entry(entry)
    source = detect_source(entry, entry_data, entry_block)
    parser = _PARSERS[source]
    key = key_override or entry_data.get("id")
    if not key:
        raise ValueError("BibTeXエントリのキーが見つかりません。")

    return parser.parse(entry_data, key, booktitle_mode=booktitle_mode, warning_callback=warning_callback)


def simplify_bibtex_entry(
    raw_bib: str,
    new_key: str | None = None,
    booktitle_mode: str = "both",
    warning_callback: Callable[[str], None] | None = None,
) -> str:
    entry_blocks = _extract_entry_blocks(raw_bib)
    processable_blocks = [block for block in entry_blocks if block[3] not in _SKIP_ENTRY_TYPES]

    if not processable_blocks:
        raise ValueError("BibTeXエントリが見つかりませんでした。")

    if new_key and len(processable_blocks) != 1:
        raise ValueError("new_key は 1 つのエントリが含まれるときのみ利用できます。")

    result_parts: list[str] = []
    cursor = 0
    override_key = new_key if len(processable_blocks) == 1 else None

    for start, end, block, entry_type in entry_blocks:
        result_parts.append(raw_bib[cursor:start])
        if entry_type in _SKIP_ENTRY_TYPES:
            result_parts.append(block)
        else:
            simplified_entry = _simplify_single_entry(
                block,
                override_key,
                booktitle_mode,
                warning_callback,
            )
            result_parts.append(simplified_entry)
            override_key = None

        cursor = end

    result_parts.append(raw_bib[cursor:])
    return "".join(result_parts)
