# SPDX-FileCopyrightText: 2023 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from .dictionary import build_dictionary, read_build_write_dictionary
from .index import build_index, read_build_write_index
from .xml import (
    convert_tabular_text_file_to_xml_file,
    convert_tabular_text_to_xml,
)

__all__ = [
    "build_dictionary",
    "build_index",
    "convert_tabular_text_file_to_xml_file",
    "convert_tabular_text_to_xml",
    "read_build_write_dictionary",
    "read_build_write_index",
]

__version__ = "1.0.0"
