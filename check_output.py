from bibtex.simplify import simplify_bibtex_entry

raw_bib = """@inproceedings{test,
    title = {A Title with {\\a} LaTeX command},
    author = {Author Name},
    booktitle = {Conference},
    year = {2024}
}"""

result = simplify_bibtex_entry(raw_bib)
print("Result with LaTeX (Expected braces preserved and surrounded by double quotes):")
print(result)

raw_bib_no_latex = """@inproceedings{test,
    title = {A {Title} without LaTeX command},
    author = {Author Name},
    booktitle = {Conference},
    year = {2024}
}"""

result_no_latex = simplify_bibtex_entry(raw_bib_no_latex)
print("\nResult without LaTeX (Expected braces removed and surrounded by double braces):")
print(result_no_latex)
