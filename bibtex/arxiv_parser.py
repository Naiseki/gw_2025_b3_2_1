# bibtex/arxiv_parser.py

from typing import Callable
from .utils import BaseParser, extract_field, normalize_title, format_authors

class ArxivParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
        required_fields: list[str] = ["title", "author", "year", "eprint", "url"]
        self.check_required_fields(raw_bib, required_fields)
        fields = self.get_fields(raw_bib, required_fields)
        title = normalize_title(fields["title"])
        author = format_authors(fields["author"])
        eprint = fields["eprint"]  # arXiv ID が入ることが多い
        volume = fields.get("volume")
        number = fields.get("number")
        pages = fields.get("pages")
        year = fields.get("year")
        url = (fields.get("url") or "").strip("<>").rstrip("/")

        lines = [
            f"@article{{{new_key},",
            f"    title = {{{{{title}}}}},",
        	f'    author = "{author}",',
        	f'    journal = "arXiv:{eprint}",',
        	f'    volume = "{volume}",',
        	f'    number = "{number}",',
        	f'    pages = "{pages}",',
        	f'    year = "{year}",',
        	f'    url = "{url}",',
        	"}"
        ]
        return "\n".join(lines)