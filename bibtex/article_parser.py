# bibtex/arxiv_parser.py

from .utils import BaseParser, extract_field, normalize_title, format_authors

class ArxivParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both") -> str:
        self.check_required_fields(raw_bib, ["title", "author", "journal", "volume", "number", "pages","year", "url"])
        title = normalize_title(extract_field(raw_bib, "title") or "Unknown Title")
        author = extract_field(raw_bib, "author")
        journal = f"arXiv:{extract_field(raw_bib, 'eprint')}" if extract_field(raw_bib, "eprint") else ""
        volume = extract_field(raw_bib, "volume")
        number = extract_field(raw_bib, "number")
        pages = extract_field(raw_bib, "pages")
        year = extract_field(raw_bib, "year")
        url = extract_field(raw_bib, "url")

        lines = [f"@article{{{new_key},",
            f"    title = {{{{{title}}}}},",
            f"    author = {{{format_authors(author)}}},"
            f"    journal = {{{journal}}},"
            f"    volume = {{{volume}}},"
            f"    number = {{{number}}},"
            f"    pages = {{{pages}}},"
            f"    year = {{{year}}},"
            f"    url = {{{url}}},"
            "}"
        ]
        return "\n".join(lines)