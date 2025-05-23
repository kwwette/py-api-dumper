from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            name="api_ref.ext_mod",
            sources=["api_ref/ext_mod.c"],
        ),
    ]
)
