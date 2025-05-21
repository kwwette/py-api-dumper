import importlib
import importlib.metadata
import inspect
import pkgutil
import sys
from types import ModuleType
from typing import List, Optional, TextIO, Type, TypeVar, Union

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

    @classmethod
    def from_modules(
        cls: Type[APIDumpType], modules: List[Union[ModuleType, str]]
    ) -> APIDumpType:
        """
        Dump the public API of the given Python modules.

        Args:
            modules (List[Union[ModuleType, str]]):
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
            inst._dump_struct(module_prefix, module)

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

    def _dump_struct(self, prefix, struct):

        # Add base entry
        self._add_api_entry(prefix)

        # Iterate over struct members
        members = inspect.getmembers(struct)
        for member_name, member in members:

            # Exclude any private members
            if member_name.startswith("_"):
                pass

            # Skip any modules
            # - all relevant modules have already been found by _load_all_modules()
            elif inspect.ismodule(member):
                pass

            # Dump classes
            elif inspect.isclass(member):
                class_prefix = prefix + [("CLASS", member.__name__)]
                self._dump_struct(class_prefix, member)

            # Dump functions
            elif inspect.isroutine(member):
                self._dump_function(prefix, member)

            # Dump properties
            elif isinstance(member, property) or inspect.isgetsetdescriptor(member):
                self._dump_property(prefix, member_name)

            else:
                # Dump everything else
                self._dump_member(prefix, member_name, member)

    def _dump_function(self, prefix, fun):

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
            func_entry = prefix + [("FUNCTION", fun.__name__, return_type)]
        else:
            func_entry = prefix + [("FUNCTION", fun.__name__, "no-signature")]
        self._add_api_entry(func_entry)

        # Add function signature, if available
        if sig is not None:
            n_req_arg = 0
            for n, par in enumerate(sig.parameters.values()):
                if par.annotation != par.empty:
                    par_type = str(par.annotation)
                else:
                    par_type = "no-type"
                if par.default == par.empty:
                    par_entry = [("REQUIRED", n_req_arg, par.name, par_type)]
                    n_req_arg += 1
                else:
                    par_entry = [("OPTIONAL", par.name, par_type)]
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
            entry_str = " ".join(str(e) for e in entry[-1])
            print(indent + entry_str, file=to)
