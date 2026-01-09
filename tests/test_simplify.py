from bibtex.simplify import simplify_bibtex_entry

def test_simplify_bibtex_entry():
    raw_bib = """% word2vec
@inproceedings{mikolov-2013-word2vec,
    title = {Efficient Estimation of Word Representations in Vector Space},
    author = "Tomas Mikolov and Kai Chen and Greg Corrado and Jeffrey Dean",
    booktitle = "Proceedings of the 1st International Conference on Learning Representations",
    year = "2013",
    url = "https://arxiv.org/abs/1301.3781",
}


% GloVeこの右側にスペースが入っている                         
@inproceedings{pennington-2014-glove,
    title = "GloVe: Global Vectors for Word Representation",
    author = "Pennington, Jeffrey  and  Socher, Richard  and  Manning, Christopher",
    booktitle = "Proc. of EMNLP",
    booktitle = "Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing",
    pages = "1532--1543",
    year = "2014",
    url = "<https://aclanthology.org/D14-1162/|https://aclanthology.org/D14-1162/>",
}
@article{alva-manchego-etal-2020-data,
    title = "Data-Driven Sentence Simplification: Survey and Benchmark",
    author = "Alva-Manchego, Fernando  and
      Scarton, Carolina  and
      Specia, Lucia",
    journal = "Computational Linguistics",
    volume = "46",
    number = "1",
    year = "2020",
    address = "Cambridge, MA",
    publisher = "MIT Press",
    url = "https://aclanthology.org/2020.cl-1.4/",
    doi = "10.1162/coli_a_00370",
    pages = "135--187",
    abstract = "Sentence Simplification (SS) aims to modify a sentence in order to make it easier to read and understand. In order to do so, several rewriting transformations can be performed such as replacement, reordering, and splitting. Executing these transformations while keeping sentences grammatical, preserving their main idea, and generating simpler output, is a challenging and still far from solved problem. In this article, we survey research on SS, focusing on approaches that attempt to learn how to simplify using corpora of aligned original-simplified sentence pairs in English, which is the dominant paradigm nowadays. We also include a benchmark of different approaches on common data sets so as to compare them and highlight their strengths and limitations. We expect that this survey will serve as a starting point for researchers interested in the task and help spark new ideas for future developments."
}




% このコメントはくっついてない

















%このコメントは下にくっついている
% fastText
@article{bojanowski-2017-fasttext,
    title = {{Enriching Word Vectors with Subword Information}},
    author = "Bojanowski, Piotr  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "TACL",
    journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",
    pages = "135--146",
    year = "2017",
    url = "https://aclanthology.org/Q17-1010/",
}
このコメントは上にくっついている


 このコメントもくっついていない(左にスペースがあります)"""

    simplified_bib = simplify_bibtex_entry(raw_bib, abbreviation_mode="both")
    expected_simplified_bib = """% word2vec
@inproceedings{mikolov-2013-word2vec,
    title = {{Efficient Estimation of Word Representations in Vector Space}},
    author = "Tomas Mikolov and Kai Chen and Greg Corrado and Jeffrey Dean",
    booktitle = "Proc. of ICLR",
    booktitle = "Proceedings of the 1st International Conference on Learning Representations",
    year = "2013",
    url = "https://arxiv.org/abs/1301.3781",
}

% GloVeこの右側にスペースが入っている
@inproceedings{pennington-2014-glove,
    title = {{GloVe: Global Vectors for Word Representation}},
    author = "Pennington, Jeffrey  and  Socher, Richard  and  Manning, Christopher",
    booktitle = "Proc. of EMNLP",
    booktitle = "Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing",
    pages = "1532--1543",
    year = "2014",
    url = "https://aclanthology.org/D14-1162",
}

@article{alva-manchego-etal-2020-data,
    title = {{Data-Driven Sentence Simplification: Survey and Benchmark}},
    author = "Alva-Manchego, Fernando  and
      Scarton, Carolina  and
      Specia, Lucia",
    journal = "CL",
    journal = "Computational Linguistics",
    volume = "46",
    number = "1",
    pages = "135--187",
    year = "2020",
    url = "https://aclanthology.org/2020.cl-1.4",
}

% このコメントはくっついてない

%このコメントは下にくっついている
% fastText
@article{bojanowski-2017-fasttext,
    title = {{Enriching Word Vectors with Subword Information}},
    author = "Bojanowski, Piotr  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "TACL",
    journal = "Transactions of the Association for Computational Linguistics",
    volume = "5",
    pages = "135--146",
    year = "2017",
    url = "https://aclanthology.org/Q17-1010",
}
このコメントは上にくっついている

このコメントもくっついていない(左にスペースがあります)
"""
    assert simplified_bib == expected_simplified_bib


