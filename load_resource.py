import json
import logging


_journal_name_dict: dict[str, str] = None

def load_journal_name_dict() -> dict[str, str] | None:
    """ジャーナル名辞書をロードする。"""
    global _journal_name_dict
    if _journal_name_dict is None:
        filename: str = "resources/journal_names.json"
        try:
            with open(filename, "r") as f:
                _journal_name_dict = json.load(f)
        except FileNotFoundError:
            logging.error("%s が見つかりません。", filename)
            raise
    return _journal_name_dict