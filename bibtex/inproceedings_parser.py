import re
from typing import Callable
from .utils import BaseParser, EntryData, normalize_title, build_short_booktitle, format_authors
from bibtexparser.model import Entry as BibtexEntry
from bibtexparser.model import Field


class InproceedingsParser(BaseParser):
    def format(self, entry: BibtexEntry, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> list[Field]:
        pass

    def parse(self, entry: EntryData, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
        field_names = [
            ("title", True), 
            ("author", True), 
            ("booktitle", True), 
            ("pages", False), 
            ("year", False), 
            ("url", False)
        ]
        fields = self.get_fields(entry, field_names)


        title = normalize_title(fields.get("title", ""))
        author = fields.get("author", "")

        long_booktitle = fields.get("booktitle", "")
        long_booktitle_clean = re.sub(r"\s*\([^)]*\)\s*$", "", long_booktitle).strip()
        short_booktitle = build_short_booktitle(long_booktitle_clean, warning_callback) if booktitle_mode == "short" or booktitle_mode == "both" else ""

        url = (fields.get("url", "") or "").split("|", 1)[0].strip("<>").rstrip("/")


        lines = [f"@inproceedings{{{new_key},"]
        lines.append(f'    title = {{{{{title}}}}},')
        lines.append(f'    author = "{format_authors(author)}",')

        # booktitle_modeに応じて出力を切り替え
        if short_booktitle and (booktitle_mode == "short" or booktitle_mode == "both"):
            lines.append(f'    booktitle = "{short_booktitle}",')
        if long_booktitle_clean and (booktitle_mode == "long" or booktitle_mode == "both"):
            lines.append(f'    booktitle = "{long_booktitle_clean}",')

        if pages := fields.get("pages"):
            lines.append(f'    pages = "{pages}",')
        if year := fields.get("year"):
            lines.append(f'    year = "{year}",')
        if url:
            lines.append(f'    url = "{url}",')
        lines.append("}")
        return "\n".join(lines)