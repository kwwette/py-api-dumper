# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

### private module ###

this_is_a_private_module = True


def F3(a: int, b: bool = False, **d) -> str:
    """Private function imported into public API."""
    return ""
