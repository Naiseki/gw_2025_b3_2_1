# bibtex/acl_parser.py

import re
from .utils import BaseParser, extract_field, normalize_title, build_short_booktitle, format_authors

class ACLParser(BaseParser):
    def parse(self, raw_bib: str, new_key: str) -> str:
        title = normalize_title(extract_field(raw_bib, "title") or "Unknown Title")
        author = extract_field(raw_bib, "author")

        long_booktitle = extract_field(raw_bib, "booktitle")
        long_booktitle_clean = re.sub(r"\s*\([^)]*\)\s*$", "", long_booktitle).strip()
        short_booktitle = build_short_booktitle(long_booktitle)

        year = extract_field(raw_bib, "year")
        pages = extract_field(raw_bib, "pages")
        url = (extract_field(raw_bib, "url") or "").strip("<>").rstrip("/")


        lines = ["@inproceedings{KEY,"]
        if title:
            lines.append(f"    title = {{{{{title}}}}},")
        if author:
            lines.append(f"    author = \"{format_authors(author, line_break_after_and=True)}\",")

        if short_booktitle:
            lines.append(f"    booktitle = \"{short_booktitle}\",")
        if long_booktitle_clean:
            lines.append(f"    booktitle = \"{long_booktitle_clean}\",")
        if year:
            lines.append(f"    year = \"{year}\",")
        if pages:
            lines.append(f"    pages = \"{pages}\",")
        if url:
            lines.append(f"    url = \"{url}\",")
        lines.append("}")
        return "\n".join(lines)