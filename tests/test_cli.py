# SPDX-FileCopyrightText: 2024 hugues de keyzer
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import tabeltekstilo
import tabeltekstilo.cli


def test_version(mocker):
    """
    test that the cli prints the version.
    """
    import sys

    sys.argv = [
        "tabeltekstilo",
        "--version",
    ]
    print_mock = mocker.patch("builtins.print")
    tabeltekstilo.cli.main()
    print_mock.assert_called_once_with(
        f"tabeltekstilo {tabeltekstilo.__version__}"
    )


def test_no_subcommand(mocker):
    """
    test that the cli without subcommand prints an error message.
    """
    import sys
    from unittest.mock import call

    import pytest

    sys.argv = ["tabeltekstilo"]
    write_mock = mocker.patch("sys.stderr.write")
    with pytest.raises(SystemExit):
        tabeltekstilo.cli.main()
    write_mock.assert_has_calls(
        [
            call(
                "usage: tabeltekstilo [-h] [--version] {dictionary,index} "
                "...\n"
            ),
            call(
                "tabeltekstilo: error: the following arguments are required: "
                "subcommand\n"
            ),
        ]
    )
