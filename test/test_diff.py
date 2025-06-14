# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

import io
import json
import textwrap
from pathlib import Path

import api_ref
import pytest

from py_api_dumper import APIDiff, APIDump
from py_api_dumper.cli import cli


@pytest.fixture
def api_dump(monkeypatch):
    """
    Return API dump of `api_ref`.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.1", raising=False)
    return APIDump.from_modules(api_ref)


@pytest.fixture
def api_dump_file(api_dump, request):
    """
    Write API dump of `api_ref` to a file.
    """
    api_dump_file = request.path.parent / "test_dump.tmp"
    api_dump.save_to_file(api_dump_file)
    return api_dump_file


def _check_diff(api_diff, expected):
    """
    Check diff text is as expected.
    """
    api_diff_text = io.StringIO()
    api_diff.print_as_text(api_diff_text)
    expected = textwrap.dedent(expected).lstrip().replace("    ", "\t")
    assert api_diff_text.getvalue() == expected


def test_diff_same(api_dump, monkeypatch):
    """
    Test for no diff.
    """
    api_diff = APIDiff(api_dump, api_dump)
    assert api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.1
        """,
    )


def test_diff_added_member(api_dump, monkeypatch):
    """
    Test diff with added member.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)
    monkeypatch.setattr(api_ref, "new1", 42, raising=False)
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        +MODULE : api_ref
        +    MEMBER : new1 : int
        """,
    )


def test_diff_removed_member(api_dump, monkeypatch):
    """
    Test diff with removed member.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)
    monkeypatch.delattr(api_ref.pub_mod, "d1")
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        -MODULE : api_ref
        -    MODULE : pub_mod
        -        MEMBER : d1 : int
        """,
    )


def test_diff_added_function(api_dump, monkeypatch):
    """
    Test diff with added function.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)

    def newF(x):
        pass

    monkeypatch.setattr(api_ref, "newF", newF, raising=False)
    monkeypatch.setattr(api_ref.newF, "__module__", api_ref.__name__)
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        +MODULE : api_ref
        +    FUNCTION : newF : no-return-type
        +        REQUIRED : 0 : x : no-type
        """,
    )


def test_diff_added_function_argument(api_dump, monkeypatch):
    """
    Test diff with added function argument.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)

    def F1(a, b):
        pass

    monkeypatch.setattr(api_ref, "F1", F1, raising=False)
    monkeypatch.setattr(api_ref.F1, "__module__", api_ref.__name__)
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        +MODULE : api_ref
        +    FUNCTION : F1 : no-return-type
        +        REQUIRED : 1 : b : no-type
        """,
    )


def test_diff_removed_function(api_dump, monkeypatch):
    """
    Test diff with removed function.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)
    monkeypatch.delattr(api_ref, "F4")
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        -MODULE : api_ref
        -    FUNCTION : F4 : None
        -        OPTIONAL : b : typing.Optional[bool]
        -        REQUIRED : 0 : a : typing.Union[typing.List, str]
        """,
    )


def test_diff_added_class(api_dump, monkeypatch):
    """
    Test diff with added class.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)

    class newC:
        def __init__(self, A):
            pass

        def B(self, x=0):
            pass

    monkeypatch.setattr(api_ref, "newC", newC, raising=False)
    for o in (api_ref.newC, api_ref.newC.__init__, api_ref.newC.B):
        monkeypatch.setattr(o, "__module__", api_ref.__name__)
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        +MODULE : api_ref
        +    CLASS : newC
        +        FUNCTION : B : no-return-type
        +            OPTIONAL : x : no-type
        +            REQUIRED : 0 : self : no-type
        +        FUNCTION : __init__ : no-return-type
        +            REQUIRED : 0 : self : no-type
        +            REQUIRED : 1 : A : no-type
        """,
    )


def test_diff_removed_class(api_dump, monkeypatch):
    """
    Test diff with removed class.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)
    monkeypatch.delattr(api_ref.pub_mod.C1, "C2")
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        -MODULE : api_ref
        -    MODULE : pub_mod
        -        CLASS : C1
        -            CLASS : C2
        -                FUNCTION : N1 : no-return-type
        -                    OPTIONAL : hh : no-type
        -                    REQUIRED : 0 : self : no-type
        -                    REQUIRED : 1 : gg : no-type
        -                FUNCTION : __init__ : no-return-type
        -                    OPTIONAL : h : no-type
        -                    REQUIRED : 0 : self : no-type
        -                    REQUIRED : 1 : g : no-type
        -                MEMBER : g1 : int
        """,
    )


def test_diff_added_method(api_dump, monkeypatch):
    """
    Test diff with added method.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)

    def newM(self, y=False):
        pass

    monkeypatch.setattr(api_ref.pub_mod.C1, "newM", newM, raising=False)
    monkeypatch.setattr(api_ref.pub_mod.C1.newM, "__module__", api_ref.pub_mod.__name__)
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        +MODULE : api_ref
        +    MODULE : pub_mod
        +        CLASS : C1
        +            FUNCTION : newM : no-return-type
        +                OPTIONAL : y : no-type
        +                REQUIRED : 0 : self : no-type
        """,
    )


def test_diff_removed_method(api_dump, monkeypatch):
    """
    Test diff with removed method.
    """
    monkeypatch.setattr(api_ref, "__version__", "0.2", raising=False)
    monkeypatch.delattr(api_ref.pub_mod.C1, "M1")
    api_dump_new = APIDump.from_modules(api_ref)
    api_diff = APIDiff(api_dump, api_dump_new)
    assert not api_diff.equal()
    _check_diff(
        api_diff,
        """
        --- /dev/null api_ref=0.1
        +++ /dev/null api_ref=0.2
        -MODULE : api_ref
        -    MODULE : pub_mod
        -        CLASS : C1
        -            FUNCTION : M1 : no-return-type
        -                REQUIRED : 0 : self : no-type
        -                REQUIRED : 1 : z : no-type
        """,
    )


