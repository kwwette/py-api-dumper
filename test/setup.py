# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

"""Build extension module `api_ref.ext_mod` needed for tests."""

from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            name="api_ref.ext_mod",
            sources=["api_ref/ext_mod.c"],
        ),
    ]
)
