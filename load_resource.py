import json


_journal_name_dict: dict[str, str] = None

def load_journal_name_dict() -> dict[str, str] | None:
    global _journal_name_dict
    if _journal_name_dict is None:
        try:
            with open("resources/journal_names.json", "r") as f:
                _journal_name_dict = json.load(f)
        except FileNotFoundError:
            print("警告: resources/journal_names.json が見つかりません。")

    return _journal_name_dict