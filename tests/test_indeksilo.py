# SPDX-FileCopyrightText: 2023 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
import pytest

import indeksilo


def test_main_package_entry():
    """
    test that indeksilo.__main__ is well-formed.
    """
    from indeksilo import __main__  # noqa: F401


def test_main(mocker):
    """
    test that the main() function calls read_build_write_index() with correct
    options.
    """
    import sys

    sys.argv = [
        "indeksilo",
        "--ref-col",
        "ref0",
        "--ref-col",
        "ref1",
        "--parent-col",
        "parent0",
        "--parent-col",
        "parent1",
        "--form-col",
        "form",
        "--split-char",
        "@",
        "--filter",
        "fcol:val0",
        "--filter",
        "fcol:val1",
        "--filter-exclude",
        "input.ods",
        "output.ods",
    ]
    read_build_write_index = mocker.patch(
        "indeksilo.cli.read_build_write_index"
    )
    indeksilo.cli.main()
    read_build_write_index.assert_called_once_with(
        "input.ods",
        "output.ods",
        ["ref0", "ref1"],
        "form",
        ["parent0", "parent1"],
        "@",
        {"fcol": ["val0", "val1"]},
        True,
    )
    read_build_write_index.reset_mock()
    sys.argv = [
        "indeksilo",
        "--ref-col",
        "ref0",
        "--form-col",
        "form",
        "input.ods",
        "output.ods",
    ]
    indeksilo.cli.main()
    read_build_write_index.assert_called_once_with(
        "input.ods",
        "output.ods",
        ["ref0"],
        "form",
        None,
        None,
        None,
        False,
    )


def test_filter_args(mocker):
    """
    test that the format of the expression of filter arguments is checked.
    """
    import sys

    import indeksilo.cli

    sys.argv = [
        "indeksilo",
        "--ref-col",
        "ref0",
        "--form-col",
        "form",
        "--filter",
        "val0",
        "input.ods",
        "output.ods",
    ]
    with pytest.raises(SystemExit):
        indeksilo.cli.main()


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
        {"fcol": ["val0", "val1"]},
        True,
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
            "fcol",
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
        {"fcol": ["val0", "val1"]},
        True,
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
        {},
        False,
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


def test_empty_form():
    """
    test that a line with no data in the form column is skipped.
    """
    df = pd.DataFrame(
        {
            "form": ["abc", "", "def"],
            "ref": ["r0", "r1", "r2"],
        }
    )
    index_df = indeksilo.build_index(
        df,
        ["ref"],
        "form",
    )
    expected_index_df = pd.DataFrame(
        {
            "form_count": [1, 1],
            "form": ["abc", "def"],
            "refs": ["r0", "r2"],
        }
    )
    assert index_df.compare(expected_index_df).empty


def test_filter():
    """
    test that filtering works.
    """
    df = pd.DataFrame(
        {
            "form": ["abcdef", "xyz", "abc", "def", "xyzabc"],
            "ref": ["r0", "r1", "r2", "r3", "r4"],
            "parent": ["a@d", "x", "a", "d", "x@a"],
            "pos": ["val0@val1", "val2", "val0", "val1", "val2@val0"],
        }
    )
    index_df = indeksilo.build_index(
        df, ["ref"], "form", ["parent"], "@", {"pos": ["val0", "val2"]}
    )
    expected_index_df = pd.DataFrame(
        {
            "parent_count": [3, "", "", 2, ""],
            "parent": ["a", "", "", "x", ""],
            "form_count": [1, 1, 1, 1, 1],
            "form": ["abc", "abcdef", "xyzabc", "xyz", "xyzabc"],
            "refs": ["r2", "r0", "r4", "r1", "r4"],
        }
    )
    assert index_df.compare(expected_index_df).empty
    index_df = indeksilo.build_index(
        df,
        ["ref"],
        "form",
        ["parent"],
        "@",
        {"pos": ["val0", "val2"]},
        True,
    )
    expected_index_df = pd.DataFrame(
        {
            "parent_count": [2, ""],
            "parent": ["d", ""],
            "form_count": [1, 1],
            "form": ["abcdef", "def"],
            "refs": ["r0", "r3"],
        }
    )
    assert index_df.compare(expected_index_df).empty
    index_df = indeksilo.build_index(
        df,
        ["ref"],
        "form",
        ["parent"],
        "@",
        {"form": ["xyz", "abc"]},
        True,
    )
    expected_index_df = pd.DataFrame(
        {
            "parent_count": [2, "", 2, "", 1],
            "parent": ["a", "", "d", "", "x"],
            "form_count": [1, 1, 1, 1, 1],
            "form": ["abcdef", "xyzabc", "abcdef", "def", "xyzabc"],
            "refs": ["r0", "r4", "r0", "r3", "r4"],
        }
    )
    assert index_df.compare(expected_index_df).empty
