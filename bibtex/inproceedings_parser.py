# bibtex/acl_parser.py

import re
from .utils import BaseParser, extract_field, normalize_title, build_short_booktitle, format_authors

class InproceedingsParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str, booktitle_mode: str = "both") -> str:
        self.check_required_fields(raw_bib, ["title", "author", "booktitle", "pages", "year", "url"])

        title = normalize_title(extract_field(raw_bib, "title") or "Unknown Title")
        author = extract_field(raw_bib, "author")

        long_booktitle = extract_field(raw_bib, "booktitle")
        long_booktitle_clean = re.sub(r"\s*\([^)]*\)\s*$", "", long_booktitle).strip()
        short_booktitle = build_short_booktitle(long_booktitle)

        year = extract_field(raw_bib, "year")
        pages = extract_field(raw_bib, "pages")
        url = (extract_field(raw_bib, "url") or "").strip("<>").rstrip("/")


        lines = [f"@inproceedings{{{new_key},"]
        if title:
            lines.append(f'    title = {{{{{title}}}}},')
        if author:
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

        if pages:
            lines.append(f'    pages = "{pages}",')
        if year:
            lines.append(f'    year = "{year}",')
        if url:
            lines.append(f'    url = "{url}",')
        lines.append("}")
        return "\n".join(lines)