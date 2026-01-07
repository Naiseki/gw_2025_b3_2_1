from slack_handler import parse_options_and_extract_bib
import pytest

def test_no_options():
    input = " % word2vec\n@inproceedings{}\n"
    expected_mode = "both"
    expected_raw_bib = "% word2vec\n@inproceedings{}"
    mode, raw_bib = parse_options_and_extract_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib


def test_short_option():
    input = "-s\n% word2vec\n@inproceedings{} \n"
    expected_mode = "short"
    expected_raw_bib = "% word2vec\n@inproceedings{}"
    mode, raw_bib = parse_options_and_extract_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib


def test_long_option_with_at():
    input = "--long   \n\n% word2vec\n@inproceedings{\n} \n"
    expected_mode = "long"
    expected_raw_bib = "% word2vec\n@inproceedings{\n}"
    mode, raw_bib = parse_options_and_extract_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib

def test_short_option_with_text_before_at():
    input = "Please convert -s\n% word2vec\n@inproceedings{} \n"
    expected_mode = "short"
    expected_raw_bib = "Please convert \n% word2vec\n@inproceedings{}"
    mode, raw_bib = parse_options_and_extract_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib

def test_independent_comment():
    input = "% This is a comment\n\n@article{}"
    expected_mode = "both"
    expected_raw_bib = "% This is a comment\n\n@article{}"
    mode, raw_bib = parse_options_and_extract_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib


def test_codeblock():
    input_raw_bib = """-s
```% fastText``
@article{bojanowski-2017-fasttext,
    title = {Enriching Word Vectors with Subword Information},
    author = "Bojanowski, Piotr  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",
    pages = "135--146",
    year = "2017",
    url = "https://aclanthology.org/Q17-1010",
}```"""
    abbreviation_mode, raw_bib = parse_options_and_extract_bib(input_raw_bib)
    expected_raw_bib = """% fastText``
@article{bojanowski-2017-fasttext,
    title = {Enriching Word Vectors with Subword Information},
    author = "Bojanowski, Piotr  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",
    pages = "135--146",
    year = "2017",
    url = "https://aclanthology.org/Q17-1010",
}"""
    assert abbreviation_mode == "short"
    assert raw_bib == expected_raw_bib

    input_raw_bib2 = """```% fastText``` --long
@article{bojanowski-2017-fasttext,
    title = {Enriching Word Vectors with Subword Information},
    author = "Bojanowski`, Piotr``  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    ```journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",```
    pages = "135--146",
    year = "2017",
    url = "```https://aclanthology.org/Q17-1010",
}"""

    expected_raw_bib2 = """% fastText 
@article{bojanowski-2017-fasttext,
    title = {Enriching Word Vectors with Subword Information},
    author = "Bojanowski`, Piotr``  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",
    pages = "135--146",
    year = "2017",
    url = "```https://aclanthology.org/Q17-1010",
}""" 
    abbreviation_mode, raw_bib2 = parse_options_and_extract_bib(input_raw_bib2)
    assert abbreviation_mode == "long"
    assert raw_bib2 == expected_raw_bib2


    input_raw_bib3 = """```-s % fastText
@article{bojanowski-2017-fasttext,
    title = {Enriching Word Vectors with Subword Information},```
    author = "Bojanowski`, Piotr``  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    ```journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",```
    pages = "135--146",
    year = "2017",
    url = "```https://aclanthology.org/Q17-1010",
}
"""

    expected_raw_bib3 = """% fastText
@article{bojanowski-2017-fasttext,
    title = {Enriching Word Vectors with Subword Information},
    author = "Bojanowski`, Piotr``  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",
    pages = "135--146",
    year = "2017",
    url = "```https://aclanthology.org/Q17-1010",
}"""
    abbreviation_mode, raw_bib3 = parse_options_and_extract_bib(input_raw_bib3)
    assert abbreviation_mode == "short"
    assert raw_bib3 == expected_raw_bib3