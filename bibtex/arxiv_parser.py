# bibtex/arxiv_parser.py

from .utils import BaseParser, extract_field, normalize_title, format_authors

class ArxivParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both") -> str:
        self.check_required_fields(raw_bib, ["title", "author", "year", "eprint", "url"])
        title = normalize_title(extract_field(raw_bib, "title") or "Unknown Title")
        author = extract_field(raw_bib, "author")
        eprint = extract_field(raw_bib, "eprint")  # arXiv ID が入ることが多い
        volume = extract_field(raw_bib, "volume")
        number = extract_field(raw_bib, "number")
        pages = extract_field(raw_bib, "pages")
        year = extract_field(raw_bib, "year")
        url = extract_field(raw_bib, "url")

        lines = [f"@article{{{new_key},"]
        lines.append(f"    title = {{{{{title}}}}},")
        if author:
            lines.append(f"    author = {{{format_authors(author)}}},")
        if eprint:
            lines.append(f"    journal = {{arXiv:{eprint}}},")
        if volume:
            lines.append(f"    volume = {{{volume}}},")
        if number:
            lines.append(f"    number = {{{number}}},")
        if pages:
            lines.append(f"    pages = {{{pages}}},")
        if year:
            lines.append(f"    year = {{{year}}},")
        if url:
            lines.append(f"    url = {{{url}}},")
        lines.append("}")
        return "\n".join(lines)