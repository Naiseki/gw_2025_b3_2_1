from typing import Callable
from .utils import BaseParser, EntryData, normalize_title, format_authors


class ArxivParser(BaseParser):
    def parse(self, entry: EntryData, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
        field_names = [
            ("title", True), 
            ("author", True), 
            ("eprint", False), 
            ("journal", False),
            ("year", False),
            ("url", False), 
        ]
        fields = self.get_fields(entry, field_names)
        title = normalize_title(fields.get("title", ""))
        author = format_authors(fields.get("author", ""))
        url = (fields.get("url", "") or "").split("|", 1)[0].strip("<>").rstrip("/")
        eprint = fields.get("eprint")
        journal = ""
        if eprint:
            journal = f"arXiv:{eprint}"
        elif fields.get("journal"):
            journal = fields.get("journal")
        else:
            raise ValueError("arXivエントリには 'eprint' または 'journal' フィールドが必要です。")

        lines = [f"@article{{{new_key},"]
        lines.append(f"    title = {{{{{title}}}}},")
        lines.append(f'    author = "{author}",')
        if journal:
            lines.append(f'    journal = "{journal}",')
        if year := fields.get("year"):
            lines.append(f'    year = "{year}",')
        if url:
            lines.append(f'    url = "{url}",')
        lines.append("}")
        
        return "\n".join(lines)