from slack_handler import parse_options_and_build_raw_bib
import pytest

def test_no_options():
    input = " % word2vec\n@inproceedings{}\n"
    expected_mode = "both"
    expected_raw_bib = "% word2vec\n@inproceedings{}"
    mode, raw_bib = parse_options_and_build_raw_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib


def test_short_option():
    input = "-s\n% word2vec\n@inproceedings{} \n"
    expected_mode = "short"
    expected_raw_bib = "% word2vec\n@inproceedings{}"
    mode, raw_bib = parse_options_and_build_raw_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib


def test_long_option_with_at():
    input = "--long   \n\n% word2vec\n@inproceedings{\n} \n"
    expected_mode = "long"
    expected_raw_bib = "% word2vec\n@inproceedings{\n}"
    mode, raw_bib = parse_options_and_build_raw_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib

def test_short_option_with_text_before_at():
    input = "Please convert -s\n% word2vec\n@inproceedings{} \n"
    expected_mode = "short"
    expected_raw_bib = "Please convert \n% word2vec\n@inproceedings{}"
    mode, raw_bib = parse_options_and_build_raw_bib(input)
    assert mode == expected_mode
    assert raw_bib == expected_raw_bib