# bibtex/arxiv_parser.py

from typing import Callable
from .utils import BaseParser, extract_field, normalize_title, format_authors

class ArxivParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
        field_names = [
            ("title", True), 
            ("author", True), 
            ("eprint", True), 
            ("year", False),
            ("url", False), 
        ]
        fields = self.get_fields(raw_bib, field_names)
        title = normalize_title(fields.get("title", ""))
        author = format_authors(fields.get("author", ""))
        url = (fields.get("url", "") or "")
            .strip("<>")
            .rstrip("/")
            .split("|", 1)[0]

        lines = [f"@article{{{new_key},"]
        lines.append(f"    title = {{{{{title}}}}},")
        lines.append(f'    author = "{author}",')
        if "eprint" in fields:
            lines.append(f'    journal = "arXiv:{fields["eprint"]}",')
        if "year" in fields:
            lines.append(f'    year = "{fields.get("year")}",')
        if url:
            lines.append(f'    url = "{url}",')
        lines.append("}")
        
        return "\n".join(lines)