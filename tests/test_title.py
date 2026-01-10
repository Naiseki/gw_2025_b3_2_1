from bibtex.simplify import simplify_bibtex_entry
import pytest

def test_latex_title_preserves_braces_and_uses_quotes():
    raw_bib = """@inproceedings{test,
    title = {A {Title} with {\\a} LaTeX command},
    author = {Author Name},
    booktitle = {Conference},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 1. 期待される挙動: 中括弧が保持されている
    assert "{\\a}" in result
    # {Title} は LaTeX コマンドではないが、タイトル全体に LaTeX コマンドが含まれている場合は
    # 他の中括弧も保持される（現在の実装の副作用だが、ユーザーの意図に近いと思われる）
    assert "{Title}" in result
    
    # 2. 期待される挙動: ダブルクォートで囲まれている ({{...}} ではなく "...")
    assert 'title = "A {Title} with {\\a} LaTeX command"' in result
    assert 'title = {{' not in result

def test_normal_title_removes_braces_and_uses_double_braces():
    raw_bib = """@inproceedings{test,
    title = {A {Normal} Title},
    author = {Author Name},
    booktitle = {Conference},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 1. 期待される挙動: 中括弧が削除されている
    assert "{Normal}" not in result
    assert "Normal" in result
    
    # 2. 期待される挙動: 二重中括弧で囲まれている
    assert "title = {{A Normal Title}}" in result

def test_title_with_colon_and_single_word_prefix():
    raw_bib = """@article{test,
    title = {deep: A Study on Something},
    author = {Author Name},
    journal = {Journal Name},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 期待される挙動: "deep" が保護されている
    assert "title = {{deep: A Study on Something}}" in result

def test_title_with_colon_and_multi_word_prefix():
    raw_bib = """@article{test,
    title = {a deep study: an analysis},
    author = {Author Name},
    journal = {Journal Name},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 期待される挙動: "a deep study" は保護されない
    assert "title = {{A Deep Study: An Analysis}}" in result

def test_title_without_colon():
    raw_bib = """@article{test,
    title = {an interesting paper},
    author = {Author Name},
    journal = {Journal Name},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 期待される挙動: 通常にtitlecaseが適用される
    assert "title = {{An Interesting Paper}}" in result

def test_title_with_colon_and_single_word_prefix_double_quotes():
    raw_bib = """@article{test,
    title = "deep: A Study on Something",
    author = {Author Name},
    journal = {Journal Name},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 期待される挙動: "deep" が保護されている
    assert "title = {{deep: A Study on Something}}" in result

def test_title_single_word_with_hyphen():
    raw_bib = """@article{test,
    title = {e-mail: The Future of Communication},
    author = {Author Name},
    journal = {Journal Name},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 期待される挙動: "e-mail" が保護されている
    assert "title = {{e-mail: The Future of Communication}}" in result

def test_title_with_braces_and_colon():
    raw_bib = """@article{test,
    title = {the {impact} of AI: a comprehensive study},
    author = {Author Name},
    journal = {Journal Name},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 期待される挙動: "the impact" は中括弧が削除され、titlecaseが適用される
    assert "title = {{The impact of AI: A Comprehensive Study}}" in result

def test_title_single_word_with_numbers():
    raw_bib = """@article{test,
    title = {COVID-19: A Global Challenge},
    author = {Author Name},
    journal = {Journal Name},
    year = {2024}
}"""
    
    result = simplify_bibtex_entry(raw_bib)
    
    # 期待される挙動: "COVID-19" が保護されている
    assert "title = {{COVID-19: A Global Challenge}}" in result