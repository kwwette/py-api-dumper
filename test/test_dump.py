# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import api_ref
import pytest

from py_api_dumper import APIDump
from py_api_dumper.cli import cli


def _compare_dumps(api_dump_text):
    """
    Compare API dump of `api_ref` against reference result.
    """
    api_dump_text_ref = Path(api_ref.__file__).parent / "api_ref.txt"
    lines_to_compare = [
        f.read_text().replace("\t", "    ").splitlines()
        for f in (api_dump_text, api_dump_text_ref)
    ]
    assert lines_to_compare[0] == lines_to_compare[1]


def test_dump_module(request):
    """
    Create API dump from module.
    """
    api_dump = APIDump.from_modules(api_ref)
    api_dump_text = request.path.parent / "test_dump.txt.tmp"
    api_dump.print_as_text(api_dump_text.open("w"))
    _compare_dumps(api_dump_text)


def test_dump_module_str_name(request):
    """
    Create API dump from module string name.
    """
    api_dump = APIDump.from_modules("api_ref")
    api_dump_text = request.path.parent / "test_dump.txt.tmp"
    api_dump.print_as_text(api_dump_text.open("w"))
    _compare_dumps(api_dump_text)


def test_dump_module_cli(request):
    """
    Create API dump using the command-line interface.
    """
    api_dump_text = request.path.parent / "test_dump.txt.tmp"
    cli("dump", "--output", api_dump_text, "--text", "api_ref")
    _compare_dumps(api_dump_text)


def test_dump_file(request):
    """
    Test save and loading API dumps.
    """
    api_dump = APIDump.from_modules(api_ref)
    api_dump_file = request.path.parent / "test_dump.tmp"
    api_dump.save_to_file(api_dump_file)
    api_dump_from_file = APIDump.load_from_file(api_dump_file)
    assert api_dump == api_dump_from_file


@pytest.mark.parametrize("file_name", ["test_dump.tmp", "test_dump.tmp.gz"])
def test_dump_file_cli(request, file_name):
    """
    Test saving and loading API dumps using the command-line interface.
    """
    api_dump = APIDump.from_modules(api_ref)
    api_dump_file = request.path.parent / file_name
    cli("dump", "--output", api_dump_file, "api_ref")
    api_dump_from_file = APIDump.load_from_file(api_dump_file)
    assert api_dump == api_dump_from_file


def test_cli():
    """
    Test the command-line interface.
    """
    with pytest.raises(SystemExit):
        cli("--help")
    cli("dump", "api_ref")
