# bibtex/arxiv_parser.py

from .utils import BaseParser, extract_field, normalize_title, format_authors, build_short_journal

class ArticleParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both") -> str:
        self.check_required_fields(raw_bib, ["title", "author", "journal", "volume", "number", "pages", "year", "url"])
        title = normalize_title(extract_field(raw_bib, "title") or "Unknown Title")
        author = extract_field(raw_bib, "author")
        long_journal = extract_field(raw_bib, "journal")
        short_journal = build_short_journal(long_journal)
        volume = extract_field(raw_bib, "volume")
        number = extract_field(raw_bib, "number")
        pages = extract_field(raw_bib, "pages")
        year = extract_field(raw_bib, "year")
        url = extract_field(raw_bib, "url")

        lines = [f"@article{{{new_key},"]
        lines.append(f"    title = {{{{{title}}}}},")
        if author:
            lines.append(f"    author = {{{format_authors(author)}}},")
        if long_journal:
            lines.append(f"    journal = {{{long_journal}}},")
        if short_journal:
            lines.append(f"    journal = {{{short_journal}}},")
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