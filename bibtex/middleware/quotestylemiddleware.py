from bibtexparser.middlewares import BlockMiddleware
from bibtexparser.model import Entry
import re

class QuoteStyleMiddleware(BlockMiddleware):
    """
    すべてのフィールドを key="value" の形式で書き込むが、`title` は原則 key={{value}} の形式で書き込む。
    ただし、タイトルに LaTeX コマンドが含まれる場合は key="value" 形式にする。
    """

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Entry:
        # ルールに従ってすべてのフィールド値を書き換える
        for field in entry.fields:
            key = field.key.lower()

            # 値の生テキストを取得
            raw_val = str(field.value)

            if key == "title":
                # LaTeXコマンド（例: {\a}）が含まれているかチェック
                if re.search(r'\{[^}]*\\', raw_val):
                    # "TITLE_VALUE"
                    quoted = f'"{raw_val}"'
                else:
                    # {{TITLE_VALUE}}
                    quoted = f"{{{{{raw_val}}}}}"
            # elif key == "pages":
            #     val = raw_val.replace(r"{\textendash}", "--")
            #     quoted = f'"{val}"'
            else:
                # "VALUE"
                quoted = f'"{raw_val}"'

            # 書き込みのためにフィールド値を上書き
            field.value = quoted

        return entry
