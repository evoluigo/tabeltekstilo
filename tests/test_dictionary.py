# SPDX-FileCopyrightText: 2024 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd

import tabeltekstilo
import tabeltekstilo.cli


def test_main(mocker):
    """
    test that the main() function calls read_build_write_dictionary() with
    correct options.
    """
    import sys

    sys.argv = [
        "tabeltekstilo",
        "dictionary",
        "--form-col",
        "form",
        "--agg-col",
        "agg0",
        "--agg-col",
        "agg1",
        "--join-str",
        " | ",
        "input.ods",
        "output.ods",
    ]
    read_build_write_dictionary = mocker.patch(
        "tabeltekstilo.cli.read_build_write_dictionary"
    )
    tabeltekstilo.cli.main()
    read_build_write_dictionary.assert_called_once_with(
        "input.ods",
        "output.ods",
        "form",
        ["agg0", "agg1"],
        " | ",
    )
    read_build_write_dictionary.reset_mock()
    sys.argv = [
        "tabeltekstilo",
        "dictionary",
        "--form-col",
        "form",
        "--agg-col",
        "agg0",
        "input.ods",
        "output.ods",
    ]
    tabeltekstilo.cli.main()
    read_build_write_dictionary.assert_called_once_with(
        "input.ods",
        "output.ods",
        "form",
        ["agg0"],
        None,
    )


def test_read_build_write_dictionary(mocker):
    """
    test that read_build_write_dictionary() reads the necessary columns from
    the data file, calls build_dictionary() with correct arguments and writes
    the result to the output data file.
    """
    read_excel = mocker.patch("pandas.read_excel")
    df = pd.DataFrame(
        {
            "agg 2": [],
            "agg 1": [],
            "agg 0": [],
            "form col": [],
        }
    )
    read_excel.return_value = df
    build_dictionary = mocker.patch(
        "tabeltekstilo.dictionary.build_dictionary"
    )
    dictionary_df = pd.DataFrame(
        {
            "agg 2": [],
            "agg 1": [],
            "agg 0": [],
            "form col": [],
        }
    )
    build_dictionary.return_value = dictionary_df
    mocker.patch.object(dictionary_df, "to_excel")
    tabeltekstilo.read_build_write_dictionary(
        "input.ods",
        "output.ods",
        "form col",
        ["agg 0", "agg 1", "agg 2"],
        " | ",
    )
    pd.read_excel.assert_called_once_with(
        "input.ods",
        usecols=[
            "form col",
            "agg 0",
            "agg 1",
            "agg 2",
        ],
        dtype=str,
        keep_default_na=False,
    )
    build_dictionary.assert_called_once_with(
        df,
        "form col",
        ["agg 0", "agg 1", "agg 2"],
        " | ",
    )
    dictionary_df.to_excel.assert_called_once_with("output.ods")
    pd.read_excel.reset_mock()
    build_dictionary.reset_mock()
    dictionary_df.to_excel.reset_mock()
    tabeltekstilo.read_build_write_dictionary(
        "input.ods",
        "output.ods",
        "form col",
        ["agg 0"],
    )
    pd.read_excel.assert_called_once_with(
        "input.ods",
        usecols=[
            "form col",
            "agg 0",
        ],
        dtype=str,
        keep_default_na=False,
    )
    build_dictionary.assert_called_once_with(
        df,
        "form col",
        ["agg 0"],
        None,
    )
    dictionary_df.to_excel.assert_called_once_with("output.ods")


def test_build_dictionary(mocker):
    """
    test that build_dictionary() correctly builds an dictionary.
    """
    df = pd.DataFrame(
        {
            "agg 2": ["yyy", "bbb", "jjj", "aaa", "xxx", "bbb", "zzz"],
            "agg 1": ["zz", "bb", "jj", "aa", "xx", "bb", "yy"],
            "agg 0": ["y", "b", "j", "a", "x", "b", "x"],
            "form": ["xyz", "abc", "jkl", "abc", "xyz", "abc", "xyz"],
        }
    )
    dictionary_df = tabeltekstilo.build_dictionary(
        df,
        "form",
        ["agg 0", "agg 1", "agg 2"],
        " | ",
    )
    expected_dictionary_df = pd.DataFrame(
        {
            "form": [
                "abc",
                "jkl",
                "xyz",
            ],
            "agg 0": [
                "a | b",
                "j",
                "x | x | y",
            ],
            "agg 1": [
                "aa | bb",
                "jj",
                "xx | yy | zz",
            ],
            "agg 2": [
                "aaa | bbb",
                "jjj",
                "xxx | zzz | yyy",
            ],
        }
    )
    assert dictionary_df.compare(expected_dictionary_df).empty
    assert (
        dictionary_df.columns
        == [
            "form",
            "agg 0",
            "agg 1",
            "agg 2",
        ]
    ).all()
    dictionary_df = tabeltekstilo.build_dictionary(
        df,
        "form",
        ["agg 0"],
    )
    expected_dictionary_df = pd.DataFrame(
        {
            "form": [
                "abc",
                "jkl",
                "xyz",
            ],
            "agg 0": [
                "a; b",
                "j",
                "x; y",
            ],
        }
    )
    assert dictionary_df.compare(expected_dictionary_df).empty
    assert (dictionary_df.columns == ["form", "agg 0"]).all()


def test_alphabetical_ordering():
    """
    test that the dictionary entries are correctly ordered alphabetically.
    """
    df = pd.DataFrame(
        {
            "form": ["abcdef", "abcdéa", "abcdef"],
            "agg": ["abc", "abc", "âab"],
        }
    )
    dictionary_df = tabeltekstilo.build_dictionary(
        df,
        "form",
        ["agg"],
    )
    expected_dictionary_df = pd.DataFrame(
        {
            "form": ["abcdéa", "abcdef"],
            "agg": ["abc", "âab; abc"],
        }
    )
    assert dictionary_df.compare(expected_dictionary_df).empty


def test_empty_form():
    """
    test that a line with no data in the form column is skipped.
    """
    df = pd.DataFrame(
        {
            "form": ["abc", "", "def"],
            "agg": ["a", "x", "d"],
        }
    )
    dictionary_df = tabeltekstilo.build_dictionary(
        df,
        "form",
        ["agg"],
    )
    expected_dictionary_df = pd.DataFrame(
        {
            "form": ["abc", "def"],
            "agg": ["a", "d"],
        }
    )
    assert dictionary_df.compare(expected_dictionary_df).empty
