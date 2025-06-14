# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

import sys
from typing import List, Optional, Union

### public module ###

# public members
v1 = 3
v2 = "hello"

# skipped since `sys` is a module
v3 = sys

# private members
_v4 = "private"


# public functions
def F1(a):
    pass


def F2(a, b, *c, **d):
    pass


def F3(a: int, b: bool = False, **d) -> str:
    return ""


def F4(a: Union[List, str], b: Optional[bool] = False) -> None:
    pass


# private functions
def _F5():
    pass
