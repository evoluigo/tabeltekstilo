# SPDX-FileCopyrightText: 2023 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import defaultdict

import pandas as pd
from pyuca import Collator

_REF_COL_SEPARATOR = ", "
_REF_SEPARATOR = "; "
_REF_WITH_COUNT_FORMAT = "{ref} ({count})"
_COUNT_COL_FORMAT = "{col}_count"
_REFS_COL_NAME = "refs"


def _index_factory(level):
    if level == 0:
        return list

    def subfactory():
        return defaultdict(_index_factory(level - 1))

    return subfactory


def _parse_row(r, parent_cols_i, split_char):
    if split_char is None:
        return [[r[i] for i in parent_cols_i]]
    parents = []
    for i in parent_cols_i:
        parents.append(r[i].split(split_char))
    return [p for p in zip(*parents)]


def _format_refs(refs):
    grouped_refs = []
    current_ref = refs[0]
    count = 1
    # + [None] is to run the loop one extra time since it processes each
    # element one iteration later.
    for ref in refs[1:] + [None]:
        if ref == current_ref:
            count += 1
        else:
            if count > 1:
                grouped_refs.append(
                    _REF_WITH_COUNT_FORMAT.format(ref=current_ref, count=count)
                )
            else:
                grouped_refs.append(current_ref)
            current_ref = ref
            count = 1
    return _REF_SEPARATOR.join(grouped_refs)


def _gen_index_list_single_parent(c, index, level=0):
    result = []
    parents = sorted(index, key=c.sort_key)
    num_entries = 0
    if level == 0:
        for p in parents:
            refs = index[p]
            num_refs = len(refs)
            num_entries += num_refs
            result.append([num_refs, p, _format_refs(refs)])
        return result, num_entries
    for p in parents:
        children, num_children_entries = _gen_index_list_single_parent(
            c, index[p], level - 1
        )
        num_entries += num_children_entries
        result.append([num_children_entries, p] + children[0])
        for child in children[1:]:
            result.append(["", ""] + child)
    return result, num_entries


def _gen_df_from_index(index, form_col, parent_cols):
    c = Collator()
    result, _ = _gen_index_list_single_parent(c, index, len(parent_cols))
    cols = []
    for c in parent_cols + [form_col]:
        cols.append(_COUNT_COL_FORMAT.format(col=c))
        cols.append(c)
    cols.append(_REFS_COL_NAME)
    return pd.DataFrame(result, columns=cols)


def build_index(
    df,
    ref_cols,
    form_col,
    parent_cols=None,
    split_char=None,
):
    if parent_cols is None:
        parent_cols = []
    col_names = []
    col_names.extend(ref_cols)
    ref_cols_i = list(range(len(ref_cols)))
    form_col_i = len(col_names)
    col_names.append(form_col)
    parent_cols_i = list(
        range(len(col_names), len(col_names) + len(parent_cols))
    )
    col_names.extend(parent_cols)
    df = df[col_names]
    num_levels = len(parent_cols) + 1
    index = _index_factory(num_levels)()
    for row in df.iterrows():
        r = row[1]
        refs = _REF_COL_SEPARATOR.join([r[i] for i in ref_cols_i])
        elems = _parse_row(r, parent_cols_i, split_char)
        form = r[form_col_i]
        if not form:
            continue
        for elem in elems:
            parent = index
            for e in elem:
                parent = parent[e]
            parent[form].append(refs)
    index_df = _gen_df_from_index(index, form_col, parent_cols)
    return index_df


def read_build_write_index(
    input_filename,
    output_filename,
    ref_cols,
    form_col,
    parent_cols=None,
    split_char=None,
):
    if parent_cols is None:
        parent_cols = []
    col_names = []
    col_names.extend(ref_cols)
    col_names.append(form_col)
    col_names.extend(parent_cols)
    df = pd.read_excel(
        input_filename, usecols=col_names, dtype=str, keep_default_na=False
    )
    index_df = build_index(df, ref_cols, form_col, parent_cols, split_char)
    index_df.to_excel(output_filename)
