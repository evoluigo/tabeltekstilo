# SPDX-FileCopyrightText: 2024 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd

import tabeltekstilo
import tabeltekstilo.cli


def test_main(mocker):
    """
    test that the main() function calls
    convert_tabular_text_file_to_xml_file() with correct options.
    """
    import sys

    sys.argv = [
        "tabeltekstilo",
        "xml",
        "--root-element",
        "root",
        "--parent-prefix",
        "parent: ",
        "--copyright",
        "© 2024 some copyright",
        "--license",
        "https://creativecommons.org/licenses/by-sa/4.0/",
        "input.ods",
        "output.xml",
    ]
    convert_tabular_text_file_to_xml_file = mocker.patch(
        "tabeltekstilo.cli.convert_tabular_text_file_to_xml_file"
    )
    tabeltekstilo.cli.main()
    convert_tabular_text_file_to_xml_file.assert_called_once_with(
        "input.ods",
        "output.xml",
        root_element="root",
        parent_prefix="parent: ",
        copyright="© 2024 some copyright",
        license="https://creativecommons.org/licenses/by-sa/4.0/",
    )
    convert_tabular_text_file_to_xml_file.reset_mock()
    sys.argv = [
        "tabeltekstilo",
        "xml",
        "input.ods",
        "output.xml",
    ]
    tabeltekstilo.cli.main()
    convert_tabular_text_file_to_xml_file.assert_called_once_with(
        "input.ods",
        "output.xml",
        root_element=None,
        parent_prefix=None,
        copyright=None,
        license=None,
    )


def test_convert_tabular_text_file_to_xml_file(mocker):
    """
    test that convert_tabular_text_file_to_xml_file() reads the necessary
    columns from the data file, calls convert_tabular_text_to_xml() with
    correct arguments and writes the result to the output file.
    """
    from unittest.mock import call, mock_open

    read_excel = mocker.patch("pandas.read_excel")
    df = pd.DataFrame(
        {
            "w": [],
        }
    )
    read_excel.return_value = df
    convert_tabular_text_to_xml = mocker.patch(
        "tabeltekstilo.xml.convert_tabular_text_to_xml"
    )
    xml_bytes = (
        b'<?xml version="1.0" encoding="utf-8"?>\n'
        b"<document>\n"
        b"</document>"
    )
    convert_tabular_text_to_xml.return_value = xml_bytes
    open_mock = mocker.patch("builtins.open", mock_open())
    tabeltekstilo.convert_tabular_text_file_to_xml_file(
        "input.ods",
        "output.xml",
        root_element="root",
        parent_prefix="parent: ",
        copyright="© 2024 some copyright",
        license="https://creativecommons.org/licenses/by-sa/4.0/",
    )
    pd.read_excel.assert_called_once_with(
        "input.ods", dtype=str, keep_default_na=False
    )
    convert_tabular_text_to_xml.assert_called_once_with(
        df,
        "root",
        "parent: ",
        "© 2024 some copyright",
        "https://creativecommons.org/licenses/by-sa/4.0/",
    )
    open_mock.assert_called_once_with("output.xml", "wb")
    open_mock().write.assert_has_calls([call(xml_bytes), call(b"\n")])
    pd.read_excel.reset_mock()
    convert_tabular_text_to_xml.reset_mock()
    open_mock.reset_mock()
    tabeltekstilo.convert_tabular_text_file_to_xml_file(
        "input.ods", "output.xml"
    )
    pd.read_excel.assert_called_once_with(
        "input.ods", dtype=str, keep_default_na=False
    )
    convert_tabular_text_to_xml.assert_called_once_with(
        df, None, None, None, None
    )
    open_mock.assert_called_once_with("output.xml", "wb")
    open_mock().write.assert_has_calls([call(xml_bytes), call(b"\n")])


