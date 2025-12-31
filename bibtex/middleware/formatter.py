import re
from typing import Callable
from bibtexparser.model import Entry
from bibtexparser.middlewares.middleware import BlockMiddleware
from bibtexparser.model import Field
from ..utils import build_short_booktitle, build_short_journal


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
        fields_dict = entry.fields_dict
        
        # journalフィールドの処理
        if "journal" in fields_dict:
            long_journal = str(fields_dict["journal"].value)
            
            # 略称抽出（カッコ内から）
            long_journal, short_journal = self._extract_abbreviation(long_journal)
            
            if not short_journal:
                try:
                    short_journal = build_short_journal(long_journal, warning_callback=self.warning_callback)
                except ValueError:
                    pass

            if short_journal and short_journal != long_journal:
                # abbreviation_modeに応じて配置を決定
                new_fields = []
                for field in entry.fields:
                    if field.key.lower() == "journal":
                        if self.abbreviation_mode == "short" or self.abbreviation_mode == "both":
                            new_fields.append(Field(key="journal", value=short_journal))
                        if self.abbreviation_mode == "long" or self.abbreviation_mode == "both":
                            new_fields.append(Field(key="journal", value=long_journal))
                    else:
                        new_fields.append(field)
                entry.fields = new_fields
        
        # booktitleフィールドの処理
        if "booktitle" in fields_dict:
            long_booktitle = str(fields_dict["booktitle"].value)
            
            # : 以降を除去
            if ":" in long_booktitle:
                long_booktitle = long_booktitle.split(":", 1)[0].strip()
            
            # 略称抽出（カッコ内から）
            long_booktitle, short_booktitle = self._extract_abbreviation(long_booktitle)
            
            if not short_booktitle:
                try:
                    short_booktitle = build_short_booktitle(long_booktitle, warning_callback=self.warning_callback)
                except ValueError:
                    pass

            if short_booktitle and short_booktitle != long_booktitle:
                    # abbreviation_modeに応じて配置を決定
                    new_fields = []
                    for field in entry.fields:
                        if field.key.lower() == "booktitle":
                            if self.abbreviation_mode == "short" or self.abbreviation_mode == "both":
                                new_fields.append(Field(key="booktitle", value="Proc. of " + short_booktitle))
                            if self.abbreviation_mode == "long" or self.abbreviation_mode == "both":
                                new_fields.append(Field(key="booktitle", value=long_booktitle))
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
            
            if abbr:
                return cleaned_text, abbr
            else:
                # 略称が空になった場合（年号のみだった場合など）はNoneを返す
                return cleaned_text, None
        
        return text, None
