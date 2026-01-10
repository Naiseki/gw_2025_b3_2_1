# import pytest
# from bibtex.middleware.formatter import BibTeXFormatterMiddleware


# class TestCleanVenue:
#     """clean_venue メソッドのユニットテスト"""

#     @pytest.fixture
#     def middleware(self):
#         """BibTeXFormatterMiddleware のインスタンスをフィクスチャとして提供"""
#         return BibTeXFormatterMiddleware()

#     def test_remove_volume(self, middleware):
#         """Vol. を含む場合の削除テスト"""
#         assert middleware.clean_venue("Journal Name, Vol. 1") == "Journal Name"

#     def test_remove_volume_full(self, middleware):
#         """Volume を含む場合の削除テスト"""
#         assert middleware.clean_venue("Conference Name, Volume 2 Articles longs") == "Conference Name"

#     def test_remove_no(self, middleware):
#         """No. を含む場合の削除テスト"""
#         assert middleware.clean_venue("Journal, No. 3") == "Journal"

#     def test_case_insensitive(self, middleware):
#         """大文字小文字を問わないテスト"""
#         assert middleware.clean_venue("Journal, VOLUME 4") == "Journal"
#         assert middleware.clean_venue("Journal, vol. 5") == "Journal"

#     def test_no_match(self, middleware):
#         """マッチしない場合のテスト（ピリオドやカンマなし）"""
#         assert middleware.clean_venue("Journal Vol. 1") == "Journal Vol. 1"

#     def test_no_number(self, middleware):
#         """数字がない場合のテスト"""
#         assert middleware.clean_venue("Journal, Vol.") == "Journal, Vol."

#     def test_multiple_matches(self, middleware):
#         """複数のキーワードがある場合のテスト（最初のマッチで削除）"""
#         assert middleware.clean_venue("Journal, Vol. 1, No. 2") == "Journal"

#     def test_empty_string(self, middleware):
#         """空文字列のテスト"""
#         assert middleware.clean_venue("") == ""

#     def test_only_keywords(self, middleware):
#         """キーワードのみの場合のテスト"""
#         assert middleware.clean_venue(", Vol. 1") == ""
