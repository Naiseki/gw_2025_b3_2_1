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
                # Double curly braces
                quoted = f"{{{{{raw_val}}}}}"
            else:
                # Standard double quotes
                # Escape any existing quotes if needed
                # (simple replace; for more robust BibTeX escaping, adjust as needed)
                safe_val = raw_val.replace('"', '\\"')
                quoted = f"\"{safe_val}\""

            # Overwrite field value for writing
            field.value = quoted

        return entry
