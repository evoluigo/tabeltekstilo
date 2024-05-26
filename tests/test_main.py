# SPDX-FileCopyrightText: 2024 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later


def test_main_package_entry():
    """
    test that tabeltekstilo.__main__ is well-formed.
    """
    from tabeltekstilo import __main__  # noqa: F401
