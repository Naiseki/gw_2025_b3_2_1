# bibtex/arxiv_parser.py

from typing import Callable
from .utils import BaseParser, extract_field, normalize_title, format_authors, build_short_journal

class ArticleParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
        # (フィールド名, 必須かどうか)のリスト
        field_names: list[tuple[str, bool]] = [
            ("title", True), 
            ("author", True), 
            ("journal", True), 
            ("volume", False), 
            ("number", False), 
            ("pages", False), 
            ("year", False), 
            ("url", False)
        ]
        fields = self.get_fields(raw_bib, field_names)

        title = normalize_title(fields.get("title", ""))
        author = format_authors(fields.get("author", ""))
        long_journal = fields.get("journal", "")
        if booktitle_mode == "short" or booktitle_mode == "both":
            short_journal = build_short_journal(long_journal, warning_callback)
        short_journal = build_short_journal(long_journal, warning_callback)
        url = (fields.get("url", "") or "").strip("<>").rstrip("/")

        lines = [f"@article{{{new_key},"]
        lines.append(f"    title = {{{{{title}}}}},")
        lines.append(f'    author = "{author}",')
        if short_journal and (booktitle_mode == "short" or booktitle_mode == "both"):
            lines.append(f'    journal = "{short_journal}",')
        if long_journal and (booktitle_mode == "long" or booktitle_mode == "both"):
            lines.append(f'    journal = "{long_journal}",')
        
        if "volume" in fields:
            lines.append(f'    volume = "{fields["volume"]}",')
        if "number" in fields:
            lines.append(f'    number = "{fields["number"]}",')
        if "pages" in fields:
            lines.append(f'    pages = "{fields["pages"]}",')
        if "year" in fields:
            lines.append(f'    year = "{fields["year"]}",')
        if url:
            lines.append(f'    url = "{url}",')
        lines.append("}")
        return "\n".join(lines)