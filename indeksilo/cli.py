# SPDX-FileCopyrightText: 2023 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse

from indeksilo import read_build_write_index


def main():
    parser = argparse.ArgumentParser(
        description=(
            "generate a multi-level alphabetical index from text in tabular "
            "data format"
        )
    )
    parser.add_argument(
        "input_filename", help="the input filename (.ods or .xlsx)"
    )
    parser.add_argument(
        "output_filename", help="the output filename (.ods or .xlsx)"
    )
    parser.add_argument(
        "--ref-col",
        required=True,
        action="append",
        help=(
            "title of the column that contains the reference (can be used "
            "multiple times)"
        ),
    )
    parser.add_argument(
        "--parent-col",
        action="append",
        help=(
            "title of the column that contains the parent of the next column "
            "(can be used multiple times)"
        ),
    )
    parser.add_argument(
        "--form-col",
        required=True,
        help=(
            "title of the column that contains the form that will appear in "
            "the index"
        ),
    )
    parser.add_argument(
        "--split-char",
        help="character used to split words (default: no splitting)",
    )
    args = parser.parse_args()
    read_build_write_index(
        args.input_filename,
        args.output_filename,
        args.ref_col,
        args.form_col,
        args.parent_col,
        args.split_char,
    )
