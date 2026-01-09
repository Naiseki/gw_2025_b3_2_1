from typing import Callable
from bibtexparser.model import Entry
from bibtexparser.middlewares.middleware import BlockMiddleware
from titlecase import titlecase, set_small_word_list
import re


class TitleFormatterMiddleware(BlockMiddleware):
    """タイトルフィールドにtitlecaseを適用するMiddleware"""

    def __init__(self, warning_callback: Callable[[str], None] | None = None, *args, **kwargs):
        """初期化"""
        super().__init__(*args, **kwargs)
        self.warning_callback = warning_callback
        new_small_words = r'a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|v\.?|via|vs\.?|with'
        set_small_word_list(new_small_words)
    

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Entry:
        """エントリのtitleフィールドを整形する"""
        if "title" in entry.fields_dict:
            title = entry.fields_dict["title"].value

            # LaTeXコマンドのチェック (例: {\a})
            if self.warning_callback and re.search(r'\{[^}]*\\', title):
                msg = (
                    f"タイトルに `{{\\a}}` のようなLaTeX コマンドが含まれている可能性があります: `{title}`\n"
                    r"正しく整形されない可能性が高いため、ご注意ください🙇‍♂️"
                )
                self.warning_callback(msg)

            formatted_title = self._format_title(title)
            
            # titleフィールドを更新
            for field in entry.fields:
                if field.key.lower() == "title":
                    field.value = formatted_title
                    break
        
        return entry
    
    def _format_title(self, title: str) -> str:
        """タイトルをtitlecase形式に整形"""
        # 保護する部分を保存
        protected_parts = []
        is_latex = bool(re.search(r'\{[^}]*\\', title))
        
        def protect_match(match):
            protected_parts.append(match.group(0))
            return f"<<protected-{len(protected_parts)-1}>>"
        
        # 1. 中括弧で囲まれた部分を保護
        def protect_braces(match):
            if is_latex:
                # LaTeXコマンドがある場合は中括弧を保持
                content = match.group(0)
            else:
                # 通常の場合は中括弧を削除
                content = match.group(1)
            protected_parts.append(content)
            return f"<<protected-{len(protected_parts)-1}>>"
        
        title = re.sub(r'\{([^}]+)\}', protect_braces, title)
        
        # LaTeXコマンドが含まれている場合は、titlecaseを適用せずにそのまま返す
        if is_latex:
            # 保護された部分を復元（is_latexの場合は中括弧ごと保護されている）
            for i, protected in enumerate(protected_parts):
                title = title.replace(f"<<protected-{i}>>", protected)
            return title

        # 2. コロン（:または：）の前にある2文字以上の連続大文字単語を保護
        # コロンの位置を探す
        colon_match = re.search(r'[:：]', title)
        if colon_match:
            before_colon = title[:colon_match.start()]
            after_colon = title[colon_match.start():]
            
            # コロン前の部分で2文字以上の連続大文字を保護
            before_colon = re.sub(r'\b([A-Z]{2,})\b', protect_match, before_colon)
            
            title = before_colon + after_colon
        
        # titlecaseライブラリを使用
        formatted = titlecase(title)
        
        # 保護された部分を復元
        for i, protected in enumerate(protected_parts):
            formatted = formatted.replace(f"<<protected-{i}>>", protected)
        
        return formatted