def test_simplify_bibtex_entry_short_mode():
    raw_bib = """ % word2vec
@inproceedings{mikolov-2013-word2vec,
    title = {Efficient Estimation of Word Representations in Vector Space},

    author = "Tomas Mikolov and Kai Chen and Greg Corrado and Jeffrey Dean",


    booktitle = "Proceedings of the 1st International Conference on Learning Representations",
    year = "2013",
    url = "https://arxiv.org/abs/1301.3781",
}


% GloVeこの右側にスペースが入っている                         
@inproceedings{pennington-2014-glove,
    title = "GloVe: Global Vectors for Word Representation",
            author = "Pennington, Jeffrey  and  Socher, Richard  and  Manning, Christopher",
 booktitle = "Proc. of EMNLP",
    booktitle = "Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing",
    pages = "1532--1543",
    year = "2014",
    url = "<https://aclanthology.org/D14-1162/|https://aclanthology.org/D14-1162/>",
}
@article{alva-manchego-etal-2020-data,
    title = "Data-Driven Sentence Simplification: Survey and Benchmark",
    author = "Alva-Manchego, Fernando  and
      Scarton, Carolina  and
      Specia, Lucia",
    journal = "Computational Linguistics",
    volume = "46",
    number = "1",
    year = "2020",
    address = "Cambridge, MA",
    publisher = "MIT Press",
    url = "https://aclanthology.org/2020.cl-1.4/",
    doi = "10.1162/coli_a_00370",
    pages = "135--187",
    abstract = "Sentence Simplification (SS) aims to modify a sentence in order to make it easier to read and understand. In order to do so, several rewriting transformations can be performed such as replacement, reordering, and splitting. Executing these transformations while keeping sentences grammatical, preserving their main idea, and generating simpler output, is a challenging and still far from solved problem. In this article, we survey research on SS, focusing on approaches that attempt to learn how to simplify using corpora of aligned original-simplified sentence pairs in English, which is the dominant paradigm nowadays. We also include a benchmark of different approaches on common data sets so as to compare them and highlight their strengths and limitations. We expect that this survey will serve as a starting point for researchers interested in the task and help spark new ideas for future developments."
}




% このコメントはくっついてない

















%このコメントは下にくっついている
% fastText
@article{bojanowski-2017-fasttext,
    title = {{Enriching Word Vectors with Subword Information}},
    author = "Bojanowski, Piotr  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "TACL",
    journal = "Transactions of the Association for Computational Linguistics",
    pages = "135--146",
    year = "2017",
    url = "https://aclanthology.org/Q17-1010/",
}
このコメントは上にくっついている


 このコメントもくっついていない(左にスペースがあります)"""

    expected_simplified_bib = """% word2vec
@inproceedings{mikolov-2013-word2vec,
    title = {{Efficient Estimation of Word Representations in Vector Space}},
    author = "Tomas Mikolov and Kai Chen and Greg Corrado and Jeffrey Dean",
    booktitle = "Proc. of ICLR",
    year = "2013",
    url = "https://arxiv.org/abs/1301.3781",
}

% GloVeこの右側にスペースが入っている
@inproceedings{pennington-2014-glove,
    title = {{GloVe: Global Vectors for Word Representation}},
    author = "Pennington, Jeffrey  and  Socher, Richard  and  Manning, Christopher",
    booktitle = "Proc. of EMNLP",
    pages = "1532--1543",
    year = "2014",
    url = "https://aclanthology.org/D14-1162",
}

@article{alva-manchego-etal-2020-data,
    title = {{Data-Driven Sentence Simplification: Survey and Benchmark}},
    author = "Alva-Manchego, Fernando  and
      Scarton, Carolina  and
      Specia, Lucia",
    journal = "CL",
    volume = "46",
    number = "1",
    pages = "135--187",
    year = "2020",
    url = "https://aclanthology.org/2020.cl-1.4",
}

% このコメントはくっついてない

%このコメントは下にくっついている
% fastText
@article{bojanowski-2017-fasttext,
    title = {{Enriching Word Vectors with Subword Information}},
    author = "Bojanowski, Piotr  and  Grave, Edouard  and  Joulin, Armand  and  Mikolov, Tomas",
    journal = "TACL",
    pages = "135--146",
    year = "2017",
    url = "https://aclanthology.org/Q17-1010",
}
このコメントは上にくっついている

このコメントもくっついていない(左にスペースがあります)
"""
    simplified_bib_short = simplify_bibtex_entry(raw_bib, abbreviation_mode="short")
    assert simplified_bib_short == expected_simplified_bib


def test_simplify_bibtex_entry_empty_input():
    try:
        simplify_bibtex_entry("", abbreviation_mode="both")
    except ValueError as e:
        assert "有効なBibTeXエントリが見つかりませんでした" in str(e)

