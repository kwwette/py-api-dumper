# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

"""Public module."""

import sys
from typing import List, Optional, Union

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


def F3(a: int, b: bool = False, **d) -> str:
    """Public function."""
    return ""


def F4(a: Union[List, str], b: Optional[bool] = False) -> None:
    """Public function."""
    pass


# private functions
def _F5():
    pass
