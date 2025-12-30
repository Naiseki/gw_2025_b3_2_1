from typing import Callable
from .utils import BaseParser, EntryData, normalize_title, format_authors, build_short_journal


class ArticleParser(BaseParser):
    def parse(self, entry: EntryData, new_key: str, booktitle_mode: str = "both", warning_callback: Callable[[str], None] | None = None) -> str:
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
        fields = self.get_fields(entry, field_names)

        title = normalize_title(fields.get("title", ""))
        author = format_authors(fields.get("author", ""))
        long_journal = fields.get("journal", "")
        short_journal = build_short_journal(long_journal, warning_callback) if booktitle_mode == "short" or booktitle_mode == "both" else ""
        url = (fields.get("url", "") or "").split("|", 1)[0].strip("<>").rstrip("/")

        lines = [f"@article{{{new_key},"]
        lines.append(f"    title = {{{{{title}}}}},")
        lines.append(f'    author = "{author}",')
        if short_journal and (booktitle_mode == "short" or booktitle_mode == "both"):
            lines.append(f'    journal = "{short_journal}",')
        if long_journal and (booktitle_mode == "long" or booktitle_mode == "both"):
            lines.append(f'    journal = "{long_journal}",')
        
        if volume := fields.get("volume"):
            lines.append(f'    volume = "{volume}",')
        if number := fields.get("number"):
            lines.append(f'    number = "{number}",')
        if pages := fields.get("pages"):
            lines.append(f'    pages = "{pages}",')
        if year := fields.get("year"):
            lines.append(f'    year = "{year}",')
        if url:
            lines.append(f'    url = "{url}",')
        lines.append("}")
        return "\n".join(lines)