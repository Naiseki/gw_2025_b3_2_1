from bibtexparser.middlewares import BlockMiddleware
from bibtexparser.model import Entry

class QuoteStyleMiddleware(BlockMiddleware):
    """
    すべてのフィールドを key="value" の形式で書き込むが、`title` は key={{value}} の形式で書き込む。
    """

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Entry:
        # ルールに従ってすべてのフィールド値を書き換える
        for field in entry.fields:
            key = field.key.lower()

            # 値の生テキストを取得
            raw_val = str(field.value)

            if key == "title":
                # {{TITLE_VALUE}}
                quoted = f"{{{{{raw_val}}}}}"
            elif key == "pages":
                val = raw_val.replace(r"{\textendash}", "--")
                quoted = f'"{val}"'
            else:
                # "VALUE"
                quoted = f'"{raw_val}"'

            # 書き込みのためにフィールド値を上書き
            field.value = quoted

        return entry
