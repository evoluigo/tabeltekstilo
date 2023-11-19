# SPDX-FileCopyrightText: 2023 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
from collections import defaultdict

from indeksilo import read_build_write_index

_FILTER_SEP = ":"


def _parse_filter_expr(parser, expr):
    split_expr = expr.split(_FILTER_SEP, maxsplit=1)
    if len(split_expr) != 2:  # noqa: PLR2004
        parser.error(
            'invalid filter expression: "{expr}"; must be of format '
            '"col{sep}regex"'.format(expr=expr, sep=_FILTER_SEP)
        )
    return tuple(split_expr)


def _parse_filters(parser, filter_args):
    if not filter_args:
        return None
    filters = defaultdict(list)
    for arg in filter_args:
        col, regex = _parse_filter_expr(parser, arg)
        filters[col].append(regex)
    return dict(filters)


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
        help=(
            "character used to split values in parent columns (default: no "
            "splitting)"
        ),
    )
    parser.add_argument(
        "--filter",
        action="append",
        help=(
            "filter by an expression; the format of the expression is "
            '"col{sep}regex", where col is a column name and regex is a '
            "regular expression matching the value (after splitting); can be "
            "used multiple times; the default behavior is to include only "
            "the rows that match an expression, rows not matching any of the "
            "expressions are ignored; this behavior can be reversed with "
            "--filter-exclude".format(sep=_FILTER_SEP)
        ),
    )
    parser.add_argument(
        "--filter-exclude",
        action="store_true",
        help=(
            "reverse the filter function: instead of including only the "
            "rows that match an expression, exclude all rows that match one; "
            "only the rows not matching any of the expressions are included"
        ),
    )
    args = parser.parse_args()
    filters = _parse_filters(parser, args.filter)
    read_build_write_index(
        args.input_filename,
        args.output_filename,
        args.ref_col,
        args.form_col,
        args.parent_col,
        args.split_char,
        filters,
        args.filter_exclude,
    )
