import pytest
from unittest.mock import patch
from bibtexparser.model import Entry, Field
from bibtex.middleware.formatter import BibTeXFormatterMiddleware

@pytest.fixture
def mock_journal_dict():
    # load_resource.py 内の load_venue_dict を mock する
    with patch("load_resource.load_venue_dict") as mocked:
        mocked.return_value = {
            "Journal of Artificial Intelligence Research": "JAIR",
            "International Conference on Machine Learning": "ICML"
        }
        yield mocked

def create_entry(entry_type="article", **fields):
    entry = Entry(entry_type, "key", [])
    for k, v in fields.items():
        entry.fields.append(Field(key=k, value=v))
    return entry

def test_add_abbreviated_fields_both_journal(mock_journal_dict):
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(journal="Journal of Artificial Intelligence Research")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    assert journal_fields == ["JAIR", "Journal of Artificial Intelligence Research"]

def test_add_abbreviated_fields_short_journal(mock_journal_dict):
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="short")
    entry = create_entry(journal="Journal of Artificial Intelligence Research")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    assert journal_fields == ["JAIR"]

def test_add_abbreviated_fields_long_journal(mock_journal_dict):
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="long")
    entry = create_entry(journal="Journal of Artificial Intelligence Research")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    assert journal_fields == ["Journal of Artificial Intelligence Research"]

def test_extract_abbreviation_from_parentheses():
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    # カッコ内に略称がある場合
    entry = create_entry(journal="Conference on Computer Vision and Pattern Recognition (CVPR)")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    assert journal_fields == ["CVPR", "Conference on Computer Vision and Pattern Recognition"]

def test_extract_abbreviation_with_year():
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    # 年号が含まれる場合
    entry = create_entry(journal="Conference on Computer Vision and Pattern Recognition (CVPR 2024)")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    assert journal_fields == ["CVPR", "Conference on Computer Vision and Pattern Recognition"]

def test_booktitle_proc_of(mock_journal_dict):
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(entry_type="inproceedings", booktitle="International Conference on Machine Learning")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    booktitle_fields = [f.value for f in new_entry.fields if f.key == "booktitle"]
    # booktitle の場合は "Proc. of " が付与される
    assert booktitle_fields == ["Proc. of ICML", "International Conference on Machine Learning"]

def test_no_abbreviation_found_but_initials_generated(mock_journal_dict):
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(journal="Unknown Journal Name")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    # 辞書にない場合、イニシャル (UJN) が生成される
    assert journal_fields == ["UJN", "Unknown Journal Name"]

def test_single_word_journal_no_duplicate(mock_journal_dict):
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(journal="Nature")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    # 単語一つの場合は略称も同じになるため、重複して追加されない
    assert journal_fields == ["Nature"]

def test_abbreviation_mode_invalid_still_works():
    # 不正なモードの場合は long 扱い（コード上 final_long が "" にならないため）
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="invalid")
    entry = create_entry(journal="Journal of Artificial Intelligence Research (JAIR)")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    # 実装上、bothと同じ挙動になる（display_shortとfinal_longが両方追加される）
    assert journal_fields == ["JAIR", "Journal of Artificial Intelligence Research"]

def test_warning_callback_on_initials(mock_journal_dict):
    warnings = []
    def callback(msg):
        warnings.append(msg)
    
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both", warning_callback=callback)
    entry = create_entry(journal="Unknown Journal Name")
    
    middleware._add_abbreviated_fields(entry)
    
    assert len(warnings) > 0
    assert "イニシャルで作成します" in warnings[0]

def test_colon_in_journal_name(mock_journal_dict):
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(journal="Journal of Testing: An Experimental Approach")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    # コロンが含まれていても正しくイニシャルが生成される
    assert journal_fields == ["JT", "Journal of Testing: An Experimental Approach"]

def test_bert_booktitle():
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(entry_type="inproceedings", booktitle="Proceedings of the 2019 Conference of the North {A}merican Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    booktitle_fields = [f.value for f in new_entry.fields if f.key == "booktitle"]
    assert booktitle_fields == ["Proc. of NAACL", "Proceedings of the 2019 Conference of the North {A}merican Chapter of the Association for Computational Linguistics: Human Language Technologies"]

def test_taln():
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(entry_type="inproceedings", booktitle="Actes des 32ème Conférence sur le Traitement Automatique des Langues Naturelles (TALN), volume 1 : articles scientifiques originaux")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    booktitle_fields = [f.value for f in new_entry.fields if f.key == "booktitle"]
    assert booktitle_fields == ["Proc. of TALN", "Actes des 32ème Conférence sur le Traitement Automatique des Langues Naturelles"]

def test_tacl():
    middleware = BibTeXFormatterMiddleware(abbreviation_mode="both")
    entry = create_entry(journal="Transactions of the Association for Computational Linguistics, Volume 4")
    
    new_entry = middleware._add_abbreviated_fields(entry)
    
    journal_fields = [f.value for f in new_entry.fields if f.key == "journal"]
    assert journal_fields == ["TACL", "Transactions of the Association for Computational Linguistics"]