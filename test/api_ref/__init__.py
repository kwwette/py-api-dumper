# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

"""Public module."""

import sys
from typing import List, Optional, Union

from other_mod import G1  # noqa: F401 - import from another module (considered private)

from ._priv_mod import F3  # noqa: F401 - import private members into public API
from .pub_mod import C1  # noqa: F401 - import from a child module (considered private)

# public members
v1 = 3
v2 = "hello"

# skipped since `sys` is a module
v3 = sys

# private members
_v4 = "private"


def F1(a):
    """Public function."""
    pass


def F2(a, b, *c, **d):
    """Public function."""
    pass


def F4(a: Union[List, str], b: Optional[bool] = False) -> None:
    """Public function."""
    pass


# private functions
def _F5():
    pass
