import logging
import tomllib


_venue_dict: dict[str, str] = None

def load_venue_dict() -> dict[str, str] | None:
    """Venue名辞書をロードする。"""
    global _venue_dict
    if _venue_dict is None:
        filename: str = "resources/venue_abbreviations.toml"
        try:
            with open(filename, "rb") as f:
                _venue_dict = tomllib.load(f)
        except FileNotFoundError:
            logging.error("%s が見つかりません。", filename)
            raise
    return _venue_dict
