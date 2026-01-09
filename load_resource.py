import json
import logging


_venue_dict: dict[str, str] = None

def load_venue_dict() -> dict[str, str] | None:
    """Venue名辞書をロードする。"""
    global _venue_dict
    if _venue_dict is None:
        filename: str = "resources/venue_abbreviations.json"
        try:
            with open(filename, "r") as f:
                _venue_dict = json.load(f)
        except FileNotFoundError:
            logging.error("%s が見つかりません。", filename)
            raise
    return _venue_dict