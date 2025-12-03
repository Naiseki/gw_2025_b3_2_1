# bibtex/simplify.py

from .utils import extract_field, normalize_title, BaseParser
from .acl_parser import ACLParser
from .arxiv_parser import ArxivParser


class GenericParser(BaseParser):
    """ACL でも arXiv でもなさそうなもの用のゆるいフォールバック。"""
    def parse(self, raw_bib: str, new_key: str) -> str:
        title = normalize_title(extract_field(raw_bib, "title") or "Unknown Title")
        author = extract_field(raw_bib, "author")
        journal = extract_field(raw_bib, "journal")
        booktitle = extract_field(raw_bib, "booktitle")
        year = extract_field(raw_bib, "year")
        url = extract_field(raw_bib, "url")

        entry_type = "article" if journal else "inproceedings"

        lines = [f"@{entry_type}{{{new_key},"]
        if title:
            lines.append(f"    title = {{{{{title}}}}},")
        if author:
            lines.append(f"    author = \"{author}\",")

        if journal:
            lines.append(f"    journal = \"{journal}\",")
        if booktitle:
            lines.append(f"    booktitle = \"{booktitle}\",")

        if year:
            lines.append(f"    year = \"{year}\",")

        if url:
            lines.append(f"    url = \"{url}\",")

        lines.append("}")
        return "\n".join(lines)


def detect_source(raw_bib: str) -> str:
    """ざっくりソース判定。必要に応じて強化していける部分。"""
    t = raw_bib.lower()
    if "arxiv" in t or "eprint" in t:
        return "arxiv"
    if "anthology" in t or "aclweb" in t or "aclanthology" in t:
        return "acl"
    return "generic"


_PARSERS: dict[str, BaseParser] = {
    "acl": ACLParser(),
    "arxiv": ArxivParser(),
    "generic": GenericParser(),
}


def simplify_bibtex_entry(raw_bib: str, new_key: str) -> str:
    """外から呼ぶのは基本これだけ。Slack からもこれを叩く。"""
    source = detect_source(raw_bib)
    parser = _PARSERS.get(source, _PARSERS["generic"])
    return parser.parse(raw_bib, new_key)