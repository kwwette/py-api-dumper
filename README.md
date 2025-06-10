# Python API dumping and comparison tool

Dumps the public API of a Python module and its members to a file, which can
then be used to show differences in the public API between two dumps, e.g. of
different versions of the same module.

## Command-line interface

```
$ py-api-dumper --help
```

* To dump the public API of a module `mymod`:

  ```
  $ py-api-dumper dump -o mymod1.dump mymod
  ```

  `mymod1.dump` will record the public API of `mymod` in a reloadable format.

* To print the API of `mymod` in text format:
  ```
  $ py-api-dumper dump mymod
  MODULE : mymod
      CLASS : myclass
          FUNCTION : __init__ : no-return-type
              REQUIRED : 0 : x : int
  ...
  ```

  The text format is a tree of entries of each nested class, class method,
  function, member variable, etc. in the public API.

* To compare the API of `mymod` between different versions:
  ```
  $ py-api-dumper diff mymod-old.dump mymod-new.dump
  --- mymod-old.dump mymod=1.0
  +++ mymod-new.dump mymod=2.0
  +MODULE : mymod
  +    CLASS : myclass
  +        FUNCTION : __init__ : no-return-type
  +            REQUIRED : 1 : b : no-type
  ```

  The above output shows the expected output if, between `mymod` versions 1.0
  and 2.0, an additional positional argument `b` had been added to the
  `__init__` method of the class `mymod.myclass`.

  ```
  $ py-api-dumper diff -o mymod.diff ...
  ```

  This will write out the API differences to `mymod.diff` in JSON format:

  * the paths to the dumps of the old and new APIs, e.g. `mymod-old.dump`
    vs. `mymod-new.dump`;
  * the version of `mymod` at the old and new API dumps, e.g. mymod `1.0`
    vs. `2.0`;
  * API entries which have been *removed*, i.e. present in the old API but not
    in the new API (e.g. none in the above example);
  * API entries which have been *added*, i.e. present in the new API but not in
    the old API (e.g. the `b` argument in the above example).

## Python interface

```python
from py_api_dumper import APIDump, APIDiff
```

* To dump the public API of a module `mymod`:
  ```python
  import mymod
  dump = APIDump.from_modules(mymod)   # OR: APIDump.from_modules("mymod")
  dump.save_to_file("mymod.dump")
  ```

* To print the API of `mymod` in text format:
  ```python
  dump.print_as_text()
  ```

* To compare the API of `mymod` between different versions:
  ```python
  diff = APIDiff.from_files("mymod-old.dump", "mymod-new.dump")
  diff.print_as_text()
  diff.save_as_json("mymod.diff")
  ```
