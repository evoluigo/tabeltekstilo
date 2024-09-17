# SPDX-FileCopyrightText: 2024 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import re
from xml.etree import ElementTree

import pandas as pd

_PARENT_TAG_REGEX_STR = "(?P<tag>[^ ]*) (?P<attr>.*)"
DEFAULT_ROOT_ELEMENT = "document"


def add_header(root, copyright, license):
    if copyright is None and license is None:
        return
    header = ElementTree.SubElement(root, "header")
    if copyright is not None:
        copyright_elem = ElementTree.SubElement(header, "copyright")
        copyright_elem.text = copyright
    if license is not None:
        license_elem = ElementTree.SubElement(header, "license")
        license_ref_elem = ElementTree.SubElement(license_elem, "ref")
        license_ref_elem.text = license


def get_cols(df, parent_prefix):
    parent_cols = []
    child_cols = []
    parent_tag_regex_str = _PARENT_TAG_REGEX_STR
    if parent_prefix:
        parent_tag_regex_str = parent_prefix + parent_tag_regex_str
    parent_tag_regex = re.compile(parent_tag_regex_str)
    for i, column in enumerate(df.columns):
        match = parent_tag_regex.match(column)
        if match is None:
            # split on . to remove the numeric suffix that pandas adds when
            # several columns have the same name.
            child_cols.append((i, column.split(".")[0]))
        else:
            parent_cols.append((i, match.group("tag"), match.group("attr")))
    return parent_cols, child_cols


def convert_tabular_text_to_etree(
    df,
    root_element=None,
    parent_prefix=None,
    copyright=None,
    license=None,
):
    """
    convert the text in tabular data format from the
    pandas DataFrame df to an xml element.
    """
    parent_cols, child_cols = get_cols(df, parent_prefix)
    w_col_i, w_col_tag = child_cols.pop()
    if root_element is None:
        root_element = DEFAULT_ROOT_ELEMENT
    root = ElementTree.Element(root_element)
    add_header(root, copyright, license)
    parents = [None] * len(parent_cols)
    parents.insert(0, root)
    parent = None
    previous_row = (None,) * len(parent_cols)
    for row in df.itertuples(index=False, name=None):
        for i, (col_i, tag, attr) in enumerate(parent_cols):
            if parent is None or previous_row[col_i] != row[col_i]:
                p = ElementTree.SubElement(parents[i], tag)
                p.set(attr, row[col_i])
                parents[i + 1] = p
                parent = None
        parent = parents[-1]
        w = ElementTree.SubElement(parent, w_col_tag)
        for col_i, attr in child_cols:
            w.set(attr, row[col_i])
        w.text = row[w_col_i]
        previous_row = row
    return root


def to_xml_bytes(root):
    # write the xml declaration manually because xml.etree uses single
    # quotes.
    declaration = b'<?xml version="1.0" encoding="utf-8"?>\n'
    ElementTree.indent(root)
    return declaration + ElementTree.tostring(root, encoding="utf-8")


def convert_tabular_text_to_xml(
    df,
    root_element=None,
    parent_prefix=None,
    copyright=None,
    license=None,
):
    root = convert_tabular_text_to_etree(
        df, root_element, parent_prefix, copyright, license
    )
    return to_xml_bytes(root)


def convert_tabular_text_file_to_xml_file(  # noqa: PLR0913
    input_filename,
    output_filename,
    root_element=None,
    parent_prefix=None,
    copyright=None,
    license=None,
):
    """
    convert text in tabular data format to xml
    """
    # read whole file
    # dtype=str is to interpret all values as strings. keep_default_na=False
    # is to avoid empty cells to be interpreted as nan.
    df = pd.read_excel(input_filename, dtype=str, keep_default_na=False)
    with open(output_filename, "wb") as f:
        f.write(
            convert_tabular_text_to_xml(
                df, root_element, parent_prefix, copyright, license
            )
        )
        f.write(b"\n")
