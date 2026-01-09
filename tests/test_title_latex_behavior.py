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
