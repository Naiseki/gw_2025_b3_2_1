import re
from typing import Callable
from bibtexparser.model import Entry
from bibtexparser.middlewares.middleware import BlockMiddleware
from bibtexparser.model import Field
from load_resource import load_venue_dict


class BibTeXFormatterMiddleware(BlockMiddleware):
    """BibTeX整形用のMiddleware"""
    
    # フィールドの順序定義
    ARTICLE_ORDER = ["title", "author", "journal", "volume", "number", "pages", "year", "url"]
    ARXIV_ORDER = ["title", "author", "journal", "year", "url"]
    INPROCEEDINGS_ORDER = ["title", "author", "booktitle", "pages", "year", "url"]
    
    def __init__(self, abbreviation_mode: str = "both", warning_callback: Callable[[str], None] | None = None, *args, **kwargs):
        """初期化
        
        Args:
            abbreviation_mode: "short" (略称のみ), "long" (正式名称のみ), "both" (両方、略称を先に)
            warning_callback: 警告メッセージを通知するコールバック関数
        """
        super().__init__(*args, **kwargs)
        self.abbreviation_mode = abbreviation_mode
        self.warning_callback = warning_callback
    
    def transform_entry(self, entry: Entry, *args, **kwargs) -> Entry:
        """エントリを整形する"""
        # arXivの場合、journalフィールドをeprintから作成
        is_arxiv = self._is_arxiv(entry)
        if is_arxiv:
            entry = self._create_arxiv_journal(entry)
            entry.entry_type = "article"
        
        # URLがない場合、DOIからURLを作成
        entry = self._create_url_from_doi(entry)
        
        # URLの整形
        entry = self._clean_url(entry)

        # フィールドの順序整理
        if is_arxiv:
            entry = self._reorder_fields(entry, self.ARXIV_ORDER)
        if entry.entry_type.lower() == "article":
            entry = self._reorder_fields(entry, self.ARTICLE_ORDER)
        elif entry.entry_type.lower() == "inproceedings":
            entry = self._reorder_fields(entry, self.INPROCEEDINGS_ORDER)

        # 略称フィールドの追加
        if not is_arxiv:
            entry = self._add_abbreviated_fields(entry)
        
        return entry

    def _is_arxiv(self, entry: Entry) -> bool:
        """arXiv論文かどうか判定"""
        return (prefix := entry.fields_dict.get("archiveprefix")) and prefix.value == "arXiv"
    
    def _create_arxiv_journal(self, entry: Entry) -> Entry:
        """arXivのjournalフィールドをeprintから作成"""
        if "journal" not in entry.fields_dict and "eprint" in entry.fields_dict:
            eprint_value = entry.fields_dict["eprint"].value
            journal_value = f"arXiv:{eprint_value}"
            # journalフィールドを追加
            entry.fields.append(Field(key="journal", value=journal_value))
        return entry
    
    def _create_url_from_doi(self, entry: Entry) -> Entry:
        """URLがない場合、DOIからURLを作成"""
        if "url" not in entry.fields_dict and "doi" in entry.fields_dict:
            doi_value = entry.fields_dict["doi"].value
            # DOIの値がURL形式でない場合、https://doi.org/ を付与
            if not doi_value.startswith("http"):
                url_value = f"https://doi.org/{doi_value}"
            else:
                url_value = doi_value
            
            entry.fields.append(Field(key="url", value=url_value))
        return entry
    
    def _clean_url(self, entry: Entry) -> Entry:
        """URLの整形：最後のスラッシュを削除、,|の手前の1個目を採用"""
        if "url" in entry.fields_dict:
            url = entry.fields_dict["url"].value
            
            # |の手前の1個目を採用
            if "|" in url:
                url = url.split("|", 1)[0]
            
            # 最後のスラッシュを削除
            url = url.strip("<>").rstrip("/")
            
            # 既存のurlフィールドを更新
            for field in entry.fields:
                if field.key.lower() == "url":
                    field.value = url
                    break
        return entry
    
    def _reorder_fields(self, entry: Entry, field_order: list) -> Entry:
        """
        フィールドを指定された順序に並び替え
        指定されていないフィールドは無視
        """
        ordered_fields = []
        existing_fields = {field.key: field for field in entry.fields}
        
        # 指定された順序でフィールドを追加
        for field_key in field_order:
            if field_key in existing_fields:
                ordered_fields.append(existing_fields[field_key])

        entry.fields = ordered_fields
        return entry
    
    def _add_abbreviated_fields(self, entry: Entry) -> Entry:
        """journal/booktitleに略称がある場合、モードに応じてフィールドを作成"""
    
        # 対象フィールド
        target_fields = ["journal", "booktitle"]

        for key in target_fields:
            if key not in entry.fields_dict:
                continue

            # 現在の値を処理
            original_value = str(entry.fields_dict[key].value)
            cleaned_value = self.clean_venue(original_value)
            long_name, short_name = self._extract_abbreviation(cleaned_value)

            # 略称が必要なモードで、かつ抽出できなかった場合は生成を試みる
            if self.abbreviation_mode != "long" and not short_name:
                try:
                    short_name = self.build_short_venue(long_name, is_booktitle=(key=="booktitle"), warning_callback=self.warning_callback)
                except ValueError:
                    pass

            # booktitleの場合のみ "Proc. of " を付与するなどの個別調整
            display_short = short_name
            if key == "booktitle" and short_name:
                display_short = f"Proc. of {short_name}"

            # 表示モードに応じた最終的な値の決定
            final_long = "" if self.abbreviation_mode == "short" else long_name
        
            # フィールドリストの更新
            new_fields = []
            for field in entry.fields:
                if field.key.lower() == key:
                    if display_short and display_short != final_long:
                        new_fields.append(Field(key=key, value=display_short))
                    if final_long:
                        new_fields.append(Field(key=key, value=final_long))
                else:
                    new_fields.append(field)
            entry.fields = new_fields

        return entry
    
    def _extract_abbreviation(self, text: str) -> tuple[str, str | None]:
        """
        文字列末尾のカッコ部分を抽出し、略称候補として整形する。
        戻り値: (カッコを除去した文字列, 整形された略称)
        """
        # 末尾の (xxx) または （xxx） を検出
        match = re.search(r'\s*[\(（]([^\)）]*)[\)）]\s*$', text)
        if match:
            content = match.group(1)
            cleaned_text = text[:match.start()].strip()
            
            # 略称の整形
            # 1. {}を除去
            abbr = content.replace("{", "").replace("}", "")
            # 2. 年号を除去 (末尾の数字4桁、およびその前の区切り文字)
            abbr = re.sub(r'[\s\-\u2013\u2014]*\d{4}$', '', abbr).strip()
            
            if abbr and abbr.isupper():
                return cleaned_text, abbr
            else:
                # 略称が空になった場合（年号のみだった場合など）はNoneを返す
                return cleaned_text, None
        
        return text, None

    
    def clean_venue(self, text: str) -> str:
        """
        Volume, Vol, Part などの付加情報を、後ろの説明文（Articles longs等）含めて削除する。
        """
        # キーワードリスト
        keywords = r"Volume|Vol\.?|No\.?"
    
        # 正規表現の解説:
        # [,.]\s+   : ピリオドまたはカンマの後に1つ以上のスペース
        # ({keywords})   : 指定したキーワードのいずれか
        # \s+            : 1つ以上のスペース
        # \d+            : 数字（巻数など）
        # (.*)$          : その後、行末までの全文字（ハイフンや "Articles longs" など）
        pattern = rf"[,.]\s+({keywords})\s+\d+.*$"
    
        # re.IGNORECASE: 大文字小文字を問わない
        # re.DOTALL は使わない（改行の手前までで止めるため）
        cleaned = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

        return cleaned

    def build_short_venue(self, long_name: str, is_booktitle: bool = True, warning_callback: Callable[[str], None] | None = None) -> str:
        """journal/booktitle 共通の略称生成ロジック"""
        if not long_name:
            return ""

        venue_dict = load_venue_dict()
        if venue_dict is None:
            raise ValueError("論文誌名辞書の読み込みに失敗しました。")

        # --- 共通のクリーニング ---
        # 1. コロン以降を削除
        name = long_name.split(":", 1)[0]
        # 2. 波括弧 {A} -> A
        name = re.sub(r"{(.+?)}", r"\1", name)
        # 3. カンマ、ピリオドを削除
        name = name.translate(str.maketrans("", "", ",.")).strip()

        # --- 個別のノイズ削除 ---
        if is_booktitle:
            # Proceedings of... などの前置きを削除
            pattern = r'^(?:In\s+)?(?:Proceedings|Proc\.)\s+of\s+(?:the\s+)?(?:\d{4}|\d+(?:st|nd|rd|th))?\s*'
            name = re.sub(pattern, '', name, flags=re.IGNORECASE | re.VERBOSE)
        else:
            # Vol.XX, No.XX, (20xx) などを削除
            pattern = r'\s+(?:Vol(?:ume)?|No|Issue)\.?\s*\d+|\s*\(\d{4}\)'
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)

        name = name.strip()
        words = name.split()
        if not words:
            return ""

        # --- 1. 辞書検索 ---
        # booktitleの場合は部分一致（後ろから削る）も試みる
        if is_booktitle:
            max_drop = 4
            for i in range(min(max_drop, len(words))):
                key = " ".join(words[i:])
                if key in venue_dict:
                    return venue_dict[key]
        else:
            if name in venue_dict:
                return venue_dict[name]

        # --- 2. 単語が1つの場合はそのまま ---
        if len(words) == 1:
            return name

        # --- 3. 最終手段：イニシャル抽出 ---
        venue_type = "会議名" if is_booktitle else "ジャーナル名"
        if warning_callback:
            warning_callback(f"*! ! ! {venue_type}が辞書に見つからなかったため、イニシャルで作成します。*")

        initials = "".join(word[0] for word in words if word and word[0].isupper())
        return initials