def test_latex_title_entry():
    raw_bib = """@inproceedings{bleuze-etal-2025-de,
    title = "{\guillemotleft} De nos jours, ce sont les r{\'e}sultats qui comptent {\guillemotright} : cr{\'e}ation et {\'e}tude diachronique d{'}un corpus de revendications issues d{'}articles de {TAL}",
    author = {Bleuze, Clementine  and
      Ducel, Fanny  and
      Amblard, Maxime  and
      Fort, Kar{\"e}n},
    editor = "Bechet, Fr{\'e}d{\'e}ric  and
      Chifu, Adrian-Gabriel  and
      Pinel-sauvagnat, Karen  and
      Favre, Benoit  and
      Maes, Eliot  and
      Nurbakova, Diana",
    booktitle = "Actes des 32{\`e}me Conf{\'e}rence sur le Traitement Automatique des Langues Naturelles (TALN), volume 1 : articles scientifiques originaux",
    month = "6",
    year = "2025",
    address = "Marseille, France",
    publisher = "ATALA {\textbackslash}{\textbackslash}{\&} ARIA",
    url = "https://aclanthology.org/2025.jeptalnrecital-taln.1/",
    pages = "1--21",
    language = "fra"
}"""
    simplified_bib = simplify_bibtex_entry(raw_bib, abbreviation_mode="both")
    expected_simplified_bib = """@inproceedings{bleuze-etal-2025-de,
    title = "{\guillemotleft} De nos jours, ce sont les r{\'e}sultats qui comptent {\guillemotright} : cr{\'e}ation et {\'e}tude diachronique d{'}un corpus de revendications issues d{'}articles de {TAL}",
    author = "Bleuze, Clementine  and
      Ducel, Fanny  and
      Amblard, Maxime  and
      Fort, Kar{\"e}n",
    booktitle = "Proc. of TALN",
    booktitle = "Actes des 32{\`e}me Conf{\'e}rence sur le Traitement Automatique des Langues Naturelles",
    pages = "1--21",
    year = "2025",
    url = "https://aclanthology.org/2025.jeptalnrecital-taln.1",
}
"""
    assert simplified_bib == expected_simplified_bib

def test_latex_command_entry():
    raw_bib = """@inproceedings{test,
    title = {A Title with {\\a} LaTeX command},
    author = {{\\e} Name},
    booktitle = "Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing",
    year = {2024}
}"""

    expected_simplified_bib = """@inproceedings{test,
    title = {A Title with {\\a} LaTeX command},
    author = {{\\e} Name},
    booktitle = "Proc. of EMNLP",
    booktitle = "Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing",
    year = {2024}
}"""
    
    warnings = []
    def warning_callback(msg):
        warnings.append(msg)
        
    simplified_bib = simplify_bibtex_entry(raw_bib, warning_callback=warning_callback)
    
    assert len(warnings) == 1
    assert "LaTeX コマンドが含まれている可能性があります" in warnings[0]
    assert "{\\a}" in warnings[0]


def test_brace_colon():
    raw_bib = """@inproceedings{alva-manchego-etal-2019-easse,
    title = "{EASSE}: Easier Automatic Sentence Simplification Evaluation",
    author = "Alva-Manchego, Fernando  and
      Martin, Louis  and
      Scarton, Carolina  and
      Specia, Lucia",
    editor = "Pad{\'o}, Sebastian  and
      Huang, Ruihong",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP): System Demonstrations",
    month = nov,
    year = "2019",
    address = "Hong Kong, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/D19-3009/",
    doi = "10.18653/v1/D19-3009",
    pages = "49--54",
    abstract = "We introduce EASSE, a Python package aiming to facilitate and standardise automatic evaluation and comparison of Sentence Simplification (SS) systems. EASSE provides a single access point to a broad range of evaluation resources: standard automatic metrics for assessing SS outputs (e.g. SARI), word-level accuracy scores for certain simplification transformations, reference-independent quality estimation features (e.g. compression ratio), and standard test data for SS evaluation (e.g. TurkCorpus). Finally, EASSE generates easy-to-visualise reports on the various metrics and features above and on how a particular SS output fares against reference simplifications. Through experiments, we show that these functionalities allow for better comparison and understanding of the performance of SS systems."
}"""
    expected_simplified_bib = """@inproceedings{alva-manchego-etal-2019-easse,
    title = {{EASSE: Easier Automatic Sentence Simplification Evaluation}},
    author = "Alva-Manchego, Fernando  and
      Martin, Louis  and
      Scarton, Carolina  and
      Specia, Lucia",
    booktitle = "Proc. of EMNLP-IJCNLP",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing: System Demonstrations",
    pages = "49--54",
    year = "2019",
    url = "https://aclanthology.org/D19-3009",
}"""

    simplified_bib = simplify_bibtex_entry(raw_bib, abbreviation_mode="both")
    assert simplified_bib == expected_simplified_bib