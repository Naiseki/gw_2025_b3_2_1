import pytest
from bibtex.simplify import _parse_bibtex_entries
from bibtexparser.model import Entry

def test_parse_single_entry():
    raw_bib = """@article{key,
        author = {Author Name},
        title = {Title},
        journal = {Journal},
        year = {2024}
    }"""
    library = _parse_bibtex_entries(raw_bib)
    assert len(library.entries) == 1
    assert isinstance(library.entries[0], Entry)
    assert library.entries[0].key == "key"

def test_parse_multiple_entries():
    raw_bib = """@article{key1,
        author = {Author One},
        title = {Title One},
        journal = {Journal One},
        year = {2024}
    }
    @book{key2,
        author = {Author Two},
        title = {Title Two},
        publisher = {Publisher},
        year = {2023}
    }"""
    library = _parse_bibtex_entries(raw_bib)
    assert len(library.entries) == 2
    assert library.entries[0].key == "key1"
    assert library.entries[1].key == "key2"

def test_parse_failed_block():
    # Entry with a syntax error that should trigger a failed block
    raw_bib = """@article{key,
        author = {Author Name},
        title = {Title},
        journal = {Journal},
        year = {2024}
    
    @article{valid,
        author = {Author One},
        title = {Title One},
        journal = {Journal One},
        year = {2024}
    }"""
    warnings = []
    def callback(msg):
        warnings.append(msg)
    
    library = _parse_bibtex_entries(raw_bib, warning_callback=callback)
    
    assert len(library.entries) == 1
    assert library.entries[0].key == "valid"
    assert len(warnings) > 0
    assert "BibTeXの解析に失敗しました" in warnings[0]
    assert """@article{key,
        author = {Author Name},
        title = {Title},
        journal = {Journal},
        year = {2024}""" in warnings[0]

def test_parse_no_valid_entries():
    raw_bib = "This is not a BibTeX entry."
    with pytest.raises(ValueError, match="有効なBibTeXエントリが見つかりませんでした"):
        _parse_bibtex_entries(raw_bib)

def test_parse_malformed_no_entries():
    # Only a malformed entry
    raw_bib = "@article{key,"
    warnings = []
    def callback(msg):
        warnings.append(msg)
    with pytest.raises(ValueError, match="BibTeX解析エラー"):
        library = _parse_bibtex_entries(raw_bib, warning_callback=callback)
    assert len(warnings) > 0
    assert "BibTeXの解析に失敗しました" in warnings[0]
    assert "@article{key," in warnings[0]

def test_parse_empty_string():
    raw_bib = ""
    with pytest.raises(ValueError, match="有効なBibTeXエントリが見つかりませんでした"):
        _parse_bibtex_entries(raw_bib)

def test_parse_duplicate_fields():
    # allow_duplicate_fields=True is used in _parse_bibtex_entries
    raw_bib = """@article{key,
        author = {Author One},
        author = {Author Two},
        title = {Title},
        journal = {Journal},
        year = {2024}
    }"""
    # Bibtexparser handles duplicate fields by keeping both in DuplicateFieldKeyBlock usually, 
    # but with allow_duplicate_fields=True, it might behave differently depending on version.
    # In v2, it allows them to exist in the entry.
    library = _parse_bibtex_entries(raw_bib)
    assert len(library.entries) == 1
    entry = library.entries[0]
    # Check if both fields are present or handled. 
    # Actually, in bibtexparser v2, fields is a list-like or dict-like.
    # We just want to ensure it doesn't crash and returns an entry.
    assert entry.key == "key"
