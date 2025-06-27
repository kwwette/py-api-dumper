# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

"""Public module."""

# import from another module (considered private)
from . import F3


class C1:
    """Public class."""

    # public fields
    f1 = 1.2
    f2 = "there"

    # private fields
    _f3 = F3
    _v = 1

    @staticmethod
    def help():
        """Public static method."""

    @classmethod
    def from_args(cls, z):
        """Public class method."""
        return cls(z)

    def __init__(self, x, *y):
        """Constructor (considered public)."""
        pass

    def M1(self, z):
        """Public method."""
        pass

    def M2(self, z, *, u, v=0):
        """Public method."""
        pass

    def M3(self, w: int, /, x: str, y: float = 0, z: float = 1):
        """Public method."""
        pass

    @property
    def v(self):
        """Public property."""
        return self._v

    @v.setter
    def v(self, v):
        self._v = v

    # private methods
    def _M4(self):
        pass

    class C2:
        """Public nested class."""

        g1 = 9
        _g2 = 4

        def __init__(self, g, h=True):
            """Constructor (considered public)."""
            pass

        def N1(self, gg, *hh):
            """Public method."""
            pass

    # private nested class
    class _C3:
        pass


# private class
class _C4:
    def __init__(self):
        pass


# public member
d1 = 27

# private member
_d2 = 94

# member with private type (considered private)
d3 = _C4()

# public function
F1 = lambda x: x  # noqa: E731