@pytest.fixture
def api_dump_new(monkeypatch):
    """
    Return API dump of `api_ref` with lots of changes.
    """
    monkeypatch.setattr(api_ref, "__version__", "1.0", raising=False)

    def newF(x):
        pass

    class newC:
        def __init__(self, A):
            pass

        def B(self, x=0):
            pass

    def newM(self, y=False):
        pass

    monkeypatch.setattr(api_ref, "new1", 42, raising=False)
    monkeypatch.delattr(api_ref.pub_mod, "d1")
    monkeypatch.setattr(api_ref, "newF", newF, raising=False)
    monkeypatch.setattr(api_ref.newF, "__module__", api_ref.__name__)
    monkeypatch.delattr(api_ref, "F4")
    monkeypatch.setattr(api_ref, "newC", newC, raising=False)
    for o in (api_ref.newC, api_ref.newC.__init__, api_ref.newC.B):
        monkeypatch.setattr(o, "__module__", api_ref.__name__)
    monkeypatch.delattr(api_ref.pub_mod.C1, "C2")
    monkeypatch.setattr(api_ref.pub_mod.C1, "newM", newM, raising=False)
    monkeypatch.setattr(api_ref.pub_mod.C1.newM, "__module__", api_ref.pub_mod.__name__)
    monkeypatch.delattr(api_ref.pub_mod.C1, "M1")
    return APIDump.from_modules(api_ref)


@pytest.fixture
def api_dump_new_file(api_dump_new, request):
    """
    Write API dump of `api_ref` with lots of changes to a file.
    """
    api_dump_new_file = request.path.parent / "test_dump_new.tmp"
    api_dump_new.save_to_file(api_dump_new_file)
    return api_dump_new_file


def test_diff_cli(api_dump_file, api_dump_new_file, request, monkeypatch, capfd):
    """
    Test comparing API dumps using the command-line interface.
    """
    wd = request.path.parent
    monkeypatch.chdir(wd)
    cli("diff", api_dump_file.relative_to(wd), api_dump_new_file.relative_to(wd))
    diff_1 = capfd.readouterr().out
    api_diff_file = wd / "test_diff.txt.tmp"
    cli(
        "diff",
        api_dump_file.relative_to(wd),
        api_dump_new_file.relative_to(wd),
        "-o",
        api_diff_file,
        "-t",
    )
    diff_2 = api_diff_file.read_text()
    expected = """
    --- test_dump.tmp api_ref=0.1
    +++ test_dump_new.tmp api_ref=1.0
    -MODULE : api_ref
    -	FUNCTION : F4 : None
    -		OPTIONAL : b : typing.Optional[bool]
    -		REQUIRED : 0 : a : typing.Union[typing.List, str]
    -	MODULE : pub_mod
    -		CLASS : C1
    -			CLASS : C2
    -				FUNCTION : N1 : no-return-type
    -					OPTIONAL : hh : no-type
    -					REQUIRED : 0 : self : no-type
    -					REQUIRED : 1 : gg : no-type
    -				FUNCTION : __init__ : no-return-type
    -					OPTIONAL : h : no-type
    -					REQUIRED : 0 : self : no-type
    -					REQUIRED : 1 : g : no-type
    -				MEMBER : g1 : int
    -			FUNCTION : M1 : no-return-type
    -				REQUIRED : 0 : self : no-type
    -				REQUIRED : 1 : z : no-type
    -		MEMBER : d1 : int
    +MODULE : api_ref
    +	CLASS : newC
    +		FUNCTION : B : no-return-type
    +			OPTIONAL : x : no-type
    +			REQUIRED : 0 : self : no-type
    +		FUNCTION : __init__ : no-return-type
    +			REQUIRED : 0 : self : no-type
    +			REQUIRED : 1 : A : no-type
    +	FUNCTION : newF : no-return-type
    +		REQUIRED : 0 : x : no-type
    +	MEMBER : new1 : int
    +	MODULE : pub_mod
    +		CLASS : C1
    +			FUNCTION : newM : no-return-type
    +				OPTIONAL : y : no-type
    +				REQUIRED : 0 : self : no-type
    """
    expected = textwrap.dedent(expected).lstrip().replace("    ", "\t")
    assert diff_1 == expected
    assert diff_2 == expected


def test_diff_cli_json(api_dump_file, api_dump_new_file, request):
    """
    Test writing API diffs in JSON format using the command-line interface.
    """
    api_diff = APIDiff.from_files(api_dump_file, api_dump_new_file)
    api_diff_file = request.path.parent / "test_diff.tmp"
    cli("diff", api_dump_file, api_dump_new_file, "-o", api_diff_file)
    api_diff_json = json.load(api_diff_file.open("rt"))
    assert api_diff.old_dump_file == Path(api_diff_json["old_dump"])
    assert api_diff.new_dump_file == Path(api_diff_json["new_dump"])
    assert api_diff.old_modules["api_ref"] == api_diff_json["old_modules"]["api_ref"]
    assert api_diff.new_modules["api_ref"] == api_diff_json["new_modules"]["api_ref"]
    assert api_diff.removed == set(
        tuple(tuple(e) for e in entry) for entry in api_diff_json["removed"]
    )
    assert api_diff.added == set(
        tuple(tuple(e) for e in entry) for entry in api_diff_json["added"]
    )
