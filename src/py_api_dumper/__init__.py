import importlib
import importlib.metadata
import inspect
import json
import pkgutil
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional, TextIO, Type, TypeVar, Union

__author__ = "Karl Wette"
__version__ = "0.1"

APIDumpType = TypeVar("APIDumpType", bound="APIDump")


class APIDump:
    """
    Dump the public API of a Python module and its members.
    """

    def __init__(self, *, api, versions):
        self._api = api
        self._versions = versions

    def __eq__(self, other):
        return self._api == other._api and self._versions == other._versions

    @classmethod
    def from_modules(
        cls: Type[APIDumpType], *modules: Union[ModuleType, str]
    ) -> APIDumpType:
        """
        Dump the public API of the given Python modules.

        Args:
            *modules (Union[ModuleType, str]):
                List of modules and/or their string names.

        Returns:
            APIDumpType: APIDump instance.
        """

        # Create instance
        inst = cls(api=set(), versions=dict())

        # Load all modules
        all_modules = inst._load_all_modules(modules)

        # Dump module APIs
        for module in all_modules:
            module_prefix = [("MODULE", m) for m in module.__name__.split(".")]
            inst._dump_struct(module_prefix, module, module)

        return inst

    def _load_all_modules(self, modules):

        # Walk and load (sub)modules
        all_modules = dict()
        for module_or_name in modules:

            # Load module if supplied a string name
            if isinstance(module_or_name, ModuleType):
                module = module_or_name
            else:
                module = importlib.import_module(module_or_name)

            # Save module
            if module.__name__ not in all_modules:
                all_modules[module.__name__] = module

            # Save module version
            try:
                module_version = importlib.metadata.version(module.__name__)
            except importlib.metadata.PackageNotFoundError:
                try:
                    module_version = module.__version__
                except AttributeError:
                    module_version = None
            self._versions[module.__name__] = module_version

            # Walk submodules
            for submodule_info in pkgutil.walk_packages(
                module.__path__, module.__name__ + "."
            ):

                # Exclude private submodules
                if any(m.startswith("_") for m in submodule_info.name.split(".")):
                    continue

                # Load submodule
                submodule = importlib.import_module(submodule_info.name)

                # Save submodule
                if submodule.__name__ not in all_modules:
                    all_modules[submodule.__name__] = submodule

        return list(all_modules.values())

    def _add_api_entry(self, entry):

        # Check that `entry` only contains `str` or `int` values
        _allowed_types = (str, int)
        assert all(
            all(isinstance(e, _allowed_types) for e in ee) for ee in entry
        ), tuple(tuple((e, isinstance(e, _allowed_types)) for e in ee) for ee in entry)

        # Add API entry
        self._api.add(tuple(entry))

    def _dump_struct(self, prefix, struct, module):

        # Add base entry
        self._add_api_entry(prefix)

        # Iterate over struct members
        members = inspect.getmembers(struct)
        for member_name, member in members:

            # Exclude any modules
            # - all relevant modules have already been found by _load_all_modules()
            if inspect.ismodule(member):
                continue

            # Exclude any private members, except class constructors
            if member_name.startswith("_") and member_name != "__init__":
                continue

            # Exclude any members defined in another module
            # - this should catch any `import`ed members
            if hasattr(member, "__module__") and member.__module__ != module.__name__:
                continue

            # Dump classes
            if inspect.isclass(member):
                class_prefix = prefix + [("CLASS", member.__name__)]
                self._dump_struct(class_prefix, member, module)

            # Dump methods and functions
            elif inspect.isroutine(member):
                if isinstance(
                    inspect.getattr_static(struct, member.__name__), staticmethod
                ):
                    self._dump_function(prefix, "STATICMETHOD", member)
                if inspect.ismethod(member) and isinstance(member.__self__, type):
                    self._dump_function(prefix, "CLASSMETHOD", member)
                else:
                    self._dump_function(prefix, "FUNCTION", member)

            # Dump properties
            elif isinstance(member, property) or inspect.isgetsetdescriptor(member):
                self._dump_property(prefix, member_name)

            else:
                # Dump everything else
                self._dump_member(prefix, member_name, member)

    def _dump_function(self, prefix, fun_type, fun):

        # Try to get function signature
        try:
            sig = inspect.signature(fun)
        except ValueError:
            sig = None

        # Add function entry
        if sig is not None:
            if sig.return_annotation != sig.empty:
                return_type = str(sig.return_annotation)
            else:
                return_type = "no-return-type"
            func_entry = prefix + [(fun_type, fun.__name__, return_type)]
        else:
            func_entry = prefix + [(fun_type, fun.__name__, "no-signature")]
        self._add_api_entry(func_entry)

        # Add function signature, if available
        if sig is not None:
            n_req_arg = 0
            for n, par in enumerate(sig.parameters.values()):
                if par.annotation != par.empty:
                    par_type = str(par.annotation)
                else:
                    par_type = "no-type"
                if par.default != par.empty or par.kind in (
                    par.VAR_POSITIONAL,
                    par.VAR_KEYWORD,
                ):
                    par_entry = [("OPTIONAL", par.name, par_type)]
                else:
                    par_entry = [("REQUIRED", n_req_arg, par.name, par_type)]
                    n_req_arg += 1
                self._add_api_entry(func_entry + par_entry)

    def _dump_property(self, prefix, name):

        # Add property entry
        entry = prefix + [("PROPERTY", name)]
        self._add_api_entry(entry)

    def _dump_member(self, prefix, name, val):

        # Exclude any private types
        typ = type(val).__name__
        if typ.startswith("_"):
            return

        # Add member entry
        entry = prefix + [("MEMBER", name, typ)]
        self._add_api_entry(entry)

    def print_as_text(self, to: Optional[TextIO] = sys.stdout) -> None:
        """
        Print the API dump as text to a file.

        Args:
            to (Optional[TextIO]):
                File to print to (default: standard output).
        """

        # Print API dump
        for entry in sorted(self._api):
            indent = "\t" * (len(entry) - 1)
            entry_str = " : ".join(str(e) for e in entry[-1])
            print(indent + entry_str, file=to)

    def save_to_file(self, file_path: Path) -> None:
        """
        Save the API dump to a file in a reloadable format.

        Args:
            file_path (Path):
                Name of file to save to.
        """

        # Assemble file content
        content = {"versions": self._versions, "api": list(sorted(self._api))}

        # Save to file as JSON
        json.dump(content, file_path.open("wt"))

    @classmethod
    def load_from_file(cls: Type[APIDumpType], file_path: Path) -> APIDumpType:
        """
        Load an API dump from a file.

        Args:
            file_path (Path):
                Name of file to load.

        Returns:
            APIDumpType: APIDump instance.
        """

        # Load from file as JSON
        content = json.load(file_path.open("rt"))

        # Create instance
        inst = cls(
            api=set(tuple(tuple(e) for e in entry) for entry in content["api"]),
            versions=dict(
                (module, version) for module, version in content["versions"].items()
            ),
        )

        return inst
