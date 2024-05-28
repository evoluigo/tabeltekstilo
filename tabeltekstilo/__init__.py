# SPDX-FileCopyrightText: 2023 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from .dictionary import build_dictionary, read_build_write_dictionary
from .index import build_index, read_build_write_index

__all__ = [
    "build_dictionary",
    "build_index",
    "read_build_write_dictionary",
    "read_build_write_index",
]

__version__ = "0.1.0"
