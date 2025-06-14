# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

# import from another module (considered private)
from . import F3

### public module ###


# public classes
class C1:

    # public fields
    f1 = 1.2
    f2 = "there"

    # private fields
    _f3 = F3
    _v = 1

    # public static methods
    @staticmethod
    def help():
        pass

    # public class methods
    @classmethod
    def from_args(cls, z):
        return cls(z)

    # constructor (considered public)
    def __init__(self, x, *y):
        pass

    # public methods
    def M1(self, z):
        pass

    def M2(self, z, *, u, v=0):
        pass

    def M3(self, w: int, /, x: str, y: float = 0, z: float = 1):
        pass

    # public properties
    @property
    def v(self):
        return self._v

    @v.setter
    def v(self, v):
        self._v = v

    # private methods
    def _M4(self):
        pass

    # public nested class
    class C2:
        g1 = 9
        _g2 = 4

        def __init__(self, g, h=True):
            pass

        def N1(self, gg, *hh):
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
