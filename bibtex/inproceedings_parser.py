# bibtex/acl_parser.py

import re
from typing import Callable
from .utils import BaseParser, extract_field, normalize_title, build_short_booktitle, format_authors

class InproceedingsParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
        required_fields: list[str] = ["title", "author", "booktitle", "pages", "year", "url"]
        self.check_required_fields(raw_bib, required_fields)
        fields = self.get_fields(raw_bib, required_fields)


        title = normalize_title(fields["title"])
        author = fields["author"]

        long_booktitle = fields["booktitle"]
        long_booktitle_clean = re.sub(r"\s*\([^)]*\)\s*$", "", long_booktitle).strip()
        short_booktitle = build_short_booktitle(long_booktitle_clean, warning_callback)

        year = fields["year"]
        pages = fields["pages"]
        url = (fields["url"] or "").strip("<>").rstrip("/")


        lines = [f"@inproceedings{{{new_key},"]
        lines.append(f'    title = {{{{{title}}}}},')
        lines.append(f'    author = "{format_authors(author)}",')

        # booktitle_modeに応じて出力を切り替え
        if booktitle_mode == "short" and short_booktitle:
            lines.append(f'    booktitle = "{short_booktitle}",')
        elif booktitle_mode == "long" and long_booktitle_clean:
            lines.append(f'    booktitle = "{long_booktitle_clean}",')
        else:  # both
            if short_booktitle:
                lines.append(f'    booktitle = "{short_booktitle}",')
            if long_booktitle_clean:
                lines.append(f'    booktitle = "{long_booktitle_clean}",')

        lines.append(f'    pages = "{pages}",')
        lines.append(f'    year = "{year}",')
        lines.append(f'    url = "{url}",')
        lines.append("}")
        return "\n".join(lines)