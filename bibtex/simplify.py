import re
from typing import Callable
from collections import defaultdict

import bibtexparser
from bibtexparser.middlewares.fieldkeys import NormalizeFieldKeys
from bibtexparser.middlewares.middleware import Middleware
from bibtexparser.middlewares.parsestack import default_parse_stack
from bibtexparser.library import Library
from bibtexparser.model import Entry as BibtexEntry
from bibtexparser.model import DuplicateFieldKeyBlock
from bibtexparser.model import ParsingFailedBlock
from bibtexparser.writer import BibtexFormat

from .arxiv_parser import ArxivParser
from .article_parser import ArticleParser
from .inproceedings_parser import InproceedingsParser
from .utils import BaseParser, EntryData
from .middleware.quotestylemiddleware import QuoteStyleMiddleware

_SKIP_ENTRY_TYPES = {"comment", "string", "preamble"}
_ENTRY_PATTERN = re.compile(r"@(?P<type>[A-Za-z]+)\s*{", re.IGNORECASE)
_LONGEST_FIELD_FOR_DUPES = {"booktitle", "journal"}

class PreferLongerFieldValue(Middleware):
    def __init__(self, field_names: set[str]):
        self.field_names = {name.lower() for name in field_names}

    def transform(self, library: Library) -> Library:
        print("PreferLongerFieldValue ミドルウェアを適用中...")
        print("len entries:", len(library.entries))
        for entry in library.entries:
            new_fields = []
            grouped = {}

            for f in entry.fields:
                key = f.key.lower()
                if key in self.field_names:
                    grouped.setdefault(key, []).append(f)
                else:
                    new_fields.append(f)

            for key, fields in grouped.items():
                if len(fields) == 1:
                    new_fields.append(fields[0])
                else:
                    best = max(
                        fields,
                        key=lambda f: len(str(f.value).strip())
                    )
                    print(f"フィールド '{key}' の値が重複しています。最長の値を採用します: {best.value}")
                    new_fields.append(best)

            entry.fields = new_fields

        return library


def _build_parse_stack() -> list[Middleware]:
    stack: list[Middleware] = default_parse_stack(allow_inplace_modification=True)
    stack.append(NormalizeFieldKeys())
    # stack.append(PreferLongerFieldValue(_LONGEST_FIELD_FOR_DUPES))
    return stack


def deduplicate_entry(entry: str, duplicate_keys: list[str]) -> str:
    keys = "|".join(map(re.escape, duplicate_keys))

    pattern = re.compile(
        rf'\b({keys})\b\s*=\s*(?:"(.*?)"|{{(.*?)}})\s*,',
        re.IGNORECASE | re.DOTALL,
    )

    matches = list(pattern.finditer(entry))
    if not matches:
        return entry

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

    # 元の entry から重複フィールドをすべて削除（後ろから）
    new_entry = entry
    for start, end in sorted(spans_to_remove, reverse=True):
        new_entry = new_entry[:start] + new_entry[end:]

    # 採用したフィールドを 1 回だけ追加（末尾手前）
    insert_pos = new_entry.rfind("}")
    if insert_pos == -1:
        return entry  # 念のため

    fields_str = ""
    for key, value in best_by_key.items():
        fields_str += f"  {key} = {{{value}}},\n"

    new_entry = (
        new_entry[:insert_pos]
        + fields_str
        + new_entry[insert_pos:]
    )

    return new_entry


def _needs_dedup(block: ParsingFailedBlock) -> bool:
    if not isinstance(block, DuplicateFieldKeyBlock):
        return False
    normalized_keys = {k.lower() for k in block.duplicate_keys}
    if normalized_keys & _LONGEST_FIELD_FOR_DUPES:
        return True
    return False


def _parse_bibtex_entries(raw_bib: str) -> Library:
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


def _normalize_entry(entry: BibtexEntry) -> EntryData:
    normalized_entry: EntryData = {
        "entrytype": entry.entry_type.lower(),
        "id": entry.key,
    }
    for field in entry.fields:
        value = field.value
        normalized_key = field.key.lower()
        normalized_value = value.strip() if isinstance(value, str) else str(value)
        existing = normalized_entry.get(normalized_key)
        if existing and normalized_key in _LONGEST_FIELD_FOR_DUPES:
            if len(normalized_value) <= len(existing):
                continue
        normalized_entry[normalized_key] = normalized_value
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
    first_entry = library.entries[0]
    for f in first_entry.fields:
        print(f"{f.key}: {f.value}")




    format = BibtexFormat()
    format.trailing_comma = True
    result = bibtexparser.write_string(library, unparse_stack=[QuoteStyleMiddleware()], bibtex_format=format)
    return result


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