def test_convert_tabular_text_to_xml(mocker):
    """
    test that convert_tabular_text_to_xml() correctly converts to xml.
    """
    df = pd.DataFrame(
        {
            "parent_parent1 val": ["a", "a", "a", "b", "b", "b", "b"],
            "parent_parent2 attr": ["c", "c", "d", "d", "e", "e", "f"],
            "value": ["g", "g", "g", "h", "h", "i", "i"],
            "form": ["j", "k", "k", "l", "l", "l", "m"],
        }
    )
    xml_bytes = tabeltekstilo.convert_tabular_text_to_xml(
        df,
        "root",
        "parent_",
        "© 2024 some copyright",
        "https://creativecommons.org/licenses/by-sa/4.0/",
    )
    expected_xml_bytes = b"""<?xml version="1.0" encoding="utf-8"?>
<root>
  <header>
    <copyright>\xc2\xa9 2024 some copyright</copyright>
    <license>
      <ref>https://creativecommons.org/licenses/by-sa/4.0/</ref>
    </license>
  </header>
  <parent1 val="a">
    <parent2 attr="c">
      <form value="g">j</form>
      <form value="g">k</form>
    </parent2>
    <parent2 attr="d">
      <form value="g">k</form>
    </parent2>
  </parent1>
  <parent1 val="b">
    <parent2 attr="d">
      <form value="h">l</form>
    </parent2>
    <parent2 attr="e">
      <form value="h">l</form>
      <form value="i">l</form>
    </parent2>
    <parent2 attr="f">
      <form value="i">m</form>
    </parent2>
  </parent1>
</root>"""
    assert xml_bytes == expected_xml_bytes
    xml_bytes = tabeltekstilo.convert_tabular_text_to_xml(df)
    expected_xml_bytes = b"""<?xml version="1.0" encoding="utf-8"?>
<document>
  <parent_parent1 val="a">
    <parent_parent2 attr="c">
      <form value="g">j</form>
      <form value="g">k</form>
    </parent_parent2>
    <parent_parent2 attr="d">
      <form value="g">k</form>
    </parent_parent2>
  </parent_parent1>
  <parent_parent1 val="b">
    <parent_parent2 attr="d">
      <form value="h">l</form>
    </parent_parent2>
    <parent_parent2 attr="e">
      <form value="h">l</form>
      <form value="i">l</form>
    </parent_parent2>
    <parent_parent2 attr="f">
      <form value="i">m</form>
    </parent_parent2>
  </parent_parent1>
</document>"""
    assert xml_bytes == expected_xml_bytes


def test_columns_with_same_name(mocker):
    """
    test that convert_tabular_text_to_xml() correctly removes the numeric
    suffix that pandas adds to columns with similar names when it converts to
    xml.
    """
    df = pd.DataFrame(
        {
            "id": ["1", "2", "3", "4", "5", "6", "7"],
            "parent1 val": ["a", "a", "a", "b", "b", "b", "b"],
            "parent2 attr": ["c", "c", "d", "d", "e", "e", "f"],
            "id.1": ["1", "2", "3", "4", "5", "6", "7"],
            "value": ["g", "g", "g", "h", "h", "i", "i"],
            "form": ["j", "k", "k", "l", "l", "l", "m"],
        }
    )
    xml_bytes = tabeltekstilo.convert_tabular_text_to_xml(df)
    expected_xml_bytes = b"""<?xml version="1.0" encoding="utf-8"?>
<document>
  <parent1 val="a">
    <parent2 attr="c">
      <form id="1" value="g">j</form>
      <form id="2" value="g">k</form>
    </parent2>
    <parent2 attr="d">
      <form id="3" value="g">k</form>
    </parent2>
  </parent1>
  <parent1 val="b">
    <parent2 attr="d">
      <form id="4" value="h">l</form>
    </parent2>
    <parent2 attr="e">
      <form id="5" value="h">l</form>
      <form id="6" value="i">l</form>
    </parent2>
    <parent2 attr="f">
      <form id="7" value="i">m</form>
    </parent2>
  </parent1>
</document>"""
    assert xml_bytes == expected_xml_bytes
