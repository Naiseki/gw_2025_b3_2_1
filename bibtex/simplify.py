# bibtex/simplify.py

from .utils import extract_field, normalize_title, BaseParser
from .arxiv_parser import ArxivParser
from .article_parser import ArticleParser
from .inproceedings_parser import InproceedingsParser
import re
from typing import Callable


def detect_source(raw_bib: str) -> str:
    """ ソース判定 """
    t = raw_bib.lower()
    if "@inproceedings" in t:
        return "inproceedings"
    if "@article" in t:
        return "article"
    if "arXiv" in raw_bib:
        return "arxiv"
    raise ValueError("対応していないBibTeXエントリです🙇‍♂️")

_PARSERS: dict[str, BaseParser] = {
    "article": ArticleParser(),
    "inproceedings": InproceedingsParser(),
    "arxiv": ArxivParser(),
}


def _extract_entry_key(raw_bib: str) -> str:
    m = re.search(r"@\w+\s*{\s*([^,\s]+)", raw_bib)
    if not m:
        raise ValueError("BibTeXエントリのキーが見つかりません。")
    return m.group(1)


def simplify_bibtex_entry(raw_bib: str, new_key: str | None = None, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
    source = detect_source(raw_bib)
    parser = _PARSERS[source]
    key = new_key or _extract_entry_key(raw_bib)
    return parser.parse(raw_bib, key, booktitle_mode=booktitle_mode, warning_callback=warning_callback)