This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: docs/**/*.{md,markdown,mdx,rmd,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  source/
    additional_features.rst
    builtin_types.rst
    changelog.md
    cheat_sheet_py3.rst
    class_basics.rst
    command_line.rst
    common_issues.rst
    config_file.rst
    duck_type_compatibility.rst
    dynamic_typing.rst
    error_code_list.rst
    error_code_list2.rst
    error_codes.rst
    existing_code.rst
    extending_mypy.rst
    faq.rst
    final_attrs.rst
    generics.rst
    getting_started.rst
    index.rst
    inline_config.rst
    installed_packages.rst
    kinds_of_types.rst
    literal_types.rst
    metaclasses.rst
    more_types.rst
    mypy_daemon.rst
    protocols.rst
    running_mypy.rst
    runtime_troubles.rst
    stubgen.rst
    stubs.rst
    stubtest.rst
    supported_python_features.rst
    type_inference_and_annotations.rst
    type_narrowing.rst
    typed_dict.rst
  README.md
  requirements-docs.txt
```

# Files

## File: docs/source/additional_features.rst
````
Additional features
-------------------

This section discusses various features that did not fit in naturally in one
of the previous sections.

.. _dataclasses_support:

Dataclasses
***********

The :py:mod:`dataclasses` module allows defining and customizing simple
boilerplate-free classes. They can be defined using the
:py:func:`@dataclasses.dataclass <python:dataclasses.dataclass>` decorator:

.. code-block:: python

    from dataclasses import dataclass, field

    @dataclass
    class Application:
        name: str
        plugins: list[str] = field(default_factory=list)

    test = Application("Testing...")  # OK
    bad = Application("Testing...", "with plugin")  # Error: list[str] expected

Mypy will detect special methods (such as :py:meth:`__lt__ <object.__lt__>`) depending on the flags used to
define dataclasses. For example:

.. code-block:: python

    from dataclasses import dataclass

    @dataclass(order=True)
    class OrderedPoint:
        x: int
        y: int

    @dataclass(order=False)
    class UnorderedPoint:
        x: int
        y: int

    OrderedPoint(1, 2) < OrderedPoint(3, 4)  # OK
    UnorderedPoint(1, 2) < UnorderedPoint(3, 4)  # Error: Unsupported operand types

Dataclasses can be generic and can be used in any other way a normal
class can be used (Python 3.12 syntax):

.. code-block:: python

    from dataclasses import dataclass

    @dataclass
    class BoxedData[T]:
        data: T
        label: str

    def unbox[T](bd: BoxedData[T]) -> T:
        ...

    val = unbox(BoxedData(42, "<important>"))  # OK, inferred type is int

For more information see :doc:`official docs <python:library/dataclasses>`
and :pep:`557`.

Caveats/Known Issues
====================

Some functions in the :py:mod:`dataclasses` module, such as :py:func:`~dataclasses.asdict`,
have imprecise (too permissive) types. This will be fixed in future releases.

Mypy does not yet recognize aliases of :py:func:`dataclasses.dataclass <dataclasses.dataclass>`, and will
probably never recognize dynamically computed decorators. The following example
does **not** work:

.. code-block:: python

    from dataclasses import dataclass

    dataclass_alias = dataclass
    def dataclass_wrapper(cls):
      return dataclass(cls)

    @dataclass_alias
    class AliasDecorated:
      """
      Mypy doesn't recognize this as a dataclass because it is decorated by an
      alias of `dataclass` rather than by `dataclass` itself.
      """
      attribute: int

    AliasDecorated(attribute=1) # error: Unexpected keyword argument


To have Mypy recognize a wrapper of :py:func:`dataclasses.dataclass <dataclasses.dataclass>`
as a dataclass decorator, consider using the :py:func:`~typing.dataclass_transform`
decorator (example uses Python 3.12 syntax):

.. code-block:: python

    from dataclasses import dataclass, Field
    from typing import dataclass_transform

    @dataclass_transform(field_specifiers=(Field,))
    def my_dataclass[T](cls: type[T]) -> type[T]:
        ...
        return dataclass(cls)


Data Class Transforms
*********************

Mypy supports the :py:func:`~typing.dataclass_transform` decorator as described in
`PEP 681 <https://www.python.org/dev/peps/pep-0681/#the-dataclass-transform-decorator>`_.

.. note::

    Pragmatically, mypy will assume such classes have the internal attribute :code:`__dataclass_fields__`
    (even though they might lack it in runtime) and will assume functions such as :py:func:`dataclasses.is_dataclass`
    and :py:func:`dataclasses.fields` treat them as if they were dataclasses
    (even though they may fail at runtime).

.. _attrs_package:

The attrs package
*****************

:doc:`attrs <attrs:index>` is a package that lets you define
classes without writing boilerplate code. Mypy can detect uses of the
package and will generate the necessary method definitions for decorated
classes using the type annotations it finds.
Type annotations can be added as follows:

.. code-block:: python

    import attr

    @attrs.define
    class A:
        one: int
        two: int = 7
        three: int = attrs.field(8)

If you're using ``auto_attribs=False`` you must use ``attrs.field``:

.. code-block:: python

    import attrs

    @attrs.define
    class A:
        one: int = attrs.field()          # Variable annotation (Python 3.6+)
        two = attrs.field()  # type: int  # Type comment
        three = attrs.field(type=int)     # type= argument

Typeshed has a couple of "white lie" annotations to make type checking
easier. :py:func:`attrs.field` and :py:class:`attrs.Factory` actually return objects, but the
annotation says these return the types that they expect to be assigned to.
That enables this to work:

.. code-block:: python

    import attrs

    @attrs.define
    class A:
        one: int = attrs.field(8)
        two: dict[str, str] = attrs.Factory(dict)
        bad: str = attrs.field(16)   # Error: can't assign int to str

Caveats/Known Issues
====================

* The detection of attr classes and attributes works by function name only.
  This means that if you have your own helper functions that, for example,
  ``return attrs.field()`` mypy will not see them.

* All boolean arguments that mypy cares about must be literal ``True`` or ``False``.
  e.g the following will not work:

  .. code-block:: python

      import attrs
      YES = True
      @attrs.define(init=YES)
      class A:
          ...

* Currently, ``converter`` only supports named functions.  If mypy finds something else it
  will complain about not understanding the argument and the type annotation in
  :py:meth:`__init__ <object.__init__>` will be replaced by ``Any``.

* :ref:`Validator decorators <attrs:examples-validators>`
  and `default decorators <https://www.attrs.org/en/stable/examples.html#defaults>`_
  are not type-checked against the attribute they are setting/validating.

* Method definitions added by mypy currently overwrite any existing method
  definitions.

.. _remote-cache:

Using a remote cache to speed up mypy runs
******************************************

Mypy performs type checking *incrementally*, reusing results from
previous runs to speed up successive runs. If you are type checking a
large codebase, mypy can still be sometimes slower than desirable. For
example, if you create a new branch based on a much more recent commit
than the target of the previous mypy run, mypy may have to
process almost every file, as a large fraction of source files may
have changed. This can also happen after you've rebased a local
branch.

Mypy supports using a *remote cache* to improve performance in cases
such as the above.  In a large codebase, remote caching can sometimes
speed up mypy runs by a factor of 10, or more.

Mypy doesn't include all components needed to set
this up -- generally you will have to perform some simple integration
with your Continuous Integration (CI) or build system to configure
mypy to use a remote cache. This discussion assumes you have a CI
system set up for the mypy build you want to speed up, and that you
are using a central git repository. Generalizing to different
environments should not be difficult.

Here are the main components needed:

* A shared repository for storing mypy cache files for all landed commits.

* CI build that uploads mypy incremental cache files to the shared repository for
  each commit for which the CI build runs.

* A wrapper script around mypy that developers use to run mypy with remote
  caching enabled.

Below we discuss each of these components in some detail.

Shared repository for cache files
=================================

You need a repository that allows you to upload mypy cache files from
your CI build and make the cache files available for download based on
a commit id.  A simple approach would be to produce an archive of the
``.mypy_cache`` directory (which contains the mypy cache data) as a
downloadable *build artifact* from your CI build (depending on the
capabilities of your CI system).  Alternatively, you could upload the
data to a web server or to S3, for example.

Continuous Integration build
============================

The CI build would run a regular mypy build and create an archive containing
the ``.mypy_cache`` directory produced by the build. Finally, it will produce
the cache as a build artifact or upload it to a repository where it is
accessible by the mypy wrapper script.

Your CI script might work like this:

* Run mypy normally. This will generate cache data under the
  ``.mypy_cache`` directory.

* Create a tarball from the ``.mypy_cache`` directory.

* Determine the current git master branch commit id (say, using
  ``git rev-parse HEAD``).

* Upload the tarball to the shared repository with a name derived from the
  commit id.

Mypy wrapper script
===================

The wrapper script is used by developers to run mypy locally during
development instead of invoking mypy directly.  The wrapper first
populates the local ``.mypy_cache`` directory from the shared
repository and then runs a normal incremental build.

The wrapper script needs some logic to determine the most recent
central repository commit (by convention, the ``origin/master`` branch
for git) the local development branch is based on. In a typical git
setup you can do it like this:

.. code::

    git merge-base HEAD origin/master

The next step is to download the cache data (contents of the
``.mypy_cache`` directory) from the shared repository based on the
commit id of the merge base produced by the git command above. The
script will decompress the data so that mypy will start with a fresh
``.mypy_cache``. Finally, the script runs mypy normally. And that's all!

Caching with mypy daemon
========================

You can also use remote caching with the :ref:`mypy daemon <mypy_daemon>`.
The remote cache will significantly speed up the first ``dmypy check``
run after starting or restarting the daemon.

The mypy daemon requires extra fine-grained dependency data in
the cache files which aren't included by default. To use caching with
the mypy daemon, use the :option:`--cache-fine-grained <mypy --cache-fine-grained>` option in your CI
build::

    $ mypy --cache-fine-grained <args...>

This flag adds extra information for the daemon to the cache. In
order to use this extra information, you will also need to use the
``--use-fine-grained-cache`` option with ``dmypy start`` or
``dmypy restart``. Example::

    $ dmypy start -- --use-fine-grained-cache <options...>

Now your first ``dmypy check`` run should be much faster, as it can use
cache information to avoid processing the whole program.

Refinements
===========

There are several optional refinements that may improve things further,
at least if your codebase is hundreds of thousands of lines or more:

* If the wrapper script determines that the merge base hasn't changed
  from a previous run, there's no need to download the cache data and
  it's better to instead reuse the existing local cache data.

* If you use the mypy daemon, you may want to restart the daemon each time
  after the merge base or local branch has changed to avoid processing a
  potentially large number of changes in an incremental build, as this can
  be much slower than downloading cache data and restarting the daemon.

* If the current local branch is based on a very recent master commit,
  the remote cache data may not yet be available for that commit, as
  there will necessarily be some latency to build the cache files. It
  may be a good idea to look for cache data for, say, the 5 latest
  master commits and use the most recent data that is available.

* If the remote cache is not accessible for some reason (say, from a public
  network), the script can still fall back to a normal incremental build.

* You can have multiple local cache directories for different local branches
  using the :option:`--cache-dir <mypy --cache-dir>` option. If the user switches to an existing
  branch where downloaded cache data is already available, you can continue
  to use the existing cache data instead of redownloading the data.

* You can set up your CI build to use a remote cache to speed up the
  CI build. This would be particularly useful if each CI build starts
  from a fresh state without access to cache files from previous
  builds. It's still recommended to run a full, non-incremental
  mypy build to create the cache data, as repeatedly updating cache
  data incrementally could result in drift over a long time period (due
  to a mypy caching issue, perhaps).

.. _extended_callable:

Extended Callable types
***********************

.. note::

   This feature is deprecated.  You can use
   :ref:`callback protocols <callback_protocols>` as a replacement.

As an experimental mypy extension, you can specify :py:class:`~collections.abc.Callable` types
that support keyword arguments, optional arguments, and more.  When
you specify the arguments of a :py:class:`~collections.abc.Callable`, you can choose to supply just
the type of a nameless positional argument, or an "argument specifier"
representing a more complicated form of argument.  This allows one to
more closely emulate the full range of possibilities given by the
``def`` statement in Python.

As an example, here's a complicated function definition and the
corresponding :py:class:`~collections.abc.Callable`:

.. code-block:: python

   from collections.abc import Callable
   from mypy_extensions import (Arg, DefaultArg, NamedArg,
                                DefaultNamedArg, VarArg, KwArg)

   def func(__a: int,  # This convention is for nameless arguments
            b: int,
            c: int = 0,
            *args: int,
            d: int,
            e: int = 0,
            **kwargs: int) -> int:
       ...

   F = Callable[[int,  # Or Arg(int)
                 Arg(int, 'b'),
                 DefaultArg(int, 'c'),
                 VarArg(int),
                 NamedArg(int, 'd'),
                 DefaultNamedArg(int, 'e'),
                 KwArg(int)],
                int]

   f: F = func

Argument specifiers are special function calls that can specify the
following aspects of an argument:

- its type (the only thing that the basic format supports)

- its name (if it has one)

- whether it may be omitted

- whether it may or must be passed using a keyword

- whether it is a ``*args`` argument (representing the remaining
  positional arguments)

- whether it is a ``**kwargs`` argument (representing the remaining
  keyword arguments)

The following functions are available in ``mypy_extensions`` for this
purpose:

.. code-block:: python

   def Arg(type=Any, name=None):
       # A normal, mandatory, positional argument.
       # If the name is specified it may be passed as a keyword.

   def DefaultArg(type=Any, name=None):
       # An optional positional argument (i.e. with a default value).
       # If the name is specified it may be passed as a keyword.

   def NamedArg(type=Any, name=None):
       # A mandatory keyword-only argument.

   def DefaultNamedArg(type=Any, name=None):
       # An optional keyword-only argument (i.e. with a default value).

   def VarArg(type=Any):
       # A *args-style variadic positional argument.
       # A single VarArg() specifier represents all remaining
       # positional arguments.

   def KwArg(type=Any):
       # A **kwargs-style variadic keyword argument.
       # A single KwArg() specifier represents all remaining
       # keyword arguments.

In all cases, the ``type`` argument defaults to ``Any``, and if the
``name`` argument is omitted the argument has no name (the name is
required for ``NamedArg`` and ``DefaultNamedArg``).  A basic
:py:class:`~collections.abc.Callable` such as

.. code-block:: python

   MyFunc = Callable[[int, str, int], float]

is equivalent to the following:

.. code-block:: python

   MyFunc = Callable[[Arg(int), Arg(str), Arg(int)], float]

A :py:class:`~collections.abc.Callable` with unspecified argument types, such as

.. code-block:: python

   MyOtherFunc = Callable[..., int]

is (roughly) equivalent to

.. code-block:: python

   MyOtherFunc = Callable[[VarArg(), KwArg()], int]

.. note::

   Each of the functions above currently just returns its ``type``
   argument at runtime, so the information contained in the argument
   specifiers is not available at runtime.  This limitation is
   necessary for backwards compatibility with the existing
   ``typing.py`` module as present in the Python 3.5+ standard library
   and distributed via PyPI.
````

## File: docs/source/builtin_types.rst
````
Built-in types
==============

This chapter introduces some commonly used built-in types. We will
cover many other kinds of types later.

Simple types
............

Here are examples of some common built-in types:

====================== ===============================
Type                   Description
====================== ===============================
``int``                integer
``float``              floating point number
``bool``               boolean value (subclass of ``int``)
``str``                text, sequence of unicode codepoints
``bytes``              8-bit string, sequence of byte values
``object``             an arbitrary object (``object`` is the common base class)
====================== ===============================

All built-in classes can be used as types.

Any type
........

If you can't find a good type for some value, you can always fall back
to ``Any``:

====================== ===============================
Type                   Description
====================== ===============================
``Any``                dynamically typed value with an arbitrary type
====================== ===============================

The type ``Any`` is defined in the :py:mod:`typing` module.
See :ref:`dynamic-typing` for more details.

Generic types
.............

In Python 3.9 and later, built-in collection type objects support
indexing:

====================== ===============================
Type                   Description
====================== ===============================
``list[str]``          list of ``str`` objects
``tuple[int, int]``    tuple of two ``int`` objects (``tuple[()]`` is the empty tuple)
``tuple[int, ...]``    tuple of an arbitrary number of ``int`` objects
``dict[str, int]``     dictionary from ``str`` keys to ``int`` values
``Iterable[int]``      iterable object containing ints
``Sequence[bool]``     sequence of booleans (read-only)
``Mapping[str, int]``  mapping from ``str`` keys to ``int`` values (read-only)
``type[C]``            type object of ``C`` (``C`` is a class/type variable/union of types)
====================== ===============================

The type ``dict`` is a *generic* class, signified by type arguments within
``[...]``. For example, ``dict[int, str]`` is a dictionary from integers to
strings and ``dict[Any, Any]`` is a dictionary of dynamically typed
(arbitrary) values and keys. ``list`` is another generic class.

``Iterable``, ``Sequence``, and ``Mapping`` are generic types that correspond to
Python protocols. For example, a ``str`` object or a ``list[str]`` object is
valid when ``Iterable[str]`` or ``Sequence[str]`` is expected.
You can import them from :py:mod:`collections.abc` instead of importing from
:py:mod:`typing` in Python 3.9.

See :ref:`generic-builtins` for more details, including how you can
use these in annotations also in Python 3.7 and 3.8.

These legacy types defined in :py:mod:`typing` are needed if you need to support
Python 3.8 and earlier:

====================== ===============================
Type                   Description
====================== ===============================
``List[str]``          list of ``str`` objects
``Tuple[int, int]``    tuple of two ``int`` objects (``Tuple[()]`` is the empty tuple)
``Tuple[int, ...]``    tuple of an arbitrary number of ``int`` objects
``Dict[str, int]``     dictionary from ``str`` keys to ``int`` values
``Iterable[int]``      iterable object containing ints
``Sequence[bool]``     sequence of booleans (read-only)
``Mapping[str, int]``  mapping from ``str`` keys to ``int`` values (read-only)
``Type[C]``            type object of ``C`` (``C`` is a class/type variable/union of types)
====================== ===============================

``List`` is an alias for the built-in type ``list`` that supports
indexing (and similarly for ``dict``/``Dict`` and
``tuple``/``Tuple``).

Note that even though ``Iterable``, ``Sequence`` and ``Mapping`` look
similar to abstract base classes defined in :py:mod:`collections.abc`
(formerly ``collections``), they are not identical, since the latter
don't support indexing prior to Python 3.9.
````

## File: docs/source/changelog.md
````markdown
<!-- This file includes mypy/CHANGELOG.md into mypy documentation -->
```{include} ../../CHANGELOG.md
```
````

## File: docs/source/cheat_sheet_py3.rst
````
.. _cheat-sheet-py3:

Type hints cheat sheet
======================

This document is a quick cheat sheet showing how to use type
annotations for various common types in Python.

Variables
*********

Technically many of the type annotations shown below are redundant,
since mypy can usually infer the type of a variable from its value.
See :ref:`type-inference-and-annotations` for more details.

.. code-block:: python

   # This is how you declare the type of a variable
   age: int = 1

   # You don't need to initialize a variable to annotate it
   a: int  # Ok (no value at runtime until assigned)

   # Doing so can be useful in conditional branches
   child: bool
   if age < 18:
       child = True
   else:
       child = False


Useful built-in types
*********************

.. code-block:: python

   # For most types, just use the name of the type in the annotation
   # Note that mypy can usually infer the type of a variable from its value,
   # so technically these annotations are redundant
   x: int = 1
   x: float = 1.0
   x: bool = True
   x: str = "test"
   x: bytes = b"test"

   # For collections on Python 3.9+, the type of the collection item is in brackets
   x: list[int] = [1]
   x: set[int] = {6, 7}

   # For mappings, we need the types of both keys and values
   x: dict[str, float] = {"field": 2.0}  # Python 3.9+

   # For tuples of fixed size, we specify the types of all the elements
   x: tuple[int, str, float] = (3, "yes", 7.5)  # Python 3.9+

   # For tuples of variable size, we use one type and ellipsis
   x: tuple[int, ...] = (1, 2, 3)  # Python 3.9+

   # On Python 3.8 and earlier, the name of the collection type is
   # capitalized, and the type is imported from the 'typing' module
   from typing import List, Set, Dict, Tuple
   x: List[int] = [1]
   x: Set[int] = {6, 7}
   x: Dict[str, float] = {"field": 2.0}
   x: Tuple[int, str, float] = (3, "yes", 7.5)
   x: Tuple[int, ...] = (1, 2, 3)

   from typing import Union, Optional

   # On Python 3.10+, use the | operator when something could be one of a few types
   x: list[int | str] = [3, 5, "test", "fun"]  # Python 3.10+
   # On earlier versions, use Union
   x: list[Union[int, str]] = [3, 5, "test", "fun"]

   # Use X | None for a value that could be None on Python 3.10+
   # Use Optional[X] on 3.9 and earlier; Optional[X] is the same as 'X | None'
   x: str | None = "something" if some_condition() else None
   if x is not None:
       # Mypy understands x won't be None here because of the if-statement
       print(x.upper())
   # If you know a value can never be None due to some logic that mypy doesn't
   # understand, use an assert
   assert x is not None
   print(x.upper())

Functions
*********

.. code-block:: python

   from collections.abc import Iterator, Callable
   from typing import Union, Optional

   # This is how you annotate a function definition
   def stringify(num: int) -> str:
       return str(num)

   # And here's how you specify multiple arguments
   def plus(num1: int, num2: int) -> int:
       return num1 + num2

   # If a function does not return a value, use None as the return type
   # Default value for an argument goes after the type annotation
   def show(value: str, excitement: int = 10) -> None:
       print(value + "!" * excitement)

   # Note that arguments without a type are dynamically typed (treated as Any)
   # and that functions without any annotations are not checked
   def untyped(x):
       x.anything() + 1 + "string"  # no errors

   # This is how you annotate a callable (function) value
   x: Callable[[int, float], float] = f
   def register(callback: Callable[[str], int]) -> None: ...

   # A generator function that yields ints is secretly just a function that
   # returns an iterator of ints, so that's how we annotate it
   def gen(n: int) -> Iterator[int]:
       i = 0
       while i < n:
           yield i
           i += 1

   # You can of course split a function annotation over multiple lines
   def send_email(
       address: str | list[str],
       sender: str,
       cc: list[str] | None,
       bcc: list[str] | None,
       subject: str = '',
       body: list[str] | None = None,
   ) -> bool:
       ...

   # Mypy understands positional-only and keyword-only arguments
   # Positional-only arguments can also be marked by using a name starting with
   # two underscores
   def quux(x: int, /, *, y: int) -> None:
       pass

   quux(3, y=5)  # Ok
   quux(3, 5)  # error: Too many positional arguments for "quux"
   quux(x=3, y=5)  # error: Unexpected keyword argument "x" for "quux"

   # This says each positional arg and each keyword arg is a "str"
   def call(self, *args: str, **kwargs: str) -> str:
       reveal_type(args)  # Revealed type is "tuple[str, ...]"
       reveal_type(kwargs)  # Revealed type is "dict[str, str]"
       request = make_request(*args, **kwargs)
       return self.do_api_query(request)

Classes
*******

.. code-block:: python

   from typing import ClassVar

   class BankAccount:
       # The "__init__" method doesn't return anything, so it gets return
       # type "None" just like any other method that doesn't return anything
       def __init__(self, account_name: str, initial_balance: int = 0) -> None:
           # mypy will infer the correct types for these instance variables
           # based on the types of the parameters.
           self.account_name = account_name
           self.balance = initial_balance

       # For instance methods, omit type for "self"
       def deposit(self, amount: int) -> None:
           self.balance += amount

       def withdraw(self, amount: int) -> None:
           self.balance -= amount

   # User-defined classes are valid as types in annotations
   account: BankAccount = BankAccount("Alice", 400)
   def transfer(src: BankAccount, dst: BankAccount, amount: int) -> None:
       src.withdraw(amount)
       dst.deposit(amount)

   # Functions that accept BankAccount also accept any subclass of BankAccount!
   class AuditedBankAccount(BankAccount):
       # You can optionally declare instance variables in the class body
       audit_log: list[str]

       def __init__(self, account_name: str, initial_balance: int = 0) -> None:
           super().__init__(account_name, initial_balance)
           self.audit_log: list[str] = []

       def deposit(self, amount: int) -> None:
           self.audit_log.append(f"Deposited {amount}")
           self.balance += amount

       def withdraw(self, amount: int) -> None:
           self.audit_log.append(f"Withdrew {amount}")
           self.balance -= amount

   audited = AuditedBankAccount("Bob", 300)
   transfer(audited, account, 100)  # type checks!

   # You can use the ClassVar annotation to declare a class variable
   class Car:
       seats: ClassVar[int] = 4
       passengers: ClassVar[list[str]]

   # If you want dynamic attributes on your class, have it
   # override "__setattr__" or "__getattr__"
   class A:
       # This will allow assignment to any A.x, if x is the same type as "value"
       # (use "value: Any" to allow arbitrary types)
       def __setattr__(self, name: str, value: int) -> None: ...

       # This will allow access to any A.x, if x is compatible with the return type
       def __getattr__(self, name: str) -> int: ...

   a = A()
   a.foo = 42  # Works
   a.bar = 'Ex-parrot'  # Fails type checking

When you're puzzled or when things are complicated
**************************************************

.. code-block:: python

   from typing import Union, Any, Optional, TYPE_CHECKING, cast

   # To find out what type mypy infers for an expression anywhere in
   # your program, wrap it in reveal_type().  Mypy will print an error
   # message with the type; remove it again before running the code.
   reveal_type(1)  # Revealed type is "builtins.int"

   # If you initialize a variable with an empty container or "None"
   # you may have to help mypy a bit by providing an explicit type annotation
   x: list[str] = []
   x: str | None = None

   # Use Any if you don't know the type of something or it's too
   # dynamic to write a type for
   x: Any = mystery_function()
   # Mypy will let you do anything with x!
   x.whatever() * x["you"] + x("want") - any(x) and all(x) is super  # no errors

   # Use a "type: ignore" comment to suppress errors on a given line,
   # when your code confuses mypy or runs into an outright bug in mypy.
   # Good practice is to add a comment explaining the issue.
   x = confusing_function()  # type: ignore  # confusing_function won't return None here because ...

   # "cast" is a helper function that lets you override the inferred
   # type of an expression. It's only for mypy -- there's no runtime check.
   a = [4]
   b = cast(list[int], a)  # Passes fine
   c = cast(list[str], a)  # Passes fine despite being a lie (no runtime check)
   reveal_type(c)  # Revealed type is "builtins.list[builtins.str]"
   print(c)  # Still prints [4] ... the object is not changed or casted at runtime

   # Use "TYPE_CHECKING" if you want to have code that mypy can see but will not
   # be executed at runtime (or to have code that mypy can't see)
   if TYPE_CHECKING:
       import json
   else:
       import orjson as json  # mypy is unaware of this

In some cases type annotations can cause issues at runtime, see
:ref:`runtime_troubles` for dealing with this.

See :ref:`silencing-type-errors` for details on how to silence errors.

Standard "duck types"
*********************

In typical Python code, many functions that can take a list or a dict
as an argument only need their argument to be somehow "list-like" or
"dict-like".  A specific meaning of "list-like" or "dict-like" (or
something-else-like) is called a "duck type", and several duck types
that are common in idiomatic Python are standardized.

.. code-block:: python

   from collections.abc import Mapping, MutableMapping, Sequence, Iterable
   # or 'from typing import ...' (required in Python 3.8)

   # Use Iterable for generic iterables (anything usable in "for"),
   # and Sequence where a sequence (supporting "len" and "__getitem__") is
   # required
   def f(ints: Iterable[int]) -> list[str]:
       return [str(x) for x in ints]

   f(range(1, 3))

   # Mapping describes a dict-like object (with "__getitem__") that we won't
   # mutate, and MutableMapping one (with "__setitem__") that we might
   def f(my_mapping: Mapping[int, str]) -> list[int]:
       my_mapping[5] = 'maybe'  # mypy will complain about this line...
       return list(my_mapping.keys())

   f({3: 'yes', 4: 'no'})

   def f(my_mapping: MutableMapping[int, str]) -> set[str]:
       my_mapping[5] = 'maybe'  # ...but mypy is OK with this.
       return set(my_mapping.values())

   f({3: 'yes', 4: 'no'})

   import sys
   from typing import IO

   # Use IO[str] or IO[bytes] for functions that should accept or return
   # objects that come from an open() call (note that IO does not
   # distinguish between reading, writing or other modes)
   def get_sys_IO(mode: str = 'w') -> IO[str]:
       if mode == 'w':
           return sys.stdout
       elif mode == 'r':
           return sys.stdin
       else:
           return sys.stdout


You can even make your own duck types using :ref:`protocol-types`.

Forward references
******************

.. code-block:: python

   # You may want to reference a class before it is defined.
   # This is known as a "forward reference".
   def f(foo: A) -> int:  # This will fail at runtime with 'A' is not defined
       ...

   # However, if you add the following special import:
   from __future__ import annotations
   # It will work at runtime and type checking will succeed as long as there
   # is a class of that name later on in the file
   def f(foo: A) -> int:  # Ok
       ...

   # Another option is to just put the type in quotes
   def f(foo: 'A') -> int:  # Also ok
       ...

   class A:
       # This can also come up if you need to reference a class in a type
       # annotation inside the definition of that class
       @classmethod
       def create(cls) -> A:
           ...

See :ref:`forward-references` for more details.

Decorators
**********

Decorator functions can be expressed via generics. See
:ref:`declaring-decorators` for more details. Example using Python 3.12
syntax:

.. code-block:: python

    from collections.abc import Callable
    from typing import Any

    def bare_decorator[F: Callable[..., Any]](func: F) -> F:
        ...

    def decorator_args[F: Callable[..., Any]](url: str) -> Callable[[F], F]:
        ...

The same example using pre-3.12 syntax:

.. code-block:: python

    from collections.abc import Callable
    from typing import Any, TypeVar

    F = TypeVar('F', bound=Callable[..., Any])

    def bare_decorator(func: F) -> F:
        ...

    def decorator_args(url: str) -> Callable[[F], F]:
        ...

Coroutines and asyncio
**********************

See :ref:`async-and-await` for the full detail on typing coroutines and asynchronous code.

.. code-block:: python

   import asyncio

   # A coroutine is typed like a normal function
   async def countdown(tag: str, count: int) -> str:
       while count > 0:
           print(f'T-minus {count} ({tag})')
           await asyncio.sleep(0.1)
           count -= 1
       return "Blastoff!"
````

## File: docs/source/class_basics.rst
````
.. _class-basics:

Class basics
============

This section will help get you started annotating your
classes. Built-in classes such as ``int`` also follow these same
rules.

Instance and class attributes
*****************************

The mypy type checker detects if you are trying to access a missing
attribute, which is a very common programming error. For this to work
correctly, instance and class attributes must be defined or
initialized within the class. Mypy infers the types of attributes:

.. code-block:: python

   class A:
       def __init__(self, x: int) -> None:
           self.x = x  # Aha, attribute 'x' of type 'int'

   a = A(1)
   a.x = 2  # OK!
   a.y = 3  # Error: "A" has no attribute "y"

This is a bit like each class having an implicitly defined
:py:data:`__slots__ <object.__slots__>` attribute. This is only enforced during type
checking and not when your program is running.

You can declare types of variables in the class body explicitly using
a type annotation:

.. code-block:: python

   class A:
       x: list[int]  # Declare attribute 'x' of type list[int]

   a = A()
   a.x = [1]     # OK

As in Python generally, a variable defined in the class body can be used
as a class or an instance variable. (As discussed in the next section, you
can override this with a :py:data:`~typing.ClassVar` annotation.)

Similarly, you can give explicit types to instance variables defined
in a method:

.. code-block:: python

   class A:
       def __init__(self) -> None:
           self.x: list[int] = []

       def f(self) -> None:
           self.y: Any = 0

You can only define an instance variable within a method if you assign
to it explicitly using ``self``:

.. code-block:: python

   class A:
       def __init__(self) -> None:
           self.y = 1   # Define 'y'
           a = self
           a.x = 1      # Error: 'x' not defined

Annotating __init__ methods
***************************

The :py:meth:`__init__ <object.__init__>` method is somewhat special -- it doesn't return a
value.  This is best expressed as ``-> None``.  However, since many feel
this is redundant, it is allowed to omit the return type declaration
on :py:meth:`__init__ <object.__init__>` methods **if at least one argument is annotated**.  For
example, in the following classes :py:meth:`__init__ <object.__init__>` is considered fully
annotated:

.. code-block:: python

   class C1:
       def __init__(self) -> None:
           self.var = 42

   class C2:
       def __init__(self, arg: int):
           self.var = arg

However, if :py:meth:`__init__ <object.__init__>` has no annotated arguments and no return type
annotation, it is considered an untyped method:

.. code-block:: python

   class C3:
       def __init__(self):
           # This body is not type checked
           self.var = 42 + 'abc'

Class attribute annotations
***************************

You can use a :py:data:`ClassVar[t] <typing.ClassVar>` annotation to explicitly declare that a
particular attribute should not be set on instances:

.. code-block:: python

  from typing import ClassVar

  class A:
      x: ClassVar[int] = 0  # Class variable only

  A.x += 1  # OK

  a = A()
  a.x = 1  # Error: Cannot assign to class variable "x" via instance
  print(a.x)  # OK -- can be read through an instance

It's not necessary to annotate all class variables using
:py:data:`~typing.ClassVar`. An attribute without the :py:data:`~typing.ClassVar` annotation can
still be used as a class variable. However, mypy won't prevent it from
being used as an instance variable, as discussed previously:

.. code-block:: python

  class A:
      x = 0  # Can be used as a class or instance variable

  A.x += 1  # OK

  a = A()
  a.x = 1  # Also OK

Note that :py:data:`~typing.ClassVar` is not a class, and you can't use it with
:py:func:`isinstance` or :py:func:`issubclass`. It does not change Python
runtime behavior -- it's only for type checkers such as mypy (and
also helpful for human readers).

You can also omit the square brackets and the variable type in
a :py:data:`~typing.ClassVar` annotation, but this might not do what you'd expect:

.. code-block:: python

   class A:
       y: ClassVar = 0  # Type implicitly Any!

In this case the type of the attribute will be implicitly ``Any``.
This behavior will change in the future, since it's surprising.

An explicit :py:data:`~typing.ClassVar` may be particularly handy to distinguish
between class and instance variables with callable types. For example:

.. code-block:: python

   from collections.abc import Callable
   from typing import ClassVar

   class A:
       foo: Callable[[int], None]
       bar: ClassVar[Callable[[A, int], None]]
       bad: Callable[[A], None]

   A().foo(42)  # OK
   A().bar(42)  # OK
   A().bad()  # Error: Too few arguments

.. note::
   A :py:data:`~typing.ClassVar` type parameter cannot include type variables:
   ``ClassVar[T]`` and ``ClassVar[list[T]]``
   are both invalid if ``T`` is a type variable (see :ref:`generic-classes`
   for more about type variables).

Overriding statically typed methods
***********************************

When overriding a statically typed method, mypy checks that the
override has a compatible signature:

.. code-block:: python

   class Base:
       def f(self, x: int) -> None:
           ...

   class Derived1(Base):
       def f(self, x: str) -> None:   # Error: type of 'x' incompatible
           ...

   class Derived2(Base):
       def f(self, x: int, y: int) -> None:  # Error: too many arguments
           ...

   class Derived3(Base):
       def f(self, x: int) -> None:   # OK
           ...

   class Derived4(Base):
       def f(self, x: float) -> None:   # OK: mypy treats int as a subtype of float
           ...

   class Derived5(Base):
       def f(self, x: int, y: int = 0) -> None:   # OK: accepts more than the base
           ...                                    #     class method

.. note::

   You can also vary return types **covariantly** in overriding. For
   example, you could override the return type ``Iterable[int]`` with a
   subtype such as ``list[int]``. Similarly, you can vary argument types
   **contravariantly** -- subclasses can have more general argument types.

In order to ensure that your code remains correct when renaming methods,
it can be helpful to explicitly mark a method as overriding a base
method. This can be done with the ``@override`` decorator. ``@override``
can be imported from ``typing`` starting with Python 3.12 or from
``typing_extensions`` for use with older Python versions. If the base
method is then renamed while the overriding method is not, mypy will
show an error:

.. code-block:: python

   from typing import override

   class Base:
       def f(self, x: int) -> None:
           ...
       def g_renamed(self, y: str) -> None:
           ...

   class Derived1(Base):
       @override
       def f(self, x: int) -> None:   # OK
           ...

       @override
       def g(self, y: str) -> None:   # Error: no corresponding base method found
           ...

.. note::

   Use :ref:`--enable-error-code explicit-override <code-explicit-override>` to require
   that method overrides use the ``@override`` decorator. Emit an error if it is missing.

You can also override a statically typed method with a dynamically
typed one. This allows dynamically typed code to override methods
defined in library classes without worrying about their type
signatures.

As always, relying on dynamically typed code can be unsafe. There is no
runtime enforcement that the method override returns a value that is
compatible with the original return type, since annotations have no
effect at runtime:

.. code-block:: python

   class Base:
       def inc(self, x: int) -> int:
           return x + 1

   class Derived(Base):
       def inc(self, x):   # Override, dynamically typed
           return 'hello'  # Incompatible with 'Base', but no mypy error

Abstract base classes and multiple inheritance
**********************************************

Mypy supports Python :doc:`abstract base classes <python:library/abc>` (ABCs). Abstract classes
have at least one abstract method or property that must be implemented
by any *concrete* (non-abstract) subclass. You can define abstract base
classes using the :py:class:`abc.ABCMeta` metaclass and the :py:func:`@abc.abstractmethod <abc.abstractmethod>`
function decorator. Example:

.. code-block:: python

   from abc import ABCMeta, abstractmethod

   class Animal(metaclass=ABCMeta):
       @abstractmethod
       def eat(self, food: str) -> None: pass

       @property
       @abstractmethod
       def can_walk(self) -> bool: pass

   class Cat(Animal):
       def eat(self, food: str) -> None:
           ...  # Body omitted

       @property
       def can_walk(self) -> bool:
           return True

   x = Animal()  # Error: 'Animal' is abstract due to 'eat' and 'can_walk'
   y = Cat()     # OK

Note that mypy performs checking for unimplemented abstract methods
even if you omit the :py:class:`~abc.ABCMeta` metaclass. This can be useful if the
metaclass would cause runtime metaclass conflicts.

Since you can't create instances of ABCs, they are most commonly used in
type annotations. For example, this method accepts arbitrary iterables
containing arbitrary animals (instances of concrete ``Animal``
subclasses):

.. code-block:: python

   def feed_all(animals: Iterable[Animal], food: str) -> None:
       for animal in animals:
           animal.eat(food)

There is one important peculiarity about how ABCs work in Python --
whether a particular class is abstract or not is somewhat implicit.
In the example below, ``Derived`` is treated as an abstract base class
since ``Derived`` inherits an abstract ``f`` method from ``Base`` and
doesn't explicitly implement it. The definition of ``Derived``
generates no errors from mypy, since it's a valid ABC:

.. code-block:: python

   from abc import ABCMeta, abstractmethod

   class Base(metaclass=ABCMeta):
       @abstractmethod
       def f(self, x: int) -> None: pass

   class Derived(Base):  # No error -- Derived is implicitly abstract
       def g(self) -> None:
           ...

Attempting to create an instance of ``Derived`` will be rejected,
however:

.. code-block:: python

   d = Derived()  # Error: 'Derived' is abstract

.. note::

   It's a common error to forget to implement an abstract method.
   As shown above, the class definition will not generate an error
   in this case, but any attempt to construct an instance will be
   flagged as an error.

Mypy allows you to omit the body for an abstract method, but if you do so,
it is unsafe to call such method via ``super()``. For example:

.. code-block:: python

   from abc import abstractmethod
   class Base:
       @abstractmethod
       def foo(self) -> int: pass
       @abstractmethod
       def bar(self) -> int:
           return 0
   class Sub(Base):
       def foo(self) -> int:
           return super().foo() + 1  # error: Call to abstract method "foo" of "Base"
                                     # with trivial body via super() is unsafe
       @abstractmethod
       def bar(self) -> int:
           return super().bar() + 1  # This is OK however.

A class can inherit any number of classes, both abstract and
concrete. As with normal overrides, a dynamically typed method can
override or implement a statically typed method defined in any base
class, including an abstract method defined in an abstract base class.

You can implement an abstract property using either a normal
property or an instance variable.

Slots
*****

When a class has explicitly defined :std:term:`__slots__`,
mypy will check that all attributes assigned to are members of ``__slots__``:

.. code-block:: python

  class Album:
      __slots__ = ('name', 'year')

      def __init__(self, name: str, year: int) -> None:
         self.name = name
         self.year = year
         # Error: Trying to assign name "released" that is not in "__slots__" of type "Album"
         self.released = True

  my_album = Album('Songs about Python', 2021)

Mypy will only check attribute assignments against ``__slots__`` when
the following conditions hold:

1. All base classes (except builtin ones) must have explicit
   ``__slots__`` defined (this mirrors Python semantics).

2. ``__slots__`` does not include ``__dict__``. If ``__slots__``
   includes ``__dict__``, arbitrary attributes can be set, similar to
   when ``__slots__`` is not defined (this mirrors Python semantics).

3. All values in ``__slots__`` must be string literals.
````

## File: docs/source/command_line.rst
````
.. _command-line:

.. program:: mypy

The mypy command line
=====================

This section documents mypy's command line interface. You can view
a quick summary of the available flags by running :option:`mypy --help`.

.. note::

   Command line flags are liable to change between releases.


Specifying what to type check
*****************************

By default, you can specify what code you want mypy to type check
by passing in the paths to what you want to have type checked::

    $ mypy foo.py bar.py some_directory

Note that directories are checked recursively.

Mypy also lets you specify what code to type check in several other
ways. A short summary of the relevant flags is included below:
for full details, see :ref:`running-mypy`.

.. option:: -m MODULE, --module MODULE

    Asks mypy to type check the provided module. This flag may be
    repeated multiple times.

    Mypy *will not* recursively type check any submodules of the provided
    module.

.. option:: -p PACKAGE, --package PACKAGE

    Asks mypy to type check the provided package. This flag may be
    repeated multiple times.

    Mypy *will* recursively type check any submodules of the provided
    package. This flag is identical to :option:`--module` apart from this
    behavior.

.. option:: -c PROGRAM_TEXT, --command PROGRAM_TEXT

    Asks mypy to type check the provided string as a program.


.. option:: --exclude

    A regular expression that matches file names, directory names and paths
    which mypy should ignore while recursively discovering files to check.
    Use forward slashes on all platforms.

    For instance, to avoid discovering any files named `setup.py` you could
    pass ``--exclude '/setup\.py$'``. Similarly, you can ignore discovering
    directories with a given name by e.g. ``--exclude /build/`` or
    those matching a subpath with ``--exclude /project/vendor/``. To ignore
    multiple files / directories / paths, you can provide the --exclude
    flag more than once, e.g ``--exclude '/setup\.py$' --exclude '/build/'``.

    Note that this flag only affects recursive directory tree discovery, that
    is, when mypy is discovering files within a directory tree or submodules of
    a package to check. If you pass a file or module explicitly it will still be
    checked. For instance, ``mypy --exclude '/setup.py$'
    but_still_check/setup.py``.

    In particular, ``--exclude`` does not affect mypy's discovery of files
    via :ref:`import following <follow-imports>`. You can use a per-module
    :confval:`ignore_errors` config option to silence errors from a given module,
    or a per-module :confval:`follow_imports` config option to additionally avoid
    mypy from following imports and checking code you do not wish to be checked.

    Note that mypy will never recursively discover files and directories named
    "site-packages", "node_modules" or "__pycache__", or those whose name starts
    with a period, exactly as ``--exclude
    '/(site-packages|node_modules|__pycache__|\..*)/$'`` would. Mypy will also
    never recursively discover files with extensions other than ``.py`` or
    ``.pyi``.

.. option:: --exclude-gitignore

    This flag will add everything that matches ``.gitignore`` file(s) to :option:`--exclude`.


Optional arguments
******************

.. option:: -h, --help

    Show help message and exit.

.. option:: -v, --verbose

    More verbose messages.

.. option:: -V, --version

    Show program's version number and exit.

.. option:: -O FORMAT, --output FORMAT {json}

    Set a custom output format.

.. _config-file-flag:

Config file
***********

.. option:: --config-file CONFIG_FILE

    This flag makes mypy read configuration settings from the given file.

    By default settings are read from ``mypy.ini``, ``.mypy.ini``, ``pyproject.toml``, or ``setup.cfg``
    in the current directory. Settings override mypy's built-in defaults and
    command line flags can override settings.

    Specifying :option:`--config-file= <--config-file>` (with no filename) will ignore *all*
    config files.

    See :ref:`config-file` for the syntax of configuration files.

.. option:: --warn-unused-configs

    This flag makes mypy warn about unused ``[mypy-<pattern>]`` config
    file sections.
    (This requires turning off incremental mode using :option:`--no-incremental`.)


.. _import-discovery:

Import discovery
****************

The following flags customize how exactly mypy discovers and follows
imports.

.. option:: --explicit-package-bases

    This flag tells mypy that top-level packages will be based in either the
    current directory, or a member of the ``MYPYPATH`` environment variable or
    :confval:`mypy_path` config option. This option is only useful
    in the absence of `__init__.py`. See :ref:`Mapping file
    paths to modules <mapping-paths-to-modules>` for details.

.. option:: --ignore-missing-imports

    This flag makes mypy ignore all missing imports. It is equivalent
    to adding ``# type: ignore`` comments to all unresolved imports
    within your codebase.

    Note that this flag does *not* suppress errors about missing names
    in successfully resolved modules. For example, if one has the
    following files::

        package/__init__.py
        package/mod.py

    Then mypy will generate the following errors with :option:`--ignore-missing-imports`:

    .. code-block:: python

        import package.unknown      # No error, ignored
        x = package.unknown.func()  # OK. 'func' is assumed to be of type 'Any'

        from package import unknown          # No error, ignored
        from package.mod import NonExisting  # Error: Module has no attribute 'NonExisting'

    For more details, see :ref:`ignore-missing-imports`.

.. option:: --follow-untyped-imports

    This flag makes mypy analyze imports from installed packages even if
    missing a :ref:`py.typed marker or stubs <installed-packages>`.

    .. warning::

        Note that analyzing all unannotated modules might result in issues
        when analyzing code not designed to be type checked and may significantly
        increase how long mypy takes to run.

.. option:: --follow-imports {normal,silent,skip,error}

    This flag adjusts how mypy follows imported modules that were not
    explicitly passed in via the command line.

    The default option is ``normal``: mypy will follow and type check
    all modules. For more information on what the other options do,
    see :ref:`Following imports <follow-imports>`.

.. option:: --python-executable EXECUTABLE

    This flag will have mypy collect type information from :pep:`561`
    compliant packages installed for the Python executable ``EXECUTABLE``.
    If not provided, mypy will use PEP 561 compliant packages installed for
    the Python executable running mypy.

    See :ref:`installed-packages` for more on making PEP 561 compliant packages.

.. option:: --no-site-packages

    This flag will disable searching for :pep:`561` compliant packages. This
    will also disable searching for a usable Python executable.

    Use this  flag if mypy cannot find a Python executable for the version of
    Python being checked, and you don't need to use PEP 561 typed packages.
    Otherwise, use :option:`--python-executable`.

.. option:: --no-silence-site-packages

    By default, mypy will suppress any error messages generated within :pep:`561`
    compliant packages. Adding this flag will disable this behavior.

.. option:: --fast-module-lookup

    The default logic used to scan through search paths to resolve imports has a
    quadratic worse-case behavior in some cases, which is for instance triggered
    by a large number of folders sharing a top-level namespace as in::

        foo/
            company/
                foo/
                    a.py
        bar/
            company/
                bar/
                    b.py
        baz/
            company/
                baz/
                    c.py
        ...

    If you are in this situation, you can enable an experimental fast path by
    setting the :option:`--fast-module-lookup` option.


.. option:: --no-namespace-packages

    This flag disables import discovery of namespace packages (see :pep:`420`).
    In particular, this prevents discovery of packages that don't have an
    ``__init__.py`` (or ``__init__.pyi``) file.

    This flag affects how mypy finds modules and packages explicitly passed on
    the command line. It also affects how mypy determines fully qualified module
    names for files passed on the command line. See :ref:`Mapping file paths to
    modules <mapping-paths-to-modules>` for details.


.. _platform-configuration:

Platform configuration
**********************

By default, mypy will assume that you intend to run your code using the same
operating system and Python version you are using to run mypy itself. The
following flags let you modify this behavior.

For more information on how to use these flags, see :ref:`version_and_platform_checks`.

.. option:: --python-version X.Y

    This flag will make mypy type check your code as if it were
    run under Python version X.Y. Without this option, mypy will default to using
    whatever version of Python is running mypy.

    This flag will attempt to find a Python executable of the corresponding
    version to search for :pep:`561` compliant packages. If you'd like to
    disable this, use the :option:`--no-site-packages` flag (see
    :ref:`import-discovery` for more details).

.. option:: --platform PLATFORM

    This flag will make mypy type check your code as if it were
    run under the given operating system. Without this option, mypy will
    default to using whatever operating system you are currently using.

    The ``PLATFORM`` parameter may be any string supported by
    :py:data:`sys.platform`.

.. _always-true:

.. option:: --always-true NAME

    This flag will treat all variables named ``NAME`` as
    compile-time constants that are always true.  This flag may
    be repeated.

.. option:: --always-false NAME

    This flag will treat all variables named ``NAME`` as
    compile-time constants that are always false.  This flag may
    be repeated.


.. _disallow-dynamic-typing:

Disallow dynamic typing
***********************

The ``Any`` type is used to represent a value that has a :ref:`dynamic type <dynamic-typing>`.
The ``--disallow-any`` family of flags will disallow various uses of the ``Any`` type in
a module -- this lets us strategically disallow the use of dynamic typing in a controlled way.

The following options are available:

.. option:: --disallow-any-unimported

    This flag disallows usage of types that come from unfollowed imports
    (such types become aliases for ``Any``). Unfollowed imports occur either
    when the imported module does not exist or when :option:`--follow-imports=skip <--follow-imports>`
    is set.

.. option:: --disallow-any-expr

    This flag disallows all expressions in the module that have type ``Any``.
    If an expression of type ``Any`` appears anywhere in the module
    mypy will output an error unless the expression is immediately
    used as an argument to :py:func:`~typing.cast` or assigned to a variable with an
    explicit type annotation.

    In addition, declaring a variable of type ``Any``
    or casting to type ``Any`` is not allowed. Note that calling functions
    that take parameters of type ``Any`` is still allowed.

.. option:: --disallow-any-decorated

    This flag disallows functions that have ``Any`` in their signature
    after decorator transformation.

.. option:: --disallow-any-explicit

    This flag disallows explicit ``Any`` in type positions such as type
    annotations and generic type parameters.

.. option:: --disallow-any-generics

    This flag disallows usage of generic types that do not specify explicit
    type parameters. For example, you can't use a bare ``x: list``. Instead, you
    must always write something like ``x: list[int]``.

.. option:: --disallow-subclassing-any

    This flag reports an error whenever a class subclasses a value of
    type ``Any``.  This may occur when the base class is imported from
    a module that doesn't exist (when using
    :option:`--ignore-missing-imports`) or is
    ignored due to :option:`--follow-imports=skip <--follow-imports>` or a
    ``# type: ignore`` comment on the ``import`` statement.

    Since the module is silenced, the imported class is given a type of ``Any``.
    By default mypy will assume that the subclass correctly inherited
    the base class even though that may not actually be the case.  This
    flag makes mypy raise an error instead.


.. _untyped-definitions-and-calls:

Untyped definitions and calls
*****************************

The following flags configure how mypy handles untyped function
definitions or calls.

.. option:: --disallow-untyped-calls

    This flag reports an error whenever a function with type annotations
    calls a function defined without annotations.

.. option:: --untyped-calls-exclude

    This flag allows to selectively disable :option:`--disallow-untyped-calls`
    for functions and methods defined in specific packages, modules, or classes.
    Note that each exclude entry acts as a prefix. For example (assuming there
    are no type annotations for ``third_party_lib`` available):

    .. code-block:: python

        # mypy --disallow-untyped-calls
        #      --untyped-calls-exclude=third_party_lib.module_a
        #      --untyped-calls-exclude=foo.A
        from third_party_lib.module_a import some_func
        from third_party_lib.module_b import other_func
        import foo

        some_func()  # OK, function comes from module `third_party_lib.module_a`
        other_func()  # E: Call to untyped function "other_func" in typed context

        foo.A().meth()  # OK, method was defined in class `foo.A`
        foo.B().meth()  # E: Call to untyped function "meth" in typed context

        # file foo.py
        class A:
            def meth(self): pass
        class B:
            def meth(self): pass

.. option:: --disallow-untyped-defs

    This flag reports an error whenever it encounters a function definition
    without type annotations or with incomplete type annotations.
    (a superset of :option:`--disallow-incomplete-defs`).

    For example, it would report an error for :code:`def f(a, b)` and :code:`def f(a: int, b)`.

.. option:: --disallow-incomplete-defs

    This flag reports an error whenever it encounters a partly annotated
    function definition, while still allowing entirely unannotated definitions.

    For example, it would report an error for :code:`def f(a: int, b)` but not :code:`def f(a, b)`.

.. option:: --check-untyped-defs

    This flag is less severe than the previous two options -- it type checks
    the body of every function, regardless of whether it has type annotations.
    (By default the bodies of functions without annotations are not type
    checked.)

    It will assume all arguments have type ``Any`` and always infer ``Any``
    as the return type.

.. option:: --disallow-untyped-decorators

    This flag reports an error whenever a function with type annotations
    is decorated with a decorator without annotations.


.. _none-and-optional-handling:

None and Optional handling
**************************

The following flags adjust how mypy handles values of type ``None``.

.. _implicit-optional:

.. option:: --implicit-optional

    This flag causes mypy to treat parameters with a ``None``
    default value as having an implicit optional type (``T | None``).

    For example, if this flag is set, mypy would assume that the ``x``
    parameter is actually of type ``int | None`` in the code snippet below,
    since the default parameter is ``None``:

    .. code-block:: python

        def foo(x: int = None) -> None:
            print(x)

    **Note:** This was disabled by default starting in mypy 0.980.

.. _no_strict_optional:

.. option:: --no-strict-optional

    This flag effectively disables checking of optional
    types and ``None`` values. With this option, mypy doesn't
    generally check the use of ``None`` values -- it is treated
    as compatible with every type.

    .. warning::

        ``--no-strict-optional`` is evil. Avoid using it and definitely do
        not use it without understanding what it does.


.. _configuring-warnings:

Configuring warnings
********************

The following flags enable warnings for code that is sound but is
potentially problematic or redundant in some way.

.. option:: --warn-redundant-casts

    This flag will make mypy report an error whenever your code uses
    an unnecessary cast that can safely be removed.

.. option:: --warn-unused-ignores

    This flag will make mypy report an error whenever your code uses
    a ``# type: ignore`` comment on a line that is not actually
    generating an error message.

    This flag, along with the :option:`--warn-redundant-casts` flag, are both
    particularly useful when you are upgrading mypy. Previously,
    you may have needed to add casts or ``# type: ignore`` annotations
    to work around bugs in mypy or missing stubs for 3rd party libraries.

    These two flags let you discover cases where either workarounds are
    no longer necessary.

.. option:: --no-warn-no-return

    By default, mypy will generate errors when a function is missing
    return statements in some execution paths. The only exceptions
    are when:

    -   The function has a ``None`` or ``Any`` return type
    -   The function has an empty body and is marked as an abstract method,
        is in a protocol class, or is in a stub file
    -  The execution path can never return; for example, if an exception
        is always raised

    Passing in :option:`--no-warn-no-return` will disable these error
    messages in all cases.

.. option:: --warn-return-any

    This flag causes mypy to generate a warning when returning a value
    with type ``Any`` from a function declared with a non-``Any`` return type.

.. option:: --warn-unreachable

    This flag will make mypy report an error whenever it encounters
    code determined to be unreachable or redundant after performing type analysis.
    This can be a helpful way of detecting certain kinds of bugs in your code.

    For example, enabling this flag will make mypy report that the ``x > 7``
    check is redundant and that the ``else`` block below is unreachable.

    .. code-block:: python

        def process(x: int) -> None:
            # Error: Right operand of "or" is never evaluated
            if isinstance(x, int) or x > 7:
                # Error: Unsupported operand types for + ("int" and "str")
                print(x + "bad")
            else:
                # Error: 'Statement is unreachable' error
                print(x + "bad")

    To help prevent mypy from generating spurious warnings, the "Statement is
    unreachable" warning will be silenced in exactly two cases:

    1.  When the unreachable statement is a ``raise`` statement, is an
        ``assert False`` statement, or calls a function that has the :py:data:`~typing.NoReturn`
        return type hint. In other words, when the unreachable statement
        throws an error or terminates the program in some way.
    2.  When the unreachable statement was *intentionally* marked as unreachable
        using :ref:`version_and_platform_checks`.

    .. note::

        Mypy currently cannot detect and report unreachable or redundant code
        inside any functions using :ref:`type-variable-value-restriction`.

        This limitation will be removed in future releases of mypy.

.. option:: --report-deprecated-as-note

    If error code ``deprecated`` is enabled, mypy emits errors if your code
    imports or uses deprecated features. This flag converts such errors to
    notes, causing mypy to eventually finish with a zero exit code. Features
    are considered deprecated when decorated with ``warnings.deprecated``.

.. option:: --deprecated-calls-exclude

    This flag allows to selectively disable :ref:`deprecated<code-deprecated>` warnings
    for functions and methods defined in specific packages, modules, or classes.
    Note that each exclude entry acts as a prefix. For example (assuming ``foo.A.func`` is deprecated):

    .. code-block:: python

        # mypy --enable-error-code deprecated
        #      --deprecated-calls-exclude=foo.A
        import foo

        foo.A().func()  # OK, the deprecated warning is ignored

        # file foo.py
        from typing_extensions import deprecated
        class A:
            @deprecated("Use A.func2 instead")
            def func(self): pass

.. _miscellaneous-strictness-flags:

Miscellaneous strictness flags
******************************

This section documents any other flags that do not neatly fall under any
of the above sections.

.. option:: --allow-untyped-globals

    This flag causes mypy to suppress errors caused by not being able to fully
    infer the types of global and class variables.

.. option:: --allow-redefinition-new

    By default, mypy won't allow a variable to be redefined with an
    unrelated type. This *experimental* flag enables the redefinition of
    unannotated variables with an arbitrary type. You will also need to enable
    :option:`--local-partial-types <mypy --local-partial-types>`.
    Example:

    .. code-block:: python

        def maybe_convert(n: int, b: bool) -> int | str:
            if b:
                x = str(n)  # Assign "str"
            else:
                x = n       # Assign "int"
            # Type of "x" is "int | str" here.
            return x

    Without the new flag, mypy only supports inferring optional types
    (``X | None``) from multiple assignments. With this option enabled,
    mypy can infer arbitrary union types.

    This also enables an unannotated variable to have different types in different
    code locations:

    .. code-block:: python

        if check():
            for x in range(n):
                # Type of "x" is "int" here.
                ...
        else:
            for x in ['a', 'b']:
                # Type of "x" is "str" here.
                ...

    Note: We are planning to turn this flag on by default in a future mypy
    release, along with :option:`--local-partial-types <mypy --local-partial-types>`.
    The feature is still experimental, and the semantics may still change.

.. option:: --allow-redefinition

    This is an older variant of
    :option:`--allow-redefinition-new <mypy --allow-redefinition-new>`.
    This flag enables redefinition of a variable with an
    arbitrary type *in some contexts*: only redefinitions within the
    same block and nesting depth as the original definition are allowed.

    We have no plans to remove this flag, but we expect that
    :option:`--allow-redefinition-new <mypy --allow-redefinition-new>`
    will replace this flag for new use cases eventually.

    Example where this can be useful:

    .. code-block:: python

       def process(items: list[str]) -> None:
           # 'items' has type list[str]
           items = [item.split() for item in items]
           # 'items' now has type list[list[str]]

    The variable must be used before it can be redefined:

    .. code-block:: python

        def process(items: list[str]) -> None:
           items = "mypy"  # invalid redefinition to str because the variable hasn't been used yet
           print(items)
           items = "100"  # valid, items now has type str
           items = int(items)  # valid, items now has type int

.. option:: --local-partial-types

    In mypy, the most common cases for partial types are variables initialized using ``None``,
    but without explicit ``X | None`` annotations. By default, mypy won't check partial types
    spanning module top level or class top level. This flag changes the behavior to only allow
    partial types at local level, therefore it disallows inferring variable type for ``None``
    from two assignments in different scopes. For example:

    .. code-block:: python

        a = None  # Need type annotation here if using --local-partial-types
        b: int | None = None

        class Foo:
            bar = None  # Need type annotation here if using --local-partial-types
            baz: int | None = None

            def __init__(self) -> None:
                self.bar = 1

        reveal_type(Foo().bar)  # 'int | None' without --local-partial-types

    Note: this option is always implicitly enabled in mypy daemon and will become
    enabled by default for mypy in a future release.

.. option:: --no-implicit-reexport

    By default, imported values to a module are treated as exported and mypy allows
    other modules to import them. This flag changes the behavior to not re-export unless
    the item is imported using from-as or is included in ``__all__``. Note this is
    always treated as enabled for stub files. For example:

    .. code-block:: python

       # This won't re-export the value
       from foo import bar

       # Neither will this
       from foo import bar as bang

       # This will re-export it as bar and allow other modules to import it
       from foo import bar as bar

       # This will also re-export bar
       from foo import bar
       __all__ = ['bar']


.. option:: --strict-equality

    By default, mypy allows always-false comparisons like ``42 == 'no'``.
    Use this flag to prohibit such comparisons of non-overlapping types, and
    similar identity and container checks:

    .. code-block:: python

       items: list[int]
       if 'some string' in items:  # Error: non-overlapping container check!
           ...

       text: str
       if text != b'other bytes':  # Error: non-overlapping equality check!
           ...

       assert text is not None  # OK, check against None is allowed as a special case.


.. option:: --strict-bytes

    By default, mypy treats ``bytearray`` and ``memoryview`` as subtypes of ``bytes`` which
    is not true at runtime. Use this flag to disable this behavior. ``--strict-bytes`` will
    be enabled by default in *mypy 2.0*.

    .. code-block:: python

       def f(buf: bytes) -> None:
           assert isinstance(buf, bytes)  # Raises runtime AssertionError with bytearray/memoryview
           with open("binary_file", "wb") as fp:
               fp.write(buf)

       f(bytearray(b""))  # error: Argument 1 to "f" has incompatible type "bytearray"; expected "bytes"
       f(memoryview(b""))  # error: Argument 1 to "f" has incompatible type "memoryview"; expected "bytes"

       # If `f` accepts any object that implements the buffer protocol, consider using:
       from collections.abc import Buffer  # "from typing_extensions" in Python 3.11 and earlier

       def f(buf: Buffer) -> None:
           with open("binary_file", "wb") as fp:
               fp.write(buf)

       f(b"")  # Ok
       f(bytearray(b""))  # Ok
       f(memoryview(b""))  # Ok


.. option:: --extra-checks

    This flag enables additional checks that are technically correct but may be
    impractical. In particular, it prohibits partial overlap in ``TypedDict`` updates,
    and makes arguments prepended via ``Concatenate`` positional-only. For example:

    .. code-block:: python

       from typing import TypedDict

       class Foo(TypedDict):
           a: int

       class Bar(TypedDict):
           a: int
           b: int

       def test(foo: Foo, bar: Bar) -> None:
           # This is technically unsafe since foo can have a subtype of Foo at
           # runtime, where type of key "b" is incompatible with int, see below
           bar.update(foo)

       class Bad(Foo):
           b: str
       bad: Bad = {"a": 0, "b": "no"}
       test(bad, bar)

    In future more checks may be added to this flag if:

    * The corresponding use cases are rare, thus not justifying a dedicated
      strictness flag.

    * The new check cannot be supported as an opt-in error code.

.. option:: --strict

    This flag mode enables a defined subset of optional error-checking flags.
    This subset primarily includes checks for inadvertent type unsoundness (i.e
    strict will catch type errors as long as intentional methods like type ignore
    or casting were not used.)

    Note: the :option:`--warn-unreachable` flag
    is not automatically enabled by the strict flag.

    The strict flag does not take precedence over other strict-related flags.
    Directly specifying a flag of alternate behavior will override the
    behavior of strict, regardless of the order in which they are passed.
    You can see the list of flags enabled by strict mode in the full
    :option:`mypy --help` output.

    Note: the exact list of flags enabled by running :option:`--strict` may change
    over time.

    .. include:: strict_list.rst
    ..
        The above file is autogenerated and included during html generation.
        (That's an include directive, and this is a comment.)
        It would be fine to generate it at some other time instead,
        theoretically, but we already had a convenient hook during html gen.


.. option:: --disable-error-code

    This flag allows disabling one or multiple error codes globally.
    See :ref:`error-codes` for more information.

    .. code-block:: python

        # no flag
        x = 'a string'
        x.trim()  # error: "str" has no attribute "trim"  [attr-defined]

        # When using --disable-error-code attr-defined
        x = 'a string'
        x.trim()

.. option:: --enable-error-code

    This flag allows enabling one or multiple error codes globally.
    See :ref:`error-codes` for more information.

    Note: This flag will override disabled error codes from the
    :option:`--disable-error-code <mypy --disable-error-code>` flag.

    .. code-block:: python

        # When using --disable-error-code attr-defined
        x = 'a string'
        x.trim()

        # --disable-error-code attr-defined --enable-error-code attr-defined
        x = 'a string'
        x.trim()  # error: "str" has no attribute "trim"  [attr-defined]


.. _configuring-error-messages:

Configuring error messages
**************************

The following flags let you adjust how much detail mypy displays
in error messages.

.. option:: --show-error-context

    This flag will precede all errors with "note" messages explaining the
    context of the error. For example, consider the following program:

    .. code-block:: python

        class Test:
            def foo(self, x: int) -> int:
                return x + "bar"

    Mypy normally displays an error message that looks like this::

        main.py:3: error: Unsupported operand types for + ("int" and "str")

    If we enable this flag, the error message now looks like this::

        main.py: note: In member "foo" of class "Test":
        main.py:3: error: Unsupported operand types for + ("int" and "str")

.. option:: --show-column-numbers

    This flag will add column offsets to error messages.
    For example, the following indicates an error in line 12, column 9
    (note that column offsets are 0-based)::

        main.py:12:9: error: Unsupported operand types for / ("int" and "str")

.. option:: --show-error-code-links

    This flag will also display a link to error code documentation, anchored to the error code reported by mypy.
    The corresponding error code will be highlighted within the documentation page.
    If we enable this flag, the error message now looks like this::

        main.py:3: error: Unsupported operand types for - ("int" and "str")  [operator]
        main.py:3: note: See 'https://mypy.rtfd.io/en/stable/_refs.html#code-operator' for more info



.. option:: --show-error-end

    This flag will make mypy show not just that start position where
    an error was detected, but also the end position of the relevant expression.
    This way various tools can easily highlight the whole error span. The format is
    ``file:line:column:end_line:end_column``. This option implies
    ``--show-column-numbers``.

.. option:: --hide-error-codes

    This flag will hide the error code ``[<code>]`` from error messages. By default, the error
    code is shown after each error message::

        prog.py:1: error: "str" has no attribute "trim"  [attr-defined]

    See :ref:`error-codes` for more information.

.. option:: --pretty

    Use visually nicer output in error messages: use soft word wrap,
    show source code snippets, and show error location markers.

.. option:: --no-color-output

    This flag will disable color output in error messages, enabled by default.

.. option:: --no-error-summary

    This flag will disable error summary. By default mypy shows a summary line
    including total number of errors, number of files with errors, and number
    of files checked.

.. option:: --show-absolute-path

    Show absolute paths to files.

.. option:: --soft-error-limit N

    This flag will adjust the limit after which mypy will (sometimes)
    disable reporting most additional errors. The limit only applies
    if it seems likely that most of the remaining errors will not be
    useful or they may be overly noisy. If ``N`` is negative, there is
    no limit. The default limit is -1.

.. option:: --force-union-syntax

    Always use ``Union[]`` and ``Optional[]`` for union types
    in error messages (instead of the ``|`` operator),
    even on Python 3.10+.


.. _incremental:

Incremental mode
****************

By default, mypy will store type information into a cache. Mypy
will use this information to avoid unnecessary recomputation when
it type checks your code again.  This can help speed up the type
checking process, especially when most parts of your program have
not changed since the previous mypy run.

If you want to speed up how long it takes to recheck your code
beyond what incremental mode can offer, try running mypy in
:ref:`daemon mode <mypy_daemon>`.

.. option:: --no-incremental

    This flag disables incremental mode: mypy will no longer reference
    the cache when re-run.

    Note that mypy will still write out to the cache even when
    incremental mode is disabled: see the :option:`--cache-dir` flag below
    for more details.

.. option:: --cache-dir DIR

    By default, mypy stores all cache data inside of a folder named
    ``.mypy_cache`` in the current directory. This flag lets you
    change this folder. This flag can also be useful for controlling
    cache use when using :ref:`remote caching <remote-cache>`.

    This setting will override the ``MYPY_CACHE_DIR`` environment
    variable if it is set.

    Mypy will also always write to the cache even when incremental
    mode is disabled so it can "warm up" the cache. To disable
    writing to the cache, use ``--cache-dir=/dev/null`` (UNIX)
    or ``--cache-dir=nul`` (Windows).

.. option:: --sqlite-cache

    Use an `SQLite`_ database to store the cache.

.. option:: --cache-fine-grained

    Include fine-grained dependency information in the cache for the mypy daemon.

.. option:: --skip-version-check

    By default, mypy will ignore cache data generated by a different
    version of mypy. This flag disables that behavior.

.. option:: --skip-cache-mtime-checks

    Skip cache internal consistency checks based on mtime.


Advanced options
****************

The following flags are useful mostly for people who are interested
in developing or debugging mypy internals.

.. option:: --pdb

    This flag will invoke the Python debugger when mypy encounters
    a fatal error.

.. option:: --show-traceback, --tb

    If set, this flag will display a full traceback when mypy
    encounters a fatal error.

.. option:: --raise-exceptions

    Raise exception on fatal error.

.. option:: --custom-typing-module MODULE

    This flag lets you use a custom module as a substitute for the
    :py:mod:`typing` module.

.. option:: --custom-typeshed-dir DIR

    This flag specifies the directory where mypy looks for standard library typeshed
    stubs, instead of the typeshed that ships with mypy.  This is
    primarily intended to make it easier to test typeshed changes before
    submitting them upstream, but also allows you to use a forked version of
    typeshed.

    Note that this doesn't affect third-party library stubs. To test third-party stubs,
    for example try ``MYPYPATH=stubs/six mypy ...``.

.. _warn-incomplete-stub:

.. option:: --warn-incomplete-stub

    This flag modifies both the :option:`--disallow-untyped-defs` and
    :option:`--disallow-incomplete-defs` flags so they also report errors
    if stubs in typeshed are missing type annotations or has incomplete
    annotations. If both flags are missing, :option:`--warn-incomplete-stub`
    also does nothing.

    This flag is mainly intended to be used by people who want contribute
    to typeshed and would like a convenient way to find gaps and omissions.

    If you want mypy to report an error when your codebase *uses* an untyped
    function, whether that function is defined in typeshed or not, use the
    :option:`--disallow-untyped-calls` flag. See :ref:`untyped-definitions-and-calls`
    for more details.

.. _shadow-file:

.. option:: --shadow-file SOURCE_FILE SHADOW_FILE

    When mypy is asked to type check ``SOURCE_FILE``, this flag makes mypy
    read from and type check the contents of ``SHADOW_FILE`` instead. However,
    diagnostics will continue to refer to ``SOURCE_FILE``.

    Specifying this argument multiple times (``--shadow-file X1 Y1 --shadow-file X2 Y2``)
    will allow mypy to perform multiple substitutions.

    This allows tooling to create temporary files with helpful modifications
    without having to change the source file in place. For example, suppose we
    have a pipeline that adds ``reveal_type`` for certain variables.
    This pipeline is run on ``original.py`` to produce ``temp.py``.
    Running ``mypy --shadow-file original.py temp.py original.py`` will then
    cause mypy to type check the contents of ``temp.py`` instead of  ``original.py``,
    but error messages will still reference ``original.py``.


Report generation
*****************

If these flags are set, mypy will generate a report in the specified
format into the specified directory.

.. option:: --any-exprs-report DIR

    Causes mypy to generate a text file report documenting how many
    expressions of type ``Any`` are present within your codebase.

.. option:: --cobertura-xml-report DIR

    Causes mypy to generate a Cobertura XML type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.

.. option:: --html-report / --xslt-html-report DIR

    Causes mypy to generate an HTML type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.

.. option:: --linecount-report DIR

    Causes mypy to generate a text file report documenting the functions
    and lines that are typed and untyped within your codebase.

.. option:: --linecoverage-report DIR

    Causes mypy to generate a JSON file that maps each source file's
    absolute filename to a list of line numbers that belong to typed
    functions in that file.

.. option:: --lineprecision-report DIR

    Causes mypy to generate a flat text file report with per-module
    statistics of how many lines are typechecked etc.

.. option:: --txt-report / --xslt-txt-report DIR

    Causes mypy to generate a text file type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.

.. option:: --xml-report DIR

    Causes mypy to generate an XML type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.


Enabling incomplete/experimental features
*****************************************

.. option:: --enable-incomplete-feature {PreciseTupleTypes, InlineTypedDict}

    Some features may require several mypy releases to implement, for example
    due to their complexity, potential for backwards incompatibility, or
    ambiguous semantics that would benefit from feedback from the community.
    You can enable such features for early preview using this flag. Note that
    it is not guaranteed that all features will be ultimately enabled by
    default. In *rare cases* we may decide to not go ahead with certain
    features.

List of currently incomplete/experimental features:

* ``PreciseTupleTypes``: this feature will infer more precise tuple types in
  various scenarios. Before variadic types were added to the Python type system
  by :pep:`646`, it was impossible to express a type like "a tuple with
  at least two integers". The best type available was ``tuple[int, ...]``.
  Therefore, mypy applied very lenient checking for variable-length tuples.
  Now this type can be expressed as ``tuple[int, int, *tuple[int, ...]]``.
  For such more precise types (when explicitly *defined* by a user) mypy,
  for example, warns about unsafe index access, and generally handles them
  in a type-safe manner. However, to avoid problems in existing code, mypy
  does not *infer* these precise types when it technically can. Here are
  notable examples where ``PreciseTupleTypes`` infers more precise types:

  .. code-block:: python

     numbers: tuple[int, ...]

     more_numbers = (1, *numbers, 1)
     reveal_type(more_numbers)
     # Without PreciseTupleTypes: tuple[int, ...]
     # With PreciseTupleTypes: tuple[int, *tuple[int, ...], int]

     other_numbers = (1, 1) + numbers
     reveal_type(other_numbers)
     # Without PreciseTupleTypes: tuple[int, ...]
     # With PreciseTupleTypes: tuple[int, int, *tuple[int, ...]]

     if len(numbers) > 2:
         reveal_type(numbers)
         # Without PreciseTupleTypes: tuple[int, ...]
         # With PreciseTupleTypes: tuple[int, int, int, *tuple[int, ...]]
     else:
         reveal_type(numbers)
         # Without PreciseTupleTypes: tuple[int, ...]
         # With PreciseTupleTypes: tuple[()] | tuple[int] | tuple[int, int]

* ``InlineTypedDict``: this feature enables non-standard syntax for inline
  :ref:`TypedDicts <typeddict>`, for example:

  .. code-block:: python

     def test_values() -> {"int": int, "str": str}:
         return {"int": 42, "str": "test"}


Miscellaneous
*************

.. option:: --install-types

    This flag causes mypy to install known missing stub packages for
    third-party libraries using pip.  It will display the pip command
    that will be run, and expects a confirmation before installing
    anything. For security reasons, these stubs are limited to only a
    small subset of manually selected packages that have been
    verified by the typeshed team. These packages include only stub
    files and no executable code.

    If you use this option without providing any files or modules to
    type check, mypy will install stub packages suggested during the
    previous mypy run. If there are files or modules to type check,
    mypy first type checks those, and proposes to install missing
    stubs at the end of the run, but only if any missing modules were
    detected.

    .. note::

        This is new in mypy 0.900. Previous mypy versions included a
        selection of third-party package stubs, instead of having
        them installed separately.

.. option:: --non-interactive

   When used together with :option:`--install-types <mypy
   --install-types>`, this causes mypy to install all suggested stub
   packages using pip without asking for confirmation, and then
   continues to perform type checking using the installed stubs, if
   some files or modules are provided to type check.

   This is implemented as up to two mypy runs internally. The first run
   is used to find missing stub packages, and output is shown from
   this run only if no missing stub packages were found. If missing
   stub packages were found, they are installed and then another run
   is performed.

.. option:: --junit-xml JUNIT_XML

    Causes mypy to generate a JUnit XML test result document with
    type checking results. This can make it easier to integrate mypy
    with continuous integration (CI) tools.

.. option:: --find-occurrences CLASS.MEMBER

    This flag will make mypy print out all usages of a class member
    based on static type information. This feature is experimental.

.. option:: --scripts-are-modules

    This flag will give command line arguments that appear to be
    scripts (i.e. files whose name does not end in ``.py``)
    a module name derived from the script name rather than the fixed
    name :py:mod:`__main__`.

    This lets you check more than one script in a single mypy invocation.
    (The default :py:mod:`__main__` is technically more correct, but if you
    have many scripts that import a large package, the behavior enabled
    by this flag is often more convenient.)

.. _lxml: https://pypi.org/project/lxml/
.. _SQLite: https://www.sqlite.org/
````

## File: docs/source/common_issues.rst
````
.. _common_issues:

Common issues and solutions
===========================

This section has examples of cases when you need to update your code
to use static typing, and ideas for working around issues if mypy
doesn't work as expected. Statically typed code is often identical to
normal Python code (except for type annotations), but sometimes you need
to do things slightly differently.

.. _annotations_needed:

No errors reported for obviously wrong code
-------------------------------------------

There are several common reasons why obviously wrong code is not
flagged as an error.

**The function containing the error is not annotated.**

Functions that
do not have any annotations (neither for any argument nor for the
return type) are not type-checked, and even the most blatant type
errors (e.g. ``2 + 'a'``) pass silently.  The solution is to add
annotations. Where that isn't possible, functions without annotations
can be checked using :option:`--check-untyped-defs <mypy --check-untyped-defs>`.

Example:

.. code-block:: python

    def foo(a):
        return '(' + a.split() + ')'  # No error!

This gives no error even though ``a.split()`` is "obviously" a list
(the author probably meant ``a.strip()``).  The error is reported
once you add annotations:

.. code-block:: python

    def foo(a: str) -> str:
        return '(' + a.split() + ')'
    # error: Unsupported operand types for + ("str" and "list[str]")

If you don't know what types to add, you can use ``Any``, but beware:

**One of the values involved has type 'Any'.**

Extending the above
example, if we were to leave out the annotation for ``a``, we'd get
no error:

.. code-block:: python

    def foo(a) -> str:
        return '(' + a.split() + ')'  # No error!

The reason is that if the type of ``a`` is unknown, the type of
``a.split()`` is also unknown, so it is inferred as having type
``Any``, and it is no error to add a string to an ``Any``.

If you're having trouble debugging such situations,
:ref:`reveal_type() <reveal-type>` might come in handy.

Note that sometimes library stubs with imprecise type information
can be a source of ``Any`` values.

:py:meth:`__init__ <object.__init__>` **method has no annotated
arguments and no return type annotation.**

This is basically a combination of the two cases above, in that ``__init__``
without annotations can cause ``Any`` types leak into instance variables:

.. code-block:: python

    class Bad:
        def __init__(self):
            self.value = "asdf"
            1 + "asdf"  # No error!

    bad = Bad()
    bad.value + 1           # No error!
    reveal_type(bad)        # Revealed type is "__main__.Bad"
    reveal_type(bad.value)  # Revealed type is "Any"

    class Good:
        def __init__(self) -> None:  # Explicitly return None
            self.value = value


**Some imports may be silently ignored**.

A common source of unexpected ``Any`` values is the
:option:`--ignore-missing-imports <mypy --ignore-missing-imports>` flag.

When you use :option:`--ignore-missing-imports <mypy --ignore-missing-imports>`,
any imported module that cannot be found is silently replaced with ``Any``.

To help debug this, simply leave out
:option:`--ignore-missing-imports <mypy --ignore-missing-imports>`.
As mentioned in :ref:`fix-missing-imports`, setting ``ignore_missing_imports=True``
on a per-module basis will make bad surprises less likely and is highly encouraged.

Use of the :option:`--follow-imports=skip <mypy --follow-imports>` flags can also
cause problems. Use of these flags is strongly discouraged and only required in
relatively niche situations. See :ref:`follow-imports` for more information.

**mypy considers some of your code unreachable**.

See :ref:`unreachable` for more information.

**A function annotated as returning a non-optional type returns 'None'
and mypy doesn't complain**.

.. code-block:: python

    def foo() -> str:
        return None  # No error!

You may have disabled strict optional checking (see
:ref:`--no-strict-optional <no_strict_optional>` for more).

.. _silencing_checker:

Spurious errors and locally silencing the checker
-------------------------------------------------

You can use a ``# type: ignore`` comment to silence the type checker
on a particular line. For example, let's say our code is using
the C extension module ``frobnicate``, and there's no stub available.
Mypy will complain about this, as it has no information about the
module:

.. code-block:: python

    import frobnicate  # Error: No module "frobnicate"
    frobnicate.start()

You can add a ``# type: ignore`` comment to tell mypy to ignore this
error:

.. code-block:: python

    import frobnicate  # type: ignore
    frobnicate.start()  # Okay!

The second line is now fine, since the ignore comment causes the name
``frobnicate`` to get an implicit ``Any`` type.

.. note::

    You can use the form ``# type: ignore[<code>]`` to only ignore
    specific errors on the line. This way you are less likely to
    silence unexpected errors that are not safe to ignore, and this
    will also document what the purpose of the comment is.  See
    :ref:`error-codes` for more information.

.. note::

    The ``# type: ignore`` comment will only assign the implicit ``Any``
    type if mypy cannot find information about that particular module. So,
    if we did have a stub available for ``frobnicate`` then mypy would
    ignore the ``# type: ignore`` comment and typecheck the stub as usual.

Another option is to explicitly annotate values with type ``Any`` --
mypy will let you perform arbitrary operations on ``Any``
values. Sometimes there is no more precise type you can use for a
particular value, especially if you use dynamic Python features
such as :py:meth:`__getattr__ <object.__getattr__>`:

.. code-block:: python

   class Wrapper:
       ...
       def __getattr__(self, a: str) -> Any:
           return getattr(self._wrapped, a)

Finally, you can create a stub file (``.pyi``) for a file that
generates spurious errors. Mypy will only look at the stub file
and ignore the implementation, since stub files take precedence
over ``.py`` files.

Ignoring a whole file
---------------------

* To only ignore errors, use a top-level ``# mypy: ignore-errors`` comment instead.
* To only ignore errors with a specific error code, use a top-level
  ``# mypy: disable-error-code="..."`` comment. Example: ``# mypy: disable-error-code="truthy-bool, ignore-without-code"``
* To replace the contents of a module with ``Any``, use a per-module ``follow_imports = skip``.
  See :ref:`Following imports <follow-imports>` for details.

Note that a ``# type: ignore`` comment at the top of a module (before any statements,
including imports or docstrings) has the effect of ignoring the entire contents of the module.
This behaviour can be surprising and result in
"Module ... has no attribute ... [attr-defined]" errors.

Issues with code at runtime
---------------------------

Idiomatic use of type annotations can sometimes run up against what a given
version of Python considers legal code. These can result in some of the
following errors when trying to run your code:

* ``ImportError`` from circular imports
* ``NameError: name "X" is not defined`` from forward references
* ``TypeError: 'type' object is not subscriptable`` from types that are not generic at runtime
* ``ImportError`` or ``ModuleNotFoundError`` from use of stub definitions not available at runtime
* ``TypeError: unsupported operand type(s) for |: 'type' and 'type'`` from use of new syntax

For dealing with these, see :ref:`runtime_troubles`.

Mypy runs are slow
------------------

If your mypy runs feel slow, you should probably use the :ref:`mypy
daemon <mypy_daemon>`, which can speed up incremental mypy runtimes by
a factor of 10 or more. :ref:`Remote caching <remote-cache>` can
make cold mypy runs several times faster.

Furthermore: as of `mypy 1.13 <https://mypy-lang.blogspot.com/2024/10/mypy-113-released.html>`_,
mypy allows use of the orjson library for handling the cache instead of the stdlib json, for
improved performance. You can ensure the presence of orjson using the faster-cache extra:

    python3 -m pip install -U mypy[faster-cache]

Mypy may depend on orjson by default in the future.

Types of empty collections
--------------------------

You often need to specify the type when you assign an empty list or
dict to a new variable, as mentioned earlier:

.. code-block:: python

   a: list[int] = []

Without the annotation mypy can't always figure out the
precise type of ``a``.

You can use a simple empty list literal in a dynamically typed function (as the
type of ``a`` would be implicitly ``Any`` and need not be inferred), if type
of the variable has been declared or inferred before, or if you perform a simple
modification operation in the same scope (such as ``append`` for a list):

.. code-block:: python

   a = []  # Okay because followed by append, inferred type list[int]
   for i in range(n):
       a.append(i * i)

However, in more complex cases an explicit type annotation can be
required (mypy will tell you this). Often the annotation can
make your code easier to understand, so it doesn't only help mypy but
everybody who is reading the code!

Redefinitions with incompatible types
-------------------------------------

Each name within a function only has a single 'declared' type. You can
reuse for loop indices etc., but if you want to use a variable with
multiple types within a single function, you may need to instead use
multiple variables (or maybe declare the variable with an ``Any`` type).

.. code-block:: python

   def f() -> None:
       n = 1
       ...
       n = 'x'  # error: Incompatible types in assignment (expression has type "str", variable has type "int")

.. note::

   Using the :option:`--allow-redefinition <mypy --allow-redefinition>`
   flag can suppress this error in several cases.

Note that you can redefine a variable with a more *precise* or a more
concrete type. For example, you can redefine a sequence (which does
not support ``sort()``) as a list and sort it in-place:

.. code-block:: python

    def f(x: Sequence[int]) -> None:
        # Type of x is Sequence[int] here; we don't know the concrete type.
        x = list(x)
        # Type of x is list[int] here.
        x.sort()  # Okay!

See :ref:`type-narrowing` for more information.

.. _variance:

Invariance vs covariance
------------------------

Most mutable generic collections are invariant, and mypy considers all
user-defined generic classes invariant by default
(see :ref:`variance-of-generics` for motivation). This could lead to some
unexpected errors when combined with type inference. For example:

.. code-block:: python

   class A: ...
   class B(A): ...

   lst = [A(), A()]  # Inferred type is list[A]
   new_lst = [B(), B()]  # inferred type is list[B]
   lst = new_lst  # mypy will complain about this, because List is invariant

Possible strategies in such situations are:

* Use an explicit type annotation:

  .. code-block:: python

     new_lst: list[A] = [B(), B()]
     lst = new_lst  # OK

* Make a copy of the right hand side:

  .. code-block:: python

     lst = list(new_lst) # Also OK

* Use immutable collections as annotations whenever possible:

  .. code-block:: python

     def f_bad(x: list[A]) -> A:
         return x[0]
     f_bad(new_lst) # Fails

     def f_good(x: Sequence[A]) -> A:
         return x[0]
     f_good(new_lst) # OK

Declaring a supertype as variable type
--------------------------------------

Sometimes the inferred type is a subtype (subclass) of the desired
type. The type inference uses the first assignment to infer the type
of a name:

.. code-block:: python

   class Shape: ...
   class Circle(Shape): ...
   class Triangle(Shape): ...

   shape = Circle()    # mypy infers the type of shape to be Circle
   shape = Triangle()  # error: Incompatible types in assignment (expression has type "Triangle", variable has type "Circle")

You can just give an explicit type for the variable in cases such the
above example:

.. code-block:: python

   shape: Shape = Circle()  # The variable s can be any Shape, not just Circle
   shape = Triangle()       # OK

Complex type tests
------------------

Mypy can usually infer the types correctly when using :py:func:`isinstance <isinstance>`,
:py:func:`issubclass <issubclass>`,
or ``type(obj) is some_class`` type tests,
and even :ref:`user-defined type guards <type-guards>`,
but for other kinds of checks you may need to add an
explicit type cast:

.. code-block:: python

  from collections.abc import Sequence
  from typing import cast

  def find_first_str(a: Sequence[object]) -> str:
      index = next((i for i, s in enumerate(a) if isinstance(s, str)), -1)
      if index < 0:
          raise ValueError('No str found')

      found = a[index]  # Has type "object", despite the fact that we know it is "str"
      return cast(str, found)  # We need an explicit cast to make mypy happy

Alternatively, you can use an ``assert`` statement together with some
of the supported type inference techniques:

.. code-block:: python

  def find_first_str(a: Sequence[object]) -> str:
      index = next((i for i, s in enumerate(a) if isinstance(s, str)), -1)
      if index < 0:
          raise ValueError('No str found')

      found = a[index]  # Has type "object", despite the fact that we know it is "str"
      assert isinstance(found, str)  # Now, "found" will be narrowed to "str"
      return found  # No need for the explicit "cast()" anymore

.. note::

    Note that the :py:class:`object` type used in the above example is similar
    to ``Object`` in Java: it only supports operations defined for *all*
    objects, such as equality and :py:func:`isinstance`. The type ``Any``,
    in contrast, supports all operations, even if they may fail at
    runtime. The cast above would have been unnecessary if the type of
    ``o`` was ``Any``.

.. note::

   You can read more about type narrowing techniques :ref:`here <type-narrowing>`.

Type inference in Mypy is designed to work well in common cases, to be
predictable and to let the type checker give useful error
messages. More powerful type inference strategies often have complex
and difficult-to-predict failure modes and could result in very
confusing error messages. The tradeoff is that you as a programmer
sometimes have to give the type checker a little help.

.. _version_and_platform_checks:

Python version and system platform checks
-----------------------------------------

Mypy supports the ability to perform Python version checks and platform
checks (e.g. Windows vs Posix), ignoring code paths that won't be run on
the targeted Python version or platform. This allows you to more effectively
typecheck code that supports multiple versions of Python or multiple operating
systems.

More specifically, mypy will understand the use of :py:data:`sys.version_info` and
:py:data:`sys.platform` checks within ``if/elif/else`` statements. For example:

.. code-block:: python

   import sys

   # Distinguishing between different versions of Python:
   if sys.version_info >= (3, 13):
       # Python 3.13+ specific definitions and imports
   else:
       # Other definitions and imports

   # Distinguishing between different operating systems:
   if sys.platform.startswith("linux"):
       # Linux-specific code
   elif sys.platform == "darwin":
       # Mac-specific code
   elif sys.platform == "win32":
       # Windows-specific code
   else:
       # Other systems

As a special case, you can also use one of these checks in a top-level
(unindented) ``assert``; this makes mypy skip the rest of the file.
Example:

.. code-block:: python

   import sys

   assert sys.platform != 'win32'

   # The rest of this file doesn't apply to Windows.

Some other expressions exhibit similar behavior; in particular,
:py:data:`~typing.TYPE_CHECKING`, variables named ``MYPY`` or ``TYPE_CHECKING``, and any variable
whose name is passed to :option:`--always-true <mypy --always-true>` or :option:`--always-false <mypy --always-false>`.
(However, ``True`` and ``False`` are not treated specially!)

.. note::

   Mypy currently does not support more complex checks, and does not assign
   any special meaning when assigning a :py:data:`sys.version_info` or :py:data:`sys.platform`
   check to a variable. This may change in future versions of mypy.

By default, mypy will use your current version of Python and your current
operating system as default values for :py:data:`sys.version_info` and
:py:data:`sys.platform`.

To target a different Python version, use the :option:`--python-version X.Y <mypy --python-version>` flag.
For example, to verify your code typechecks if were run using Python 3.8, pass
in :option:`--python-version 3.8 <mypy --python-version>` from the command line. Note that you do not need
to have Python 3.8 installed to perform this check.

To target a different operating system, use the :option:`--platform PLATFORM <mypy --platform>` flag.
For example, to verify your code typechecks if it were run in Windows, pass
in :option:`--platform win32 <mypy --platform>`. See the documentation for :py:data:`sys.platform`
for examples of valid platform parameters.

.. _reveal-type:

Displaying the type of an expression
------------------------------------

You can use ``reveal_type(expr)`` to ask mypy to display the inferred
static type of an expression. This can be useful when you don't quite
understand how mypy handles a particular piece of code. Example:

.. code-block:: python

   reveal_type((1, 'hello'))  # Revealed type is "tuple[builtins.int, builtins.str]"

You can also use ``reveal_locals()`` at any line in a file
to see the types of all local variables at once. Example:

.. code-block:: python

   a = 1
   b = 'one'
   reveal_locals()
   # Revealed local types are:
   #     a: builtins.int
   #     b: builtins.str
.. note::

    ``reveal_type`` and ``reveal_locals`` are handled specially by mypy during
    type checking, and don't have to be defined or imported.

    However, if you want to run your code,
    you'll have to remove any ``reveal_type`` and ``reveal_locals``
    calls from your program or else Python will give you an error at runtime.

    Alternatively, you can import ``reveal_type`` from ``typing_extensions``
    or ``typing`` (on Python 3.11 and newer)

.. _silencing-linters:

Silencing linters
-----------------

In some cases, linters will complain about unused imports or code. In
these cases, you can silence them with a comment after type comments, or on
the same line as the import:

.. code-block:: python

   # to silence complaints about unused imports
   from typing import List  # noqa
   a = None  # type: List[int]


To silence the linter on the same line as a type comment
put the linter comment *after* the type comment:

.. code-block:: python

    a = some_complex_thing()  # type: ignore  # noqa

Covariant subtyping of mutable protocol members is rejected
-----------------------------------------------------------

Mypy rejects this because this is potentially unsafe.
Consider this example:

.. code-block:: python

   from typing import Protocol

   class P(Protocol):
       x: float

   def fun(arg: P) -> None:
       arg.x = 3.14

   class C:
       x = 42
   c = C()
   fun(c)  # This is not safe
   c.x << 5  # Since this will fail!

To work around this problem consider whether "mutating" is actually part
of a protocol. If not, then one can use a :py:class:`@property <property>` in
the protocol definition:

.. code-block:: python

   from typing import Protocol

   class P(Protocol):
       @property
       def x(self) -> float:
          pass

   def fun(arg: P) -> None:
       ...

   class C:
       x = 42
   fun(C())  # OK

Dealing with conflicting names
------------------------------

Suppose you have a class with a method whose name is the same as an
imported (or built-in) type, and you want to use the type in another
method signature.  E.g.:

.. code-block:: python

   class Message:
       def bytes(self):
           ...
       def register(self, path: bytes):  # error: Invalid type "mod.Message.bytes"
           ...

The third line elicits an error because mypy sees the argument type
``bytes`` as a reference to the method by that name.  Other than
renaming the method, a workaround is to use an alias:

.. code-block:: python

   bytes_ = bytes
   class Message:
       def bytes(self):
           ...
       def register(self, path: bytes_):
           ...

Using a development mypy build
------------------------------

You can install the latest development version of mypy from source. Clone the
`mypy repository on GitHub <https://github.com/python/mypy>`_, and then run
``pip install`` locally:

.. code-block:: text

    git clone https://github.com/python/mypy.git
    cd mypy
    python3 -m pip install --upgrade .

To install a development version of mypy that is mypyc-compiled, see the
instructions at the `mypyc wheels repo <https://github.com/mypyc/mypy_mypyc-wheels>`_.

Variables vs type aliases
-------------------------

Mypy has both *type aliases* and variables with types like ``type[...]``. These are
subtly different, and it's important to understand how they differ to avoid pitfalls.

1. A variable with type ``type[...]`` is defined using an assignment with an
   explicit type annotation:

   .. code-block:: python

     class A: ...
     tp: type[A] = A

2. You can define a type alias using an assignment without an explicit type annotation
   at the top level of a module:

   .. code-block:: python

     class A: ...
     Alias = A

   You can also use ``TypeAlias`` (:pep:`613`) to define an *explicit type alias*:

   .. code-block:: python

     from typing import TypeAlias  # "from typing_extensions" in Python 3.9 and earlier

     class A: ...
     Alias: TypeAlias = A

   You should always use ``TypeAlias`` to define a type alias in a class body or
   inside a function.

The main difference is that the target of an alias is precisely known statically, and this
means that they can be used in type annotations and other *type contexts*. Type aliases
can't be defined conditionally (unless using
:ref:`supported Python version and platform checks <version_and_platform_checks>`):

   .. code-block:: python

     class A: ...
     class B: ...

     if random() > 0.5:
         Alias = A
     else:
         # error: Cannot assign multiple types to name "Alias" without an
         # explicit "Type[...]" annotation
         Alias = B

     tp: type[object]  # "tp" is a variable with a type object value
     if random() > 0.5:
         tp = A
     else:
         tp = B  # This is OK

     def fun1(x: Alias) -> None: ...  # OK
     def fun2(x: tp) -> None: ...  # Error: "tp" is not valid as a type

Incompatible overrides
----------------------

It's unsafe to override a method with a more specific argument type,
as it violates the `Liskov substitution principle
<https://stackoverflow.com/questions/56860/what-is-an-example-of-the-liskov-substitution-principle>`_.
For return types, it's unsafe to override a method with a more general
return type.

Other incompatible signature changes in method overrides, such as
adding an extra required parameter, or removing an optional parameter,
will also generate errors. The signature of a method in a subclass
should accept all valid calls to the base class method. Mypy
treats a subclass as a subtype of the base class. An instance of a
subclass is valid everywhere where an instance of the base class is
valid.

This example demonstrates both safe and unsafe overrides:

.. code-block:: python

    from collections.abc import Sequence, Iterable

    class A:
        def test(self, t: Sequence[int]) -> Sequence[str]:
            ...

    class GeneralizedArgument(A):
        # A more general argument type is okay
        def test(self, t: Iterable[int]) -> Sequence[str]:  # OK
            ...

    class NarrowerArgument(A):
        # A more specific argument type isn't accepted
        def test(self, t: list[int]) -> Sequence[str]:  # Error
            ...

    class NarrowerReturn(A):
        # A more specific return type is fine
        def test(self, t: Sequence[int]) -> List[str]:  # OK
            ...

    class GeneralizedReturn(A):
        # A more general return type is an error
        def test(self, t: Sequence[int]) -> Iterable[str]:  # Error
            ...

You can use ``# type: ignore[override]`` to silence the error. Add it
to the line that generates the error, if you decide that type safety is
not necessary:

.. code-block:: python

    class NarrowerArgument(A):
        def test(self, t: List[int]) -> Sequence[str]:  # type: ignore[override]
            ...

.. _unreachable:

Unreachable code
----------------

Mypy may consider some code as *unreachable*, even if it might not be
immediately obvious why.  It's important to note that mypy will *not*
type check such code. Consider this example:

.. code-block:: python

    class Foo:
        bar: str = ''

    def bar() -> None:
        foo: Foo = Foo()
        return
        x: int = 'abc'  # Unreachable -- no error

It's easy to see that any statement after ``return`` is unreachable,
and hence mypy will not complain about the mistyped code below
it. For a more subtle example, consider this code:

.. code-block:: python

    class Foo:
        bar: str = ''

    def bar() -> None:
        foo: Foo = Foo()
        assert foo.bar is None
        x: int = 'abc'  # Unreachable -- no error

Again, mypy will not report any errors. The type of ``foo.bar`` is
``str``, and mypy reasons that it can never be ``None``.  Hence the
``assert`` statement will always fail and the statement below will
never be executed.  (Note that in Python, ``None`` is not an empty
reference but an object of type ``None``.)

In this example mypy will go on to check the last line and report an
error, since mypy thinks that the condition could be either True or
False:

.. code-block:: python

    class Foo:
        bar: str = ''

    def bar() -> None:
        foo: Foo = Foo()
        if not foo.bar:
            return
        x: int = 'abc'  # Reachable -- error

If you use the :option:`--warn-unreachable <mypy --warn-unreachable>` flag, mypy will generate
an error about each unreachable code block.

Narrowing and inner functions
-----------------------------

Because closures in Python are late-binding (https://docs.python-guide.org/writing/gotchas/#late-binding-closures),
mypy will not narrow the type of a captured variable in an inner function.
This is best understood via an example:

.. code-block:: python

    def foo(x: int | None) -> Callable[[], int]:
        if x is None:
            x = 5
        print(x + 1)  # mypy correctly deduces x must be an int here
        def inner() -> int:
            return x + 1  # but (correctly) complains about this line

        x = None  # because x could later be assigned None
        return inner

    inner = foo(5)
    inner()  # this will raise an error when called

To get this code to type check, you could assign ``y = x`` after ``x`` has been
narrowed, and use ``y`` in the inner function, or add an assert in the inner
function.

.. _incorrect-self:

Incorrect use of ``Self``
-------------------------

``Self`` is not the type of the current class; it's a type variable with upper
bound of the current class. That is, it represents the type of the current class
or of potential subclasses.

.. code-block:: python

    from typing import Self

    class Foo:
        @classmethod
        def constructor(cls) -> Self:
            # Instead, either call cls() or change the annotation to -> Foo
            return Foo()  # error: Incompatible return value type (got "Foo", expected "Self")

    class Bar(Foo):
        ...

    reveal_type(Foo.constructor())  # note: Revealed type is "Foo"
    # In the context of the subclass Bar, the Self return type promises
    # that the return value will be Bar
    reveal_type(Bar.constructor())  # note: Revealed type is "Bar"
````

## File: docs/source/config_file.rst
````
.. _config-file:

The mypy configuration file
===========================

Mypy is very configurable. This is most useful when introducing typing to
an existing codebase. See :ref:`existing-code` for concrete advice for
that situation.

Mypy supports reading configuration settings from a file. By default, mypy will
discover configuration files by walking up the file system (up until the root of
a repository or the root of the filesystem). In each directory, it will look for
the following configuration files (in this order):

    1. ``mypy.ini``
    2. ``.mypy.ini``
    3. ``pyproject.toml`` (containing a ``[tool.mypy]`` section)
    4. ``setup.cfg`` (containing a ``[mypy]`` section)

If no configuration file is found by this method, mypy will then look for
configuration files in the following locations (in this order):

    1. ``$XDG_CONFIG_HOME/mypy/config``
    2. ``~/.config/mypy/config``
    3. ``~/.mypy.ini``

The :option:`--config-file <mypy --config-file>` command-line flag has the
highest precedence and must point towards a valid configuration file;
otherwise mypy will report an error and exit. Without the command line option,
mypy will look for configuration files in the precedence order above.

It is important to understand that there is no merging of configuration
files, as it would lead to ambiguity.

Most flags correspond closely to :ref:`command-line flags
<command-line>` but there are some differences in flag names and some
flags may take a different value based on the module being processed.

Some flags support user home directory and environment variable expansion.
To refer to the user home directory, use ``~`` at the beginning of the path.
To expand environment variables use ``$VARNAME`` or ``${VARNAME}``.


Config file format
******************

The configuration file format is the usual
:doc:`ini file <python:library/configparser>` format. It should contain
section names in square brackets and flag settings of the form
`NAME = VALUE`. Comments start with ``#`` characters.

- A section named ``[mypy]`` must be present.  This specifies
  the global flags.

- Additional sections named ``[mypy-PATTERN1,PATTERN2,...]`` may be
  present, where ``PATTERN1``, ``PATTERN2``, etc., are comma-separated
  patterns of fully-qualified module names, with some components optionally
  replaced by the '*' character (e.g. ``foo.bar``, ``foo.bar.*``, ``foo.*.baz``).
  These sections specify additional flags that only apply to *modules*
  whose name matches at least one of the patterns.

  A pattern of the form ``qualified_module_name`` matches only the named module,
  while ``dotted_module_name.*`` matches ``dotted_module_name`` and any
  submodules (so ``foo.bar.*`` would match all of ``foo.bar``,
  ``foo.bar.baz``, and ``foo.bar.baz.quux``).

  Patterns may also be "unstructured" wildcards, in which stars may
  appear in the middle of a name (e.g
  ``site.*.migrations.*``). Stars match zero or more module
  components (so ``site.*.migrations.*`` can match ``site.migrations``).

  .. _config-precedence:

  When options conflict, the precedence order for configuration is:

    1. :ref:`Inline configuration <inline-config>` in the source file
    2. Sections with concrete module names (``foo.bar``)
    3. Sections with "unstructured" wildcard patterns (``foo.*.baz``),
       with sections later in the configuration file overriding
       sections earlier.
    4. Sections with "well-structured" wildcard patterns
       (``foo.bar.*``), with more specific overriding more general.
    5. Command line options.
    6. Top-level configuration file options.

The difference in precedence order between "structured" patterns (by
specificity) and "unstructured" patterns (by order in the file) is
unfortunate, and is subject to change in future versions.

.. note::

   The :confval:`warn_unused_configs` flag may be useful to debug misspelled
   section names.

.. note::

   Configuration flags are liable to change between releases.


Per-module and global options
*****************************

Some of the config options may be set either globally (in the ``[mypy]`` section)
or on a per-module basis (in sections like ``[mypy-foo.bar]``).

If you set an option both globally and for a specific module, the module configuration
options take precedence. This lets you set global defaults and override them on a
module-by-module basis. If multiple pattern sections match a module, :ref:`the options from the
most specific section are used where they disagree <config-precedence>`.

Some other options, as specified in their description,
may only be set in the global section (``[mypy]``).


Inverting option values
***********************

Options that take a boolean value may be inverted by adding ``no_`` to
their name or by (when applicable) swapping their prefix from
``disallow`` to ``allow`` (and vice versa).


Example ``mypy.ini``
********************

Here is an example of a ``mypy.ini`` file. To use this config file, place it at the root
of your repo and run mypy.

.. code-block:: ini

    # Global options:

    [mypy]
    warn_return_any = True
    warn_unused_configs = True

    # Per-module options:

    [mypy-mycode.foo.*]
    disallow_untyped_defs = True

    [mypy-mycode.bar]
    warn_return_any = False

    [mypy-somelibrary]
    ignore_missing_imports = True

This config file specifies two global options in the ``[mypy]`` section. These two
options will:

1.  Report an error whenever a function returns a value that is inferred
    to have type ``Any``.

2.  Report any config options that are unused by mypy. (This will help us catch typos
    when making changes to our config file).

Next, this module specifies three per-module options. The first two options change how mypy
type checks code in ``mycode.foo.*`` and ``mycode.bar``, which we assume here are two modules
that you wrote. The final config option changes how mypy type checks ``somelibrary``, which we
assume here is some 3rd party library you've installed and are importing. These options will:

1.  Selectively disallow untyped function definitions only within the ``mycode.foo``
    package -- that is, only for function definitions defined in the
    ``mycode/foo`` directory.

2.  Selectively *disable* the "function is returning any" warnings within
    ``mycode.bar`` only. This overrides the global default we set earlier.

3.  Suppress any error messages generated when your codebase tries importing the
    module ``somelibrary``. This is useful if ``somelibrary`` is some 3rd party library
    missing type hints.


.. _config-file-import-discovery:

Import discovery
****************

For more information, see the :ref:`Import discovery <import-discovery>`
section of the command line docs.

.. confval:: mypy_path

    :type: string

    Specifies the paths to use, after trying the paths from ``MYPYPATH`` environment
    variable.  Useful if you'd like to keep stubs in your repo, along with the config file.
    Multiple paths are always separated with a ``:`` or ``,`` regardless of the platform.
    User home directory and environment variables will be expanded.

    Relative paths are treated relative to the working directory of the mypy command,
    not the config file.
    Use the ``MYPY_CONFIG_FILE_DIR`` environment variable to refer to paths relative to
    the config file (e.g. ``mypy_path = $MYPY_CONFIG_FILE_DIR/src``).

    This option may only be set in the global section (``[mypy]``).

    **Note:** On Windows, use UNC paths to avoid using ``:`` (e.g. ``\\127.0.0.1\X$\MyDir`` where ``X`` is the drive letter).

.. confval:: files

    :type: comma-separated list of strings

    A comma-separated list of paths which should be checked by mypy if none are given on the command
    line. Supports recursive file globbing using :py:mod:`glob`, where ``*`` (e.g. ``*.py``) matches
    files in the current directory and ``**/`` (e.g. ``**/*.py``) matches files in any directories below
    the current one. User home directory and environment variables will be expanded.

    This option may only be set in the global section (``[mypy]``).

.. confval:: modules

    :type: comma-separated list of strings

    A comma-separated list of packages which should be checked by mypy if none are given on the command
    line. Mypy *will not* recursively type check any submodules of the provided
    module.

    This option may only be set in the global section (``[mypy]``).


.. confval:: packages

    :type: comma-separated list of strings

    A comma-separated list of packages which should be checked by mypy if none are given on the command
    line.  Mypy *will* recursively type check any submodules of the provided
    package. This flag is identical to :confval:`modules` apart from this
    behavior.

    This option may only be set in the global section (``[mypy]``).

.. confval:: exclude

    :type: regular expression

    A regular expression that matches file names, directory names and paths
    which mypy should ignore while recursively discovering files to check.
    Use forward slashes (``/``) as directory separators on all platforms.

    .. code-block:: ini

      [mypy]
      exclude = (?x)(
          ^one\.py$    # files named "one.py"
          | two\.pyi$  # or files ending with "two.pyi"
          | ^three\.   # or files starting with "three."
        )

    Crafting a single regular expression that excludes multiple files while remaining
    human-readable can be a challenge. The above example demonstrates one approach.
    ``(?x)`` enables the ``VERBOSE`` flag for the subsequent regular expression, which
    :py:data:`ignores most whitespace and supports comments <re.VERBOSE>`.
    The above is equivalent to: ``(^one\.py$|two\.pyi$|^three\.)``.

    For more details, see :option:`--exclude <mypy --exclude>`.

    This option may only be set in the global section (``[mypy]``).

    .. note::

       Note that the TOML equivalent differs slightly. It can be either a single string
       (including a multi-line string) -- which is treated as a single regular
       expression -- or an array of such strings. The following TOML examples are
       equivalent to the above INI example.

       Array of strings:

       .. code-block:: toml

          [tool.mypy]
          exclude = [
              "^one\\.py$",  # TOML's double-quoted strings require escaping backslashes
              'two\.pyi$',  # but TOML's single-quoted strings do not
              '^three\.',
          ]

       A single, multi-line string:

       .. code-block:: toml

          [tool.mypy]
          exclude = '''(?x)(
              ^one\.py$    # files named "one.py"
              | two\.pyi$  # or files ending with "two.pyi"
              | ^three\.   # or files starting with "three."
          )'''  # TOML's single-quoted strings do not require escaping backslashes

       See :ref:`using-a-pyproject-toml`.

.. confval:: exclude_gitignore

    :type: boolean
    :default: False

    This flag will add everything that matches ``.gitignore`` file(s) to :confval:`exclude`.
    This option may only be set in the global section (``[mypy]``).

.. confval:: namespace_packages

    :type: boolean
    :default: True

    Enables :pep:`420` style namespace packages.  See the
    corresponding flag :option:`--no-namespace-packages <mypy --no-namespace-packages>`
    for more information.

    This option may only be set in the global section (``[mypy]``).

.. confval:: explicit_package_bases

    :type: boolean
    :default: False

    This flag tells mypy that top-level packages will be based in either the
    current directory, or a member of the ``MYPYPATH`` environment variable or
    :confval:`mypy_path` config option. This option is only useful in
    the absence of `__init__.py`. See :ref:`Mapping file
    paths to modules <mapping-paths-to-modules>` for details.

    This option may only be set in the global section (``[mypy]``).

.. confval:: ignore_missing_imports

    :type: boolean
    :default: False

    Suppresses error messages about imports that cannot be resolved.

    If this option is used in a per-module section, the module name should
    match the name of the *imported* module, not the module containing the
    import statement.

.. confval:: follow_untyped_imports

    :type: boolean
    :default: False

    Makes mypy analyze imports from installed packages even if missing a
    :ref:`py.typed marker or stubs <installed-packages>`.

    If this option is used in a per-module section, the module name should
    match the name of the *imported* module, not the module containing the
    import statement.

    .. warning::

        Note that analyzing all unannotated modules might result in issues
        when analyzing code not designed to be type checked and may significantly
        increase how long mypy takes to run.

.. confval:: follow_imports

    :type: string
    :default: ``normal``

    Directs what to do with imports when the imported module is found
    as a ``.py`` file and not part of the files, modules and packages
    provided on the command line.

    The four possible values are ``normal``, ``silent``, ``skip`` and
    ``error``.  For explanations see the discussion for the
    :option:`--follow-imports <mypy --follow-imports>` command line flag.

    Using this option in a per-module section (potentially with a wildcard,
    as described at the top of this page) is a good way to prevent mypy from
    checking portions of your code.

    If this option is used in a per-module section, the module name should
    match the name of the *imported* module, not the module containing the
    import statement.

.. confval:: follow_imports_for_stubs

    :type: boolean
    :default: False

    Determines whether to respect the :confval:`follow_imports` setting even for
    stub (``.pyi``) files.

    Used in conjunction with :confval:`follow_imports=skip <follow_imports>`, this can be used
    to suppress the import of a module from ``typeshed``, replacing it
    with ``Any``.

    Used in conjunction with :confval:`follow_imports=error <follow_imports>`, this can be used
    to make any use of a particular ``typeshed`` module an error.

    .. note::

         This is not supported by the mypy daemon.

.. confval:: python_executable

    :type: string

    Specifies the path to the Python executable to inspect to collect
    a list of available :ref:`PEP 561 packages <installed-packages>`. User
    home directory and environment variables will be expanded. Defaults to
    the executable used to run mypy.

    This option may only be set in the global section (``[mypy]``).

.. confval:: no_site_packages

    :type: boolean
    :default: False

    Disables using type information in installed packages (see :pep:`561`).
    This will also disable searching for a usable Python executable. This acts
    the same as :option:`--no-site-packages <mypy --no-site-packages>` command
    line flag.

.. confval:: no_silence_site_packages

    :type: boolean
    :default: False

    Enables reporting error messages generated within installed packages (see
    :pep:`561` for more details on distributing type information). Those error
    messages are suppressed by default, since you are usually not able to
    control errors in 3rd party code.

    This option may only be set in the global section (``[mypy]``).


Platform configuration
**********************

.. confval:: python_version

    :type: string

    Specifies the Python version used to parse and check the target
    program.  The string should be in the format ``MAJOR.MINOR`` --
    for example ``3.9``.  The default is the version of the Python
    interpreter used to run mypy.

    This option may only be set in the global section (``[mypy]``).

.. confval:: platform

    :type: string

    Specifies the OS platform for the target program, for example
    ``darwin`` or ``win32`` (meaning OS X or Windows, respectively).
    The default is the current platform as revealed by Python's
    :py:data:`sys.platform` variable.

    This option may only be set in the global section (``[mypy]``).

.. confval:: always_true

    :type: comma-separated list of strings

    Specifies a list of variables that mypy will treat as
    compile-time constants that are always true.

.. confval:: always_false

    :type: comma-separated list of strings

    Specifies a list of variables that mypy will treat as
    compile-time constants that are always false.


Disallow dynamic typing
***********************

For more information, see the :ref:`Disallow dynamic typing <disallow-dynamic-typing>`
section of the command line docs.

.. confval:: disallow_any_unimported

    :type: boolean
    :default: False

    Disallows usage of types that come from unfollowed imports (anything imported from
    an unfollowed import is automatically given a type of ``Any``).

.. confval:: disallow_any_expr

    :type: boolean
    :default: False

    Disallows all expressions in the module that have type ``Any``.

.. confval:: disallow_any_decorated

    :type: boolean
    :default: False

    Disallows functions that have ``Any`` in their signature after decorator transformation.

.. confval:: disallow_any_explicit

    :type: boolean
    :default: False

    Disallows explicit ``Any`` in type positions such as type annotations and generic
    type parameters.

.. confval:: disallow_any_generics

    :type: boolean
    :default: False

    Disallows usage of generic types that do not specify explicit type parameters.

.. confval:: disallow_subclassing_any

    :type: boolean
    :default: False

    Disallows subclassing a value of type ``Any``.


Untyped definitions and calls
*****************************

For more information, see the :ref:`Untyped definitions and calls <untyped-definitions-and-calls>`
section of the command line docs.

.. confval:: disallow_untyped_calls

    :type: boolean
    :default: False

    Disallows calling functions without type annotations from functions with type
    annotations. Note that when used in per-module options, it enables/disables
    this check **inside** the module(s) specified, not for functions that come
    from that module(s), for example config like this:

    .. code-block:: ini

        [mypy]
        disallow_untyped_calls = True

        [mypy-some.library.*]
        disallow_untyped_calls = False

    will disable this check inside ``some.library``, not for your code that
    imports ``some.library``. If you want to selectively disable this check for
    all your code that imports ``some.library`` you should instead use
    :confval:`untyped_calls_exclude`, for example:

    .. code-block:: ini

        [mypy]
        disallow_untyped_calls = True
        untyped_calls_exclude = some.library

.. confval:: untyped_calls_exclude

    :type: comma-separated list of strings

    Selectively excludes functions and methods defined in specific packages,
    modules, and classes from action of :confval:`disallow_untyped_calls`.
    This also applies to all submodules of packages (i.e. everything inside
    a given prefix). Note, this option does not support per-file configuration,
    the exclusions list is defined globally for all your code.

.. confval:: disallow_untyped_defs

    :type: boolean
    :default: False

    Disallows defining functions without type annotations or with incomplete type
    annotations (a superset of :confval:`disallow_incomplete_defs`).

    For example, it would report an error for :code:`def f(a, b)` and :code:`def f(a: int, b)`.

.. confval:: disallow_incomplete_defs

    :type: boolean
    :default: False

    Disallows defining functions with incomplete type annotations, while still
    allowing entirely unannotated definitions.

    For example, it would report an error for :code:`def f(a: int, b)` but not :code:`def f(a, b)`.

.. confval:: check_untyped_defs

    :type: boolean
    :default: False

    Type-checks the interior of functions without type annotations.

.. confval:: disallow_untyped_decorators

    :type: boolean
    :default: False

    Reports an error whenever a function with type annotations is decorated with a
    decorator without annotations.


.. _config-file-none-and-optional-handling:

None and Optional handling
**************************

For more information, see the :ref:`None and Optional handling <none-and-optional-handling>`
section of the command line docs.

.. confval:: implicit_optional

    :type: boolean
    :default: False

    Causes mypy to treat parameters with a ``None``
    default value as having an implicit optional type (``T | None``).

    **Note:** This was True by default in mypy versions 0.980 and earlier.

.. confval:: strict_optional

    :type: boolean
    :default: True

    Effectively disables checking of optional
    types and ``None`` values. With this option, mypy doesn't
    generally check the use of ``None`` values -- it is treated
    as compatible with every type.

    .. warning::

        ``strict_optional = false`` is evil. Avoid using it and definitely do
        not use it without understanding what it does.


Configuring warnings
********************

For more information, see the :ref:`Configuring warnings <configuring-warnings>`
section of the command line docs.

.. confval:: warn_redundant_casts

    :type: boolean
    :default: False

    Warns about casting an expression to its inferred type.

    This option may only be set in the global section (``[mypy]``).

.. confval:: warn_unused_ignores

    :type: boolean
    :default: False

    Warns about unneeded ``# type: ignore`` comments.

.. confval:: warn_no_return

    :type: boolean
    :default: True

    Shows errors for missing return statements on some execution paths.

.. confval:: warn_return_any

    :type: boolean
    :default: False

    Shows a warning when returning a value with type ``Any`` from a function
    declared with a non- ``Any`` return type.

.. confval:: warn_unreachable

    :type: boolean
    :default: False

    Shows a warning when encountering any code inferred to be unreachable or
    redundant after performing type analysis.

.. confval:: deprecated_calls_exclude

    :type: comma-separated list of strings

    Selectively excludes functions and methods defined in specific packages,
    modules, and classes from the :ref:`deprecated<code-deprecated>` error code.
    This also applies to all submodules of packages (i.e. everything inside
    a given prefix). Note, this option does not support per-file configuration,
    the exclusions list is defined globally for all your code.


Suppressing errors
******************

Note: these configuration options are available in the config file only. There is
no analog available via the command line options.

.. confval:: ignore_errors

    :type: boolean
    :default: False

    Ignores all non-fatal errors.


Miscellaneous strictness flags
******************************

For more information, see the :ref:`Miscellaneous strictness flags <miscellaneous-strictness-flags>`
section of the command line docs.

.. confval:: allow_untyped_globals

    :type: boolean
    :default: False

    Causes mypy to suppress errors caused by not being able to fully
    infer the types of global and class variables.

.. confval:: allow_redefinition_new

    :type: boolean
    :default: False

    By default, mypy won't allow a variable to be redefined with an
    unrelated type. This *experimental* flag enables the redefinition of
    unannotated variables with an arbitrary type. You will also need to enable
    :confval:`local_partial_types`.
    Example:

    .. code-block:: python

        def maybe_convert(n: int, b: bool) -> int | str:
            if b:
                x = str(n)  # Assign "str"
            else:
                x = n       # Assign "int"
            # Type of "x" is "int | str" here.
            return x

    This also enables an unannotated variable to have different types in different
    code locations:

    .. code-block:: python

        if check():
            for x in range(n):
                # Type of "x" is "int" here.
                ...
        else:
            for x in ['a', 'b']:
                # Type of "x" is "str" here.
                ...

    Note: We are planning to turn this flag on by default in a future mypy
    release, along with :confval:`local_partial_types`.

.. confval:: allow_redefinition

    :type: boolean
    :default: False

    Allows variables to be redefined with an arbitrary type, as long as the redefinition
    is in the same block and nesting level as the original definition.
    Example where this can be useful:

    .. code-block:: python

       def process(items: list[str]) -> None:
           # 'items' has type list[str]
           items = [item.split() for item in items]
           # 'items' now has type list[list[str]]

    The variable must be used before it can be redefined:

    .. code-block:: python

        def process(items: list[str]) -> None:
           items = "mypy"  # invalid redefinition to str because the variable hasn't been used yet
           print(items)
           items = "100"  # valid, items now has type str
           items = int(items)  # valid, items now has type int

.. confval:: local_partial_types

    :type: boolean
    :default: False

    Disallows inferring variable type for ``None`` from two assignments in different scopes.
    This is always implicitly enabled when using the :ref:`mypy daemon <mypy_daemon>`.
    This will be enabled by default in a future mypy release.

.. confval:: disable_error_code

    :type: comma-separated list of strings

    Allows disabling one or multiple error codes globally.

.. confval:: enable_error_code

    :type: comma-separated list of strings

    Allows enabling one or multiple error codes globally.

    Note: This option will override disabled error codes from the disable_error_code option.

.. confval:: extra_checks

   :type: boolean
   :default: False

   This flag enables additional checks that are technically correct but may be impractical.
   See :option:`mypy --extra-checks` for more info.

.. confval:: implicit_reexport

    :type: boolean
    :default: True

    By default, imported values to a module are treated as exported and mypy allows
    other modules to import them. When false, mypy will not re-export unless
    the item is imported using from-as or is included in ``__all__``. Note that mypy
    treats stub files as if this is always disabled. For example:

    .. code-block:: python

       # This won't re-export the value
       from foo import bar
       # This will re-export it as bar and allow other modules to import it
       from foo import bar as bar
       # This will also re-export bar
       from foo import bar
       __all__ = ['bar']

.. confval:: strict_equality

   :type: boolean
   :default: False

   Prohibit equality checks, identity checks, and container checks between
   non-overlapping types.

.. confval:: strict_bytes

   :type: boolean
   :default: False

   Disable treating ``bytearray`` and ``memoryview`` as subtypes of ``bytes``.
   This will be enabled by default in *mypy 2.0*.

.. confval:: strict

   :type: boolean
   :default: False

   Enable all optional error checking flags.  You can see the list of
   flags enabled by strict mode in the full :option:`mypy --help`
   output.

   Note: the exact list of flags enabled by :confval:`strict` may
   change over time.


Configuring error messages
**************************

For more information, see the :ref:`Configuring error messages <configuring-error-messages>`
section of the command line docs.

These options may only be set in the global section (``[mypy]``).

.. confval:: show_error_context

    :type: boolean
    :default: False

    Prefixes each error with the relevant context.

.. confval:: show_column_numbers

    :type: boolean
    :default: False

    Shows column numbers in error messages.

.. confval:: show_error_code_links

    :type: boolean
    :default: False

    Shows documentation link to corresponding error code.

.. confval:: hide_error_codes

    :type: boolean
    :default: False

    Hides error codes in error messages. See :ref:`error-codes` for more information.

.. confval:: pretty

    :type: boolean
    :default: False

    Use visually nicer output in error messages: use soft word wrap,
    show source code snippets, and show error location markers.

.. confval:: color_output

    :type: boolean
    :default: True

    Shows error messages with color enabled.

.. confval:: error_summary

    :type: boolean
    :default: True

    Shows a short summary line after error messages.

.. confval:: show_absolute_path

    :type: boolean
    :default: False

    Show absolute paths to files.

.. confval:: force_union_syntax

    :type: boolean
    :default: False

    Always use ``Union[]`` and ``Optional[]`` for union types
    in error messages (instead of the ``|`` operator),
    even on Python 3.10+.

Incremental mode
****************

These options may only be set in the global section (``[mypy]``).

.. confval:: incremental

    :type: boolean
    :default: True

    Enables :ref:`incremental mode <incremental>`.

.. confval:: cache_dir

    :type: string
    :default: ``.mypy_cache``

    Specifies the location where mypy stores incremental cache info.
    User home directory and environment variables will be expanded.
    This setting will be overridden by the ``MYPY_CACHE_DIR`` environment
    variable.

    Note that the cache is only read when incremental mode is enabled
    but is always written to, unless the value is set to ``/dev/null``
    (UNIX) or ``nul`` (Windows).

.. confval:: sqlite_cache

    :type: boolean
    :default: False

    Use an `SQLite`_ database to store the cache.

.. confval:: cache_fine_grained

    :type: boolean
    :default: False

    Include fine-grained dependency information in the cache for the mypy daemon.

.. confval:: skip_version_check

    :type: boolean
    :default: False

    Makes mypy use incremental cache data even if it was generated by a
    different version of mypy. (By default, mypy will perform a version
    check and regenerate the cache if it was written by older versions of mypy.)

.. confval:: skip_cache_mtime_checks

    :type: boolean
    :default: False

    Skip cache internal consistency checks based on mtime.


Advanced options
****************

These options may only be set in the global section (``[mypy]``).

.. confval:: plugins

    :type: comma-separated list of strings

    A comma-separated list of mypy plugins. See :ref:`extending-mypy-using-plugins`.

.. confval:: pdb

    :type: boolean
    :default: False

    Invokes :mod:`pdb` on fatal error.

.. confval:: show_traceback

    :type: boolean
    :default: False

    Shows traceback on fatal error.

.. confval:: raise_exceptions

    :type: boolean
    :default: False

    Raise exception on fatal error.

.. confval:: custom_typing_module

    :type: string

    Specifies a custom module to use as a substitute for the :py:mod:`typing` module.

.. confval:: custom_typeshed_dir

    :type: string

    This specifies the directory where mypy looks for standard library typeshed
    stubs, instead of the typeshed that ships with mypy.  This is
    primarily intended to make it easier to test typeshed changes before
    submitting them upstream, but also allows you to use a forked version of
    typeshed.

    User home directory and environment variables will be expanded.

    Note that this doesn't affect third-party library stubs. To test third-party stubs,
    for example try ``MYPYPATH=stubs/six mypy ...``.

.. confval:: warn_incomplete_stub

    :type: boolean
    :default: False

    Warns about missing type annotations in typeshed.  This is only relevant
    in combination with :confval:`disallow_untyped_defs` or :confval:`disallow_incomplete_defs`.


Report generation
*****************

If these options are set, mypy will generate a report in the specified
format into the specified directory.

.. warning::

  Generating reports disables incremental mode and can significantly slow down
  your workflow. It is recommended to enable reporting only for specific runs
  (e.g. in CI).

.. confval:: any_exprs_report

    :type: string

    Causes mypy to generate a text file report documenting how many
    expressions of type ``Any`` are present within your codebase.

.. confval:: cobertura_xml_report

    :type: string

    Causes mypy to generate a Cobertura XML type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.

.. confval:: html_report / xslt_html_report

    :type: string

    Causes mypy to generate an HTML type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.

.. confval:: linecount_report

    :type: string

    Causes mypy to generate a text file report documenting the functions
    and lines that are typed and untyped within your codebase.

.. confval:: linecoverage_report

    :type: string

    Causes mypy to generate a JSON file that maps each source file's
    absolute filename to a list of line numbers that belong to typed
    functions in that file.

.. confval:: lineprecision_report

    :type: string

    Causes mypy to generate a flat text file report with per-module
    statistics of how many lines are typechecked etc.

.. confval:: txt_report / xslt_txt_report

    :type: string

    Causes mypy to generate a text file type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.

.. confval:: xml_report

    :type: string

    Causes mypy to generate an XML type checking coverage report.

    To generate this report, you must either manually install the `lxml`_
    library or specify mypy installation with the setuptools extra
    ``mypy[reports]``.


Miscellaneous
*************

These options may only be set in the global section (``[mypy]``).

.. confval:: junit_xml

    :type: string

    Causes mypy to generate a JUnit XML test result document with
    type checking results. This can make it easier to integrate mypy
    with continuous integration (CI) tools.

.. confval:: scripts_are_modules

    :type: boolean
    :default: False

    Makes script ``x`` become module ``x`` instead of ``__main__``.  This is
    useful when checking multiple scripts in a single run.

.. confval:: warn_unused_configs

    :type: boolean
    :default: False

    Warns about per-module sections in the config file that do not
    match any files processed when invoking mypy.
    (This requires turning off incremental mode using :confval:`incremental = False <incremental>`.)

.. confval:: verbosity

    :type: integer
    :default: 0

    Controls how much debug output will be generated.  Higher numbers are more verbose.


.. _using-a-pyproject-toml:

Using a pyproject.toml file
***************************

Instead of using a ``mypy.ini`` file, a ``pyproject.toml`` file (as specified by
`PEP 518`_) may be used instead. A few notes on doing so:

* The ``[mypy]`` section should have ``tool.`` prepended to its name:

  * I.e., ``[mypy]`` would become ``[tool.mypy]``

* The module specific sections should be moved into ``[[tool.mypy.overrides]]`` sections:

  * For example, ``[mypy-packagename]`` would become:

.. code-block:: toml

  [[tool.mypy.overrides]]
  module = 'packagename'
  ...

* Multi-module specific sections can be moved into a single ``[[tool.mypy.overrides]]`` section with a
  module property set to an array of modules:

  * For example, ``[mypy-packagename,packagename2]`` would become:

.. code-block:: toml

  [[tool.mypy.overrides]]
  module = [
      'packagename',
      'packagename2'
  ]
  ...

* The following care should be given to values in the ``pyproject.toml`` files as compared to ``ini`` files:

  * Strings must be wrapped in double quotes, or single quotes if the string contains special characters

  * Boolean values should be all lower case

Please see the `TOML Documentation`_ for more details and information on
what is allowed in a ``toml`` file. See `PEP 518`_ for more information on the layout
and structure of the ``pyproject.toml`` file.

Example ``pyproject.toml``
**************************

Here is an example of a ``pyproject.toml`` file. To use this config file, place it at the root
of your repo (or append it to the end of an existing ``pyproject.toml`` file) and run mypy.

.. code-block:: toml

    # mypy global options:

    [tool.mypy]
    python_version = "3.9"
    warn_return_any = true
    warn_unused_configs = true
    exclude = [
        '^file1\.py$',  # TOML literal string (single-quotes, no escaping necessary)
        "^file2\\.py$",  # TOML basic string (double-quotes, backslash and other characters need escaping)
    ]

    # mypy per-module options:

    [[tool.mypy.overrides]]
    module = "mycode.foo.*"
    disallow_untyped_defs = true

    [[tool.mypy.overrides]]
    module = "mycode.bar"
    warn_return_any = false

    [[tool.mypy.overrides]]
    module = [
        "somelibrary",
        "some_other_library"
    ]
    ignore_missing_imports = true

.. _lxml: https://pypi.org/project/lxml/
.. _SQLite: https://www.sqlite.org/
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _TOML Documentation: https://toml.io/
````

## File: docs/source/duck_type_compatibility.rst
````
Duck type compatibility
-----------------------

In Python, certain types are compatible even though they aren't subclasses of
each other. For example, ``int`` objects are valid whenever ``float`` objects
are expected. Mypy supports this idiom via *duck type compatibility*. This is
supported for a small set of built-in types:

* ``int`` is duck type compatible with ``float`` and ``complex``.
* ``float`` is duck type compatible with ``complex``.
* ``bytearray`` and ``memoryview`` are duck type compatible with ``bytes``.

For example, mypy considers an ``int`` object to be valid whenever a
``float`` object is expected.  Thus code like this is nice and clean
and also behaves as expected:

.. code-block:: python

   import math

   def degrees_to_radians(degrees: float) -> float:
       return math.pi * degrees / 180

   n = 90  # Inferred type 'int'
   print(degrees_to_radians(n))  # Okay!

You can also often use :ref:`protocol-types` to achieve a similar effect in
a more principled and extensible fashion. Protocols don't apply to
cases like ``int`` being compatible with ``float``, since ``float`` is not
a protocol class but a regular, concrete class, and many standard library
functions expect concrete instances of ``float`` (or ``int``).
````

## File: docs/source/dynamic_typing.rst
````
.. _dynamic-typing:

Dynamically typed code
======================

In :ref:`getting-started-dynamic-vs-static`, we discussed how bodies of functions
that don't have any explicit type annotations in their function are "dynamically typed"
and that mypy will not check them. In this section, we'll talk a little bit more
about what that means and how you can enable dynamic typing on a more fine grained basis.

In cases where your code is too magical for mypy to understand, you can make a
variable or parameter dynamically typed by explicitly giving it the type
``Any``. Mypy will let you do basically anything with a value of type ``Any``,
including assigning a value of type ``Any`` to a variable of any type (or vice
versa).

.. code-block:: python

   from typing import Any

   num = 1         # Statically typed (inferred to be int)
   num = 'x'       # error: Incompatible types in assignment (expression has type "str", variable has type "int")

   dyn: Any = 1    # Dynamically typed (type Any)
   dyn = 'x'       # OK

   num = dyn       # No error, mypy will let you assign a value of type Any to any variable
   num += 1        # Oops, mypy still thinks num is an int

You can think of ``Any`` as a way to locally disable type checking.
See :ref:`silencing-type-errors` for other ways you can shut up
the type checker.

Operations on Any values
------------------------

You can do anything using a value with type ``Any``, and the type checker
will not complain:

.. code-block:: python

    def f(x: Any) -> int:
        # All of these are valid!
        x.foobar(1, y=2)
        print(x[3] + 'f')
        if x:
            x.z = x(2)
        open(x).read()
        return x

Values derived from an ``Any`` value also usually have the type ``Any``
implicitly, as mypy can't infer a more precise result type. For
example, if you get the attribute of an ``Any`` value or call a
``Any`` value the result is ``Any``:

.. code-block:: python

    def f(x: Any) -> None:
        y = x.foo()
        reveal_type(y)  # Revealed type is "Any"
        z = y.bar("mypy will let you do anything to y")
        reveal_type(z)  # Revealed type is "Any"

``Any`` types may propagate through your program, making type checking
less effective, unless you are careful.

Function parameters without annotations are also implicitly ``Any``:

.. code-block:: python

    def f(x) -> None:
        reveal_type(x)  # Revealed type is "Any"
        x.can.do["anything", x]("wants", 2)

You can make mypy warn you about untyped function parameters using the
:option:`--disallow-untyped-defs <mypy --disallow-untyped-defs>` flag.

Generic types missing type parameters will have those parameters implicitly
treated as ``Any``:

.. code-block:: python

    def f(x: list) -> None:
        reveal_type(x)        # Revealed type is "builtins.list[Any]"
        reveal_type(x[0])     # Revealed type is "Any"
        x[0].anything_goes()  # OK

You can make mypy warn you about missing generic parameters using the
:option:`--disallow-any-generics <mypy --disallow-any-generics>` flag.

Finally, another major source of ``Any`` types leaking into your program is from
third party libraries that mypy does not know about. This is particularly the case
when using the :option:`--ignore-missing-imports <mypy --ignore-missing-imports>`
flag. See :ref:`fix-missing-imports` for more information about this.

.. _any-vs-object:

Any vs. object
--------------

The type :py:class:`object` is another type that can have an instance of arbitrary
type as a value. Unlike ``Any``, :py:class:`object` is an ordinary static type (it
is similar to ``Object`` in Java), and only operations valid for *all*
types are accepted for :py:class:`object` values. These are all valid:

.. code-block:: python

    def f(o: object) -> None:
        if o:
            print(o)
        print(isinstance(o, int))
        o = 2
        o = 'foo'

These are, however, flagged as errors, since not all objects support these
operations:

.. code-block:: python

    def f(o: object) -> None:
        o.foo()       # Error!
        o + 2         # Error!
        open(o)       # Error!
        n: int = 1
        n = o         # Error!


If you're not sure whether you need to use :py:class:`object` or ``Any``, use
:py:class:`object` -- only switch to using ``Any`` if you get a type checker
complaint.

You can use different :ref:`type narrowing <type-narrowing>`
techniques to narrow :py:class:`object` to a more specific
type (subtype) such as ``int``. Type narrowing is not needed with
dynamically typed values (values with type ``Any``).
````

## File: docs/source/error_code_list.rst
````
.. _error-code-list:

Error codes enabled by default
==============================

This section documents various errors codes that mypy can generate
with default options. See :ref:`error-codes` for general documentation
about error codes. :ref:`error-codes-optional` documents additional
error codes that you can enable.

.. _code-attr-defined:

Check that attribute exists [attr-defined]
------------------------------------------

Mypy checks that an attribute is defined in the target class or module
when using the dot operator. This applies to both getting and setting
an attribute. New attributes are defined by assignments in the class
body, or assignments to ``self.x`` in methods. These assignments don't
generate ``attr-defined`` errors.

Example:

.. code-block:: python

   class Resource:
       def __init__(self, name: str) -> None:
           self.name = name

   r = Resource('x')
   print(r.name)  # OK
   print(r.id)  # Error: "Resource" has no attribute "id"  [attr-defined]
   r.id = 5  # Error: "Resource" has no attribute "id"  [attr-defined]

This error code is also generated if an imported name is not defined
in the module in a ``from ... import`` statement (as long as the
target module can be found):

.. code-block:: python

    # Error: Module "os" has no attribute "non_existent"  [attr-defined]
    from os import non_existent

A reference to a missing attribute is given the ``Any`` type. In the
above example, the type of ``non_existent`` will be ``Any``, which can
be important if you silence the error.

.. _code-union-attr:

Check that attribute exists in each union item [union-attr]
-----------------------------------------------------------

If you access the attribute of a value with a union type, mypy checks
that the attribute is defined for *every* type in that
union. Otherwise the operation can fail at runtime. This also applies
to optional types.

Example:

.. code-block:: python

   class Cat:
       def sleep(self) -> None: ...
       def miaow(self) -> None: ...

   class Dog:
       def sleep(self) -> None: ...
       def follow_me(self) -> None: ...

   def func(animal: Cat | Dog) -> None:
       # OK: 'sleep' is defined for both Cat and Dog
       animal.sleep()
       # Error: Item "Cat" of "Cat | Dog" has no attribute "follow_me"  [union-attr]
       animal.follow_me()

You can often work around these errors by using ``assert isinstance(obj, ClassName)``
or ``assert obj is not None`` to tell mypy that you know that the type is more specific
than what mypy thinks.

.. _code-name-defined:

Check that name is defined [name-defined]
-----------------------------------------

Mypy expects that all references to names have a corresponding
definition in an active scope, such as an assignment, function
definition or an import. This can catch missing definitions, missing
imports, and typos.

This example accidentally calls ``sort()`` instead of :py:func:`sorted`:

.. code-block:: python

    x = sort([3, 2, 4])  # Error: Name "sort" is not defined  [name-defined]

.. _code-used-before-def:

Check that a variable is not used before it's defined [used-before-def]
-----------------------------------------------------------------------

Mypy will generate an error if a name is used before it's defined.
While the name-defined check will catch issues with names that are undefined,
it will not flag if a variable is used and then defined later in the scope.
used-before-def check will catch such cases.

Example:

.. code-block:: python

    print(x)  # Error: Name "x" is used before definition [used-before-def]
    x = 123

.. _code-call-arg:

Check arguments in calls [call-arg]
-----------------------------------

Mypy expects that the number and names of arguments match the called function.
Note that argument type checks have a separate error code ``arg-type``.

Example:

.. code-block:: python

    def greet(name: str) -> None:
         print('hello', name)

    greet('jack')  # OK
    greet('jill', 'jack')  # Error: Too many arguments for "greet"  [call-arg]

.. _code-arg-type:

Check argument types [arg-type]
-------------------------------

Mypy checks that argument types in a call match the declared argument
types in the signature of the called function (if one exists).

Example:

.. code-block:: python

    def first(x: list[int]) -> int:
        return x[0] if x else 0

    t = (5, 4)
    # Error: Argument 1 to "first" has incompatible type "tuple[int, int]";
    #        expected "list[int]"  [arg-type]
    print(first(t))

.. _code-call-overload:

Check calls to overloaded functions [call-overload]
---------------------------------------------------

When you call an overloaded function, mypy checks that at least one of
the signatures of the overload items match the argument types in the
call.

Example:

.. code-block:: python

   from typing import overload

   @overload
   def inc_maybe(x: None) -> None: ...

   @overload
   def inc_maybe(x: int) -> int: ...

   def inc_maybe(x: int | None) -> int | None:
        if x is None:
            return None
        else:
            return x + 1

   inc_maybe(None)  # OK
   inc_maybe(5)  # OK

   # Error: No overload variant of "inc_maybe" matches argument type "float"  [call-overload]
   inc_maybe(1.2)

.. _code-valid-type:

Check validity of types [valid-type]
------------------------------------

Mypy checks that each type annotation and any expression that
represents a type is a valid type. Examples of valid types include
classes, union types, callable types, type aliases, and literal types.
Examples of invalid types include bare integer literals, functions,
variables, and modules.

This example incorrectly uses the function ``log`` as a type:

.. code-block:: python

    def log(x: object) -> None:
        print('log:', repr(x))

    # Error: Function "t.log" is not valid as a type  [valid-type]
    def log_all(objs: list[object], f: log) -> None:
        for x in objs:
            f(x)

You can use :py:class:`~collections.abc.Callable` as the type for callable objects:

.. code-block:: python

    from collections.abc import Callable

    # OK
    def log_all(objs: list[object], f: Callable[[object], None]) -> None:
        for x in objs:
            f(x)

.. _code-metaclass:

Check the validity of a class's metaclass [metaclass]
-----------------------------------------------------

Mypy checks whether the metaclass of a class is valid. The metaclass
must be a subclass of ``type``. Further, the class hierarchy must yield
a consistent metaclass. For more details, see the
`Python documentation <https://docs.python.org/3.13/reference/datamodel.html#determining-the-appropriate-metaclass>`_

Note that mypy's metaclass checking is limited and may produce false-positives.
See also :ref:`limitations`.

Example with an error:

.. code-block:: python

    class GoodMeta(type):
        pass

    class BadMeta:
        pass

    class A1(metaclass=GoodMeta):  # OK
        pass

    class A2(metaclass=BadMeta):  # Error:  Metaclasses not inheriting from "type" are not supported  [metaclass]
        pass

.. _code-var-annotated:

Require annotation if variable type is unclear [var-annotated]
--------------------------------------------------------------

In some cases mypy can't infer the type of a variable without an
explicit annotation. Mypy treats this as an error. This typically
happens when you initialize a variable with an empty collection or
``None``.  If mypy can't infer the collection item type, mypy replaces
any parts of the type it couldn't infer with ``Any`` and generates an
error.

Example with an error:

.. code-block:: python

    class Bundle:
        def __init__(self) -> None:
            # Error: Need type annotation for "items"
            #        (hint: "items: list[<type>] = ...")  [var-annotated]
            self.items = []

    reveal_type(Bundle().items)  # list[Any]

To address this, we add an explicit annotation:

.. code-block:: python

    class Bundle:
        def __init__(self) -> None:
            self.items: list[str] = []  # OK

   reveal_type(Bundle().items)  # list[str]

.. _code-override:

Check validity of overrides [override]
--------------------------------------

Mypy checks that an overridden method or attribute is compatible with
the base class.  A method in a subclass must accept all arguments
that the base class method accepts, and the return type must conform
to the return type in the base class (Liskov substitution principle).

Argument types can be more general is a subclass (i.e., they can vary
contravariantly).  The return type can be narrowed in a subclass
(i.e., it can vary covariantly).  It's okay to define additional
arguments in a subclass method, as long all extra arguments have default
values or can be left out (``*args``, for example).

Example:

.. code-block:: python

   class Base:
       def method(self,
                  arg: int) -> int | None:
           ...

   class Derived(Base):
       def method(self,
                  arg: int | str) -> int:  # OK
           ...

   class DerivedBad(Base):
       # Error: Argument 1 of "method" is incompatible with "Base"  [override]
       def method(self,
                  arg: bool) -> int:
           ...

.. _code-return:

Check that function returns a value [return]
--------------------------------------------

If a function has a non-``None`` return type, mypy expects that the
function always explicitly returns a value (or raises an exception).
The function should not fall off the end of the function, since this
is often a bug.

Example:

.. code-block:: python

    # Error: Missing return statement  [return]
    def show(x: int) -> int:
        print(x)

    # Error: Missing return statement  [return]
    def pred1(x: int) -> int:
        if x > 0:
            return x - 1

    # OK
    def pred2(x: int) -> int:
        if x > 0:
            return x - 1
        else:
            raise ValueError('not defined for zero')

.. _code-empty-body:

Check that functions don't have empty bodies outside stubs [empty-body]
-----------------------------------------------------------------------

This error code is similar to the ``[return]`` code but is emitted specifically
for functions and methods with empty bodies (if they are annotated with
non-trivial return type). Such a distinction exists because in some contexts
an empty body can be valid, for example for an abstract method or in a stub
file. Also old versions of mypy used to unconditionally allow functions with
empty bodies, so having a dedicated error code simplifies cross-version
compatibility.

Note that empty bodies are allowed for methods in *protocols*, and such methods
are considered implicitly abstract:

.. code-block:: python

   from abc import abstractmethod
   from typing import Protocol

   class RegularABC:
       @abstractmethod
       def foo(self) -> int:
           pass  # OK
       def bar(self) -> int:
           pass  # Error: Missing return statement  [empty-body]

   class Proto(Protocol):
       def bar(self) -> int:
           pass  # OK

.. _code-return-value:

Check that return value is compatible [return-value]
----------------------------------------------------

Mypy checks that the returned value is compatible with the type
signature of the function.

Example:

.. code-block:: python

   def func(x: int) -> str:
       # Error: Incompatible return value type (got "int", expected "str")  [return-value]
       return x + 1

.. _code-assignment:

Check types in assignment statement [assignment]
------------------------------------------------

Mypy checks that the assigned expression is compatible with the
assignment target (or targets).

Example:

.. code-block:: python

    class Resource:
        def __init__(self, name: str) -> None:
            self.name = name

    r = Resource('A')

    r.name = 'B'  # OK

    # Error: Incompatible types in assignment (expression has type "int",
    #        variable has type "str")  [assignment]
    r.name = 5

.. _code-method-assign:

Check that assignment target is not a method [method-assign]
------------------------------------------------------------

In general, assigning to a method on class object or instance (a.k.a.
monkey-patching) is ambiguous in terms of types, since Python's static type
system cannot express the difference between bound and unbound callable types.
Consider this example:

.. code-block:: python

   class A:
       def f(self) -> None: pass
       def g(self) -> None: pass

   def h(self: A) -> None: pass

   A.f = h  # Type of h is Callable[[A], None]
   A().f()  # This works
   A.f = A().g  # Type of A().g is Callable[[], None]
   A().f()  # ...but this also works at runtime

To prevent the ambiguity, mypy will flag both assignments by default. If this
error code is disabled, mypy will treat the assigned value in all method assignments as unbound,
so only the second assignment will still generate an error.

.. note::

    This error code is a subcode of the more general ``[assignment]`` code.

.. _code-type-var:

Check type variable values [type-var]
-------------------------------------

Mypy checks that value of a type variable is compatible with a value
restriction or the upper bound type.

Example (Python 3.12 syntax):

.. code-block:: python

    def add[T1: (int, float)](x: T1, y: T1) -> T1:
        return x + y

    add(4, 5.5)  # OK

    # Error: Value of type variable "T1" of "add" cannot be "str"  [type-var]
    add('x', 'y')

.. _code-operator:

Check uses of various operators [operator]
------------------------------------------

Mypy checks that operands support a binary or unary operation, such as
``+`` or ``~``. Indexing operations are so common that they have their
own error code ``index`` (see below).

Example:

.. code-block:: python

   # Error: Unsupported operand types for + ("int" and "str")  [operator]
   1 + 'x'

.. _code-index:

Check indexing operations [index]
---------------------------------

Mypy checks that the indexed value in indexing operation such as
``x[y]`` supports indexing, and that the index expression has a valid
type.

Example:

.. code-block:: python

   a = {'x': 1, 'y': 2}

   a['x']  # OK

   # Error: Invalid index type "int" for "dict[str, int]"; expected type "str"  [index]
   print(a[1])

   # Error: Invalid index type "bytes" for "dict[str, int]"; expected type "str"  [index]
   a[b'x'] = 4

.. _code-list-item:

Check list items [list-item]
----------------------------

When constructing a list using ``[item, ...]``, mypy checks that each item
is compatible with the list type that is inferred from the surrounding
context.

Example:

.. code-block:: python

    # Error: List item 0 has incompatible type "int"; expected "str"  [list-item]
    a: list[str] = [0]

.. _code-dict-item:

Check dict items [dict-item]
----------------------------

When constructing a dictionary using ``{key: value, ...}`` or ``dict(key=value, ...)``,
mypy checks that each key and value is compatible with the dictionary type that is
inferred from the surrounding context.

Example:

.. code-block:: python

    # Error: Dict entry 0 has incompatible type "str": "str"; expected "str": "int"  [dict-item]
    d: dict[str, int] = {'key': 'value'}

.. _code-typeddict-item:

Check TypedDict items [typeddict-item]
--------------------------------------

When constructing a TypedDict object, mypy checks that each key and value is compatible
with the TypedDict type that is inferred from the surrounding context.

When getting a TypedDict item, mypy checks that the key
exists. When assigning to a TypedDict, mypy checks that both the
key and the value are valid.

Example:

.. code-block:: python

    from typing import TypedDict

    class Point(TypedDict):
        x: int
        y: int

    # Error: Incompatible types (expression has type "float",
    #        TypedDict item "x" has type "int")  [typeddict-item]
    p: Point = {'x': 1.2, 'y': 4}

.. _code-typeddict-unknown-key:

Check TypedDict Keys [typeddict-unknown-key]
--------------------------------------------

When constructing a TypedDict object, mypy checks whether the
definition contains unknown keys, to catch invalid keys and
misspellings. On the other hand, mypy will not generate an error when
a previously constructed TypedDict value with extra keys is passed
to a function as an argument, since TypedDict values support
structural subtyping ("static duck typing") and the keys are assumed
to have been validated at the point of construction. Example:

.. code-block:: python

    from typing import TypedDict

    class Point(TypedDict):
        x: int
        y: int

    class Point3D(Point):
        z: int

    def add_x_coordinates(a: Point, b: Point) -> int:
        return a["x"] + b["x"]

    a: Point = {"x": 1, "y": 4}
    b: Point3D = {"x": 2, "y": 5, "z": 6}

    add_x_coordinates(a, b)  # OK

    # Error: Extra key "z" for TypedDict "Point"  [typeddict-unknown-key]
    add_x_coordinates(a, {"x": 1, "y": 4, "z": 5})

Setting a TypedDict item using an unknown key will also generate this
error, since it could be a misspelling:

.. code-block:: python

    a: Point = {"x": 1, "y": 2}
    # Error: Extra key "z" for TypedDict "Point"  [typeddict-unknown-key]
    a["z"] = 3

Reading an unknown key will generate the more general (and serious)
``typeddict-item`` error, which is likely to result in an exception at
runtime:

.. code-block:: python

    a: Point = {"x": 1, "y": 2}
    # Error: TypedDict "Point" has no key "z"  [typeddict-item]
    _ = a["z"]

.. note::

    This error code is a subcode of the wider ``[typeddict-item]`` code.

.. _code-has-type:

Check that type of target is known [has-type]
---------------------------------------------

Mypy sometimes generates an error when it hasn't inferred any type for
a variable being referenced. This can happen for references to
variables that are initialized later in the source file, and for
references across modules that form an import cycle. When this
happens, the reference gets an implicit ``Any`` type.

In this example the definitions of ``x`` and ``y`` are circular:

.. code-block:: python

   class Problem:
       def set_x(self) -> None:
           # Error: Cannot determine type of "y"  [has-type]
           self.x = self.y

       def set_y(self) -> None:
           self.y = self.x

To work around this error, you can add an explicit type annotation to
the target variable or attribute. Sometimes you can also reorganize
the code so that the definition of the variable is placed earlier than
the reference to the variable in a source file. Untangling cyclic
imports may also help.

We add an explicit annotation to the ``y`` attribute to work around
the issue:

.. code-block:: python

   class Problem:
       def set_x(self) -> None:
           self.x = self.y  # OK

       def set_y(self) -> None:
           self.y: int = self.x  # Added annotation here

.. _code-import:

Check for an issue with imports [import]
----------------------------------------

Mypy generates an error if it can't resolve an `import` statement.
This is a parent error code of `import-not-found` and `import-untyped`

See :ref:`ignore-missing-imports` for how to work around these errors.

.. _code-import-not-found:

Check that import target can be found [import-not-found]
--------------------------------------------------------

Mypy generates an error if it can't find the source code or a stub file
for an imported module.

Example:

.. code-block:: python

    # Error: Cannot find implementation or library stub for module named "m0dule_with_typo"  [import-not-found]
    import m0dule_with_typo

See :ref:`ignore-missing-imports` for how to work around these errors.

.. _code-import-untyped:

Check that import target can be found [import-untyped]
--------------------------------------------------------

Mypy generates an error if it can find the source code for an imported module,
but that module does not provide type annotations (via :ref:`PEP 561 <installed-packages>`).

Example:

.. code-block:: python

    # Error: Library stubs not installed for "bs4"  [import-untyped]
    import bs4
    # Error: Skipping analyzing "no_py_typed": module is installed, but missing library stubs or py.typed marker  [import-untyped]
    import no_py_typed

In some cases, these errors can be fixed by installing an appropriate
stub package. See :ref:`ignore-missing-imports` for more details.

.. _code-no-redef:

Check that each name is defined once [no-redef]
-----------------------------------------------

Mypy may generate an error if you have multiple definitions for a name
in the same namespace.  The reason is that this is often an error, as
the second definition may overwrite the first one. Also, mypy often
can't be able to determine whether references point to the first or
the second definition, which would compromise type checking.

If you silence this error, all references to the defined name refer to
the *first* definition.

Example:

.. code-block:: python

   class A:
       def __init__(self, x: int) -> None: ...

   class A:  # Error: Name "A" already defined on line 1  [no-redef]
       def __init__(self, x: str) -> None: ...

   # Error: Argument 1 to "A" has incompatible type "str"; expected "int"
   #        (the first definition wins!)
   A('x')

.. _code-func-returns-value:

Check that called function returns a value [func-returns-value]
---------------------------------------------------------------

Mypy reports an error if you call a function with a ``None``
return type and don't ignore the return value, as this is
usually (but not always) a programming error.

In this example, the ``if f()`` check is always false since ``f``
returns ``None``:

.. code-block:: python

   def f() -> None:
       ...

   # OK: we don't do anything with the return value
   f()

   # Error: "f" does not return a value (it only ever returns None)  [func-returns-value]
   if f():
        print("not false")

.. _code-abstract:

Check instantiation of abstract classes [abstract]
--------------------------------------------------

Mypy generates an error if you try to instantiate an abstract base
class (ABC). An abstract base class is a class with at least one
abstract method or attribute. (See also :py:mod:`abc` module documentation)

Sometimes a class is made accidentally abstract, often due to an
unimplemented abstract method. In a case like this you need to provide
an implementation for the method to make the class concrete
(non-abstract).

Example:

.. code-block:: python

    from abc import ABCMeta, abstractmethod

    class Persistent(metaclass=ABCMeta):
        @abstractmethod
        def save(self) -> None: ...

    class Thing(Persistent):
        def __init__(self) -> None:
            ...

        ...  # No "save" method

    # Error: Cannot instantiate abstract class "Thing" with abstract attribute "save"  [abstract]
    t = Thing()

.. _code-type-abstract:

Safe handling of abstract type object types [type-abstract]
-----------------------------------------------------------

Mypy always allows instantiating (calling) type objects typed as ``type[t]``,
even if it is not known that ``t`` is non-abstract, since it is a common
pattern to create functions that act as object factories (custom constructors).
Therefore, to prevent issues described in the above section, when an abstract
type object is passed where ``type[t]`` is expected, mypy will give an error.
Example (Python 3.12 syntax):

.. code-block:: python

   from abc import ABCMeta, abstractmethod

   class Config(metaclass=ABCMeta):
       @abstractmethod
       def get_value(self, attr: str) -> str: ...

   def make_many[T](typ: type[T], n: int) -> list[T]:
       return [typ() for _ in range(n)]  # This will raise if typ is abstract

   # Error: Only concrete class can be given where "type[Config]" is expected [type-abstract]
   make_many(Config, 5)

.. _code-safe-super:

Check that call to an abstract method via super is valid [safe-super]
---------------------------------------------------------------------

Abstract methods often don't have any default implementation, i.e. their
bodies are just empty. Calling such methods in subclasses via ``super()``
will cause runtime errors, so mypy prevents you from doing so:

.. code-block:: python

   from abc import abstractmethod
   class Base:
       @abstractmethod
       def foo(self) -> int: ...
   class Sub(Base):
       def foo(self) -> int:
           return super().foo() + 1  # error: Call to abstract method "foo" of "Base" with
                                     # trivial body via super() is unsafe  [safe-super]
   Sub().foo()  # This will crash at runtime.

Mypy considers the following as trivial bodies: a ``pass`` statement, a literal
ellipsis ``...``, a docstring, and a ``raise NotImplementedError`` statement.

.. _code-valid-newtype:

Check the target of NewType [valid-newtype]
-------------------------------------------

The target of a :py:class:`~typing.NewType` definition must be a class type. It can't
be a union type, ``Any``, or various other special types.

You can also get this error if the target has been imported from a
module whose source mypy cannot find, since any such definitions are
treated by mypy as values with ``Any`` types. Example:

.. code-block:: python

   from typing import NewType

   # The source for "acme" is not available for mypy
   from acme import Entity  # type: ignore

   # Error: Argument 2 to NewType(...) must be subclassable (got "Any")  [valid-newtype]
   UserEntity = NewType('UserEntity', Entity)

To work around the issue, you can either give mypy access to the sources
for ``acme`` or create a stub file for the module.  See :ref:`ignore-missing-imports`
for more information.

.. _code-exit-return:

Check the return type of __exit__ [exit-return]
-----------------------------------------------

If mypy can determine that :py:meth:`__exit__ <object.__exit__>` always returns ``False``, mypy
checks that the return type is *not* ``bool``.  The boolean value of
the return type affects which lines mypy thinks are reachable after a
``with`` statement, since any :py:meth:`__exit__ <object.__exit__>` method that can return
``True`` may swallow exceptions. An imprecise return type can result
in mysterious errors reported near ``with`` statements.

To fix this, use either ``typing.Literal[False]`` or
``None`` as the return type. Returning ``None`` is equivalent to
returning ``False`` in this context, since both are treated as false
values.

Example:

.. code-block:: python

   class MyContext:
       ...
       def __exit__(self, exc, value, tb) -> bool:  # Error
           print('exit')
           return False

This produces the following output from mypy:

.. code-block:: text

   example.py:3: error: "bool" is invalid as return type for "__exit__" that always returns False
   example.py:3: note: Use "typing_extensions.Literal[False]" as the return type or change it to
       "None"
   example.py:3: note: If return type of "__exit__" implies that it may return True, the context
       manager may swallow exceptions

You can use ``Literal[False]`` to fix the error:

.. code-block:: python

   from typing import Literal

   class MyContext:
       ...
       def __exit__(self, exc, value, tb) -> Literal[False]:  # OK
           print('exit')
           return False

You can also use ``None``:

.. code-block:: python

   class MyContext:
       ...
       def __exit__(self, exc, value, tb) -> None:  # Also OK
           print('exit')

.. _code-name-match:

Check that naming is consistent [name-match]
--------------------------------------------

The definition of a named tuple or a TypedDict must be named
consistently when using the call-based syntax. Example:

.. code-block:: python

    from typing import NamedTuple

    # Error: First argument to namedtuple() should be "Point2D", not "Point"
    Point2D = NamedTuple("Point", [("x", int), ("y", int)])

.. _code-literal-required:

Check that literal is used where expected [literal-required]
------------------------------------------------------------

There are some places where only a (string) literal value is expected for
the purposes of static type checking, for example a ``TypedDict`` key, or
a ``__match_args__`` item. Providing a ``str``-valued variable in such contexts
will result in an error. Note that in many cases you can also use ``Final``
or ``Literal`` variables. Example:

.. code-block:: python

   from typing import Final, Literal, TypedDict

   class Point(TypedDict):
       x: int
       y: int

   def test(p: Point) -> None:
       X: Final = "x"
       p[X]  # OK

       Y: Literal["y"] = "y"
       p[Y]  # OK

       key = "x"  # Inferred type of key is `str`
       # Error: TypedDict key must be a string literal;
       #   expected one of ("x", "y")  [literal-required]
       p[key]

.. _code-no-overload-impl:

Check that overloaded functions have an implementation [no-overload-impl]
-------------------------------------------------------------------------

Overloaded functions outside of stub files must be followed by a non overloaded
implementation.

.. code-block:: python

   from typing import overload

   @overload
   def func(value: int) -> int:
       ...

   @overload
   def func(value: str) -> str:
       ...

   # presence of required function below is checked
   def func(value):
       pass  # actual implementation

.. _code-unused-coroutine:

Check that coroutine return value is used [unused-coroutine]
------------------------------------------------------------

Mypy ensures that return values of async def functions are not
ignored, as this is usually a programming error, as the coroutine
won't be executed at the call site.

.. code-block:: python

   async def f() -> None:
       ...

   async def g() -> None:
       f()  # Error: missing await
       await f()  # OK

You can work around this error by assigning the result to a temporary,
otherwise unused variable:

.. code-block:: python

       _ = f()  # No error

.. _code-top-level-await:

Warn about top level await expressions [top-level-await]
--------------------------------------------------------

This error code is separate from the general ``[syntax]`` errors, because in
some environments (e.g. IPython) a top level ``await`` is allowed. In such
environments a user may want to use ``--disable-error-code=top-level-await``,
that allows to still have errors for other improper uses of ``await``, for
example:

.. code-block:: python

   async def f() -> None:
       ...

   top = await f()  # Error: "await" outside function  [top-level-await]

.. _code-await-not-async:

Warn about await expressions used outside of coroutines [await-not-async]
-------------------------------------------------------------------------

``await`` must be used inside a coroutine.

.. code-block:: python

   async def f() -> None:
       ...

   def g() -> None:
       await f()  # Error: "await" outside coroutine ("async def")  [await-not-async]

.. _code-assert-type:

Check types in assert_type [assert-type]
----------------------------------------

The inferred type for an expression passed to ``assert_type`` must match
the provided type.

.. code-block:: python

   from typing_extensions import assert_type

   assert_type([1], list[int])  # OK

   assert_type([1], list[str])  # Error

.. _code-truthy-function:

Check that function isn't used in boolean context [truthy-function]
-------------------------------------------------------------------

Functions will always evaluate to true in boolean contexts.

.. code-block:: python

    def f():
        ...

    if f:  # Error: Function "Callable[[], Any]" could always be true in boolean context  [truthy-function]
        pass

.. _code-str-format:

Check that string formatting/interpolation is type-safe [str-format]
--------------------------------------------------------------------

Mypy will check that f-strings, ``str.format()`` calls, and ``%`` interpolations
are valid (when corresponding template is a literal string). This includes
checking number and types of replacements, for example:

.. code-block:: python

    # Error: Cannot find replacement for positional format specifier 1 [str-format]
    "{} and {}".format("spam")
    "{} and {}".format("spam", "eggs")  # OK
    # Error: Not all arguments converted during string formatting [str-format]
    "{} and {}".format("spam", "eggs", "cheese")

    # Error: Incompatible types in string interpolation
    # (expression has type "float", placeholder has type "int") [str-format]
    "{:d}".format(3.14)

.. _code-str-bytes-safe:

Check for implicit bytes coercions [str-bytes-safe]
-------------------------------------------------------------------

Warn about cases where a bytes object may be converted to a string in an unexpected manner.

.. code-block:: python

    b = b"abc"

    # Error: If x = b'abc' then f"{x}" or "{}".format(x) produces "b'abc'", not "abc".
    # If this is desired behavior, use f"{x!r}" or "{!r}".format(x).
    # Otherwise, decode the bytes [str-bytes-safe]
    print(f"The alphabet starts with {b}")

    # Okay
    print(f"The alphabet starts with {b!r}")  # The alphabet starts with b'abc'
    print(f"The alphabet starts with {b.decode('utf-8')}")  # The alphabet starts with abc

.. _code-overload-overlap:

Check that overloaded functions don't overlap [overload-overlap]
----------------------------------------------------------------

Warn if multiple ``@overload`` variants overlap in potentially unsafe ways.
This guards against the following situation:

.. code-block:: python

    from typing import overload

    class A: ...
    class B(A): ...

    @overload
    def foo(x: B) -> int: ...  # Error: Overloaded function signatures 1 and 2 overlap with incompatible return types  [overload-overlap]
    @overload
    def foo(x: A) -> str: ...
    def foo(x): ...

    def takes_a(a: A) -> str:
        return foo(a)

    a: A = B()
    value = takes_a(a)
    # mypy will think that value is a str, but it could actually be an int
    reveal_type(value) # Revealed type is "builtins.str"


Note that in cases where you ignore this error, mypy will usually still infer the
types you expect.

See :ref:`overloading <function-overloading>` for more explanation.


.. _code-overload-cannot-match:

Check for overload signatures that cannot match [overload-cannot-match]
--------------------------------------------------------------------------

Warn if an ``@overload`` variant can never be matched, because an earlier
overload has a wider signature. For example, this can happen if the two
overloads accept the same parameters and each parameter on the first overload
has the same type or a wider type than the corresponding parameter on the second
overload.

Example:

.. code-block:: python

    from typing import overload, Union

    @overload
    def process(response1: object, response2: object) -> object:
        ...
    @overload
    def process(response1: int, response2: int) -> int: # E: Overloaded function signature 2 will never be matched: signature 1's parameter type(s) are the same or broader  [overload-cannot-match]
        ...

    def process(response1: object, response2: object) -> object:
        return response1 + response2

.. _code-annotation-unchecked:

Notify about an annotation in an unchecked function [annotation-unchecked]
--------------------------------------------------------------------------

Sometimes a user may accidentally omit an annotation for a function, and mypy
will not check the body of this function (unless one uses
:option:`--check-untyped-defs <mypy --check-untyped-defs>` or
:option:`--disallow-untyped-defs <mypy --disallow-untyped-defs>`). To avoid
such situations go unnoticed, mypy will show a note, if there are any type
annotations in an unchecked function:

.. code-block:: python

    def test_assignment():  # "-> None" return annotation is missing
        # Note: By default the bodies of untyped functions are not checked,
        # consider using --check-untyped-defs [annotation-unchecked]
        x: int = "no way"

Note that mypy will still exit with return code ``0``, since such behaviour is
specified by :pep:`484`.

.. _code-prop-decorator:

Decorator preceding property not supported [prop-decorator]
-----------------------------------------------------------

Mypy does not yet support analysis of decorators that precede the property
decorator. If the decorator does not preserve the declared type of the property,
mypy will not infer the correct type for the declaration. If the decorator cannot
be moved after the ``@property`` decorator, then you must use a type ignore
comment:

.. code-block:: python

    class MyClass:
        @special  # type: ignore[prop-decorator]
        @property
        def magic(self) -> str:
            return "xyzzy"

.. note::

    For backward compatibility, this error code is a subcode of the generic ``[misc]`` code.

.. _code-syntax:

Report syntax errors [syntax]
-----------------------------

If the code being checked is not syntactically valid, mypy issues a
syntax error. Most, but not all, syntax errors are *blocking errors*:
they can't be ignored with a ``# type: ignore`` comment.

.. _code-typeddict-readonly-mutated:

ReadOnly key of a TypedDict is mutated [typeddict-readonly-mutated]
-------------------------------------------------------------------

Consider this example:

.. code-block:: python

    from datetime import datetime
    from typing import TypedDict
    from typing_extensions import ReadOnly

    class User(TypedDict):
        username: ReadOnly[str]
        last_active: datetime

    user: User = {'username': 'foobar', 'last_active': datetime.now()}
    user['last_active'] = datetime.now()  # ok
    user['username'] = 'other'  # error: ReadOnly TypedDict key "key" TypedDict is mutated  [typeddict-readonly-mutated]

`PEP 705 <https://peps.python.org/pep-0705>`_ specifies
how ``ReadOnly`` special form works for ``TypedDict`` objects.

.. _code-narrowed-type-not-subtype:

Check that ``TypeIs`` narrows types [narrowed-type-not-subtype]
---------------------------------------------------------------

:pep:`742` requires that when ``TypeIs`` is used, the narrowed
type must be a subtype of the original type::

    from typing_extensions import TypeIs

    def f(x: int) -> TypeIs[str]:  # Error, str is not a subtype of int
        ...

    def g(x: object) -> TypeIs[str]:  # OK
        ...

.. _code-misc:

Miscellaneous checks [misc]
---------------------------

Mypy performs numerous other, less commonly failing checks that don't
have specific error codes. These use the ``misc`` error code. Other
than being used for multiple unrelated errors, the ``misc`` error code
is not special. For example, you can ignore all errors in this
category by using ``# type: ignore[misc]`` comment. Since these errors
are not expected to be common, it's unlikely that you'll see two
*different* errors with the ``misc`` code on a single line -- though
this can certainly happen once in a while.

.. note::

    Future mypy versions will likely add new error codes for some errors
    that currently use the ``misc`` error code.
````

## File: docs/source/error_code_list2.rst
````
.. _error-codes-optional:

Error codes for optional checks
===============================

This section documents various errors codes that mypy generates only
if you enable certain options. See :ref:`error-codes` for general
documentation about error codes and their configuration.
:ref:`error-code-list` documents error codes that are enabled by default.

.. note::

   The examples in this section use :ref:`inline configuration
   <inline-config>` to specify mypy options. You can also set the same
   options by using a :ref:`configuration file <config-file>` or
   :ref:`command-line options <command-line>`.

.. _code-type-arg:

Check that type arguments exist [type-arg]
------------------------------------------

If you use :option:`--disallow-any-generics <mypy --disallow-any-generics>`, mypy requires that each generic
type has values for each type argument. For example, the types ``list`` or
``dict`` would be rejected. You should instead use types like ``list[int]`` or
``dict[str, int]``. Any omitted generic type arguments get implicit ``Any``
values. The type ``list`` is equivalent to ``list[Any]``, and so on.

Example:

.. code-block:: python

    # mypy: disallow-any-generics

    # Error: Missing type parameters for generic type "list"  [type-arg]
    def remove_dups(items: list) -> list:
        ...

.. _code-no-untyped-def:

Check that every function has an annotation [no-untyped-def]
------------------------------------------------------------

If you use :option:`--disallow-untyped-defs <mypy --disallow-untyped-defs>`, mypy requires that all functions
have annotations (either a Python 3 annotation or a type comment).

Example:

.. code-block:: python

    # mypy: disallow-untyped-defs

    def inc(x):  # Error: Function is missing a type annotation  [no-untyped-def]
        return x + 1

    def inc_ok(x: int) -> int:  # OK
        return x + 1

    class Counter:
         # Error: Function is missing a type annotation  [no-untyped-def]
         def __init__(self):
             self.value = 0

    class CounterOk:
         # OK: An explicit "-> None" is needed if "__init__" takes no arguments
         def __init__(self) -> None:
             self.value = 0

.. _code-redundant-cast:

Check that cast is not redundant [redundant-cast]
-------------------------------------------------

If you use :option:`--warn-redundant-casts <mypy --warn-redundant-casts>`, mypy will generate an error if the source
type of a cast is the same as the target type.

Example:

.. code-block:: python

    # mypy: warn-redundant-casts

    from typing import cast

    Count = int

    def example(x: Count) -> int:
        # Error: Redundant cast to "int"  [redundant-cast]
        return cast(int, x)

.. _code-redundant-self:

Check that methods do not have redundant Self annotations [redundant-self]
--------------------------------------------------------------------------

If a method uses the ``Self`` type in the return type or the type of a
non-self argument, there is no need to annotate the ``self`` argument
explicitly. Such annotations are allowed by :pep:`673` but are
redundant. If you enable this error code, mypy will generate an error if
there is a redundant ``Self`` type.

Example:

.. code-block:: python

   # mypy: enable-error-code="redundant-self"

   from typing import Self

   class C:
       # Error: Redundant "Self" annotation for the first method argument
       def copy(self: Self) -> Self:
           return type(self)()

.. _code-comparison-overlap:

Check that comparisons are overlapping [comparison-overlap]
-----------------------------------------------------------

If you use :option:`--strict-equality <mypy --strict-equality>`, mypy will generate an error if it
thinks that a comparison operation is always true or false. These are
often bugs. Sometimes mypy is too picky and the comparison can
actually be useful. Instead of disabling strict equality checking
everywhere, you can use ``# type: ignore[comparison-overlap]`` to
ignore the issue on a particular line only.

Example:

.. code-block:: python

    # mypy: strict-equality

    def is_magic(x: bytes) -> bool:
        # Error: Non-overlapping equality check (left operand type: "bytes",
        #        right operand type: "str")  [comparison-overlap]
        return x == 'magic'

We can fix the error by changing the string literal to a bytes
literal:

.. code-block:: python

    # mypy: strict-equality

    def is_magic(x: bytes) -> bool:
        return x == b'magic'  # OK

.. _code-no-untyped-call:

Check that no untyped functions are called [no-untyped-call]
------------------------------------------------------------

If you use :option:`--disallow-untyped-calls <mypy --disallow-untyped-calls>`, mypy generates an error when you
call an unannotated function in an annotated function.

Example:

.. code-block:: python

    # mypy: disallow-untyped-calls

    def do_it() -> None:
        # Error: Call to untyped function "bad" in typed context  [no-untyped-call]
        bad()

    def bad():
        ...

.. _code-no-any-return:

Check that function does not return Any value [no-any-return]
-------------------------------------------------------------

If you use :option:`--warn-return-any <mypy --warn-return-any>`, mypy generates an error if you return a
value with an ``Any`` type in a function that is annotated to return a
non-``Any`` value.

Example:

.. code-block:: python

    # mypy: warn-return-any

    def fields(s):
         return s.split(',')

    def first_field(x: str) -> str:
        # Error: Returning Any from function declared to return "str"  [no-any-return]
        return fields(x)[0]

.. _code-no-any-unimported:

Check that types have no Any components due to missing imports [no-any-unimported]
----------------------------------------------------------------------------------

If you use :option:`--disallow-any-unimported <mypy --disallow-any-unimported>`, mypy generates an error if a component of
a type becomes ``Any`` because mypy couldn't resolve an import. These "stealth"
``Any`` types can be surprising and accidentally cause imprecise type checking.

In this example, we assume that mypy can't find the module ``animals``, which means
that ``Cat`` falls back to ``Any`` in a type annotation:

.. code-block:: python

    # mypy: disallow-any-unimported

    from animals import Cat  # type: ignore

    # Error: Argument 1 to "feed" becomes "Any" due to an unfollowed import  [no-any-unimported]
    def feed(cat: Cat) -> None:
        ...

.. _code-unreachable:

Check that statement or expression is unreachable [unreachable]
---------------------------------------------------------------

If you use :option:`--warn-unreachable <mypy --warn-unreachable>`, mypy generates an error if it
thinks that a statement or expression will never be executed. In most cases, this is due to
incorrect control flow or conditional checks that are accidentally always true or false.

.. code-block:: python

    # mypy: warn-unreachable

    def example(x: int) -> None:
        # Error: Right operand of "or" is never evaluated  [unreachable]
        assert isinstance(x, int) or x == 'unused'

        return
        # Error: Statement is unreachable  [unreachable]
        print('unreachable')

.. _code-deprecated:

Check that imported or used feature is deprecated [deprecated]
--------------------------------------------------------------

If you use :option:`--enable-error-code deprecated <mypy --enable-error-code>`,
mypy generates an error if your code imports a deprecated feature explicitly with a
``from mod import depr`` statement or uses a deprecated feature imported otherwise or defined
locally.  Features are considered deprecated when decorated with ``warnings.deprecated``, as
specified in `PEP 702 <https://peps.python.org/pep-0702>`_.
Use the :option:`--report-deprecated-as-note <mypy --report-deprecated-as-note>` option to
turn all such errors into notes.
Use :option:`--deprecated-calls-exclude <mypy --deprecated-calls-exclude>` to hide warnings
for specific functions, classes and packages.

.. note::

    The ``warnings`` module provides the ``@deprecated`` decorator since Python 3.13.
    To use it with older Python versions, import it from ``typing_extensions`` instead.

Examples:

.. code-block:: python

    # mypy: report-deprecated-as-error

    # Error: abc.abstractproperty is deprecated: Deprecated, use 'property' with 'abstractmethod' instead
    from abc import abstractproperty

    from typing_extensions import deprecated

    @deprecated("use new_function")
    def old_function() -> None:
        print("I am old")

    # Error: __main__.old_function is deprecated: use new_function
    old_function()
    old_function()  # type: ignore[deprecated]


.. _code-redundant-expr:

Check that expression is redundant [redundant-expr]
---------------------------------------------------

If you use :option:`--enable-error-code redundant-expr <mypy --enable-error-code>`,
mypy generates an error if it thinks that an expression is redundant.

.. code-block:: python

    # mypy: enable-error-code="redundant-expr"

    def example(x: int) -> None:
        # Error: Left operand of "and" is always true  [redundant-expr]
        if isinstance(x, int) and x > 0:
            pass

        # Error: If condition is always true  [redundant-expr]
        1 if isinstance(x, int) else 0

        # Error: If condition in comprehension is always true  [redundant-expr]
        [i for i in range(x) if isinstance(i, int)]


.. _code-possibly-undefined:

Warn about variables that are defined only in some execution paths [possibly-undefined]
---------------------------------------------------------------------------------------

If you use :option:`--enable-error-code possibly-undefined <mypy --enable-error-code>`,
mypy generates an error if it cannot verify that a variable will be defined in
all execution paths. This includes situations when a variable definition
appears in a loop, in a conditional branch, in an except handler, etc. For
example:

.. code-block:: python

    # mypy: enable-error-code="possibly-undefined"

    from collections.abc import Iterable

    def test(values: Iterable[int], flag: bool) -> None:
        if flag:
            a = 1
        z = a + 1  # Error: Name "a" may be undefined [possibly-undefined]

        for v in values:
            b = v
        z = b + 1  # Error: Name "b" may be undefined [possibly-undefined]

.. _code-truthy-bool:

Check that expression is not implicitly true in boolean context [truthy-bool]
-----------------------------------------------------------------------------

Warn when the type of an expression in a boolean context does not
implement ``__bool__`` or ``__len__``. Unless one of these is
implemented by a subtype, the expression will always be considered
true, and there may be a bug in the condition.

As an exception, the ``object`` type is allowed in a boolean context.
Using an iterable value in a boolean context has a separate error code
(see below).

.. code-block:: python

    # mypy: enable-error-code="truthy-bool"

    class Foo:
        pass
    foo = Foo()
    # Error: "foo" has type "Foo" which does not implement __bool__ or __len__ so it could always be true in boolean context
    if foo:
         ...

.. _code-truthy-iterable:

Check that iterable is not implicitly true in boolean context [truthy-iterable]
-------------------------------------------------------------------------------

Generate an error if a value of type ``Iterable`` is used as a boolean
condition, since ``Iterable`` does not implement ``__len__`` or ``__bool__``.

Example:

.. code-block:: python

    from collections.abc import Iterable

    def transform(items: Iterable[int]) -> list[int]:
        # Error: "items" has type "Iterable[int]" which can always be true in boolean context. Consider using "Collection[int]" instead.  [truthy-iterable]
        if not items:
            return [42]
        return [x + 1 for x in items]

If ``transform`` is called with a ``Generator`` argument, such as
``int(x) for x in []``, this function would not return ``[42]`` unlike
what might be intended. Of course, it's possible that ``transform`` is
only called with ``list`` or other container objects, and the ``if not
items`` check is actually valid. If that is the case, it is
recommended to annotate ``items`` as ``Collection[int]`` instead of
``Iterable[int]``.

.. _code-ignore-without-code:

Check that ``# type: ignore`` include an error code [ignore-without-code]
-------------------------------------------------------------------------

Warn when a ``# type: ignore`` comment does not specify any error codes.
This clarifies the intent of the ignore and ensures that only the
expected errors are silenced.

Example:

.. code-block:: python

    # mypy: enable-error-code="ignore-without-code"

    class Foo:
        def __init__(self, name: str) -> None:
            self.name = name

    f = Foo('foo')

    # This line has a typo that mypy can't help with as both:
    # - the expected error 'assignment', and
    # - the unexpected error 'attr-defined'
    # are silenced.
    # Error: "type: ignore" comment without error code (consider "type: ignore[attr-defined]" instead)
    f.nme = 42  # type: ignore

    # This line warns correctly about the typo in the attribute name
    # Error: "Foo" has no attribute "nme"; maybe "name"?
    f.nme = 42  # type: ignore[assignment]

.. _code-unused-awaitable:

Check that awaitable return value is used [unused-awaitable]
------------------------------------------------------------

If you use :option:`--enable-error-code unused-awaitable <mypy --enable-error-code>`,
mypy generates an error if you don't use a returned value that defines ``__await__``.

Example:

.. code-block:: python

    # mypy: enable-error-code="unused-awaitable"

    import asyncio

    async def f() -> int: ...

    async def g() -> None:
        # Error: Value of type "Task[int]" must be used
        #        Are you missing an await?
        asyncio.create_task(f())

You can assign the value to a temporary, otherwise unused variable to
silence the error:

.. code-block:: python

    async def g() -> None:
        _ = asyncio.create_task(f())  # No error

.. _code-unused-ignore:

Check that ``# type: ignore`` comment is used [unused-ignore]
-------------------------------------------------------------

If you use :option:`--enable-error-code unused-ignore <mypy --enable-error-code>`,
or :option:`--warn-unused-ignores <mypy --warn-unused-ignores>`
mypy generates an error if you don't use a ``# type: ignore`` comment, i.e. if
there is a comment, but there would be no error generated by mypy on this line
anyway.

Example:

.. code-block:: python

    # Use "mypy --warn-unused-ignores ..."

    def add(a: int, b: int) -> int:
        # Error: unused "type: ignore" comment
        return a + b  # type: ignore

Note that due to a specific nature of this comment, the only way to selectively
silence it, is to include the error code explicitly. Also note that this error is
not shown if the ``# type: ignore`` is not used due to code being statically
unreachable (e.g. due to platform or version checks).

Example:

.. code-block:: python

    # Use "mypy --warn-unused-ignores ..."

    import sys

    try:
        # The "[unused-ignore]" is needed to get a clean mypy run
        # on both Python 3.8, and 3.9 where this module was added
        import graphlib  # type: ignore[import,unused-ignore]
    except ImportError:
        pass

    if sys.version_info >= (3, 9):
        # The following will not generate an error on either
        # Python 3.8, or Python 3.9
        42 + "testing..."  # type: ignore

.. _code-explicit-override:

Check that ``@override`` is used when overriding a base class method [explicit-override]
----------------------------------------------------------------------------------------

If you use :option:`--enable-error-code explicit-override <mypy --enable-error-code>`
mypy generates an error if you override a base class method without using the
``@override`` decorator. An error will not be emitted for overrides of ``__init__``
or ``__new__``. See `PEP 698 <https://peps.python.org/pep-0698/#strict-enforcement-per-project>`_.

.. note::

    Starting with Python 3.12, the ``@override`` decorator can be imported from ``typing``.
    To use it with older Python versions, import it from ``typing_extensions`` instead.

Example:

.. code-block:: python

    # mypy: enable-error-code="explicit-override"

    from typing import override

    class Parent:
        def f(self, x: int) -> None:
            pass

        def g(self, y: int) -> None:
            pass


    class Child(Parent):
        def f(self, x: int) -> None:  # Error: Missing @override decorator
            pass

        @override
        def g(self, y: int) -> None:
            pass

.. _code-mutable-override:

Check that overrides of mutable attributes are safe [mutable-override]
----------------------------------------------------------------------

`mutable-override` will enable the check for unsafe overrides of mutable attributes.
For historical reasons, and because this is a relatively common pattern in Python,
this check is not enabled by default. The example below is unsafe, and will be
flagged when this error code is enabled:

.. code-block:: python

    from typing import Any

    class C:
        x: float
        y: float
        z: float

    class D(C):
        x: int  # Error: Covariant override of a mutable attribute
                # (base class "C" defined the type as "float",
                # expression has type "int")  [mutable-override]
        y: float  # OK
        z: Any  # OK

    def f(c: C) -> None:
        c.x = 1.1
    d = D()
    f(d)
    d.x >> 1  # This will crash at runtime, because d.x is now float, not an int

.. _code-unimported-reveal:

Check that ``reveal_type`` is imported from typing or typing_extensions [unimported-reveal]
-------------------------------------------------------------------------------------------

Mypy used to have ``reveal_type`` as a special builtin
that only existed during type-checking.
In runtime it fails with expected ``NameError``,
which can cause real problem in production, hidden from mypy.

But, in Python3.11 :py:func:`typing.reveal_type` was added.
``typing_extensions`` ported this helper to all supported Python versions.

Now users can actually import ``reveal_type`` to make the runtime code safe.

.. note::

    Starting with Python 3.11, the ``reveal_type`` function can be imported from ``typing``.
    To use it with older Python versions, import it from ``typing_extensions`` instead.

.. code-block:: python

    # mypy: enable-error-code="unimported-reveal"

    x = 1
    reveal_type(x)  # Note: Revealed type is "builtins.int" \
                    # Error: Name "reveal_type" is not defined

Correct usage:

.. code-block:: python

    # mypy: enable-error-code="unimported-reveal"
    from typing import reveal_type   # or `typing_extensions`

    x = 1
    # This won't raise an error:
    reveal_type(x)  # Note: Revealed type is "builtins.int"

When this code is enabled, using ``reveal_locals`` is always an error,
because there's no way one can import it.


.. _code-explicit-any:

Check that explicit Any type annotations are not allowed [explicit-any]
-----------------------------------------------------------------------

If you use :option:`--disallow-any-explicit <mypy --disallow-any-explicit>`, mypy generates an error
if you use an explicit ``Any`` type annotation.

Example:

.. code-block:: python

    # mypy: disallow-any-explicit
    from typing import Any
    x: Any = 1  # Error: Explicit "Any" type annotation  [explicit-any]


.. _code-exhaustive-match:

Check that match statements match exhaustively [exhaustive-match]
-----------------------------------------------------------------------

If enabled with :option:`--enable-error-code exhaustive-match <mypy --enable-error-code>`,
mypy generates an error if a match statement does not match all possible cases/types.


Example:

.. code-block:: python

        import enum


        class Color(enum.Enum):
            RED = 1
            BLUE = 2

        val: Color = Color.RED

        # OK without --enable-error-code exhaustive-match
        match val:
            case Color.RED:
                print("red")

        # With --enable-error-code exhaustive-match
        # Error: Match statement has unhandled case for values of type "Literal[Color.BLUE]"
        match val:
            case Color.RED:
                print("red")

        # OK with or without --enable-error-code exhaustive-match, since all cases are handled
        match val:
            case Color.RED:
                print("red")
            case _:
                print("other")
````

## File: docs/source/error_codes.rst
````
.. _error-codes:

Error codes
===========

Mypy can optionally display an error code such as ``[attr-defined]``
after each error message. Error codes serve two purposes:

1. It's possible to silence specific error codes on a line using ``#
   type: ignore[code]``. This way you won't accidentally ignore other,
   potentially more serious errors.

2. The error code can be used to find documentation about the error.
   The next two topics (:ref:`error-code-list` and
   :ref:`error-codes-optional`) document the various error codes
   mypy can report.

Most error codes are shared between multiple related error messages.
Error codes may change in future mypy releases.


.. _silence-error-codes:

Silencing errors based on error codes
-------------------------------------

You can use a special comment ``# type: ignore[code, ...]`` to only
ignore errors with a specific error code (or codes) on a particular
line.  This can be used even if you have not configured mypy to show
error codes.

This example shows how to ignore an error about an imported name mypy
thinks is undefined:

.. code-block:: python

   # 'foo' is defined in 'foolib', even though mypy can't see the
   # definition.
   from foolib import foo  # type: ignore[attr-defined]

Enabling/disabling specific error codes globally
------------------------------------------------

There are command-line flags and config file settings for enabling
certain optional error codes, such as :option:`--disallow-untyped-defs <mypy --disallow-untyped-defs>`,
which enables the ``no-untyped-def`` error code.

You can use :option:`--enable-error-code <mypy --enable-error-code>`
and :option:`--disable-error-code <mypy --disable-error-code>`
to enable or disable specific error codes that don't have a dedicated
command-line flag or config file setting.

Per-module enabling/disabling error codes
-----------------------------------------

You can use :ref:`configuration file <config-file>` sections to enable or
disable specific error codes only in some modules. For example, this ``mypy.ini``
config will enable non-annotated empty containers in tests, while keeping
other parts of code checked in strict mode:

.. code-block:: ini

   [mypy]
   strict = True

   [mypy-tests.*]
   allow_untyped_defs = True
   allow_untyped_calls = True
   disable_error_code = var-annotated, has-type

Note that per-module enabling/disabling acts as override over the global
options. So that you don't need to repeat the error code lists for each
module if you have them in global config section. For example:

.. code-block:: ini

   [mypy]
   enable_error_code = truthy-bool, ignore-without-code, unused-awaitable

   [mypy-extensions.*]
   disable_error_code = unused-awaitable

The above config will allow unused awaitables in extension modules, but will
still keep the other two error codes enabled. The overall logic is following:

* Command line and/or config main section set global error codes

* Individual config sections *adjust* them per glob/module

* Inline ``# mypy: disable-error-code="..."`` and ``# mypy: enable-error-code="..."``
  comments can further *adjust* them for a specific file.
  For example:

.. code-block:: python

  # mypy: enable-error-code="truthy-bool, ignore-without-code"

So one can e.g. enable some code globally, disable it for all tests in
the corresponding config section, and then re-enable it with an inline
comment in some specific test.

Subcodes of error codes
-----------------------

In some cases, mostly for backwards compatibility reasons, an error
code may be covered also by another, wider error code. For example, an error with
code ``[method-assign]`` can be ignored by ``# type: ignore[assignment]``.
Similar logic works for disabling error codes globally. If a given error code
is a subcode of another one, it will be mentioned in the documentation for the narrower
code. This hierarchy is not nested: there cannot be subcodes of other
subcodes.


Requiring error codes
---------------------

It's possible to require error codes be specified in ``type: ignore`` comments.
See :ref:`ignore-without-code<code-ignore-without-code>` for more information.
````

## File: docs/source/existing_code.rst
````
.. _existing-code:

Using mypy with an existing codebase
====================================

This section explains how to get started using mypy with an existing,
significant codebase that has little or no type annotations. If you are
a beginner, you can skip this section.

Start small
-----------

If your codebase is large, pick a subset of your codebase (say, 5,000 to 50,000
lines) and get mypy to run successfully only on this subset at first, *before
adding annotations*. This should be doable in a day or two. The sooner you get
some form of mypy passing on your codebase, the sooner you benefit.

You'll likely need to fix some mypy errors, either by inserting
annotations requested by mypy or by adding ``# type: ignore``
comments to silence errors you don't want to fix now.

We'll mention some tips for getting mypy passing on your codebase in various
sections below.

Run mypy consistently and prevent regressions
---------------------------------------------

Make sure all developers on your codebase run mypy the same way.
One way to ensure this is adding a small script with your mypy
invocation to your codebase, or adding your mypy invocation to
existing tools you use to run tests, like ``tox``.

* Make sure everyone runs mypy with the same options. Checking a mypy
  :ref:`configuration file <config-file>` into your codebase is the
  easiest way to do this.

* Make sure everyone type checks the same set of files. See
  :ref:`specifying-code-to-be-checked` for details.

* Make sure everyone runs mypy with the same version of mypy, for instance
  by pinning mypy with the rest of your dev requirements.

In particular, you'll want to make sure to run mypy as part of your
Continuous Integration (CI) system as soon as possible. This will
prevent new type errors from being introduced into your codebase.

A simple CI script could look something like this:

.. code-block:: text

    python3 -m pip install mypy==1.8
    # Run your standardised mypy invocation, e.g.
    mypy my_project
    # This could also look like `scripts/run_mypy.sh`, `tox run -e mypy`, `make mypy`, etc

Ignoring errors from certain modules
------------------------------------

By default mypy will follow imports in your code and try to check everything.
This means even if you only pass in a few files to mypy, it may still process a
large number of imported files. This could potentially result in lots of errors
you don't want to deal with at the moment.

One way to deal with this is to ignore errors in modules you aren't yet ready to
type check. The :confval:`ignore_errors` option is useful for this, for instance,
if you aren't yet ready to deal with errors from ``package_to_fix_later``:

.. code-block:: text

   [mypy-package_to_fix_later.*]
   ignore_errors = True

You could even invert this, by setting ``ignore_errors = True`` in your global
config section and only enabling error reporting with ``ignore_errors = False``
for the set of modules you are ready to type check.

The per-module configuration that mypy's configuration file allows can be
extremely useful. Many configuration options can be enabled or disabled
only for specific modules. In particular, you can also enable or disable
various error codes on a per-module basis, see :ref:`error-codes`.

Fixing errors related to imports
--------------------------------

A common class of error you will encounter is errors from mypy about modules
that it can't find, that don't have types, or don't have stub files:

.. code-block:: text

    core/config.py:7: error: Cannot find implementation or library stub for module named 'frobnicate'
    core/model.py:9: error: Cannot find implementation or library stub for module named 'acme'
    ...

Sometimes these can be fixed by installing the relevant packages or
stub libraries in the environment you're running ``mypy`` in.

See :ref:`fix-missing-imports` for a complete reference on these errors
and the ways in which you can fix them.

You'll likely find that you want to suppress all errors from importing
a given module that doesn't have types. If you only import that module
in one or two places, you can use ``# type: ignore`` comments. For example,
here we ignore an error about a third-party module ``frobnicate`` that
doesn't have stubs using ``# type: ignore``:

.. code-block:: python

   import frobnicate  # type: ignore
   ...
   frobnicate.initialize()  # OK (but not checked)

But if you import the module in many places, this becomes unwieldy. In this
case, we recommend using a :ref:`configuration file <config-file>`. For example,
to disable errors about importing ``frobnicate`` and ``acme`` everywhere in your
codebase, use a config like this:

.. code-block:: text

   [mypy-frobnicate.*]
   ignore_missing_imports = True

   [mypy-acme.*]
   ignore_missing_imports = True

If you get a large number of errors, you may want to ignore all errors
about missing imports, for instance by setting
:option:`--disable-error-code=import-untyped <mypy --ignore-missing-imports>`.
or setting :confval:`ignore_missing_imports` to true globally.
This can hide errors later on, so we recommend avoiding this
if possible.

Finally, mypy allows fine-grained control over specific import following
behaviour. It's very easy to silently shoot yourself in the foot when playing
around with these, so this should be a last resort. For more
details, look :ref:`here <follow-imports>`.

Prioritise annotating widely imported modules
---------------------------------------------

Most projects have some widely imported modules, such as utilities or
model classes. It's a good idea to annotate these pretty early on,
since this allows code using these modules to be type checked more
effectively.

Mypy is designed to support gradual typing, i.e. letting you add annotations at
your own pace, so it's okay to leave some of these modules unannotated. The more
you annotate, the more useful mypy will be, but even a little annotation
coverage is useful.

Write annotations as you go
---------------------------

Consider adding something like these in your code style
conventions:

1. Developers should add annotations for any new code.
2. It's also encouraged to write annotations when you modify existing code.

This way you'll gradually increase annotation coverage in your
codebase without much effort.

Automate annotation of legacy code
----------------------------------

There are tools for automatically adding draft annotations based on simple
static analysis or on type profiles collected at runtime.  Tools include
:doc:`monkeytype:index`, `autotyping`_ and `PyAnnotate`_.

A simple approach is to collect types from test runs. This may work
well if your test coverage is good (and if your tests aren't very
slow).

Another approach is to enable type collection for a small, random
fraction of production network requests.  This clearly requires more
care, as type collection could impact the reliability or the
performance of your service.

.. _getting-to-strict:

Introduce stricter options
--------------------------

Mypy is very configurable. Once you get started with static typing, you may want
to explore the various strictness options mypy provides to catch more bugs. For
example, you can ask mypy to require annotations for all functions in certain
modules to avoid accidentally introducing code that won't be type checked using
:confval:`disallow_untyped_defs`. Refer to :ref:`config-file` for the details.

An excellent goal to aim for is to have your codebase pass when run against ``mypy --strict``.
This basically ensures that you will never have a type related error without an explicit
circumvention somewhere (such as a ``# type: ignore`` comment).

The following config is equivalent to ``--strict`` (as of mypy 1.0):

.. code-block:: text

   # Start off with these
   warn_unused_configs = True
   warn_redundant_casts = True
   warn_unused_ignores = True

   # Getting this passing should be easy
   strict_equality = True

   # Strongly recommend enabling this one as soon as you can
   check_untyped_defs = True

   # These shouldn't be too much additional work, but may be tricky to
   # get passing if you use a lot of untyped libraries
   disallow_subclassing_any = True
   disallow_untyped_decorators = True
   disallow_any_generics = True

   # These next few are various gradations of forcing use of type annotations
   disallow_untyped_calls = True
   disallow_incomplete_defs = True
   disallow_untyped_defs = True

   # This one isn't too hard to get passing, but return on investment is lower
   no_implicit_reexport = True

   # This one can be tricky to get passing if you use a lot of untyped libraries
   warn_return_any = True

   # This one is a catch-all flag for the rest of strict checks that are technically
   # correct but may not be practical
   extra_checks = True

Note that you can also start with ``--strict`` and subtract, for instance:

.. code-block:: text

   strict = True
   warn_return_any = False

Remember that many of these options can be enabled on a per-module basis. For instance,
you may want to enable ``disallow_untyped_defs`` for modules which you've completed
annotations for, in order to prevent new code from being added without annotations.

And if you want, it doesn't stop at ``--strict``. Mypy has additional checks
that are not part of ``--strict`` that can be useful. See the complete
:ref:`command-line` reference and :ref:`error-codes-optional`.

Speed up mypy runs
------------------

You can use :ref:`mypy daemon <mypy_daemon>` to get much faster
incremental mypy runs. The larger your project is, the more useful
this will be.  If your project has at least 100,000 lines of code or
so, you may also want to set up :ref:`remote caching <remote-cache>`
for further speedups.

.. _PyAnnotate: https://github.com/dropbox/pyannotate
.. _autotyping: https://github.com/JelleZijlstra/autotyping
````

## File: docs/source/extending_mypy.rst
````
.. _extending-mypy:

Extending and integrating mypy
==============================

.. _integrating-mypy:

Integrating mypy into another Python application
************************************************

It is possible to integrate mypy into another Python 3 application by
importing ``mypy.api`` and calling the ``run`` function with a parameter of type ``list[str]``, containing
what normally would have been the command line arguments to mypy.

Function ``run`` returns a ``tuple[str, str, int]``, namely
``(<normal_report>, <error_report>, <exit_status>)``, in which ``<normal_report>``
is what mypy normally writes to :py:data:`sys.stdout`, ``<error_report>`` is what mypy
normally writes to :py:data:`sys.stderr` and ``exit_status`` is the exit status mypy normally
returns to the operating system.

A trivial example of using the api is the following

.. code-block:: python

    import sys
    from mypy import api

    result = api.run(sys.argv[1:])

    if result[0]:
        print('\nType checking report:\n')
        print(result[0])  # stdout

    if result[1]:
        print('\nError report:\n')
        print(result[1])  # stderr

    print('\nExit status:', result[2])


.. _extending-mypy-using-plugins:

Extending mypy using plugins
****************************

Python is a highly dynamic language and has extensive metaprogramming
capabilities. Many popular libraries use these to create APIs that may
be more flexible and/or natural for humans, but are hard to express using
static types. Extending the :pep:`484` type system to accommodate all existing
dynamic patterns is impractical and often just impossible.

Mypy supports a plugin system that lets you customize the way mypy type checks
code. This can be useful if you want to extend mypy so it can type check code
that uses a library that is difficult to express using just :pep:`484` types.

The plugin system is focused on improving mypy's understanding
of *semantics* of third party frameworks. There is currently no way to define
new first class kinds of types.

.. note::

   The plugin system is experimental and prone to change. If you want to write
   a mypy plugin, we recommend you start by contacting the mypy core developers
   on `gitter <https://gitter.im/python/typing>`_. In particular, there are
   no guarantees about backwards compatibility.

   Backwards incompatible changes may be made without a deprecation period,
   but we will announce them in
   `the plugin API changes announcement issue <https://github.com/python/mypy/issues/6617>`_.

Configuring mypy to use plugins
*******************************

Plugins are Python files that can be specified in a mypy
:ref:`config file <config-file>` using the :confval:`plugins` option and one of the two formats: relative or
absolute path to the plugin file, or a module name (if the plugin
is installed using ``pip install`` in the same virtual environment where mypy
is running). The two formats can be mixed, for example:

.. code-block:: ini

    [mypy]
    plugins = /one/plugin.py, other.plugin

Mypy will try to import the plugins and will look for an entry point function
named ``plugin``. If the plugin entry point function has a different name, it
can be specified after colon:

.. code-block:: ini

    [mypy]
    plugins = custom_plugin:custom_entry_point

In the following sections we describe the basics of the plugin system with
some examples. For more technical details, please read the docstrings in
`mypy/plugin.py <https://github.com/python/mypy/blob/master/mypy/plugin.py>`_
in mypy source code. Also you can find good examples in the bundled plugins
located in `mypy/plugins <https://github.com/python/mypy/tree/master/mypy/plugins>`_.

High-level overview
*******************

Every entry point function should accept a single string argument
that is a full mypy version and return a subclass of ``mypy.plugin.Plugin``:

.. code-block:: python

   from mypy.plugin import Plugin

   class CustomPlugin(Plugin):
       def get_type_analyze_hook(self, fullname: str):
           # see explanation below
           ...

   def plugin(version: str):
       # ignore version argument if the plugin works with all mypy versions.
       return CustomPlugin

During different phases of analyzing the code (first in semantic analysis,
and then in type checking) mypy calls plugin methods such as
``get_type_analyze_hook()`` on user plugins. This particular method, for example,
can return a callback that mypy will use to analyze unbound types with the given
full name. See the full plugin hook method list :ref:`below <plugin_hooks>`.

Mypy maintains a list of plugins it gets from the config file plus the default
(built-in) plugin that is always enabled. Mypy calls a method once for each
plugin in the list until one of the methods returns a non-``None`` value.
This callback will be then used to customize the corresponding aspect of
analyzing/checking the current abstract syntax tree node.

The callback returned by the ``get_xxx`` method will be given a detailed
current context and an API to create new nodes, new types, emit error messages,
etc., and the result will be used for further processing.

Plugin developers should ensure that their plugins work well in incremental and
daemon modes. In particular, plugins should not hold global state due to caching
of plugin hook results.

.. _plugin_hooks:

Current list of plugin hooks
****************************

**get_type_analyze_hook()** customizes behaviour of the type analyzer.
For example, :pep:`484` doesn't support defining variadic generic types:

.. code-block:: python

   from lib import Vector

   a: Vector[int, int]
   b: Vector[int, int, int]

When analyzing this code, mypy will call ``get_type_analyze_hook("lib.Vector")``,
so the plugin can return some valid type for each variable.

**get_function_hook()** is used to adjust the return type of a function call.
This hook will be also called for instantiation of classes.
This is a good choice if the return type is too complex
to be expressed by regular python typing.

**get_function_signature_hook()** is used to adjust the signature of a function.

**get_method_hook()** is the same as ``get_function_hook()`` but for methods
instead of module level functions.

**get_method_signature_hook()** is used to adjust the signature of a method.
This includes special Python methods except :py:meth:`~object.__init__` and :py:meth:`~object.__new__`.
For example in this code:

.. code-block:: python

   from ctypes import Array, c_int

   x: Array[c_int]
   x[0] = 42

mypy will call ``get_method_signature_hook("ctypes.Array.__setitem__")``
so that the plugin can mimic the :py:mod:`ctypes` auto-convert behavior.

**get_attribute_hook()** overrides instance member field lookups and property
access (not method calls). This hook is only called for
fields which already exist on the class. *Exception:* if :py:meth:`__getattr__ <object.__getattr__>` or
:py:meth:`__getattribute__ <object.__getattribute__>` is a method on the class, the hook is called for all
fields which do not refer to methods.

**get_class_attribute_hook()** is similar to above, but for attributes on classes rather than instances.
Unlike above, this does not have special casing for :py:meth:`__getattr__ <object.__getattr__>` or
:py:meth:`__getattribute__ <object.__getattribute__>`.

**get_class_decorator_hook()** can be used to update class definition for
given class decorators. For example, you can add some attributes to the class
to match runtime behaviour:

.. code-block:: python

   from dataclasses import dataclass

   @dataclass  # built-in plugin adds `__init__` method here
   class User:
       name: str

   user = User(name='example')  # mypy can understand this using a plugin

**get_metaclass_hook()** is similar to above, but for metaclasses.

**get_base_class_hook()** is similar to above, but for base classes.

**get_dynamic_class_hook()** can be used to allow dynamic class definitions
in mypy. This plugin hook is called for every assignment to a simple name
where right hand side is a function call:

.. code-block:: python

   from lib import dynamic_class

   X = dynamic_class('X', [])

For such definition, mypy will call ``get_dynamic_class_hook("lib.dynamic_class")``.
The plugin should create the corresponding ``mypy.nodes.TypeInfo`` object, and
place it into a relevant symbol table. (Instances of this class represent
classes in mypy and hold essential information such as qualified name,
method resolution order, etc.)

**get_customize_class_mro_hook()** can be used to modify class MRO (for example
insert some entries there) before the class body is analyzed.

**get_additional_deps()** can be used to add new dependencies for a
module. It is called before semantic analysis. For example, this can
be used if a library has dependencies that are dynamically loaded
based on configuration information.

**report_config_data()** can be used if the plugin has some sort of
per-module configuration that can affect typechecking. In that case,
when the configuration for a module changes, we want to invalidate
mypy's cache for that module so that it can be rechecked. This hook
should be used to report to mypy any relevant configuration data,
so that mypy knows to recheck the module if the configuration changes.
The hooks should return data encodable as JSON.

Useful tools
************

Mypy ships ``mypy.plugins.proper_plugin`` plugin which can be useful
for plugin authors, since it finds missing ``get_proper_type()`` calls,
which is a pretty common mistake.

It is recommended to enable it as a part of your plugin's CI.
````

## File: docs/source/faq.rst
````
Frequently Asked Questions
==========================

Why have both dynamic and static typing?
****************************************

Dynamic typing can be flexible, powerful, convenient and easy. But
it's not always the best approach; there are good reasons why many
developers choose to use statically typed languages or static typing
for Python.

Here are some potential benefits of mypy-style static typing:

- Static typing can make programs easier to understand and
  maintain. Type declarations can serve as machine-checked
  documentation. This is important as code is typically read much more
  often than modified, and this is especially important for large and
  complex programs.

- Static typing can help you find bugs earlier and with less testing
  and debugging. Especially in large and complex projects this can be
  a major time-saver.

- Static typing can help you find difficult-to-find bugs before your
  code goes into production. This can improve reliability and reduce
  the number of security issues.

- Static typing makes it practical to build very useful development
  tools that can improve programming productivity or software quality,
  including IDEs with precise and reliable code completion, static
  analysis tools, etc.

- You can get the benefits of both dynamic and static typing in a
  single language. Dynamic typing can be perfect for a small project
  or for writing the UI of your program, for example. As your program
  grows, you can adapt tricky application logic to static typing to
  help maintenance.

See also the `front page <https://www.mypy-lang.org>`_ of the mypy web
site.

Would my project benefit from static typing?
********************************************

For many projects dynamic typing is perfectly fine (we think that
Python is a great language). But sometimes your projects demand bigger
guns, and that's when mypy may come in handy.

If some of these ring true for your projects, mypy (and static typing)
may be useful:

- Your project is large or complex.

- Your codebase must be maintained for a long time.

- Multiple developers are working on the same code.

- Running tests takes a lot of time or work (type checking helps
  you find errors quickly early in development, reducing the number of
  testing iterations).

- Some project members (devs or management) don't like dynamic typing,
  but others prefer dynamic typing and Python syntax. Mypy could be a
  solution that everybody finds easy to accept.

- You want to future-proof your project even if currently none of the
  above really apply. The earlier you start, the easier it will be to
  adopt static typing.

Can I use mypy to type check my existing Python code?
*****************************************************

Mypy supports most Python features and idioms, and many large Python
projects are using mypy successfully. Code that uses complex
introspection or metaprogramming may be impractical to type check, but
it should still be possible to use static typing in other parts of a
codebase that are less dynamic.

Will static typing make my programs run faster?
***********************************************

Mypy only does static type checking and it does not improve
performance. It has a minimal performance impact. In the future, there
could be other tools that can compile statically typed mypy code to C
modules or to efficient JVM bytecode, for example, but this is outside
the scope of the mypy project.

Is mypy free?
*************

Yes. Mypy is free software, and it can also be used for commercial and
proprietary projects. Mypy is available under the MIT license.

Can I use duck typing with mypy?
********************************

Mypy provides support for both `nominal subtyping
<https://en.wikipedia.org/wiki/Nominative_type_system>`_ and
`structural subtyping
<https://en.wikipedia.org/wiki/Structural_type_system>`_.
Structural subtyping can be thought of as "static duck typing".
Some argue that structural subtyping is better suited for languages with duck
typing such as Python. Mypy however primarily uses nominal subtyping,
leaving structural subtyping mostly opt-in (except for built-in protocols
such as :py:class:`~collections.abc.Iterable` that always support structural
subtyping). Here are some reasons why:

1. It is easy to generate short and informative error messages when
   using a nominal type system. This is especially important when
   using type inference.

2. Python provides built-in support for nominal :py:func:`isinstance` tests and
   they are widely used in programs. Only limited support for structural
   :py:func:`isinstance` is available, and it's less type safe than nominal type tests.

3. Many programmers are already familiar with static, nominal subtyping and it
   has been successfully used in languages such as Java, C++ and
   C#. Fewer languages use structural subtyping.

However, structural subtyping can also be useful. For example, a "public API"
may be more flexible if it is typed with protocols. Also, using protocol types
removes the necessity to explicitly declare implementations of ABCs.
As a rule of thumb, we recommend using nominal classes where possible, and
protocols where necessary. For more details about protocol types and structural
subtyping see :ref:`protocol-types` and :pep:`544`.

I like Python and I have no need for static typing
**************************************************

The aim of mypy is not to convince everybody to write statically typed
Python -- static typing is entirely optional, now and in the
future. The goal is to give more options for Python programmers, to
make Python a more competitive alternative to other statically typed
languages in large projects, to improve programmer productivity, and
to improve software quality.

How are mypy programs different from normal Python?
***************************************************

Since you use a vanilla Python implementation to run mypy programs,
mypy programs are also Python programs. The type checker may give
warnings for some valid Python code, but the code is still always
runnable. Also, a few Python features are still not
supported by mypy, but this is gradually improving.

The obvious difference is the availability of static type
checking. The section :ref:`common_issues` mentions some
modifications to Python code that may be required to make code type
check without errors. Also, your code must make defined
attributes explicit.

Mypy supports modular, efficient type checking, and this seems to
rule out type checking some language features, such as arbitrary
monkey patching of methods.

How is mypy different from Cython?
**********************************

:doc:`Cython <cython:index>` is a variant of Python that supports
compilation to CPython C modules. It can give major speedups to
certain classes of programs compared to CPython, and it provides
static typing (though this is different from mypy). Mypy differs in
the following aspects, among others:

- Cython is much more focused on performance than mypy. Mypy is only
  about static type checking, and increasing performance is not a
  direct goal.

- The mypy syntax is arguably simpler and more "Pythonic" (no cdef/cpdef, etc.) for statically typed code.

- The mypy syntax is compatible with Python. Mypy programs are normal
  Python programs that can be run using any Python
  implementation. Cython has many incompatible extensions to Python
  syntax, and Cython programs generally cannot be run without first
  compiling them to CPython extension modules via C. Cython also has a
  pure Python mode, but it seems to support only a subset of Cython
  functionality, and the syntax is quite verbose.

- Mypy has a different set of type system features. For example, mypy
  has genericity (parametric polymorphism), function types and
  bidirectional type inference, which are not supported by
  Cython. (Cython has fused types that are different but related to
  mypy generics. Mypy also has a similar feature as an extension of
  generics.)

- The mypy type checker knows about the static types of many Python
  stdlib modules and can effectively type check code that uses them.

- Cython supports accessing C functions directly and many features are
  defined in terms of translating them to C or C++. Mypy just uses
  Python semantics, and mypy does not deal with accessing C library
  functionality.

Does it run on PyPy?
*********************

Somewhat. With PyPy 3.8, mypy is at least able to type check itself.
With older versions of PyPy, mypy relies on `typed-ast
<https://github.com/python/typed_ast>`_, which uses several APIs that
PyPy does not support (including some internal CPython APIs).

Mypy is a cool project. Can I help?
***********************************

Any help is much appreciated! `Contact
<https://www.mypy-lang.org/contact.html>`_ the developers if you would
like to contribute. Any help related to development, design,
publicity, documentation, testing, web site maintenance, financing,
etc. can be helpful. You can learn a lot by contributing, and anybody
can help, even beginners! However, some knowledge of compilers and/or
type systems is essential if you want to work on mypy internals.
````

## File: docs/source/final_attrs.rst
````
.. _final_attrs:

Final names, methods and classes
================================

This section introduces these related features:

1. *Final names* are variables or attributes that should not be reassigned after
   initialization. They are useful for declaring constants.
2. *Final methods* should not be overridden in a subclass.
3. *Final classes* should not be subclassed.

All of these are only enforced by mypy, and only in annotated code.
There is no runtime enforcement by the Python runtime.

.. note::

    The examples in this page import ``Final`` and ``final`` from the
    ``typing`` module. These types were added to ``typing`` in Python 3.8,
    but are also available for use in Python 3.4 - 3.7 via the
    ``typing_extensions`` package.

Final names
-----------

You can use the ``typing.Final`` qualifier to indicate that
a name or attribute should not be reassigned, redefined, or
overridden. This is often useful for module and class-level
constants to prevent unintended modification. Mypy will prevent
further assignments to final names in type-checked code:

.. code-block:: python

   from typing import Final

   RATE: Final = 3_000

   class Base:
       DEFAULT_ID: Final = 0

   RATE = 300  # Error: can't assign to final attribute
   Base.DEFAULT_ID = 1  # Error: can't override a final attribute

Another use case for final attributes is to protect certain attributes
from being overridden in a subclass:

.. code-block:: python

   from typing import Final

   class Window:
       BORDER_WIDTH: Final = 2.5
       ...

   class ListView(Window):
       BORDER_WIDTH = 3  # Error: can't override a final attribute

You can use :py:class:`@property <property>` to make an attribute read-only, but unlike ``Final``,
it doesn't work with module attributes, and it doesn't prevent overriding in
subclasses.

Syntax variants
***************

You can use ``Final`` in one of these forms:

* You can provide an explicit type using the syntax ``Final[<type>]``. Example:

  .. code-block:: python

     ID: Final[int] = 1

  Here, mypy will infer type ``int`` for ``ID``.

* You can omit the type:

  .. code-block:: python

     ID: Final = 1

  Here, mypy will infer type ``Literal[1]`` for ``ID``. Note that unlike for
  generic classes, this is *not* the same as ``Final[Any]``.

* In class bodies and stub files, you can omit the right-hand side and just write
  ``ID: Final[int]``.

* Finally, you can write ``self.id: Final = 1`` (also optionally with
  a type in square brackets). This is allowed *only* in
  :py:meth:`__init__ <object.__init__>` methods so the final instance attribute is
  assigned only once when an instance is created.

Details of using ``Final``
**************************

These are the two main rules for defining a final name:

* There can be *at most one* final declaration per module or class for
  a given attribute. There can't be separate class-level and instance-level
  constants with the same name.

* There must be *exactly one* assignment to a final name.

A final attribute declared in a class body without an initializer must
be initialized in the :py:meth:`__init__ <object.__init__>` method (you can skip the
initializer in stub files):

.. code-block:: python

   class ImmutablePoint:
       x: Final[int]
       y: Final[int]  # Error: final attribute without an initializer

       def __init__(self) -> None:
           self.x = 1  # Good

``Final`` can only be used as the outermost type in assignments or variable
annotations. Using it in any other position is an error. In particular,
``Final`` can't be used in annotations for function arguments:

.. code-block:: python

   x: list[Final[int]] = []  # Error!

   def fun(x: Final[list[int]]) ->  None:  # Error!
       ...

``Final`` and :py:data:`~typing.ClassVar` should not be used together. Mypy will infer
the scope of a final declaration automatically depending on whether it was
initialized in the class body or in :py:meth:`__init__ <object.__init__>`.

A final attribute can't be overridden by a subclass (even with another
explicit final declaration). Note, however, that a final attribute can
override a read-only property:

.. code-block:: python

   class Base:
       @property
       def ID(self) -> int: ...

   class Derived(Base):
       ID: Final = 1  # OK

Declaring a name as final only guarantees that the name will not be re-bound
to another value. It doesn't make the value immutable. You can use immutable ABCs
and containers to prevent mutating such values:

.. code-block:: python

   x: Final = ['a', 'b']
   x.append('c')  # OK

   y: Final[Sequence[str]] = ['a', 'b']
   y.append('x')  # Error: Sequence is immutable
   z: Final = ('a', 'b')  # Also an option

Final methods
-------------

Like with attributes, sometimes it is useful to protect a method from
overriding. You can use the ``typing.final`` decorator for this purpose:

.. code-block:: python

   from typing import final

   class Base:
       @final
       def common_name(self) -> None:
           ...

   class Derived(Base):
       def common_name(self) -> None:  # Error: cannot override a final method
           ...

This ``@final`` decorator can be used with instance methods, class methods,
static methods, and properties.

For overloaded methods, you should add ``@final`` on the implementation
to make it final (or on the first overload in stubs):

.. code-block:: python

   from typing import final, overload

   class Base:
       @overload
       def method(self) -> None: ...
       @overload
       def method(self, arg: int) -> int: ...
       @final
       def method(self, x=None):
           ...

Final classes
-------------

You can apply the ``typing.final`` decorator to a class to indicate
to mypy that it should not be subclassed:

.. code-block:: python

   from typing import final

   @final
   class Leaf:
       ...

   class MyLeaf(Leaf):  # Error: Leaf can't be subclassed
       ...

The decorator acts as a declaration for mypy (and as documentation for
humans), but it doesn't actually prevent subclassing at runtime.

Here are some situations where using a final class may be useful:

* A class wasn't designed to be subclassed. Perhaps subclassing would not
  work as expected, or subclassing would be error-prone.
* Subclassing would make code harder to understand or maintain.
  For example, you may want to prevent unnecessarily tight coupling between
  base classes and subclasses.
* You want to retain the freedom to arbitrarily change the class implementation
  in the future, and these changes might break subclasses.

An abstract class that defines at least one abstract method or
property and has ``@final`` decorator will generate an error from
mypy since those attributes could never be implemented.

.. code-block:: python

    from abc import ABCMeta, abstractmethod
    from typing import final

    @final
    class A(metaclass=ABCMeta):  # error: Final class A has abstract attributes "f"
        @abstractmethod
        def f(self, x: int) -> None: pass
````

## File: docs/source/generics.rst
````
Generics
========

This section explains how you can define your own generic classes that take
one or more type arguments, similar to built-in types such as ``list[T]``.
User-defined generics are a moderately advanced feature and you can get far
without ever using them -- feel free to skip this section and come back later.

.. _generic-classes:

Defining generic classes
************************

The built-in collection classes are generic classes. Generic types
accept one or more type arguments within ``[...]``, which can be
arbitrary types. For example, the type ``dict[int, str]`` has the
type arguments ``int`` and ``str``, and ``list[int]`` has the type
argument ``int``.

Programs can also define new generic classes. Here is a very simple
generic class that represents a stack (using the syntax introduced in
Python 3.12):

.. code-block:: python

   class Stack[T]:
       def __init__(self) -> None:
           # Create an empty list with items of type T
           self.items: list[T] = []

       def push(self, item: T) -> None:
           self.items.append(item)

       def pop(self) -> T:
           return self.items.pop()

       def empty(self) -> bool:
           return not self.items

There are two syntax variants for defining generic classes in Python.
Python 3.12 introduced a
`new dedicated syntax <https://docs.python.org/3/whatsnew/3.12.html#pep-695-type-parameter-syntax>`_
for defining generic classes (and also functions and type aliases, which
we will discuss later). The above example used the new syntax. Most examples are
given using both the new and the old (or legacy) syntax variants.
Unless mentioned otherwise, they work the same -- but the new syntax
is more readable and more convenient.

Here is the same example using the old syntax (required for Python 3.11
and earlier, but also supported on newer Python versions):

.. code-block:: python

   from typing import TypeVar, Generic

   T = TypeVar('T')  # Define type variable "T"

   class Stack(Generic[T]):
       def __init__(self) -> None:
           # Create an empty list with items of type T
           self.items: list[T] = []

       def push(self, item: T) -> None:
           self.items.append(item)

       def pop(self) -> T:
           return self.items.pop()

       def empty(self) -> bool:
           return not self.items

.. note::

    There are currently no plans to deprecate the legacy syntax.
    You can freely mix code using the new and old syntax variants,
    even within a single file (but *not* within a single class).

The ``Stack`` class can be used to represent a stack of any type:
``Stack[int]``, ``Stack[tuple[int, str]]``, etc. You can think of
``Stack[int]`` as referring to the definition of ``Stack`` above,
but with all instances of ``T`` replaced with ``int``.

Using ``Stack`` is similar to built-in container types:

.. code-block:: python

   # Construct an empty Stack[int] instance
   stack = Stack[int]()
   stack.push(2)
   stack.pop()

   # error: Argument 1 to "push" of "Stack" has incompatible type "str"; expected "int"
   stack.push('x')

   stack2: Stack[str] = Stack()
   stack2.push('x')

Construction of instances of generic types is type checked (Python 3.12 syntax):

.. code-block:: python

   class Box[T]:
       def __init__(self, content: T) -> None:
           self.content = content

   Box(1)       # OK, inferred type is Box[int]
   Box[int](1)  # Also OK

   # error: Argument 1 to "Box" has incompatible type "str"; expected "int"
   Box[int]('some string')

Here is the definition of ``Box`` using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   from typing import TypeVar, Generic

   T = TypeVar('T')

   class Box(Generic[T]):
       def __init__(self, content: T) -> None:
           self.content = content

.. note::

    Before moving on, let's clarify some terminology.
    The name ``T`` in ``class Stack[T]`` or ``class Stack(Generic[T])``
    declares a *type parameter* ``T`` (of class ``Stack``).
    ``T`` is also called a *type variable*, especially in a type annotation,
    such as in the signature of ``push`` above.
    When the type ``Stack[...]`` is used in a type annotation, the type
    within square brackets is called a *type argument*.
    This is similar to the distinction between function parameters and arguments.

.. _generic-subclasses:

Defining subclasses of generic classes
**************************************

User-defined generic classes and generic classes defined in :py:mod:`typing`
can be used as a base class for another class (generic or non-generic). For
example (Python 3.12 syntax):

.. code-block:: python

   from typing import Mapping, Iterator

   # This is a generic subclass of Mapping
   class MyMap[KT, VT](Mapping[KT, VT]):
       def __getitem__(self, k: KT) -> VT: ...
       def __iter__(self) -> Iterator[KT]: ...
       def __len__(self) -> int: ...

   items: MyMap[str, int]  # OK

   # This is a non-generic subclass of dict
   class StrDict(dict[str, str]):
       def __str__(self) -> str:
           return f'StrDict({super().__str__()})'

   data: StrDict[int, int]  # Error! StrDict is not generic
   data2: StrDict  # OK

   # This is a user-defined generic class
   class Receiver[T]:
       def accept(self, value: T) -> None: ...

   # This is a generic subclass of Receiver
   class AdvancedReceiver[T](Receiver[T]): ...

Here is the above example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   from typing import Generic, TypeVar, Mapping, Iterator

   KT = TypeVar('KT')
   VT = TypeVar('VT')

   # This is a generic subclass of Mapping
   class MyMap(Mapping[KT, VT]):
       def __getitem__(self, k: KT) -> VT: ...
       def __iter__(self) -> Iterator[KT]: ...
       def __len__(self) -> int: ...

   items: MyMap[str, int]  # OK

   # This is a non-generic subclass of dict
   class StrDict(dict[str, str]):
       def __str__(self) -> str:
           return f'StrDict({super().__str__()})'

   data: StrDict[int, int]  # Error! StrDict is not generic
   data2: StrDict  # OK

   # This is a user-defined generic class
   class Receiver(Generic[T]):
       def accept(self, value: T) -> None: ...

   # This is a generic subclass of Receiver
   class AdvancedReceiver(Receiver[T]): ...

.. note::

    You have to add an explicit :py:class:`~collections.abc.Mapping` base class
    if you want mypy to consider a user-defined class as a mapping (and
    :py:class:`~collections.abc.Sequence` for sequences, etc.). This is because
    mypy doesn't use *structural subtyping* for these ABCs, unlike simpler protocols
    like :py:class:`~collections.abc.Iterable`, which use
    :ref:`structural subtyping <protocol-types>`.

When using the legacy syntax, :py:class:`Generic <typing.Generic>` can be omitted
from bases if there are
other base classes that include type variables, such as ``Mapping[KT, VT]``
in the above example. If you include ``Generic[...]`` in bases, then
it should list all type variables present in other bases (or more,
if needed). The order of type parameters is defined by the following
rules:

* If ``Generic[...]`` is present, then the order of parameters is
  always determined by their order in ``Generic[...]``.
* If there are no ``Generic[...]`` in bases, then all type parameters
  are collected in the lexicographic order (i.e. by first appearance).

Example:

.. code-block:: python

   from typing import Generic, TypeVar, Any

   T = TypeVar('T')
   S = TypeVar('S')
   U = TypeVar('U')

   class One(Generic[T]): ...
   class Another(Generic[T]): ...

   class First(One[T], Another[S]): ...
   class Second(One[T], Another[S], Generic[S, U, T]): ...

   x: First[int, str]        # Here T is bound to int, S is bound to str
   y: Second[int, str, Any]  # Here T is Any, S is int, and U is str

When using the Python 3.12 syntax, all type parameters must always be
explicitly defined immediately after the class name within ``[...]``, and the
``Generic[...]`` base class is never used.

.. _generic-functions:

Generic functions
*****************

Functions can also be generic, i.e. they can have type parameters (Python 3.12 syntax):

.. code-block:: python

   from collections.abc import Sequence

   # A generic function!
   def first[T](seq: Sequence[T]) -> T:
       return seq[0]

Here is the same example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   from typing import TypeVar, Sequence

   T = TypeVar('T')

   # A generic function!
   def first(seq: Sequence[T]) -> T:
       return seq[0]

As with generic classes, the type parameter ``T`` can be replaced with any
type. That means ``first`` can be passed an argument with any sequence type,
and the return type is derived from the sequence item type. Example:

.. code-block:: python

   reveal_type(first([1, 2, 3]))   # Revealed type is "builtins.int"
   reveal_type(first(('a', 'b')))  # Revealed type is "builtins.str"

When using the legacy syntax, a single definition of a type variable
(such as ``T`` above) can be used in multiple generic functions or
classes. In this example we use the same type variable in two generic
functions to declare type parameters:

.. code-block:: python

   from typing import TypeVar, Sequence

   T = TypeVar('T')      # Define type variable

   def first(seq: Sequence[T]) -> T:
       return seq[0]

   def last(seq: Sequence[T]) -> T:
       return seq[-1]

Since the Python 3.12 syntax is more concise, it doesn't need (or have)
an equivalent way of sharing type parameter definitions.

A variable cannot have a type variable in its type unless the type
variable is bound in a containing generic class or function.

When calling a generic function, you can't explicitly pass the values of
type parameters as type arguments. The values of type parameters are always
inferred by mypy. This is not valid:

.. code-block:: python

    first[int]([1, 2])  # Error: can't use [...] with generic function

If you really need this, you can define a generic class with a ``__call__``
method.

.. _type-variable-upper-bound:

Type variables with upper bounds
********************************

A type variable can also be restricted to having values that are
subtypes of a specific type. This type is called the upper bound of
the type variable, and it is specified using ``T: <bound>`` when using the
Python 3.12 syntax. In the definition of a generic function or a generic
class that uses such a type variable ``T``, the type represented by ``T``
is assumed to be a subtype of its upper bound, so you can use methods
of the upper bound on values of type ``T`` (Python 3.12 syntax):

.. code-block:: python

   from typing import SupportsAbs

   def max_by_abs[T: SupportsAbs[float]](*xs: T) -> T:
       # We can use abs(), because T is a subtype of SupportsAbs[float].
       return max(xs, key=abs)

An upper bound can also be specified with the ``bound=...`` keyword
argument to :py:class:`~typing.TypeVar`.
Here is the example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   from typing import TypeVar, SupportsAbs

   T = TypeVar('T', bound=SupportsAbs[float])

   def max_by_abs(*xs: T) -> T:
       return max(xs, key=abs)

In a call to such a function, the type ``T`` must be replaced by a
type that is a subtype of its upper bound. Continuing the example
above:

.. code-block:: python

   max_by_abs(-3.5, 2)   # Okay, has type 'float'
   max_by_abs(5+6j, 7)   # Okay, has type 'complex'
   max_by_abs('a', 'b')  # Error: 'str' is not a subtype of SupportsAbs[float]

Type parameters of generic classes may also have upper bounds, which
restrict the valid values for the type parameter in the same way.

.. _generic-methods-and-generic-self:

Generic methods and generic self
********************************

You can also define generic methods. In
particular, the ``self`` parameter may also be generic, allowing a
method to return the most precise type known at the point of access.
In this way, for example, you can type check a chain of setter
methods (Python 3.12 syntax):

.. code-block:: python

   class Shape:
       def set_scale[T: Shape](self: T, scale: float) -> T:
           self.scale = scale
           return self

   class Circle(Shape):
       def set_radius(self, r: float) -> 'Circle':
           self.radius = r
           return self

   class Square(Shape):
       def set_width(self, w: float) -> 'Square':
           self.width = w
           return self

   circle: Circle = Circle().set_scale(0.5).set_radius(2.7)
   square: Square = Square().set_scale(0.5).set_width(3.2)

Without using generic ``self``, the last two lines could not be type
checked properly, since the return type of ``set_scale`` would be
``Shape``, which doesn't define ``set_radius`` or ``set_width``.

When using the legacy syntax, just use a type variable in the
method signature that is different from class type parameters (if any
are defined). Here is the above example using the legacy
syntax (3.11 and earlier):

.. code-block:: python

   from typing import TypeVar

   T = TypeVar('T', bound='Shape')

   class Shape:
       def set_scale(self: T, scale: float) -> T:
           self.scale = scale
           return self

   class Circle(Shape):
       def set_radius(self, r: float) -> 'Circle':
           self.radius = r
           return self

   class Square(Shape):
       def set_width(self, w: float) -> 'Square':
           self.width = w
           return self

   circle: Circle = Circle().set_scale(0.5).set_radius(2.7)
   square: Square = Square().set_scale(0.5).set_width(3.2)

Other uses include factory methods, such as copy and deserialization methods.
For class methods, you can also define generic ``cls``, using ``type[T]``
or :py:class:`Type[T] <typing.Type>` (Python 3.12 syntax):

.. code-block:: python

   class Friend:
       other: "Friend | None" = None

       @classmethod
       def make_pair[T: Friend](cls: type[T]) -> tuple[T, T]:
           a, b = cls(), cls()
           a.other = b
           b.other = a
           return a, b

   class SuperFriend(Friend):
       pass

   a, b = SuperFriend.make_pair()

Here is the same example using the legacy syntax (3.11 and earlier):

.. code-block:: python

   from typing import TypeVar

   T = TypeVar('T', bound='Friend')

   class Friend:
       other: "Friend | None" = None

       @classmethod
       def make_pair(cls: type[T]) -> tuple[T, T]:
           a, b = cls(), cls()
           a.other = b
           b.other = a
           return a, b

   class SuperFriend(Friend):
       pass

   a, b = SuperFriend.make_pair()

Note that when overriding a method with generic ``self``, you must either
return a generic ``self`` too, or return an instance of the current class.
In the latter case, you must implement this method in all future subclasses.

Note also that mypy cannot always verify that the implementation of a copy
or a deserialization method returns the actual type of self. Therefore
you may need to silence mypy inside these methods (but not at the call site),
possibly by making use of the ``Any`` type or a ``# type: ignore`` comment.

Mypy lets you use generic self types in certain unsafe ways
in order to support common idioms. For example, using a generic
self type in an argument type is accepted even though it's unsafe (Python 3.12
syntax):

.. code-block:: python

   class Base:
       def compare[T: Base](self: T, other: T) -> bool:
           return False

   class Sub(Base):
       def __init__(self, x: int) -> None:
           self.x = x

       # This is unsafe (see below) but allowed because it's
       # a common pattern and rarely causes issues in practice.
       def compare(self, other: 'Sub') -> bool:
           return self.x > other.x

   b: Base = Sub(42)
   b.compare(Base())  # Runtime error here: 'Base' object has no attribute 'x'

For some advanced uses of self types, see :ref:`additional examples <advanced_self>`.

Automatic self types using typing.Self
**************************************

Since the patterns described above are quite common, mypy supports a
simpler syntax, introduced in :pep:`673`, to make them easier to use.
Instead of introducing a type parameter and using an explicit annotation
for ``self``, you can import the special type ``typing.Self`` that is
automatically transformed into a method-level type parameter with the
current class as the upper bound, and you don't need an annotation for
``self`` (or ``cls`` in class methods). The example from the previous
section can be made simpler by using ``Self``:

.. code-block:: python

   from typing import Self

   class Friend:
       other: Self | None = None

       @classmethod
       def make_pair(cls) -> tuple[Self, Self]:
           a, b = cls(), cls()
           a.other = b
           b.other = a
           return a, b

   class SuperFriend(Friend):
       pass

   a, b = SuperFriend.make_pair()

This is more compact than using explicit type parameters. Also, you can
use ``Self`` in attribute annotations in addition to methods.

.. note::

   To use this feature on Python versions earlier than 3.11, you will need to
   import ``Self`` from ``typing_extensions`` (version 4.0 or newer).

.. _variance-of-generics:

Variance of generic types
*************************

There are three main kinds of generic types with respect to subtype
relations between them: invariant, covariant, and contravariant.
Assuming that we have a pair of types ``A`` and ``B``, and ``B`` is
a subtype of ``A``, these are defined as follows:

* A generic class ``MyCovGen[T]`` is called covariant in type variable
  ``T`` if ``MyCovGen[B]`` is always a subtype of ``MyCovGen[A]``.
* A generic class ``MyContraGen[T]`` is called contravariant in type
  variable ``T`` if ``MyContraGen[A]`` is always a subtype of
  ``MyContraGen[B]``.
* A generic class ``MyInvGen[T]`` is called invariant in ``T`` if neither
  of the above is true.

Let us illustrate this by few simple examples:

.. code-block:: python

    # We'll use these classes in the examples below
    class Shape: ...
    class Triangle(Shape): ...
    class Square(Shape): ...

* Most immutable container types, such as :py:class:`~collections.abc.Sequence`
  and :py:class:`~frozenset` are covariant. Union types are
  also covariant in all union items: ``Triangle | int`` is
  a subtype of ``Shape | int``.

  .. code-block:: python

    def count_lines(shapes: Sequence[Shape]) -> int:
        return sum(shape.num_sides for shape in shapes)

    triangles: Sequence[Triangle]
    count_lines(triangles)  # OK

    def foo(triangle: Triangle, num: int) -> None:
        shape_or_number: Union[Shape, int]
        # a Triangle is a Shape, and a Shape is a valid Union[Shape, int]
        shape_or_number = triangle

  Covariance should feel relatively intuitive, but contravariance and invariance
  can be harder to reason about.

* :py:class:`~collections.abc.Callable` is an example of type that behaves contravariant
  in types of arguments. That is, ``Callable[[Shape], int]`` is a subtype of
  ``Callable[[Triangle], int]``, despite ``Shape`` being a supertype of
  ``Triangle``. To understand this, consider:

  .. code-block:: python

    def cost_of_paint_required(
        triangle: Triangle,
        area_calculator: Callable[[Triangle], float]
    ) -> float:
        return area_calculator(triangle) * DOLLAR_PER_SQ_FT

    # This straightforwardly works
    def area_of_triangle(triangle: Triangle) -> float: ...
    cost_of_paint_required(triangle, area_of_triangle)  # OK

    # But this works as well!
    def area_of_any_shape(shape: Shape) -> float: ...
    cost_of_paint_required(triangle, area_of_any_shape)  # OK

  ``cost_of_paint_required`` needs a callable that can calculate the area of a
  triangle. If we give it a callable that can calculate the area of an
  arbitrary shape (not just triangles), everything still works.

* ``list`` is an invariant generic type. Naively, one would think
  that it is covariant, like :py:class:`~collections.abc.Sequence` above, but consider this code:

  .. code-block:: python

     class Circle(Shape):
         # The rotate method is only defined on Circle, not on Shape
         def rotate(self): ...

     def add_one(things: list[Shape]) -> None:
         things.append(Shape())

     my_circles: list[Circle] = []
     add_one(my_circles)     # This may appear safe, but...
     my_circles[0].rotate()  # ...this will fail, since my_circles[0] is now a Shape, not a Circle

  Another example of invariant type is ``dict``. Most mutable containers
  are invariant.

When using the Python 3.12 syntax for generics, mypy will automatically
infer the most flexible variance for each class type variable. Here
``Box`` will be inferred as covariant:

.. code-block:: python

   class Box[T]:  # this type is implicitly covariant
       def __init__(self, content: T) -> None:
           self._content = content

       def get_content(self) -> T:
           return self._content

   def look_into(box: Box[Shape]): ...

   my_box = Box(Square())
   look_into(my_box)  # OK, but mypy would complain here for an invariant type

Here the underscore prefix for ``_content`` is significant. Without an
underscore prefix, the class would be invariant, as the attribute would
be understood as a public, mutable attribute (a single underscore prefix
has no special significance for mypy in most other contexts). By declaring
the attribute as ``Final``, the class could still be made covariant:

.. code-block:: python

   from typing import Final

   class Box[T]:  # this type is implicitly covariant
       def __init__(self, content: T) -> None:
           self.content: Final = content

       def get_content(self) -> T:
           return self.content

When using the legacy syntax, mypy assumes that all user-defined generics
are invariant by default. To declare a given generic class as covariant or
contravariant, use type variables defined with special keyword arguments
``covariant`` or ``contravariant``. For example (Python 3.11 or earlier):

.. code-block:: python

   from typing import Generic, TypeVar

   T_co = TypeVar('T_co', covariant=True)

   class Box(Generic[T_co]):  # this type is declared covariant
       def __init__(self, content: T_co) -> None:
           self._content = content

       def get_content(self) -> T_co:
           return self._content

   def look_into(box: Box[Shape]): ...

   my_box = Box(Square())
   look_into(my_box)  # OK, but mypy would complain here for an invariant type

.. _type-variable-value-restriction:

Type variables with value restriction
*************************************

By default, a type variable can be replaced with any type -- or any type that
is a subtype of the upper bound, which defaults to ``object``. However, sometimes
it's useful to have a type variable that can only have some specific types
as its value. A typical example is a type variable that can only have values
``str`` and ``bytes``. This lets us define a function that can concatenate
two strings or bytes objects, but it can't be called with other argument
types (Python 3.12 syntax):

.. code-block:: python

   def concat[S: (str, bytes)](x: S, y: S) -> S:
       return x + y

   concat('a', 'b')    # Okay
   concat(b'a', b'b')  # Okay
   concat(1, 2)        # Error!


The same thing is also possibly using the legacy syntax (Python 3.11 or earlier):

.. code-block:: python

   from typing import TypeVar

   AnyStr = TypeVar('AnyStr', str, bytes)

   def concat(x: AnyStr, y: AnyStr) -> AnyStr:
       return x + y

No matter which syntax you use, such a type variable is called a type variable
with a value restriction. Importantly, this is different from a union type,
since combinations of ``str`` and ``bytes`` are not accepted:

.. code-block:: python

   concat('string', b'bytes')   # Error!

In this case, this is exactly what we want, since it's not possible
to concatenate a string and a bytes object! If we tried to use
a union type, the type checker would complain about this possibility:

.. code-block:: python

   def union_concat(x: str | bytes, y: str | bytes) -> str | bytes:
       return x + y  # Error: can't concatenate str and bytes

Another interesting special case is calling ``concat()`` with a
subtype of ``str``:

.. code-block:: python

    class S(str): pass

    ss = concat(S('foo'), S('bar'))
    reveal_type(ss)  # Revealed type is "builtins.str"

You may expect that the type of ``ss`` is ``S``, but the type is
actually ``str``: a subtype gets promoted to one of the valid values
for the type variable, which in this case is ``str``.

This is thus subtly different from using ``str | bytes`` as an upper bound,
where the return type would be ``S`` (see :ref:`type-variable-upper-bound`).
Using a value restriction is correct for ``concat``, since ``concat``
actually returns a ``str`` instance in the above example:

.. code-block:: python

    >>> print(type(ss))
    <class 'str'>

You can also use type variables with a restricted set of possible
values when defining a generic class. For example, the type
:py:class:`Pattern[S] <typing.Pattern>` is used for the return
value of :py:func:`re.compile`, where ``S`` can be either ``str``
or ``bytes``. Regular expressions can be based on a string or a
bytes pattern.

A type variable may not have both a value restriction and an upper bound.

Note that you may come across :py:data:`~typing.AnyStr` imported from
:py:mod:`typing`. This feature is now deprecated, but it means the same
as our definition of ``AnyStr`` above.

.. _declaring-decorators:

Declaring decorators
********************

Decorators are typically functions that take a function as an argument and
return another function. Describing this behaviour in terms of types can
be a little tricky; we'll show how you can use type variables and a special
kind of type variable called a *parameter specification* to do so.

Suppose we have the following decorator, not type annotated yet,
that preserves the original function's signature and merely prints the decorated
function's name:

.. code-block:: python

   def printing_decorator(func):
       def wrapper(*args, **kwds):
           print("Calling", func)
           return func(*args, **kwds)
       return wrapper

We can use it to decorate function ``add_forty_two``:

.. code-block:: python

   # A decorated function.
   @printing_decorator
   def add_forty_two(value: int) -> int:
       return value + 42

   a = add_forty_two(3)

Since ``printing_decorator`` is not type-annotated, the following won't get type checked:

.. code-block:: python

   reveal_type(a)        # Revealed type is "Any"
   add_forty_two('foo')  # No type checker error :(

This is a sorry state of affairs! If you run with ``--strict``, mypy will
even alert you to this fact:
``Untyped decorator makes function "add_forty_two" untyped``

Note that class decorators are handled differently than function decorators in
mypy: decorating a class does not erase its type, even if the decorator has
incomplete type annotations.

Here's how one could annotate the decorator (Python 3.12 syntax):

.. code-block:: python

   from collections.abc import Callable
   from typing import Any, cast

   # A decorator that preserves the signature.
   def printing_decorator[F: Callable[..., Any]](func: F) -> F:
       def wrapper(*args, **kwds):
           print("Calling", func)
           return func(*args, **kwds)
       return cast(F, wrapper)

   @printing_decorator
   def add_forty_two(value: int) -> int:
       return value + 42

   a = add_forty_two(3)
   reveal_type(a)      # Revealed type is "builtins.int"
   add_forty_two('x')  # Argument 1 to "add_forty_two" has incompatible type "str"; expected "int"

Here is the example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   from collections.abc import Callable
   from typing import Any, TypeVar, cast

   F = TypeVar('F', bound=Callable[..., Any])

   # A decorator that preserves the signature.
   def printing_decorator(func: F) -> F:
       def wrapper(*args, **kwds):
           print("Calling", func)
           return func(*args, **kwds)
       return cast(F, wrapper)

   @printing_decorator
   def add_forty_two(value: int) -> int:
       return value + 42

   a = add_forty_two(3)
   reveal_type(a)      # Revealed type is "builtins.int"
   add_forty_two('x')  # Argument 1 to "add_forty_two" has incompatible type "str"; expected "int"

This still has some shortcomings. First, we need to use the unsafe
:py:func:`~typing.cast` to convince mypy that ``wrapper()`` has the same
signature as ``func`` (see :ref:`casts <casts>`).

Second, the ``wrapper()`` function is not tightly type checked, although
wrapper functions are typically small enough that this is not a big
problem. This is also the reason for the :py:func:`~typing.cast` call in the
``return`` statement in ``printing_decorator()``.

However, we can use a parameter specification, introduced using ``**P``,
for a more faithful type annotation (Python 3.12 syntax):

.. code-block:: python

   from collections.abc import Callable

   def printing_decorator[**P, T](func: Callable[P, T]) -> Callable[P, T]:
       def wrapper(*args: P.args, **kwds: P.kwargs) -> T:
           print("Calling", func)
           return func(*args, **kwds)
       return wrapper

The same is possible using the legacy syntax with :py:class:`~typing.ParamSpec`
(Python 3.11 and earlier):

.. code-block:: python

   from collections.abc import Callable
   from typing import TypeVar
   from typing_extensions import ParamSpec

   P = ParamSpec('P')
   T = TypeVar('T')

   def printing_decorator(func: Callable[P, T]) -> Callable[P, T]:
       def wrapper(*args: P.args, **kwds: P.kwargs) -> T:
           print("Calling", func)
           return func(*args, **kwds)
       return wrapper

Parameter specifications also allow you to describe decorators that
alter the signature of the input function (Python 3.12 syntax):

.. code-block:: python

   from collections.abc import Callable

   # We reuse 'P' in the return type, but replace 'T' with 'str'
   def stringify[**P, T](func: Callable[P, T]) -> Callable[P, str]:
       def wrapper(*args: P.args, **kwds: P.kwargs) -> str:
           return str(func(*args, **kwds))
       return wrapper

    @stringify
    def add_forty_two(value: int) -> int:
        return value + 42

    a = add_forty_two(3)
    reveal_type(a)      # Revealed type is "builtins.str"
    add_forty_two('x')  # error: Argument 1 to "add_forty_two" has incompatible type "str"; expected "int"

Here is the above example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   from collections.abc import Callable
   from typing import TypeVar
   from typing_extensions import ParamSpec

   P = ParamSpec('P')
   T = TypeVar('T')

   # We reuse 'P' in the return type, but replace 'T' with 'str'
   def stringify(func: Callable[P, T]) -> Callable[P, str]:
       def wrapper(*args: P.args, **kwds: P.kwargs) -> str:
           return str(func(*args, **kwds))
       return wrapper

You can also insert an argument in a decorator (Python 3.12 syntax):

.. code-block:: python

    from collections.abc import Callable
    from typing import Concatenate

    def printing_decorator[**P, T](func: Callable[P, T]) -> Callable[Concatenate[str, P], T]:
        def wrapper(msg: str, /, *args: P.args, **kwds: P.kwargs) -> T:
            print("Calling", func, "with", msg)
            return func(*args, **kwds)
        return wrapper

    @printing_decorator
    def add_forty_two(value: int) -> int:
        return value + 42

    a = add_forty_two('three', 3)

Here is the same function using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

    from collections.abc import Callable
    from typing import TypeVar
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec('P')
    T = TypeVar('T')

    def printing_decorator(func: Callable[P, T]) -> Callable[Concatenate[str, P], T]:
        def wrapper(msg: str, /, *args: P.args, **kwds: P.kwargs) -> T:
            print("Calling", func, "with", msg)
            return func(*args, **kwds)
        return wrapper

.. _decorator-factories:

Decorator factories
-------------------

Functions that take arguments and return a decorator (also called second-order decorators), are
similarly supported via generics (Python 3.12 syntax):

.. code-block:: python

    from collections.abc import Callable
    from typing import Any

    def route[F: Callable[..., Any]](url: str) -> Callable[[F], F]:
        ...

    @route(url='/')
    def index(request: Any) -> str:
        return 'Hello world'

Note that mypy infers that ``F`` is used to make the ``Callable`` return value
of ``route`` generic, instead of making ``route`` itself generic, since ``F`` is
only used in the return type. Python has no explicit syntax to mark that ``F``
is only bound in the return value.

Here is the example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

    from collections.abc import Callable
    from typing import Any, TypeVar

    F = TypeVar('F', bound=Callable[..., Any])

    def route(url: str) -> Callable[[F], F]:
        ...

    @route(url='/')
    def index(request: Any) -> str:
        return 'Hello world'

Sometimes the same decorator supports both bare calls and calls with arguments. This can be
achieved by combining with :py:func:`@overload <typing.overload>` (Python 3.12 syntax):

.. code-block:: python

    from collections.abc import Callable
    from typing import Any, overload

    # Bare decorator usage
    @overload
    def atomic[F: Callable[..., Any]](func: F, /) -> F: ...
    # Decorator with arguments
    @overload
    def atomic[F: Callable[..., Any]](*, savepoint: bool = True) -> Callable[[F], F]: ...

    # Implementation
    def atomic(func: Callable[..., Any] | None = None, /, *, savepoint: bool = True):
        def decorator(func: Callable[..., Any]):
            ...  # Code goes here
        if __func is not None:
            return decorator(__func)
        else:
            return decorator

    # Usage
    @atomic
    def func1() -> None: ...

    @atomic(savepoint=False)
    def func2() -> None: ...

Here is the decorator from the example using the legacy syntax
(Python 3.11 and earlier):

.. code-block:: python

    from collections.abc import Callable
    from typing import Any, Optional, TypeVar, overload

    F = TypeVar('F', bound=Callable[..., Any])

    # Bare decorator usage
    @overload
    def atomic(func: F, /) -> F: ...
    # Decorator with arguments
    @overload
    def atomic(*, savepoint: bool = True) -> Callable[[F], F]: ...

    # Implementation
    def atomic(func: Optional[Callable[..., Any]] = None, /, *, savepoint: bool = True):
        ...  # Same as above

Generic protocols
*****************

Mypy supports generic protocols (see also :ref:`protocol-types`). Several
:ref:`predefined protocols <predefined_protocols>` are generic, such as
:py:class:`Iterable[T] <collections.abc.Iterable>`, and you can define additional
generic protocols. Generic protocols mostly follow the normal rules for
generic classes. Example (Python 3.12 syntax):

.. code-block:: python

   from typing import Protocol

   class Box[T](Protocol):
       content: T

   def do_stuff(one: Box[str], other: Box[bytes]) -> None:
       ...

   class StringWrapper:
       def __init__(self, content: str) -> None:
           self.content = content

   class BytesWrapper:
       def __init__(self, content: bytes) -> None:
           self.content = content

   do_stuff(StringWrapper('one'), BytesWrapper(b'other'))  # OK

   x: Box[float] = ...
   y: Box[int] = ...
   x = y  # Error -- Box is invariant

Here is the definition of ``Box`` from the above example using the legacy
syntax (Python 3.11 and earlier):

.. code-block:: python

   from typing import Protocol, TypeVar

   T = TypeVar('T')

   class Box(Protocol[T]):
       content: T

Note that ``class ClassName(Protocol[T])`` is allowed as a shorthand for
``class ClassName(Protocol, Generic[T])`` when using the legacy syntax,
as per :pep:`PEP 544: Generic protocols <544#generic-protocols>`.
This form is only valid when using the legacy syntax.

When using the legacy syntax, there is an important difference between
generic protocols and ordinary generic classes: mypy checks that the
declared variances of generic type variables in a protocol match how
they are used in the protocol definition.  The protocol in this example
is rejected, since the type variable ``T`` is used covariantly as
a return type, but the type variable is invariant:

.. code-block:: python

   from typing import Protocol, TypeVar

   T = TypeVar('T')

   class ReadOnlyBox(Protocol[T]):  # error: Invariant type variable "T" used in protocol where covariant one is expected
       def content(self) -> T: ...

This example correctly uses a covariant type variable:

.. code-block:: python

   from typing import Protocol, TypeVar

   T_co = TypeVar('T_co', covariant=True)

   class ReadOnlyBox(Protocol[T_co]):  # OK
       def content(self) -> T_co: ...

   ax: ReadOnlyBox[float] = ...
   ay: ReadOnlyBox[int] = ...
   ax = ay  # OK -- ReadOnlyBox is covariant

See :ref:`variance-of-generics` for more about variance.

Generic protocols can also be recursive. Example (Python 3.12 synta):

.. code-block:: python

   class Linked[T](Protocol):
       val: T
       def next(self) -> 'Linked[T]': ...

   class L:
       val: int
       def next(self) -> 'L': ...

   def last(seq: Linked[T]) -> T: ...

   result = last(L())
   reveal_type(result)  # Revealed type is "builtins.int"

Here is the definition of ``Linked`` using the legacy syntax
(Python 3.11 and earlier):

.. code-block:: python

   from typing import TypeVar

   T = TypeVar('T')

   class Linked(Protocol[T]):
       val: T
       def next(self) -> 'Linked[T]': ...

.. _generic-type-aliases:

Generic type aliases
********************

Type aliases can be generic. In this case they can be used in two ways.
First, subscripted aliases are equivalent to original types with substituted type
variables. Second, unsubscripted aliases are treated as original types with type
parameters replaced with ``Any``.

The ``type`` statement introduced in Python 3.12 is used to define generic
type aliases (it also supports non-generic type aliases):

.. code-block:: python

    from collections.abc import Callable, Iterable

    type TInt[S] = tuple[int, S]
    type UInt[S] = S | int
    type CBack[S] = Callable[..., S]

    def response(query: str) -> UInt[str]:  # Same as str | int
        ...
    def activate[S](cb: CBack[S]) -> S:        # Same as Callable[..., S]
        ...
    table_entry: TInt  # Same as tuple[int, Any]

    type Vec[T: (int, float, complex)] = Iterable[tuple[T, T]]

    def inproduct[T: (int, float, complex)](v: Vec[T]) -> T:
        return sum(x*y for x, y in v)

    def dilate[T: (int, float, complex)](v: Vec[T], scale: T) -> Vec[T]:
        return ((x * scale, y * scale) for x, y in v)

    v1: Vec[int] = []      # Same as Iterable[tuple[int, int]]
    v2: Vec = []           # Same as Iterable[tuple[Any, Any]]
    v3: Vec[int, int] = [] # Error: Invalid alias, too many type arguments!

There is also a legacy syntax that relies on ``TypeVar``.
Here the number of type arguments must match the number of free type variables
in the generic type alias definition. A type variables is free if it's not
a type parameter of a surrounding class or function. Example (following
:pep:`PEP 484: Type aliases <484#type-aliases>`, Python 3.11 and earlier):

.. code-block:: python

    from typing import TypeVar, Iterable, Union, Callable

    S = TypeVar('S')

    TInt = tuple[int, S]  # 1 type parameter, since only S is free
    UInt = Union[S, int]
    CBack = Callable[..., S]

    def response(query: str) -> UInt[str]:  # Same as Union[str, int]
        ...
    def activate(cb: CBack[S]) -> S:        # Same as Callable[..., S]
        ...
    table_entry: TInt  # Same as tuple[int, Any]

    T = TypeVar('T', int, float, complex)

    Vec = Iterable[tuple[T, T]]

    def inproduct(v: Vec[T]) -> T:
        return sum(x*y for x, y in v)

    def dilate(v: Vec[T], scale: T) -> Vec[T]:
        return ((x * scale, y * scale) for x, y in v)

    v1: Vec[int] = []      # Same as Iterable[tuple[int, int]]
    v2: Vec = []           # Same as Iterable[tuple[Any, Any]]
    v3: Vec[int, int] = [] # Error: Invalid alias, too many type arguments!

Type aliases can be imported from modules just like other names. An
alias can also target another alias, although building complex chains
of aliases is not recommended -- this impedes code readability, thus
defeating the purpose of using aliases.  Example (Python 3.12 syntax):

.. code-block:: python

    from example1 import AliasType
    from example2 import Vec

    # AliasType and Vec are type aliases (Vec as defined above)

    def fun() -> AliasType:
        ...

    type OIntVec = Vec[int] | None

Type aliases defined using the ``type`` statement are not valid as
base classes, and they can't be used to construct instances:

.. code-block:: python

    from example1 import AliasType
    from example2 import Vec

    # AliasType and Vec are type aliases (Vec as defined above)

    class NewVec[T](Vec[T]):  # Error: not valid as base class
        ...

    x = AliasType()  # Error: can't be used to create instances

Here are examples using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

    from typing import TypeVar, Generic, Optional
    from example1 import AliasType
    from example2 import Vec

    # AliasType and Vec are type aliases (Vec as defined above)

    def fun() -> AliasType:
        ...

    OIntVec = Optional[Vec[int]]

    T = TypeVar('T')

    # Old-style type aliases can be used as base classes and you can
    # construct instances using them

    class NewVec(Vec[T]):
        ...

    x = AliasType()

    for i, j in NewVec[int]():
        ...

Using type variable bounds or value restriction in generic aliases has
the same effect as in generic classes and functions.


Differences between the new and old syntax
******************************************

There are a few notable differences between the new (Python 3.12 and later)
and the old syntax for generic classes, functions and type aliases, beyond
the obvious syntactic differences:

 * Type variables defined using the old syntax create definitions at runtime
   in the surrounding namespace, whereas the type variables defined using the
   new syntax are only defined within the class, function or type variable
   that uses them.
 * Type variable definitions can be shared when using the old syntax, but
   the new syntax doesn't support this.
 * When using the new syntax, the variance of class type variables is always
   inferred.
 * Type aliases defined using the new syntax can contain forward references
   and recursive references without using string literal escaping. The
   same is true for the bounds and constraints of type variables.
 * The new syntax lets you define a generic alias where the definition doesn't
   contain a reference to a type parameter. This is occasionally useful, at
   least when conditionally defining type aliases.
 * Type aliases defined using the new syntax can't be used as base classes
   and can't be used to construct instances, unlike aliases defined using the
   old syntax.


Generic class internals
***********************

You may wonder what happens at runtime when you index a generic class.
Indexing returns a *generic alias* to the original class that returns instances
of the original class on instantiation (Python 3.12 syntax):

.. code-block:: python

   >>> class Stack[T]: ...
   >>> Stack
   __main__.Stack
   >>> Stack[int]
   __main__.Stack[int]
   >>> instance = Stack[int]()
   >>> instance.__class__
   __main__.Stack

Here is the same example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   >>> from typing import TypeVar, Generic
   >>> T = TypeVar('T')
   >>> class Stack(Generic[T]): ...
   >>> Stack
   __main__.Stack
   >>> Stack[int]
   __main__.Stack[int]
   >>> instance = Stack[int]()
   >>> instance.__class__
   __main__.Stack

Generic aliases can be instantiated or subclassed, similar to real
classes, but the above examples illustrate that type variables are
erased at runtime. Generic ``Stack`` instances are just ordinary
Python objects, and they have no extra runtime overhead or magic due
to being generic, other than the ``Generic`` base class that overloads
the indexing operator using ``__class_getitem__``. ``typing.Generic``
is included as an implicit base class even when using the new syntax:

.. code-block:: python

   >>> class Stack[T]: ...
   >>> Stack.mro()
   [<class '__main__.Stack'>, <class 'typing.Generic'>, <class 'object'>]

Note that in Python 3.8 and earlier, the built-in types
:py:class:`list`, :py:class:`dict` and others do not support indexing.
This is why we have the aliases :py:class:`~typing.List`,
:py:class:`~typing.Dict` and so on in the :py:mod:`typing`
module. Indexing these aliases gives you a generic alias that
resembles generic aliases constructed by directly indexing the target
class in more recent versions of Python:

.. code-block:: python

   >>> # Only relevant for Python 3.8 and below
   >>> # If using Python 3.9 or newer, prefer the 'list[int]' syntax
   >>> from typing import List
   >>> List[int]
   typing.List[int]

Note that the generic aliases in ``typing`` don't support constructing
instances, unlike the corresponding built-in classes:

.. code-block:: python

   >>> list[int]()
   []
   >>> from typing import List
   >>> List[int]()
   Traceback (most recent call last):
   ...
   TypeError: Type List cannot be instantiated; use list() instead
````

## File: docs/source/getting_started.rst
````
.. _getting-started:

Getting started
===============

This chapter introduces some core concepts of mypy, including function
annotations, the :py:mod:`typing` module, stub files, and more.

If you're looking for a quick intro, see the
:ref:`mypy cheatsheet <cheat-sheet-py3>`.

If you're unfamiliar with the concepts of static and dynamic type checking,
be sure to read this chapter carefully, as the rest of the documentation
may not make much sense otherwise.

Installing and running mypy
***************************

Mypy requires Python 3.9 or later to run.  You can install mypy using pip:

.. code-block:: shell

    $ python3 -m pip install mypy

Once mypy is installed, run it by using the ``mypy`` tool:

.. code-block:: shell

    $ mypy program.py

This command makes mypy *type check* your ``program.py`` file and print
out any errors it finds. Mypy will type check your code *statically*: this
means that it will check for errors without ever running your code, just
like a linter.

This also means that you are always free to ignore the errors mypy reports,
if you so wish. You can always use the Python interpreter to run your code,
even if mypy reports errors.

However, if you try directly running mypy on your existing Python code, it
will most likely report little to no errors. This is a feature! It makes it
easy to adopt mypy incrementally.

In order to get useful diagnostics from mypy, you must add *type annotations*
to your code. See the section below for details.

.. _getting-started-dynamic-vs-static:

Dynamic vs static typing
************************

A function without type annotations is considered to be *dynamically typed* by mypy:

.. code-block:: python

   def greeting(name):
       return 'Hello ' + name

By default, mypy will **not** type check dynamically typed functions. This means
that with a few exceptions, mypy will not report any errors with regular unannotated Python.

This is the case even if you misuse the function!

.. code-block:: python

   def greeting(name):
       return 'Hello ' + name

   # These calls will fail when the program runs, but mypy does not report an error
   # because "greeting" does not have type annotations.
   greeting(123)
   greeting(b"Alice")

We can get mypy to detect these kinds of bugs by adding *type annotations* (also
known as *type hints*). For example, you can tell mypy that ``greeting`` both accepts
and returns a string like so:

.. code-block:: python

   # The "name: str" annotation says that the "name" argument should be a string
   # The "-> str" annotation says that "greeting" will return a string
   def greeting(name: str) -> str:
       return 'Hello ' + name

This function is now *statically typed*: mypy will use the provided type hints
to detect incorrect use of the ``greeting`` function and incorrect use of
variables within the ``greeting`` function. For example:

.. code-block:: python

   def greeting(name: str) -> str:
       return 'Hello ' + name

   greeting(3)         # Argument 1 to "greeting" has incompatible type "int"; expected "str"
   greeting(b'Alice')  # Argument 1 to "greeting" has incompatible type "bytes"; expected "str"
   greeting("World!")  # No error

   def bad_greeting(name: str) -> str:
       return 'Hello ' * name  # Unsupported operand types for * ("str" and "str")

Being able to pick whether you want a function to be dynamically or statically
typed can be very helpful. For example, if you are migrating an existing
Python codebase to use static types, it's usually easier to migrate by incrementally
adding type hints to your code rather than adding them all at once. Similarly,
when you are prototyping a new feature, it may be convenient to initially implement
the code using dynamic typing and only add type hints later once the code is more stable.

Once you are finished migrating or prototyping your code, you can make mypy warn you
if you add a dynamic function by mistake by using the :option:`--disallow-untyped-defs <mypy --disallow-untyped-defs>`
flag. You can also get mypy to provide some limited checking of dynamically typed
functions by using the :option:`--check-untyped-defs <mypy --check-untyped-defs>` flag.
See :ref:`command-line` for more information on configuring mypy.

Strict mode and configuration
*****************************

Mypy has a *strict mode* that enables a number of additional checks,
like :option:`--disallow-untyped-defs <mypy --disallow-untyped-defs>`.

If you run mypy with the :option:`--strict <mypy --strict>` flag, you
will basically never get a type related error at runtime without a corresponding
mypy error, unless you explicitly circumvent mypy somehow.

However, this flag will probably be too aggressive if you are trying
to add static types to a large, existing codebase. See :ref:`existing-code`
for suggestions on how to handle that case.

Mypy is very configurable, so you can start with using ``--strict``
and toggle off individual checks. For instance, if you use many third
party libraries that do not have types,
:option:`--ignore-missing-imports <mypy --ignore-missing-imports>`
may be useful. See :ref:`getting-to-strict` for how to build up to ``--strict``.

See :ref:`command-line` and :ref:`config-file` for a complete reference on
configuration options.

More complex types
******************

So far, we've added type hints that use only basic concrete types like
``str`` and ``float``. What if we want to express more complex types,
such as "a list of strings" or "an iterable of ints"?

For example, to indicate that some function can accept a list of
strings, use the ``list[str]`` type (Python 3.9 and later):

.. code-block:: python

   def greet_all(names: list[str]) -> None:
       for name in names:
           print('Hello ' + name)

   names = ["Alice", "Bob", "Charlie"]
   ages = [10, 20, 30]

   greet_all(names)   # Ok!
   greet_all(ages)    # Error due to incompatible types

The :py:class:`list` type is an example of something called a *generic type*: it can
accept one or more *type parameters*. In this case, we *parameterized* :py:class:`list`
by writing ``list[str]``. This lets mypy know that ``greet_all`` accepts specifically
lists containing strings, and not lists containing ints or any other type.

In the above examples, the type signature is perhaps a little too rigid.
After all, there's no reason why this function must accept *specifically* a list --
it would run just fine if you were to pass in a tuple, a set, or any other custom iterable.

You can express this idea using :py:class:`collections.abc.Iterable`:

.. code-block:: python

   from collections.abc import Iterable  # or "from typing import Iterable"

   def greet_all(names: Iterable[str]) -> None:
       for name in names:
           print('Hello ' + name)

This behavior is actually a fundamental aspect of the PEP 484 type system: when
we annotate some variable with a type ``T``, we are actually telling mypy that
variable can be assigned an instance of ``T``, or an instance of a *subtype* of ``T``.
That is, ``list[str]`` is a subtype of ``Iterable[str]``.

This also applies to inheritance, so if you have a class ``Child`` that inherits from
``Parent``, then a value of type ``Child`` can be assigned to a variable of type ``Parent``.
For example, a ``RuntimeError`` instance can be passed to a function that is annotated
as taking an ``Exception``.

As another example, suppose you want to write a function that can accept *either*
ints or strings, but no other types. You can express this using a
union type. For example, ``int`` is a subtype of ``int | str``:

.. code-block:: python

   def normalize_id(user_id: int | str) -> str:
       if isinstance(user_id, int):
           return f'user-{100_000 + user_id}'
       else:
           return user_id

.. note::

    If using Python 3.9 or earlier, use ``typing.Union[int, str]`` instead of
    ``int | str``, or use ``from __future__ import annotations`` at the top of
    the file (see :ref:`runtime_troubles`).

The :py:mod:`typing` module contains many other useful types.

For a quick overview, look through the :ref:`mypy cheatsheet <cheat-sheet-py3>`.

For a detailed overview (including information on how to make your own
generic types or your own type aliases), look through the
:ref:`type system reference <overview-type-system-reference>`.

.. note::

   When adding types, the convention is to import types
   using the form ``from typing import <name>`` (as opposed to doing
   just ``import typing`` or ``import typing as t`` or ``from typing import *``).

   For brevity, we often omit imports from :py:mod:`typing` or :py:mod:`collections.abc`
   in code examples, but mypy will give an error if you use types such as
   :py:class:`~collections.abc.Iterable` without first importing them.

.. note::

   In some examples we use capitalized variants of types, such as
   ``List``, and sometimes we use plain ``list``. They are equivalent,
   but the prior variant is needed if you are using Python 3.8 or earlier.

Local type inference
********************

Once you have added type hints to a function (i.e. made it statically typed),
mypy will automatically type check that function's body. While doing so,
mypy will try and *infer* as many details as possible.

We saw an example of this in the ``normalize_id`` function above -- mypy understands
basic :py:func:`isinstance <isinstance>` checks and so can infer that the ``user_id`` variable was of
type ``int`` in the if-branch and of type ``str`` in the else-branch.

As another example, consider the following function. Mypy can type check this function
without a problem: it will use the available context and deduce that ``output`` must be
of type ``list[float]`` and that ``num`` must be of type ``float``:

.. code-block:: python

   def nums_below(numbers: Iterable[float], limit: float) -> list[float]:
       output = []
       for num in numbers:
           if num < limit:
               output.append(num)
       return output

For more details, see :ref:`type-inference-and-annotations`.

Types from libraries
********************

Mypy can also understand how to work with types from libraries that you use.

For instance, mypy comes out of the box with an intimate knowledge of the
Python standard library. For example, here is a function which uses the
``Path`` object from the :doc:`pathlib standard library module <python:library/pathlib>`:

.. code-block:: python

    from pathlib import Path

    def load_template(template_path: Path, name: str) -> str:
        # Mypy knows that `template_path` has a `read_text` method that returns a str
        template = template_path.read_text()
        # ...so it understands this line type checks
        return template.replace('USERNAME', name)

If a third party library you use :ref:`declares support for type checking <installed-packages>`,
mypy will type check your use of that library based on the type hints
it contains.

However, if the third party library does not have type hints, mypy will
complain about missing type information.

.. code-block:: text

  prog.py:1: error: Library stubs not installed for "yaml"
  prog.py:1: note: Hint: "python3 -m pip install types-PyYAML"
  prog.py:2: error: Library stubs not installed for "requests"
  prog.py:2: note: Hint: "python3 -m pip install types-requests"
  ...

In this case, you can provide mypy a different source of type information,
by installing a *stub* package. A stub package is a package that contains
type hints for another library, but no actual code.

.. code-block:: shell

  $ python3 -m pip install types-PyYAML types-requests

Stubs packages for a distribution are often named ``types-<distribution>``.
Note that a distribution name may be different from the name of the package that
you import. For example, ``types-PyYAML`` contains stubs for the ``yaml``
package.

For more discussion on strategies for handling errors about libraries without
type information, refer to :ref:`fix-missing-imports`.

For more information about stubs, see :ref:`stub-files`.

Next steps
**********

If you are in a hurry and don't want to read lots of documentation
before getting started, here are some pointers to quick learning
resources:

* Read the :ref:`mypy cheatsheet <cheat-sheet-py3>`.

* Read :ref:`existing-code` if you have a significant existing
  codebase without many type annotations.

* Read the `blog post <https://blog.zulip.org/2016/10/13/static-types-in-python-oh-mypy/>`_
  about the Zulip project's experiences with adopting mypy.

* If you prefer watching talks instead of reading, here are
  some ideas:

  * Carl Meyer:
    `Type Checked Python in the Real World <https://www.youtube.com/watch?v=pMgmKJyWKn8>`_
    (PyCon 2018)

  * Greg Price:
    `Clearer Code at Scale: Static Types at Zulip and Dropbox <https://www.youtube.com/watch?v=0c46YHS3RY8>`_
    (PyCon 2018)

* Look at :ref:`solutions to common issues <common_issues>` with mypy if
  you encounter problems.

* You can ask questions about mypy in the
  `mypy issue tracker <https://github.com/python/mypy/issues>`_ and
  typing `Gitter chat <https://gitter.im/python/typing>`_.

* For general questions about Python typing, try posting at
  `typing discussions <https://github.com/python/typing/discussions>`_.

You can also continue reading this document and skip sections that
aren't relevant for you. You don't need to read sections in order.
````

## File: docs/source/index.rst
````
.. Mypy documentation master file, created by
   sphinx-quickstart on Sun Sep 14 19:50:35 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mypy documentation!
==============================

Mypy is a static type checker for Python.

Type checkers help ensure that you're using variables and functions in your code
correctly. With mypy, add type hints (:pep:`484`)
to your Python programs, and mypy will warn you when you use those types
incorrectly.

Python is a dynamic language, so usually you'll only see errors in your code
when you attempt to run it. Mypy is a *static* checker, so it finds bugs
in your programs without even running them!

Here is a small example to whet your appetite:

.. code-block:: python

   number = input("What is your favourite number?")
   print("It is", number + 1)  # error: Unsupported operand types for + ("str" and "int")

Adding type hints for mypy does not interfere with the way your program would
otherwise run. Think of type hints as similar to comments! You can always use
the Python interpreter to run your code, even if mypy reports errors.

Mypy is designed with gradual typing in mind. This means you can add type
hints to your code base slowly and that you can always fall back to dynamic
typing when static typing is not convenient.

Mypy has a powerful and easy-to-use type system, supporting features such as
type inference, generics, callable types, tuple types, union types,
structural subtyping and more. Using mypy will make your programs easier to
understand, debug, and maintain.

.. note::

   Although mypy is production ready, there may be occasional changes
   that break backward compatibility. The mypy development team tries to
   minimize the impact of changes to user code. In case of a major breaking
   change, mypy's major version will be bumped.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: First steps

   getting_started
   cheat_sheet_py3
   existing_code

.. _overview-type-system-reference:

.. toctree::
   :maxdepth: 2
   :caption: Type system reference

   builtin_types
   type_inference_and_annotations
   kinds_of_types
   class_basics
   runtime_troubles
   protocols
   dynamic_typing
   type_narrowing
   duck_type_compatibility
   stubs
   generics
   more_types
   literal_types
   typed_dict
   final_attrs
   metaclasses

.. toctree::
   :maxdepth: 2
   :caption: Configuring and running mypy

   running_mypy
   command_line
   config_file
   inline_config
   mypy_daemon
   installed_packages
   extending_mypy
   stubgen
   stubtest

.. toctree::
   :maxdepth: 2
   :caption: Miscellaneous

   common_issues
   supported_python_features
   error_codes
   error_code_list
   error_code_list2
   additional_features
   faq
   changelog

.. toctree::
   :hidden:
   :caption: Project Links

   GitHub <https://github.com/python/mypy>
   Website <https://mypy-lang.org/>

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
````

## File: docs/source/inline_config.rst
````
.. _inline-config:

Inline configuration
====================

Mypy supports setting per-file configuration options inside files themselves
using ``# mypy:`` comments. For example:

.. code-block:: python

  # mypy: disallow-any-generics

Inline configuration comments take precedence over all other
configuration mechanisms.

Configuration comment format
****************************

Flags correspond to :ref:`config file flags <config-file>` but allow
hyphens to be substituted for underscores.

Values are specified using ``=``, but ``= True`` may be omitted:

.. code-block:: python

  # mypy: disallow-any-generics
  # mypy: always-true=FOO

Multiple flags can be separated by commas or placed on separate
lines. To include a comma as part of an option's value, place the
value inside quotes:

.. code-block:: python

  # mypy: disallow-untyped-defs, always-false="FOO,BAR"

Like in the configuration file, options that take a boolean value may be
inverted by adding ``no-`` to their name or by (when applicable)
swapping their prefix from ``disallow`` to ``allow`` (and vice versa):

.. code-block:: python

  # mypy: allow-untyped-defs, no-strict-optional
````

## File: docs/source/installed_packages.rst
````
.. _installed-packages:

Using installed packages
========================

Packages installed with pip can declare that they support type
checking. For example, the `aiohttp
<https://docs.aiohttp.org/en/stable/>`_ package has built-in support
for type checking.

Packages can also provide stubs for a library. For example,
``types-requests`` is a stub-only package that provides stubs for the
`requests <https://requests.readthedocs.io/en/master/>`_ package.
Stub packages are usually published from `typeshed
<https://github.com/python/typeshed>`_, a shared repository for Python
library stubs, and have a name of form ``types-<library>``. Note that
many stub packages are not maintained by the original maintainers of
the package.

The sections below explain how mypy can use these packages, and how
you can create such packages.

.. note::

   :pep:`561` specifies how a package can declare that it supports
   type checking.

.. note::

   New versions of stub packages often use type system features not
   supported by older, and even fairly recent mypy versions. If you
   pin to an older version of mypy (using ``requirements.txt``, for
   example), it is recommended that you also pin the versions of all
   your stub package dependencies.

.. note::

   Starting in mypy 0.900, most third-party package stubs must be
   installed explicitly. This decouples mypy and stub versioning,
   allowing stubs to updated without updating mypy. This also allows
   stubs not originally included with mypy to be installed. Earlier
   mypy versions included a fixed set of stubs for third-party
   packages.

Using installed packages with mypy (PEP 561)
********************************************

Typically mypy will automatically find and use installed packages that
support type checking or provide stubs. This requires that you install
the packages in the Python environment that you use to run mypy.  As
many packages don't support type checking yet, you may also have to
install a separate stub package, usually named
``types-<library>``. (See :ref:`fix-missing-imports` for how to deal
with libraries that don't support type checking and are also missing
stubs.)

If you have installed typed packages in another Python installation or
environment, mypy won't automatically find them. One option is to
install another copy of those packages in the environment in which you
installed mypy. Alternatively, you can use the
:option:`--python-executable <mypy --python-executable>` flag to point
to the Python executable for another environment, and mypy will find
packages installed for that Python executable.

Note that mypy does not support some more advanced import features,
such as zip imports and custom import hooks.

If you don't want to use installed packages that provide type
information at all, use the :option:`--no-site-packages <mypy
--no-site-packages>` flag to disable searching for installed packages.

Note that stub-only packages cannot be used with ``MYPYPATH``. If you
want mypy to find the package, it must be installed. For a package
``foo``, the name of the stub-only package (``foo-stubs``) is not a
legal package name, so mypy will not find it, unless it is installed
(see :pep:`PEP 561: Stub-only Packages <561#stub-only-packages>` for
more information).

Creating PEP 561 compatible packages
************************************

.. note::

  You can generally ignore this section unless you maintain a package on
  PyPI, or want to publish type information for an existing PyPI
  package.

:pep:`561` describes three main ways to distribute type
information:

1. A package has inline type annotations in the Python implementation.

2. A package ships :ref:`stub files <stub-files>` with type
   information alongside the Python implementation.

3. A package ships type information for another package separately as
   stub files (also known as a "stub-only package").

If you want to create a stub-only package for an existing library, the
simplest way is to contribute stubs to the `typeshed
<https://github.com/python/typeshed>`_ repository, and a stub package
will automatically be uploaded to PyPI.

If you would like to publish a library package to a package repository
yourself (e.g. on PyPI) for either internal or external use in type
checking, packages that supply type information via type comments or
annotations in the code should put a ``py.typed`` file in their
package directory. For example, here is a typical directory structure:

.. code-block:: text

    setup.py
    package_a/
        __init__.py
        lib.py
        py.typed

The ``setup.py`` file could look like this:

.. code-block:: python

    from setuptools import setup

    setup(
        name="SuperPackageA",
        author="Me",
        version="0.1",
        package_data={"package_a": ["py.typed"]},
        packages=["package_a"]
    )

Some packages have a mix of stub files and runtime files. These packages also
require a ``py.typed`` file. An example can be seen below:

.. code-block:: text

    setup.py
    package_b/
        __init__.py
        lib.py
        lib.pyi
        py.typed

The ``setup.py`` file might look like this:

.. code-block:: python

    from setuptools import setup

    setup(
        name="SuperPackageB",
        author="Me",
        version="0.1",
        package_data={"package_b": ["py.typed", "lib.pyi"]},
        packages=["package_b"]
    )

In this example, both ``lib.py`` and the ``lib.pyi`` stub file exist. At
runtime, the Python interpreter will use ``lib.py``, but mypy will use
``lib.pyi`` instead.

If the package is stub-only (not imported at runtime), the package should have
a prefix of the runtime package name and a suffix of ``-stubs``.
A ``py.typed`` file is not needed for stub-only packages. For example, if we
had stubs for ``package_c``, we might do the following:

.. code-block:: text

    setup.py
    package_c-stubs/
        __init__.pyi
        lib.pyi

The ``setup.py`` might look like this:

.. code-block:: python

    from setuptools import setup

    setup(
        name="SuperPackageC",
        author="Me",
        version="0.1",
        package_data={"package_c-stubs": ["__init__.pyi", "lib.pyi"]},
        packages=["package_c-stubs"]
    )

The instructions above are enough to ensure that the built wheels
contain the appropriate files. However, to ensure inclusion inside the
``sdist`` (``.tar.gz`` archive), you may also need to modify the
inclusion rules in your ``MANIFEST.in``:

.. code-block:: text

    global-include *.pyi
    global-include *.typed
````

## File: docs/source/kinds_of_types.rst
````
Kinds of types
==============

We've mostly restricted ourselves to built-in types until now. This
section introduces several additional kinds of types. You are likely
to need at least some of them to type check any non-trivial programs.

Class types
***********

Every class is also a valid type. Any instance of a subclass is also
compatible with all superclasses -- it follows that every value is compatible
with the :py:class:`object` type (and incidentally also the ``Any`` type, discussed
below). Mypy analyzes the bodies of classes to determine which methods and
attributes are available in instances. This example uses subclassing:

.. code-block:: python

   class A:
       def f(self) -> int:  # Type of self inferred (A)
           return 2

   class B(A):
       def f(self) -> int:
            return 3
       def g(self) -> int:
           return 4

   def foo(a: A) -> None:
       print(a.f())  # 3
       a.g()         # Error: "A" has no attribute "g"

   foo(B())  # OK (B is a subclass of A)

The Any type
************

A value with the ``Any`` type is dynamically typed. Mypy doesn't know
anything about the possible runtime types of such value. Any
operations are permitted on the value, and the operations are only checked
at runtime. You can use ``Any`` as an "escape hatch" when you can't use
a more precise type for some reason.

This should not be confused with the
:py:class:`object` type, which represents the set of all values.
Unlike ``object``, ``Any`` introduces type unsafety — see
:ref:`any-vs-object` for more.

``Any`` is compatible with every other type, and vice versa. You can freely
assign a value of type ``Any`` to a variable with a more precise type:

.. code-block:: python

   a: Any = None
   s: str = ''
   a = 2     # OK (assign "int" to "Any")
   s = a     # OK (assign "Any" to "str")

Declared (and inferred) types are ignored (or *erased*) at runtime. They are
basically treated as comments, and thus the above code does not
generate a runtime error, even though ``s`` gets an ``int`` value when
the program is run, while the declared type of ``s`` is actually
``str``! You need to be careful with ``Any`` types, since they let you
lie to mypy, and this could easily hide bugs.

If you do not define a function return value or argument types, these
default to ``Any``:

.. code-block:: python

   def show_heading(s) -> None:
       print('=== ' + s + ' ===')  # No static type checking, as s has type Any

   show_heading(1)  # OK (runtime error only; mypy won't generate an error)

You should give a statically typed function an explicit ``None``
return type even if it doesn't return a value, as this lets mypy catch
additional type errors:

.. code-block:: python

   def wait(t: float):  # Implicit Any return value
       print('Waiting...')
       time.sleep(t)

   if wait(2) > 1:   # Mypy doesn't catch this error!
       ...

If we had used an explicit ``None`` return type, mypy would have caught
the error:

.. code-block:: python

   def wait(t: float) -> None:
       print('Waiting...')
       time.sleep(t)

   if wait(2) > 1:   # Error: can't compare None and int
       ...

The ``Any`` type is discussed in more detail in section :ref:`dynamic-typing`.

.. note::

  A function without any types in the signature is dynamically
  typed. The body of a dynamically typed function is not checked
  statically, and local variables have implicit ``Any`` types.
  This makes it easier to migrate legacy Python code to mypy, as
  mypy won't complain about dynamically typed functions.

.. _tuple-types:

Tuple types
***********

The type ``tuple[T1, ..., Tn]`` represents a tuple with the item types ``T1``, ..., ``Tn``:

.. code-block:: python

   # Use `typing.Tuple` in Python 3.8 and earlier
   def f(t: tuple[int, str]) -> None:
       t = 1, 'foo'    # OK
       t = 'foo', 1    # Type check error

A tuple type of this kind has exactly a specific number of items (2 in
the above example). Tuples can also be used as immutable,
varying-length sequences. You can use the type ``tuple[T, ...]`` (with
a literal ``...`` -- it's part of the syntax) for this
purpose. Example:

.. code-block:: python

    def print_squared(t: tuple[int, ...]) -> None:
        for n in t:
            print(n, n ** 2)

    print_squared(())           # OK
    print_squared((1, 3, 5))    # OK
    print_squared([1, 2])       # Error: only a tuple is valid

.. note::

   Usually it's a better idea to use ``Sequence[T]`` instead of ``tuple[T, ...]``, as
   :py:class:`~collections.abc.Sequence` is also compatible with lists and other non-tuple sequences.

.. note::

   ``tuple[...]`` is valid as a base class in Python 3.6 and later, and
   always in stub files. In earlier Python versions you can sometimes work around this
   limitation by using a named tuple as a base class (see section :ref:`named-tuples`).

.. _callable-types:

Callable types (and lambdas)
****************************

You can pass around function objects and bound methods in statically
typed code. The type of a function that accepts arguments ``A1``, ..., ``An``
and returns ``Rt`` is ``Callable[[A1, ..., An], Rt]``. Example:

.. code-block:: python

   from collections.abc import Callable

   def twice(i: int, next: Callable[[int], int]) -> int:
       return next(next(i))

   def add(i: int) -> int:
       return i + 1

   print(twice(3, add))   # 5

.. note::

    Import :py:data:`Callable[...] <typing.Callable>` from ``typing`` instead
    of ``collections.abc`` if you use Python 3.8 or earlier.

You can only have positional arguments, and only ones without default
values, in callable types. These cover the vast majority of uses of
callable types, but sometimes this isn't quite enough. Mypy recognizes
a special form ``Callable[..., T]`` (with a literal ``...``) which can
be used in less typical cases. It is compatible with arbitrary
callable objects that return a type compatible with ``T``, independent
of the number, types or kinds of arguments. Mypy lets you call such
callable values with arbitrary arguments, without any checking -- in
this respect they are treated similar to a ``(*args: Any, **kwargs:
Any)`` function signature. Example:

.. code-block:: python

   from collections.abc import Callable

   def arbitrary_call(f: Callable[..., int]) -> int:
       return f('x') + f(y=2)  # OK

   arbitrary_call(ord)   # No static error, but fails at runtime
   arbitrary_call(open)  # Error: does not return an int
   arbitrary_call(1)     # Error: 'int' is not callable

In situations where more precise or complex types of callbacks are
necessary one can use flexible :ref:`callback protocols <callback_protocols>`.
Lambdas are also supported. The lambda argument and return value types
cannot be given explicitly; they are always inferred based on context
using bidirectional type inference:

.. code-block:: python

   l = map(lambda x: x + 1, [1, 2, 3])   # Infer x as int and l as list[int]

If you want to give the argument or return value types explicitly, use
an ordinary, perhaps nested function definition.

Callables can also be used against type objects, matching their
``__init__`` or ``__new__`` signature:

.. code-block:: python

    from collections.abc import Callable

    class C:
        def __init__(self, app: str) -> None:
            pass

    CallableType = Callable[[str], C]

    def class_or_callable(arg: CallableType) -> None:
        inst = arg("my_app")
        reveal_type(inst)  # Revealed type is "C"

This is useful if you want ``arg`` to be either a ``Callable`` returning an
instance of ``C`` or the type of ``C`` itself. This also works with
:ref:`callback protocols <callback_protocols>`.


.. _union-types:
.. _alternative_union_syntax:

Union types
***********

Python functions often accept values of two or more different
types. You can use :ref:`overloading <function-overloading>` to
represent this, but union types are often more convenient.

Use ``T1 | ... | Tn`` to construct a union
type. For example, if an argument has type ``int | str``, both
integers and strings are valid argument values.

You can use an :py:func:`isinstance` check to narrow down a union type to a
more specific type:

.. code-block:: python

   def f(x: int | str) -> None:
       x + 1     # Error: str + int is not valid
       if isinstance(x, int):
           # Here type of x is int.
           x + 1      # OK
       else:
           # Here type of x is str.
           x + 'a'    # OK

   f(1)    # OK
   f('x')  # OK
   f(1.1)  # Error

.. note::

    Operations are valid for union types only if they are valid for *every*
    union item. This is why it's often necessary to use an :py:func:`isinstance`
    check to first narrow down a union type to a non-union type. This also
    means that it's recommended to avoid union types as function return types,
    since the caller may have to use :py:func:`isinstance` before doing anything
    interesting with the value.

Python 3.9 and older only partially support this syntax. Instead, you can
use the legacy ``Union[T1, ..., Tn]`` type constructor. Example:

.. code-block:: python

   from typing import Union

   def f(x: Union[int, str]) -> None:
       ...

It is also possible to use the new syntax with versions of Python where it
isn't supported by the runtime with some limitations, if you use
``from __future__ import annotations`` (see :ref:`runtime_troubles`):

.. code-block:: python

   from __future__ import annotations

   def f(x: int | str) -> None:   # OK on Python 3.7 and later
       ...

.. _strict_optional:

Optional types and the None type
********************************

You can use ``T | None`` to define a type variant that allows ``None`` values,
such as ``int | None``. This is called an *optional type*:

.. code-block:: python

   def strlen(s: str) -> int | None:
       if not s:
           return None  # OK
       return len(s)

   def strlen_invalid(s: str) -> int:
       if not s:
           return None  # Error: None not compatible with int
       return len(s)

To support Python 3.9 and earlier, you can use the :py:data:`~typing.Optional`
type modifier instead, such as ``Optional[int]`` (``Optional[X]`` is
the preferred shorthand for ``Union[X, None]``):

.. code-block:: python

   from typing import Optional

   def strlen(s: str) -> Optional[int]:
       ...

Most operations will not be allowed on unguarded ``None`` or *optional* values
(values with an optional type):

.. code-block:: python

   def my_inc(x: int | None) -> int:
       return x + 1  # Error: Cannot add None and int

Instead, an explicit ``None`` check is required. Mypy has
powerful type inference that lets you use regular Python
idioms to guard against ``None`` values. For example, mypy
recognizes ``is None`` checks:

.. code-block:: python

   def my_inc(x: int | None) -> int:
       if x is None:
           return 0
       else:
           # The inferred type of x is just int here.
           return x + 1

Mypy will infer the type of ``x`` to be ``int`` in the else block due to the
check against ``None`` in the if condition.

Other supported checks for guarding against a ``None`` value include
``if x is not None``, ``if x`` and ``if not x``. Additionally, mypy understands
``None`` checks within logical expressions:

.. code-block:: python

   def concat(x: str | None, y: str | None) -> str | None:
       if x is not None and y is not None:
           # Both x and y are not None here
           return x + y
       else:
           return None

Sometimes mypy doesn't realize that a value is never ``None``. This notably
happens when a class instance can exist in a partially defined state,
where some attribute is initialized to ``None`` during object
construction, but a method assumes that the attribute is no longer ``None``. Mypy
will complain about the possible ``None`` value. You can use
``assert x is not None`` to work around this in the method:

.. code-block:: python

   class Resource:
       path: str | None = None

       def initialize(self, path: str) -> None:
           self.path = path

       def read(self) -> str:
           # We require that the object has been initialized.
           assert self.path is not None
           with open(self.path) as f:  # OK
              return f.read()

   r = Resource()
   r.initialize('/foo/bar')
   r.read()

When initializing a variable as ``None``, ``None`` is usually an
empty place-holder value, and the actual value has a different type.
This is why you need to annotate an attribute in cases like the class
``Resource`` above:

.. code-block:: python

    class Resource:
        path: str | None = None
        ...

This also works for attributes defined within methods:

.. code-block:: python

    class Counter:
        def __init__(self) -> None:
            self.count: int | None = None

Often it's easier to not use any initial value for an attribute.
This way you don't need to use an optional type and can avoid ``assert ... is not None``
checks. No initial value is needed if you annotate an attribute in the class body:

.. code-block:: python

   class Container:
       items: list[str]  # No initial value

Mypy generally uses the first assignment to a variable to
infer the type of the variable. However, if you assign both a ``None``
value and a non-``None`` value in the same scope, mypy can usually do
the right thing without an annotation:

.. code-block:: python

   def f(i: int) -> None:
       n = None  # Inferred type 'int | None' because of the assignment below
       if i > 0:
            n = i
       ...

Sometimes you may get the error "Cannot determine type of <something>". In this
case you should add an explicit ``... | None`` annotation.

.. note::

   ``None`` is a type with only one value, ``None``. ``None`` is also used
   as the return type for functions that don't return a value, i.e. functions
   that implicitly return ``None``.

.. note::

   The Python interpreter internally uses the name ``NoneType`` for
   the type of ``None``, but ``None`` is always used in type
   annotations. The latter is shorter and reads better. (``NoneType``
   is available as :py:data:`types.NoneType` on Python 3.10+, but is
   not exposed at all on earlier versions of Python.)

.. note::

    The type ``Optional[T]`` *does not* mean a function parameter with a default value.
    It simply means that ``None`` is a valid argument value. This is
    a common confusion because ``None`` is a common default value for parameters,
    and parameters with default values are sometimes called *optional* parameters
    (or arguments).

.. _type-aliases:

Type aliases
************

In certain situations, type names may end up being long and painful to type,
especially if they are used frequently:

.. code-block:: python

   def f() -> list[dict[tuple[int, str], set[int]]] | tuple[str, list[str]]:
       ...

When cases like this arise, you can define a type alias by simply
assigning the type to a variable (this is an *implicit type alias*):

.. code-block:: python

   AliasType = list[dict[tuple[int, str], set[int]]] | tuple[str, list[str]]

   # Now we can use AliasType in place of the full name:

   def f() -> AliasType:
       ...

.. note::

    A type alias does not create a new type. It's just a shorthand notation for
    another type -- it's equivalent to the target type except for
    :ref:`generic aliases <generic-type-aliases>`.

Python 3.12 introduced the ``type`` statement for defining *explicit type aliases*.
Explicit type aliases are unambiguous and can also improve readability by
making the intent clear:

.. code-block:: python

   type AliasType = list[dict[tuple[int, str], set[int]]] | tuple[str, list[str]]

   # Now we can use AliasType in place of the full name:

   def f() -> AliasType:
       ...

There can be confusion about exactly when an assignment defines an implicit type alias --
for example, when the alias contains forward references, invalid types, or violates some other
restrictions on type alias declarations.  Because the
distinction between an unannotated variable and a type alias is implicit,
ambiguous or incorrect type alias declarations default to defining
a normal variable instead of a type alias.

Aliases defined using the ``type`` statement have these properties, which
distinguish them from implicit type aliases:

* The definition may contain forward references without having to use string
  literal escaping, since it is evaluated lazily.
* The alias can be used in type annotations, type arguments, and casts, but
  it can't be used in contexts which require a class object. For example, it's
  not valid as a base class and it can't be used to construct instances.

There is also use an older syntax for defining explicit type aliases, which was
introduced in Python 3.10 (:pep:`613`):

.. code-block:: python

   from typing import TypeAlias  # "from typing_extensions" in Python 3.9 and earlier

   AliasType: TypeAlias = list[dict[tuple[int, str], set[int]]] | tuple[str, list[str]]

.. _named-tuples:

Named tuples
************

Mypy recognizes named tuples and can type check code that defines or
uses them.  In this example, we can detect code trying to access a
missing attribute:

.. code-block:: python

    Point = namedtuple('Point', ['x', 'y'])
    p = Point(x=1, y=2)
    print(p.z)  # Error: Point has no attribute 'z'

If you use :py:func:`namedtuple <collections.namedtuple>` to define your named tuple, all the items
are assumed to have ``Any`` types. That is, mypy doesn't know anything
about item types. You can use :py:class:`~typing.NamedTuple` to also define
item types:

.. code-block:: python

    from typing import NamedTuple

    Point = NamedTuple('Point', [('x', int),
                                 ('y', int)])
    p = Point(x=1, y='x')  # Argument has incompatible type "str"; expected "int"

Python 3.6 introduced an alternative, class-based syntax for named tuples with types:

.. code-block:: python

    from typing import NamedTuple

    class Point(NamedTuple):
        x: int
        y: int

    p = Point(x=1, y='x')  # Argument has incompatible type "str"; expected "int"

.. note::

  You can use the raw ``NamedTuple`` "pseudo-class" in type annotations
  if any ``NamedTuple`` object is valid.

  For example, it can be useful for deserialization:

  .. code-block:: python

    def deserialize_named_tuple(arg: NamedTuple) -> Dict[str, Any]:
        return arg._asdict()

    Point = namedtuple('Point', ['x', 'y'])
    Person = NamedTuple('Person', [('name', str), ('age', int)])

    deserialize_named_tuple(Point(x=1, y=2))  # ok
    deserialize_named_tuple(Person(name='Nikita', age=18))  # ok

    # Error: Argument 1 to "deserialize_named_tuple" has incompatible type
    # "Tuple[int, int]"; expected "NamedTuple"
    deserialize_named_tuple((1, 2))

  Note that this behavior is highly experimental, non-standard,
  and may not be supported by other type checkers and IDEs.

.. _type-of-class:

The type of class objects
*************************

(Freely after :pep:`PEP 484: The type of class objects
<484#the-type-of-class-objects>`.)

Sometimes you want to talk about class objects that inherit from a
given class.  This can be spelled as ``type[C]`` (or, on Python 3.8 and lower,
:py:class:`typing.Type[C] <typing.Type>`) where ``C`` is a
class.  In other words, when ``C`` is the name of a class, using ``C``
to annotate an argument declares that the argument is an instance of
``C`` (or of a subclass of ``C``), but using ``type[C]`` as an
argument annotation declares that the argument is a class object
deriving from ``C`` (or ``C`` itself).

For example, assume the following classes:

.. code-block:: python

   class User:
       # Defines fields like name, email

   class BasicUser(User):
       def upgrade(self):
           """Upgrade to Pro"""

   class ProUser(User):
       def pay(self):
           """Pay bill"""

Note that ``ProUser`` doesn't inherit from ``BasicUser``.

Here's a function that creates an instance of one of these classes if
you pass it the right class object:

.. code-block:: python

   def new_user(user_class):
       user = user_class()
       # (Here we could write the user object to a database)
       return user

How would we annotate this function?  Without the ability to parameterize ``type``, the best we
could do would be:

.. code-block:: python

   def new_user(user_class: type) -> User:
       # Same  implementation as before

This seems reasonable, except that in the following example, mypy
doesn't see that the ``buyer`` variable has type ``ProUser``:

.. code-block:: python

   buyer = new_user(ProUser)
   buyer.pay()  # Rejected, not a method on User

However, using the ``type[C]`` syntax and a type variable with an upper bound (see
:ref:`type-variable-upper-bound`) we can do better (Python 3.12 syntax):

.. code-block:: python

   def new_user[U: User](user_class: type[U]) -> U:
       # Same implementation as before

Here is the example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

   U = TypeVar('U', bound=User)

   def new_user(user_class: type[U]) -> U:
       # Same implementation as before

Now mypy will infer the correct type of the result when we call
``new_user()`` with a specific subclass of ``User``:

.. code-block:: python

   beginner = new_user(BasicUser)  # Inferred type is BasicUser
   beginner.upgrade()  # OK

.. note::

   The value corresponding to ``type[C]`` must be an actual class
   object that's a subtype of ``C``.  Its constructor must be
   compatible with the constructor of ``C``.  If ``C`` is a type
   variable, its upper bound must be a class object.

For more details about ``type[]`` and :py:class:`typing.Type[] <typing.Type>`, see :pep:`PEP 484: The type of
class objects <484#the-type-of-class-objects>`.

.. _generators:

Generators
**********

A basic generator that only yields values can be succinctly annotated as having a return
type of either :py:class:`Iterator[YieldType] <typing.Iterator>` or :py:class:`Iterable[YieldType] <typing.Iterable>`. For example:

.. code-block:: python

   def squares(n: int) -> Iterator[int]:
       for i in range(n):
           yield i * i

A good rule of thumb is to annotate functions with the most specific return
type possible. However, you should also take care to avoid leaking implementation
details into a function's public API. In keeping with these two principles, prefer
:py:class:`Iterator[YieldType] <typing.Iterator>` over
:py:class:`Iterable[YieldType] <typing.Iterable>` as the return-type annotation for a
generator function, as it lets mypy know that users are able to call :py:func:`next` on
the object returned by the function. Nonetheless, bear in mind that ``Iterable`` may
sometimes be the better option, if you consider it an implementation detail that
``next()`` can be called on the object returned by your function.

If you want your generator to accept values via the :py:meth:`~generator.send` method or return
a value, on the other hand, you should use the
:py:class:`Generator[YieldType, SendType, ReturnType] <typing.Generator>` generic type instead of
either ``Iterator`` or ``Iterable``. For example:

.. code-block:: python

   def echo_round() -> Generator[int, float, str]:
       sent = yield 0
       while sent >= 0:
           sent = yield round(sent)
       return 'Done'

Note that unlike many other generics in the typing module, the ``SendType`` of
:py:class:`~typing.Generator` behaves contravariantly, not covariantly or invariantly.

If you do not plan on receiving or returning values, then set the ``SendType``
or ``ReturnType`` to ``None``, as appropriate. For example, we could have
annotated the first example as the following:

.. code-block:: python

   def squares(n: int) -> Generator[int, None, None]:
       for i in range(n):
           yield i * i

This is slightly different from using ``Iterator[int]`` or ``Iterable[int]``,
since generators have :py:meth:`~generator.close`, :py:meth:`~generator.send`, and :py:meth:`~generator.throw` methods that
generic iterators and iterables don't. If you plan to call these methods on the returned
generator, use the :py:class:`~typing.Generator` type instead of :py:class:`~typing.Iterator` or :py:class:`~typing.Iterable`.
````

## File: docs/source/literal_types.rst
````
Literal types and Enums
=======================

.. _literal_types:

Literal types
-------------

Literal types let you indicate that an expression is equal to some specific
primitive value. For example, if we annotate a variable with type ``Literal["foo"]``,
mypy will understand that variable is not only of type ``str``, but is also
equal to specifically the string ``"foo"``.

This feature is primarily useful when annotating functions that behave
differently based on the exact value the caller provides. For example,
suppose we have a function ``fetch_data(...)`` that returns ``bytes`` if the
first argument is ``True``, and ``str`` if it's ``False``. We can construct a
precise type signature for this function using ``Literal[...]`` and overloads:

.. code-block:: python

    from typing import overload, Union, Literal

    # The first two overloads use Literal[...] so we can
    # have precise return types:

    @overload
    def fetch_data(raw: Literal[True]) -> bytes: ...
    @overload
    def fetch_data(raw: Literal[False]) -> str: ...

    # The last overload is a fallback in case the caller
    # provides a regular bool:

    @overload
    def fetch_data(raw: bool) -> Union[bytes, str]: ...

    def fetch_data(raw: bool) -> Union[bytes, str]:
        # Implementation is omitted
        ...

    reveal_type(fetch_data(True))        # Revealed type is "bytes"
    reveal_type(fetch_data(False))       # Revealed type is "str"

    # Variables declared without annotations will continue to have an
    # inferred type of 'bool'.

    variable = True
    reveal_type(fetch_data(variable))    # Revealed type is "Union[bytes, str]"

.. note::

    The examples in this page import ``Literal`` as well as ``Final`` and
    ``TypedDict`` from the ``typing`` module. These types were added to
    ``typing`` in Python 3.8, but are also available for use in Python
    3.4 - 3.7 via the ``typing_extensions`` package.

Parameterizing Literals
***********************

Literal types may contain one or more literal bools, ints, strs, bytes, and
enum values. However, literal types **cannot** contain arbitrary expressions:
types like ``Literal[my_string.trim()]``, ``Literal[x > 3]``, or ``Literal[3j + 4]``
are all illegal.

Literals containing two or more values are equivalent to the union of those values.
So, ``Literal[-3, b"foo", MyEnum.A]`` is equivalent to
``Union[Literal[-3], Literal[b"foo"], Literal[MyEnum.A]]``. This makes writing more
complex types involving literals a little more convenient.

Literal types may also contain ``None``. Mypy will treat ``Literal[None]`` as being
equivalent to just ``None``. This means that ``Literal[4, None]``,
``Literal[4] | None``, and ``Optional[Literal[4]]`` are all equivalent.

Literals may also contain aliases to other literal types. For example, the
following program is legal:

.. code-block:: python

    PrimaryColors = Literal["red", "blue", "yellow"]
    SecondaryColors = Literal["purple", "green", "orange"]
    AllowedColors = Literal[PrimaryColors, SecondaryColors]

    def paint(color: AllowedColors) -> None: ...

    paint("red")        # Type checks!
    paint("turquoise")  # Does not type check

Literals may not contain any other kind of type or expression. This means doing
``Literal[my_instance]``, ``Literal[Any]``, ``Literal[3.14]``, or
``Literal[{"foo": 2, "bar": 5}]`` are all illegal.

Declaring literal variables
***************************

You must explicitly add an annotation to a variable to declare that it has
a literal type:

.. code-block:: python

    a: Literal[19] = 19
    reveal_type(a)          # Revealed type is "Literal[19]"

In order to preserve backwards-compatibility, variables without this annotation
are **not** assumed to be literals:

.. code-block:: python

    b = 19
    reveal_type(b)          # Revealed type is "int"

If you find repeating the value of the variable in the type hint to be tedious,
you can instead change the variable to be ``Final`` (see :ref:`final_attrs`):

.. code-block:: python

    from typing import Final, Literal

    def expects_literal(x: Literal[19]) -> None: pass

    c: Final = 19

    reveal_type(c)          # Revealed type is "Literal[19]?"
    expects_literal(c)      # ...and this type checks!

If you do not provide an explicit type in the ``Final``, the type of ``c`` becomes
*context-sensitive*: mypy will basically try "substituting" the original assigned
value whenever it's used before performing type checking. This is why the revealed
type of ``c`` is ``Literal[19]?``: the question mark at the end reflects this
context-sensitive nature.

For example, mypy will type check the above program almost as if it were written like so:

.. code-block:: python

    from typing import Final, Literal

    def expects_literal(x: Literal[19]) -> None: pass

    reveal_type(19)
    expects_literal(19)

This means that while changing a variable to be ``Final`` is not quite the same thing
as adding an explicit ``Literal[...]`` annotation, it often leads to the same effect
in practice.

The main cases where the behavior of context-sensitive vs true literal types differ are
when you try using those types in places that are not explicitly expecting a ``Literal[...]``.
For example, compare and contrast what happens when you try appending these types to a list:

.. code-block:: python

    from typing import Final, Literal

    a: Final = 19
    b: Literal[19] = 19

    # Mypy will choose to infer list[int] here.
    list_of_ints = []
    list_of_ints.append(a)
    reveal_type(list_of_ints)  # Revealed type is "list[int]"

    # But if the variable you're appending is an explicit Literal, mypy
    # will infer list[Literal[19]].
    list_of_lits = []
    list_of_lits.append(b)
    reveal_type(list_of_lits)  # Revealed type is "list[Literal[19]]"


Intelligent indexing
********************

We can use Literal types to more precisely index into structured heterogeneous
types such as tuples, NamedTuples, and TypedDicts. This feature is known as
*intelligent indexing*.

For example, when we index into a tuple using some int, the inferred type is
normally the union of the tuple item types. However, if we want just the type
corresponding to some particular index, we can use Literal types like so:

.. code-block:: python

    from typing import TypedDict

    tup = ("foo", 3.4)

    # Indexing with an int literal gives us the exact type for that index
    reveal_type(tup[0])  # Revealed type is "str"

    # But what if we want the index to be a variable? Normally mypy won't
    # know exactly what the index is and so will return a less precise type:
    int_index = 0
    reveal_type(tup[int_index])  # Revealed type is "Union[str, float]"

    # But if we use either Literal types or a Final int, we can gain back
    # the precision we originally had:
    lit_index: Literal[0] = 0
    fin_index: Final = 0
    reveal_type(tup[lit_index])  # Revealed type is "str"
    reveal_type(tup[fin_index])  # Revealed type is "str"

    # We can do the same thing with with TypedDict and str keys:
    class MyDict(TypedDict):
        name: str
        main_id: int
        backup_id: int

    d: MyDict = {"name": "Saanvi", "main_id": 111, "backup_id": 222}
    name_key: Final = "name"
    reveal_type(d[name_key])  # Revealed type is "str"

    # You can also index using unions of literals
    id_key: Literal["main_id", "backup_id"]
    reveal_type(d[id_key])    # Revealed type is "int"

.. _tagged_unions:

Tagged unions
*************

When you have a union of types, you can normally discriminate between each type
in the union by using ``isinstance`` checks. For example, if you had a variable ``x`` of
type ``Union[int, str]``, you could write some code that runs only if ``x`` is an int
by doing ``if isinstance(x, int): ...``.

However, it is not always possible or convenient to do this. For example, it is not
possible to use ``isinstance`` to distinguish between two different TypedDicts since
at runtime, your variable will simply be just a dict.

Instead, what you can do is *label* or *tag* your TypedDicts with a distinct Literal
type. Then, you can discriminate between each kind of TypedDict by checking the label:

.. code-block:: python

    from typing import Literal, TypedDict, Union

    class NewJobEvent(TypedDict):
        tag: Literal["new-job"]
        job_name: str
        config_file_path: str

    class CancelJobEvent(TypedDict):
        tag: Literal["cancel-job"]
        job_id: int

    Event = Union[NewJobEvent, CancelJobEvent]

    def process_event(event: Event) -> None:
        # Since we made sure both TypedDicts have a key named 'tag', it's
        # safe to do 'event["tag"]'. This expression normally has the type
        # Literal["new-job", "cancel-job"], but the check below will narrow
        # the type to either Literal["new-job"] or Literal["cancel-job"].
        #
        # This in turns narrows the type of 'event' to either NewJobEvent
        # or CancelJobEvent.
        if event["tag"] == "new-job":
            print(event["job_name"])
        else:
            print(event["job_id"])

While this feature is mostly useful when working with TypedDicts, you can also
use the same technique with regular objects, tuples, or namedtuples.

Similarly, tags do not need to be specifically str Literals: they can be any type
you can normally narrow within ``if`` statements and the like. For example, you
could have your tags be int or Enum Literals or even regular classes you narrow
using ``isinstance()`` (Python 3.12 syntax):

.. code-block:: python

    class Wrapper[T]:
        def __init__(self, inner: T) -> None:
            self.inner = inner

    def process(w: Wrapper[int] | Wrapper[str]) -> None:
        # Doing `if isinstance(w, Wrapper[int])` does not work: isinstance requires
        # that the second argument always be an *erased* type, with no generics.
        # This is because generics are a typing-only concept and do not exist at
        # runtime in a way `isinstance` can always check.
        #
        # However, we can side-step this by checking the type of `w.inner` to
        # narrow `w` itself:
        if isinstance(w.inner, int):
            reveal_type(w)  # Revealed type is "Wrapper[int]"
        else:
            reveal_type(w)  # Revealed type is "Wrapper[str]"

This feature is sometimes called "sum types" or "discriminated union types"
in other programming languages.

Exhaustiveness checking
***********************

You may want to check that some code covers all possible
``Literal`` or ``Enum`` cases. Example:

.. code-block:: python

  from typing import Literal

  PossibleValues = Literal['one', 'two']

  def validate(x: PossibleValues) -> bool:
      if x == 'one':
          return True
      elif x == 'two':
          return False
      raise ValueError(f'Invalid value: {x}')

  assert validate('one') is True
  assert validate('two') is False

In the code above, it's easy to make a mistake. You can
add a new literal value to ``PossibleValues`` but forget
to handle it in the ``validate`` function:

.. code-block:: python

  PossibleValues = Literal['one', 'two', 'three']

Mypy won't catch that ``'three'`` is not covered.  If you want mypy to
perform an exhaustiveness check, you need to update your code to use an
``assert_never()`` check:

.. code-block:: python

  from typing import Literal, NoReturn
  from typing_extensions import assert_never

  PossibleValues = Literal['one', 'two']

  def validate(x: PossibleValues) -> bool:
      if x == 'one':
          return True
      elif x == 'two':
          return False
      assert_never(x)

Now if you add a new value to ``PossibleValues`` but don't update ``validate``,
mypy will spot the error:

.. code-block:: python

  PossibleValues = Literal['one', 'two', 'three']

  def validate(x: PossibleValues) -> bool:
      if x == 'one':
          return True
      elif x == 'two':
          return False
      # Error: Argument 1 to "assert_never" has incompatible type "Literal['three']";
      # expected "NoReturn"
      assert_never(x)

If runtime checking against unexpected values is not needed, you can
leave out the ``assert_never`` call in the above example, and mypy
will still generate an error about function ``validate`` returning
without a value:

.. code-block:: python

  PossibleValues = Literal['one', 'two', 'three']

  # Error: Missing return statement
  def validate(x: PossibleValues) -> bool:
      if x == 'one':
          return True
      elif x == 'two':
          return False

Exhaustiveness checking is also supported for match statements (Python 3.10 and later):

.. code-block:: python

  def validate(x: PossibleValues) -> bool:
      match x:
          case 'one':
              return True
          case 'two':
              return False
      assert_never(x)


Limitations
***********

Mypy will not understand expressions that use variables of type ``Literal[..]``
on a deep level. For example, if you have a variable ``a`` of type ``Literal[3]``
and another variable ``b`` of type ``Literal[5]``, mypy will infer that
``a + b`` has type ``int``, **not** type ``Literal[8]``.

The basic rule is that literal types are treated as just regular subtypes of
whatever type the parameter has. For example, ``Literal[3]`` is treated as a
subtype of ``int`` and so will inherit all of ``int``'s methods directly. This
means that ``Literal[3].__add__`` accepts the same arguments and has the same
return type as ``int.__add__``.


Enums
-----

Mypy has special support for :py:class:`enum.Enum` and its subclasses:
:py:class:`enum.IntEnum`, :py:class:`enum.Flag`, :py:class:`enum.IntFlag`,
and :py:class:`enum.StrEnum`.

.. code-block:: python

  from enum import Enum

  class Direction(Enum):
      up = 'up'
      down = 'down'

  reveal_type(Direction.up)  # Revealed type is "Literal[Direction.up]?"
  reveal_type(Direction.down)  # Revealed type is "Literal[Direction.down]?"

You can use enums to annotate types as you would expect:

.. code-block:: python

  class Movement:
      def __init__(self, direction: Direction, speed: float) -> None:
          self.direction = direction
          self.speed = speed

  Movement(Direction.up, 5.0)  # ok
  Movement('up', 5.0)  # E: Argument 1 to "Movement" has incompatible type "str"; expected "Direction"

Exhaustiveness checking
***********************

Similar to ``Literal`` types, ``Enum`` supports exhaustiveness checking.
Let's start with a definition:

.. code-block:: python

  from enum import Enum
  from typing import NoReturn
  from typing_extensions import assert_never

  class Direction(Enum):
      up = 'up'
      down = 'down'

Now, let's use an exhaustiveness check:

.. code-block:: python

  def choose_direction(direction: Direction) -> None:
      if direction is Direction.up:
          reveal_type(direction)  # N: Revealed type is "Literal[Direction.up]"
          print('Going up!')
          return
      elif direction is Direction.down:
          print('Down')
          return
      # This line is never reached
      assert_never(direction)

If we forget to handle one of the cases, mypy will generate an error:

.. code-block:: python

  def choose_direction(direction: Direction) -> None:
      if direction == Direction.up:
          print('Going up!')
          return
      assert_never(direction)  # E: Argument 1 to "assert_never" has incompatible type "Direction"; expected "NoReturn"

Exhaustiveness checking is also supported for match statements (Python 3.10 and later).
For match statements specifically, inexhaustive matches can be caught
without needing to use ``assert_never`` by using
:option:`--enable-error-code exhaustive-match <mypy --enable-error-code>`.


Extra Enum checks
*****************

Mypy also tries to support special features of ``Enum``
the same way Python's runtime does:

- Any ``Enum`` class with values is implicitly :ref:`final <final_attrs>`.
  This is what happens in CPython:

  .. code-block:: python

    >>> class AllDirection(Direction):
    ...     left = 'left'
    ...     right = 'right'
    Traceback (most recent call last):
      ...
    TypeError: AllDirection: cannot extend enumeration 'Direction'

  Mypy also catches this error:

  .. code-block:: python

    class AllDirection(Direction):  # E: Cannot inherit from final class "Direction"
        left = 'left'
        right = 'right'

- All ``Enum`` fields are implicitly ``final`` as well.

  .. code-block:: python

    Direction.up = '^'  # E: Cannot assign to final attribute "up"

- All field names are checked to be unique.

  .. code-block:: python

     class Some(Enum):
        x = 1
        x = 2  # E: Attempted to reuse member name "x" in Enum definition "Some"

- Base classes have no conflicts and mixin types are correct.

  .. code-block:: python

    class WrongEnum(str, int, enum.Enum):
        # E: Only a single data type mixin is allowed for Enum subtypes, found extra "int"
        ...

    class MixinAfterEnum(enum.Enum, Mixin): # E: No base classes are allowed after "enum.Enum"
        ...
````

## File: docs/source/metaclasses.rst
````
.. _metaclasses:

Metaclasses
===========

A :ref:`metaclass <python:metaclasses>` is a class that describes
the construction and behavior of other classes, similarly to how classes
describe the construction and behavior of objects.
The default metaclass is :py:class:`type`, but it's possible to use other metaclasses.
Metaclasses allows one to create "a different kind of class", such as
:py:class:`~enum.Enum`\s, :py:class:`~typing.NamedTuple`\s and singletons.

Mypy has some special understanding of :py:class:`~abc.ABCMeta` and ``EnumMeta``.

.. _defining:

Defining a metaclass
********************

.. code-block:: python

    class M(type):
        pass

    class A(metaclass=M):
        pass

.. _examples:

Metaclass usage example
***********************

Mypy supports the lookup of attributes in the metaclass:

.. code-block:: python

    from typing import ClassVar, TypeVar

    S = TypeVar("S")

    class M(type):
        count: ClassVar[int] = 0

        def make(cls: type[S]) -> S:
            M.count += 1
            return cls()

    class A(metaclass=M):
        pass

    a: A = A.make()  # make() is looked up at M; the result is an object of type A
    print(A.count)

    class B(A):
        pass

    b: B = B.make()  # metaclasses are inherited
    print(B.count + " objects were created")  # Error: Unsupported operand types for + ("int" and "str")

.. _limitations:

Gotchas and limitations of metaclass support
********************************************

Note that metaclasses pose some requirements on the inheritance structure,
so it's better not to combine metaclasses and class hierarchies:

.. code-block:: python

    class M1(type): pass
    class M2(type): pass

    class A1(metaclass=M1): pass
    class A2(metaclass=M2): pass

    class B1(A1, metaclass=M2): pass  # Mypy Error: metaclass conflict
    # At runtime the above definition raises an exception
    # TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases

    class B12(A1, A2): pass  # Mypy Error: metaclass conflict

    # This can be solved via a common metaclass subtype:
    class CorrectMeta(M1, M2): pass
    class B2(A1, A2, metaclass=CorrectMeta): pass  # OK, runtime is also OK

* Mypy does not understand dynamically-computed metaclasses,
  such as ``class A(metaclass=f()): ...``
* Mypy does not and cannot understand arbitrary metaclass code.
* Mypy only recognizes subclasses of :py:class:`type` as potential metaclasses.
* ``Self`` is not allowed as annotation in metaclasses as per `PEP 673`_.

.. _PEP 673: https://peps.python.org/pep-0673/#valid-locations-for-self

For some builtin types, mypy may think their metaclass is :py:class:`abc.ABCMeta`
even if it is :py:class:`type` at runtime. In those cases, you can either:

* use :py:class:`abc.ABCMeta` instead of :py:class:`type` as the
  superclass of your metaclass if that works in your use-case
* mute the error with ``# type: ignore[metaclass]``

.. code-block:: python

    import abc

    assert type(tuple) is type  # metaclass of tuple is type at runtime

    # The problem:
    class M0(type): pass
    class A0(tuple, metaclass=M0): pass  # Mypy Error: metaclass conflict

    # Option 1: use ABCMeta instead of type
    class M1(abc.ABCMeta): pass
    class A1(tuple, metaclass=M1): pass

    # Option 2: mute the error
    class M2(type): pass
    class A2(tuple, metaclass=M2): pass  # type: ignore[metaclass]
````

## File: docs/source/more_types.rst
````
More types
==========

This section introduces a few additional kinds of types, including :py:data:`~typing.NoReturn`,
:py:class:`~typing.NewType`, and types for async code. It also discusses
how to give functions more precise types using overloads. All of these are only
situationally useful, so feel free to skip this section and come back when you
have a need for some of them.

Here's a quick summary of what's covered here:

* :py:data:`~typing.NoReturn` lets you tell mypy that a function never returns normally.

* :py:class:`~typing.NewType` lets you define a variant of a type that is treated as a
  separate type by mypy but is identical to the original type at runtime.
  For example, you can have ``UserId`` as a variant of ``int`` that is
  just an ``int`` at runtime.

* :py:func:`@overload <typing.overload>` lets you define a function that can accept multiple distinct
  signatures. This is useful if you need to encode a relationship between the
  arguments and the return type that would be difficult to express normally.

* Async types let you type check programs using ``async`` and ``await``.

.. _noreturn:

The NoReturn type
*****************

Mypy provides support for functions that never return. For
example, a function that unconditionally raises an exception:

.. code-block:: python

   from typing import NoReturn

   def stop() -> NoReturn:
       raise Exception('no way')

Mypy will ensure that functions annotated as returning :py:data:`~typing.NoReturn`
truly never return, either implicitly or explicitly. Mypy will also
recognize that the code after calls to such functions is unreachable
and will behave accordingly:

.. code-block:: python

   def f(x: int) -> int:
       if x == 0:
           return x
       stop()
       return 'whatever works'  # No error in an unreachable block

In earlier Python versions you need to install ``typing_extensions`` using
pip to use :py:data:`~typing.NoReturn` in your code. Python 3 command line:

.. code-block:: text

    python3 -m pip install --upgrade typing-extensions

.. _newtypes:

NewTypes
********

There are situations where you may want to avoid programming errors by
creating simple derived classes that are only used to distinguish
certain values from base class instances. Example:

.. code-block:: python

    class UserId(int):
        pass

    def get_by_user_id(user_id: UserId):
        ...

However, this approach introduces some runtime overhead. To avoid this, the typing
module provides a helper object :py:class:`~typing.NewType` that creates simple unique types with
almost zero runtime overhead. Mypy will treat the statement
``Derived = NewType('Derived', Base)`` as being roughly equivalent to the following
definition:

.. code-block:: python

    class Derived(Base):
        def __init__(self, _x: Base) -> None:
            ...

However, at runtime, ``NewType('Derived', Base)`` will return a dummy callable that
simply returns its argument:

.. code-block:: python

    def Derived(_x):
        return _x

Mypy will require explicit casts from ``int`` where ``UserId`` is expected, while
implicitly casting from ``UserId`` where ``int`` is expected. Examples:

.. code-block:: python

    from typing import NewType

    UserId = NewType('UserId', int)

    def name_by_id(user_id: UserId) -> str:
        ...

    UserId('user')          # Fails type check

    name_by_id(42)          # Fails type check
    name_by_id(UserId(42))  # OK

    num: int = UserId(5) + 1

:py:class:`~typing.NewType` accepts exactly two arguments. The first argument must be a string literal
containing the name of the new type and must equal the name of the variable to which the new
type is assigned. The second argument must be a properly subclassable class, i.e.,
not a type construct like a :ref:`union type <union-types>`, etc.

The callable returned by :py:class:`~typing.NewType` accepts only one argument; this is equivalent to
supporting only one constructor accepting an instance of the base class (see above).
Example:

.. code-block:: python

    from typing import NewType

    class PacketId:
        def __init__(self, major: int, minor: int) -> None:
            self._major = major
            self._minor = minor

    TcpPacketId = NewType('TcpPacketId', PacketId)

    packet = PacketId(100, 100)
    tcp_packet = TcpPacketId(packet)  # OK

    tcp_packet = TcpPacketId(127, 0)  # Fails in type checker and at runtime

You cannot use :py:func:`isinstance` or :py:func:`issubclass` on the object returned by
:py:class:`~typing.NewType`, nor can you subclass an object returned by :py:class:`~typing.NewType`.

.. note::

    Unlike type aliases, :py:class:`~typing.NewType` will create an entirely new and
    unique type when used. The intended purpose of :py:class:`~typing.NewType` is to help you
    detect cases where you accidentally mixed together the old base type and the
    new derived type.

    For example, the following will successfully typecheck when using type
    aliases:

    .. code-block:: python

        UserId = int

        def name_by_id(user_id: UserId) -> str:
            ...

        name_by_id(3)  # ints and UserId are synonymous

    But a similar example using :py:class:`~typing.NewType` will not typecheck:

    .. code-block:: python

        from typing import NewType

        UserId = NewType('UserId', int)

        def name_by_id(user_id: UserId) -> str:
            ...

        name_by_id(3)  # int is not the same as UserId

.. _function-overloading:

Function overloading
********************

Sometimes the arguments and types in a function depend on each other
in ways that can't be captured with a :ref:`union types <union-types>`. For example, suppose
we want to write a function that can accept x-y coordinates. If we pass
in just a single x-y coordinate, we return a ``ClickEvent`` object. However,
if we pass in two x-y coordinates, we return a ``DragEvent`` object.

Our first attempt at writing this function might look like this:

.. code-block:: python

    def mouse_event(x1: int,
                    y1: int,
                    x2: int | None = None,
                    y2: int | None = None) -> ClickEvent | DragEvent:
        if x2 is None and y2 is None:
            return ClickEvent(x1, y1)
        elif x2 is not None and y2 is not None:
            return DragEvent(x1, y1, x2, y2)
        else:
            raise TypeError("Bad arguments")

While this function signature works, it's too loose: it implies ``mouse_event``
could return either object regardless of the number of arguments
we pass in. It also does not prohibit a caller from passing in the wrong
number of ints: mypy would treat calls like ``mouse_event(1, 2, 20)`` as being
valid, for example.

We can do better by using :pep:`overloading <484#function-method-overloading>`
which lets us give the same function multiple type annotations (signatures)
to more accurately describe the function's behavior:

.. code-block:: python

    from typing import overload

    # Overload *variants* for 'mouse_event'.
    # These variants give extra information to the type checker.
    # They are ignored at runtime.

    @overload
    def mouse_event(x1: int, y1: int) -> ClickEvent: ...
    @overload
    def mouse_event(x1: int, y1: int, x2: int, y2: int) -> DragEvent: ...

    # The actual *implementation* of 'mouse_event'.
    # The implementation contains the actual runtime logic.
    #
    # It may or may not have type hints. If it does, mypy
    # will check the body of the implementation against the
    # type hints.
    #
    # Mypy will also check and make sure the signature is
    # consistent with the provided variants.

    def mouse_event(x1: int,
                    y1: int,
                    x2: int | None = None,
                    y2: int | None = None) -> ClickEvent | DragEvent:
        if x2 is None and y2 is None:
            return ClickEvent(x1, y1)
        elif x2 is not None and y2 is not None:
            return DragEvent(x1, y1, x2, y2)
        else:
            raise TypeError("Bad arguments")

This allows mypy to understand calls to ``mouse_event`` much more precisely.
For example, mypy will understand that ``mouse_event(5, 25)`` will
always have a return type of ``ClickEvent`` and will report errors for
calls like ``mouse_event(5, 25, 2)``.

As another example, suppose we want to write a custom container class that
implements the :py:meth:`__getitem__ <object.__getitem__>` method (``[]`` bracket indexing). If this
method receives an integer we return a single item. If it receives a
``slice``, we return a :py:class:`~collections.abc.Sequence` of items.

We can precisely encode this relationship between the argument and the
return type by using overloads like so (Python 3.12 syntax):

.. code-block:: python

    from collections.abc import Sequence
    from typing import overload

    class MyList[T](Sequence[T]):
        @overload
        def __getitem__(self, index: int) -> T: ...

        @overload
        def __getitem__(self, index: slice) -> Sequence[T]: ...

        def __getitem__(self, index: int | slice) -> T | Sequence[T]:
            if isinstance(index, int):
                # Return a T here
            elif isinstance(index, slice):
                # Return a sequence of Ts here
            else:
                raise TypeError(...)

Here is the same example using the legacy syntax (Python 3.11 and earlier):

.. code-block:: python

    from collections.abc import Sequence
    from typing import TypeVar, overload

    T = TypeVar('T')

    class MyList(Sequence[T]):
        @overload
        def __getitem__(self, index: int) -> T: ...

        @overload
        def __getitem__(self, index: slice) -> Sequence[T]: ...

        def __getitem__(self, index: int | slice) -> T | Sequence[T]:
            if isinstance(index, int):
                # Return a T here
            elif isinstance(index, slice):
                # Return a sequence of Ts here
            else:
                raise TypeError(...)

.. note::

   If you just need to constrain a type variable to certain types or
   subtypes, you can use a :ref:`value restriction
   <type-variable-value-restriction>`.

The default values of a function's arguments don't affect its signature -- only
the absence or presence of a default value does. So in order to reduce
redundancy, it's possible to replace default values in overload definitions with
``...`` as a placeholder:

.. code-block:: python

    from typing import overload

    class M: ...

    @overload
    def get_model(model_or_pk: M, flag: bool = ...) -> M: ...
    @overload
    def get_model(model_or_pk: int, flag: bool = ...) -> M | None: ...

    def get_model(model_or_pk: int | M, flag: bool = True) -> M | None:
        ...


Runtime behavior
----------------

An overloaded function must consist of two or more overload *variants*
followed by an *implementation*. The variants and the implementations
must be adjacent in the code: think of them as one indivisible unit.

The variant bodies must all be empty; only the implementation is allowed
to contain code. This is because at runtime, the variants are completely
ignored: they're overridden by the final implementation function.

This means that an overloaded function is still an ordinary Python
function! There is no automatic dispatch handling and you must manually
handle the different types in the implementation (e.g. by using
``if`` statements and :py:func:`isinstance <isinstance>` checks).

If you are adding an overload within a stub file, the implementation
function should be omitted: stubs do not contain runtime logic.

.. note::

   While we can leave the variant body empty using the ``pass`` keyword,
   the more common convention is to instead use the ellipsis (``...``) literal.

Type checking calls to overloads
--------------------------------

When you call an overloaded function, mypy will infer the correct return
type by picking the best matching variant, after taking into consideration
both the argument types and arity. However, a call is never type
checked against the implementation. This is why mypy will report calls
like ``mouse_event(5, 25, 3)`` as being invalid even though it matches the
implementation signature.

If there are multiple equally good matching variants, mypy will select
the variant that was defined first. For example, consider the following
program:

.. code-block:: python

    # For Python 3.8 and below you must use `typing.List` instead of `list`. e.g.
    # from typing import List
    from typing import overload

    @overload
    def summarize(data: list[int]) -> float: ...

    @overload
    def summarize(data: list[str]) -> str: ...

    def summarize(data):
        if not data:
            return 0.0
        elif isinstance(data[0], int):
            # Do int specific code
        else:
            # Do str-specific code

    # What is the type of 'output'? float or str?
    output = summarize([])

The ``summarize([])`` call matches both variants: an empty list could
be either a ``list[int]`` or a ``list[str]``. In this case, mypy
will break the tie by picking the first matching variant: ``output``
will have an inferred type of ``float``. The implementer is responsible
for making sure ``summarize`` breaks ties in the same way at runtime.

However, there are two exceptions to the "pick the first match" rule.
First, if multiple variants match due to an argument being of type
``Any``, mypy will make the inferred type also be ``Any``:

.. code-block:: python

    dynamic_var: Any = some_dynamic_function()

    # output2 is of type 'Any'
    output2 = summarize(dynamic_var)

Second, if multiple variants match due to one or more of the arguments
being a union, mypy will make the inferred type be the union of the
matching variant returns:

.. code-block:: python

    some_list: list[int] | list[str]

    # output3 is of type 'float | str'
    output3 = summarize(some_list)

.. note::

   Due to the "pick the first match" rule, changing the order of your
   overload variants can change how mypy type checks your program.

   To minimize potential issues, we recommend that you:

   1. Make sure your overload variants are listed in the same order as
      the runtime checks (e.g. :py:func:`isinstance <isinstance>` checks) in your implementation.
   2. Order your variants and runtime checks from most to least specific.
      (See the following section for an example).

Type checking the variants
--------------------------

Mypy will perform several checks on your overload variant definitions
to ensure they behave as expected. First, mypy will check and make sure
that no overload variant is shadowing a subsequent one. For example,
consider the following function which adds together two ``Expression``
objects, and contains a special-case to handle receiving two ``Literal``
types:

.. code-block:: python

    from typing import overload

    class Expression:
        # ...snip...

    class Literal(Expression):
        # ...snip...

    # Warning -- the first overload variant shadows the second!

    @overload
    def add(left: Expression, right: Expression) -> Expression: ...

    @overload
    def add(left: Literal, right: Literal) -> Literal: ...

    def add(left: Expression, right: Expression) -> Expression:
        # ...snip...

While this code snippet is technically type-safe, it does contain an
anti-pattern: the second variant will never be selected! If we try calling
``add(Literal(3), Literal(4))``, mypy will always pick the first variant
and evaluate the function call to be of type ``Expression``, not ``Literal``.
This is because ``Literal`` is a subtype of ``Expression``, which means
the "pick the first match" rule will always halt after considering the
first overload.

Because having an overload variant that can never be matched is almost
certainly a mistake, mypy will report an error. To fix the error, we can
either 1) delete the second overload or 2) swap the order of the overloads:

.. code-block:: python

    # Everything is ok now -- the variants are correctly ordered
    # from most to least specific.

    @overload
    def add(left: Literal, right: Literal) -> Literal: ...

    @overload
    def add(left: Expression, right: Expression) -> Expression: ...

    def add(left: Expression, right: Expression) -> Expression:
        # ...snip...

Mypy will also type check the different variants and flag any overloads
that have inherently unsafely overlapping variants. For example, consider
the following unsafe overload definition:

.. code-block:: python

    from typing import overload

    @overload
    def unsafe_func(x: int) -> int: ...

    @overload
    def unsafe_func(x: object) -> str: ...

    def unsafe_func(x: object) -> int | str:
        if isinstance(x, int):
            return 42
        else:
            return "some string"

On the surface, this function definition appears to be fine. However, it will
result in a discrepancy between the inferred type and the actual runtime type
when we try using it like so:

.. code-block:: python

    some_obj: object = 42
    unsafe_func(some_obj) + " danger danger"  # Type checks, yet crashes at runtime!

Since ``some_obj`` is of type :py:class:`object`, mypy will decide that ``unsafe_func``
must return something of type ``str`` and concludes the above will type check.
But in reality, ``unsafe_func`` will return an int, causing the code to crash
at runtime!

To prevent these kinds of issues, mypy will detect and prohibit inherently unsafely
overlapping overloads on a best-effort basis. Two variants are considered unsafely
overlapping when both of the following are true:

1. All of the arguments of the first variant are potentially compatible with the second.
2. The return type of the first variant is *not* compatible with (e.g. is not a
   subtype of) the second.

So in this example, the ``int`` argument in the first variant is a subtype of
the ``object`` argument in the second, yet the ``int`` return type is not a subtype of
``str``. Both conditions are true, so mypy will correctly flag ``unsafe_func`` as
being unsafe.

Note that in cases where you ignore the overlapping overload error, mypy will usually
still infer the types you expect at callsites.

However, mypy will not detect *all* unsafe uses of overloads. For example,
suppose we modify the above snippet so it calls ``summarize`` instead of
``unsafe_func``:

.. code-block:: python

    some_list: list[str] = []
    summarize(some_list) + "danger danger"  # Type safe, yet crashes at runtime!

We run into a similar issue here. This program type checks if we look just at the
annotations on the overloads. But since ``summarize(...)`` is designed to be biased
towards returning a float when it receives an empty list, this program will actually
crash during runtime.

The reason mypy does not flag definitions like ``summarize`` as being potentially
unsafe is because if it did, it would be extremely difficult to write a safe
overload. For example, suppose we define an overload with two variants that accept
types ``A`` and ``B`` respectively. Even if those two types were completely unrelated,
the user could still potentially trigger a runtime error similar to the ones above by
passing in a value of some third type ``C`` that inherits from both ``A`` and ``B``.

Thankfully, these types of situations are relatively rare. What this does mean,
however, is that you should exercise caution when designing or using an overloaded
function that can potentially receive values that are an instance of two seemingly
unrelated types.


Type checking the implementation
--------------------------------

The body of an implementation is type-checked against the
type hints provided on the implementation. For example, in the
``MyList`` example up above, the code in the body is checked with
argument list ``index: int | slice`` and a return type of
``T | Sequence[T]``. If there are no annotations on the
implementation, then the body is not type checked. If you want to
force mypy to check the body anyways, use the :option:`--check-untyped-defs <mypy --check-untyped-defs>`
flag (:ref:`more details here <untyped-definitions-and-calls>`).

The variants must also also be compatible with the implementation
type hints. In the ``MyList`` example, mypy will check that the
parameter type ``int`` and the return type ``T`` are compatible with
``int | slice`` and ``T | Sequence`` for the
first variant. For the second variant it verifies the parameter
type ``slice`` and the return type ``Sequence[T]`` are compatible
with ``int | slice`` and ``T | Sequence``.

.. note::

   The overload semantics documented above are new as of mypy 0.620.

   Previously, mypy used to perform type erasure on all overload variants. For
   example, the ``summarize`` example from the previous section used to be
   illegal because ``list[str]`` and ``list[int]`` both erased to just ``list[Any]``.
   This restriction was removed in mypy 0.620.

   Mypy also previously used to select the best matching variant using a different
   algorithm. If this algorithm failed to find a match, it would default to returning
   ``Any``. The new algorithm uses the "pick the first match" rule and will fall back
   to returning ``Any`` only if the input arguments also contain ``Any``.


Conditional overloads
---------------------

Sometimes it is useful to define overloads conditionally.
Common use cases include types that are unavailable at runtime or that
only exist in a certain Python version. All existing overload rules still apply.
For example, there must be at least two overloads.

.. note::

    Mypy can only infer a limited number of conditions.
    Supported ones currently include :py:data:`~typing.TYPE_CHECKING`, ``MYPY``,
    :ref:`version_and_platform_checks`, :option:`--always-true <mypy --always-true>`,
    and :option:`--always-false <mypy --always-false>` values.

.. code-block:: python

    from typing import TYPE_CHECKING, Any, overload

    if TYPE_CHECKING:
        class A: ...
        class B: ...


    if TYPE_CHECKING:
        @overload
        def func(var: A) -> A: ...

        @overload
        def func(var: B) -> B: ...

    def func(var: Any) -> Any:
        return var


    reveal_type(func(A()))  # Revealed type is "A"

.. code-block:: python

    # flags: --python-version 3.10
    import sys
    from typing import Any, overload

    class A: ...
    class B: ...
    class C: ...
    class D: ...


    if sys.version_info < (3, 7):
        @overload
        def func(var: A) -> A: ...

    elif sys.version_info >= (3, 10):
        @overload
        def func(var: B) -> B: ...

    else:
        @overload
        def func(var: C) -> C: ...

    @overload
    def func(var: D) -> D: ...

    def func(var: Any) -> Any:
        return var


    reveal_type(func(B()))  # Revealed type is "B"
    reveal_type(func(C()))  # No overload variant of "func" matches argument type "C"
        # Possible overload variants:
        #     def func(var: B) -> B
        #     def func(var: D) -> D
        # Revealed type is "Any"


.. note::

    In the last example, mypy is executed with
    :option:`--python-version 3.10 <mypy --python-version>`.
    Therefore, the condition ``sys.version_info >= (3, 10)`` will match and
    the overload for ``B`` will be added.
    The overloads for ``A`` and ``C`` are ignored!
    The overload for ``D`` is not defined conditionally and thus is also added.

When mypy cannot infer a condition to be always ``True`` or always ``False``,
an error is emitted.

.. code-block:: python

    from typing import Any, overload

    class A: ...
    class B: ...


    def g(bool_var: bool) -> None:
        if bool_var:  # Condition can't be inferred, unable to merge overloads
            @overload
            def func(var: A) -> A: ...

            @overload
            def func(var: B) -> B: ...

        def func(var: Any) -> Any: ...

        reveal_type(func(A()))  # Revealed type is "Any"


.. _advanced_self:

Advanced uses of self-types
***************************

Normally, mypy doesn't require annotations for the first arguments of instance and
class methods. However, they may be needed to have more precise static typing
for certain programming patterns.

Restricted methods in generic classes
-------------------------------------

In generic classes some methods may be allowed to be called only
for certain values of type arguments (Python 3.12 syntax):

.. code-block:: python

   class Tag[T]:
       item: T

       def uppercase_item(self: Tag[str]) -> str:
           return self.item.upper()

   def label(ti: Tag[int], ts: Tag[str]) -> None:
       ti.uppercase_item()  # E: Invalid self argument "Tag[int]" to attribute function
                            # "uppercase_item" with type "Callable[[Tag[str]], str]"
       ts.uppercase_item()  # This is OK

This pattern also allows matching on nested types in situations where the type
argument is itself generic (Python 3.12 syntax):

.. code-block:: python

   from collections.abc import Sequence

   class Storage[T]:
       def __init__(self, content: T) -> None:
           self._content = content

       def first_chunk[S](self: Storage[Sequence[S]]) -> S:
           return self._content[0]

   page: Storage[list[str]]
   page.first_chunk()  # OK, type is "str"

   Storage(0).first_chunk()  # Error: Invalid self argument "Storage[int]" to attribute function
                             # "first_chunk" with type "Callable[[Storage[Sequence[S]]], S]"

Finally, one can use overloads on self-type to express precise types of
some tricky methods (Python 3.12 syntax):

.. code-block:: python

   from collections.abc import Callable
   from typing import overload

   class Tag[T]:
       @overload
       def export(self: Tag[str]) -> str: ...
       @overload
       def export(self, converter: Callable[[T], str]) -> str: ...

       def export(self, converter=None):
           if isinstance(self.item, str):
               return self.item
           return converter(self.item)

In particular, an :py:meth:`~object.__init__` method overloaded on self-type
may be useful to annotate generic class constructors where type arguments
depend on constructor parameters in a non-trivial way, see e.g. :py:class:`~subprocess.Popen`.

Mixin classes
-------------

Using host class protocol as a self-type in mixin methods allows
more code re-usability for static typing of mixin classes. For example,
one can define a protocol that defines common functionality for
host classes instead of adding required abstract methods to every mixin:

.. code-block:: python

   class Lockable(Protocol):
       @property
       def lock(self) -> Lock: ...

   class AtomicCloseMixin:
       def atomic_close(self: Lockable) -> int:
           with self.lock:
               # perform actions

   class AtomicOpenMixin:
       def atomic_open(self: Lockable) -> int:
           with self.lock:
               # perform actions

   class File(AtomicCloseMixin, AtomicOpenMixin):
       def __init__(self) -> None:
           self.lock = Lock()

   class Bad(AtomicCloseMixin):
       pass

   f = File()
   b: Bad
   f.atomic_close()  # OK
   b.atomic_close()  # Error: Invalid self type for "atomic_close"

Note that the explicit self-type is *required* to be a protocol whenever it
is not a supertype of the current class. In this case mypy will check the validity
of the self-type only at the call site.

Precise typing of alternative constructors
------------------------------------------

Some classes may define alternative constructors. If these
classes are generic, self-type allows giving them precise
signatures (Python 3.12 syntax):

.. code-block:: python

   from typing import Self

   class Base[T]:
       def __init__(self, item: T) -> None:
           self.item = item

       @classmethod
       def make_pair(cls, item: T) -> tuple[Self, Self]:
           return cls(item), cls(item)

   class Sub[T](Base[T]):
       ...

   pair = Sub.make_pair('yes')  # Type is "tuple[Sub[str], Sub[str]]"
   bad = Sub[int].make_pair('no')  # Error: Argument 1 to "make_pair" of "Base"
                                   # has incompatible type "str"; expected "int"

.. _async-and-await:

Typing async/await
******************

Mypy lets you type coroutines that use the ``async/await`` syntax.
For more information regarding coroutines, see :pep:`492` and the
`asyncio documentation <python:library/asyncio>`_.

Functions defined using ``async def`` are typed similar to normal functions.
The return type annotation should be the same as the type of the value you
expect to get back when ``await``-ing the coroutine.

.. code-block:: python

   import asyncio

   async def format_string(tag: str, count: int) -> str:
       return f'T-minus {count} ({tag})'

   async def countdown(tag: str, count: int) -> str:
       while count > 0:
           my_str = await format_string(tag, count)  # type is inferred to be str
           print(my_str)
           await asyncio.sleep(0.1)
           count -= 1
       return "Blastoff!"

   asyncio.run(countdown("Millennium Falcon", 5))

The result of calling an ``async def`` function *without awaiting* will
automatically be inferred to be a value of type
:py:class:`Coroutine[Any, Any, T] <collections.abc.Coroutine>`, which is a subtype of
:py:class:`Awaitable[T] <collections.abc.Awaitable>`:

.. code-block:: python

   my_coroutine = countdown("Millennium Falcon", 5)
   reveal_type(my_coroutine)  # Revealed type is "typing.Coroutine[Any, Any, builtins.str]"

.. _async-iterators:

Asynchronous iterators
----------------------

If you have an asynchronous iterator, you can use the
:py:class:`~collections.abc.AsyncIterator` type in your annotations:

.. code-block:: python

   from collections.abc import AsyncIterator
   from typing import Optional
   import asyncio

   class arange:
       def __init__(self, start: int, stop: int, step: int) -> None:
           self.start = start
           self.stop = stop
           self.step = step
           self.count = start - step

       def __aiter__(self) -> AsyncIterator[int]:
           return self

       async def __anext__(self) -> int:
           self.count += self.step
           if self.count == self.stop:
               raise StopAsyncIteration
           else:
               return self.count

   async def run_countdown(tag: str, countdown: AsyncIterator[int]) -> str:
       async for i in countdown:
           print(f'T-minus {i} ({tag})')
           await asyncio.sleep(0.1)
       return "Blastoff!"

   asyncio.run(run_countdown("Serenity", arange(5, 0, -1)))

Async generators (introduced in :pep:`525`) are an easy way to create
async iterators:

.. code-block:: python

   from collections.abc import AsyncGenerator
   from typing import Optional
   import asyncio

   # Could also type this as returning AsyncIterator[int]
   async def arange(start: int, stop: int, step: int) -> AsyncGenerator[int, None]:
       current = start
       while (step > 0 and current < stop) or (step < 0 and current > stop):
           yield current
           current += step

   asyncio.run(run_countdown("Battlestar Galactica", arange(5, 0, -1)))

One common confusion is that the presence of a ``yield`` statement in an
``async def`` function has an effect on the type of the function:

.. code-block:: python

   from collections.abc import AsyncIterator

   async def arange(stop: int) -> AsyncIterator[int]:
       # When called, arange gives you an async iterator
       # Equivalent to Callable[[int], AsyncIterator[int]]
       i = 0
       while i < stop:
           yield i
           i += 1

   async def coroutine(stop: int) -> AsyncIterator[int]:
       # When called, coroutine gives you something you can await to get an async iterator
       # Equivalent to Callable[[int], Coroutine[Any, Any, AsyncIterator[int]]]
       return arange(stop)

   async def main() -> None:
       reveal_type(arange(5))  # Revealed type is "typing.AsyncIterator[builtins.int]"
       reveal_type(coroutine(5))  # Revealed type is "typing.Coroutine[Any, Any, typing.AsyncIterator[builtins.int]]"

       await arange(5)  # Error: Incompatible types in "await" (actual type "AsyncIterator[int]", expected type "Awaitable[Any]")
       reveal_type(await coroutine(5))  # Revealed type is "typing.AsyncIterator[builtins.int]"

This can sometimes come up when trying to define base classes, Protocols or overloads:

.. code-block:: python

    from collections.abc import AsyncIterator
    from typing import Protocol, overload

    class LauncherIncorrect(Protocol):
        # Because launch does not have yield, this has type
        # Callable[[], Coroutine[Any, Any, AsyncIterator[int]]]
        # instead of
        # Callable[[], AsyncIterator[int]]
        async def launch(self) -> AsyncIterator[int]:
            raise NotImplementedError

    class LauncherCorrect(Protocol):
        def launch(self) -> AsyncIterator[int]:
            raise NotImplementedError

    class LauncherAlsoCorrect(Protocol):
        async def launch(self) -> AsyncIterator[int]:
            raise NotImplementedError
            if False:
                yield 0

    # The type of the overloads is independent of the implementation.
    # In particular, their type is not affected by whether or not the
    # implementation contains a `yield`.
    # Use of `def`` makes it clear the type is Callable[..., AsyncIterator[int]],
    # whereas with `async def` it would be Callable[..., Coroutine[Any, Any, AsyncIterator[int]]]
    @overload
    def launch(*, count: int = ...) -> AsyncIterator[int]: ...
    @overload
    def launch(*, time: float = ...) -> AsyncIterator[int]: ...

    async def launch(*, count: int = 0, time: float = 0) -> AsyncIterator[int]:
        # The implementation of launch is an async generator and contains a yield
        yield 0
````

## File: docs/source/mypy_daemon.rst
````
.. _mypy_daemon:

.. program:: dmypy

Mypy daemon (mypy server)
=========================

Instead of running mypy as a command-line tool, you can also run it as
a long-running daemon (server) process and use a command-line client to
send type-checking requests to the server.  This way mypy can perform type
checking much faster, since program state cached from previous runs is kept
in memory and doesn't have to be read from the file system on each run.
The server also uses finer-grained dependency tracking to reduce the amount
of work that needs to be done.

If you have a large codebase to check, running mypy using the mypy
daemon can be *10 or more times faster* than the regular command-line
``mypy`` tool, especially if your workflow involves running mypy
repeatedly after small edits -- which is often a good idea, as this way
you'll find errors sooner.

.. note::

    The command-line interface of mypy daemon may change in future mypy
    releases.

.. note::

    Each mypy daemon process supports one user and one set of source files,
    and it can only process one type checking request at a time. You can
    run multiple mypy daemon processes to type check multiple repositories.


Basic usage
***********

The client utility ``dmypy`` is used to control the mypy daemon.
Use ``dmypy run -- <flags> <files>`` to type check a set of files
(or directories). This will launch the daemon if it is not running.
You can use almost arbitrary mypy flags after ``--``.  The daemon
will always run on the current host. Example::

    dmypy run -- prog.py pkg/*.py

``dmypy run`` will automatically restart the daemon if the
configuration or mypy version changes.

The initial run will process all the code and may take a while to
finish, but subsequent runs will be quick, especially if you've only
changed a few files. (You can use :ref:`remote caching <remote-cache>`
to speed up the initial run. The speedup can be significant if
you have a large codebase.)

.. note::

   Mypy 0.780 added support for following imports in dmypy (enabled by
   default). This functionality is still experimental. You can use
   ``--follow-imports=skip`` or ``--follow-imports=error`` to fall
   back to the stable functionality.  See :ref:`follow-imports` for
   details on how these work.

.. note::

    The mypy daemon requires ``--local-partial-types`` and automatically enables it.


Daemon client commands
**********************

While ``dmypy run`` is sufficient for most uses, some workflows
(ones using :ref:`remote caching <remote-cache>`, perhaps),
require more precise control over the lifetime of the daemon process:

* ``dmypy stop`` stops the daemon.

* ``dmypy start -- <flags>`` starts the daemon but does not check any files.
  You can use almost arbitrary mypy flags after ``--``.

* ``dmypy restart -- <flags>`` restarts the daemon. The flags are the same
  as with ``dmypy start``. This is equivalent to a stop command followed
  by a start.

* Use ``dmypy run --timeout SECONDS -- <flags>`` (or
  ``start`` or ``restart``) to automatically
  shut down the daemon after inactivity. By default, the daemon runs
  until it's explicitly stopped.

* ``dmypy check <files>`` checks a set of files using an already
  running daemon.

* ``dmypy recheck`` checks the same set of files as the most recent
  ``check`` or ``recheck`` command. (You can also use the :option:`--update`
  and :option:`--remove` options to alter the set of files, and to define
  which files should be processed.)

* ``dmypy status`` checks whether a daemon is running. It prints a
  diagnostic and exits with ``0`` if there is a running daemon.

Use ``dmypy --help`` for help on additional commands and command-line
options not discussed here, and ``dmypy <command> --help`` for help on
command-specific options.

Additional daemon flags
***********************

.. option:: --status-file FILE

   Use ``FILE`` as the status file for storing daemon runtime state. This is
   normally a JSON file that contains information about daemon process and
   connection. The default path is ``.dmypy.json`` in the current working
   directory.

.. option:: --log-file FILE

   Direct daemon stdout/stderr to ``FILE``. This is useful for debugging daemon
   crashes, since the server traceback is not always printed by the client.
   This is available for the ``start``, ``restart``, and ``run`` commands.

.. option:: --timeout TIMEOUT

   Automatically shut down server after ``TIMEOUT`` seconds of inactivity.
   This is available for the ``start``, ``restart``, and ``run`` commands.

.. option:: --update FILE

   Re-check ``FILE``, or add it to the set of files being
   checked (and check it). This option may be repeated, and it's only available for
   the ``recheck`` command.  By default, mypy finds and checks all files changed
   since the previous run and files that depend on them.  However, if you use this option
   (and/or :option:`--remove`), mypy assumes that only the explicitly
   specified files have changed. This is only useful to
   speed up mypy if you type check a very large number of files, and use an
   external, fast file system watcher, such as `watchman`_ or
   `watchdog`_, to determine which files got edited or deleted.
   *Note:* This option is never required and is only available for
   performance tuning.

.. option:: --remove FILE

   Remove ``FILE`` from the set of files being checked. This option may be
   repeated. This is only available for the
   ``recheck`` command. See :option:`--update` above for when this may be useful.
   *Note:* This option is never required and is only available for performance
   tuning.

.. option:: --fswatcher-dump-file FILE

   Collect information about the current internal file state. This is
   only available for the ``status`` command. This will dump JSON to
   ``FILE`` in the format ``{path: [modification_time, size,
   content_hash]}``. This is useful for debugging the built-in file
   system watcher. *Note:* This is an internal flag and the format may
   change.

.. option:: --perf-stats-file FILE

   Write performance profiling information to ``FILE``. This is only available
   for the ``check``, ``recheck``, and ``run`` commands.

.. option:: --export-types

   Store all expression types in memory for future use. This is useful to speed
   up future calls to ``dmypy inspect`` (but uses more memory). Only valid for
   ``check``, ``recheck``, and ``run`` command.

Static inference of annotations
*******************************

The mypy daemon supports (as an experimental feature) statically inferring
draft function and method type annotations. Use ``dmypy suggest FUNCTION`` to
generate a draft signature in the format
``(param_type_1, param_type_2, ...) -> ret_type`` (types are included for all
arguments, including keyword-only arguments, ``*args`` and ``**kwargs``).

This is a low-level feature intended to be used by editor integrations,
IDEs, and other tools (for example, the `mypy plugin for PyCharm`_),
to automatically add annotations to source files, or to propose function
signatures.

In this example, the function ``format_id()`` has no annotation:

.. code-block:: python

   def format_id(user):
       return f"User: {user}"

   root = format_id(0)

``dmypy suggest`` uses call sites, return statements, and other heuristics (such as
looking for signatures in base classes) to infer that ``format_id()`` accepts
an ``int`` argument and returns a ``str``. Use ``dmypy suggest module.format_id`` to
print the suggested signature for the function.

More generally, the target function may be specified in two ways:

* By its fully qualified name, i.e. ``[package.]module.[class.]function``.

* By its location in a source file, i.e. ``/path/to/file.py:line``. The path can be
  absolute or relative, and ``line`` can refer to any line number within
  the function body.

This command can also be used to find a more precise alternative for an existing,
imprecise annotation with some ``Any`` types.

The following flags customize various aspects of the ``dmypy suggest``
command.

.. option:: --json

   Output the signature as JSON, so that `PyAnnotate`_ can read it and add
   the signature to the source file. Here is what the JSON looks like:

   .. code-block:: python

      [{"func_name": "example.format_id",
        "line": 1,
        "path": "/absolute/path/to/example.py",
        "samples": 0,
        "signature": {"arg_types": ["int"], "return_type": "str"}}]

.. option:: --no-errors

   Only produce suggestions that cause no errors in the checked code. By default,
   mypy will try to find the most precise type, even if it causes some type errors.

.. option:: --no-any

   Only produce suggestions that don't contain ``Any`` types. By default mypy
   proposes the most precise signature found, even if it contains ``Any`` types.

.. option:: --flex-any FRACTION

   Only allow some fraction of types in the suggested signature to be ``Any`` types.
   The fraction ranges from ``0`` (same as ``--no-any``) to ``1``.

.. option:: --callsites

   Only find call sites for a given function instead of suggesting a type.
   This will produce a list with line numbers and types of actual
   arguments for each call: ``/path/to/file.py:line: (arg_type_1, arg_type_2, ...)``.

.. option:: --use-fixme NAME

   Use a dummy name instead of plain ``Any`` for types that cannot
   be inferred. This may be useful to emphasize to a user that a given type
   couldn't be inferred and needs to be entered manually.

.. option:: --max-guesses NUMBER

   Set the maximum number of types to try for a function (default: ``64``).

Statically inspect expressions
******************************

The daemon allows to get declared or inferred type of an expression (or other
information about an expression, such as known attributes or definition location)
using ``dmypy inspect LOCATION`` command. The location of the expression should be
specified in the format ``path/to/file.py:line:column[:end_line:end_column]``.
Both line and column are 1-based. Both start and end position are inclusive.
These rules match how mypy prints the error location in error messages.

If a span is given (i.e. all 4 numbers), then only an exactly matching expression
is inspected. If only a position is given (i.e. 2 numbers, line and column), mypy
will inspect all *expressions*, that include this position, starting from the
innermost one.

Consider this Python code snippet:

.. code-block:: python

   def foo(x: int, longer_name: str) -> None:
       x
       longer_name

Here to find the type of ``x`` one needs to call ``dmypy inspect src.py:2:5:2:5``
or ``dmypy inspect src.py:2:5``. While for ``longer_name`` one needs to call
``dmypy inspect src.py:3:5:3:15`` or, for example, ``dmypy inspect src.py:3:10``.
Please note that this command is only valid after daemon had a successful type
check (without parse errors), so that types are populated, e.g. using
``dmypy check``. In case where multiple expressions match the provided location,
their types are returned separated by a newline.

Important note: it is recommended to check files with :option:`--export-types`
since otherwise most inspections will not work without :option:`--force-reload`.

.. option:: --show INSPECTION

   What kind of inspection to run for expression(s) found. Currently the supported
   inspections are:

   * ``type`` (default): Show the best known type of a given expression.
   * ``attrs``: Show which attributes are valid for an expression (e.g. for
     auto-completion). Format is ``{"Base1": ["name_1", "name_2", ...]; "Base2": ...}``.
     Names are sorted by method resolution order. If expression refers to a module,
     then module attributes will be under key like ``"<full.module.name>"``.
   * ``definition`` (experimental): Show the definition location for a name
     expression or member expression. Format is ``path/to/file.py:line:column:Symbol``.
     If multiple definitions are found (e.g. for a Union attribute), they are
     separated by comma.

.. option:: --verbose

   Increase verbosity of types string representation (can be repeated).
   For example, this will print fully qualified names of instance types (like
   ``"builtins.str"``), instead of just a short name (like ``"str"``).

.. option:: --limit NUM

   If the location is given as ``line:column``, this will cause daemon to
   return only at most ``NUM`` inspections of innermost expressions.
   Value of 0 means no limit (this is the default). For example, if one calls
   ``dmypy inspect src.py:4:10 --limit=1`` with this code

   .. code-block:: python

      def foo(x: int) -> str: ..
      def bar(x: str) -> None: ...
      baz: int
      bar(foo(baz))

   This will output just one type ``"int"`` (for ``baz`` name expression).
   While without the limit option, it would output all three types: ``"int"``,
   ``"str"``, and ``"None"``.

.. option:: --include-span

   With this option on, the daemon will prepend each inspection result with
   the full span of corresponding expression, formatted as ``1:2:1:4 -> "int"``.
   This may be useful in case multiple expressions match a location.

.. option:: --include-kind

   With this option on, the daemon will prepend each inspection result with
   the kind of corresponding expression, formatted as ``NameExpr -> "int"``.
   If both this option and :option:`--include-span` are on, the kind will
   appear first, for example ``NameExpr:1:2:1:4 -> "int"``.

.. option:: --include-object-attrs

   This will make the daemon include attributes of ``object`` (excluded by
   default) in case of an ``atts`` inspection.

.. option:: --union-attrs

   Include attributes valid for some of possible expression types (by default
   an intersection is returned). This is useful for union types of type variables
   with values. For example, with this code:

   .. code-block:: python

      from typing import Union

      class A:
          x: int
          z: int
      class B:
          y: int
          z: int
      var: Union[A, B]
      var

   The command ``dmypy inspect --show attrs src.py:10:1`` will return
   ``{"A": ["z"], "B": ["z"]}``, while with ``--union-attrs`` it will return
   ``{"A": ["x", "z"], "B": ["y", "z"]}``.

.. option:: --force-reload

   Force re-parsing and re-type-checking file before inspection. By default
   this is done only when needed (for example file was not loaded from cache
   or daemon was initially run without ``--export-types`` mypy option),
   since reloading may be slow (up to few seconds for very large files).

.. TODO: Add similar section about find usages when added, and then move
   this to a separate file.


.. _watchman: https://facebook.github.io/watchman/
.. _watchdog: https://pypi.org/project/watchdog/
.. _PyAnnotate: https://github.com/dropbox/pyannotate
.. _mypy plugin for PyCharm: https://github.com/dropbox/mypy-PyCharm-plugin
````

## File: docs/source/protocols.rst
````
.. _protocol-types:

Protocols and structural subtyping
==================================

The Python type system supports two ways of deciding whether two objects are
compatible as types: nominal subtyping and structural subtyping.

*Nominal* subtyping is strictly based on the class hierarchy. If class ``Dog``
inherits class ``Animal``, it's a subtype of ``Animal``. Instances of ``Dog``
can be used when ``Animal`` instances are expected. This form of subtyping
is what Python's type system predominantly uses: it's easy to
understand and produces clear and concise error messages, and matches how the
native :py:func:`isinstance <isinstance>` check works -- based on class
hierarchy.

*Structural* subtyping is based on the operations that can be performed with an
object. Class ``Dog`` is a structural subtype of class ``Animal`` if the former
has all attributes and methods of the latter, and with compatible types.

Structural subtyping can be seen as a static equivalent of duck typing, which is
well known to Python programmers. See :pep:`544` for the detailed specification
of protocols and structural subtyping in Python.

.. _predefined_protocols:

Predefined protocols
********************

The :py:mod:`collections.abc`, :py:mod:`typing` and other stdlib modules define
various protocol classes that correspond to common Python protocols, such as
:py:class:`Iterable[T] <collections.abc.Iterable>`. If a class
defines a suitable :py:meth:`__iter__ <object.__iter__>` method, mypy understands that it
implements the iterable protocol and is compatible with :py:class:`Iterable[T] <collections.abc.Iterable>`.
For example, ``IntList`` below is iterable, over ``int`` values:

.. code-block:: python

   from __future__ import annotations

   from collections.abc import Iterator, Iterable

   class IntList:
       def __init__(self, value: int, next: IntList | None) -> None:
           self.value = value
           self.next = next

       def __iter__(self) -> Iterator[int]:
           current = self
           while current:
               yield current.value
               current = current.next

   def print_numbered(items: Iterable[int]) -> None:
       for n, x in enumerate(items):
           print(n + 1, x)

   x = IntList(3, IntList(5, None))
   print_numbered(x)  # OK
   print_numbered([4, 5])  # Also OK

:ref:`predefined_protocols_reference` lists various protocols defined in
:py:mod:`collections.abc` and :py:mod:`typing` and the signatures of the corresponding methods
you need to define to implement each protocol.

.. note::
    ``typing`` also contains deprecated aliases to protocols and ABCs defined in
    :py:mod:`collections.abc`, such as :py:class:`Iterable[T] <typing.Iterable>`.
    These are only necessary in Python 3.8 and earlier, since the protocols in
    ``collections.abc`` didn't yet support subscripting (``[]``) in Python 3.8,
    but the aliases in ``typing`` have always supported
    subscripting. In Python 3.9 and later, the aliases in ``typing`` don't provide
    any extra functionality.

Simple user-defined protocols
*****************************

You can define your own protocol class by inheriting the special ``Protocol``
class:

.. code-block:: python

   from collections.abc import Iterable
   from typing import Protocol

   class SupportsClose(Protocol):
       # Empty method body (explicit '...')
       def close(self) -> None: ...

   class Resource:  # No SupportsClose base class!

       def close(self) -> None:
          self.resource.release()

       # ... other methods ...

   def close_all(items: Iterable[SupportsClose]) -> None:
       for item in items:
           item.close()

   close_all([Resource(), open('some/file')])  # OK

``Resource`` is a subtype of the ``SupportsClose`` protocol since it defines
a compatible ``close`` method. Regular file objects returned by :py:func:`open` are
similarly compatible with the protocol, as they support ``close()``.

Defining subprotocols and subclassing protocols
***********************************************

You can also define subprotocols. Existing protocols can be extended
and merged using multiple inheritance. Example:

.. code-block:: python

   # ... continuing from the previous example

   class SupportsRead(Protocol):
       def read(self, amount: int) -> bytes: ...

   class TaggedReadableResource(SupportsClose, SupportsRead, Protocol):
       label: str

   class AdvancedResource(Resource):
       def __init__(self, label: str) -> None:
           self.label = label

       def read(self, amount: int) -> bytes:
           # some implementation
           ...

   resource: TaggedReadableResource
   resource = AdvancedResource('handle with care')  # OK

Note that inheriting from an existing protocol does not automatically
turn the subclass into a protocol -- it just creates a regular
(non-protocol) class or ABC that implements the given protocol (or
protocols). The ``Protocol`` base class must always be explicitly
present if you are defining a protocol:

.. code-block:: python

   class NotAProtocol(SupportsClose):  # This is NOT a protocol
       new_attr: int

   class Concrete:
      new_attr: int = 0

      def close(self) -> None:
          ...

   # Error: nominal subtyping used by default
   x: NotAProtocol = Concrete()  # Error!

You can also include default implementations of methods in
protocols. If you explicitly subclass these protocols you can inherit
these default implementations.

Explicitly including a protocol as a
base class is also a way of documenting that your class implements a
particular protocol, and it forces mypy to verify that your class
implementation is actually compatible with the protocol. In particular,
omitting a value for an attribute or a method body will make it implicitly
abstract:

.. code-block:: python

   class SomeProto(Protocol):
       attr: int  # Note, no right hand side
       def method(self) -> str: ...  # Literally just ... here

   class ExplicitSubclass(SomeProto):
       pass

   ExplicitSubclass()  # error: Cannot instantiate abstract class 'ExplicitSubclass'
                       # with abstract attributes 'attr' and 'method'

Similarly, explicitly assigning to a protocol instance can be a way to ask the
type checker to verify that your class implements a protocol:

.. code-block:: python

   _proto: SomeProto = cast(ExplicitSubclass, None)

Invariance of protocol attributes
*********************************

A common issue with protocols is that protocol attributes are invariant.
For example:

.. code-block:: python

   class Box(Protocol):
         content: object

   class IntBox:
         content: int

   def takes_box(box: Box) -> None: ...

   takes_box(IntBox())  # error: Argument 1 to "takes_box" has incompatible type "IntBox"; expected "Box"
                        # note:  Following member(s) of "IntBox" have conflicts:
                        # note:      content: expected "object", got "int"

This is because ``Box`` defines ``content`` as a mutable attribute.
Here's why this is problematic:

.. code-block:: python

   def takes_box_evil(box: Box) -> None:
       box.content = "asdf"  # This is bad, since box.content is supposed to be an object

   my_int_box = IntBox()
   takes_box_evil(my_int_box)
   my_int_box.content + 1  # Oops, TypeError!

This can be fixed by declaring ``content`` to be read-only in the ``Box``
protocol using ``@property``:

.. code-block:: python

   class Box(Protocol):
       @property
       def content(self) -> object: ...

   class IntBox:
       content: int

   def takes_box(box: Box) -> None: ...

   takes_box(IntBox(42))  # OK

Recursive protocols
*******************

Protocols can be recursive (self-referential) and mutually
recursive. This is useful for declaring abstract recursive collections
such as trees and linked lists:

.. code-block:: python

   from __future__ import annotations

   from typing import Protocol

   class TreeLike(Protocol):
       value: int

       @property
       def left(self) -> TreeLike | None: ...

       @property
       def right(self) -> TreeLike | None: ...

   class SimpleTree:
       def __init__(self, value: int) -> None:
           self.value = value
           self.left: SimpleTree | None = None
           self.right: SimpleTree | None = None

   root: TreeLike = SimpleTree(0)  # OK

Using isinstance() with protocols
*********************************

You can use a protocol class with :py:func:`isinstance` if you decorate it
with the ``@runtime_checkable`` class decorator. The decorator adds
rudimentary support for runtime structural checks:

.. code-block:: python

   from typing import Protocol, runtime_checkable

   @runtime_checkable
   class Portable(Protocol):
       handles: int

   class Mug:
       def __init__(self) -> None:
           self.handles = 1

   def use(handles: int) -> None: ...

   mug = Mug()
   if isinstance(mug, Portable):  # Works at runtime!
      use(mug.handles)

:py:func:`isinstance` also works with the :ref:`predefined protocols <predefined_protocols>`
in :py:mod:`typing` such as :py:class:`~typing.Iterable`.

.. warning::
   :py:func:`isinstance` with protocols is not completely safe at runtime.
   For example, signatures of methods are not checked. The runtime
   implementation only checks that all protocol members exist,
   not that they have the correct type. :py:func:`issubclass` with protocols
   will only check for the existence of methods.

.. note::
   :py:func:`isinstance` with protocols can also be surprisingly slow.
   In many cases, you're better served by using :py:func:`hasattr` to
   check for the presence of attributes.

.. _callback_protocols:

Callback protocols
******************

Protocols can be used to define flexible callback types that are hard
(or even impossible) to express using the
:py:class:`Callable[...] <collections.abc.Callable>` syntax,
such as variadic, overloaded, and complex generic callbacks. They are defined with a
special :py:meth:`__call__ <object.__call__>` member:

.. code-block:: python

   from collections.abc import Iterable
   from typing import Optional, Protocol

   class Combiner(Protocol):
       def __call__(self, *vals: bytes, maxlen: int | None = None) -> list[bytes]: ...

   def batch_proc(data: Iterable[bytes], cb_results: Combiner) -> bytes:
       for item in data:
           ...

   def good_cb(*vals: bytes, maxlen: int | None = None) -> list[bytes]:
       ...
   def bad_cb(*vals: bytes, maxitems: int | None) -> list[bytes]:
       ...

   batch_proc([], good_cb)  # OK
   batch_proc([], bad_cb)   # Error! Argument 2 has incompatible type because of
                            # different name and kind in the callback

Callback protocols and :py:class:`~collections.abc.Callable` types can be used mostly interchangeably.
Parameter names in :py:meth:`__call__ <object.__call__>` methods must be identical, unless
the parameters are positional-only. Example (using the legacy syntax for generic functions):

.. code-block:: python

   from collections.abc import Callable
   from typing import Protocol, TypeVar

   T = TypeVar('T')

   class Copy(Protocol):
       # '/' marks the end of positional-only parameters
       def __call__(self, origin: T, /) -> T: ...

   copy_a: Callable[[T], T]
   copy_b: Copy

   copy_a = copy_b  # OK
   copy_b = copy_a  # Also OK

Binding of types in protocol attributes
***************************************

All protocol attributes annotations are treated as externally visible types
of those attributes. This means that for example callables are not bound,
and descriptors are not invoked:

.. code-block:: python

   from typing import Callable, Protocol, overload

   class Integer:
       @overload
       def __get__(self, instance: None, owner: object) -> Integer: ...
       @overload
       def __get__(self, instance: object, owner: object) -> int: ...
       # <some implementation>

   class Example(Protocol):
       foo: Callable[[object], int]
       bar: Integer

   ex: Example
   reveal_type(ex.foo)  # Revealed type is Callable[[object], int]
   reveal_type(ex.bar)  # Revealed type is Integer

In other words, protocol attribute types are handled as they would appear in a
``self`` attribute annotation in a regular class. If you want some protocol
attributes to be handled as though they were defined at class level, you should
declare them explicitly using ``ClassVar[...]``. Continuing previous example:

.. code-block:: python

   from typing import ClassVar

   class OtherExample(Protocol):
       # This style is *not recommended*, but may be needed to reuse
       # some complex callable types. Otherwise use regular methods.
       foo: ClassVar[Callable[[object], int]]
       # This may be needed to mimic descriptor access on Type[...] types,
       # otherwise use a plain "bar: int" style.
       bar: ClassVar[Integer]

   ex2: OtherExample
   reveal_type(ex2.foo)  # Revealed type is Callable[[], int]
   reveal_type(ex2.bar)  # Revealed type is int

.. _predefined_protocols_reference:

Predefined protocol reference
*****************************

Iteration protocols
...................

The iteration protocols are useful in many contexts. For example, they allow
iteration of objects in for loops.

collections.abc.Iterable[T]
---------------------------

The :ref:`example above <predefined_protocols>` has a simple implementation of an
:py:meth:`__iter__ <object.__iter__>` method.

.. code-block:: python

   def __iter__(self) -> Iterator[T]

See also :py:class:`~collections.abc.Iterable`.

collections.abc.Iterator[T]
---------------------------

.. code-block:: python

   def __next__(self) -> T
   def __iter__(self) -> Iterator[T]

See also :py:class:`~collections.abc.Iterator`.

Collection protocols
....................

Many of these are implemented by built-in container types such as
:py:class:`list` and :py:class:`dict`, and these are also useful for user-defined
collection objects.

collections.abc.Sized
---------------------

This is a type for objects that support :py:func:`len(x) <len>`.

.. code-block:: python

   def __len__(self) -> int

See also :py:class:`~collections.abc.Sized`.

collections.abc.Container[T]
----------------------------

This is a type for objects that support the ``in`` operator.

.. code-block:: python

   def __contains__(self, x: object) -> bool

See also :py:class:`~collections.abc.Container`.

collections.abc.Collection[T]
-----------------------------

.. code-block:: python

   def __len__(self) -> int
   def __iter__(self) -> Iterator[T]
   def __contains__(self, x: object) -> bool

See also :py:class:`~collections.abc.Collection`.

One-off protocols
.................

These protocols are typically only useful with a single standard
library function or class.

collections.abc.Reversible[T]
-----------------------------

This is a type for objects that support :py:func:`reversed(x) <reversed>`.

.. code-block:: python

   def __reversed__(self) -> Iterator[T]

See also :py:class:`~collections.abc.Reversible`.

typing.SupportsAbs[T]
---------------------

This is a type for objects that support :py:func:`abs(x) <abs>`. ``T`` is the type of
value returned by :py:func:`abs(x) <abs>`.

.. code-block:: python

   def __abs__(self) -> T

See also :py:class:`~typing.SupportsAbs`.

typing.SupportsBytes
--------------------

This is a type for objects that support :py:class:`bytes(x) <bytes>`.

.. code-block:: python

   def __bytes__(self) -> bytes

See also :py:class:`~typing.SupportsBytes`.

.. _supports-int-etc:

typing.SupportsComplex
----------------------

This is a type for objects that support :py:class:`complex(x) <complex>`. Note that no arithmetic operations
are supported.

.. code-block:: python

   def __complex__(self) -> complex

See also :py:class:`~typing.SupportsComplex`.

typing.SupportsFloat
--------------------

This is a type for objects that support :py:class:`float(x) <float>`. Note that no arithmetic operations
are supported.

.. code-block:: python

   def __float__(self) -> float

See also :py:class:`~typing.SupportsFloat`.

typing.SupportsInt
------------------

This is a type for objects that support :py:class:`int(x) <int>`. Note that no arithmetic operations
are supported.

.. code-block:: python

   def __int__(self) -> int

See also :py:class:`~typing.SupportsInt`.

typing.SupportsRound[T]
-----------------------

This is a type for objects that support :py:func:`round(x) <round>`.

.. code-block:: python

   def __round__(self) -> T

See also :py:class:`~typing.SupportsRound`.

Async protocols
...............

These protocols can be useful in async code. See :ref:`async-and-await`
for more information.

collections.abc.Awaitable[T]
----------------------------

.. code-block:: python

   def __await__(self) -> Generator[Any, None, T]

See also :py:class:`~collections.abc.Awaitable`.

collections.abc.AsyncIterable[T]
--------------------------------

.. code-block:: python

   def __aiter__(self) -> AsyncIterator[T]

See also :py:class:`~collections.abc.AsyncIterable`.

collections.abc.AsyncIterator[T]
--------------------------------

.. code-block:: python

   def __anext__(self) -> Awaitable[T]
   def __aiter__(self) -> AsyncIterator[T]

See also :py:class:`~collections.abc.AsyncIterator`.

Context manager protocols
.........................

There are two protocols for context managers -- one for regular context
managers and one for async ones. These allow defining objects that can
be used in ``with`` and ``async with`` statements.

contextlib.AbstractContextManager[T]
------------------------------------

.. code-block:: python

   def __enter__(self) -> T
   def __exit__(self,
                exc_type: type[BaseException] | None,
                exc_value: BaseException | None,
                traceback: TracebackType | None) -> bool | None

See also :py:class:`~contextlib.AbstractContextManager`.

contextlib.AbstractAsyncContextManager[T]
-----------------------------------------

.. code-block:: python

   def __aenter__(self) -> Awaitable[T]
   def __aexit__(self,
                 exc_type: type[BaseException] | None,
                 exc_value: BaseException | None,
                 traceback: TracebackType | None) -> Awaitable[bool | None]

See also :py:class:`~contextlib.AbstractAsyncContextManager`.
````

## File: docs/source/running_mypy.rst
````
.. _running-mypy:

Running mypy and managing imports
=================================

The :ref:`getting-started` page should have already introduced you
to the basics of how to run mypy -- pass in the files and directories
you want to type check via the command line::

    $ mypy foo.py bar.py some_directory

This page discusses in more detail how exactly to specify what files
you want mypy to type check, how mypy discovers imported modules,
and recommendations on how to handle any issues you may encounter
along the way.

If you are interested in learning about how to configure the
actual way mypy type checks your code, see our
:ref:`command-line` guide.


.. _specifying-code-to-be-checked:

Specifying code to be checked
*****************************

Mypy lets you specify what files it should type check in several different ways.

1.  First, you can pass in paths to Python files and directories you
    want to type check. For example::

        $ mypy file_1.py foo/file_2.py file_3.pyi some/directory

    The above command tells mypy it should type check all of the provided
    files together. In addition, mypy will recursively type check the
    entire contents of any provided directories.

    For more details about how exactly this is done, see
    :ref:`Mapping file paths to modules <mapping-paths-to-modules>`.

2.  Second, you can use the :option:`-m <mypy -m>` flag (long form: :option:`--module <mypy --module>`) to
    specify a module name to be type checked. The name of a module
    is identical to the name you would use to import that module
    within a Python program. For example, running::

        $ mypy -m html.parser

    ...will type check the module ``html.parser`` (this happens to be
    a library stub).

    Mypy will use an algorithm very similar to the one Python uses to
    find where modules and imports are located on the file system.
    For more details, see :ref:`finding-imports`.

3.  Third, you can use the :option:`-p <mypy -p>` (long form: :option:`--package <mypy --package>`) flag to
    specify a package to be (recursively) type checked. This flag
    is almost identical to the :option:`-m <mypy -m>` flag except that if you give it
    a package name, mypy will recursively type check all submodules
    and subpackages of that package. For example, running::

        $ mypy -p html

    ...will type check the entire ``html`` package (of library stubs).
    In contrast, if we had used the :option:`-m <mypy -m>` flag, mypy would have type
    checked just ``html``'s ``__init__.py`` file and anything imported
    from there.

    Note that we can specify multiple packages and modules on the
    command line. For example::

      $ mypy --package p.a --package p.b --module c

4.  Fourth, you can also instruct mypy to directly type check small
    strings as programs by using the :option:`-c <mypy -c>` (long form: :option:`--command <mypy --command>`)
    flag. For example::

        $ mypy -c 'x = [1, 2]; print(x())'

    ...will type check the above string as a mini-program (and in this case,
    will report that ``list[int]`` is not callable).

You can also use the :confval:`files` option in your :file:`mypy.ini` file to specify which
files to check, in which case you can simply run ``mypy`` with no arguments.


Reading a list of files from a file
***********************************

Finally, any command-line argument starting with ``@`` reads additional
command-line arguments from the file following the ``@`` character.
This is primarily useful if you have a file containing a list of files
that you want to be type-checked: instead of using shell syntax like::

    $ mypy $(cat file_of_files.txt)

you can use this instead::

    $ mypy @file_of_files.txt

This file can technically also contain any command line flag, not
just file paths. However, if you want to configure many different
flags, the recommended approach is to use a
:ref:`configuration file <config-file>` instead.


.. _mapping-paths-to-modules:

Mapping file paths to modules
*****************************

One of the main ways you can tell mypy what to type check
is by providing mypy a list of paths. For example::

    $ mypy file_1.py foo/file_2.py file_3.pyi some/directory

This section describes how exactly mypy maps the provided paths
to modules to type check.

- Mypy will check all paths provided that correspond to files.

- Mypy will recursively discover and check all files ending in ``.py`` or
  ``.pyi`` in directory paths provided, after accounting for
  :option:`--exclude <mypy --exclude>`.

- For each file to be checked, mypy will attempt to associate the file (e.g.
  ``project/foo/bar/baz.py``) with a fully qualified module name (e.g.
  ``foo.bar.baz``). The directory the package is in (``project``) is then
  added to mypy's module search paths.

How mypy determines fully qualified module names depends on if the options
:option:`--no-namespace-packages <mypy --no-namespace-packages>` and
:option:`--explicit-package-bases <mypy --explicit-package-bases>` are set.

1. If :option:`--no-namespace-packages <mypy --no-namespace-packages>` is set,
   mypy will rely solely upon the presence of ``__init__.py[i]`` files to
   determine the fully qualified module name. That is, mypy will crawl up the
   directory tree for as long as it continues to find ``__init__.py`` (or
   ``__init__.pyi``) files.

   For example, if your directory tree consists of ``pkg/subpkg/mod.py``, mypy
   would require ``pkg/__init__.py`` and ``pkg/subpkg/__init__.py`` to exist in
   order correctly associate ``mod.py`` with ``pkg.subpkg.mod``

2. The default case. If :option:`--namespace-packages <mypy
   --no-namespace-packages>` is on, but :option:`--explicit-package-bases <mypy
   --explicit-package-bases>` is off, mypy will allow for the possibility that
   directories without ``__init__.py[i]`` are packages. Specifically, mypy will
   look at all parent directories of the file and use the location of the
   highest ``__init__.py[i]`` in the directory tree to determine the top-level
   package.

   For example, say your directory tree consists solely of ``pkg/__init__.py``
   and ``pkg/a/b/c/d/mod.py``. When determining ``mod.py``'s fully qualified
   module name, mypy will look at ``pkg/__init__.py`` and conclude that the
   associated module name is ``pkg.a.b.c.d.mod``.

3. You'll notice that the above case still relies on ``__init__.py``. If
   you can't put an ``__init__.py`` in your top-level package, but still wish to
   pass paths (as opposed to packages or modules using the ``-p`` or ``-m``
   flags), :option:`--explicit-package-bases <mypy --explicit-package-bases>`
   provides a solution.

   With :option:`--explicit-package-bases <mypy --explicit-package-bases>`, mypy
   will locate the nearest parent directory that is a member of the ``MYPYPATH``
   environment variable, the :confval:`mypy_path` config or is the current
   working directory. Mypy will then use the relative path to determine the
   fully qualified module name.

   For example, say your directory tree consists solely of
   ``src/namespace_pkg/mod.py``. If you run the following command, mypy
   will correctly associate ``mod.py`` with ``namespace_pkg.mod``::

       $ MYPYPATH=src mypy --namespace-packages --explicit-package-bases .

If you pass a file not ending in ``.py[i]``, the module name assumed is
``__main__`` (matching the behavior of the Python interpreter), unless
:option:`--scripts-are-modules <mypy --scripts-are-modules>` is passed.

Passing :option:`-v <mypy -v>` will show you the files and associated module
names that mypy will check.


How mypy handles imports
************************

When mypy encounters an ``import`` statement, it will first
:ref:`attempt to locate <finding-imports>` that module
or type stubs for that module in the file system. Mypy will then
type check the imported module. There are three different outcomes
of this process:

1.  Mypy is unable to follow the import: the module either does not
    exist, or is a third party library that does not use type hints.

2.  Mypy is able to follow and type check the import, but you did
    not want mypy to type check that module at all.

3.  Mypy is able to successfully both follow and type check the
    module, and you want mypy to type check that module.

The third outcome is what mypy will do in the ideal case. The following
sections will discuss what to do in the other two cases.

.. _ignore-missing-imports:
.. _fix-missing-imports:

Missing imports
***************

When you import a module, mypy may report that it is unable to follow
the import. This can cause errors that look like the following:

.. code-block:: text

    main.py:1: error: Skipping analyzing 'django': module is installed, but missing library stubs or py.typed marker
    main.py:2: error: Library stubs not installed for "requests"
    main.py:3: error: Cannot find implementation or library stub for module named "this_module_does_not_exist"

If you get any of these errors on an import, mypy will assume the type of that
module is ``Any``, the dynamic type. This means attempting to access any
attribute of the module will automatically succeed:

.. code-block:: python

    # Error: Cannot find implementation or library stub for module named 'does_not_exist'
    import does_not_exist

    # But this type checks, and x will have type 'Any'
    x = does_not_exist.foobar()

This can result in mypy failing to warn you about errors in your code. Since
operations on ``Any`` result in ``Any``, these dynamic types can propagate
through your code, making type checking less effective. See
:ref:`dynamic-typing` for more information.

The next sections describe what each of these errors means and recommended next steps; scroll to
the section that matches your error.


Missing library stubs or py.typed marker
----------------------------------------

If you are getting a ``Skipping analyzing X: module is installed, but missing library stubs or py.typed marker``,
error, this means mypy was able to find the module you were importing, but no
corresponding type hints.

Mypy will not try inferring the types of any 3rd party libraries you have installed
unless they either have declared themselves to be
:ref:`PEP 561 compliant stub package <installed-packages>` (e.g. with a ``py.typed`` file) or have registered
themselves on `typeshed <https://github.com/python/typeshed>`_, the repository
of types for the standard library and some 3rd party libraries.

If you are getting this error, try to obtain type hints for the library you're using:

1.  Upgrading the version of the library you're using, in case a newer version
    has started to include type hints.

2.  Searching to see if there is a :ref:`PEP 561 compliant stub package <installed-packages>`
    corresponding to your third party library. Stub packages let you install
    type hints independently from the library itself.

    For example, if you want type hints for the ``django`` library, you can
    install the `django-stubs <https://pypi.org/project/django-stubs/>`_ package.

3.  :ref:`Writing your own stub files <stub-files>` containing type hints for
    the library. You can point mypy at your type hints either by passing
    them in via the command line, by using the  :confval:`files` or :confval:`mypy_path`
    config file options, or by
    adding the location to the ``MYPYPATH`` environment variable.

    These stub files do not need to be complete! A good strategy is to use
    :ref:`stubgen <stubgen>`, a program that comes bundled with mypy, to generate a first
    rough draft of the stubs. You can then iterate on just the parts of the
    library you need.

    If you want to share your work, you can try contributing your stubs back
    to the library -- see our documentation on creating
    :ref:`PEP 561 compliant packages <installed-packages>`.

4.  Force mypy to analyze the library as best as it can (as if the library provided
    a ``py.typed`` file), despite it likely missing any type annotations. In general,
    the quality of type checking will be poor and mypy may have issues when
    analyzing code not designed to be type checked.

    You can do this via setting the
    :option:`--follow-untyped-imports <mypy --follow-untyped-imports>`
    command line flag or :confval:`follow_untyped_imports` config file option to True.
    This option can be specified on a per-module basis as well:

    .. tab:: mypy.ini

        .. code-block:: ini

            [mypy-untyped_package.*]
            follow_untyped_imports = True

    .. tab:: pyproject.toml

        .. code-block:: toml

            [[tool.mypy.overrides]]
            module = ["untyped_package.*"]
            follow_untyped_imports = true

If you are unable to find any existing type hints nor have time to write your
own, you can instead *suppress* the errors.

All this will do is make mypy stop reporting an error on the line containing the
import: the imported module will continue to be of type ``Any``, and mypy may
not catch errors in its use.

1.  To suppress a *single* missing import error, add a ``# type: ignore`` at the end of the
    line containing the import.

2.  To suppress *all* missing import errors from a single library, add
    a per-module section to your :ref:`mypy config file <config-file>` setting
    :confval:`ignore_missing_imports` to True for that library. For example,
    suppose your codebase
    makes heavy use of an (untyped) library named ``foobar``. You can silence
    all import errors associated with that library and that library alone by
    adding the following section to your config file:

    .. tab:: mypy.ini

        .. code-block:: ini

            [mypy-foobar.*]
            ignore_missing_imports = True

    .. tab:: pyproject.toml

        .. code-block:: toml

            [[tool.mypy.overrides]]
            module = ["foobar.*"]
            ignore_missing_imports = true

    Note: this option is equivalent to adding a ``# type: ignore`` to every
    import of ``foobar`` in your codebase. For more information, see the
    documentation about configuring
    :ref:`import discovery <config-file-import-discovery>` in config files.
    The ``.*`` after ``foobar`` will ignore imports of ``foobar`` modules
    and subpackages in addition to the ``foobar`` top-level package namespace.

3.  To suppress *all* missing import errors for *all* untyped libraries
    in your codebase, use :option:`--disable-error-code=import-untyped <mypy --ignore-missing-imports>`.
    See :ref:`code-import-untyped` for more details on this error code.

    You can also set :confval:`disable_error_code`, like so:

    .. tab:: mypy.ini

        .. code-block:: ini

            [mypy]
            disable_error_code = import-untyped

    .. tab:: pyproject.toml

        .. code-block:: ini

            [tool.mypy]
            disable_error_code = ["import-untyped"]

    You can also set the :option:`--ignore-missing-imports <mypy --ignore-missing-imports>`
    command line flag or set the :confval:`ignore_missing_imports` config file
    option to True in the *global* section of your mypy config file. We
    recommend avoiding ``--ignore-missing-imports`` if possible: it's equivalent
    to adding a ``# type: ignore`` to all unresolved imports in your codebase.


Library stubs not installed
---------------------------

If mypy can't find stubs for a third-party library, and it knows that stubs exist for
the library, you will get a message like this:

.. code-block:: text

    main.py:1: error: Library stubs not installed for "yaml"
    main.py:1: note: Hint: "python3 -m pip install types-PyYAML"
    main.py:1: note: (or run "mypy --install-types" to install all missing stub packages)

You can resolve the issue by running the suggested pip commands.
If you're running mypy in CI, you can ensure the presence of any stub packages
you need the same as you would any other test dependency, e.g. by adding them to
the appropriate ``requirements.txt`` file.

Alternatively, add the :option:`--install-types <mypy --install-types>`
to your mypy command to install all known missing stubs:

.. code-block:: text

    mypy --install-types

This is slower than explicitly installing stubs, since it effectively
runs mypy twice -- the first time to find the missing stubs, and
the second time to type check your code properly after mypy has
installed the stubs. It also can make controlling stub versions harder,
resulting in less reproducible type checking.

By default, :option:`--install-types <mypy --install-types>` shows a confirmation prompt.
Use :option:`--non-interactive <mypy --non-interactive>` to install all suggested
stub packages without asking for confirmation *and* type check your code:

If you've already installed the relevant third-party libraries in an environment
other than the one mypy is running in, you can use :option:`--python-executable
<mypy --python-executable>` flag to point to the Python executable for that
environment, and mypy will find packages installed for that Python executable.

If you've installed the relevant stub packages and are still getting this error,
see the :ref:`section below <missing-type-hints-for-third-party-library>`.

.. _missing-type-hints-for-third-party-library:

Cannot find implementation or library stub
------------------------------------------

If you are getting a ``Cannot find implementation or library stub for module``
error, this means mypy was not able to find the module you are trying to
import, whether it comes bundled with type hints or not. If you are getting
this error, try:

1.  Making sure your import does not contain a typo.

2.  If the module is a third party library, making sure that mypy is able
    to find the interpreter containing the installed library.

    For example, if you are running your code in a virtualenv, make sure
    to install and use mypy within the virtualenv. Alternatively, if you
    want to use a globally installed mypy, set the
    :option:`--python-executable <mypy --python-executable>` command
    line flag to point the Python interpreter containing your installed
    third party packages.

    You can confirm that you are running mypy from the environment you expect
    by running it like ``python -m mypy ...``. You can confirm that you are
    installing into the environment you expect by running pip like
    ``python -m pip ...``.

3.  Reading the :ref:`finding-imports` section below to make sure you
    understand how exactly mypy searches for and finds modules and modify
    how you're invoking mypy accordingly.

4.  Directly specifying the directory containing the module you want to
    type check from the command line, by using the :confval:`mypy_path`
    or :confval:`files` config file options,
    or by using the ``MYPYPATH`` environment variable.

    Note: if the module you are trying to import is actually a *submodule* of
    some package, you should specify the directory containing the *entire* package.
    For example, suppose you are trying to add the module ``foo.bar.baz``
    which is located at ``~/foo-project/src/foo/bar/baz.py``. In this case,
    you must run ``mypy ~/foo-project/src`` (or set the ``MYPYPATH`` to
    ``~/foo-project/src``).

.. _finding-imports:

How imports are found
*********************

When mypy encounters an ``import`` statement or receives module
names from the command line via the :option:`--module <mypy --module>` or :option:`--package <mypy --package>`
flags, mypy tries to find the module on the file system similar
to the way Python finds it. However, there are some differences.

First, mypy has its own search path.
This is computed from the following items:

- The ``MYPYPATH`` environment variable
  (a list of directories, colon-separated on UNIX systems, semicolon-separated on Windows).
- The :confval:`mypy_path` config file option.
- The directories containing the sources given on the command line
  (see :ref:`Mapping file paths to modules <mapping-paths-to-modules>`).
- The installed packages marked as safe for type checking (see
  :ref:`PEP 561 support <installed-packages>`)
- The relevant directories of the
  `typeshed <https://github.com/python/typeshed>`_ repo.

.. note::

    You cannot point to a stub-only package (:pep:`561`) via the ``MYPYPATH``, it must be
    installed (see :ref:`PEP 561 support <installed-packages>`)

Second, mypy searches for stub files in addition to regular Python files
and packages.
The rules for searching for a module ``foo`` are as follows:

- The search looks in each of the directories in the search path
  (see above) until a match is found.
- If a package named ``foo`` is found (i.e. a directory
  ``foo`` containing an ``__init__.py`` or ``__init__.pyi`` file)
  that's a match.
- If a stub file named ``foo.pyi`` is found, that's a match.
- If a Python module named ``foo.py`` is found, that's a match.

These matches are tried in order, so that if multiple matches are found
in the same directory on the search path
(e.g. a package and a Python file, or a stub file and a Python file)
the first one in the above list wins.

In particular, if a Python file and a stub file are both present in the
same directory on the search path, only the stub file is used.
(However, if the files are in different directories, the one found
in the earlier directory is used.)

Setting :confval:`mypy_path`/``MYPYPATH`` is mostly useful in the case
where you want to try running mypy against multiple distinct
sets of files that happen to share some common dependencies.

For example, if you have multiple projects that happen to be
using the same set of work-in-progress stubs, it could be
convenient to just have your ``MYPYPATH`` point to a single
directory containing the stubs.

.. _follow-imports:

Following imports
*****************

Mypy is designed to :ref:`doggedly follow all imports <finding-imports>`,
even if the imported module is not a file you explicitly wanted mypy to check.

For example, suppose we have two modules ``mycode.foo`` and ``mycode.bar``:
the former has type hints and the latter does not. We run
:option:`mypy -m mycode.foo <mypy -m>` and mypy discovers that ``mycode.foo`` imports
``mycode.bar``.

How do we want mypy to type check ``mycode.bar``? Mypy's behaviour here is
configurable -- although we **strongly recommend** using the default --
by using the :option:`--follow-imports <mypy --follow-imports>` flag. This flag
accepts one of four string values:

-   ``normal`` (the default, recommended) follows all imports normally and
    type checks all top level code (as well as the bodies of all
    functions and methods with at least one type annotation in
    the signature).

-   ``silent`` behaves in the same way as ``normal`` but will
    additionally *suppress* any error messages.

-   ``skip`` will *not* follow imports and instead will silently
    replace the module (and *anything imported from it*) with an
    object of type ``Any``.

-   ``error`` behaves in the same way as ``skip`` but is not quite as
    silent -- it will flag the import as an error, like this::

        main.py:1: note: Import of "mycode.bar" ignored
        main.py:1: note: (Using --follow-imports=error, module not passed on command line)

If you are starting a new codebase and plan on using type hints from
the start, we **recommend** you use either :option:`--follow-imports=normal <mypy --follow-imports>`
(the default) or :option:`--follow-imports=error <mypy --follow-imports>`. Either option will help
make sure you are not skipping checking any part of your codebase by
accident.

If you are planning on adding type hints to a large, existing code base,
we recommend you start by trying to make your entire codebase (including
files that do not use type hints) pass under :option:`--follow-imports=normal <mypy --follow-imports>`.
This is usually not too difficult to do: mypy is designed to report as
few error messages as possible when it is looking at unannotated code.

Only if doing this is intractable, try passing mypy just the files
you want to type check and using :option:`--follow-imports=silent <mypy --follow-imports>`.
Even if mypy is unable to perfectly type check a file, it can still glean some
useful information by parsing it (for example, understanding what methods
a given object has). See :ref:`existing-code` for more recommendations.

Adjusting import following behaviour is often most useful when restricted to
specific modules. This can be accomplished by setting a per-module
:confval:`follow_imports` config option.

.. warning::

    We do not recommend using ``follow_imports=skip`` unless you're really sure
    you know what you are doing. This option greatly restricts the analysis mypy
    can perform and you will lose a lot of the benefits of type checking.

    This is especially true at the global level. Setting a per-module
    ``follow_imports=skip`` for a specific problematic module can be
    useful without causing too much harm.

.. note::

    If you're looking to resolve import errors related to libraries, try following
    the advice in :ref:`fix-missing-imports` before messing with ``follow_imports``.
````

## File: docs/source/runtime_troubles.rst
````
.. _runtime_troubles:

Annotation issues at runtime
============================

Idiomatic use of type annotations can sometimes run up against what a given
version of Python considers legal code. This section describes these scenarios
and explains how to get your code running again. Generally speaking, we have
three tools at our disposal:

* Use of string literal types or type comments
* Use of ``typing.TYPE_CHECKING``
* Use of ``from __future__ import annotations`` (:pep:`563`)

We provide a description of these before moving onto discussion of specific
problems you may encounter.

.. _string-literal-types:

String literal types and type comments
--------------------------------------

Mypy lets you add type annotations using the (now deprecated) ``# type:``
type comment syntax. These were required with Python versions older than 3.6,
since they didn't support type annotations on variables. Example:

.. code-block:: python

   a = 1  # type: int

   def f(x):  # type: (int) -> int
       return x + 1

   # Alternative type comment syntax for functions with many arguments
   def send_email(
        address,     # type: Union[str, List[str]]
        sender,      # type: str
        cc,          # type: Optional[List[str]]
        subject='',
        body=None    # type: List[str]
   ):
       # type: (...) -> bool

Type comments can't cause runtime errors because comments are not evaluated by
Python.

In a similar way, using string literal types sidesteps the problem of
annotations that would cause runtime errors.

Any type can be entered as a string literal, and you can combine
string-literal types with non-string-literal types freely:

.. code-block:: python

   def f(a: list['A']) -> None: ...  # OK, prevents NameError since A is defined later
   def g(n: 'int') -> None: ...      # Also OK, though not useful

   class A: pass

String literal types are never needed in ``# type:`` comments and :ref:`stub files <stub-files>`.

String literal types must be defined (or imported) later *in the same module*.
They cannot be used to leave cross-module references unresolved.  (For dealing
with import cycles, see :ref:`import-cycles`.)

.. _future-annotations:

Future annotations import (PEP 563)
-----------------------------------

Many of the issues described here are caused by Python trying to evaluate
annotations. Future Python versions (potentially Python 3.14) will by default no
longer attempt to evaluate function and variable annotations. This behaviour is
made available in Python 3.7 and later through the use of
``from __future__ import annotations``.

This can be thought of as automatic string literal-ification of all function and
variable annotations. Note that function and variable annotations are still
required to be valid Python syntax. For more details, see :pep:`563`.

.. note::

    Even with the ``__future__`` import, there are some scenarios that could
    still require string literals or result in errors, typically involving use
    of forward references or generics in:

    * :ref:`type aliases <type-aliases>` not defined using the ``type`` statement;
    * :ref:`type narrowing <type-narrowing>`;
    * type definitions (see :py:class:`~typing.TypeVar`, :py:class:`~typing.NewType`, :py:class:`~typing.NamedTuple`);
    * base classes.

    .. code-block:: python

        # base class example
        from __future__ import annotations

        class A(tuple['B', 'C']): ... # String literal types needed here
        class B: ...
        class C: ...

.. warning::

    Some libraries may have use cases for dynamic evaluation of annotations, for
    instance, through use of ``typing.get_type_hints`` or ``eval``. If your
    annotation would raise an error when evaluated (say by using :pep:`604`
    syntax with Python 3.9), you may need to be careful when using such
    libraries.

.. _typing-type-checking:

typing.TYPE_CHECKING
--------------------

The :py:mod:`typing` module defines a :py:data:`~typing.TYPE_CHECKING` constant
that is ``False`` at runtime but treated as ``True`` while type checking.

Since code inside ``if TYPE_CHECKING:`` is not executed at runtime, it provides
a convenient way to tell mypy something without the code being evaluated at
runtime. This is most useful for resolving :ref:`import cycles <import-cycles>`.

.. _forward-references:

Class name forward references
-----------------------------

Python does not allow references to a class object before the class is
defined (aka forward reference). Thus this code does not work as expected:

.. code-block:: python

   def f(x: A) -> None: ...  # NameError: name "A" is not defined
   class A: ...

Starting from Python 3.7, you can add ``from __future__ import annotations`` to
resolve this, as discussed earlier:

.. code-block:: python

   from __future__ import annotations

   def f(x: A) -> None: ...  # OK
   class A: ...

For Python 3.6 and below, you can enter the type as a string literal or type comment:

.. code-block:: python

   def f(x: 'A') -> None: ...  # OK

   # Also OK
   def g(x):  # type: (A) -> None
       ...

   class A: ...

Of course, instead of using future annotations import or string literal types,
you could move the function definition after the class definition. This is not
always desirable or even possible, though.

.. _import-cycles:

Import cycles
-------------

An import cycle occurs where module A imports module B and module B
imports module A (perhaps indirectly, e.g. ``A -> B -> C -> A``).
Sometimes in order to add type annotations you have to add extra
imports to a module and those imports cause cycles that didn't exist
before. This can lead to errors at runtime like:

.. code-block:: text

   ImportError: cannot import name 'b' from partially initialized module 'A' (most likely due to a circular import)

If those cycles do become a problem when running your program, there's a trick:
if the import is only needed for type annotations and you're using a) the
:ref:`future annotations import<future-annotations>`, or b) string literals or type
comments for the relevant annotations, you can write the imports inside ``if
TYPE_CHECKING:`` so that they are not executed at runtime. Example:

File ``foo.py``:

.. code-block:: python

   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       import bar

   def listify(arg: 'bar.BarClass') -> 'list[bar.BarClass]':
       return [arg]

File ``bar.py``:

.. code-block:: python

   from foo import listify

   class BarClass:
       def listifyme(self) -> 'list[BarClass]':
           return listify(self)

.. _not-generic-runtime:

Using classes that are generic in stubs but not at runtime
----------------------------------------------------------

Some classes are declared as :ref:`generic<generic-classes>` in stubs, but not
at runtime.

In Python 3.8 and earlier, there are several examples within the standard library,
for instance, :py:class:`os.PathLike` and :py:class:`queue.Queue`. Subscripting
such a class will result in a runtime error:

.. code-block:: python

   from queue import Queue

   class Tasks(Queue[str]):  # TypeError: 'type' object is not subscriptable
       ...

   results: Queue[int] = Queue()  # TypeError: 'type' object is not subscriptable

To avoid errors from use of these generics in annotations, just use the
:ref:`future annotations import<future-annotations>` (or string literals or type
comments for Python 3.6 and below).

To avoid errors when inheriting from these classes, things are a little more
complicated and you need to use :ref:`typing.TYPE_CHECKING
<typing-type-checking>`:

.. code-block:: python

   from typing import TYPE_CHECKING
   from queue import Queue

   if TYPE_CHECKING:
       BaseQueue = Queue[str]  # this is only processed by mypy
   else:
       BaseQueue = Queue  # this is not seen by mypy but will be executed at runtime

   class Tasks(BaseQueue):  # OK
       ...

   task_queue: Tasks
   reveal_type(task_queue.get())  # Reveals str

If your subclass is also generic, you can use the following (using the
legacy syntax for generic classes):

.. code-block:: python

   from typing import TYPE_CHECKING, TypeVar, Generic
   from queue import Queue

   _T = TypeVar("_T")
   if TYPE_CHECKING:
       class _MyQueueBase(Queue[_T]): pass
   else:
       class _MyQueueBase(Generic[_T], Queue): pass

   class MyQueue(_MyQueueBase[_T]): pass

   task_queue: MyQueue[str]
   reveal_type(task_queue.get())  # Reveals str

In Python 3.9 and later, we can just inherit directly from ``Queue[str]`` or ``Queue[T]``
since its :py:class:`queue.Queue` implements :py:meth:`~object.__class_getitem__`, so
the class object can be subscripted at runtime. You may still encounter issues (even if
you use a recent Python version) when subclassing generic classes defined in third-party
libraries if types are generic only in stubs.

Using types defined in stubs but not at runtime
-----------------------------------------------

Sometimes stubs that you're using may define types you wish to reuse that do
not exist at runtime. Importing these types naively will cause your code to fail
at runtime with ``ImportError`` or ``ModuleNotFoundError``. Similar to previous
sections, these can be dealt with by using :ref:`typing.TYPE_CHECKING
<typing-type-checking>`:

.. code-block:: python

   from __future__ import annotations
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from _typeshed import SupportsRichComparison

    def f(x: SupportsRichComparison) -> None

The ``from __future__ import annotations`` is required to avoid
a ``NameError`` when using the imported symbol.
For more information and caveats, see the section on
:ref:`future annotations <future-annotations>`.

.. _generic-builtins:

Using generic builtins
----------------------

Starting with Python 3.9 (:pep:`585`), the type objects of many collections in
the standard library support subscription at runtime. This means that you no
longer have to import the equivalents from :py:mod:`typing`; you can simply use
the built-in collections or those from :py:mod:`collections.abc`:

.. code-block:: python

   from collections.abc import Sequence
   x: list[str]
   y: dict[int, str]
   z: Sequence[str] = x

There is limited support for using this syntax in Python 3.7 and later as well:
if you use ``from __future__ import annotations``, mypy will understand this
syntax in annotations. However, since this will not be supported by the Python
interpreter at runtime, make sure you're aware of the caveats mentioned in the
notes at :ref:`future annotations import<future-annotations>`.

Using X | Y syntax for Unions
-----------------------------

Starting with Python 3.10 (:pep:`604`), you can spell union types as
``x: int | str``, instead of ``x: typing.Union[int, str]``.

There is limited support for using this syntax in Python 3.7 and later as well:
if you use ``from __future__ import annotations``, mypy will understand this
syntax in annotations, string literal types, type comments and stub files.
However, since this will not be supported by the Python interpreter at runtime
(if evaluated, ``int | str`` will raise ``TypeError: unsupported operand type(s)
for |: 'type' and 'type'``), make sure you're aware of the caveats mentioned in
the notes at :ref:`future annotations import<future-annotations>`.

Using new additions to the typing module
----------------------------------------

You may find yourself wanting to use features added to the :py:mod:`typing`
module in earlier versions of Python than the addition.

The easiest way to do this is to install and use the ``typing_extensions``
package from PyPI for the relevant imports, for example:

.. code-block:: python

   from typing_extensions import TypeIs

If you don't want to rely on ``typing_extensions`` being installed on newer
Pythons, you could alternatively use:

.. code-block:: python

   import sys
   if sys.version_info >= (3, 13):
       from typing import TypeIs
   else:
       from typing_extensions import TypeIs

This plays nicely well with following :pep:`508` dependency specification:
``typing_extensions; python_version<"3.13"``
````

## File: docs/source/stubgen.rst
````
.. _stubgen:

.. program:: stubgen

Automatic stub generation (stubgen)
===================================

A stub file (see :pep:`484`) contains only type hints for the public
interface of a module, with empty function bodies. Mypy can use a stub
file instead of the real implementation to provide type information
for the module. They are useful for third-party modules whose authors
have not yet added type hints (and when no stubs are available in
typeshed) and C extension modules (which mypy can't directly process).

Mypy includes the ``stubgen`` tool that can automatically generate
stub files (``.pyi`` files) for Python modules and C extension modules.
For example, consider this source file:

.. code-block:: python

   from other_module import dynamic

   BORDER_WIDTH = 15

   class Window:
       parent = dynamic()
       def __init__(self, width, height):
           self.width = width
           self.height = height

   def create_empty() -> Window:
       return Window(0, 0)

Stubgen can generate this stub file based on the above file:

.. code-block:: python

   from typing import Any

   BORDER_WIDTH: int = ...

   class Window:
       parent: Any = ...
       width: Any = ...
       height: Any = ...
       def __init__(self, width, height) -> None: ...

   def create_empty() -> Window: ...

Stubgen generates *draft* stubs. The auto-generated stub files often
require some manual updates, and most types will default to ``Any``.
The stubs will be much more useful if you add more precise type annotations,
at least for the most commonly used functionality.

The rest of this section documents the command line interface of stubgen.
Run :option:`stubgen --help` for a quick summary of options.

.. note::

  The command-line flags may change between releases.

Specifying what to stub
***********************

You can give stubgen paths of the source files for which you want to
generate stubs::

    $ stubgen foo.py bar.py

This generates stubs ``out/foo.pyi`` and ``out/bar.pyi``. The default
output directory ``out`` can be overridden with :option:`-o DIR <-o>`.

You can also pass directories, and stubgen will recursively search
them for any ``.py`` files and generate stubs for all of them::

    $ stubgen my_pkg_dir

Alternatively, you can give module or package names using the
:option:`-m` or :option:`-p` options::

    $ stubgen -m foo -m bar -p my_pkg_dir

Details of the options:

.. option:: -m MODULE, --module MODULE

    Generate a stub file for the given module. This flag may be repeated
    multiple times.

    Stubgen *will not* recursively generate stubs for any submodules of
    the provided module.

.. option:: -p PACKAGE, --package PACKAGE

    Generate stubs for the given package. This flag maybe repeated
    multiple times.

    Stubgen *will* recursively generate stubs for all submodules of
    the provided package. This flag is identical to :option:`--module` apart from
    this behavior.

.. note::

   You can't mix paths and :option:`-m`/:option:`-p` options in the same stubgen
   invocation.

Stubgen applies heuristics to avoid generating stubs for submodules
that include tests or vendored third-party packages.

Specifying how to generate stubs
********************************

By default stubgen will try to import the target modules and packages.
This allows stubgen to use runtime introspection to generate stubs for C
extension modules and to improve the quality of the generated
stubs. By default, stubgen will also use mypy to perform light-weight
semantic analysis of any Python modules. Use the following flags to
alter the default behavior:

.. option:: --no-import

    Don't try to import modules. Instead only use mypy's normal search mechanism to find
    sources. This does not support C extension modules. This flag also disables
    runtime introspection functionality, which mypy uses to find the value of
    ``__all__``. As result the set of exported imported names in stubs may be
    incomplete. This flag is generally only useful when importing a module causes
    unwanted side effects, such as the running of tests. Stubgen tries to skip test
    modules even without this option, but this does not always work.

.. option:: --no-analysis

    Don't perform semantic analysis of source files. This may generate
    worse stubs -- in particular, some module, class, and function aliases may
    be represented as variables with the ``Any`` type. This is generally only
    useful if semantic analysis causes a critical mypy error.  Does not apply to
    C extension modules.  Incompatible with :option:`--inspect-mode`.

.. option:: --inspect-mode

    Import and inspect modules instead of parsing source code. This is the default
    behavior for C modules and pyc-only packages.  The flag is useful to force
    inspection for pure Python modules that make use of dynamically generated
    members that would otherwise be omitted when using the default behavior of
    code parsing.  Implies :option:`--no-analysis` as analysis requires source
    code.

.. option:: --doc-dir PATH

    Try to infer better signatures by parsing .rst documentation in ``PATH``.
    This may result in better stubs, but currently it only works for C extension
    modules.

Additional flags
****************

.. option:: -h, --help

    Show help message and exit.

.. option:: --ignore-errors

    If an exception was raised during stub generation, continue to process any
    remaining modules instead of immediately failing with an error.

.. option:: --include-private

    Include definitions that are considered private in stubs (with names such
    as ``_foo`` with single leading underscore and no trailing underscores).

.. option:: --export-less

    Don't export all names imported from other modules within the same package.
    Instead, only export imported names that are not referenced in the module
    that contains the import.

.. option:: --include-docstrings

    Include docstrings in stubs. This will add docstrings to Python function and
    classes stubs and to C extension function stubs.

.. option:: --search-path PATH

    Specify module search directories, separated by colons (only used if
    :option:`--no-import` is given).

.. option:: -o PATH, --output PATH

    Change the output directory. By default the stubs are written in the
    ``./out`` directory. The output directory will be created if it doesn't
    exist. Existing stubs in the output directory will be overwritten without
    warning.

.. option:: -v, --verbose

    Produce more verbose output.

.. option:: -q, --quiet

    Produce less verbose output.
````

## File: docs/source/stubs.rst
````
.. _stub-files:

Stub files
==========

A *stub file* is a file containing a skeleton of the public interface
of that Python module, including classes, variables, functions -- and
most importantly, their types.

Mypy uses stub files stored in the
`typeshed <https://github.com/python/typeshed>`_ repository to determine
the types of standard library and third-party library functions, classes,
and other definitions. You can also create your own stubs that will be
used to type check your code.

Creating a stub
***************

Here is an overview of how to create a stub file:

* Write a stub file for the library (or an arbitrary module) and store it as
  a ``.pyi`` file in the same directory as the library module.
* Alternatively, put your stubs (``.pyi`` files) in a directory
  reserved for stubs (e.g., :file:`myproject/stubs`). In this case you
  have to set the environment variable ``MYPYPATH`` to refer to the
  directory.  For example::

    $ export MYPYPATH=~/work/myproject/stubs

Use the normal Python file name conventions for modules, e.g. :file:`csv.pyi`
for module ``csv``. Use a subdirectory with :file:`__init__.pyi` for packages. Note
that :pep:`561` stub-only packages must be installed, and may not be pointed
at through the ``MYPYPATH`` (see :ref:`PEP 561 support <installed-packages>`).

If a directory contains both a ``.py`` and a ``.pyi`` file for the
same module, the ``.pyi`` file takes precedence. This way you can
easily add annotations for a module even if you don't want to modify
the source code. This can be useful, for example, if you use 3rd party
open source libraries in your program (and there are no stubs in
typeshed yet).

That's it!

Now you can access the module in mypy programs and type check
code that uses the library. If you write a stub for a library module,
consider making it available for other programmers that use mypy
by contributing it back to the typeshed repo.

Mypy also ships with two tools for making it easier to create and maintain
stubs: :ref:`stubgen` and :ref:`stubtest`.

The following sections explain the kinds of type annotations you can use
in your programs and stub files.

.. note::

   You may be tempted to point ``MYPYPATH`` to the standard library or
   to the :file:`site-packages` directory where your 3rd party packages
   are installed. This is almost always a bad idea -- you will likely
   get tons of error messages about code you didn't write and that
   mypy can't analyze all that well yet, and in the worst case
   scenario mypy may crash due to some construct in a 3rd party
   package that it didn't expect.

Stub file syntax
****************

Stub files are written in normal Python syntax, but generally
leaving out runtime logic like variable initializers, function bodies,
and default arguments.

If it is not possible to completely leave out some piece of runtime
logic, the recommended convention is to replace or elide them with ellipsis
expressions (``...``). Each ellipsis below is literally written in the
stub file as three dots:

.. code-block:: python

    # Variables with annotations do not need to be assigned a value.
    # So by convention, we omit them in the stub file.
    x: int

    # Function bodies cannot be completely removed. By convention,
    # we replace them with `...` instead of the `pass` statement.
    def func_1(code: str) -> int: ...

    # We can do the same with default arguments.
    def func_2(a: int, b: int = ...) -> int: ...

.. note::

    The ellipsis ``...`` is also used with a different meaning in
    :ref:`callable types <callable-types>` and :ref:`tuple types
    <tuple-types>`.

Using stub file syntax at runtime
*********************************

You may also occasionally need to elide actual logic in regular
Python code -- for example, when writing methods in
:ref:`overload variants <function-overloading>` or
:ref:`custom protocols <protocol-types>`.

The recommended style is to use ellipses to do so, just like in
stub files. It is also considered stylistically acceptable to
throw a :py:exc:`NotImplementedError` in cases where the user of the
code may accidentally call functions with no actual logic.

You can also elide default arguments as long as the function body
also contains no runtime logic: the function body only contains
a single ellipsis, the pass statement, or a ``raise NotImplementedError()``.
It is also acceptable for the function body to contain a docstring.
For example:

.. code-block:: python

    from typing import Protocol

    class Resource(Protocol):
        def ok_1(self, foo: list[str] = ...) -> None: ...

        def ok_2(self, foo: list[str] = ...) -> None:
            raise NotImplementedError()

        def ok_3(self, foo: list[str] = ...) -> None:
            """Some docstring"""
            pass

        # Error: Incompatible default for argument "foo" (default has
        # type "ellipsis", argument has type "list[str]")
        def not_ok(self, foo: list[str] = ...) -> None:
            print(foo)
````

## File: docs/source/stubtest.rst
````
.. _stubtest:

.. program:: stubtest

Automatic stub testing (stubtest)
=================================

Stub files are files containing type annotations. See
`PEP 484 <https://www.python.org/dev/peps/pep-0484/#stub-files>`_
for more motivation and details.

A common problem with stub files is that they tend to diverge from the
actual implementation. Mypy includes the ``stubtest`` tool that can
automatically check for discrepancies between the stubs and the
implementation at runtime.

What stubtest does and does not do
**********************************

Stubtest will import your code and introspect your code objects at runtime, for
example, by using the capabilities of the :py:mod:`inspect` module. Stubtest
will then analyse the stub files, and compare the two, pointing out things that
differ between stubs and the implementation at runtime.

It's important to be aware of the limitations of this comparison. Stubtest will
not make any attempt to statically analyse your actual code and relies only on
dynamic runtime introspection (in particular, this approach means stubtest works
well with extension modules). However, this means that stubtest has limited
visibility; for instance, it cannot tell if a return type of a function is
accurately typed in the stubs.

For clarity, here are some additional things stubtest can't do:

* Type check your code -- use ``mypy`` instead
* Generate stubs -- use ``stubgen`` or ``pyright --createstub`` instead
* Generate stubs based on running your application or test suite -- use ``monkeytype`` instead
* Apply stubs to code to produce inline types -- use ``retype`` or ``libcst`` instead

In summary, stubtest works very well for ensuring basic consistency between
stubs and implementation or to check for stub completeness. It's used to
test Python's official collection of library stubs,
`typeshed <https://github.com/python/typeshed>`_.

.. warning::

    stubtest will import and execute Python code from the packages it checks.

Example
*******

Here's a quick example of what stubtest can do:

.. code-block:: shell

    $ python3 -m pip install mypy

    $ cat library.py
    x = "hello, stubtest"

    def foo(x=None):
        print(x)

    $ cat library.pyi
    x: int

    def foo(x: int) -> None: ...

    $ python3 -m mypy.stubtest library
    error: library.foo is inconsistent, runtime argument "x" has a default value but stub argument does not
    Stub: at line 3
    def (x: builtins.int)
    Runtime: in file ~/library.py:3
    def (x=None)

    error: library.x variable differs from runtime type Literal['hello, stubtest']
    Stub: at line 1
    builtins.int
    Runtime:
    'hello, stubtest'


Usage
*****

Running stubtest can be as simple as ``stubtest module_to_check``.
Run :option:`stubtest --help` for a quick summary of options.

Stubtest must be able to import the code to be checked, so make sure that mypy
is installed in the same environment as the library to be tested. In some
cases, setting ``PYTHONPATH`` can help stubtest find the code to import.

Similarly, stubtest must be able to find the stubs to be checked. Stubtest
respects the ``MYPYPATH`` environment variable -- consider using this if you
receive a complaint along the lines of "failed to find stubs".

Note that stubtest requires mypy to be able to analyse stubs. If mypy is unable
to analyse stubs, you may get an error on the lines of "not checking stubs due
to mypy build errors". In this case, you will need to mitigate those errors
before stubtest will run. Despite potential overlap in errors here, stubtest is
not intended as a substitute for running mypy directly.

If you wish to ignore some of stubtest's complaints, stubtest supports a
pretty handy allowlist system.

The rest of this section documents the command line interface of stubtest.

.. option:: --concise

    Makes stubtest's output more concise, one line per error

.. option:: --ignore-missing-stub

    Ignore errors for stub missing things that are present at runtime

.. option:: --ignore-positional-only

    Ignore errors for whether an argument should or shouldn't be positional-only

.. option:: --allowlist FILE

    Use file as an allowlist. Can be passed multiple times to combine multiple
    allowlists. Allowlists can be created with --generate-allowlist. Allowlists
    support regular expressions.

    The presence of an entry in the allowlist means stubtest will not generate
    any errors for the corresponding definition.

.. option:: --generate-allowlist

    Print an allowlist (to stdout) to be used with --allowlist

    When introducing stubtest to an existing project, this is an easy way to
    silence all existing errors.

.. option:: --ignore-unused-allowlist

    Ignore unused allowlist entries

    Without this option enabled, the default is for stubtest to complain if an
    allowlist entry is not necessary for stubtest to pass successfully.

    Note if an allowlist entry is a regex that matches the empty string,
    stubtest will never consider it unused. For example, to get
    `--ignore-unused-allowlist` behaviour for a single allowlist entry like
    ``foo.bar`` you could add an allowlist entry ``(foo\.bar)?``.
    This can be useful when an error only occurs on a specific platform.

.. option:: --mypy-config-file FILE

    Use specified mypy config file to determine mypy plugins and mypy path

.. option:: --custom-typeshed-dir DIR

    Use the custom typeshed in DIR

.. option:: --check-typeshed

    Check all stdlib modules in typeshed

.. option:: --help

    Show a help message :-)
````

## File: docs/source/supported_python_features.rst
````
Supported Python features
=========================

A list of unsupported Python features is maintained in the mypy wiki:

- `Unsupported Python features <https://github.com/python/mypy/wiki/Unsupported-Python-Features>`_

Runtime definition of methods and functions
*******************************************

By default, mypy will complain if you add a function to a class
or module outside its definition -- but only if this is visible to the
type checker. This only affects static checking, as mypy performs no
additional type checking at runtime. You can easily work around
this. For example, you can use dynamically typed code or values with
``Any`` types, or you can use :py:func:`setattr` or other introspection
features. However, you need to be careful if you decide to do this. If
used indiscriminately, you may have difficulty using static typing
effectively, since the type checker cannot see functions defined at
runtime.
````

## File: docs/source/type_inference_and_annotations.rst
````
.. _type-inference-and-annotations:

Type inference and type annotations
===================================

Type inference
**************

For most variables, if you do not explicitly specify its type, mypy will
infer the correct type based on what is initially assigned to the variable.

.. code-block:: python

    # Mypy will infer the type of these variables, despite no annotations
    i = 1
    reveal_type(i)  # Revealed type is "builtins.int"
    l = [1, 2]
    reveal_type(l)  # Revealed type is "builtins.list[builtins.int]"


.. note::

    Note that mypy will not use type inference in dynamically typed functions
    (those without a function type annotation) — every local variable type
    defaults to ``Any`` in such functions. For more details, see :ref:`dynamic-typing`.

    .. code-block:: python

        def untyped_function():
            i = 1
            reveal_type(i) # Revealed type is "Any"
                           # 'reveal_type' always outputs 'Any' in unchecked functions

.. _explicit-var-types:

Explicit types for variables
****************************

You can override the inferred type of a variable by using a
variable type annotation:

.. code-block:: python

   x: int | str = 1

Without the type annotation, the type of ``x`` would be just ``int``. We
use an annotation to give it a more general type ``int | str`` (this
type means that the value can be either an ``int`` or a ``str``).

The best way to think about this is that the type annotation sets the type of
the variable, not the type of the expression. For instance, mypy will complain
about the following code:

.. code-block:: python

   x: int | str = 1.1  # error: Incompatible types in assignment
                       # (expression has type "float", variable has type "int | str")

.. note::

   To explicitly override the type of an expression you can use
   :py:func:`cast(\<type\>, \<expression\>) <typing.cast>`.
   See :ref:`casts` for details.

Note that you can explicitly declare the type of a variable without
giving it an initial value:

.. code-block:: python

   # We only unpack two values, so there's no right-hand side value
   # for mypy to infer the type of "cs" from:
   a, b, *cs = 1, 2  # error: Need type annotation for "cs"

   rs: list[int]  # no assignment!
   p, q, *rs = 1, 2  # OK

Explicit types for collections
******************************

The type checker cannot always infer the type of a list or a
dictionary. This often arises when creating an empty list or
dictionary and assigning it to a new variable that doesn't have an explicit
variable type. Here is an example where mypy can't infer the type
without some help:

.. code-block:: python

   l = []  # Error: Need type annotation for "l"

In these cases you can give the type explicitly using a type annotation:

.. code-block:: python

   l: list[int] = []       # Create empty list of int
   d: dict[str, int] = {}  # Create empty dictionary (str -> int)

.. note::

   Using type arguments (e.g. ``list[int]``) on builtin collections like
   :py:class:`list`,  :py:class:`dict`, :py:class:`tuple`, and  :py:class:`set`
   only works in Python 3.9 and later. For Python 3.8 and earlier, you must use
   :py:class:`~typing.List` (e.g. ``List[int]``), :py:class:`~typing.Dict`, and
   so on.


Compatibility of container types
********************************

A quick note: container types can sometimes be unintuitive. We'll discuss this
more in :ref:`variance`. For example, the following program generates a mypy error,
because mypy treats ``list[int]`` as incompatible with ``list[object]``:

.. code-block:: python

   def f(l: list[object], k: list[int]) -> None:
       l = k  # error: Incompatible types in assignment

The reason why the above assignment is disallowed is that allowing the
assignment could result in non-int values stored in a list of ``int``:

.. code-block:: python

   def f(l: list[object], k: list[int]) -> None:
       l = k
       l.append('x')
       print(k[-1])  # Ouch; a string in list[int]

Other container types like :py:class:`dict` and :py:class:`set` behave similarly.

You can still run the above program; it prints ``x``. This illustrates the fact
that static types do not affect the runtime behavior of programs. You can run
programs with type check failures, which is often very handy when performing a
large refactoring. Thus you can always 'work around' the type system, and it
doesn't really limit what you can do in your program.

Context in type inference
*************************

Type inference is *bidirectional* and takes context into account.

Mypy will take into account the type of the variable on the left-hand side
of an assignment when inferring the type of the expression on the right-hand
side. For example, the following will type check:

.. code-block:: python

   def f(l: list[object]) -> None:
       l = [1, 2]  # Infer type list[object] for [1, 2], not list[int]


The value expression ``[1, 2]`` is type checked with the additional
context that it is being assigned to a variable of type ``list[object]``.
This is used to infer the type of the *expression* as ``list[object]``.

Declared argument types are also used for type context. In this program
mypy knows that the empty list ``[]`` should have type ``list[int]`` based
on the declared type of ``arg`` in ``foo``:

.. code-block:: python

    def foo(arg: list[int]) -> None:
        print('Items:', ''.join(str(a) for a in arg))

    foo([])  # OK

However, context only works within a single statement. Here mypy requires
an annotation for the empty list, since the context would only be available
in the following statement:

.. code-block:: python

    def foo(arg: list[int]) -> None:
        print('Items:', ', '.join(arg))

    a = []  # Error: Need type annotation for "a"
    foo(a)

Working around the issue is easy by adding a type annotation:

.. code-block:: Python

    ...
    a: list[int] = []  # OK
    foo(a)

.. _silencing-type-errors:

Silencing type errors
*********************

You might want to disable type checking on specific lines, or within specific
files in your codebase. To do that, you can use a ``# type: ignore`` comment.

For example, say in its latest update, the web framework you use can now take an
integer argument to ``run()``, which starts it on localhost on that port.
Like so:

.. code-block:: python

    # Starting app on http://localhost:8000
    app.run(8000)

However, the devs forgot to update their type annotations for
``run``, so mypy still thinks ``run`` only expects ``str`` types.
This would give you the following error:

.. code-block:: text

    error: Argument 1 to "run" of "A" has incompatible type "int"; expected "str"

If you cannot directly fix the web framework yourself, you can temporarily
disable type checking on that line, by adding a ``# type: ignore``:

.. code-block:: python

    # Starting app on http://localhost:8000
    app.run(8000)  # type: ignore

This will suppress any mypy errors that would have raised on that specific line.

You should probably add some more information on the ``# type: ignore`` comment,
to explain why the ignore was added in the first place. This could be a link to
an issue on the repository responsible for the type stubs, or it could be a
short explanation of the bug. To do that, use this format:

.. code-block:: python

    # Starting app on http://localhost:8000
    app.run(8000)  # type: ignore  # `run()` in v2.0 accepts an `int`, as a port

Type ignore error codes
-----------------------

By default, mypy displays an error code for each error:

.. code-block:: text

   error: "str" has no attribute "trim"  [attr-defined]


It is possible to add a specific error-code in your ignore comment (e.g.
``# type: ignore[attr-defined]``) to clarify what's being silenced. You can
find more information about error codes :ref:`here <silence-error-codes>`.

Other ways to silence errors
----------------------------

You can get mypy to silence errors about a specific variable by dynamically
typing it with ``Any``. See :ref:`dynamic-typing` for more information.

.. code-block:: python

    from typing import Any

    def f(x: Any, y: str) -> None:
        x = 'hello'
        x += 1  # OK

You can ignore all mypy errors in a file by adding a
``# mypy: ignore-errors`` at the top of the file:

.. code-block:: python

    # mypy: ignore-errors
    # This is a test file, skipping type checking in it.
    import unittest
    ...

You can also specify per-module configuration options in your :ref:`config-file`.
For example:

.. code-block:: ini

    # Don't report errors in the 'package_to_fix_later' package
    [mypy-package_to_fix_later.*]
    ignore_errors = True

    # Disable specific error codes in the 'tests' package
    # Also don't require type annotations
    [mypy-tests.*]
    disable_error_code = var-annotated, has-type
    allow_untyped_defs = True

    # Silence import errors from the 'library_missing_types' package
    [mypy-library_missing_types.*]
    ignore_missing_imports = True

Finally, adding a ``@typing.no_type_check`` decorator to a class, method or
function causes mypy to avoid type checking that class, method or function
and to treat it as not having any type annotations.

.. code-block:: python

    @typing.no_type_check
    def foo() -> str:
       return 12345  # No error!
````

## File: docs/source/type_narrowing.rst
````
.. _type-narrowing:

Type narrowing
==============

This section is dedicated to several type narrowing
techniques which are supported by mypy.

Type narrowing is when you convince a type checker that a broader type is actually more specific, for instance, that an object of type ``Shape`` is actually of the narrower type ``Square``.

The following type narrowing techniques are available:

- :ref:`type-narrowing-expressions`
- :ref:`casts`
- :ref:`type-guards`
- :ref:`typeis`


.. _type-narrowing-expressions:

Type narrowing expressions
--------------------------

The simplest way to narrow a type is to use one of the supported expressions:

- :py:func:`isinstance` like in :code:`isinstance(obj, float)` will narrow ``obj`` to have ``float`` type
- :py:func:`issubclass` like in :code:`issubclass(cls, MyClass)` will narrow ``cls`` to be ``Type[MyClass]``
- :py:class:`type` like in :code:`type(obj) is int` will narrow ``obj`` to have ``int`` type
- :py:func:`callable` like in :code:`callable(obj)` will narrow object to callable type
- :code:`obj is not None` will narrow object to its :ref:`non-optional form <strict_optional>`

Type narrowing is contextual. For example, based on the condition, mypy will narrow an expression only within an ``if`` branch:

.. code-block:: python

  def function(arg: object):
      if isinstance(arg, int):
          # Type is narrowed within the ``if`` branch only
          reveal_type(arg)  # Revealed type: "builtins.int"
      elif isinstance(arg, str) or isinstance(arg, bool):
          # Type is narrowed differently within this ``elif`` branch:
          reveal_type(arg)  # Revealed type: "builtins.str | builtins.bool"

          # Subsequent narrowing operations will narrow the type further
          if isinstance(arg, bool):
              reveal_type(arg)  # Revealed type: "builtins.bool"

      # Back outside of the ``if`` statement, the type isn't narrowed:
      reveal_type(arg)  # Revealed type: "builtins.object"

Mypy understands the implications ``return`` or exception raising can have
for what type an object could be:

.. code-block:: python

  def function(arg: int | str):
      if isinstance(arg, int):
          return

      # `arg` can't be `int` at this point:
      reveal_type(arg)  # Revealed type: "builtins.str"

We can also use ``assert`` to narrow types in the same context:

.. code-block:: python

  def function(arg: Any):
      assert isinstance(arg, int)
      reveal_type(arg)  # Revealed type: "builtins.int"

.. note::

  With :option:`--warn-unreachable <mypy --warn-unreachable>`
  narrowing types to some impossible state will be treated as an error.

  .. code-block:: python

     def function(arg: int):
         # error: Subclass of "int" and "str" cannot exist:
         # would have incompatible method signatures
         assert isinstance(arg, str)

         # error: Statement is unreachable
         print("so mypy concludes the assert will always trigger")

  Without ``--warn-unreachable`` mypy will simply not check code it deems to be
  unreachable. See :ref:`unreachable` for more information.

  .. code-block:: python

     x: int = 1
     assert isinstance(x, str)
     reveal_type(x)  # Revealed type is "builtins.int"
     print(x + '!')  # Typechecks with `mypy`, but fails in runtime.


issubclass
~~~~~~~~~~

Mypy can also use :py:func:`issubclass`
for better type inference when working with types and metaclasses:

.. code-block:: python

   class MyCalcMeta(type):
       @classmethod
       def calc(cls) -> int:
           ...

   def f(o: object) -> None:
       t = type(o)  # We must use a variable here
       reveal_type(t)  # Revealed type is "builtins.type"

       if issubclass(t, MyCalcMeta):  # `issubclass(type(o), MyCalcMeta)` won't work
           reveal_type(t)  # Revealed type is "Type[MyCalcMeta]"
           t.calc()  # Okay

callable
~~~~~~~~

Mypy knows what types are callable and which ones are not during type checking.
So, we know what ``callable()`` will return. For example:

.. code-block:: python

  from collections.abc import Callable

  x: Callable[[], int]

  if callable(x):
      reveal_type(x)  # N: Revealed type is "def () -> builtins.int"
  else:
      ...  # Will never be executed and will raise error with `--warn-unreachable`

The ``callable`` function can even split union types into
callable and non-callable parts:

.. code-block:: python

  from collections.abc import Callable

  x: int | Callable[[], int]

  if callable(x):
      reveal_type(x)  # N: Revealed type is "def () -> builtins.int"
  else:
      reveal_type(x)  # N: Revealed type is "builtins.int"

.. _casts:

Casts
-----

Mypy supports type casts that are usually used to coerce a statically
typed value to a subtype. Unlike languages such as Java or C#,
however, mypy casts are only used as hints for the type checker, and they
don't perform a runtime type check. Use the function :py:func:`~typing.cast`
to perform a cast:

.. code-block:: python

   from typing import cast

   o: object = [1]
   x = cast(list[int], o)  # OK
   y = cast(list[str], o)  # OK (cast performs no actual runtime check)

To support runtime checking of casts such as the above, we'd have to check
the types of all list items, which would be very inefficient for large lists.
Casts are used to silence spurious
type checker warnings and give the type checker a little help when it can't
quite understand what is going on.

.. note::

   You can use an assertion if you want to perform an actual runtime check:

   .. code-block:: python

      def foo(o: object) -> None:
          print(o + 5)  # Error: can't add 'object' and 'int'
          assert isinstance(o, int)
          print(o + 5)  # OK: type of 'o' is 'int' here

You don't need a cast for expressions with type ``Any``, or when
assigning to a variable with type ``Any``, as was explained earlier.
You can also use ``Any`` as the cast target type -- this lets you perform
any operations on the result. For example:

.. code-block:: python

    from typing import cast, Any

    x = 1
    x.whatever()  # Type check error
    y = cast(Any, x)
    y.whatever()  # Type check OK (runtime error)


.. _type-guards:

User-Defined Type Guards
------------------------

Mypy supports User-Defined Type Guards (:pep:`647`).

A type guard is a way for programs to influence conditional
type narrowing employed by a type checker based on runtime checks.

Basically, a ``TypeGuard`` is a "smart" alias for a ``bool`` type.
Let's have a look at the regular ``bool`` example:

.. code-block:: python

  def is_str_list(val: list[object]) -> bool:
    """Determines whether all objects in the list are strings"""
    return all(isinstance(x, str) for x in val)

  def func1(val: list[object]) -> None:
      if is_str_list(val):
          reveal_type(val)  # Reveals list[object]
          print(" ".join(val)) # Error: incompatible type

The same example with ``TypeGuard``:

.. code-block:: python

  from typing import TypeGuard  # use `typing_extensions` for Python 3.9 and below

  def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
      """Determines whether all objects in the list are strings"""
      return all(isinstance(x, str) for x in val)

  def func1(val: list[object]) -> None:
      if is_str_list(val):
          reveal_type(val)  # list[str]
          print(" ".join(val)) # ok

How does it work? ``TypeGuard`` narrows the first function argument (``val``)
to the type specified as the first type parameter (``list[str]``).

.. note::

  Narrowing is
  `not strict <https://www.python.org/dev/peps/pep-0647/#enforcing-strict-narrowing>`_.
  For example, you can narrow ``str`` to ``int``:

  .. code-block:: python

    def f(value: str) -> TypeGuard[int]:
        return True

  Note: since strict narrowing is not enforced, it's easy
  to break type safety.

  However, there are many ways a determined or uninformed developer can
  subvert type safety -- most commonly by using cast or Any.
  If a Python developer takes the time to learn about and implement
  user-defined type guards within their code,
  it is safe to assume that they are interested in type safety
  and will not write their type guard functions in a way
  that will undermine type safety or produce nonsensical results.

Generic TypeGuards
~~~~~~~~~~~~~~~~~~

``TypeGuard`` can also work with generic types (Python 3.12 syntax):

.. code-block:: python

  from typing import TypeGuard  # use `typing_extensions` for `python<3.10`

  def is_two_element_tuple[T](val: tuple[T, ...]) -> TypeGuard[tuple[T, T]]:
      return len(val) == 2

  def func(names: tuple[str, ...]):
      if is_two_element_tuple(names):
          reveal_type(names)  # tuple[str, str]
      else:
          reveal_type(names)  # tuple[str, ...]

TypeGuards with parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~

Type guard functions can accept extra arguments (Python 3.12 syntax):

.. code-block:: python

  from typing import TypeGuard  # use `typing_extensions` for `python<3.10`

  def is_set_of[T](val: set[Any], type: type[T]) -> TypeGuard[set[T]]:
      return all(isinstance(x, type) for x in val)

  items: set[Any]
  if is_set_of(items, str):
      reveal_type(items)  # set[str]

TypeGuards as methods
~~~~~~~~~~~~~~~~~~~~~

A method can also serve as a ``TypeGuard``:

.. code-block:: python

  class StrValidator:
      def is_valid(self, instance: object) -> TypeGuard[str]:
          return isinstance(instance, str)

  def func(to_validate: object) -> None:
      if StrValidator().is_valid(to_validate):
          reveal_type(to_validate)  # Revealed type is "builtins.str"

.. note::

  Note, that ``TypeGuard``
  `does not narrow <https://www.python.org/dev/peps/pep-0647/#narrowing-of-implicit-self-and-cls-parameters>`_
  types of ``self`` or ``cls`` implicit arguments.

  If narrowing of ``self`` or ``cls`` is required,
  the value can be passed as an explicit argument to a type guard function:

  .. code-block:: python

    class Parent:
        def method(self) -> None:
            reveal_type(self)  # Revealed type is "Parent"
            if is_child(self):
                reveal_type(self)  # Revealed type is "Child"

    class Child(Parent):
        ...

    def is_child(instance: Parent) -> TypeGuard[Child]:
        return isinstance(instance, Child)

Assignment expressions as TypeGuards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you might need to create a new variable and narrow it
to some specific type at the same time.
This can be achieved by using ``TypeGuard`` together
with `:= operator <https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions>`_.

.. code-block:: python

  from typing import TypeGuard  # use `typing_extensions` for `python<3.10`

  def is_float(a: object) -> TypeGuard[float]:
      return isinstance(a, float)

  def main(a: object) -> None:
      if is_float(x := a):
          reveal_type(x)  # N: Revealed type is 'builtins.float'
          reveal_type(a)  # N: Revealed type is 'builtins.object'
      reveal_type(x)  # N: Revealed type is 'builtins.object'
      reveal_type(a)  # N: Revealed type is 'builtins.object'

What happens here?

1. We create a new variable ``x`` and assign a value of ``a`` to it
2. We run ``is_float()`` type guard on ``x``
3. It narrows ``x`` to be ``float`` in the ``if`` context and does not touch ``a``

.. note::

  The same will work with ``isinstance(x := a, float)`` as well.


.. _typeis:

TypeIs
------

Mypy supports TypeIs (:pep:`742`).

A `TypeIs narrowing function <https://typing.readthedocs.io/en/latest/spec/narrowing.html#typeis>`_
allows you to define custom type checks that can narrow the type of a variable
in `both the if and else <https://docs.python.org/3.13/library/typing.html#typing.TypeIs>`_
branches of a conditional, similar to how the built-in isinstance() function works.

TypeIs is new in Python 3.13 — for use in older Python versions, use the backport
from `typing_extensions <https://typing-extensions.readthedocs.io/en/latest/>`_

Consider the following example using TypeIs:

.. code-block:: python

    from typing import TypeIs

    def is_str(x: object) -> TypeIs[str]:
        return isinstance(x, str)

    def process(x: int | str) -> None:
        if is_str(x):
            reveal_type(x)  # Revealed type is 'str'
            print(x.upper())  # Valid: x is str
        else:
            reveal_type(x)  # Revealed type is 'int'
            print(x + 1)  # Valid: x is int

In this example, the function is_str is a type narrowing function
that returns TypeIs[str]. When used in an if statement, x is narrowed
to str in the if branch and to int in the else branch.

Key points:


- The function must accept at least one positional argument.

- The return type is annotated as ``TypeIs[T]``, where ``T`` is the type you
  want to narrow to.

- The function must return a ``bool`` value.

- In the ``if`` branch (when the function returns ``True``), the type of the
  argument is narrowed to the intersection of its original type and ``T``.

- In the ``else`` branch (when the function returns ``False``), the type of
  the argument is narrowed to the intersection of its original type and the
  complement of ``T``.


TypeIs vs TypeGuard
~~~~~~~~~~~~~~~~~~~

While both TypeIs and TypeGuard allow you to define custom type narrowing
functions, they differ in important ways:

- **Type narrowing behavior**: TypeIs narrows the type in both the if and else branches,
  whereas TypeGuard narrows only in the if branch.

- **Compatibility requirement**: TypeIs requires that the narrowed type T be
  compatible with the input type of the function. TypeGuard does not have this restriction.

- **Type inference**: With TypeIs, the type checker may infer a more precise type by
  combining existing type information with T.

Here's an example demonstrating the behavior with TypeGuard:

.. code-block:: python

    from typing import TypeGuard, reveal_type

    def is_str(x: object) -> TypeGuard[str]:
        return isinstance(x, str)

    def process(x: int | str) -> None:
        if is_str(x):
            reveal_type(x)  # Revealed type is "builtins.str"
            print(x.upper())  # ok: x is str
        else:
            reveal_type(x)  # Revealed type is "Union[builtins.int, builtins.str]"
            print(x + 1)  # ERROR: Unsupported operand types for + ("str" and "int")  [operator]

Generic TypeIs
~~~~~~~~~~~~~~

``TypeIs`` functions can also work with generic types:

.. code-block:: python

    from typing import TypeVar, TypeIs

    T = TypeVar('T')

    def is_two_element_tuple(val: tuple[T, ...]) -> TypeIs[tuple[T, T]]:
        return len(val) == 2

    def process(names: tuple[str, ...]) -> None:
        if is_two_element_tuple(names):
            reveal_type(names)  # Revealed type is 'tuple[str, str]'
        else:
            reveal_type(names)  # Revealed type is 'tuple[str, ...]'


TypeIs with Additional Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TypeIs functions can accept additional parameters beyond the first.
The type narrowing applies only to the first argument.

.. code-block:: python

    from typing import Any, TypeVar, reveal_type, TypeIs

    T = TypeVar('T')

    def is_instance_of(val: Any, typ: type[T]) -> TypeIs[T]:
        return isinstance(val, typ)

    def process(x: Any) -> None:
        if is_instance_of(x, int):
            reveal_type(x)  # Revealed type is 'int'
            print(x + 1)  # ok
        else:
            reveal_type(x)  # Revealed type is 'Any'

TypeIs in Methods
~~~~~~~~~~~~~~~~~

A method can also serve as a ``TypeIs`` function. Note that in instance or
class methods, the type narrowing applies to the second parameter
(after ``self`` or ``cls``).

.. code-block:: python

    class Validator:
        def is_valid(self, instance: object) -> TypeIs[str]:
            return isinstance(instance, str)

        def process(self, to_validate: object) -> None:
            if Validator().is_valid(to_validate):
                reveal_type(to_validate)  # Revealed type is 'str'
                print(to_validate.upper())  # ok: to_validate is str


Assignment Expressions with TypeIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the assignment expression operator ``:=`` with ``TypeIs`` to create a new variable and narrow its type simultaneously.

.. code-block:: python

    from typing import TypeIs, reveal_type

    def is_float(x: object) -> TypeIs[float]:
        return isinstance(x, float)

    def main(a: object) -> None:
        if is_float(x := a):
            reveal_type(x)  # Revealed type is 'float'
            # x is narrowed to float in this block
            print(x + 1.0)


Limitations
-----------

Mypy's analysis is limited to individual symbols and it will not track
relationships between symbols. For example, in the following code
it's easy to deduce that if :code:`a` is None then :code:`b` must not be,
therefore :code:`a or b` will always be an instance of :code:`C`,
but Mypy will not be able to tell that:

.. code-block:: python

    class C:
        pass

    def f(a: C | None, b: C | None) -> C:
        if a is not None or b is not None:
            return a or b  # Incompatible return value type (got "C | None", expected "C")
        return C()

Tracking these sort of cross-variable conditions in a type checker would add significant complexity
and performance overhead.

You can use an ``assert`` to convince the type checker, override it with a :ref:`cast <casts>`
or rewrite the function to be slightly more verbose:

.. code-block:: python

    def f(a: C | None, b: C | None) -> C:
        if a is not None:
            return a
        elif b is not None:
            return b
        return C()
````

## File: docs/source/typed_dict.rst
````
.. _typeddict:

TypedDict
*********

Python programs often use dictionaries with string keys to represent objects.
``TypedDict`` lets you give precise types for dictionaries that represent
objects with a fixed schema, such as ``{'id': 1, 'items': ['x']}``.

Here is a typical example:

.. code-block:: python

   movie = {'name': 'Blade Runner', 'year': 1982}

Only a fixed set of string keys is expected (``'name'`` and
``'year'`` above), and each key has an independent value type (``str``
for ``'name'`` and ``int`` for ``'year'`` above). We've previously
seen the ``dict[K, V]`` type, which lets you declare uniform
dictionary types, where every value has the same type, and arbitrary keys
are supported. This is clearly not a good fit for
``movie`` above. Instead, you can use a ``TypedDict`` to give a precise
type for objects like ``movie``, where the type of each
dictionary value depends on the key:

.. code-block:: python

   from typing import TypedDict

   Movie = TypedDict('Movie', {'name': str, 'year': int})

   movie: Movie = {'name': 'Blade Runner', 'year': 1982}

``Movie`` is a ``TypedDict`` type with two items: ``'name'`` (with type ``str``)
and ``'year'`` (with type ``int``). Note that we used an explicit type
annotation for the ``movie`` variable. This type annotation is
important -- without it, mypy will try to infer a regular, uniform
:py:class:`dict` type for ``movie``, which is not what we want here.

.. note::

   If you pass a ``TypedDict`` object as an argument to a function, no
   type annotation is usually necessary since mypy can infer the
   desired type based on the declared argument type. Also, if an
   assignment target has been previously defined, and it has a
   ``TypedDict`` type, mypy will treat the assigned value as a ``TypedDict``,
   not :py:class:`dict`.

Now mypy will recognize these as valid:

.. code-block:: python

   name = movie['name']  # Okay; type of name is str
   year = movie['year']  # Okay; type of year is int

Mypy will detect an invalid key as an error:

.. code-block:: python

   director = movie['director']  # Error: 'director' is not a valid key

Mypy will also reject a runtime-computed expression as a key, as
it can't verify that it's a valid key. You can only use string
literals as ``TypedDict`` keys.

The ``TypedDict`` type object can also act as a constructor. It
returns a normal :py:class:`dict` object at runtime -- a ``TypedDict`` does
not define a new runtime type:

.. code-block:: python

   toy_story = Movie(name='Toy Story', year=1995)

This is equivalent to just constructing a dictionary directly using
``{ ... }`` or ``dict(key=value, ...)``. The constructor form is
sometimes convenient, since it can be used without a type annotation,
and it also makes the type of the object explicit.

Like all types, ``TypedDict``\s can be used as components to build
arbitrarily complex types. For example, you can define nested
``TypedDict``\s and containers with ``TypedDict`` items.
Unlike most other types, mypy uses structural compatibility checking
(or structural subtyping) with ``TypedDict``\s. A ``TypedDict`` object with
extra items is compatible with (a subtype of) a narrower
``TypedDict``, assuming item types are compatible (*totality* also affects
subtyping, as discussed below).

A ``TypedDict`` object is not a subtype of the regular ``dict[...]``
type (and vice versa), since :py:class:`dict` allows arbitrary keys to be
added and removed, unlike ``TypedDict``. However, any ``TypedDict`` object is
a subtype of (that is, compatible with) ``Mapping[str, object]``, since
:py:class:`~collections.abc.Mapping` only provides read-only access to the dictionary items:

.. code-block:: python

   def print_typed_dict(obj: Mapping[str, object]) -> None:
       for key, value in obj.items():
           print(f'{key}: {value}')

   print_typed_dict(Movie(name='Toy Story', year=1995))  # OK

.. note::

   Unless you are on Python 3.8 or newer (where ``TypedDict`` is available in
   standard library :py:mod:`typing` module) you need to install ``typing_extensions``
   using pip to use ``TypedDict``:

   .. code-block:: text

      python3 -m pip install --upgrade typing-extensions

Totality
--------

By default mypy ensures that a ``TypedDict`` object has all the specified
keys. This will be flagged as an error:

.. code-block:: python

   # Error: 'year' missing
   toy_story: Movie = {'name': 'Toy Story'}

Sometimes you want to allow keys to be left out when creating a
``TypedDict`` object. You can provide the ``total=False`` argument to
``TypedDict(...)`` to achieve this:

.. code-block:: python

   GuiOptions = TypedDict(
       'GuiOptions', {'language': str, 'color': str}, total=False)
   options: GuiOptions = {}  # Okay
   options['language'] = 'en'

You may need to use :py:meth:`~dict.get` to access items of a partial (non-total)
``TypedDict``, since indexing using ``[]`` could fail at runtime.
However, mypy still lets use ``[]`` with a partial ``TypedDict`` -- you
just need to be careful with it, as it could result in a :py:exc:`KeyError`.
Requiring :py:meth:`~dict.get` everywhere would be too cumbersome. (Note that you
are free to use :py:meth:`~dict.get` with total ``TypedDict``\s as well.)

Keys that aren't required are shown with a ``?`` in error messages:

.. code-block:: python

   # Revealed type is "TypedDict('GuiOptions', {'language'?: builtins.str,
   #                                            'color'?: builtins.str})"
   reveal_type(options)

Totality also affects structural compatibility. You can't use a partial
``TypedDict`` when a total one is expected. Also, a total ``TypedDict`` is not
valid when a partial one is expected.

Supported operations
--------------------

``TypedDict`` objects support a subset of dictionary operations and methods.
You must use string literals as keys when calling most of the methods,
as otherwise mypy won't be able to check that the key is valid. List
of supported operations:

* Anything included in :py:class:`~collections.abc.Mapping`:

  * ``d[key]``
  * ``key in d``
  * ``len(d)``
  * ``for key in d`` (iteration)
  * :py:meth:`d.get(key[, default]) <dict.get>`
  * :py:meth:`d.keys() <dict.keys>`
  * :py:meth:`d.values() <dict.values>`
  * :py:meth:`d.items() <dict.items>`

* :py:meth:`d.copy() <dict.copy>`
* :py:meth:`d.setdefault(key, default) <dict.setdefault>`
* :py:meth:`d1.update(d2) <dict.update>`
* :py:meth:`d.pop(key[, default]) <dict.pop>` (partial ``TypedDict``\s only)
* ``del d[key]`` (partial ``TypedDict``\s only)

.. note::

   :py:meth:`~dict.clear` and :py:meth:`~dict.popitem` are not supported since they are unsafe
   -- they could delete required ``TypedDict`` items that are not visible to
   mypy because of structural subtyping.

Class-based syntax
------------------

An alternative, class-based syntax to define a ``TypedDict`` is supported
in Python 3.6 and later:

.. code-block:: python

   from typing import TypedDict  # "from typing_extensions" in Python 3.7 and earlier

   class Movie(TypedDict):
       name: str
       year: int

The above definition is equivalent to the original ``Movie``
definition. It doesn't actually define a real class. This syntax also
supports a form of inheritance -- subclasses can define additional
items. However, this is primarily a notational shortcut. Since mypy
uses structural compatibility with ``TypedDict``\s, inheritance is not
required for compatibility. Here is an example of inheritance:

.. code-block:: python

   class Movie(TypedDict):
       name: str
       year: int

   class BookBasedMovie(Movie):
       based_on: str

Now ``BookBasedMovie`` has keys ``name``, ``year`` and ``based_on``.

Mixing required and non-required items
--------------------------------------

In addition to allowing reuse across ``TypedDict`` types, inheritance also allows
you to mix required and non-required (using ``total=False``) items
in a single ``TypedDict``. Example:

.. code-block:: python

   class MovieBase(TypedDict):
       name: str
       year: int

   class Movie(MovieBase, total=False):
       based_on: str

Now ``Movie`` has required keys ``name`` and ``year``, while ``based_on``
can be left out when constructing an object. A ``TypedDict`` with a mix of required
and non-required keys, such as ``Movie`` above, will only be compatible with
another ``TypedDict`` if all required keys in the other ``TypedDict`` are required keys in the
first ``TypedDict``, and all non-required keys of the other ``TypedDict`` are also non-required keys
in the first ``TypedDict``.

Read-only items
---------------

You can use ``typing.ReadOnly``, introduced in Python 3.13, or
``typing_extensions.ReadOnly`` to mark TypedDict items as read-only (:pep:`705`):

.. code-block:: python

    from typing import TypedDict

    # Or "from typing ..." on Python 3.13+
    from typing_extensions import ReadOnly

    class Movie(TypedDict):
        name: ReadOnly[str]
        num_watched: int

    m: Movie = {"name": "Jaws", "num_watched": 1}
    m["name"] = "The Godfather"  # Error: "name" is read-only
    m["num_watched"] += 1  # OK

A TypedDict with a mutable item can be assigned to a TypedDict
with a corresponding read-only item, and the type of the item can
vary :ref:`covariantly <variance-of-generics>`:

.. code-block:: python

    class Entry(TypedDict):
        name: ReadOnly[str | None]
        year: ReadOnly[int]

    class Movie(TypedDict):
        name: str
        year: int

    def process_entry(i: Entry) -> None: ...

    m: Movie = {"name": "Jaws", "year": 1975}
    process_entry(m)  # OK

Unions of TypedDicts
--------------------

Since TypedDicts are really just regular dicts at runtime, it is not possible to
use ``isinstance`` checks to distinguish between different variants of a Union of
TypedDict in the same way you can with regular objects.

Instead, you can use the :ref:`tagged union pattern <tagged_unions>`. The referenced
section of the docs has a full description with an example, but in short, you will
need to give each TypedDict the same key where each value has a unique
:ref:`Literal type <literal_types>`. Then, check that key to distinguish
between your TypedDicts.

Inline TypedDict types
----------------------

.. note::

    This is an experimental (non-standard) feature. Use
    ``--enable-incomplete-feature=InlineTypedDict`` to enable.

Sometimes you may want to define a complex nested JSON schema, or annotate
a one-off function that returns a TypedDict. In such cases it may be convenient
to use inline TypedDict syntax. For example:

.. code-block:: python

    def test_values() -> {"int": int, "str": str}:
        return {"int": 42, "str": "test"}

    class Response(TypedDict):
        status: int
        msg: str
        # Using inline syntax here avoids defining two additional TypedDicts.
        content: {"items": list[{"key": str, "value": str}]}

Inline TypedDicts can also by used as targets of type aliases, but due to
ambiguity with a regular variables it is only allowed for (newer) explicit
type alias forms:

.. code-block:: python

    from typing import TypeAlias

    X = {"a": int, "b": int}  # creates a variable with type dict[str, type[int]]
    Y: TypeAlias = {"a": int, "b": int}  # creates a type alias
    type Z = {"a": int, "b": int}  # same as above (Python 3.12+ only)

Also, due to incompatibility with runtime type-checking it is strongly recommended
to *not* use inline syntax in union types.
````

## File: docs/README.md
````markdown
Mypy Documentation
==================

What's this?
------------

This directory contains the source code for Mypy documentation (under `source/`)
and build scripts. The documentation uses Sphinx and reStructuredText. We use
`furo` as the documentation theme.

Building the documentation
--------------------------

Install Sphinx and other dependencies (i.e. theme) needed for the documentation.
From the `docs` directory, use `pip`:

```
pip install -r requirements-docs.txt
```

Build the documentation like this:

```
make html
```

The built documentation will be placed in the `docs/build` directory. Open
`docs/build/index.html` to view the documentation.

Helpful documentation build commands
------------------------------------

Clean the documentation build:

```
make clean
```

Test and check the links found in the documentation:

```
make linkcheck
```

Documentation on Read The Docs
------------------------------

The mypy documentation is hosted on Read The Docs, and the latest version
can be found at https://mypy.readthedocs.io/en/latest.
````

## File: docs/requirements-docs.txt
````
sphinx>=8.1.0
furo>=2022.3.4
myst-parser>=4.0.0
sphinx_inline_tabs>=2023.04.21
````
