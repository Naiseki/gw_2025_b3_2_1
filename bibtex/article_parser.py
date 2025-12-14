# bibtex/arxiv_parser.py

from typing import Callable
from .utils import BaseParser, extract_field, normalize_title, format_authors, build_short_journal

class ArticleParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
        required_fields: list[str] = ["title", "author", "journal", "volume", "number", "pages", "year", "url"]
        self.check_required_fields(raw_bib, required_fields)
        fields = self.get_fields(raw_bib, required_fields)
        title = normalize_title(fields["title"])
        author = format_authors(fields["author"])
        long_journal = fields["journal"]
        short_journal = build_short_journal(long_journal)
        url = (fields["url"] or "").strip("<>").rstrip("/")


        lines = [f"@article{{{new_key},"]
        lines.append(f"    title = {{{{{title}}}}},")
        lines.append(f'    author = "{author}",')
        lines.append(f'    journal = "{long_journal}",')
        lines.append(f'    journal = "{short_journal}",')
        lines.append(f'    volume = "{fields["volume"]}",')
        lines.append(f'    number = "{fields["number"]}",')
        lines.append(f'    pages = "{fields["pages"]}",')
        lines.append(f'    year = "{fields["year"]}",')
        lines.append(f'    url = "{url}",')
        lines.append("}")
        return "\n".join(lines)