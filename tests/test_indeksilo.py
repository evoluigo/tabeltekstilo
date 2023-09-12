# SPDX-FileCopyrightText: 2023 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd

import indeksilo


def test_read_build_write_index(mocker):
    """
    test that read_build_write_index() reads the necessary columns from the
    data file, calls build_index() with correct arguments and writes the
    result to the output data file.
    """
    read_excel = mocker.patch("pandas.read_excel")
    df = pd.DataFrame(
        {
            "form col": [],
            "ref 1": [],
            "ref 0": [],
            "parent 2": [],
            "parent 1": [],
            "parent 0": [],
        }
    )
    read_excel.return_value = df
    build_index = mocker.patch("indeksilo.indexer.build_index")
    index_df = pd.DataFrame(
        {
            "parent 2": [],
            "parent 1": [],
            "form col": [],
            "refs": [],
        }
    )
    build_index.return_value = index_df
    mocker.patch.object(index_df, "to_excel")
    indeksilo.read_build_write_index(
        "input.ods",
        "output.ods",
        ["ref 0", "ref 1"],
        "form col",
        ["parent 0", "parent 1", "parent 2"],
        "@",
    )
    pd.read_excel.assert_called_once_with(
        "input.ods",
        usecols=[
            "ref 0",
            "ref 1",
            "form col",
            "parent 0",
            "parent 1",
            "parent 2",
        ],
        dtype=str,
        keep_default_na=False,
    )
    build_index.assert_called_once_with(
        df,
        ["ref 0", "ref 1"],
        "form col",
        ["parent 0", "parent 1", "parent 2"],
        "@",
    )
    index_df.to_excel.assert_called_once_with("output.ods")
    pd.read_excel.reset_mock()
    build_index.reset_mock()
    index_df.to_excel.reset_mock()
    indeksilo.read_build_write_index(
        "input.ods",
        "output.ods",
        ["ref 0"],
        "form col",
    )
    pd.read_excel.assert_called_once_with(
        "input.ods",
        usecols=[
            "ref 0",
            "form col",
        ],
        dtype=str,
        keep_default_na=False,
    )
    build_index.assert_called_once_with(
        df,
        ["ref 0"],
        "form col",
        [],
        None,
    )
    index_df.to_excel.assert_called_once_with("output.ods")


def test_build_index(mocker):
    """
    test that build_index() correctly builds an index.
    """
    df = pd.DataFrame(
        {
            "form": ["xyzabcjkl", "abc", "xyjk", "abc"],
            "ref 1": ["l 42", "l 2", "l 27", "l 7"],
            "ref 0": ["p 7", "p 23", "p 32", "p 42"],
            "parent 2": ["yyy@ccc@lll", "ccc", "zzz@kkk", "ccc"],
            "parent 1": ["yy@bb@kk", "bb", "zz@kk", "bb"],
            "parent 0": ["x@a@j", "a", "x@j", "a"],
        }
    )
    index_df = indeksilo.build_index(
        df,
        ["ref 0", "ref 1"],
        "form",
        ["parent 0", "parent 1", "parent 2"],
        "@",
    )
    expected_index_df = pd.DataFrame(
        {
            "parent 0_count": [3, "", 2, "", 2, ""],
            "parent 0": ["a", "", "j", "", "x", ""],
            "parent 1_count": [3, "", 2, "", 1, 1],
            "parent 1": ["bb", "", "kk", "", "yy", "zz"],
            "parent 2_count": [3, "", 1, 1, 1, 1],
            "parent 2": ["ccc", "", "kkk", "lll", "yyy", "zzz"],
            "form_count": [2, 1, 1, 1, 1, 1],
            "form": [
                "abc",
                "xyzabcjkl",
                "xyjk",
                "xyzabcjkl",
                "xyzabcjkl",
                "xyjk",
            ],
            "refs": [
                "p 23, l 2; p 42, l 7",
                "p 7, l 42",
                "p 32, l 27",
                "p 7, l 42",
                "p 7, l 42",
                "p 32, l 27",
            ],
        }
    )
    assert index_df.compare(expected_index_df).empty
    assert (
        index_df.columns
        == [
            "parent 0_count",
            "parent 0",
            "parent 1_count",
            "parent 1",
            "parent 2_count",
            "parent 2",
            "form_count",
            "form",
            "refs",
        ]
    ).all()
    index_df = indeksilo.build_index(
        df,
        ["ref 0"],
        "form",
    )
    expected_index_df = pd.DataFrame(
        {
            "form_count": [2, 1, 1],
            "form": ["abc", "xyjk", "xyzabcjkl"],
            "refs": ["p 23; p 42", "p 32", "p 7"],
        }
    )
    assert index_df.compare(expected_index_df).empty
    assert (index_df.columns == ["form_count", "form", "refs"]).all()


def test_alphabetical_ordering():
    """
    test that the index entries are correctly ordered alphabetically.
    """
    df = pd.DataFrame(
        {
            "form": ["abcdef", "abcdéa"],
            "ref": ["r0", "r1"],
            "parent": ["abc@âab", "âab@abc"],
        }
    )
    index_df = indeksilo.build_index(
        df,
        ["ref"],
        "form",
        ["parent"],
        "@",
    )
    expected_index_df = pd.DataFrame(
        {
            "parent_count": [2, "", 2, ""],
            "parent": ["âab", "", "abc", ""],
            "form_count": [1, 1, 1, 1],
            "form": ["abcdéa", "abcdef", "abcdéa", "abcdef"],
            "refs": ["r1", "r0", "r1", "r0"],
        }
    )
    assert index_df.compare(expected_index_df).empty


def test_grouped_refs():
    """
    test that identical references for the same form get grouped instead of
    being repeated.
    """
    df = pd.DataFrame(
        {
            "form": ["abc", "def", "abc", "def", "abc"],
            "ref": ["r0", "r0", "r0", "r1", "r1"],
        }
    )
    index_df = indeksilo.build_index(
        df,
        ["ref"],
        "form",
    )
    expected_index_df = pd.DataFrame(
        {
            "form_count": [3, 2],
            "form": ["abc", "def"],
            "refs": ["r0 (2); r1", "r0; r1"],
        }
    )
    assert index_df.compare(expected_index_df).empty
