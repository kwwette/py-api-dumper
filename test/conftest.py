# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

import shutil
import sys
from pathlib import Path
from subprocess import check_call

import pytest


@pytest.hookimpl
def pytest_sessionstart(session):
    """
    Build extension module `api_ref.ext_mod` needed for tests.
    """
    w = shutil.get_terminal_size().columns
    print(" build test extension module ".center(w, "-"))
    sys.stdout.flush()
    check_call(
        [
            sys.executable,
            "setup.py",
            "build_ext",
            "--build-lib",
            ".",
            "--build-temp",
            ".",
        ],
        cwd=Path(__file__).parent,
    )
    sys.stdout.flush()
