from bibtex.simplify import simplify_bibtex_entry
import pytest

def test_latex_command_warning():
    raw_bib = """@inproceedings{test,
    title = {A Title with {\\a} LaTeX command},
    author = {Author Name},
    booktitle = {Conference},
    year = {2024}
}"""
    
    warnings = []
    def warning_callback(msg):
        warnings.append(msg)
        
    simplify_bibtex_entry(raw_bib, warning_callback=warning_callback)
    
    assert len(warnings) > 0
    assert "LaTeX コマンドが含まれている可能性があります" in warnings[0]
    assert "{\\a}" in warnings[0]

def test_no_latex_command_no_warning():
    raw_bib = """@inproceedings{test,
    title = {A Title without LaTeX command},
    author = {Author Name},
    booktitle = {Conference},
    year = {2024}
}"""
    
    warnings = []
    def warning_callback(msg):
        warnings.append(msg)
        
    simplify_bibtex_entry(raw_bib, warning_callback=warning_callback)
    
    assert len(warnings) == 0

def test_nested_braces_warning():
    raw_bib = """@inproceedings{test,
    title = {A Title with {\\"{a}} symbol},
    author = {Author Name},
    booktitle = {Conference},
    year = {2024}
}"""
    
    warnings = []
    def warning_callback(msg):
        warnings.append(msg)
        
    simplify_bibtex_entry(raw_bib, warning_callback=warning_callback)
    
    assert len(warnings) > 0
    assert "LaTeX コマンドが含まれている可能性があります" in warnings[0]

def test_accent_commands_warning():
    accent_commands = ["{\\^o}", "{\\\"u}", "{\\~n}", "{\\c c}", "{\\guillemotleft}"]
    
    for command in accent_commands:
        raw_bib = f"""@inproceedings{{test,
    title = {{A Title with {command} command}},
    author = {{Author Name}},
    booktitle = {{Conference}},
    year = {{2024}}
}}"""
        
        warnings = []
        def warning_callback(msg):
            warnings.append(msg)
            
        simplify_bibtex_entry(raw_bib, warning_callback=warning_callback)
        
        assert any("LaTeX コマンドが含まれている可能性があります" in w for w in warnings)
        assert any(command in w for w in warnings)

def test_author_latex_command_warning():
    raw_bib = """@inproceedings{test,
    title = {A Title},
    author = {Author with {\\a} LaTeX command},
    booktitle = {Conference},
    year = {2024}
}"""
    
    warnings = []
    def warning_callback(msg):
        warnings.append(msg)
        
    simplify_bibtex_entry(raw_bib, warning_callback=warning_callback)
    
    assert len(warnings) == 0
