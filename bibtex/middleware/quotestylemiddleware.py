from bibtexparser.middlewares import BlockMiddleware
from bibtexparser.model import Entry

class QuoteStyleMiddleware(BlockMiddleware):
    """
    Write all fields as key=\"value\" except `title`
    which is written as key={{value}}.
    """

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Entry:
        # Rewrite all field values according to rules
        for field in entry.fields:
            key = field.key.lower()

            # Grab the raw text of the value
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

            # Overwrite field value for writing
            field.value = quoted

        return entry
