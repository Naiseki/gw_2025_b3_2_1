import pytest
from unittest.mock import patch
from bibtex.middleware.formatter import BibTeXFormatterMiddleware


class TestBuildShortVenue:
    """build_short_venue メソッドのユニットテスト"""

    @pytest.fixture
    def middleware(self):
        """BibTeXFormatterMiddleware のインスタンスをフィクスチャとして提供"""
        return BibTeXFormatterMiddleware()

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_empty_long_name(self, mock_load, middleware):
        """空文字列のテスト"""
        mock_load.return_value = {}
        assert middleware.build_short_venue("") == ""

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_journal_exact_match(self, mock_load, middleware):
        """journal の完全一致テスト"""
        mock_load.return_value = {"Journal of Something": "JOS"}
        assert middleware.build_short_venue("Journal of Something", is_booktitle=False) == "JOS"

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_booktitle_partial_match(self, mock_load, middleware):
        """booktitle の部分一致テスト"""
        mock_load.return_value = {"Something Conference": "SC"}
        assert middleware.build_short_venue("Proceedings of Something Conference", is_booktitle=True) == "SC"

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_single_word(self, mock_load, middleware):
        """単語が1つの場合のテスト"""
        mock_load.return_value = {}
        assert middleware.build_short_venue("Nature", is_booktitle=False) == "Nature"

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_initials_generation(self, mock_load, middleware):
        """イニシャル生成のテスト"""
        mock_load.return_value = {}
        assert middleware.build_short_venue("International Conference on Something", is_booktitle=True) == "ICS"

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_warning_callback(self, mock_load, middleware):
        """警告コールバックのテスト"""
        mock_load.return_value = {}
        warnings = []
        middleware.build_short_venue("Unknown Venue", is_booktitle=False, warning_callback=lambda msg: warnings.append(msg))
        assert len(warnings) == 1
        assert "ジャーナル名" in warnings[0]

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_cleaning_colon(self, mock_load, middleware):
        """コロン以降削除のテスト"""
        mock_load.return_value = {"Journal": "J"}
        assert middleware.build_short_venue("Journal: Special Issue", is_booktitle=False) == "J"

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_cleaning_braces(self, mock_load, middleware):
        """波括弧削除のテスト"""
        mock_load.return_value = {"Journal A": "JA"}
        assert middleware.build_short_venue("Journal {A}", is_booktitle=False) == "JA"

    @patch('bibtex.middleware.formatter.load_venue_dict')
    def test_load_venue_dict_failure(self, mock_load, middleware):
        """辞書読み込み失敗のテスト"""
        mock_load.return_value = None
        with pytest.raises(ValueError, match="論文誌名辞書の読み込みに失敗しました。"):
            middleware.build_short_venue("Any Venue", is_booktitle=False)
