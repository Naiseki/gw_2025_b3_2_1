# bibtex/arxiv_parser.py

from .utils import (
    BaseParser,
    extract_field,
    normalize_title,
    format_authors,
)

class JNLPParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, use_short: bool = False) -> str:
        title = normalize_title(extract_field(raw_bib, "title") or "Unknown Title")
        author = extract_field(raw_bib, "author")
        journal = extract_field(raw_bib, "journal")
        volume = extract_field(raw_bib, "volume")
        number = extract_field(raw_bib, "number")
        pages = extract_field(raw_bib, "pages")
        year = extract_field(raw_bib, "year")

        lines = [f"@article{{{new_key},"]
        if title:
            lines.append(f"    title = {{{{{title}}}}},")
        if author:
            lines.append(f"    author = {{{format_authors(author, threshold=999)}}},")
        if journal:
            lines.append(f"    journal = {{{journal}}},")
        if volume:
            lines.append(f"    volume = {{{volume}}},")
        if number:
            lines.append(f"    number = {{{number}}},")
        if pages:
            lines.append(f"    pages = {{{pages}}},")
        if year:
            lines.append(f"    year = {{{year}}},")
        lines.append("}")
        return "\n".join(lines)