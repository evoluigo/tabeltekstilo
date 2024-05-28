# SPDX-FileCopyrightText: 2024 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
from pyuca import Collator

_DEFAULT_JOIN_STR = "; "
_WHITESPACE = " \u200c"


def build_dictionary(
    df,
    form_col,
    agg_cols,
    join_str=None,
):
    """
    build an alphabetical dictionary from the text in tabular data format from
    the pandas DataFrame df and output the result as a DataFrame.
    """
    if join_str is None:
        join_str = _DEFAULT_JOIN_STR
    j = join_str.join
    # avoid modifying the provided dataframe (in the next step)
    df = df.copy(deep=False)
    # strip whitespace in the form column
    df[form_col] = df[form_col].str.strip(_WHITESPACE)
    # remove rows where the form column is empty
    df = df[df[form_col].astype(bool)]
    columns = [form_col] + agg_cols
    # sort values alphabetically
    c = Collator()
    df = df.sort_values(columns, key=lambda x: x.map(c.sort_key))
    # drop duplicates to avoid aggregating the same value multiple times
    df = df.drop_duplicates(columns)
    # group by the form column, without sorting because it is already sorted
    df = df.groupby(form_col, sort=False)
    # aggregate by agg_cols
    df = df.agg({c: j for c in agg_cols})
    # reset index
    df = df.reset_index()
    return df


def read_build_write_dictionary(
    input_filename,
    output_filename,
    form_col,
    agg_cols,
    join_str=None,
):
    """
    build an alphabetical dictionary from the text in tabular data format from
    input_filename and write the result to output_filename.
    """
    col_names = [form_col] + agg_cols
    # dtype=str is to interpret all values as strings. keep_default_na=False
    # is to avoid empty cells to be interpreted as nan.
    df = pd.read_excel(
        input_filename, usecols=col_names, dtype=str, keep_default_na=False
    )
    dictionary_df = build_dictionary(df, form_col, agg_cols, join_str)
    dictionary_df.to_excel(output_filename)
