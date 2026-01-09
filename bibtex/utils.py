# bibtex/utils.py

import re
from abc import ABC, abstractmethod
from typing import Callable
from titlecase import titlecase
from load_resource import load_journal_name_dict


# def build_short_venue(long_name: str, is_booktitle: bool = True, warning_callback: Callable[[str], None] | None = None) -> str:
#     """journal/booktitle 共通の略称生成ロジック"""
#     if not long_name:
#         return ""

#     journal_name_dict = load_journal_name_dict()
#     if journal_name_dict is None:
#         raise ValueError("論文誌名辞書の読み込みに失敗しました。")

#     # --- 共通のクリーニング ---
#     # 1. コロン以降を削除
#     name = long_name.split(":", 1)[0]
#     # 2. 波括弧 {A} -> A
#     name = re.sub(r"{(.+?)}", r"\1", name)
#     # 3. カンマ、ピリオドを削除
#     name = name.translate(str.maketrans("", "", ",.")).strip()

#     # --- 個別のノイズ削除 ---
#     if is_booktitle:
#         # Proceedings of... などの前置きを削除
#         pattern = r'^(?:In\s+)?(?:Proceedings|Proc\.)\s+of\s+(?:the\s+)?(?:\d{4}|\d+(?:st|nd|rd|th))?\s*'
#         name = re.sub(pattern, '', name, flags=re.IGNORECASE | re.VERBOSE)
#     else:
#         # Vol.XX, No.XX, (20xx) などを削除
#         pattern = r'\s+(?:Vol(?:ume)?|No|Issue)\.?\s*\d+|\s*\(\d{4}\)'
#         name = re.sub(pattern, '', name, flags=re.IGNORECASE)

#     name = name.strip()
#     words = name.split()
#     if not words:
#         return ""

#     # --- 1. 辞書検索 ---
#     # booktitleの場合は部分一致（後ろから削る）も試みる
#     if is_booktitle:
#         max_drop = 4
#         for i in range(min(max_drop, len(words))):
#             key = " ".join(words[i:])
#             if key in journal_name_dict:
#                 return journal_name_dict[key]
#     else:
#         if name in journal_name_dict:
#             return journal_name_dict[name]

#     # --- 2. 単語が1つの場合はそのまま ---
#     if len(words) == 1:
#         return name

#     # --- 3. 最終手段：イニシャル抽出 ---
#     venue_type = "会議名" if is_booktitle else "ジャーナル名"
#     if warning_callback:
#         warning_callback(f"*! ! ! {venue_type}が辞書に見つからなかったため、イニシャルで作成します。*")

#     initials = "".join(word[0] for word in words if word and word[0].isupper())
#     return initials