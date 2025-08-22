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
- Only files matching these patterns are included: doc/**/*.{md,markdown,mdx,rmd,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
doc/
  additional_tools/
    pyreverse/
      configuration.rst
      index.rst
      output_examples.rst
    symilar/
      index.rst
  data/
    messages/
      a/
        anomalous-backslash-in-string/
          details.rst
          related.rst
        arguments-differ/
          details.rst
          related.rst
        assert-on-string-literal/
          details.rst
          related.rst
        assert-on-tuple/
          details.rst
        astroid-error/
          details.rst
        await-outside-async/
          related.rst
      b/
        bad-chained-comparison/
          related.rst
        bad-configuration-section/
          details.rst
        bad-docstring-quotes/
          details.rst
          related.rst
        bad-exception-cause/
          related.rst
        bad-format-character/
          details.rst
          related.rst
        bad-format-string/
          related.rst
        bad-format-string-key/
          details.rst
        bad-indentation/
          details.rst
        bad-plugin-value/
          details.rst
        bad-str-strip-call/
          details.rst
          related.rst
        bad-string-format-type/
          details.rst
          related.rst
        bad-super-call/
          details.rst
          related.rst
        bare-except/
          details.rst
          related.rst
        bare-name-capture-pattern/
          related.rst
        boolean-datetime/
          related.rst
        break-in-finally/
          related.rst
        broad-exception-caught/
          details.rst
          related.rst
        broad-exception-raised/
          related.rst
        broken-collections-callable/
          related.rst
      c/
        c-extension-no-member/
          details.rst
        cell-var-from-loop/
          related.rst
        config-parse-error/
          details.rst
        confusing-consecutive-elif/
          details.rst
        consider-alternative-union-syntax/
          details.rst
        consider-using-dict-comprehension/
          details.rst
        consider-using-f-string/
          details.rst
        consider-using-generator/
          details.rst
          related.rst
        consider-using-set-comprehension/
          details.rst
        consider-using-with/
          details.rst
          related.rst
        contextmanager-generator-missing-cleanup/
          details.rst
          related.rst
        continue-in-finally/
          related.rst
        cyclic-import/
          details.rst
      d/
        dangerous-default-value/
          details.rst
        deprecated-argument/
          details.rst
        deprecated-attribute/
          details.rst
        deprecated-class/
          details.rst
        deprecated-decorator/
          details.rst
        deprecated-method/
          details.rst
        deprecated-module/
          details.rst
        duplicate-code/
          details.rst
        duplicate-key/
          related.rst
      e/
        exec-used/
          details.rst
          related.rst
      f/
        fatal/
          details.rst
        file-ignored/
          details.rst
        fixme/
          details.rst
      g/
        global-at-module-level/
          related.rst
      i/
        implicit-str-concat/
          details.rst
        import-error/
          details.rst
        import-private-name/
          details.rst
        import-self/
          details.rst
        invalid-all-object/
          details.rst
          related.rst
        invalid-character-carriage-return/
          details.rst
        invalid-character-nul/
          details.rst
          related.rst
        invalid-characters-in-docstring/
          details.rst
        invalid-name/
          details.rst
        invalid-sequence-index/
          details.rst
        invalid-slots-object/
          related.rst
        invalid-unicode-codec/
          details.rst
      l/
        line-too-long/
          details.rst
        literal-comparison/
          related.rst
        logging-format-interpolation/
          details.rst
          related.rst
        logging-fstring-interpolation/
          details.rst
          related.rst
        logging-not-lazy/
          details.rst
          related.rst
      m/
        method-check-failed/
          details.rst
        misplaced-future/
          details.rst
        missing-final-newline/
          details.rst
          related.rst
        missing-format-argument-key/
          related.rst
        missing-return-doc/
          details.rst
        missing-return-type-doc/
          details.rst
        missing-timeout/
          details.rst
        missing-yield-doc/
          details.rst
        missing-yield-type-doc/
          details.rst
        mixed-line-endings/
          related.rst
        multiple-constructor-doc/
          details.rst
      n/
        no-member/
          details.rst
        no-self-use/
          details.rst
        non-ascii-file-name/
          related.rst
        not-async-context-manager/
          details.rst
      o/
        overlapping-except/
          related.rst
        overridden-final-method/
          details.rst
          related.rst
      p/
        parse-error/
          details.rst
        pointless-string-statement/
          related.rst
        positional-only-arguments-expected/
          related.rst
        possibly-used-before-assignment/
          details.rst
        prefer-typing-namedtuple/
          related.rst
      r/
        raise-missing-from/
          related.rst
        raw-checker-failed/
          details.rst
        redefined-builtin/
          details.rst
        redefined-outer-name/
          details.rst
        redundant-unittest-assert/
          details.rst
          related.rst
        relative-beyond-top-level/
          details.rst
          related.rst
        return-arg-in-generator/
          details.rst
          related.rst
        return-in-finally/
          related.rst
        return-in-init/
          related.rst
      s/
        self-assigning-variable/
          related.rst
        simplifiable-if-expression/
          related.rst
        singleton-comparison/
          related.rst
        stop-iteration-return/
          details.rst
          related.rst
        subclassed-final-class/
          details.rst
          related.rst
        subprocess-run-check/
          related.rst
        suppressed-message/
          details.rst
        syntax-error/
          details.rst
          related.rst
      t/
        too-few-format-args/
          related.rst
        too-many-format-args/
          related.rst
        too-many-lines/
          details.rst
        too-many-locals/
          details.rst
        too-many-positional-arguments/
          details.rst
          related.rst
        too-many-public-methods/
          details.rst
          related.rst
        try-except-raise/
          details.rst
        typevar-name-incorrect-variance/
          details.rst
      u/
        unbalanced-tuple-unpacking/
          related.rst
        undefined-all-variable/
          related.rst
        unexpected-line-ending-format/
          related.rst
        unidiomatic-typecheck/
          related.rst
        unnecessary-default-type-args/
          details.rst
          related.rst
        unnecessary-dunder-call/
          related.rst
        unrecognized-option/
          details.rst
        unused-import/
          details.rst
          related.rst
        unused-wildcard-import/
          detail.rst
        use-a-generator/
          details.rst
          related.rst
        use-dict-literal/
          details.rst
          related.rst
        use-maxsplit-arg/
          details.rst
        use-sequence-for-iteration/
          details.rst
        use-yield-from/
          details.rst
          related.rst
        useless-import-alias/
          details.rst
          related.rst
        useless-option-value/
          details.rst
        useless-parent-delegation/
          related.rst
        using-assignment-expression-in-unsupported-version/
          details.rst
        using-exception-groups-in-unsupported-version/
          details.rst
        using-f-string-in-unsupported-version/
          details.rst
        using-final-decorator-in-unsupported-version/
          details.rst
          related.rst
        using-generic-type-syntax-in-unsupported-version/
          details.rst
        using-positional-only-args-in-unsupported-version/
          details.rst
      w/
        while-used/
          related.rst
      y/
        yield-inside-async-function/
          details.rst
          related.rst
  development_guide/
    api/
      index.rst
      pylint.rst
    contributor_guide/
      tests/
        index.rst
        install.rst
        launching_test.rst
        writing_test.rst
      contribute.rst
      governance.rst
      index.rst
      major_release.rst
      minor_release.rst
      oss_fuzz.rst
      patch_release.rst
      profiling.rst
      release.rst
    how_tos/
      custom_checkers.rst
      index.rst
      plugins.rst
      transform_plugins.rst
    technical_reference/
      checkers.rst
      index.rst
      startup.rst
  user_guide/
    checkers/
      extensions.rst
      features.rst
      index.rst
    configuration/
      all-options.rst
      index.rst
    installation/
      ide_integration/
        flymake-emacs.rst
        index.rst
        textmate.rst
      badge.rst
      command_line_installation.rst
      index.rst
      pre-commit-integration.rst
      upgrading_pylint.rst
      with-multiple-interpreters.rst
    messages/
      index.rst
      message_control.rst
      messages_overview.rst
    usage/
      index.rst
      output.rst
      run.rst
  whatsnew/
    0/
      0.x.rst
      index.rst
    1/
      1.6/
        full.rst
        index.rst
        summary.rst
      1.7/
        full.rst
        index.rst
        summary.rst
      1.8/
        full.rst
        index.rst
        summary.rst
      1.9/
        full.rst
        index.rst
        summary.rst
      1.0.rst
      1.1.rst
      1.2.rst
      1.3.rst
      1.4.rst
      1.5.rst
      index.rst
    2/
      2.0/
        full.rst
        index.rst
        summary.rst
      2.1/
        full.rst
        index.rst
        summary.rst
      2.10/
        full.rst
        index.rst
        summary.rst
      2.11/
        full.rst
        index.rst
        summary.rst
      2.12/
        full.rst
        index.rst
        summary.rst
      2.13/
        full.rst
        index.rst
        summary.rst
      2.14/
        full.rst
        index.rst
        summary.rst
      2.15/
        index.rst
      2.16/
        index.rst
      2.17/
        index.rst
      2.2/
        full.rst
        index.rst
        summary.rst
      2.3/
        full.rst
        index.rst
        summary.rst
      2.4/
        full.rst
        index.rst
        summary.rst
      2.5/
        full.rst
        index.rst
        summary.rst
      2.6/
        full.rst
        index.rst
        summary.rst
      2.7/
        full.rst
        index.rst
        summary.rst
      2.8/
        full.rst
        index.rst
        summary.rst
      2.9/
        full.rst
        index.rst
        summary.rst
      index.rst
    3/
      3.0/
        index.rst
      3.1/
        index.rst
      3.2/
        index.rst
      3.3/
        index.rst
      index.rst
    4/
      4.0/
        index.rst
      index.rst
    fragments/
      _template.rst
    full_changelog_explanation.rst
    index.rst
    summary_explanation.rst
  contact.rst
  faq.rst
  index.rst
  readthedoc_requirements.txt
  requirements.txt
  short_text_contribute.rst
  short_text_installation.rst
  tutorial.rst
```

# Files

## File: doc/additional_tools/pyreverse/configuration.rst
````
.. This file is auto-generated. Make any changes to the associated
.. docs extension in 'doc/exts/pyreverse_configuration.py'.


Usage
#####


``pyreverse`` is run from the command line using the following syntax::

  pyreverse [options] <packages>

where ``<packages>`` is one or more Python packages or modules to analyze.

The available options are organized into the following categories:

* :ref:`filtering-and-scope` - Control which classes and relationships appear in your diagrams
* :ref:`display-options` - Customize the visual appearance including colors and labels
* :ref:`output-control` - Select output formats and set the destination directory
* :ref:`project-configuration` - Define project settings like source roots and ignored files


.. _filtering-and-scope:

Filtering and Scope
===================


--all-ancestors
---------------
*Show all ancestors of all classes in <projects>.*

**Default:**  ``None``


--all-associated
----------------
*Show all classes associated with the target classes, including indirect associations.*

**Default:**  ``None``


--class
-------
*Create a class diagram with all classes related to <class>; this uses by default the options -ASmy*

**Default:**  ``None``


--filter-mode
-------------
*Filter attributes and functions according to <mode>. Correct modes are:
'PUB_ONLY' filter all non public attributes [DEFAULT], equivalent to PRIVATE+SPECIAL
'ALL' no filter
'SPECIAL' filter Python special functions except constructor
'OTHER' filter protected and private attributes*

**Default:**  ``PUB_ONLY``


--max-depth
-----------
*Maximum depth of packages/modules to include in the diagram, relative to the deepest specified package. A depth of 0 shows only the specified packages/modules, while 1 includes their immediate children, etc. When specifying nested packages,  depth is calculated from the deepest package level. If not specified, all packages/modules in the hierarchy are shown.*

**Default:**  ``None``


--show-ancestors
----------------
*Show <ancestor> generations of ancestor classes not in <projects>.*

**Default:**  ``None``


--show-associated
-----------------
*Show <association_level> levels of associated classes not in <projects>.*

**Default:**  ``None``


--show-builtin
--------------
*Include builtin objects in representation of classes.*

**Default:**  ``False``


--show-stdlib
-------------
*Include standard library objects in representation of classes.*

**Default:**  ``False``




.. _display-options:

Display Options
===============


--color-palette
---------------
*Comma separated list of colors to use for the package depth coloring.*

**Default:**  ``('#77AADD', '#99DDFF', '#44BB99', '#BBCC33', '#AAAA00', '#EEDD88', '#EE8866', '#FFAABB', '#DDDDDD')``


--colorized
-----------
*Use colored output. Classes/modules of the same package get the same color.*

**Default:**  ``False``


--max-color-depth
-----------------
*Use separate colors up to package depth of <depth>. Higher depths will reuse colors.*

**Default:**  ``2``


--module-names
--------------
*Include module name in the representation of classes.*

**Default:**  ``None``


--no-standalone
---------------
*Only show nodes with connections.*

**Default:**  ``False``


--only-classnames
-----------------
*Don't show attributes and methods in the class boxes; this disables -f values.*

**Default:**  ``False``




.. _output-control:

Output Control
==============


--output
--------
*Create a *.<format> output file if format is available. Available formats are: .dot, .puml, .plantuml, .mmd, .html. Any other format will be tried to be created by using the 'dot' command line tool, which requires a graphviz installation. In this case, these additional formats are available (see `Graphviz output formats <https://graphviz.org/docs/outputs/>`_).*

**Default:**  ``dot``


--output-directory
------------------
*Set the output directory path.*

**Default:** ``""``




.. _project-configuration:

Project Configuration
=====================


--ignore
--------
*Files or directories to be skipped. They should be base names, not paths.*

**Default:**  ``('CVS',)``


--project
---------
*Set the project name. This will later be appended to the output file names.*

**Default:** ``""``


--source-roots
--------------
*Add paths to the list of the source roots. Supports globbing patterns. The source root is an absolute path or a path relative to the current working directory used to determine a package namespace for modules located under the source root.*

**Default:**  ``()``


--verbose
---------
*Makes pyreverse more verbose/talkative. Mostly useful for debugging.*

**Default:**  ``False``
````

## File: doc/additional_tools/pyreverse/index.rst
````
.. _pyreverse:

=========
Pyreverse
=========

``pyreverse`` is a powerful tool that creates UML diagrams from your Python code. It helps you visualize:

- Package dependencies and structure
- Class hierarchies and relationships
- Method and attribute organization

Output Formats
==============

``pyreverse`` supports multiple output formats:

* Native formats:
    * ``.dot``/``.gv`` (Graphviz)
    * ``.puml``/``.plantuml`` (PlantUML)
    * ``.mmd``/``.html`` (MermaidJS)

* Additional formats (requires Graphviz installation):
    * All `Graphviz output formats <https://graphviz.org/docs/outputs/>`_ (PNG, SVG, PDF, etc.)
    * ``pyreverse`` first generates a temporary ``.gv`` file, which is then fed to Graphviz to generate the final image

Getting Started
===============

Check out the :doc:`configuration` guide to learn about available options, or see :doc:`output_examples`
for sample diagrams and common use cases.

.. toctree::
   :maxdepth: 2
   :caption: Pyreverse
   :titlesonly:
   :hidden:

   configuration
   output_examples
````

## File: doc/additional_tools/pyreverse/output_examples.rst
````
Example Output
##############

Example diagrams generated with the ``.puml`` output format are shown below.

Package Diagram
...............

.. image:: ../../media/pyreverse_example_packages.png
   :width: 344
   :height: 177
   :alt: Package diagram generated by pyreverse
   :align: center

Class Diagram
.............

.. image:: ../../media/pyreverse_example_classes.png
   :width: 625
   :height: 589
   :alt: Class diagram generated by pyreverse
   :align: center

Creating Class Diagrams for Specific Classes
''''''''''''''''''''''''''''''''''''''''''''

In many cases creating a single diagram depicting all classes in the project yields a rather unwieldy, giant diagram.
While limiting the input path to a single package or module can already help greatly to narrow down the scope, the ``-c`` option
provides another way to create a class diagram focusing on a single class and its collaborators.
For example, running::

  pyreverse -ASmy -c pylint.checkers.classes.ClassChecker pylint

will generate the full class and package diagrams for ``pylint``, but will additionally generate a file ``pylint.checkers.classes.ClassChecker.dot``:

.. image:: ../../media/ClassChecker_diagram.png
   :width: 757
   :height: 1452
   :alt: Package diagram generated by pyreverse
   :align: center
````

## File: doc/additional_tools/symilar/index.rst
````
.. _symilar:

Symilar
-------

The console script ``symilar`` finds copy pasted block of text in a set of files. It provides a command line interface to check only the ``duplicate-code`` message.

It can be invoked with::

  symilar [-d|--duplicates min_duplicated_lines] [-i|--ignore-comments] [--ignore-docstrings] [--ignore-imports] [--ignore-signatures] file1...

All files that shall be checked have to be passed in explicitly, e.g.::

  symilar foo.py, bar.py, subpackage/spam.py, subpackage/eggs.py

``symilar`` produces output like the following::

  17 similar lines in 2 files
  ==tests/data/clientmodule_test.py:3
  ==tests/data/suppliermodule_test.py:12
    class Ancestor:
        """ Ancestor method """
        cls_member = DoNothing()

        def __init__(self, value):
            local_variable = 0
            self.attr = 'this method shouldn\'t have a docstring'
            self.__value = value

        def get_value(self):
            """ nice docstring ;-) """
            return self.__value

        def set_value(self, value):
            self.__value = value
            return 'this method shouldn\'t have a docstring'
  TOTAL lines=58 duplicates=17 percent=29.31
````

## File: doc/data/messages/a/anomalous-backslash-in-string/details.rst
````
``\z`` is same as ``\\z`` because there's no escape sequence for ``z``. But it is not clear
for the reader of the code.

The only reason this is demonstrated to raise ``syntax-error`` is because
pylint's CI now runs on Python 3.12, where this truly raises a ``SyntaxError``.
We hope to address this discrepancy in the documentation in the future.
````

## File: doc/data/messages/a/anomalous-backslash-in-string/related.rst
````
- `String and Bytes literals <https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals>`_
- `Long form stackoverflow explanation  <https://stackoverflow.com/a/19030982/2519059>`_
````

## File: doc/data/messages/a/arguments-differ/details.rst
````
``argument-differ`` denotes an issue with the Liskov Substitution Principle.
This means that the code in question violates an important design principle which does not have
one single solution. We recommend to search online for the best solution in your case.

To give some examples of potential solutions:

* Add the argument to the parent class
* Remove the inheritance completely
* Add default arguments to the child class
````

## File: doc/data/messages/a/arguments-differ/related.rst
````
- `Liskov Substitution Principle <https://en.wikipedia.org/wiki/Liskov_substitution_principle>`_
````

## File: doc/data/messages/a/assert-on-string-literal/details.rst
````
Directly asserting a string literal will always pass. The solution is to
test something that could fail, or not assert at all.

For ``unittest`` assertions there is the similar :ref:`redundant-unittest-assert` message.
````

## File: doc/data/messages/a/assert-on-string-literal/related.rst
````
- `Tests without assertion <https://stackoverflow.com/a/137418/2519059>`_
- `Testing that there is no error raised <https://stackoverflow.com/questions/20274987>`_
- `Parametrizing conditional raising <https://docs.pytest.org/en/latest/example/parametrize.html#parametrizing-conditional-raising>`_
````

## File: doc/data/messages/a/assert-on-tuple/details.rst
````
Directly asserting a non-empty tuple will always pass. The solution is to
 test something that could fail, or not assert at all.

 For ``unittest`` assertions there is the similar :ref:`redundant-unittest-assert` message.
````

## File: doc/data/messages/a/astroid-error/details.rst
````
This is a message linked to an internal problem in pylint. There's nothing to change in your code,
but maybe in pylint's configuration or installation.
````

## File: doc/data/messages/a/await-outside-async/related.rst
````
- `PEP 492 <https://peps.python.org/pep-0492/#await-expression>`_
````

## File: doc/data/messages/b/bad-chained-comparison/related.rst
````
- `Comparison Chaining <https://docs.python.org/3/reference/expressions.html#comparisons>`_
````

## File: doc/data/messages/b/bad-configuration-section/details.rst
````
This error was raised when we encountered an unexpected value type in a toml
configuration between pylint 2.12 and pylint 2.14 (before the argparse refactor).
````

## File: doc/data/messages/b/bad-docstring-quotes/details.rst
````
From `PEP 257`:
    "For consistency, always use ``"""triple double quotes"""`` around docstrings."
````

## File: doc/data/messages/b/bad-docstring-quotes/related.rst
````
- `PEP 257 – Docstring Conventions <https://peps.python.org/pep-0257/#specification>`_
````

## File: doc/data/messages/b/bad-exception-cause/related.rst
````
- `The raise statement <https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement>`_
- `Explicit Exception Chaining <https://peps.python.org/pep-3134/#explicit-exception-chaining>`_ per PEP 3134
````

## File: doc/data/messages/b/bad-format-character/details.rst
````
This check is currently only active for "old-style" string formatting as seen in the examples.
See `Issue #6085 <https://github.com/pylint-dev/pylint/issues/6085>`_ for more information.
````

## File: doc/data/messages/b/bad-format-character/related.rst
````
- `Format String Syntax <https://docs.python.org/3/library/string.html#formatstrings>`_
- `PyFormat <https://pyformat.info/>`_
````

## File: doc/data/messages/b/bad-format-string/related.rst
````
- `Format String Syntax <https://docs.python.org/3/library/string.html#formatstrings>`_
- `PyFormat <https://pyformat.info/>`_
````

## File: doc/data/messages/b/bad-format-string-key/details.rst
````
This check only works for old-style string formatting using the '%' operator.

This check only works if the dictionary with the values to be formatted is defined inline.
Passing a variable will not trigger the check as the other keys in this dictionary may be
used in other contexts, while an inline defined dictionary is clearly only intended to hold
the values that should be formatted.
````

## File: doc/data/messages/b/bad-indentation/details.rst
````
The option ``--indent-string`` can be used to set the indentation unit for this check.
````

## File: doc/data/messages/b/bad-plugin-value/details.rst
````
One of your pylint plugins cannot be loaded. There's nothing to change in
your code, but your pylint configuration or installation has an issue.

For example, there might be a typo. The following config::

    [MAIN]
    load-plugins = pylint.extensions.bad_biultin

Should be::

    [MAIN]
    load-plugins = pylint.extensions.bad_builtin

Or the plugin you added is not importable in your environment.
````

## File: doc/data/messages/b/bad-str-strip-call/details.rst
````
A common misconception is that ``str.strip('Hello')`` removes the *substring* ``'Hello'`` from the beginning and end of the string.
This is **not**  the case.
From the `documentation <https://docs.python.org/3/library/stdtypes.html?highlight=strip#str.strip>`_:

> The chars argument is not a prefix or suffix; rather, all combinations of its values are stripped

Duplicated characters in the ``str.strip`` call, besides not having any effect on the actual result, may indicate this misunderstanding.
````

## File: doc/data/messages/b/bad-str-strip-call/related.rst
````
- Documentation: `str.strip([chars]) <https://docs.python.org/3/library/stdtypes.html?highlight=strip#str.strip>`_
````

## File: doc/data/messages/b/bad-string-format-type/details.rst
````
This check is currently only active for "old-style" string formatting as seen in the examples.
See `Issue #6085 <https://github.com/pylint-dev/pylint/issues/6163>`_ for more information.
````

## File: doc/data/messages/b/bad-string-format-type/related.rst
````
- `Format String Syntax <https://docs.python.org/3/library/string.html#formatstrings>`_
- `PyFormat <https://pyformat.info/>`_
````

## File: doc/data/messages/b/bad-super-call/details.rst
````
In Python 2.7, ``super()`` has to be called with its own class and ``self`` as arguments (``super(Cat, self)``), which can
lead to a mix up of parent and child class in the code.

In Python 3 the recommended way is to call ``super()`` without arguments (see also ``super-with-arguments``).

One exception is calling ``super()`` on a non-direct parent class. This can be used to get a method other than the default
method returned by the ``mro()``.
````

## File: doc/data/messages/b/bad-super-call/related.rst
````
- `Documentation for super() <https://docs.python.org/3/library/functions.html#super>`_
````

## File: doc/data/messages/b/bare-except/details.rst
````
A good rule of thumb is to limit use of bare ‘except’ clauses to two cases:
- If the exception handler will be printing out or logging the traceback; at least the user will be aware that an error has occurred.
- If the code needs to do some cleanup work, but then lets the exception propagate upwards with raise. ``try...finally`` can be a better way to handle this case.
````

## File: doc/data/messages/b/bare-except/related.rst
````
- `Programming recommendation in PEP8 <https://peps.python.org/pep-0008/#programming-recommendations>`_
- `PEP 760 – No More Bare Excepts (Rejected) <https://peps.python.org/pep-0760/>`_
- `Discussion about PEP 760 <https://discuss.python.org/t/pep-760-no-more-bare-excepts/67182>`_
````

## File: doc/data/messages/b/bare-name-capture-pattern/related.rst
````
- `PEP 636 <https://peps.python.org/pep-0636/#matching-against-constants-and-enums>`_
````

## File: doc/data/messages/b/boolean-datetime/related.rst
````
- `Python bug tracker <https://bugs.python.org/issue13936>`_
````

## File: doc/data/messages/b/break-in-finally/related.rst
````
- `Python 3 docs 'finally' clause <https://docs.python.org/3/reference/compound_stmts.html#finally-clause>`_
- `PEP 765 - Disallow return/break/continue that exit a finally block <https://peps.python.org/pep-0765/>`_
````

## File: doc/data/messages/b/broad-exception-caught/details.rst
````
For example, you're trying to import a library with required system dependencies and you catch
everything instead of only import errors, you will miss the error message telling you, that
your code could work if you had installed the system dependencies.
````

## File: doc/data/messages/b/broad-exception-caught/related.rst
````
- `Should I always specify an exception type in 'except' statements? <https://stackoverflow.com/a/14797508/2519059>`_
````

## File: doc/data/messages/b/broad-exception-raised/related.rst
````
- `Programming recommendation in PEP8 <https://peps.python.org/pep-0008/#programming-recommendations>`_
````

## File: doc/data/messages/b/broken-collections-callable/related.rst
````
- `bpo-42965 <https://bugs.python.org/issue42965>`_
````

## File: doc/data/messages/c/c-extension-no-member/details.rst
````
``c-extension-no-member`` is an informational variant of ``no-member`` to encourage
allowing introspection of C extensions as described in the
`page <https://pylint.readthedocs.io/en/latest/user_guide/messages/error/no-member.html>`_
for ``no-member``.
````

## File: doc/data/messages/c/cell-var-from-loop/related.rst
````
- `Stackoverflow discussion <https://stackoverflow.com/questions/25314547/cell-var-from-loop-warning-from-pylint>`_
````

## File: doc/data/messages/c/config-parse-error/details.rst
````
This is a message linked to a problem in your configuration not your code.
````

## File: doc/data/messages/c/confusing-consecutive-elif/details.rst
````
Creating a function for the nested conditional, or adding an explicit ``else`` in the indented ``if`` statement, even if it only contains a ``pass`` statement, can help clarify the code.
````

## File: doc/data/messages/c/consider-alternative-union-syntax/details.rst
````
Using the shorthand syntax for union types is |recommended over the typing module|__. This is consistent with the broader recommendation to prefer built-in types over imports (for example, using ``list`` instead of the now-deprecated ``typing.List``).

``typing.Optional`` can also cause confusion in annotated function arguments, since an argument annotated as ``Optional`` is still a *required* argument when a default value is not set. Explicitly annotating such arguments with ``type | None`` makes the intention clear.

.. |recommended over the typing module| replace:: recommended over the ``typing`` module
__ https://docs.python.org/3/library/typing.html#typing.Union
````

## File: doc/data/messages/c/consider-using-dict-comprehension/details.rst
````
pyupgrade_ or ruff_ can fix this issue automatically.

.. _pyupgrade: https://github.com/asottile/pyupgrade
.. _ruff: https://docs.astral.sh/ruff/
````

## File: doc/data/messages/c/consider-using-f-string/details.rst
````
Formatted string literals (f-strings) give a concise, consistent syntax
that can replace most use cases for the ``%`` formatting operator,
``str.format()`` and ``string.Template``.

F-strings also perform better than alternatives; see
`this tweet <https://twitter.com/raymondh/status/1205969258800275456>`_ for
a simple example.
````

## File: doc/data/messages/c/consider-using-generator/details.rst
````
Removing ``[]`` inside calls that can use containers or generators should be considered
for performance reasons since a generator will have an upfront cost to pay. The
performance will be better if you are working with long lists or sets.

For ``max``, ``min`` and ``sum`` using a generator is also recommended by pep289.
````

## File: doc/data/messages/c/consider-using-generator/related.rst
````
- `PEP 289 <https://peps.python.org/pep-0289/>`_
- `Benchmark and discussion for any/all/list/tuple <https://github.com/pylint-dev/pylint/pull/3309#discussion_r576683109>`_
- `Benchmark and discussion for sum/max/min <https://github.com/pylint-dev/pylint/pull/6595#issuecomment-1125704244>`_
````

## File: doc/data/messages/c/consider-using-set-comprehension/details.rst
````
pyupgrade_ or ruff_ can fix this issue automatically.

.. _pyupgrade: https://github.com/asottile/pyupgrade
.. _ruff: https://docs.astral.sh/ruff/
````

## File: doc/data/messages/c/consider-using-with/details.rst
````
Calling ``write()`` without using the ``with`` keyword or calling ``close()`` might
result in the arguments of ``write()`` not being completely written to the disk,
even if the program exits successfully.

This message applies to callables of Python's stdlib which can be replaced by a ``with`` statement.
It is suppressed in the following cases:

- the call is located inside a context manager
- the call result is returned from the enclosing function
- the call result is used in a ``with`` statement itself
````

## File: doc/data/messages/c/consider-using-with/related.rst
````
- `Python doc: Reading and writing files <https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files>`_
- `PEP 343 <https://peps.python.org/pep-0343/>`_
- `Context managers in Python <https://johnlekberg.com/blog/2020-10-11-ctx-manage.html>`_ by John Lekberg
- `Rationale <https://stackoverflow.com/a/73181877/2519059>`_
````

## File: doc/data/messages/c/contextmanager-generator-missing-cleanup/details.rst
````
Instantiating and using a contextmanager inside a generator function can
result in unexpected behavior if there is an expectation that the context is only
available for the generator function. In the case that the generator is not closed or destroyed
then the context manager is held suspended as is.

This message warns on the generator function instead of the contextmanager function
because the ways to use a contextmanager are many.
A contextmanager can be used as a decorator (which immediately has ``__enter__``/``__exit__`` applied)
and the use of ``as ...`` or discard of the return value also implies whether the context needs cleanup or not.
So for this message, warning the invoker of the contextmanager is important.

The check can create false positives if ``yield`` is used inside an ``if-else`` block without custom cleanup. Use ``pylint: disable`` for these.

.. code-block:: python

    from contextlib import contextmanager

    @contextmanager
    def good_cm_no_cleanup():
        contextvar = "acquired context"
        print("cm enter")
        if some_condition:
            yield contextvar
        else:
            yield contextvar


    def good_cm_no_cleanup_genfunc():
        # pylint: disable-next=contextmanager-generator-missing-cleanup
        with good_cm_no_cleanup() as context:
            yield context * 2
````

## File: doc/data/messages/c/contextmanager-generator-missing-cleanup/related.rst
````
- `Rationale <https://discuss.python.org/t/preventing-yield-inside-certain-context-managers/1091>`_
- `CPython Issue <https://github.com/python/cpython/issues/81924#issuecomment-1093830682>`_
````

## File: doc/data/messages/c/continue-in-finally/related.rst
````
- `Python 3 docs 'finally' clause <https://docs.python.org/3/reference/compound_stmts.html#finally-clause>`_
- `PEP 765 - Disallow return/break/continue that exit a finally block <https://peps.python.org/pep-0765/>`_
````

## File: doc/data/messages/c/cyclic-import/details.rst
````
The good code is just an example. There are various strategies to resolving
cyclic imports and the best choice relies heavily on the context of the code
and the affected modules.
````

## File: doc/data/messages/d/dangerous-default-value/details.rst
````
With a mutable default value, with each call the default value is modified, i.e.:

.. code-block:: python

    whats_on_the_telly() # ["property of the zoo"]
    whats_on_the_telly() # ["property of the zoo", "property of the zoo"]
    whats_on_the_telly() # ["property of the zoo", "property of the zoo", "property of the zoo"]
````

## File: doc/data/messages/d/deprecated-argument/details.rst
````
The actual replacement needs to be studied on a case by case basis
by reading the deprecation warning or the release notes.
````

## File: doc/data/messages/d/deprecated-attribute/details.rst
````
The actual replacement needs to be studied on a case by case basis
by reading the deprecation warning or the release notes.
````

## File: doc/data/messages/d/deprecated-class/details.rst
````
The actual replacement needs to be studied on a case by case basis
by reading the deprecation warning or the release notes.
````

## File: doc/data/messages/d/deprecated-decorator/details.rst
````
The actual replacement needs to be studied on a case by case basis
by reading the deprecation warning or the release notes.
````

## File: doc/data/messages/d/deprecated-method/details.rst
````
The actual replacement needs to be studied on a case by case basis
by reading the deprecation warning or the release notes.
````

## File: doc/data/messages/d/deprecated-module/details.rst
````
The actual replacement needs to be studied on a case by case basis
by reading the deprecation warning or the release notes.
````

## File: doc/data/messages/d/duplicate-code/details.rst
````
If you need to make a change to the logic or functionality of the duplicated
code, you will need to identify all the places that need to be changed, which
can be time-consuming and error-prone. If there are multiple copies of the
same code, then you will also need to test each copy to ensure that the
functionality is correct. Duplicate code can be confusing for someone who is
trying to understand the logic and flow of the code if they come across multiple
identical or nearly identical blocks of code. The reader can then skim and
think something is identical when it actually isn't. This is particularly true
during review.
````

## File: doc/data/messages/d/duplicate-key/related.rst
````
- `Python Dictionaries <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
- `Mapping Types — dict <https://docs.python.org/3/library/stdtypes.html#typesmapping>`_
````

## File: doc/data/messages/e/exec-used/details.rst
````
The available methods and variables used in ``exec()`` may introduce a security hole.
You can restrict the use of these variables and methods by passing optional globals
and locals parameters (dictionaries) to the ``exec()`` method.

However, use of ``exec()`` is still insecure if you allow some functions like
``__import__`` or ``open``. For example, consider the following call that writes a
file to the user's system and then execute code unrestrained by the ``allowed_globals``,
or ``allowed_locals`` parameters:

.. code-block:: python

    import textwrap


    def forbid_print(*args):
        raise ValueError("This is raised when a print is used")


    allowed_globals = {
        "__builtins__": {
            "__import__": __builtins__.__import__,
            "open": __builtins__.open,
            "print": forbid_print,
        }
    }

    exec(
        textwrap.dedent(
            """
        import textwrap

        with open("nefarious.py", "w") as f:
            f.write(textwrap.dedent('''
                def connive():
                    print("Here's some code as nefarious as imaginable")
            '''))

        import nefarious

        nefarious.connive()  # This will NOT raise a ValueError
        """
        ),
        allowed_globals,
    )


The import is used only for readability of the example in this case but it could
import a dangerous functions:

- ``subprocess.run('echo "print(\"Hello, World!\")" > nefarious.py'``
- ``pathlib.Path("nefarious.py").write_file("print(\"Hello, World!\")")``
- ``os.system('echo "print(\"Hello, World!\")" > nefarious.py')``
- ``logging.basicConfig(filename='nefarious.py'); logging.error('print("Hello, World!")')``
- etc.
````

## File: doc/data/messages/e/exec-used/related.rst
````
- `Be careful with exec and eval in Python <https://lucumr.pocoo.org/2011/2/1/exec-in-python/>`_
- `Python documentation <https://docs.python.org/3/library/functions.html#exec>`_
````

## File: doc/data/messages/f/fatal/details.rst
````
This is a message linked to an internal problem in pylint. There's nothing to change in your code.
````

## File: doc/data/messages/f/file-ignored/details.rst
````
There's no checks at all for a file if it starts by ``# pylint: skip-file``.
````

## File: doc/data/messages/f/fixme/details.rst
````
You can use regular expressions and the ``notes-rgx`` option to create some constraints for this message.
See `the following issue <https://github.com/pylint-dev/pylint/issues/2874>`_ for some examples.
````

## File: doc/data/messages/g/global-at-module-level/related.rst
````
- `Official Python FAQ - global and local <https://docs.python.org/3/faq/programming.html#what-are-the-rules-for-local-and-global-variables-in-python>`_
- `PEP 3104 - Access to Names in Outer Scopes <https://peps.python.org/pep-3104/>`_
- `Python global statement <https://docs.python.org/3/reference/simple_stmts.html#global>`_
````

## File: doc/data/messages/i/implicit-str-concat/details.rst
````
By default, detection of implicit string concatenation of line jumps is disabled.
Hence the following code will not trigger this rule:

.. code-block:: python

    SEQ = ('a', 'b'
                'c')

In order to detect this case, you must enable `check-str-concat-over-line-jumps`:

.. code-block:: toml

    [STRING_CONSTANT]
    check-str-concat-over-line-jumps = true

However, the drawback of this setting is that it will trigger false positive
for string parameters passed on multiple lines in function calls:

.. code-block:: python

    warnings.warn(
        "rotate() is deprecated and will be removed in a future release. "
        "Use the rotation() context manager instead.",
        DeprecationWarning,
        stacklevel=3,
    )

No message will be emitted, though, if you clarify the wanted concatenation with parentheses:

.. code-block:: python

    warnings.warn(
        (
            "rotate() is deprecated and will be removed in a future release. "
            "Use the rotation() context manager instead."
        ),
        DeprecationWarning,
        stacklevel=3,
    )
````

## File: doc/data/messages/i/import-error/details.rst
````
This can happen if you're importing a package that is not installed in your environment, or if you made a typo.

The solution is to install the package via pip/setup.py/wheel or fix the typo.
````

## File: doc/data/messages/i/import-private-name/details.rst
````
Using private imports expose you to unexpected breaking changes for any version
bump of your dependencies, even in patch versions.
````

## File: doc/data/messages/i/import-self/details.rst
````
Say you have a file called ``my_file.py``. ``import-self`` would be raised on the following code::


    from my_file import a_function  # [import-self]

    def a_function():
        pass

The solution would be to remove the import::

    def a_function():
        pass
````

## File: doc/data/messages/i/invalid-all-object/details.rst
````
From `The Python Language Reference – The import statement <https://docs.python.org/3/reference/simple_stmts.html#the-import-statement>`_:
    "The `public names` defined by a module are determined by checking the module's namespace for a variable named ``__all__``; if defined, it must be a sequence of strings which are names defined or imported by that module."
````

## File: doc/data/messages/i/invalid-all-object/related.rst
````
- `PEP 8 – Style Guide for Python Code <https://peps.python.org/pep-0008/#module-level-dunder-names>`_
````

## File: doc/data/messages/i/invalid-character-carriage-return/details.rst
````
This message exists because one of our checkers is very generic, but it's never going to
raise during normal use as it's a ``syntax-error`` that would prevent the python ast
(and thus pylint) from constructing a code representation of the file.

You could encounter it by feeding a properly constructed node directly to the checker.
````

## File: doc/data/messages/i/invalid-character-nul/details.rst
````
There's no need to use end-of-string characters. String objects maintain their
own length.
````

## File: doc/data/messages/i/invalid-character-nul/related.rst
````
- `Null terminator in python  <https://stackoverflow.com/a/24410304/2519059>`_
````

## File: doc/data/messages/i/invalid-characters-in-docstring/details.rst
````
This is a message linked to an internal problem in enchant. There's nothing to change in your code,
but maybe in pylint's configuration or the way you installed the 'enchant' system library.
````

## File: doc/data/messages/i/invalid-name/details.rst
````
Pylint recognizes a number of different name types internally. With a few
exceptions, the type of the name is governed by the location the assignment to a
name is found in, and not the type of object assigned.

+--------------------+-------------------------------------------------------------------------------------------------------------+
| Name Type          | Description                                                                                                 |
+====================+=============================================================================================================+
| ``module``         | Module and package names, same as the file names.                                                           |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``const``          | Module-level constants: any name defined at module level that is not bound to a class object nor reassigned.|
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``class``          | Names in ``class`` statements, as well as names bound to class objects at module level.                     |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``function``       | Functions, toplevel or nested in functions or methods.                                                      |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``method``         | Methods, functions defined in class bodies. Includes static and class methods.                              |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``attr``           | Attributes created on class instances inside methods.                                                       |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``argument``       | Arguments to any function type, including lambdas.                                                          |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``variable``       | Local variables in function scopes or module-level names that are assigned multiple times.                  |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``class-attribute``| Attributes defined in class bodies.                                                                         |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``class-const``    | Enum constants and class variables annotated with ``Final``                                                 |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``inlinevar``      | Loop variables in list comprehensions and generator expressions.                                            |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``typevar``        | Type variable declared with ``TypeVar``.                                                                    |
+--------------------+-------------------------------------------------------------------------------------------------------------+
| ``typealias``      | Type alias declared with ``TypeAlias`` or assignments of ``Union``.                                         |
+--------------------+-------------------------------------------------------------------------------------------------------------+

Default behavior
~~~~~~~~~~~~~~~~
By default, Pylint will enforce PEP8_-suggested names.

Predefined Naming Styles
~~~~~~~~~~~~~~~~~~~~~~~~
Pylint provides set of predefined naming styles. Those predefined
naming styles may be used to adjust Pylint configuration to coding
style used in linted project.

Following predefined naming styles are available:

* ``snake_case``
* ``camelCase``
* ``PascalCase``
* ``UPPER_CASE``
* ``any`` - fake style which does not enforce any limitations

The following options are exposed:

.. option:: --module-naming-style=<style>

.. option:: --const-naming-style=<style>

.. option:: --class-naming-style=<style>

.. option:: --function-naming-style=<style>

.. option:: --method-naming-style=<style>

.. option:: --attr-naming-style=<style>

.. option:: --argument-naming-style=<style>

.. option:: --variable-naming-style=<style>

.. option:: --class-attribute-naming-style=<style>

.. option:: --class-const-naming-style=<style>

.. option:: --inlinevar-naming-style=<style>

Predefined Naming Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pylint provides predefined naming patterns for some names. These patterns are often
based on a Naming Style but there is no option to choose one of the styles mentioned above.
The pattern can be overwritten with the options discussed below.

The following types of names are checked with a predefined pattern:

+--------------------+-------------------------------------------------------+------------------------------------------------------------+
| Name type          | Good names                                            | Bad names                                                  |
+====================+=======================================================+============================================================+
| ``typevar``        | ``T``, ``_CallableT``, ``_T_co``, ``AnyStr``,         | ``DICT_T``, ``CALLABLE_T``, ``ENUM_T``, ``DeviceType``,    |
|                    | ``DeviceTypeT``, ``IPAddressT``                       | ``_StrType``                                               |
+--------------------+-------------------------------------------------------+------------------------------------------------------------+
| ``typealias``      | ``GoodName``, ``_GoodName``, ``IPAddressType``,       | ``BadNameT``, ``badName``, ``TBadName``, ``TypeBadName``,  |
|                    |  ``GoodName2`` and other PascalCase variants that     |  ``_1BadName``                                             |
|                    |  don't start with ``T`` or ``Type``. This is to       |                                                            |
|                    |  distinguish them from ``typevars``. Note that        |                                                            |
|                    |  ``TopName`` is allowed but ``TTopName`` isn't.       |                                                            |
+--------------------+-------------------------------------------------------+------------------------------------------------------------+

Before pylint 3.0, most predefined patterns also enforced a minimum length
of three characters. If this behavior is desired in versions 3.0 and following,
it can be had by providing custom regular expressions as described next. (Or,
if the ``disallowed-name`` check is sufficient instead of ``invalid-name``,
providing the single option ``bad-names-rgxs="^..?$"`` will suffice to fail 1-2
character names.

Custom regular expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~

If predefined naming styles are too limited, checker behavior may be further
customized. For each name type, a separate regular expression matching valid
names of this type can be defined. If any of custom regular expressions are
defined, it overrides ``*-naming-style`` option value.

Regular expressions for the names are anchored at the beginning, any anchor for
the end must be supplied explicitly. Any name not matching the regular
expression will lead to an instance of ``invalid-name``.


.. option:: --module-rgx=<regex>

.. option:: --const-rgx=<regex>

.. option:: --class-rgx=<regex>

.. option:: --function-rgx=<regex>

.. option:: --method-rgx=<regex>

.. option:: --attr-rgx=<regex>

.. option:: --argument-rgx=<regex>

.. option:: --variable-rgx=<regex>

.. option:: --class-attribute-rgx=<regex>

.. option:: --class-const-rgx=<regex>

.. option:: --inlinevar-rgx=<regex>

.. option:: --typevar-rgx=<regex>

.. option:: --typealias-rgx=<regex>

Multiple naming styles for custom regular expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Large code bases that have been worked on for multiple years often exhibit an
evolution in style as well. In some cases, modules can be in the same package,
but still have different naming style based on the stratum they belong to.
However, intra-module consistency should still be required, to make changes
inside a single file easier. For this case, Pylint supports regular expression
with several named capturing group.

Rather than emitting name warnings immediately, Pylint will determine the
prevalent naming style inside each module and enforce it on all names.

Consider the following (simplified) example::

   pylint --function-rgx='(?:(?P<snake>[a-z_]+)|(?P<camel>[a-z]+([A-Z][a-z]*)*))$' sample.py

The regular expression defines two naming styles, ``snake`` for snake-case
names, and ``camel`` for camel-case names.

In ``sample.py``, the function name on line 1 and 7 will mark the module
and enforce the match of named group ``snake`` for the remaining names in
the module::

   def valid_snake_case(arg):
      ...

   def InvalidCamelCase(arg):
      ...

   def more_valid_snake_case(arg):
    ...

Because of this, the name on line 4 will trigger an ``invalid-name`` warning,
even though the name matches the given regex.

Matches named ``exempt`` or ``ignore`` can be used for non-tainting names, to
prevent built-in or interface-dictated names to trigger certain naming styles.

.. option:: --name-group=<name1:name2:...,...>

   Default value: empty

   Format: comma-separated groups of colon-separated names.

   This option can be used to combine name styles. For example, ``function:method`` enforces that functions and methods use the same style, and a style triggered by either name type carries over to the other. This requires that the regular expression for the combined name types use the same group names.

Name Hints
~~~~~~~~~~

.. option:: --include-naming-hint=y|n

   Default: off

   Include a hint (regular expression used) for the correct name format with every ``invalid-name`` warning.

.. _PEP8: https://peps.python.org/pep-0008
````

## File: doc/data/messages/i/invalid-sequence-index/details.rst
````
Be careful with ``[True]`` or ``[False]`` as sequence index, since ``True`` and ``False`` will respectively
be evaluated as ``1`` and ``0`` and will bring the second element of the list and the first without erroring.
````

## File: doc/data/messages/i/invalid-slots-object/related.rst
````
- `Documentation for __slots__ <https://docs.python.org/3/reference/datamodel.html#slots>`_
````

## File: doc/data/messages/i/invalid-unicode-codec/details.rst
````
This message is a placeholder for a potential future issue with unicode codecs.
````

## File: doc/data/messages/l/line-too-long/details.rst
````
Pragma controls such as ``# pylint: disable=all`` are not counted toward line length for the purposes of this message.

If you attempt to disable this message via ``# pylint: disable=line-too-long`` in a module with no code, you may receive a message for ``useless-suppression``. This is a false positive of ``useless-suppression`` we can't easily fix.

See https://github.com/pylint-dev/pylint/issues/3368 for more information.
````

## File: doc/data/messages/l/literal-comparison/related.rst
````
- `Comparison operations in Python <https://docs.python.org/3/library/stdtypes.html#comparisons>`_
````

## File: doc/data/messages/l/logging-format-interpolation/details.rst
````
Another reasonable option is to use f-string. If you want to do that, you need to enable
``logging-format-interpolation`` and disable ``logging-fstring-interpolation``.
````

## File: doc/data/messages/l/logging-format-interpolation/related.rst
````
- `logging variable data <https://docs.python.org/3/howto/logging.html#logging-variable-data>`_
- `Rationale for the message on stackoverflow <https://stackoverflow.com/a/34634301/2519059>`_
````

## File: doc/data/messages/l/logging-fstring-interpolation/details.rst
````
This message permits to allow f-string in logging and still be warned of
``logging-format-interpolation``.
````

## File: doc/data/messages/l/logging-fstring-interpolation/related.rst
````
- `logging variable data <https://docs.python.org/3/howto/logging.html#logging-variable-data>`_
- `Rationale <https://stackoverflow.com/questions/34619790>`_
````

## File: doc/data/messages/l/logging-not-lazy/details.rst
````
Another reasonable option is to use f-strings. If you want to do that, you need to enable
``logging-not-lazy`` and disable ``logging-fstring-interpolation``.
````

## File: doc/data/messages/l/logging-not-lazy/related.rst
````
- `Logging variable data <https://docs.python.org/3/howto/logging.html#logging-variable-data>`_
- `Rationale for the message on stackoverflow <https://stackoverflow.com/a/34634301/2519059>`_
````

## File: doc/data/messages/m/method-check-failed/details.rst
````
This is a message linked to an internal problem in pylint. There's nothing to change in your code.
````

## File: doc/data/messages/m/misplaced-future/details.rst
````
A bare raise statement will re-raise the last active exception in the current scope. If the ``raise`` statement is not in an ``except`` or ``finally`` block, a RuntimeError will be raised instead.
````

## File: doc/data/messages/m/missing-final-newline/details.rst
````
The POSIX standard defines a line as:
    "A sequence of zero or more non- <newline> characters plus a terminating <newline> character."
````

## File: doc/data/messages/m/missing-final-newline/related.rst
````
- `POSIX Standard <https://pubs.opengroup.org/onlinepubs/9699919799/>`_
- `POSIX Standard Chapter 3.206 Line <https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap03.html#tag_03_206>`_
````

## File: doc/data/messages/m/missing-format-argument-key/related.rst
````
- `PEP 3101 <https://peps.python.org/pep-3101/>`_
- `Custom String Formatting <https://docs.python.org/3/library/string.html#custom-string-formatting>`_
````

## File: doc/data/messages/m/missing-return-doc/details.rst
````
This message is raised only when parameter ``accept-no-return-doc`` is set to ``no``.
````

## File: doc/data/messages/m/missing-return-type-doc/details.rst
````
This message is raised only when parameter ``accept-no-return-doc`` is set to ``no``.
````

## File: doc/data/messages/m/missing-timeout/details.rst
````
You can add new methods that should have a defined ```timeout`` argument as qualified names
in the ``timeout-methods`` option, for example:

* ``requests.api.get``
* ``requests.api.head``
* ``requests.api.options``
* ``requests.api.patch``
* ``requests.api.post``
* ``requests.api.put``
* ``requests.api.request``
````

## File: doc/data/messages/m/missing-yield-doc/details.rst
````
This message is raised only when parameter ``accept-no-yields-doc`` is set to ``no``.
````

## File: doc/data/messages/m/missing-yield-type-doc/details.rst
````
This message is raised only when parameter ``accept-no-yields-doc`` is set to ``no``.
````

## File: doc/data/messages/m/mixed-line-endings/related.rst
````
- `History of CRLF and LF <https://stackoverflow.com/a/6521730/2519059>`_
- `Dealing with line endings in Git <https://stackoverflow.com/a/10855862/2519059>`_
- `A Collection of Useful .gitattributes Templates <https://github.com/alexkaratarakis/gitattributes>`_
````

## File: doc/data/messages/m/multiple-constructor-doc/details.rst
````
Both docstrings are acceptable but not both at the same time.
````

## File: doc/data/messages/n/no-member/details.rst
````
If you are getting the dreaded ``no-member`` error, there is a possibility that
either:

- pylint found a bug in your code
- You're launching pylint without the dependencies installed in its environment
- pylint would need to lint a C extension module and is refraining to do so
- pylint does not understand dynamically generated code

Linting C extension modules is not supported out of the box, especially since
pylint has no way to get an AST object out of the extension module.

But pylint actually has a mechanism which you might use in case you
want to analyze C extensions. Pylint has a flag, called ``extension-pkg-allow-list``
(formerly ``extension-pkg-whitelist``), through which you can tell it to
import that module and to build an AST from that imported module::

   $ pylint --extension-pkg-allow-list=your_c_extension

Be aware though that using this flag means that extensions are loaded into the
active Python interpreter and may run arbitrary code, which you may not want. This
is the reason why we disable by default loading C extensions. In case you do not want
the hassle of passing C extensions module with this flag all the time, you
can enable ``unsafe-load-any-extension`` in your configuration file, which will
build AST objects from all the C extensions that pylint encounters::

   $ pylint --unsafe-load-any-extension=y

Alternatively, since pylint emits a separate error for attributes that cannot be
found in C extensions, ``c-extension-no-member``, you can disable this error for
your project.

If something is generated dynamically, pylint won't be able to understand the code
from your library (c-extension or not). You can then specify generated attributes
with the ``generated-members`` option. For example if ``cv2.LINE_AA`` and
``sphinx.generated_member`` create false positives for ``no-member``, you can do::

   $ pylint --generated-member=cv2.LINE_AA,sphinx.generated_member
````

## File: doc/data/messages/n/no-self-use/details.rst
````
If a function is not using any class attribute it can be a ``@staticmethod``,
or a function outside the class.
````

## File: doc/data/messages/n/non-ascii-file-name/related.rst
````
- `PEP 489 <https://peps.python.org/pep-0489/#export-hook-name>`_
- `PEP 672 <https://peps.python.org/pep-0672/#confusing-features>`_
- `Python issue 20485 <https://bugs.python.org/issue20485>`_
````

## File: doc/data/messages/n/not-async-context-manager/details.rst
````
Async context manager doesn't implement ``__aenter__`` and ``__aexit__``. It can't be emitted when using Python < 3.5.
````

## File: doc/data/messages/o/overlapping-except/related.rst
````
- `Exception hierarchy <https://docs.python.org/3/library/exceptions.html#exception-hierarchy>`_
````

## File: doc/data/messages/o/overridden-final-method/details.rst
````
The message can't be emitted when using Python < 3.8.
````

## File: doc/data/messages/o/overridden-final-method/related.rst
````
- `PEP 591 <https://peps.python.org/pep-0591/>`_
````

## File: doc/data/messages/p/parse-error/details.rst
````
This is a message linked to an internal problem in pylint. There's nothing to change in your code.
````

## File: doc/data/messages/p/pointless-string-statement/related.rst
````
- `Discussion thread re: docstrings on assignments <https://discuss.python.org/t/docstrings-for-new-type-aliases-as-defined-in-pep-695/39816>`_
````

## File: doc/data/messages/p/positional-only-arguments-expected/related.rst
````
- `PEP 570 <https://peps.python.org/pep-570/>`_
````

## File: doc/data/messages/p/possibly-used-before-assignment/details.rst
````
You can use ``assert_never`` to mark exhaustive choices:

.. sourcecode:: python

    from typing import assert_never

    def handle_date_suffix(suffix):
        if suffix == "d":
            ...
        elif suffix == "m":
            ...
        elif suffix == "y":
            ...
        else:
            assert_never(suffix)

    if suffix in "dmy":
        handle_date_suffix(suffix)

Or, instead of `assert_never()`, you can call a function with a return
annotation of `Never` or `NoReturn`. Unlike in the general case, where
by design pylint ignores type annotations and does its own static analysis,
here, pylint treats these special annotations like a disable comment.

Pylint currently allows repeating the same test like this, even though this
lets some error cases through, as pylint does not assess the intervening code:

.. sourcecode:: python

    if guarded():
        var = 1

    # what if code here affects the result of guarded()?

    if guarded():
        print(var)

But this exception is limited to the repeating the exact same test.
This warns:

.. sourcecode:: python

    if guarded():
        var = 1

    if guarded() or other_condition:
        print(var)  # [possibly-used-before-assignment]

If you find this surprising, consider that pylint, as a static analysis
tool, does not know if ``guarded()`` is deterministic or talks to
a database. For variables (e.g. ``guarded`` versus ``guarded()``),
this is less of an issue, so in this case,
``possibly-used-before-assignment`` acts more like a future-proofing style
preference than an error, per se.
````

## File: doc/data/messages/p/prefer-typing-namedtuple/related.rst
````
- `typing.NamedTuple <https://docs.python.org/3/library/typing.html#typing.NamedTuple>`_
````

## File: doc/data/messages/r/raise-missing-from/related.rst
````
- `PEP 3134 <https://peps.python.org/pep-3134/>`_
````

## File: doc/data/messages/r/raw-checker-failed/details.rst
````
This warns you that a builtin module was impossible to analyse (an ast node is not pure python).
There's nothing to change in your code, this is a warning about astroid and pylint's limitations.
````

## File: doc/data/messages/r/redefined-builtin/details.rst
````
The :ref:`allowed-redefined-builtins <variables-options>` option lets you specify names that are permitted to shadow built-ins.

However, this option is not effective for redefinitions at the module level or for global variables. For example:

Module-Level Redefinitions::

    # module_level_redefine.py
    id = 1  # Shadows the built-in `id`

Global Variable Redefinitions::

    # global_variable_redefine.py
    def my_func():
        global len
        len = 1  # Shadows the built-in `len`

Rationale:

Shadowing built-ins at the global scope is discouraged because it obscures their behavior
throughout the entire module, increasing the risk of subtle bugs when the built-in is needed elsewhere.
In contrast, local redefinitions are acceptable as their impact is confined to a specific scope,
reducing unintended side effects and simplifying debugging.
````

## File: doc/data/messages/r/redefined-outer-name/details.rst
````
A common issue is that this message is triggered when using `pytest` `fixtures <https://docs.pytest.org/en/7.1.x/how-to/fixtures.html>`_:

.. code-block:: python

    import pytest

    @pytest.fixture
    def setup():
        ...


    def test_something(setup):  # [redefined-outer-name]
        ...

One solution to this problem is to explicitly name the fixture:

.. code-block:: python

    @pytest.fixture(name="setup")
    def setup_fixture():
        ...

Alternatively `pylint` plugins like `pylint-pytest <https://pypi.org/project/pylint-pytest/>`_ can be used.
````

## File: doc/data/messages/r/redundant-unittest-assert/details.rst
````
Directly asserting a string literal will always pass. The solution is to
test something that could fail, or not assert at all.

For assertions using ``assert`` there are similar messages: :ref:`assert-on-string-literal` and :ref:`assert-on-tuple`.
````

## File: doc/data/messages/r/redundant-unittest-assert/related.rst
````
- `Tests without assertion <https://stackoverflow.com/a/137418/2519059>`_
- `Testing that there is no error raised <https://stackoverflow.com/questions/20274987>`_
- `Parametrizing conditional raising <https://docs.pytest.org/en/latest/example/parametrize.html#parametrizing-conditional-raising>`_
````

## File: doc/data/messages/r/relative-beyond-top-level/details.rst
````
Absolute imports were strongly preferred, historically. Relative imports allow you
to reorganize packages without changing any code, but these days refactoring tools and IDEs
allow you to do that at almost no cost anyway if the imports are explicit/absolute.
Therefore, absolute imports are often still preferred over relative ones.
````

## File: doc/data/messages/r/relative-beyond-top-level/related.rst
````
- `Absolute vs. explicit relative import of Python module  <https://stackoverflow.com/a/16748366/2519059>`_
- `Withdraw anti-recommendation of relative imports from documentation <https://bugs.python.org/msg118031>`_
````

## File: doc/data/messages/r/return-arg-in-generator/details.rst
````
This is a message that isn't going to be raised for python > 3.3. It was raised
for code like::

    def interrogate_until_you_find_jack(pirates):
        for pirate in pirates:
            if pirate == "Captain Jack Sparrow":
                return "Arrr! We've found our captain!"
            yield pirate

Which is now valid and equivalent to the previously expected::

    def interrogate_until_you_find_jack(pirates):
        for pirate in pirates:
            if pirate == "Captain Jack Sparrow":
                raise StopIteration("Arrr! We've found our captain!")
            yield pirate
````

## File: doc/data/messages/r/return-arg-in-generator/related.rst
````
- `PEP380 <https://peps.python.org/pep-0380/>`_
- `Stackoverflow explanation <https://stackoverflow.com/a/16780113/2519059>`_
````

## File: doc/data/messages/r/return-in-finally/related.rst
````
- `Python 3 docs 'finally' clause <https://docs.python.org/3/reference/compound_stmts.html#finally-clause>`_
- `PEP 765 - Disallow return/break/continue that exit a finally block <https://peps.python.org/pep-0765/>`_
````

## File: doc/data/messages/r/return-in-init/related.rst
````
- `__init__ method documentation <https://docs.python.org/3/reference/datamodel.html#object.__init__>`_
````

## File: doc/data/messages/s/self-assigning-variable/related.rst
````
- `Python assignment statement <https://docs.python.org/3/reference/simple_stmts.html#assignment-statements>`_
````

## File: doc/data/messages/s/simplifiable-if-expression/related.rst
````
- `Simplifying an 'if' statement with bool() <https://stackoverflow.com/questions/49546992/>`_
````

## File: doc/data/messages/s/singleton-comparison/related.rst
````
- `PEP 285 – Adding a bool type <https://peps.python.org/pep-0285/>`_
````

## File: doc/data/messages/s/stop-iteration-return/details.rst
````
It's possible to give a default value to ``next`` or catch the ``StopIteration``,
or return directly. A ``StopIteration`` cannot be propagated from a generator.
````

## File: doc/data/messages/s/stop-iteration-return/related.rst
````
- `PEP 479 <https://peps.python.org/pep-0479/>`_
````

## File: doc/data/messages/s/subclassed-final-class/details.rst
````
This message is emitted when a class which is decorated with `final` is subclassed; the decorator indicates that the class is not intended to be extended.

Note this message can't be emitted when using Python < 3.8.
````

## File: doc/data/messages/s/subclassed-final-class/related.rst
````
- `PEP 591 <https://peps.python.org/pep-0591/#the-final-decorator>`_
````

## File: doc/data/messages/s/subprocess-run-check/related.rst
````
- `subprocess.run documentation <https://docs.python.org/3/library/subprocess.html#subprocess.run>`_
````

## File: doc/data/messages/s/suppressed-message/details.rst
````
``suppressed-message`` is simply a way to see messages that would be raised
without the disable in your codebase. It should not be activated most
of the time. See also ``useless-suppression`` if you want to see the message
that are disabled for no reasons.
````

## File: doc/data/messages/s/syntax-error/details.rst
````
The python's ast builtin module cannot parse your code if there's a syntax error, so
if there's a syntax error other messages won't be available at all.
````

## File: doc/data/messages/s/syntax-error/related.rst
````
- `Why can't pylint recover from a syntax error ? <https://stackoverflow.com/a/78419051/2519059>`_
````

## File: doc/data/messages/t/too-few-format-args/related.rst
````
- `String Formatting <https://docs.python.org/3/library/string.html#formatstrings>`_
````

## File: doc/data/messages/t/too-many-format-args/related.rst
````
- `String Formatting <https://docs.python.org/3/library/string.html#formatstrings>`_
````

## File: doc/data/messages/t/too-many-lines/details.rst
````
When a module has too many lines it can make it difficult to read and understand. There might be
performance issue while editing the file because the IDE must parse more code. You need more expertise
to navigate the file properly (go to a particular line when debugging, or search for a specific code construct, instead of navigating by clicking and scrolling)

This measure is a proxy for higher cyclomatic complexity that you might not be calculating if you're not using ``load-plugins=pylint.extensions.mccabe,``. Cyclomatic complexity is slower to compute, but also a more fine grained measure than raw SLOC. In particular, you can't make the code less readable by making a very complex one liner if you're using cyclomatic complexity.

The example simplify the code, but it's not always possible. Most of the time bursting the file
by creating a package with the same API is the only solution. Anticipating and creating the file
from the get go will permit to have the same end result with a better version control history.
````

## File: doc/data/messages/t/too-many-locals/details.rst
````
Having too many locals may indicate that you're doing too much in a function and that
classes regrouping some attributes could be created. Maybe operations could be separated in
multiple functions. Are all your variables really closely related ?
````

## File: doc/data/messages/t/too-many-positional-arguments/details.rst
````
Good function signatures don’t have many positional parameters. For almost all
interfaces, comprehensibility suffers beyond a handful of arguments.

Positional arguments work well for cases where the the use cases are
self-evident, such as unittest's ``assertEqual(first, second, "assert msg")``
or ``zip(fruits, vegetables)``.

There are a few exceptions where four or more positional parameters make sense,
for example ``rgba(1.0, 0.5, 0.3, 1.0)``, because it uses a very well-known and
well-established convention, and using keywords all the time would be a waste
of time.
````

## File: doc/data/messages/t/too-many-positional-arguments/related.rst
````
- `Special parameters in python <https://docs.python.org/3/tutorial/controlflow.html#special-parameters>`_
````

## File: doc/data/messages/t/too-many-public-methods/details.rst
````
Having too many public methods is an indication that you might not be respecting
the Single-responsibility principle (S of SOLID).

The class should have only one reason to change, but in the example the
spaceship has at least 4 persons that could ask for change to it
(laser manager, shield manager, missile manager, teleportation officer...).
````

## File: doc/data/messages/t/too-many-public-methods/related.rst
````
- `Single-responsibility principle <https://en.wikipedia.org/wiki/Single-responsibility_principle>`_
````

## File: doc/data/messages/t/try-except-raise/details.rst
````
There is a legitimate use case for re-raising immediately. E.g. with the following inheritance tree::

    +-- ArithmeticError
         +-- FloatingPointError
         +-- OverflowError
         +-- ZeroDivisionError

The following code shows valid case for re-raising exception immediately::

    def execute_calculation(a, b):
        try:
            return some_calculation(a, b)
        except ZeroDivisionError:
            raise
        except ArithmeticError:
            return float('nan')

The pylint is able to detect this case and does not produce error.
````

## File: doc/data/messages/t/typevar-name-incorrect-variance/details.rst
````
When naming type vars, only use a ``_co`` suffix when indicating covariance or ``_contra`` when indicating contravariance.
````

## File: doc/data/messages/u/unbalanced-tuple-unpacking/related.rst
````
- `PEP 3132 - Extended Iterable Unpacking <https://peps.python.org/pep-3132/>`_
````

## File: doc/data/messages/u/undefined-all-variable/related.rst
````
- `Importing * From a Package <https://docs.python.org/3/tutorial/modules.html#importing-from-a-package>`_
````

## File: doc/data/messages/u/unexpected-line-ending-format/related.rst
````
- `History of CRLF and LF <https://stackoverflow.com/a/6521730/2519059>`_
- `Dealing with line endings in Git <https://stackoverflow.com/a/10855862/2519059>`_
- `A Collection of Useful .gitattributes Templates <https://github.com/alexkaratarakis/gitattributes>`_
````

## File: doc/data/messages/u/unidiomatic-typecheck/related.rst
````
- `Builtin function type() <https://docs.python.org/3/library/functions.html#type>`_
- `Builtin function isinstance() <https://docs.python.org/3/library/functions.html#isinstance>`_
````

## File: doc/data/messages/u/unnecessary-default-type-args/details.rst
````
At the moment, this check only works for ``Generator`` and ``AsyncGenerator``.

Starting with Python 3.13, the ``SendType`` and ``ReturnType`` default to ``None``.
As such it's no longer necessary to specify them. The ``collections.abc`` variants
don't validate the number of type arguments. Therefore the defaults for these
can be used in earlier versions as well.
````

## File: doc/data/messages/u/unnecessary-default-type-args/related.rst
````
- `Python documentation for AsyncGenerator <https://docs.python.org/3.13/library/typing.html#typing.AsyncGenerator>`_
- `Python documentation for Generator <https://docs.python.org/3.13/library/typing.html#typing.Generator>`_
````

## File: doc/data/messages/u/unnecessary-dunder-call/related.rst
````
- `Define dunder methods but don't call them directly <https://www.pythonmorsels.com/avoid-dunder-methods/>`_
````

## File: doc/data/messages/u/unrecognized-option/details.rst
````
One of your options is not recognized. There's nothing to change in
your code, but your pylint configuration or the way you launch
pylint needs to be modified.

For example, this message would be raised when invoking pylint with
``pylint --unknown-option=yes test.py``. Or you might be launching
pylint with the following ``toml`` configuration::

    [tool.pylint]
    jars = "10"

When the following should be used::

    [tool.pylint]
    jobs = "10"

This warning was released in pylint 2.14: bad options were silently failing before.
````

## File: doc/data/messages/u/unused-import/details.rst
````
By default, this check is skipped for ``__init__.py`` files, as they often contain imports from submodules for the convenience of end users. While these imports are not used within ``__init__.py``, they serve the purpose of providing intuitive import paths for the module's important classes and constants.
````

## File: doc/data/messages/u/unused-import/related.rst
````
- :ref:`--init-import <variables-options>`
````

## File: doc/data/messages/u/unused-wildcard-import/detail.rst
````
Either remove the wildcard import, make use of every object from the wildcard import, or only import the required objects.
````

## File: doc/data/messages/u/use-a-generator/details.rst
````
By using a generator you can cut the execution tree and exit directly at the first element that is ``False`` for ``all`` or ``True`` for ``any`` instead of
calculating all the elements. Except in the worst possible case where you still need to evaluate everything (all values
are True for ``all`` or all values are false for ``any``) performance will be better.
````

## File: doc/data/messages/u/use-a-generator/related.rst
````
- `PEP 289 – Generator Expressions <https://peps.python.org/pep-0289/>`_
- `Benchmark and discussion during initial implementation <https://github.com/pylint-dev/pylint/pull/3309#discussion_r576683109>`_
````

## File: doc/data/messages/u/use-dict-literal/details.rst
````
https://gist.github.com/hofrob/ad143aaa84c096f42489c2520a3875f9

This example script shows an 18% increase in performance when using a literal over the
constructor in python version 3.10.6.
````

## File: doc/data/messages/u/use-dict-literal/related.rst
````
- `Performance Analysis of Python’s dict() vs dict literal <https://madebyme.today/blog/python-dict-vs-curly-brackets/>`_
````

## File: doc/data/messages/u/use-maxsplit-arg/details.rst
````
Be aware that the performance improvement from not splitting the string
so many times will only be realized in cases presenting more instances of
the splitting character than the minimal example here.
````

## File: doc/data/messages/u/use-sequence-for-iteration/details.rst
````
https://gist.github.com/hofrob/8b1c1e205a0d4c66a680b1fe4bfeba11

This example script shows a significant increase in performance when using a list, tuple or range over a set in python version 3.11.1.
````

## File: doc/data/messages/u/use-yield-from/details.rst
````
:code:`yield from` can be thought of as removing the intermediary (your for loop) between the function caller and the
requested generator. This enables the caller to directly communicate with the generator (e.g. using :code:`send()`).
This communication is not possible when manually yielding each element one by one in a loop.

PEP 380 describes the possibility of adding optimizations specific to :code:`yield from`. It looks like they
have not been implemented as of the time of writing. Even without said optimizations, the following snippet shows
that :code:`yield from` is marginally faster.

.. code-block:: sh

  $ python3 -m timeit "def yield_from(): yield from range(100)" "for _ in yield_from(): pass"
  100000 loops, best of 5: 2.44 usec per loop
  $ python3 -m timeit "def yield_loop():" "    for item in range(100): yield item" "for _ in yield_loop(): pass"
  100000 loops, best of 5: 2.49 usec per loop
````

## File: doc/data/messages/u/use-yield-from/related.rst
````
- `PEP 380 <https://peps.python.org/pep-0380/>`_
````

## File: doc/data/messages/u/useless-import-alias/details.rst
````
Known issue
-----------

If you prefer to use "from-as" to explicitly reexport in API (``from fruit import orange as orange``)
instead of using ``__all__`` this message will be a false positive.

Use ``--allow-reexport-from-package`` to allow explicit reexports by alias
in package ``__init__`` files.
````

## File: doc/data/messages/u/useless-import-alias/related.rst
````
- :ref:`--allow-reexport-from-package<imports-options>`
- `PEP 8, Import Guideline <https://peps.python.org/pep-0008/#imports>`_
- :ref:`Pylint block-disable <block_disables>`
- `mypy --no-implicit-reexport <https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-no-implicit-reexport>`_
````

## File: doc/data/messages/u/useless-option-value/details.rst
````
You can disable this check if you don't want to cleanup your configuration of old messages.
````

## File: doc/data/messages/u/useless-parent-delegation/related.rst
````
- `Stackoverflow explanation for 'useless-super-delegation' <https://stackoverflow.com/a/51030674/2519059>`_
````

## File: doc/data/messages/u/using-assignment-expression-in-unsupported-version/details.rst
````
The assignment expression (walrus) operator (`:=`) was introduced in Python 3.8; to use it, please use a more recent version of Python.
````

## File: doc/data/messages/u/using-exception-groups-in-unsupported-version/details.rst
````
Exception groups were introduced in Python 3.11; to use it, please use a more recent version of Python.
````

## File: doc/data/messages/u/using-f-string-in-unsupported-version/details.rst
````
f-strings were introduced in Python version 3.6; to use them, please use a more recent version of Python.
````

## File: doc/data/messages/u/using-final-decorator-in-unsupported-version/details.rst
````
The message is emitted when the ``final`` decorator is used with a Python version less than 3.8.
The ``final`` decorator was introduced in Python version 3.8.
````

## File: doc/data/messages/u/using-final-decorator-in-unsupported-version/related.rst
````
- `PEP 591 <https://peps.python.org/pep-0591/#the-final-decorator>`_
````

## File: doc/data/messages/u/using-generic-type-syntax-in-unsupported-version/details.rst
````
Generic type syntax was introduced in Python 3.12; to use it, please use a more recent version of Python.
````

## File: doc/data/messages/u/using-positional-only-args-in-unsupported-version/details.rst
````
Positional-only arguments were introduced in Python 3.8; to use them, please use a more recent version of Python.
````

## File: doc/data/messages/w/while-used/related.rst
````
- `Stackoverflow discussion <https://stackoverflow.com/questions/920645/when-to-use-while-or-for-in-python>`_
````

## File: doc/data/messages/y/yield-inside-async-function/details.rst
````
The message can't be emitted when using Python < 3.5.
````

## File: doc/data/messages/y/yield-inside-async-function/related.rst
````
- `PEP 525 <https://peps.python.org/pep-0525/>`_
````

## File: doc/development_guide/api/index.rst
````
###
API
###

You can call ``Pylint``, ``symilar`` and ``pyreverse`` from another
Python program thanks to their APIs:

.. sourcecode:: python

    from pylint import run_pylint, run_pyreverse, run_symilar

    run_pylint("--disable=C", "myfile.py")
    run_pyreverse(...)
    run_symilar(...)


.. toctree::
  :maxdepth: 1
  :hidden:

  pylint
````

## File: doc/development_guide/api/pylint.rst
````
=======
 Pylint
=======

As you would launch the command line
------------------------------------

You can use the ``run_pylint`` function, which is the same function
called by the command line (using ``sys.argv``). You can supply
arguments yourself:

.. sourcecode:: python

    from pylint import run_pylint

    run_pylint(argv=["--disable=line-too-long", "myfile.py"])


Recover the result in a stream
------------------------------

You can also use ``pylint.lint.Run`` directly if you want to do something that
can't be done using only pylint's command line options. Here's the basic example:

.. sourcecode:: python

    from pylint.lint import Run

    Run(argv=["--disable=line-too-long", "myfile.py"])

With ``Run`` it is possible to invoke pylint programmatically with a
reporter initialized with a custom stream:

.. sourcecode:: python

    from io import StringIO

    from pylint.lint import Run
    from pylint.reporters.text import TextReporter

    pylint_output = StringIO()  # Custom open stream
    reporter = TextReporter(pylint_output)
    Run(["test_file.py"], reporter=reporter, exit=False)
    print(pylint_output.getvalue())  # Retrieve and print the text report

The reporter can accept any stream object as as parameter. In this example,
the stream outputs to a file:

.. sourcecode:: python

    from pylint.lint import Run
    from pylint.reporters.text import TextReporter

    with open("report.out", "w") as f:
        reporter = TextReporter(f)
        Run(["test_file.py"], reporter=reporter, exit=False)

This would be useful to capture pylint output in an open stream which
can be passed onto another program.

If your program expects that the files being linted might be edited
between runs, you will need to clear pylint's inference cache:

.. sourcecode:: python

    from pylint.lint import pylinter
    pylinter.MANAGER.clear_cache()
````

## File: doc/development_guide/contributor_guide/tests/index.rst
````
.. _contributor_testing:
.. _test_your_code:

==============
Testing pylint
==============

Pylint is very well tested and has a high code coverage. New contributions are not accepted
unless they include tests.

.. toctree::
   :maxdepth: 3
   :titlesonly:

   install
   launching_test
   writing_test
````

## File: doc/development_guide/contributor_guide/tests/install.rst
````
.. _contributor_install:

Contributor installation
========================

Basic installation
------------------

Pylint is developed using the git_ distributed version control system.

You can clone Pylint using ::

  git clone https://github.com/pylint-dev/pylint

Before you start testing your code, you need to install your source-code package locally.
Suppose you just cloned pylint with the previous ``git clone`` command. To set up your
environment for testing, open a terminal and run::

    cd pylint
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements_test_min.txt
    pip install -e .

This ensures your testing environment is similar to Pylint's testing environment on GitHub.

**Optionally** (Because there's an auto-fix if you open a merge request): We have
pre-commit hooks which should take care of the autoformatting for you before each
commit. To enable it, run ``pre-commit install`` in the ``pylint`` root directory.

Astroid installation
--------------------

If you're testing new changes in astroid you need to also clone astroid_ and install
with an editable installation alongside pylint as follows::

    # Suppose you're in the pylint directory
    git clone https://github.com/pylint-dev/astroid.git
    python3 -m pip install -e astroid/

You're now using the local astroid in pylint and can control the version with git for example::

    cd astroid/
    git switch my-astroid-dev-branch

.. _pytest-cov: https://pypi.org/project/pytest-cov/
.. _astroid: https://github.com/pylint-dev/astroid
.. _git: https://git-scm.com/
````

## File: doc/development_guide/contributor_guide/tests/launching_test.rst
````
Launching tests
===============

pytest
------

Since we use pytest_ to run the tests, you can also use it on its own.
We do recommend using the tox_ command though::

    pytest tests/ -k test_functional

You can use pytest_ directly. If you want to run tests on a specific portion of the
code with pytest_ and your local python version::

    python3 -m pytest


Everything in tests/message with coverage for the relevant code (require `pytest-cov`_)::

    python3 -m pytest tests/message/ --cov=pylint.message
    coverage html

Only the functional test "missing_kwoa_py3"::

    python3 -m pytest "tests/test_functional.py::test_functional[missing_kwoa_py3]"

tox
---

You can also *optionally* install tox_ and run our tests using the tox_ package, as in::

    python -m tox
    python -m tox -epy313 # for Python 3.13 suite only
    python -m tox -epylint # for running Pylint over Pylint's codebase
    python -m tox -eformatting # for running formatting checks over Pylint's codebase

It's usually a good idea to run tox_ with ``--recreate``. This flag tells tox_ to re-download
all dependencies before running the tests. This can be important when a new version of
astroid_ or any of the other dependencies has been published::

    python -m tox --recreate # The entire tox environment will be recreated
    python -m tox --recreate -e py310 # The python 3.10 tox environment will be recreated


To run only a specific test suite, use a pattern for the test filename
(**without** the ``.py`` extension), as in::

    python -m tox -e py310 -- -k test_functional
    python -m tox -e py310 -- -k  \*func\*
    python -m tox --recreate -e py310 -- -k test_functional # With recreation of the environment


.. _primer_tests:

Primer tests
------------

Pylint also uses what we refer to as ``primer`` tests. These are tests that are run automatically
in our Continuous Integration and check whether any changes in Pylint lead to crashes or fatal errors
on the ``stdlib``, and also assess a pull request's impact on the linting of a selection of external
repositories by posting the diff against ``pylint``'s current output as a comment.

To run the primer test for the ``stdlib``, which only checks for crashes and fatal errors, you can add
``--primer-stdlib`` to the pytest_ command. For example::

    pytest -m primer_stdlib --primer-stdlib

To produce the output generated on Continuous Integration for the linting of external repositories,
run these commands::

    python tests/primer/__main__.py prepare --clone
    python tests/primer/__main__.py run --type=pr

To fully simulate the process on Continuous Integration, you should then checkout ``main``, and
then run these commands::

    python tests/primer/__main__.py run --type=main
    python tests/primer/__main__.py compare

The list of repositories is created on the basis of three criteria: 1) projects need to use a diverse
range of language features, 2) projects need to be well maintained and 3) projects should not have a codebase
that is too repetitive. This guarantees a good balance between speed of our CI and finding potential bugs.

You can find the latest list of repositories and any relevant code for these tests in the ``tests/primer``
directory.

.. _pytest-cov: https://pypi.org/project/pytest-cov/
.. _astroid: https://github.com/pylint-dev/astroid
````

## File: doc/development_guide/contributor_guide/tests/writing_test.rst
````
.. _writing_tests:

Writing tests
=============

Pylint uses three types of tests: unittests, functional tests and primer tests.

- :ref:`unittests <writing_unittests>` can be found in ``pylint/tests``. Unless you're working on pylint's
  internal you're probably not going to have to write any.
- :ref:`Global functional tests <writing_functional_tests>`  can be found in the ``pylint/tests/functional``. They are
  mainly used to test whether Pylint emits the correct messages.
- :ref:`Configuration's functional tests <writing_config_functional_tests>`  can be found in the
  ``pylint/tests/config/functional``. They are used to test Pylint's configuration loading.
- :ref:`Primer tests <primer_tests>` you can suggest a new external repository to check but there's nothing to do
  most of the time.

.. _writing_unittests:

Unittest tests
--------------

Most other tests reside in the '/pylint/test' directory. These unittests can be used to test
almost all functionality within Pylint. A good step before writing any new unittests is to look
at some tests that test a similar functionality. This can often help write new tests.

If your new test requires any additional files you can put those in the
``/pylint/test/regrtest_data`` directory. This is the directory we use to store any data needed for
the unittests.



.. _writing_functional_tests:

Functional tests
----------------

These are located under ``/pylint/test/functional`` and they are formed of multiple
components. First, each Python file is considered to be a test case and it
should be accompanied by a ``.txt`` file, having the same name. The ``.txt`` file contains the ``pylint`` messages
that are supposed to be emitted by the given test file.

In your ``.py`` test file, each line for which Pylint is supposed to emit a message
has to be annotated with a comment following this pattern ``# [message_symbol]``, as in::

    a, b, c = 1 # [unbalanced-tuple-unpacking]

If multiple messages are expected on the same line, then this syntax can be used::

    a, b, c = 1.test # [unbalanced-tuple-unpacking, no-member]

You can also use  ``# +n: [`` where ``n`` is an integer to deal with special cases, e.g., where the above regular syntax makes the line too long::

    A = 5
    # +1: [singleton-comparison]
    B = A == None  # The test will look for the `singleton-comparison` message in this line

If you need special control over Pylint's configuration, you can also create a ``.rc`` file, which
can set sections of Pylint's configuration.
The ``.rc`` file can also contain a section ``[testoptions]`` to pass options for the functional
test runner. The following options are currently supported:

- "min_pyver": Minimal python version required to run the test
- "max_pyver": Python version from which the test won't be run. If the last supported version is 3.9 this setting should be set to 3.10.
- "min_pyver_end_position": Minimal python version required to check the end_line and end_column attributes of the message
- "requires": Packages required to be installed locally to run the test
- "except_implementations": List of python implementations on which the test should not run
- "exclude_platforms": List of operating systems on which the test should not run

**Different output for different Python versions**

Sometimes the linting result can change between Python releases. In these cases errors can be marked as conditional.
Supported operators are ``<``, ``<=``, ``>`` and ``>=``.

.. code-block:: python

    def some_func() -> X:  # <3.14:[undefined-variable]
      ...

    # It can also be combined with offsets
    # +1:<3.14:[undefined-variable]
    def some_other_func() -> X:
      ...

    class X: ...

Since the output messages are different, it is necessary to add two separate files for it.
First ``<test-file-name>.314.txt``, this will include the output messages for ``>=3.14``, i.e. should be empty here.
Second ``<test-file-name>.txt``, this will be the default for all other Python versions.

.. note::

    This does only work if the code itself is parsable in all tested Python versions.
    For new syntax, use ``min_pyver`` / ``max_pyver`` instead.

**Functional test file locations**

For existing checkers, new test cases should preferably be appended to the existing test file.
For new checkers, a new file ``new_checker_message.py`` should be created (Note the use of
underscores). This file should then be placed in the ``test/functional/n`` sub-directory.

Some additional notes:

- If the checker is part of an extension the test should go in ``test/functional/ext/extension_name``
- If the test is a regression test it should go in ``test/r/regression`` or ``test/r/regression_02``.
  The file name should start with ``regression_``.
- For some sub-directories, such as ``test/functional/u``, there are additional sub-directories (``test/functional/u/use``).
  Please check if your test file should be placed in any of these directories. It should be placed there
  if the sub-directory name matches the word before the first underscore of your test file name.

The folder structure is enforced when running the test suite, so you might be directed to put the file
in a different sub-directory.

**Running and updating functional tests**

During development, it's sometimes helpful to run all functional tests in your
current environment in order to have faster feedback. Run from Pylint root directory with::

    python tests/test_functional.py

You can use all the options you would use for pytest_, for example ``-k "test_functional[len_checks]"``.
Furthermore, if required the .txt file with expected messages can be regenerated based
on the the current output by appending ``--update-functional-output`` to the command line::

    python tests/test_functional.py --update-functional-output -k "test_functional[len_checks]"


.. _writing_config_functional_tests:

Functional tests for configurations
-----------------------------------

To test the different ways to configure Pylint there is also a small functional test framework
for configuration files. These tests can be found in the '/pylint/test/config' directory.

To create a new test create a new file with an unused name in the directory of that type
of configuration file. Subsequently add a ``filename.result.json`` file with 'filename'
being the same name as your configuration file. This file should record
what the configuration should be **compared to the standard configuration**.

For example, if the configuration should add a warning to the list of disabled messages
and you changed the configuration for ``job`` to 10 instead of the default 1 the
``.json`` file should include::

    "functional_append": {
        "disable": [["a-message-to-be-added"],]
    }
    "jobs": 10,

Similarly if a message should be removed you can add the following to the ``.json`` file::

    "functional_remove": {
        "disable": [["a-message-to-be-removed"],]
    }

If a configuration is incorrect and should lead to a crash or warning being emitted you can
specify this by adding a ``.out`` file. This file should have the following name
``name_of_configuration_testfile.error_code.out``. So, if your test is called ``bad_configuration.toml``
and should exit with exit code 2 the ``.out`` file should be named ``bad_configuration.2.out``.
The content of the ``.out`` file should have a similar pattern as a normal Pylint output. Note that the
module name should be ``{abspath}`` and the file name ``{relpath}``.


.. _tox: https://tox.wiki/en/latest/
.. _pytest: https://docs.pytest.org/en/latest/
.. _pytest-cov: https://pypi.org/project/pytest-cov/
.. _astroid: https://github.com/pylint-dev/astroid
````

## File: doc/development_guide/contributor_guide/contribute.rst
````
==============
 Contributing
==============

.. _repository:

Finding something to do
-----------------------

Want to contribute to pylint? There's a lot of things you can do.
Here's a list of links you can check depending on what you want to do:

- `Asking a question on discord`_, or `on github`_
- `Opening an issue`_
- `Making the documentation better`_
- `Making the error message better`_
- `Reproducing bugs and confirming that issues are valid`_
- `Investigating or debugging complicated issues`_
- `Designing or specifying a solution`_
- `Giving your opinion on ongoing discussion`_
- `Fixing bugs and crashes`_
- `Fixing false positives`_
- `Creating new features or fixing false negatives`_
- `Reviewing pull requests`_

.. _`Asking a question on discord`: https://discord.com/invite/qYxpadCgkx
.. _`on github`: https://github.com/pylint-dev/pylint/issues/new/choose
.. _`Opening an issue`: https://github.com/pylint-dev/pylint/issues/new?assignees=&labels=Needs+triage+%3Ainbox_tray%3A&template=BUG-REPORT.yml
.. _`Making the documentation better`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Documentation+%3Agreen_book%3A%22
.. _`Making the error message better`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen%20is%3Aissue%20project%3Apylint-dev%2Fpylint%2F4
.. _`Reproducing bugs and confirming that issues are valid`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Needs+reproduction+%3Amag%3A%22%2C%22Cannot+reproduce+%F0%9F%A4%B7%22
.. _`Investigating or debugging complicated issues`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Needs+investigation+%F0%9F%94%AC%22
.. _`Designing or specifying a solution`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Needs+design+proposal+%3Alock%3A%22%2C%22Needs+specification+%3Aclosed_lock_with_key%3A%22
.. _`Giving your opinion on ongoing discussion`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Needs+decision+%3Alock%3A%22
.. _`Fixing bugs and crashes`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Bug+%3Abeetle%3A%22%2C%22Crash+%F0%9F%92%A5%22
.. _`Fixing false positives`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22False+Positive+%F0%9F%A6%9F%22
.. _`Creating new features or fixing false negatives`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22False+Negative+%F0%9F%A6%8B%22%2C%22Enhancement+%E2%9C%A8%22
.. _`Reviewing pull requests`: https://github.com/pylint-dev/pylint/pulls?q=is%3Aopen+is%3Apr+label%3A%22Needs+review+%F0%9F%94%8D%22


If you are a pylint maintainer there's also:

- `Triaging issues`_
- `Labeling issues that do not have an actionable label yet`_
- `Preparing the next patch release`_
- `Checking stale pull requests status`_

.. _`Triaging issues`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Needs+triage+%3Ainbox_tray%3A%22
.. _`Labeling issues that do not have an actionable label yet`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+-label%3A%22Needs+astroid+Brain+%F0%9F%A7%A0%22+-label%3A%22Needs+astroid+update%22+-label%3A%22Needs+backport%22+-label%3A%22Needs+decision+%3Alock%3A%22+-label%3A%22Needs+investigation+%F0%9F%94%AC%22+-label%3A%22Needs+PR%22+-label%3A%22Needs+reproduction+%3Amag%3A%22+-label%3A%22Needs+review+%F0%9F%94%8D%22+-label%3A%22Needs+triage+%3Ainbox_tray%3A%22+-label%3A%22Waiting+on+author%22+-label%3A%22Work+in+progress%22+-label%3AMaintenance+sort%3Aupdated-desc+-label%3A%22Needs+specification+%3Aclosed_lock_with_key%3A%22+-label%3A%22Needs+design+proposal+%3Alock%3A%22
.. _`Preparing the next patch release`: https://github.com/pylint-dev/pylint/issues?q=is%3Aopen+is%3Aissue+label%3A%22Needs+backport%22
.. _`Checking stale pull requests status`: https://github.com/pylint-dev/pylint/pulls?q=is%3Aopen+is%3Apr+label%3A%22Work+in+progress%22%2C%22Needs+astroid+update%22%2C%22Waiting+on+author%22


Creating a pull request
-----------------------

Got a change for Pylint?  Below are a few steps you should take to make sure
your patch gets accepted:

- You must use at least Python 3.8 for development of Pylint as it gives
  you access to the latest ``ast`` parser and some pre-commit hooks do not
  support python 3.7.

- Install the dev dependencies, see :ref:`contributor_install`.

- Use our test suite and write new tests, see :ref:`contributor_testing`.

.. keep this in sync with the description of PULL_REQUEST_TEMPLATE.md!

- Document your change, if it is a non-trivial one:

  * A maintainer might label the issue ``skip-news`` if the change does not need to be in the changelog.
  * Otherwise, create a news fragment with ``towncrier create <IssueNumber>.<type>`` which will be
    included in the changelog. ``<type>`` can be one of the types defined in `./towncrier.toml`.
    If necessary you can write details or offer examples on how the new change is supposed to work.
  * Generating the doc is done with ``tox -e docs``

- Send a pull request from GitHub (see `About pull requests`_ for more insight about this topic).

- Write comprehensive commit messages and/or a good description of what the PR does.
  Relate your change to an issue in the tracker if such an issue exists (see
  `Closing issues via commit messages`_ of the GitHub documentation for more
  information on this)

- Keep the change small, separate the consensual changes from the opinionated one.

  * Don't hesitate to open multiple PRs if the change requires it. If your review is so
    big it requires to actually plan and allocate time to review, it's more likely
    that it's going to go stale.
  * Maintainers might have multiple 5 to 10 minutes review windows per day, Say while waiting
    for their teapot to boil, or for their partner to recover from their hilarious nerdy joke,
    but only one full hour review time per week, if at all.

- If you used multiple emails or multiple names when contributing, add your mails
  and preferred name in the ``script/.contributors_aliases.json`` file.

.. _`Closing issues via commit messages`: https://github.blog/2013-01-22-closing-issues-via-commit-messages/
.. _`About pull requests`: https://support.github.com/features/pull-requests
.. _tox: https://tox.readthedocs.io/en/latest/
.. _pytest: https://docs.pytest.org/en/latest/
.. _black: https://github.com/psf/black
.. _isort: https://github.com/PyCQA/isort
.. _astroid: https://github.com/pylint-dev/astroid


Tips for Getting Started with Pylint Development
------------------------------------------------
* Read the :ref:`technical-reference`. It gives a short walk through of the pylint
  codebase and will help you identify where you will need to make changes
  for what you are trying to implement.

* ``astroid.extract_node`` is your friend. Most checkers are AST based,
  so you will likely need to interact with ``astroid``.
  A short example of how to use ``astroid.extract_node`` is given
  :ref:`here <astroid_extract_node>`.

* When fixing a bug for a specific check, search the code for the warning
  message to find where the warning is raised,
  and therefore where the logic for that code exists.

* When adding a new checker class you can use the :file:`get_unused_message_id_category.py`
  script in :file:`./script` to get a message id that is not used by
  any of the other checkers.

Building the documentation
----------------------------

You can use the makefile in the doc directory to build the documentation::

  $ make -C doc/ install-dependencies
  $ make -C doc/ html

We're reusing generated files for speed, use ``make clean`` or ``tox -e docs`` when you want to start from scratch.

How to choose the target version ?
----------------------------------

Choose depending on the kind of change you're doing:

.. include:: patch_release.rst
.. include:: minor_release.rst
.. include:: major_release.rst
````

## File: doc/development_guide/contributor_guide/governance.rst
````
============
 Governance
============

How to become part of the project ?
-----------------------------------

How to become a contributor ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Follow the code of conduct
- Search by yourself before asking for help
- Open an issue
- Investigate an issue and report your finding
- Open a merge request directly if you feel it's a consensual change

Reporting a bug is being a contributor already.

How to become a triager ?
^^^^^^^^^^^^^^^^^^^^^^^^^

- Create a pylint plugin, then migrate it to the 'pylint-dev' github organization.

Or:

- Contribute for more than 3 releases consistently.
- Do not be too opinionated, follow the code of conduct without requiring emotional
  works from the maintainers. It does not mean that disagreements are impossible,
  only that arguments should stay technical and reasonable so the conversation
  is civil and productive.
- Have a maintainer suggest that you become triager, without you asking
- Get unanimous approval or neutral agreement from current maintainers.

How to become a maintainer ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^


- Take ownership of a part of the code that is not maintained well at the moment
  or that you contributed personally (if we feel we can't merge something without
  your review, you're going to be able to merge those yourself soon).

Or:

- Contribute two big code merge requests over multiple releases (for example
  one checker in 2.13 and the following bug after release and one complicated
  bug fixes in 2.14). Otherwise contributing for more than 3 releases consistently
  with great technical and interpersonal skills.
- Triage for multiple months (close duplicate, clean up issues, answer questions...)
- Have an admin suggest that you become maintainer, without you asking
- Get unanimous approval or neutral agreement from current maintainers.


How to become an admin ?
^^^^^^^^^^^^^^^^^^^^^^^^

- Contribute for several hundreds of commits over a long period of time
  with excellent interpersonal skills and code quality.
- Maintain pylint for multiple years (code review, triaging and maintenance tasks).
- At this point probably have another admin leave the project or
  become inactive for years.
- Have an admin suggest that you become an admin, without you asking.
- Get unanimous approval or neutral agreement from current admins.


How are decisions made ?
------------------------

Everyone is expected to follow the code of conduct. pylint is a do-ocracy / democracy.
You're not allowed to behave poorly because you contributed a lot. But if
you're not going to do the future maintenance work, your valid opinions might not be
taken into account by those that will be affected by it.

What are the fundamental tenets of pylint development?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

General:

- We favor correctness over performance, because pylint is not used primarily
  for its performance. Performance is still important and needs to be taken into
  account from the get go.

- We then favor false negatives over false positives if correctness is
  impossible to achieve.

- We try to keep the configuration sane, but if there's a hard decision to take we
  add an option so that pylint is multiple sizes fit all (after configuration)

Where to add a new checker or message:

- Error messages (things that will result in an error if run) should be builtin
  checks, activated by default

- Messages that are opinionated, even slightly, should be opt-in (added as :ref:`an extension<plugins>`)

- We don't shy away from opinionated checks (like the while checker), but there's such a
  thing as too opinionated, if something is too opinionated it should be an external
  :ref:`pylint plugin<plugins>`.

How are disagreements handled ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When something is not consensual users, maintainers, and admins discuss until an
agreement is reached.

Depending on the difficulty of the discussion and the importance of a fast resolution,
a decision can be taken:

- Unanimously between discussion participants, contributors and maintainers (preferably)

- By asking discussion participants for their opinions with an emoji survey in the
  issue and then using the majority if no maintainers feel strongly about the issue.

- By majority of admins if no admins feel strongly about the issue.

- By asking all users for their opinions in a new issue that will be pinned for
  multiple months before taking the decision if two admins feel strongly on an
  opposite side of the issue. Once the result is obvious the majority decision
  is not up for discussion anymore.
````

## File: doc/development_guide/contributor_guide/index.rst
````
.. _contribute_guide:

Contributing to pylint
======================

The contributor guide will help you if you want to contribute to pylint itself.

.. toctree::
   :maxdepth: 2
   :titlesonly:

   contribute
   tests/index
   profiling
   oss_fuzz
   release
   governance
````

## File: doc/development_guide/contributor_guide/major_release.rst
````
- In **major releases** (``1.0.0``) we change everything else (pylint options, json output, dev API...)
  while still trying to minimize disruption.
````

## File: doc/development_guide/contributor_guide/minor_release.rst
````
- In **minor releases** (``1.2.0``), we add checks, remove checks, drop python interpreters
  past end of life, upgrade astroid minor/major versions and fix false negatives.
````

## File: doc/development_guide/contributor_guide/oss_fuzz.rst
````
======================
 OSS-Fuzz integration
======================

Platform overview
-----------------

`OSS-Fuzz <https://google.github.io/oss-fuzz/>`_ is Google's free fuzzing platform for open source
software. It runs astroid's fuzz targets to help detect reliability issues that could affect astroid
and Pylint.

Google provides public `build logs <https://oss-fuzz-build-logs.storage.googleapis.com/index.html#astroid>`_
and `fuzzing stats <https://introspector.oss-fuzz.com/project-profile?project=astroid>`_, but most
of the details about bug reports and fuzzed testcases require approved access.

Gaining access
^^^^^^^^^^^^^^

The configuration files for the OSS-Fuzz integration can be found in the
`OSS-Fuzz repository <https://github.com/google/oss-fuzz/tree/master/projects/astroid>`_.
The ``project.yaml`` file controls who has access to bug reports and testcases. Ping the
maintainers if you'd like to be added to the list (note: a Google account is required for
access).

Fuzzing progress
----------------

Once you have access to OSS-Fuzz, you can log in to https://oss-fuzz.com/ with your Google account
to see a dashboard of astroid's fuzzing progress.

Testcases
^^^^^^^^^

The dashboard contains a link to a `testcases page <https://oss-fuzz.com/testcases?project=astroid&open=yes>`_
that lists all testcases that currently trigger a bug in astroid.

Every testcase has a dedicated page with links to view and download a minimized testcase for
reproducing the failure. Each testcase page also contains a stacktrace for the failure and stats
about how often the failure is encountered while fuzzing.

Reproducing a failure
"""""""""""""""""""""

You can download a minimized testcase and run it locally to debug a failure on your machine.
For example, to reproduce a failure with the ``fuzz_parse`` fuzz target, you can run the following
commands:

.. code:: bash

  mkdir fuzzing-repro
  cd fuzzing-repro

  # Note: Atheris doesn't support Python 3.12+ yet:
  # https://github.com/google/atheris/issues/82
  uv venv --python 3.11
  source .venv/bin/activate

  git clone https://github.com/pylint-dev/astroid.git
  cd astroid

  uv pip install atheris==2.3.0
  uv pip install --editable .

  # Save the minimized testcase as `minimized.py` in the astroid directory

  cat << EOF > ./run_fuzz_parse.py

  import astroid
  import atheris

  with open('minimized.py', 'rb') as f:
      fdp = atheris.FuzzedDataProvider(f.read())

  code = fdp.ConsumeUnicodeNoSurrogates(fdp.ConsumeIntInRange(0, 4096))
  astroid.builder.parse(code)
  EOF

  python ./run_fuzz_parse.py


If the failure does not reproduce locally, you can try reproducing the issue in an OSS-Fuzz
container:

.. code:: bash

  git clone https://github.com/google/oss-fuzz.git
  cd oss-fuzz

  python infra/helper.py build_image astroid
  python infra/helper.py build_fuzzers astroid
  python infra/helper.py reproduce astroid fuzz_parse minimized.py

Some failures may only be reproducible in an OSS-Fuzz container because of differences in Python
versions between the OSS-Fuzz platform and your local environment.

Code coverage
^^^^^^^^^^^^^

The dashboard also links to code coverage data for individual fuzz targets and combined code
coverage data for all targets (click on the "TOTAL COVERAGE" link for the combined data).

The combined coverage data is helpful for identifying coverage gaps, insufficient corpus data, and
potential candidates for future fuzz targets.

Bug reports
^^^^^^^^^^^

Bug reports for new failures are automatically filed in the OSS-Fuzz bug tracker with an
`astroid label <https://issues.oss-fuzz.com/issues?q=project:astroid%20status:open>`_.
Make sure you are logged in to view all existing issues.

Build maintenance
-----------------

Google runs compiled fuzz targets on Google Compute Engine VMs. This architecture requires each
project to provide a ``Dockerfile`` and ``build.sh`` script to download code, configure
dependencies, compile fuzz targets, and package any corpus files.

astroid's build files and fuzz-target code can be found in the
`OSS-Fuzz repo <https://github.com/google/oss-fuzz/blob/master/projects/astroid/>`_.

If dependencies change or if new fuzz targets are added, then you may need to modify the build files
and build a new Docker image for OSS-Fuzz.

Building an image
^^^^^^^^^^^^^^^^^

Run the following commands to build astroid's OSS-Fuzz image and fuzz targets:

.. code:: bash

  git clone https://github.com/google/oss-fuzz.git
  cd oss-fuzz

  python infra/helper.py build_image astroid
  python infra/helper.py build_fuzzers astroid

Any changes you make to the build files must be submitted as pull requests to the OSS-Fuzz repo.

Debugging build failures
""""""""""""""""""""""""

You can debug build failures during the ``build_fuzzers`` stage by creating a container and manually
running the ``compile`` command:

.. code:: bash

  # Create a container for building fuzz targets
  python infra/helper.py shell astroid

  # Run this command inside the container to build the fuzz targets
  compile

The ``build.sh`` script will be located at ``/src/build.sh`` inside the container.

Quick links
-----------

- `OSS-Fuzz dashboard <https://oss-fuzz.com/>`_
- `OSS-Fuzz configuration files, build scripts, and fuzz targets for astroid <https://github.com/google/oss-fuzz/tree/master/projects/astroid>`_
- `All open OSS-Fuzz bugs for astroid <https://issues.oss-fuzz.com/issues?q=project:astroid%20status:open>`_
- `Google's OSS-Fuzz documentation <https://google.github.io/oss-fuzz/>`_
````

## File: doc/development_guide/contributor_guide/patch_release.rst
````
- In **patch release** (``1.2.3``), we only fix false positives and crashes.
````

## File: doc/development_guide/contributor_guide/profiling.rst
````
.. -*- coding: utf-8 -*-
.. _profiling:

===================================
 Profiling and performance analysis
===================================

Performance analysis for Pylint
-------------------------------

To analyse the performance of Pylint we recommend to use the ``cProfile`` module
from ``stdlib``. Together with the ``pstats`` module this should give you all the tools
you need to profile a Pylint run and see which functions take how long to run.

The documentation for both modules can be found at cProfile_.

To profile a run of Pylint over itself you can use the following code and run it from the base directory.
Note that ``cProfile`` will create a document called ``stats`` that is then read by ``pstats``. The
human-readable output will be stored by ``pstats`` in ``./profiler_stats``. It will be sorted by
``cumulative time``:

.. sourcecode:: python

    import cProfile
    import pstats
    import sys

    sys.argv = ["pylint", "pylint"]
    cProfile.run("from pylint import __main__", "stats")

    with open("profiler_stats", "w", encoding="utf-8") as file:
        stats = pstats.Stats("stats", stream=file)
        stats.sort_stats("cumtime")
        stats.print_stats()

You can also interact with the stats object by sorting or restricting the output.
For example, to only print functions from the ``pylint`` module and sort by cumulative time you could
use:

.. sourcecode:: python

    import cProfile
    import pstats
    import sys

    sys.argv = ["pylint", "pylint"]
    cProfile.run("from pylint import __main__", "stats")

    with open("profiler_stats", "w", encoding="utf-8") as file:
        stats = pstats.Stats("stats", stream=file)
        stats.sort_stats("cumtime")
        stats.print_stats("pylint/pylint")

Lastly, to profile a run over your own module or code you can use:

.. sourcecode:: python

    import cProfile
    import pstats
    import sys

    sys.argv = ["pylint", "your_dir/your_file"]
    cProfile.run("from pylint import __main__", "stats")

    with open("profiler_stats", "w", encoding="utf-8") as file:
        stats = pstats.Stats("stats", stream=file)
        stats.sort_stats("cumtime")
        stats.print_stats()

The documentation of the ``pstats`` module discusses other possibilities to interact with
the profiling output.


Performance analysis of a specific checker
------------------------------------------

To analyse the performance of specific checker within Pylint we can use the human-readable output
created by ``pstats``.

If you search in the ``profiler_stats`` file for the file name of the checker you will find all functional
calls from functions within the checker. Let's say we want to check the ``visit_importfrom`` method of the
``variables`` checker::

    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    622    0.006    0.000    8.039    0.013 /MY_PROGRAMMING_DIR/pylint/pylint/checkers/variables.py:1445(visit_importfrom)

The previous line tells us that this method was called 622 times during the profile and we were inside the
function itself for 6 ms in total. The time per call is less than a millisecond (0.006 / 622)
and thus is displayed as being 0.

Often you are more interested in the cumulative time (per call). This refers to the time spent within the function
and any of the functions it called or the functions they called (etc.). In our example, the ``visit_importfrom``
method and all of its child-functions took a little over 8 seconds to execute, with an execution time of
0.013 ms per call.

You can also search the ``profiler_stats`` for an individual function you want to check. For example
``_analyse_fallback_blocks``, a function called by ``visit_importfrom`` in the ``variables`` checker. This
allows more detailed analysis of specific functions::

    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    1    0.000    0.000    0.000    0.000 /MY_PROGRAMMING_DIR/pylint/pylint/checkers/variables.py:1511(_analyse_fallback_blocks)


Parsing the profiler stats with other tools
-------------------------------------------

Often you might want to create a visual representation of your profiling stats. A good tool
to do this is gprof2dot_. This tool can create a ``.dot`` file from the profiling stats
created by ``cProfile`` and ``pstats``. You can then convert the ``.dot`` file to a ``.png``
file with one of the many converters found online.

You can read the gprof2dot_ documentation for installation instructions for your specific environment.

Another option would be snakeviz_.

.. _cProfile: https://docs.python.org/3/library/profile.html
.. _gprof2dot: https://github.com/jrfonseca/gprof2dot
.. _snakeviz: https://jiffyclub.github.io/snakeviz/
````

## File: doc/development_guide/contributor_guide/release.rst
````
Releasing a pylint version
==========================

So, you want to release the ``X.Y.Z`` version of pylint ?

Releasing a major or minor version
----------------------------------

**Before releasing a major or minor version check if there are any
unreleased commits on the maintenance branch. If so, release a last
patch release first. See ``Releasing a patch version``.**

-  Write the ``Summary -- Release highlights`` in ``doc/whatsnew`` and
   upgrade the release date.
-  Install the release dependencies:
   ``pip3 install -r requirements_test.txt``
-  Bump the version and release by using
   ``tbump X.Y.0 --no-push --no-tag``. (For example:
   ``tbump 2.4.0 --no-push --no-tag``)
-  Check the commit created with ``git show`` amend the commit if
   required.
-  Move the ``main`` branch up to a dev version with ``tbump``:

.. code:: bash

   tbump X.Y+1.0-dev0 --no-tag --no-push  # You can interrupt after the first step
   git commit -am "Upgrade the version to x.y+1.0-dev0 following x.y.0 release"

For example:

.. code:: bash

   tbump 2.5.0-dev0 --no-tag --no-push
   git commit -am "Upgrade the version to 2.5.0-dev0 following 2.4.0 release"

-  tbump will have created a new ``What's new in Pylint X.Y+1`` document.
   Add it to ``doc/whatsnew/3/index.rst``. Take a look at the examples from ``doc/whatsnew``.
   Commit that with ``git commit -a --amend``.
- Push to a release branch
- Open a merge request with the two commits (no one can push directly
  on ``main``)
-  After the merge, recover the merged commits on ``main`` and tag the
   first one (the version should be ``X.Y.Z``) as ``vX.Y.Z`` (For
   example: ``v2.4.0``)
-  Push the tag.
-  Release the version on GitHub with the same name as the tag and copy
   and paste the appropriate changelog in the description. This triggers
   the PyPI release.
-  Create a ``maintenance/X.Y.x`` (For example: ``maintenance/2.4.x``
   from the ``v2.4.0`` tag.)
-  Upgrade the pattern for the protected branches in the settings under
   ``Branches`` / ``Branch protection rules``. (For example:
   ``maintenance/2.4*`` instead of ``maintenance/2.3*``.). There’s a lot
   of configuration done in these settings, do NOT recreate it from
   scratch.
-  Delete the ``maintenance/X.Y-1.x`` branch. (For example:
   ``maintenance/2.3.x``)
-  Select all the *closed* issues labelled ``backport maintenance/X.Y-1.x`` and
   label them ``backported``, then rename the
   ``backport maintenance/X.Y-1.x`` label to
   ``backport maintenance/X.Y.x`` (for example rename
   ``backport maintenance/2.3.x`` to ``backport maintenance/2.4.x``)
-  Close the current milestone and create the new ones (For example:
   close ``2.4.0``, create ``2.4.1`` and ``2.6.0``)
-  Hide and deactivate all the patch releases for the previous minor
   release on
   `readthedocs <https://readthedocs.org/projects/pylint/versions/>`__,
   except the last one. (For example: hide ``v2.4.0``, ``v2.4.1``,
   ``v2.4.2`` and keep only ``v2.4.3``)

Back-porting a fix from ``main`` to the maintenance branch
----------------------------------------------------------

Whenever a PR on ``main`` should be released in a patch release on the
current maintenance branch:

-  Label the PR with ``backport maintenance/X.Y-1.x``. (For example
   ``backport maintenance/2.3.x``)
-  Squash the PR before merging (alternatively rebase if there’s a
   single commit)
-  (If the automated cherry-pick has conflicts)

   -  Add a ``Needs backport`` label and do it manually.
   -  You might alternatively also:

      -  Cherry-pick the changes that create the conflict if it’s not a
         new feature before doing the original PR cherry-pick manually.
      -  Decide to wait for the next minor to release the PR
      -  In any case upgrade the milestones in the original PR and newly
         cherry-picked PR to match reality.

-  Release a patch version

Releasing a patch version
-------------------------

We release patch versions when a crash or a bug is fixed on the main
branch and has been cherry-picked on the maintenance branch.

-  Install the release dependencies:
   ``pip3 install -r requirements_test.txt``
-  Bump the version and release by using ``tbump X.Y-1.Z --no-push``.
   (For example: ``tbump 2.3.5 --no-push``)
-  Check the result visually with ``git show``.
-  Open a merge request of ``release-X.Y-1.Z'`` in ``maintenance/X.Y.x``
   (For example: ``release-2.3.5-branch`` in ``maintenance/2.3.x``) to
   run the CI tests for this branch.
-  Create and push the tag.
-  Release the version on GitHub with the same name as the tag and copy
   and paste the changelog from the ReadtheDoc generated documentation
   from the pull request pipeline in the description. This triggers the
   PyPI release.
-  Merge the ``maintenance/X.Y.x`` branch on the main branch. The main
   branch should have the changelog for ``X.Y-1.Z+1`` (For example
   ``v2.3.6``). This merge is required so ``pre-commit autoupdate``
   works for pylint.
-  Fix version conflicts properly, or bump the version to ``X.Y.0-devZ``
   (For example: ``2.4.0-dev6``) before pushing on the main branch
-  Close the current milestone and create the new one (For example:
   close ``2.3.5``, create ``2.3.6``)

Milestone handling
------------------

We move issues that were not done to the next milestone and block
releases only if there are any open issues labelled as ``blocker``.
````

## File: doc/development_guide/how_tos/custom_checkers.rst
````
.. _write_a_checker:

How to Write a Checker
======================
You can find some simple examples in the distribution
(`custom.py <https://github.com/pylint-dev/pylint/blob/main/examples/custom.py>`_
,
`custom_raw.py <https://github.com/pylint-dev/pylint/blob/main/examples/custom_raw.py>`_
and
`deprecation_checker.py <https://github.com/pylint-dev/pylint/blob/main/examples/deprecation_checker.py>`_).

.. TODO Create custom_token.py

There are three kinds of checkers:

* Raw checkers, which analyse each module as a raw file stream.
* Token checkers, which analyse a file using the list of tokens that
  represent the source code in the file.
* AST checkers, which work on an AST representation of the module.

The AST representation is provided by the ``astroid`` library.
``astroid`` adds additional information and methods
over ``ast`` in the standard library,
to make tree navigation and code introspection easier.

.. TODO Writing a Raw Checker

.. TODO Writing a Token Checker

Writing an AST Checker
----------------------
Let's implement a checker to make sure that all ``return`` nodes in a function
return a unique constant.
Firstly we will need to fill in some required boilerplate:

.. code-block:: python

  import astroid
  from astroid import nodes
  from typing import TYPE_CHECKING, Optional

  from pylint.checkers import BaseChecker

  if TYPE_CHECKING:
      from pylint.lint import PyLinter


  class UniqueReturnChecker(BaseChecker):

      name = "unique-returns"
      msgs = {
          "W0001": (
              "Returns a non-unique constant.",
              "non-unique-returns",
              "All constants returned in a function should be unique.",
          ),
      }
      options = (
          (
              "ignore-ints",
              {
                  "default": False,
                  "type": "yn",
                  "metavar": "<y or n>",
                  "help": "Allow returning non-unique integers",
              },
          ),
      )


So far we have defined the following required components of our checker:

* A name. The name is used to generate a special configuration
   section for the checker, when options have been provided.

* A message dictionary. Each checker is being used for finding problems
   in your code, the problems being displayed to the user through **messages**.
   The message dictionary should specify what messages the checker is
   going to emit. See `Defining a Message`_ for the details about defining a new message.

We have also defined an optional component of the checker.
The options list defines any user configurable options.
It has the following format::

    options = (
        ("option-symbol", {"argparse-like-kwarg": "value"}),
    )


* The ``option-symbol`` is a unique name for the option.
  This is used on the command line and in config files.
  The hyphen is replaced by an underscore when used in the checker,
  similarly to how you would use  ``argparse.Namespace``:

  .. code-block:: python

    if not self.linter.config.ignore_ints:
        ...

Next we'll track when we enter and leave a function.

.. code-block:: python

  def __init__(self, linter: Optional["PyLinter"] = None) -> None:
      super().__init__(linter)
      self._function_stack = []

  def visit_functiondef(self, node: nodes.FunctionDef) -> None:
      self._function_stack.append([])

  def leave_functiondef(self, node: nodes.FunctionDef) -> None:
      self._function_stack.pop()

In the constructor we initialise a stack to keep a list of return nodes
for each function.
An AST checker is a visitor, and should implement
``visit_<lowered class name>`` or ``leave_<lowered class name>``
methods for the nodes it's interested in.
In this case we have implemented ``visit_functiondef`` and ``leave_functiondef``
to add a new list of return nodes for this function,
and to remove the list of return nodes when we leave the function.

Finally we'll implement the check.
We will define a ``visit_return`` function,
which is called with an ``.astroid.nodes.Return`` node.

.. _astroid_extract_node:
.. TODO We can shorten/remove this bit once astroid has API docs.

We'll need to be able to figure out what attributes an
``.astroid.nodes.Return`` node has available.
We can use ``astroid.extract_node`` for this::

  >>> node = astroid.extract_node("return 5")
  >>> node
  <Return l.1 at 0x7efe62196390>
  >>> help(node)
  >>> node.value
  <Const.int l.1 at 0x7efe62196ef0>

We could also construct a more complete example::

  >>> node_a, node_b = astroid.extract_node("""
  ... def test():
  ...     if True:
  ...         return 5 #@
  ...     return 5 #@
  ... """)
  >>> node_a.value
  <Const.int l.4 at 0x7efe621a74e0>
  >>> node_a.value.value
  5
  >>> node_a.value.value == node_b.value.value
  True

For ``astroid.extract_node``, you can use ``#@`` at the end of a line to choose which statements will be extracted into nodes.

For more information on ``astroid.extract_node``,
see the `astroid documentation <https://pylint.readthedocs.io/projects/astroid/en/latest/>`_.

Now we know how to use the astroid node, we can implement our check.

.. code-block:: python

  def visit_return(self, node: nodes.Return) -> None:
      if not isinstance(node.value, nodes.Const):
          return
      for other_return in self._function_stack[-1]:
          if node.value.value == other_return.value.value and not (
              self.linter.config.ignore_ints and node.value.pytype() == int
          ):
              self.add_message("non-unique-returns", node=node)

      self._function_stack[-1].append(node)

Once we have established that the source code has failed our check,
we use ``~.BaseChecker.add_message`` to emit our failure message.

Finally, we need to register the checker with pylint.
Add the ``register`` function to the top level of the file.

.. code-block:: python

  def register(linter: "PyLinter") -> None:
      """This required method auto registers the checker during initialization.
      :param linter: The linter to register the checker to.
      """
      linter.register_checker(UniqueReturnChecker(linter))

We are now ready to debug and test our checker!

Debugging a Checker
-------------------
It is very simple to get to a point where we can use ``pdb``.
We'll need a small test case.
Put the following into a Python file:

.. code-block:: python

  def test():
      if True:
          return 5
      return 5

  def test2():
      if True:
          return 1
      return 5

After inserting pdb into our checker and installing it,
we can run pylint with only our checker::

  $ pylint --load-plugins=my_plugin --disable=all --enable=non-unique-returns test.py
  (Pdb)

Now we can debug our checker!

.. Note::

    ``my_plugin`` refers to a module called ``my_plugin.py``.
    The preferred way of making this plugin available to pylint is
    by installing it as a package. This can be done either from a packaging index like
    ``PyPI`` or by installing it from a local source such as with ``pip install``.

    Alternatively, the plugin module can be made available to pylint by
    putting this module's parent directory in your ``PYTHONPATH``
    environment variable.

    If your pylint config has an ``init-hook`` that modifies
    ``sys.path`` to include the module's parent directory, this
    will also work, but only if either:

    * the ``init-hook`` and the ``load-plugins`` list are both
      defined in a configuration file, or...
    * the ``init-hook`` is passed as a command-line argument and
      the ``load-plugins`` list is in the configuration file

    So, you cannot load a custom plugin by modifying ``sys.path`` if you
    supply the ``init-hook`` in a configuration file, but pass the module name
    in via ``--load-plugins`` on the command line.
    This is because pylint loads plugins specified on command
    line before loading any configuration from other sources.

Defining a Message
------------------

Pylint message is defined using the following format::

   msgs = {
       "E0401": ( # message id
        "Unable to import %s", # template of displayed message
        "import-error", # message symbol
        "Used when pylint has been unable to import a module.",  # Message description
        { # Additional parameters:
             # message control support for the old names of the messages:
            "old_names": [("F0401", "old-import-error")]
            "minversion": (3, 5), # No check under this version
            "maxversion": (3, 7), # No check above this version
        },
    ),

The message is then formatted using the ``args`` parameter from ``add_message`` i.e. in
``self.add_message("import-error", args=module_we_cant_import, node=importnode)``, the value in ``module_we_cant_import`` say ``patglib`` will be interpolled and the final result will be:
``Unable to import patglib``


* The ``message-id`` should be a 4-digit number,
  prefixed with a **message category**.
  There are multiple message categories,
  these being ``C``, ``W``, ``E``, ``F``, ``R``,
  standing for ``Convention``, ``Warning``, ``Error``, ``Fatal`` and ``Refactoring``.
  The 4 digits should not conflict with existing checkers
  and the first 2 digits should consistent across the checker (except shared messages).
  It is safe to use 51-99 as the first 2 digits for custom checkers because this range is reserved for them.

* The ``displayed-message`` is used for displaying the message to the user,
  once it is emitted.

* The ``message-symbol`` is an alias of the message id
  and it can be used wherever the message id can be used.

* The ``message-help`` is used when calling ``pylint --help-msg``.

Optionally message can contain optional extra options:

* The ``old_names`` option permits to change the message id or symbol of a message without breaking the message control used on the old messages by users. The option is specified as a list
  of tuples (``message-id``, ``old-message-symbol``) e.g. ``{"old_names": [("F0401", "old-import-error")]}``.
  The symbol / msgid association must be unique so if you're changing the message id the symbol also need to change and you can generally use the ``old-`` prefix for that.

* The ``minversion`` or ``maxversion`` options specify minimum or maximum version of python
  relevant for this message. The option value is specified as tuple with major version number
  as first number and minor version number as second number e.g. ``{"minversion": (3, 5)}``

* The ``shared`` option enables sharing message between multiple checkers. As mentioned
  previously, normally the message cannot be shared between multiple checkers.
  To allow having message shared between multiple checkers, the ``shared`` option must
  be set to ``True``.

Parallelize a Checker
---------------------

``BaseChecker`` has two methods ``get_map_data`` and ``reduce_map_data`` that
permit to parallelize the checks when used with the ``-j`` option. If a checker
actually needs to reduce data it should define ``get_map_data`` as returning
something different than ``None`` and let its ``reduce_map_data`` handle a list
of the types returned by ``get_map_data``.

An example can be seen by looking at ``pylint/checkers/similar.py``.

Testing a Checker
-----------------
Pylint is very well suited to test driven development.
You can implement the template of the checker,
produce all of your test cases and check that they fail,
implement the checker,
then check that all of your test cases work.

Pylint provides a ``pylint.testutils.CheckerTestCase``
to make test cases very simple.
We can use the example code that we used for debugging as our test cases.

.. code-block:: python

  import astroid
  import my_plugin
  import pylint.testutils


  class TestUniqueReturnChecker(pylint.testutils.CheckerTestCase):
      CHECKER_CLASS = my_plugin.UniqueReturnChecker

      def test_finds_non_unique_ints(self):
          func_node, return_node_a, return_node_b = astroid.extract_node("""
          def test(): #@
              if True:
                  return 5 #@
              return 5 #@
          """)

          self.checker.visit_functiondef(func_node)
          self.checker.visit_return(return_node_a)
          with self.assertAddsMessages(
              pylint.testutils.MessageTest(
                  msg_id="non-unique-returns",
                  node=return_node_b,
              ),
          ):
              self.checker.visit_return(return_node_b)

      def test_ignores_unique_ints(self):
          func_node, return_node_a, return_node_b = astroid.extract_node("""
          def test(): #@
              if True:
                  return 1 #@
              return 5 #@
          """)

          with self.assertNoMessages():
              self.checker.visit_functiondef(func_node)
              self.checker.visit_return(return_node_a)
              self.checker.visit_return(return_node_b)


Once again we are using ``astroid.extract_node`` to
construct our test cases.
``pylint.testutils.CheckerTestCase`` has created the linter and checker for us,
we simply simulate a traversal of the AST tree
using the nodes that we are interested in.
````

## File: doc/development_guide/how_tos/index.rst
````
How To Guides
=============

.. toctree::
   :maxdepth: 2
   :titlesonly:

   custom_checkers
   plugins
   transform_plugins
````

## File: doc/development_guide/how_tos/plugins.rst
````
.. -*- coding: utf-8 -*-

.. _plugins:

How To Write a Pylint Plugin
============================

Pylint provides support for writing two types of extensions.
First, there is the concept of **checkers**,
which can be used for finding problems in your code.
Secondly, there is also the concept of **transform plugin**,
which represents a way through which the inference and
the capabilities of Pylint can be enhanced
and tailored to a particular module, library of framework.

In general, a plugin is a module which should have a function ``register``,
which takes an instance of ``pylint.lint.PyLinter`` as input.

A plugin can optionally define a function, ``load_configuration``,
which takes an instance of ``pylint.lint.PyLinter`` as input. This
function is called after Pylint loads configuration from configuration
file and command line interface. This function should load additional
plugin specific configuration to Pylint.

So a basic hello-world plugin can be implemented as:

.. sourcecode:: python

  # Inside hello_plugin.py
  from typing import TYPE_CHECKING

  import astroid

  if TYPE_CHECKING:
      from pylint.lint import PyLinter


  def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    print('Hello world')


We can run this plugin by placing this module in the PYTHONPATH and invoking
**pylint** as:

.. sourcecode:: bash

  $ pylint -E --load-plugins hello_plugin foo.py
  Hello world

We can extend hello-world plugin to ignore some specific names using
``load_configuration`` function:

.. sourcecode:: python

  # Inside hello_plugin.py
  from typing import TYPE_CHECKING

  import astroid

  if TYPE_CHECKING:
      from pylint.lint import PyLinter


  def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    print('Hello world')

  def load_configuration(linter):

    name_checker = get_checker(linter, NameChecker)
    # We consider as good names of variables Hello and World
    name_checker.config.good_names += ('Hello', 'World')

    # We ignore bin directory
    linter.config.black_list += ('bin',)

Depending if we need a **transform plugin** or a **checker**, this might not
be enough. For the former, this is enough to declare the module as a plugin,
but in the case of the latter, we need to register our checker with the linter
object, by calling the following inside the ``register`` function::

    linter.register_checker(OurChecker(linter))

For more information on writing a checker see :ref:`write_a_checker`.
````

## File: doc/development_guide/how_tos/transform_plugins.rst
````
Transform plugins
^^^^^^^^^^^^^^^^^

Why write a plugin?
-------------------

Pylint is a static analysis tool and Python is a dynamically typed language.
So there will be cases where Pylint cannot analyze files properly (this problem
can happen in statically typed languages also if reflection or dynamic
evaluation is used).

The plugins are a way to tell Pylint how to handle such cases,
since only the user would know what needs to be done. They are usually operating
on the AST level, by modifying or changing it in a way which can ease its
understanding by Pylint.

Example
-------

Let us run Pylint on a module from the Python source: `warnings.py`_ and see what happens:

.. sourcecode:: shell

  amitdev$ pylint -E Lib/warnings.py
  E:297,36: Instance of 'WarningMessage' has no 'message' member (no-member)
  E:298,36: Instance of 'WarningMessage' has no 'filename' member (no-member)
  E:298,51: Instance of 'WarningMessage' has no 'lineno' member (no-member)
  E:298,64: Instance of 'WarningMessage' has no 'line' member (no-member)


Did we catch a genuine error? Let's open the code and look at ``WarningMessage`` class:

.. sourcecode:: python

  class WarningMessage(object):

    """Holds the result of a single showwarning() call."""

    _WARNING_DETAILS = ("message", "category", "filename", "lineno", "file",
                        "line")

    def __init__(self, message, category, filename, lineno, file=None,
                    line=None):
      local_values = locals()
      for attr in self._WARNING_DETAILS:
        setattr(self, attr, local_values[attr])
      self._category_name = category.__name__ if category else None

    def __str__(self):
      ...

Ah, the fields (``message``, ``category`` etc) are not defined statically on the class.
Instead they are added using ``setattr``. Pylint would have a tough time figuring
this out.

Enter Plugin
------------

We can write a transform plugin to tell Pylint how to analyze this properly.

One way to fix our example with a plugin would be to transform the ``WarningMessage`` class,
by setting the attributes so that Pylint can see them. This can be done by
registering a transform function. We can transform any node in the parsed AST like
Module, Class, Function etc. In our case we need to transform a class. It can be done so:

.. sourcecode:: python

  from typing import TYPE_CHECKING

  import astroid

  if TYPE_CHECKING:
      from pylint.lint import PyLinter


  def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    pass

  def transform(cls):
    if cls.name == 'WarningMessage':
      import warnings
      for f in warnings.WarningMessage._WARNING_DETAILS:
        cls.locals[f] = [astroid.ClassDef(f, None)]

  astroid.MANAGER.register_transform(astroid.ClassDef, transform)

Let's go through the plugin. First, we need to register a class transform, which
is done via the ``register_transform`` function in ``MANAGER``. It takes the node
type and function as parameters. We need to change a class, so we use ``astroid.ClassDef``.
We also pass a ``transform`` function which does the actual transformation.

``transform`` function is simple as well. If the class is ``WarningMessage`` then we
add the attributes to its locals (we are not bothered about type of attributes, so setting
them as class will do. But we could set them to any type we want). That's it.

Note: We don't need to do anything in the ``register`` function of the plugin since we
are not modifying anything in the linter itself.

Lets run Pylint with this plugin and see:

.. sourcecode:: bash

  amitdev$ pylint -E --load-plugins warning_plugin Lib/warnings.py
  amitdev$

All the false positives associated with ``WarningMessage`` are now gone. This is just
an example, any code transformation can be done by plugins.

See `astroid/brain`_ for real life examples of transform plugins.

.. _`warnings.py`: https://hg.python.org/cpython/file/2.7/Lib/warnings.py
.. _`astroid/brain`: https://github.com/pylint-dev/astroid/tree/main/astroid/brain
````

## File: doc/development_guide/technical_reference/checkers.rst
````
Checkers
--------
All of the default pylint checkers exist in ``pylint.checkers``.
This is where most of pylint's brains exist.
Most checkers are AST based and so use ``astroid``.
``pylint.checkers.utils`` provides a large number of utility methods for
dealing with ``astroid``.
````

## File: doc/development_guide/technical_reference/index.rst
````
.. _technical-reference:

Technical Reference
===================

.. TODO Configuration
.. TODO Messages
.. TODO Reports
.. extensions.rst and features.rst are generated.

.. toctree::
  :maxdepth: 2
  :titlesonly:

  startup
  checkers
````

## File: doc/development_guide/technical_reference/startup.rst
````
Startup and the Linter Class
----------------------------

The two main classes in ``pylint.lint`` are
``.pylint.lint.Run`` and ``.pylint.lint.PyLinter``.

The ``.pylint.lint.Run`` object is responsible for starting up pylint.
It does some basic checking of the given command line options to
find the initial hook to run,
find the config file to use,
and find which plugins have been specified.
It can then create the main ``.pylint.lint.PyLinter`` instance
and initialise it with the config file and plugins that were discovered
when preprocessing the command line options.
Finally the ``.pylint.lint.Run`` object launches any child linters
for parallel jobs, and starts the linting process.

The ``.pylint.lint.PyLinter`` is responsible for coordinating the
linting process.
It parses the configuration and provides it for the checkers and other plugins,
it handles the messages emitted by the checkers,
it handles the output reporting,
and it launches the checkers.
````

## File: doc/user_guide/checkers/extensions.rst
````
Optional checkers
=================

.. This file is auto-generated. Make any changes to the associated
.. docs extension in 'doc/exts/pylint_extensions.py'.

Pylint provides the following optional plugins:

- :ref:`pylint.extensions.bad_builtin`
- :ref:`pylint.extensions.broad_try_clause`
- :ref:`pylint.extensions.check_elif`
- :ref:`pylint.extensions.code_style`
- :ref:`pylint.extensions.comparison_placement`
- :ref:`pylint.extensions.confusing_elif`
- :ref:`pylint.extensions.consider_refactoring_into_while_condition`
- :ref:`pylint.extensions.consider_ternary_expression`
- :ref:`pylint.extensions.dict_init_mutate`
- :ref:`pylint.extensions.docparams`
- :ref:`pylint.extensions.docstyle`
- :ref:`pylint.extensions.dunder`
- :ref:`pylint.extensions.empty_comment`
- :ref:`pylint.extensions.eq_without_hash`
- :ref:`pylint.extensions.for_any_all`
- :ref:`pylint.extensions.magic_value`
- :ref:`pylint.extensions.mccabe`
- :ref:`pylint.extensions.no_self_use`
- :ref:`pylint.extensions.overlapping_exceptions`
- :ref:`pylint.extensions.private_import`
- :ref:`pylint.extensions.redefined_loop_name`
- :ref:`pylint.extensions.redefined_variable_type`
- :ref:`pylint.extensions.set_membership`
- :ref:`pylint.extensions.typing`
- :ref:`pylint.extensions.while_used`

You can activate any or all of these extensions by adding a ``load-plugins`` line to the ``MAIN`` section of your ``.pylintrc``, for example::

    load-plugins=pylint.extensions.docparams,pylint.extensions.docstyle

.. _pylint.extensions.broad_try_clause:

Broad Try Clause checker
~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.broad_try_clause``.
Verbatim name of the checker is ``broad_try_clause``.

See also :ref:`broad_try_clause checker's options' documentation <broad_try_clause-options>`

Broad Try Clause checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:too-many-try-statements (W0717):
  Try clause contains too many statements.


.. _pylint.extensions.code_style:

Code Style checker
~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.code_style``.
Verbatim name of the checker is ``code_style``.

Code Style checker Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Checkers that can improve code consistency.
As such they don't necessarily provide a performance benefit and
are often times opinionated.

See also :ref:`code_style checker's options' documentation <code_style-options>`

Code Style checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^
:consider-using-tuple (R6102): *Consider using an in-place tuple instead of list*
  Only for style consistency! Emitted where an in-place defined ``list`` can be
  replaced by a ``tuple``. Due to optimizations by CPython, there is no
  performance benefit from it.
:consider-using-namedtuple-or-dataclass (R6101): *Consider using namedtuple or dataclass for dictionary values*
  Emitted when dictionary values can be replaced by namedtuples or dataclass
  instances.
:prefer-typing-namedtuple (R6105): *Prefer 'typing.NamedTuple' over 'collections.namedtuple'*
  'typing.NamedTuple' uses the well-known 'class' keyword with type-hints for
  readability (it's also faster as it avoids an internal exec call). Disabled
  by default!
:consider-using-assignment-expr (R6103): *Use '%s' instead*
  Emitted when an if assignment is directly followed by an if statement and
  both can be combined by using an assignment expression ``:=``. Requires
  Python 3.8 and ``py-version >= 3.8``.
:consider-using-augmented-assign (R6104): *Use '%s' to do an augmented assign directly*
  Emitted when an assignment is referring to the object that it is assigning
  to. This can be changed to be an augmented assign. Disabled by default!


.. _pylint.extensions.comparison_placement:

Comparison-Placement checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.comparison_placement``.
Verbatim name of the checker is ``comparison-placement``.

Comparison-Placement checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:misplaced-comparison-constant (C2201): *Comparison should be %s*
  Used when the constant is placed on the left side of a comparison. It is
  usually clearer in intent to place it in the right hand side of the
  comparison.


.. _pylint.extensions.confusing_elif:

Confusing Elif checker
~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.confusing_elif``.
Verbatim name of the checker is ``confusing_elif``.

Confusing Elif checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:confusing-consecutive-elif (R5601): *Consecutive elif with differing indentation level, consider creating a function to separate the inner elif*
  Used when an elif statement follows right after an indented block which
  itself ends with if or elif. It may not be obvious if the elif statement was
  willingly or mistakenly unindented. Extracting the indented if statement into
  a separate function might avoid confusion and prevent errors.


.. _pylint.extensions.for_any_all:

Consider-Using-Any-Or-All checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.for_any_all``.
Verbatim name of the checker is ``consider-using-any-or-all``.

Consider-Using-Any-Or-All checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:consider-using-any-or-all (C0501): *`for` loop could be `%s`*
  A for loop that checks for a condition and return a bool can be replaced with
  any or all.


.. _pylint.extensions.consider_refactoring_into_while_condition:

Consider Refactoring Into While checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.consider_refactoring_into_while_condition``.
Verbatim name of the checker is ``consider_refactoring_into_while``.

Consider Refactoring Into While checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:consider-refactoring-into-while-condition (R3501): *Consider using 'while %s' instead of 'while %s:' an 'if', and a 'break'*
  Emitted when `while True:` loop is used and the first statement is a break
  condition. The ``if / break`` construct can be removed if the check is
  inverted and moved to the ``while`` statement.


.. _pylint.extensions.consider_ternary_expression:

Consider Ternary Expression checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.consider_ternary_expression``.
Verbatim name of the checker is ``consider_ternary_expression``.

Consider Ternary Expression checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:consider-ternary-expression (W0160): *Consider rewriting as a ternary expression*
  Multiple assign statements spread across if/else blocks can be rewritten with
  a single assignment and ternary expression


.. _pylint.extensions.bad_builtin:

Deprecated Builtins checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.bad_builtin``.
Verbatim name of the checker is ``deprecated_builtins``.

Deprecated Builtins checker Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This used to be the ``bad-builtin`` core checker, but it was moved to
an extension instead. It can be used for finding prohibited used builtins,
such as ``map`` or ``filter``, for which other alternatives exists.

If you want to control for what builtins the checker should warn about,
you can use the ``bad-functions`` option::

    $ pylint a.py --load-plugins=pylint.extensions.bad_builtin --bad-functions=apply,reduce
    ...

See also :ref:`deprecated_builtins checker's options' documentation <deprecated_builtins-options>`

Deprecated Builtins checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:bad-builtin (W0141): *Used builtin function %s*
  Used when a disallowed builtin function is used (see the bad-function
  option). Usual disallowed functions are the ones like map, or filter , where
  Python offers now some cleaner alternative like list comprehension.


.. _pylint.extensions.mccabe:

Design checker
~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.mccabe``.
Verbatim name of the checker is ``design``.

Design checker Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can now use this plugin for finding complexity issues in your code base.

Activate it through ``pylint --load-plugins=pylint.extensions.mccabe``. It introduces
a new warning, ``too-complex``, which is emitted when a code block has a complexity
higher than a preestablished value, which can be controlled through the
``max-complexity`` option, such as in this example::

    $ cat a.py
    def f10():
        """McCabe rating: 11"""
        myint = 2
        if myint == 5:
            return myint
        elif myint == 6:
            return myint
        elif myint == 7:
            return myint
        elif myint == 8:
            return myint
        elif myint == 9:
            return myint
        elif myint == 10:
            if myint == 8:
                while True:
                    return True
            elif myint == 8:
                with myint:
                    return 8
        else:
            if myint == 2:
                return myint
            return myint
        return myint
    $ pylint a.py --load-plugins=pylint.extensions.mccabe
    R:1: 'f10' is too complex. The McCabe rating is 11 (too-complex)
    $ pylint a.py --load-plugins=pylint.extensions.mccabe --max-complexity=50
    $

See also :ref:`design checker's options' documentation <design-options>`

Design checker Messages
^^^^^^^^^^^^^^^^^^^^^^^
:too-complex (R1260): *%s is too complex. The McCabe rating is %d*
  Used when a method or function is too complex based on McCabe Complexity
  Cyclomatic


.. _pylint.extensions.dict_init_mutate:

Dict-Init-Mutate checker
~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.dict_init_mutate``.
Verbatim name of the checker is ``dict-init-mutate``.

Dict-Init-Mutate checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:dict-init-mutate (C3401): *Declare all known key/values when initializing the dictionary.*
  Dictionaries can be initialized with a single statement using dictionary
  literal syntax.


.. _pylint.extensions.docstyle:

Docstyle checker
~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.docstyle``.
Verbatim name of the checker is ``docstyle``.

Docstyle checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^
:bad-docstring-quotes (C0198): *Bad docstring quotes in %s, expected """, given %s*
  Used when a docstring does not have triple double quotes.
:docstring-first-line-empty (C0199): *First line empty in %s docstring*
  Used when a blank line is found at the beginning of a docstring.


.. _pylint.extensions.dunder:

Dunder checker
~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.dunder``.
Verbatim name of the checker is ``dunder``.

See also :ref:`dunder checker's options' documentation <dunder-options>`

Dunder checker Messages
^^^^^^^^^^^^^^^^^^^^^^^
:bad-dunder-name (W3201): *Bad or misspelled dunder method name %s.*
  Used when a dunder method is misspelled or defined with a name not within the
  predefined list of dunder names.


.. _pylint.extensions.check_elif:

Else If Used checker
~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.check_elif``.
Verbatim name of the checker is ``else_if_used``.

Else If Used checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:else-if-used (R5501): *Consider using "elif" instead of "else" then "if" to remove one indentation level*
  Used when an else statement is immediately followed by an if statement and
  does not contain statements that would be unrelated to it.


.. _pylint.extensions.empty_comment:

Empty-Comment checker
~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.empty_comment``.
Verbatim name of the checker is ``empty-comment``.

Empty-Comment checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:empty-comment (R2044): *Line with empty comment*
  Used when a # symbol appears on a line not followed by an actual comment


.. _pylint.extensions.eq_without_hash:

Eq-Without-Hash checker
~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.eq_without_hash``.
Verbatim name of the checker is ``eq-without-hash``.

Eq-Without-Hash checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:eq-without-hash (W1641): *Implementing __eq__ without also implementing __hash__*
  Used when a class implements __eq__ but not __hash__. Objects get None as
  their default __hash__ implementation if they also implement __eq__.


.. _pylint.extensions.private_import:

Import-Private-Name checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.private_import``.
Verbatim name of the checker is ``import-private-name``.

Import-Private-Name checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:import-private-name (C2701): *Imported private %s (%s)*
  Used when a private module or object prefixed with _ is imported. PEP8
  guidance on Naming Conventions states that public attributes with leading
  underscores should be considered private.


.. _pylint.extensions.magic_value:

Magic-Value checker
~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.magic_value``.
Verbatim name of the checker is ``magic-value``.

See also :ref:`magic-value checker's options' documentation <magic-value-options>`

Magic-Value checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:magic-value-comparison (R2004): *Consider using a named constant or an enum instead of '%s'.*
  Using named constants instead of magic values helps improve readability and
  maintainability of your code, try to avoid them in comparisons.


.. _pylint.extensions.redefined_variable_type:

Multiple Types checker
~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.redefined_variable_type``.
Verbatim name of the checker is ``multiple_types``.

Multiple Types checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:redefined-variable-type (R0204): *Redefinition of %s type from %s to %s*
  Used when the type of a variable changes inside a method or a function.


.. _pylint.extensions.no_self_use:

No Self Use checker
~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.no_self_use``.
Verbatim name of the checker is ``no_self_use``.

No Self Use checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:no-self-use (R6301): *Method could be a function*
  Used when a method doesn't use its bound instance, and so could be written as
  a function.


.. _pylint.extensions.overlapping_exceptions:

Overlap-Except checker
~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.overlapping_exceptions``.
Verbatim name of the checker is ``overlap-except``.

Overlap-Except checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:overlapping-except (W0714): *Overlapping exceptions (%s)*
  Used when exceptions in handler overlap or are identical


.. _pylint.extensions.docparams:

Parameter Documentation checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.docparams``.
Verbatim name of the checker is ``parameter_documentation``.

Parameter Documentation checker Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you document the parameters of your functions, methods and constructors and
their types systematically in your code this optional component might
be useful for you. Sphinx style, Google style, and Numpy style are supported.
(For some examples, see https://pypi.org/project/sphinxcontrib-napoleon/ .)

You can activate this checker by adding the line::

    load-plugins=pylint.extensions.docparams

to the ``MAIN`` section of your ``.pylintrc``.

This checker verifies that all function, method, and constructor docstrings
include documentation of the

* parameters and their types
* return value and its type
* exceptions raised

and can handle docstrings in

* Sphinx style (``param``, ``type``, ``return``, ``rtype``,
  ``raise`` / ``except``)::

   def function_foo(x, y, z):
       '''function foo ...

       :param x: bla x
       :type x: int

       :param y: bla y
       :type y: float

       :param int z: bla z

       :return: sum
       :rtype: float

       :raises OSError: bla
       '''
       return x + y + z

* or the Google style (``Args:``, ``Returns:``, ``Raises:``)::

   def function_foo(x, y, z):
       '''function foo ...

       Args:
           x (int): bla x
           y (float): bla y

           z (int): bla z

       Returns:
           float: sum

       Raises:
           OSError: bla
       '''
       return x + y + z

* or the Numpy style (``Parameters``, ``Returns``, ``Raises``)::

   def function_foo(x, y, z):
       '''function foo ...

       Parameters
       ----------
       x: int
           bla x
       y: float
           bla y

       z: int
           bla z

       Returns
       -------
       float
           sum

       Raises
       ------
       OSError
           bla
       '''
       return x + y + z


You'll be notified of **missing parameter documentation** but also of
**naming inconsistencies** between the signature and the documentation which
often arise when parameters are renamed automatically in the code, but not in
the documentation.
**Note:** by default docstrings of private and magic methods are not checked.
To change this behaviour (for example, to also check ``__init__``) add
``no-docstring-rgx=^(?!__init__$)_`` to the ``BASIC`` section of your ``.pylintrc``.

Constructor parameters can be documented in either the class docstring or
the ``__init__`` docstring, but not both::

    class ClassFoo(object):
        '''Sphinx style docstring foo

        :param float x: bla x

        :param y: bla y
        :type y: int
        '''
        def __init__(self, x, y):
            pass

    class ClassBar(object):
        def __init__(self, x, y):
            '''Google style docstring bar

            Args:
                x (float): bla x
                y (int): bla y
            '''
            pass

In some cases, having to document all parameters is a nuisance, for instance if
many of your functions or methods just follow a **common interface**. To remove
this burden, the checker accepts missing parameter documentation if one of the
following phrases is found in the docstring:

* For the other parameters, see
* For the parameters, see

(with arbitrary whitespace between the words). Please add a link to the
docstring defining the interface, e.g. a superclass method, after "see"::

   def callback(x, y, z):
       '''Sphinx style docstring for callback ...

       :param x: bla x
       :type x: int

       For the other parameters, see
       :class:`MyFrameworkUsingAndDefiningCallback`
       '''
       return x + y + z

   def callback(x, y, z):
       '''Google style docstring for callback ...

       Args:
           x (int): bla x

       For the other parameters, see
       :class:`MyFrameworkUsingAndDefiningCallback`
       '''
       return x + y + z

Naming inconsistencies in existing parameter and their type documentations are
still detected.

See also :ref:`parameter_documentation checker's options' documentation <parameter_documentation-options>`

Parameter Documentation checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:differing-param-doc (W9017): *"%s" differing in parameter documentation*
  Please check parameter names in declarations.
:differing-type-doc (W9018): *"%s" differing in parameter type documentation*
  Please check parameter names in type declarations.
:multiple-constructor-doc (W9005): *"%s" has constructor parameters documented in class and __init__*
  Please remove parameter declarations in the class or constructor.
:missing-param-doc (W9015): *"%s" missing in parameter documentation*
  Please add parameter declarations for all parameters.
:missing-type-doc (W9016): *"%s" missing in parameter type documentation*
  Please add parameter type declarations for all parameters.
:missing-raises-doc (W9006): *"%s" not documented as being raised*
  Please document exceptions for all raised exception types.
:useless-param-doc (W9019): *"%s" useless ignored parameter documentation*
  Please remove the ignored parameter documentation.
:useless-type-doc (W9020): *"%s" useless ignored parameter type documentation*
  Please remove the ignored parameter type documentation.
:missing-any-param-doc (W9021): *Missing any documentation in "%s"*
  Please add parameter and/or type documentation.
:missing-return-doc (W9011): *Missing return documentation*
  Please add documentation about what this method returns.
:missing-return-type-doc (W9012): *Missing return type documentation*
  Please document the type returned by this method.
:missing-yield-doc (W9013): *Missing yield documentation*
  Please add documentation about what this generator yields.
:missing-yield-type-doc (W9014): *Missing yield type documentation*
  Please document the type yielded by this method.
:redundant-returns-doc (W9008): *Redundant returns documentation*
  Please remove the return/rtype documentation from this method.
:redundant-yields-doc (W9010): *Redundant yields documentation*
  Please remove the yields documentation from this method.


.. _pylint.extensions.redefined_loop_name:

Redefined-Loop-Name checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.redefined_loop_name``.
Verbatim name of the checker is ``redefined-loop-name``.

Redefined-Loop-Name checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:redefined-loop-name (W2901): *Redefining %r from loop (line %s)*
  Used when a loop variable is overwritten in the loop body.


.. _pylint.extensions.set_membership:

Set Membership checker
~~~~~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.set_membership``.
Verbatim name of the checker is ``set_membership``.

Set Membership checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:use-set-for-membership (R6201): *Consider using set for membership test*
  Membership tests are more efficient when performed on a lookup optimized
  datatype like ``sets``.


.. _pylint.extensions.typing:

Typing checker
~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.typing``.
Verbatim name of the checker is ``typing``.

Typing checker Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Find issue specifically related to type annotations.

See also :ref:`typing checker's options' documentation <typing-options>`

Typing checker Messages
^^^^^^^^^^^^^^^^^^^^^^^
:broken-noreturn (E6004): *'NoReturn' inside compound types is broken in 3.7.0 / 3.7.1*
  ``typing.NoReturn`` inside compound types is broken in Python 3.7.0 and
  3.7.1. If not dependent on runtime introspection, use string annotation
  instead. E.g. ``Callable[..., 'NoReturn']``.
  https://bugs.python.org/issue34921
:broken-collections-callable (E6005): *'collections.abc.Callable' inside Optional and Union is broken in 3.9.0 / 3.9.1 (use 'typing.Callable' instead)*
  ``collections.abc.Callable`` inside Optional and Union is broken in Python
  3.9.0 and 3.9.1. Use ``typing.Callable`` for these cases instead.
  https://bugs.python.org/issue42965
:deprecated-typing-alias (W6001): *'%s' is deprecated, use '%s' instead*
  Emitted when a deprecated typing alias is used.
:consider-using-alias (R6002): *'%s' will be deprecated with PY39, consider using '%s' instead%s*
  Only emitted if 'runtime-typing=no' and a deprecated typing alias is used in
  a type annotation context in Python 3.7 or 3.8.
:consider-alternative-union-syntax (R6003): *Consider using alternative union syntax instead of '%s'%s*
  Emitted when ``typing.Union`` or ``typing.Optional`` is used instead of the
  shorthand union syntax. For example, ``Union[int, float]`` instead of ``int |
  float``. Using the shorthand for unions aligns with Python typing
  recommendations, removes the need for imports, and avoids confusion in
  function signatures.
:unnecessary-default-type-args (R6007): *Type `%s` has unnecessary default type args. Change it to `%s`.*
  Emitted when types have default type args which can be omitted. Mainly used
  for `typing.Generator` and `typing.AsyncGenerator`.
:redundant-typehint-argument (R6006): *Type `%s` is used more than once in union type annotation. Remove redundant typehints.*
  Duplicated type arguments will be skipped by `mypy` tool, therefore should be
  removed to avoid confusion.


.. _pylint.extensions.while_used:

While Used checker
~~~~~~~~~~~~~~~~~~

This checker is provided by ``pylint.extensions.while_used``.
Verbatim name of the checker is ``while_used``.

While Used checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^
:while-used (W0149): *Used `while` loop*
  Unbounded `while` loops can often be rewritten as bounded `for` loops.
  Exceptions can be made for cases such as event loops, listeners, etc.
````

## File: doc/user_guide/checkers/features.rst
````
Pylint features
===============

.. This file is auto-generated. Make any changes to the associated
.. docs extension in 'doc/exts/pylint_features.py'.

Pylint checkers' options and switches
-------------------------------------

Pylint checkers can provide three set of features:

* options that control their execution,
* messages that they can raise,
* reports that they can generate.

Below is a list of all checkers and their features.

Async checker
~~~~~~~~~~~~~

Verbatim name of the checker is ``async``.

Async checker Messages
^^^^^^^^^^^^^^^^^^^^^^
:not-async-context-manager (E1701): *Async context manager '%s' doesn't implement __aenter__ and __aexit__.*
  Used when an async context manager is used with an object that does not
  implement the async context management protocol. This message can't be
  emitted when using Python < 3.5.
:yield-inside-async-function (E1700): *Yield inside async function*
  Used when an `yield` or `yield from` statement is found inside an async
  function. This message can't be emitted when using Python < 3.5.


Bad-Chained-Comparison checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``bad-chained-comparison``.

Bad-Chained-Comparison checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:bad-chained-comparison (W3601): *Suspicious %s-part chained comparison using semantically incompatible operators (%s)*
  Used when there is a chained comparison where one expression is part of two
  comparisons that belong to different semantic groups ("<" does not mean the
  same thing as "is", chaining them in "0 < x is None" is probably a mistake).


Basic checker
~~~~~~~~~~~~~

Verbatim name of the checker is ``basic``.

See also :ref:`basic checker's options' documentation <basic-options>`

Basic checker Messages
^^^^^^^^^^^^^^^^^^^^^^
:not-in-loop (E0103): *%r not properly in loop*
  Used when break or continue keywords are used outside a loop.
:function-redefined (E0102): *%s already defined line %s*
  Used when a function / class / method is redefined.
:abstract-class-instantiated (E0110): *Abstract class %r with abstract methods instantiated*
  Used when an abstract class with `abc.ABCMeta` as metaclass has abstract
  methods and is instantiated.
:star-needs-assignment-target (E0114): *Can use starred expression only in assignment target*
  Emitted when a star expression is not used in an assignment target.
:duplicate-argument-name (E0108): *Duplicate argument name %r in function definition*
  Duplicate argument names in function definitions are syntax errors.
:return-in-init (E0101): *Explicit return in __init__*
  Used when the special class method __init__ has an explicit return value.
:too-many-star-expressions (E0112): *More than one starred expression in assignment*
  Emitted when there are more than one starred expressions (`*x`) in an
  assignment. This is a SyntaxError.
:nonlocal-and-global (E0115): *Name %r is nonlocal and global*
  Emitted when a name is both nonlocal and global.
:used-prior-global-declaration (E0118): *Name %r is used prior to global declaration*
  Emitted when a name is used prior a global declaration, which results in an
  error since Python 3.6. This message can't be emitted when using Python <
  3.6.
:return-outside-function (E0104): *Return outside function*
  Used when a "return" statement is found outside a function or method.
:return-arg-in-generator (E0106): *Return with argument inside generator*
  Used when a "return" statement with an argument is found in a generator
  function or method (e.g. with some "yield" statements). This message can't be
  emitted when using Python >= 3.3.
:invalid-star-assignment-target (E0113): *Starred assignment target must be in a list or tuple*
  Emitted when a star expression is used as a starred assignment target.
:bad-reversed-sequence (E0111): *The first reversed() argument is not a sequence*
  Used when the first argument to reversed() builtin isn't a sequence (does not
  implement __reversed__, nor __getitem__ and __len__
:nonexistent-operator (E0107): *Use of the non-existent %s operator*
  Used when you attempt to use the C-style pre-increment or pre-decrement
  operator -- and ++, which doesn't exist in Python.
:yield-outside-function (E0105): *Yield outside function*
  Used when a "yield" statement is found outside a function or method.
:init-is-generator (E0100): *__init__ method is a generator*
  Used when the special class method __init__ is turned into a generator by a
  yield in its body.
:misplaced-format-function (E0119): *format function is not called on str*
  Emitted when format function is not called on str object. e.g doing
  print("value: {}").format(123) instead of print("value: {}".format(123)).
  This might not be what the user intended to do.
:nonlocal-without-binding (E0117): *nonlocal name %s found without binding*
  Emitted when a nonlocal variable does not have an attached name somewhere in
  the parent scopes
:lost-exception (W0150): *%s statement in finally block may swallow exception*
  Used when a break or a return statement is found inside the finally clause of
  a try...finally block: the exceptions raised in the try clause will be
  silently swallowed instead of being re-raised.
:break-in-finally (W0137): *'break' discouraged inside 'finally' clause*
  Emitted when the `break` keyword is found inside a finally clause. This
  will raise a SyntaxWarning starting in Python 3.14.
:continue-in-finally (W0136): *'continue' discouraged inside 'finally' clause*
  Emitted when the `continue` keyword is found inside a finally clause. This
  will raise a SyntaxWarning starting in Python 3.14.
:return-in-finally (W0134): *'return' shadowed by the 'finally' clause.*
  Emitted when a 'return' statement is found in a 'finally' block. This will
  overwrite the return value of a function and should be avoided.
:assert-on-tuple (W0199): *Assert called on a populated tuple. Did you mean 'assert x,y'?*
  A call of assert on a tuple will always evaluate to true if the tuple is not
  empty, and will always evaluate to false if it is.
:assert-on-string-literal (W0129): *Assert statement has a string literal as its first argument. The assert will %s fail.*
  Used when an assert statement has a string literal as its first argument,
  which will cause the assert to always pass.
:self-assigning-variable (W0127): *Assigning the same variable %r to itself*
  Emitted when we detect that a variable is assigned to itself
:comparison-with-callable (W0143): *Comparing against a callable, did you omit the parenthesis?*
  This message is emitted when pylint detects that a comparison with a callable
  was made, which might suggest that some parenthesis were omitted, resulting
  in potential unwanted behaviour.
:nan-comparison (W0177): *Comparison %s should be %s*
  Used when an expression is compared to NaN values like numpy.NaN and
  float('nan').
:dangerous-default-value (W0102): *Dangerous default value %s as argument*
  Used when a mutable value as list or dictionary is detected in a default
  value for an argument.
:duplicate-key (W0109): *Duplicate key %r in dictionary*
  Used when a dictionary expression binds the same key multiple times.
:duplicate-value (W0130): *Duplicate value %r in set*
  This message is emitted when a set contains the same value two or more times.
:useless-else-on-loop (W0120): *Else clause on loop without a break statement, remove the else and de-indent all the code inside it*
  Loops should only have an else clause if they can exit early with a break
  statement, otherwise the statements under else should be on the same scope as
  the loop itself.
:pointless-exception-statement (W0133): *Exception statement has no effect*
  Used when an exception is created without being assigned, raised or returned
  for subsequent use elsewhere.
:expression-not-assigned (W0106): *Expression "%s" is assigned to nothing*
  Used when an expression that is not a function call is assigned to nothing.
  Probably something else was intended.
:confusing-with-statement (W0124): *Following "as" with another context manager looks like a tuple.*
  Emitted when a `with` statement component returns multiple values and uses
  name binding with `as` only for a part of those values, as in with ctx() as
  a, b. This can be misleading, since it's not clear if the context manager
  returns a tuple or if the node without a name binding is another context
  manager.
:unnecessary-lambda (W0108): *Lambda may not be necessary*
  Used when the body of a lambda expression is a function call on the same
  argument list as the lambda itself; such lambda expressions are in all but a
  few cases replaceable with the function being called in the body of the
  lambda.
:named-expr-without-context (W0131): *Named expression used without context*
  Emitted if named expression is used to do a regular assignment outside a
  context like if, for, while, or a comprehension.
:redeclared-assigned-name (W0128): *Redeclared variable %r in assignment*
  Emitted when we detect that a variable was redeclared in the same assignment.
:pointless-statement (W0104): *Statement seems to have no effect*
  Used when a statement doesn't have (or at least seems to) any effect.
:pointless-string-statement (W0105): *String statement has no effect*
  Used when a string is used as a statement (which of course has no effect).
  This is a particular case of W0104 with its own message so you can easily
  disable it if you're using those strings as documentation, instead of
  comments.
:contextmanager-generator-missing-cleanup (W0135): *The context used in function %r will not be exited.*
  Used when a contextmanager is used inside a generator function and the
  cleanup is not handled.
:unnecessary-pass (W0107): *Unnecessary pass statement*
  Used when a "pass" statement can be removed without affecting the behaviour
  of the code.
:unreachable (W0101): *Unreachable code*
  Used when there is some code behind a "return" or "raise" statement, which
  will never be accessed.
:eval-used (W0123): *Use of eval*
  Used when you use the "eval" function, to discourage its usage. Consider
  using `ast.literal_eval` for safely evaluating strings containing Python
  expressions from untrusted sources.
:exec-used (W0122): *Use of exec*
  Raised when the 'exec' statement is used. It's dangerous to use this function
  for a user input, and it's also slower than actual code in general. This
  doesn't mean you should never use it, but you should consider alternatives
  first and restrict the functions available.
:using-constant-test (W0125): *Using a conditional statement with a constant value*
  Emitted when a conditional statement (If or ternary if) uses a constant value
  for its test. This might not be what the user intended to do.
:missing-parentheses-for-call-in-test (W0126): *Using a conditional statement with potentially wrong function or method call due to missing parentheses*
  Emitted when a conditional statement (If or ternary if) seems to wrongly call
  a function due to missing parentheses
:comparison-of-constants (R0133): *Comparison between constants: '%s %s %s' has a constant value*
  When two literals are compared with each other the result is a constant.
  Using the constant directly is both easier to read and more performant.
  Initializing 'True' and 'False' this way is not required since Python 2.3.
:literal-comparison (R0123): *In '%s', use '%s' when comparing constant literals not '%s' ('%s')*
  Used when comparing an object to a literal, which is usually what you do not
  want to do, since you can compare to a different literal than what was
  expected altogether.
:comparison-with-itself (R0124): *Redundant comparison - %s*
  Used when something is compared against itself.
:invalid-name (C0103): *%s name "%s" doesn't conform to %s*
  Used when the name doesn't conform to naming rules associated to its type
  (constant, variable, class...).
:singleton-comparison (C0121): *Comparison %s should be %s*
  Used when an expression is compared to singleton values like True, False or
  None.
:disallowed-name (C0104): *Disallowed name "%s"*
  Used when the name matches bad-names or bad-names-rgxs- (unauthorized names).
:empty-docstring (C0112): *Empty %s docstring*
  Used when a module, function, class or method has an empty docstring (it
  would be too easy ;).
:missing-class-docstring (C0115): *Missing class docstring*
  Used when a class has no docstring. Even an empty class must have a
  docstring.
:missing-function-docstring (C0116): *Missing function or method docstring*
  Used when a function or method has no docstring. Some special methods like
  __init__ do not require a docstring.
:missing-module-docstring (C0114): *Missing module docstring*
  Used when a module has no docstring. Empty modules do not require a
  docstring.
:typevar-name-incorrect-variance (C0105): *Type variable name does not reflect variance%s*
  Emitted when a TypeVar name doesn't reflect its type variance. According to
  PEP8, it is recommended to add suffixes '_co' and '_contra' to the variables
  used to declare covariant or contravariant behaviour respectively. Invariant
  (default) variables do not require a suffix. The message is also emitted when
  invariant variables do have a suffix.
:typevar-double-variance (C0131): *TypeVar cannot be both covariant and contravariant*
  Emitted when both the "covariant" and "contravariant" keyword arguments are
  set to "True" in a TypeVar.
:typevar-name-mismatch (C0132): *TypeVar name "%s" does not match assigned variable name "%s"*
  Emitted when a TypeVar is assigned to a variable that does not match its name
  argument.
:unidiomatic-typecheck (C0123): *Use isinstance() rather than type() for a typecheck.*
  The idiomatic way to perform an explicit typecheck in Python is to use
  isinstance(x, Y) rather than type(x) == Y, type(x) is Y. Though there are
  unusual situations where these give different results.

Basic checker Reports
^^^^^^^^^^^^^^^^^^^^^
:RP0101: Statistics by type


Classes checker
~~~~~~~~~~~~~~~

Verbatim name of the checker is ``classes``.

See also :ref:`classes checker's options' documentation <classes-options>`

Classes checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^
:access-member-before-definition (E0203): *Access to member %r before its definition line %s*
  Used when an instance member is accessed before it's actually assigned.
:method-hidden (E0202): *An attribute defined in %s line %s hides this method*
  Used when a class defines a method which is hidden by an instance attribute
  from an ancestor class or set by some client code.
:assigning-non-slot (E0237): *Assigning to attribute %r not defined in class slots*
  Used when assigning to an attribute not defined in the class slots.
:duplicate-bases (E0241): *Duplicate bases for class %r*
  Duplicate use of base classes in derived classes raise TypeErrors.
:invalid-enum-extension (E0244): *Extending inherited Enum class "%s"*
  Used when a class tries to extend an inherited Enum class. Doing so will
  raise a TypeError at runtime.
:inconsistent-mro (E0240): *Inconsistent method resolution order for class %r*
  Used when a class has an inconsistent method resolution order.
:inherit-non-class (E0239): *Inheriting %r, which is not a class.*
  Used when a class inherits from something which is not a class.
:invalid-slots (E0238): *Invalid __slots__ object*
  Used when an invalid __slots__ is found in class. Only a string, an iterable
  or a sequence is permitted.
:invalid-class-object (E0243): *Invalid assignment to '__class__'. Should be a class definition but got a '%s'*
  Used when an invalid object is assigned to a __class__ property. Only a class
  is permitted.
:invalid-slots-object (E0236): *Invalid object %r in __slots__, must contain only non empty strings*
  Used when an invalid (non-string) object occurs in __slots__.
:no-method-argument (E0211): *Method %r has no argument*
  Used when a method which should have the bound instance as first argument has
  no argument defined.
:no-self-argument (E0213): *Method %r should have "self" as first argument*
  Used when a method has an attribute different the "self" as first argument.
  This is considered as an error since this is a so common convention that you
  shouldn't break it!
:declare-non-slot (E0245): *No such name %r in __slots__*
  Raised when a type annotation on a class is absent from the list of names in
  __slots__, and __slots__ does not contain a __dict__ entry.
:unexpected-special-method-signature (E0302): *The special method %r expects %s param(s), %d %s given*
  Emitted when a special method was defined with an invalid number of
  parameters. If it has too few or too many, it might not work at all.
:class-variable-slots-conflict (E0242): *Value %r in slots conflicts with class variable*
  Used when a value in __slots__ conflicts with a class variable, property or
  method.
:invalid-bool-returned (E0304): *__bool__ does not return bool*
  Used when a __bool__ method returns something which is not a bool
:invalid-bytes-returned (E0308): *__bytes__ does not return bytes*
  Used when a __bytes__ method returns something which is not bytes
:invalid-format-returned (E0311): *__format__ does not return str*
  Used when a __format__ method returns something which is not a string
:invalid-getnewargs-returned (E0312): *__getnewargs__ does not return a tuple*
  Used when a __getnewargs__ method returns something which is not a tuple
:invalid-getnewargs-ex-returned (E0313): *__getnewargs_ex__ does not return a tuple containing (tuple, dict)*
  Used when a __getnewargs_ex__ method returns something which is not of the
  form tuple(tuple, dict)
:invalid-hash-returned (E0309): *__hash__ does not return int*
  Used when a __hash__ method returns something which is not an integer
:invalid-index-returned (E0305): *__index__ does not return int*
  Used when an __index__ method returns something which is not an integer
:non-iterator-returned (E0301): *__iter__ returns non-iterator*
  Used when an __iter__ method returns something which is not an iterable (i.e.
  has no `__next__` method)
:invalid-length-returned (E0303): *__len__ does not return non-negative integer*
  Used when a __len__ method returns something which is not a non-negative
  integer
:invalid-length-hint-returned (E0310): *__length_hint__ does not return non-negative integer*
  Used when a __length_hint__ method returns something which is not a non-
  negative integer
:invalid-repr-returned (E0306): *__repr__ does not return str*
  Used when a __repr__ method returns something which is not a string
:invalid-str-returned (E0307): *__str__ does not return str*
  Used when a __str__ method returns something which is not a string
:arguments-differ (W0221): *%s %s %r method*
  Used when a method has a different number of arguments than in the
  implemented interface or in an overridden method. Extra arguments with
  default values are ignored.
:arguments-renamed (W0237): *%s %s %r method*
  Used when a method parameter has a different name than in the implemented
  interface or in an overridden method.
:protected-access (W0212): *Access to a protected member %s of a client class*
  Used when a protected member (i.e. class member with a name beginning with an
  underscore) is accessed outside the class or a descendant of the class where
  it's defined.
:attribute-defined-outside-init (W0201): *Attribute %r defined outside __init__*
  Used when an instance attribute is defined outside the __init__ method.
:subclassed-final-class (W0240): *Class %r is a subclass of a class decorated with typing.final: %r*
  Used when a class decorated with typing.final has been subclassed.
:implicit-flag-alias (W0213): *Flag member %(overlap)s shares bit positions with %(sources)s*
  Used when multiple integer values declared within an enum.IntFlag class share
  a common bit position.
:abstract-method (W0223): *Method %r is abstract in class %r but is not overridden in child class %r*
  Used when an abstract method (i.e. raise NotImplementedError) is not
  overridden in concrete class.
:overridden-final-method (W0239): *Method %r overrides a method decorated with typing.final which is defined in class %r*
  Used when a method decorated with typing.final has been overridden.
:invalid-overridden-method (W0236): *Method %r was expected to be %r, found it instead as %r*
  Used when we detect that a method was overridden in a way that does not match
  its base class which could result in potential bugs at runtime.
:redefined-slots-in-subclass (W0244): *Redefined slots %r in subclass*
  Used when a slot is re-defined in a subclass.
:signature-differs (W0222): *Signature differs from %s %r method*
  Used when a method signature is different than in the implemented interface
  or in an overridden method.
:bad-staticmethod-argument (W0211): *Static method with %r as first argument*
  Used when a static method has "self" or a value specified in valid-
  classmethod-first-arg option or valid-metaclass-classmethod-first-arg option
  as first argument.
:super-without-brackets (W0245): *Super call without brackets*
  Used when a call to super does not have brackets and thus is not an actual
  call and does not work as expected.
:unused-private-member (W0238): *Unused private member `%s.%s`*
  Emitted when a private member of a class is defined but not used.
:useless-parent-delegation (W0246): *Useless parent or super() delegation in method %r*
  Used whenever we can detect that an overridden method is useless, relying on
  parent or super() delegation to do the same thing as another method from the
  MRO.
:non-parent-init-called (W0233): *__init__ method from a non direct base class %r is called*
  Used when an __init__ method is called on a class which is not in the direct
  ancestors for the analysed class.
:super-init-not-called (W0231): *__init__ method from base class %r is not called*
  Used when an ancestor class method has an __init__ method which is not called
  by a derived class.
:property-with-parameters (R0206): *Cannot have defined parameters for properties*
  Used when we detect that a property also has parameters, which are useless,
  given that properties cannot be called with additional arguments.
:useless-object-inheritance (R0205): *Class %r inherits from object, can be safely removed from bases in python3*
  Used when a class inherit from object, which under python3 is implicit, hence
  can be safely removed from bases.
:no-classmethod-decorator (R0202): *Consider using a decorator instead of calling classmethod*
  Used when a class method is defined without using the decorator syntax.
:no-staticmethod-decorator (R0203): *Consider using a decorator instead of calling staticmethod*
  Used when a static method is defined without using the decorator syntax.
:single-string-used-for-slots (C0205): *Class __slots__ should be a non-string iterable*
  Used when a class __slots__ is a simple string, rather than an iterable.
:bad-classmethod-argument (C0202): *Class method %s should have %s as first argument*
  Used when a class method has a first argument named differently than the
  value specified in valid-classmethod-first-arg option (default to "cls"),
  recommended to easily differentiate them from regular instance methods.
:bad-mcs-classmethod-argument (C0204): *Metaclass class method %s should have %s as first argument*
  Used when a metaclass class method has a first argument named differently
  than the value specified in valid-metaclass-classmethod-first-arg option
  (default to "mcs"), recommended to easily differentiate them from regular
  instance methods.
:bad-mcs-method-argument (C0203): *Metaclass method %s should have %s as first argument*
  Used when a metaclass method has a first argument named differently than the
  value specified in valid-classmethod-first-arg option (default to "cls"),
  recommended to easily differentiate them from regular instance methods.
:method-check-failed (F0202): *Unable to check methods signature (%s / %s)*
  Used when Pylint has been unable to check methods signature compatibility for
  an unexpected reason. Please report this kind if you don't make sense of it.


Dataclass checker
~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``dataclass``.

Dataclass checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^
:invalid-field-call (E3701): *Invalid usage of field(), %s*
  The dataclasses.field() specifier should only be used as the value of an
  assignment within a dataclass, or within the make_dataclass() function.


Design checker
~~~~~~~~~~~~~~

Verbatim name of the checker is ``design``.

See also :ref:`design checker's options' documentation <design-options>`

Design checker Messages
^^^^^^^^^^^^^^^^^^^^^^^
:too-few-public-methods (R0903): *Too few public methods (%s/%s)*
  Used when class has too few public methods, so be sure it's really worth it.
:too-many-ancestors (R0901): *Too many ancestors (%s/%s)*
  Used when class has too many parent classes, try to reduce this to get a
  simpler (and so easier to use) class.
:too-many-arguments (R0913): *Too many arguments (%s/%s)*
  Used when a function or method takes too many arguments.
:too-many-boolean-expressions (R0916): *Too many boolean expressions in if statement (%s/%s)*
  Used when an if statement contains too many boolean expressions.
:too-many-branches (R0912): *Too many branches (%s/%s)*
  Used when a function or method has too many branches, making it hard to
  follow.
:too-many-instance-attributes (R0902): *Too many instance attributes (%s/%s)*
  Used when class has too many instance attributes, try to reduce this to get a
  simpler (and so easier to use) class.
:too-many-locals (R0914): *Too many local variables (%s/%s)*
  Used when a function or method has too many local variables.
:too-many-positional-arguments (R0917): *Too many positional arguments (%s/%s)*
  Used when a function has too many positional arguments.
:too-many-public-methods (R0904): *Too many public methods (%s/%s)*
  Used when class has too many public methods, try to reduce this to get a
  simpler (and so easier to use) class.
:too-many-return-statements (R0911): *Too many return statements (%s/%s)*
  Used when a function or method has too many return statement, making it hard
  to follow.
:too-many-statements (R0915): *Too many statements (%s/%s)*
  Used when a function or method has too many statements. You should then split
  it in smaller functions / methods.


Exceptions checker
~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``exceptions``.

See also :ref:`exceptions checker's options' documentation <exceptions-options>`

Exceptions checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^
:bad-except-order (E0701): *Bad except clauses order (%s)*
  Used when except clauses are not in the correct order (from the more specific
  to the more generic). If you don't fix the order, some exceptions may not be
  caught by the most specific handler.
:catching-non-exception (E0712): *Catching an exception which doesn't inherit from Exception: %s*
  Used when a class which doesn't inherit from Exception is used as an
  exception in an except clause.
:bad-exception-cause (E0705): *Exception cause set to something which is not an exception, nor None*
  Used when using the syntax "raise ... from ...", where the exception cause is
  not an exception, nor None.
:notimplemented-raised (E0711): *NotImplemented raised - should raise NotImplementedError*
  Used when NotImplemented is raised instead of NotImplementedError
:raising-bad-type (E0702): *Raising %s while only classes or instances are allowed*
  Used when something which is neither a class nor an instance is raised (i.e.
  a `TypeError` will be raised).
:raising-non-exception (E0710): *Raising a class which doesn't inherit from BaseException*
  Used when a class which doesn't inherit from BaseException is raised.
:misplaced-bare-raise (E0704): *The raise statement is not inside an except clause*
  Used when a bare raise is not used inside an except clause. This generates an
  error, since there are no active exceptions to be reraised. An exception to
  this rule is represented by a bare raise inside a finally clause, which might
  work, as long as an exception is raised inside the try block, but it is
  nevertheless a code smell that must not be relied upon.
:duplicate-except (W0705): *Catching previously caught exception type %s*
  Used when an except catches a type that was already caught by a previous
  handler.
:broad-exception-caught (W0718): *Catching too general exception %s*
  If you use a naked ``except Exception:`` clause, you might end up catching
  exceptions other than the ones you expect to catch. This can hide bugs or
  make it harder to debug programs when unrelated errors are hidden.
:raise-missing-from (W0707): *Consider explicitly re-raising using %s'%s from %s'*
  Python's exception chaining shows the traceback of the current exception, but
  also of the original exception. When you raise a new exception after another
  exception was caught it's likely that the second exception is a friendly re-
  wrapping of the first exception. In such cases `raise from` provides a better
  link between the two tracebacks in the final error.
:raising-format-tuple (W0715): *Exception arguments suggest string formatting might be intended*
  Used when passing multiple arguments to an exception constructor, the first
  of them a string literal containing what appears to be placeholders intended
  for formatting
:binary-op-exception (W0711): *Exception to catch is the result of a binary "%s" operation*
  Used when the exception to catch is of the form "except A or B:". If
  intending to catch multiple, rewrite as "except (A, B):"
:wrong-exception-operation (W0716): *Invalid exception operation. %s*
  Used when an operation is done against an exception, but the operation is not
  valid for the exception in question. Usually emitted when having binary
  operations between exceptions in except handlers.
:bare-except (W0702): *No exception type(s) specified*
  A bare ``except:`` clause will catch ``SystemExit`` and ``KeyboardInterrupt``
  exceptions, making it harder to interrupt a program with ``Control-C``, and
  can disguise other problems. If you want to catch all exceptions that signal
  program errors, use ``except Exception:`` (bare except is equivalent to
  ``except BaseException:``).
:broad-exception-raised (W0719): *Raising too general exception: %s*
  Raising exceptions that are too generic force you to catch exceptions
  generically too. It will force you to use a naked ``except Exception:``
  clause. You might then end up catching exceptions other than the ones you
  expect to catch. This can hide bugs or make it harder to debug programs when
  unrelated errors are hidden.
:try-except-raise (W0706): *The except handler raises immediately*
  Used when an except handler uses raise as its first or only operator. This is
  useless because it raises back the exception immediately. Remove the raise
  operator or the entire try-except-raise block!


Format checker
~~~~~~~~~~~~~~

Verbatim name of the checker is ``format``.

See also :ref:`format checker's options' documentation <format-options>`

Format checker Messages
^^^^^^^^^^^^^^^^^^^^^^^
:bad-indentation (W0311): *Bad indentation. Found %s %s, expected %s*
  Used when an unexpected number of indentation's tabulations or spaces has
  been found.
:unnecessary-semicolon (W0301): *Unnecessary semicolon*
  Used when a statement is ended by a semi-colon (";"), which isn't necessary
  (that's python, not C ;).
:missing-final-newline (C0304): *Final newline missing*
  Used when the last line in a file is missing a newline.
:line-too-long (C0301): *Line too long (%s/%s)*
  Used when a line is longer than a given number of characters.
:mixed-line-endings (C0327): *Mixed line endings LF and CRLF*
  Used when there are mixed (LF and CRLF) newline signs in a file.
:multiple-statements (C0321): *More than one statement on a single line*
  Used when more than on statement are found on the same line.
:too-many-lines (C0302): *Too many lines in module (%s/%s)*
  Used when a module has too many lines, reducing its readability.
:trailing-newlines (C0305): *Trailing newlines*
  Used when there are trailing blank lines in a file.
:trailing-whitespace (C0303): *Trailing whitespace*
  Used when there is whitespace between the end of a line and the newline.
:unexpected-line-ending-format (C0328): *Unexpected line ending format. There is '%s' while it should be '%s'.*
  Used when there is different newline than expected.
:superfluous-parens (C0325): *Unnecessary parens after %r keyword*
  Used when a single item in parentheses follows an if, for, or other keyword.


Imports checker
~~~~~~~~~~~~~~~

Verbatim name of the checker is ``imports``.

See also :ref:`imports checker's options' documentation <imports-options>`

Imports checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^
:relative-beyond-top-level (E0402): *Attempted relative import beyond top-level package*
  Used when a relative import tries to access too many levels in the current
  package.
:import-error (E0401): *Unable to import %s*
  Used when pylint has been unable to import a module.
:deprecated-module (W4901): *Deprecated module %r*
  A module marked as deprecated is imported.
:import-self (W0406): *Module import itself*
  Used when a module is importing itself.
:preferred-module (W0407): *Prefer importing %r instead of %r*
  Used when a module imported has a preferred replacement module.
:reimported (W0404): *Reimport %r (imported line %s)*
  Used when a module is imported more than once.
:shadowed-import (W0416): *Shadowed %r (imported line %s)*
  Used when a module is aliased with a name that shadows another import.
:wildcard-import (W0401): *Wildcard import %s*
  Used when `from module import *` is detected.
:misplaced-future (W0410): *__future__ import is not the first non docstring statement*
  Python 2.5 and greater require __future__ import to be the first non
  docstring statement in the module.
:cyclic-import (R0401): *Cyclic import (%s)*
  Used when a cyclic import between two or more modules is detected.
:consider-using-from-import (R0402): *Use 'from %s import %s' instead*
  Emitted when a submodule of a package is imported and aliased with the same
  name, e.g., instead of ``import concurrent.futures as futures`` use ``from
  concurrent import futures``.
:wrong-import-order (C0411): *%s should be placed before %s*
  Used when PEP8 import order is not respected (standard imports first, then
  third-party libraries, then local imports).
:wrong-import-position (C0413): *Import "%s" should be placed at the top of the module*
  Used when code and imports are mixed.
:useless-import-alias (C0414): *Import alias does not rename original package*
  Used when an import alias is same as original package, e.g., using import
  numpy as numpy instead of import numpy as np.
:import-outside-toplevel (C0415): *Import outside toplevel (%s)*
  Used when an import statement is used anywhere other than the module
  toplevel. Move this import to the top of the file.
:ungrouped-imports (C0412): *Imports from package %s are not grouped*
  Used when imports are not grouped by packages.
:multiple-imports (C0410): *Multiple imports on one line (%s)*
  Used when import statement importing multiple modules is detected.

Imports checker Reports
^^^^^^^^^^^^^^^^^^^^^^^
:RP0401: External dependencies
:RP0402: Modules dependencies graph


Lambda-Expressions checker
~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``lambda-expressions``.

Lambda-Expressions checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:unnecessary-lambda-assignment (C3001): *Lambda expression assigned to a variable. Define a function using the "def" keyword instead.*
  Used when a lambda expression is assigned to variable rather than defining a
  standard function with the "def" keyword.
:unnecessary-direct-lambda-call (C3002): *Lambda expression called directly. Execute the expression inline instead.*
  Used when a lambda expression is directly called rather than executing its
  contents inline.


Logging checker
~~~~~~~~~~~~~~~

Verbatim name of the checker is ``logging``.

See also :ref:`logging checker's options' documentation <logging-options>`

Logging checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^
:logging-format-truncated (E1201): *Logging format string ends in middle of conversion specifier*
  Used when a logging statement format string terminates before the end of a
  conversion specifier.
:logging-too-few-args (E1206): *Not enough arguments for logging format string*
  Used when a logging format string is given too few arguments.
:logging-too-many-args (E1205): *Too many arguments for logging format string*
  Used when a logging format string is given too many arguments.
:logging-unsupported-format (E1200): *Unsupported logging format character %r (%#02x) at index %d*
  Used when an unsupported format character is used in a logging statement
  format string.
:logging-format-interpolation (W1202): *Use %s formatting in logging functions*
  Used when a logging statement has a call form of "logging.<logging
  method>(format_string.format(format_args...))". Use another type of string
  formatting instead. You can use % formatting but leave interpolation to the
  logging function by passing the parameters as arguments. If logging-fstring-
  interpolation is disabled then you can use fstring formatting. If logging-
  not-lazy is disabled then you can use % formatting as normal.
:logging-fstring-interpolation (W1203): *Use %s formatting in logging functions*
  Used when a logging statement has a call form of "logging.<logging
  method>(f"...")".Use another type of string formatting instead. You can use %
  formatting but leave interpolation to the logging function by passing the
  parameters as arguments. If logging-format-interpolation is disabled then you
  can use str.format. If logging-not-lazy is disabled then you can use %
  formatting as normal.
:logging-not-lazy (W1201): *Use %s formatting in logging functions*
  Used when a logging statement has a call form of "logging.<logging
  method>(format_string % (format_args...))". Use another type of string
  formatting instead. You can use % formatting but leave interpolation to the
  logging function by passing the parameters as arguments. If logging-fstring-
  interpolation is disabled then you can use fstring formatting. If logging-
  format-interpolation is disabled then you can use str.format.


Match Statements checker
~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``match_statements``.

Match Statements checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:bare-name-capture-pattern (E1901): *The name capture `case %s` makes the remaining patterns unreachable. Use a dotted name (for example an enum) to fix this.*
  Emitted when a name capture pattern is used in a match statement and there
  are case statements below it.


Method Args checker
~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``method_args``.

See also :ref:`method_args checker's options' documentation <method_args-options>`

Method Args checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:positional-only-arguments-expected (E3102): *`%s()` got some positional-only arguments passed as keyword arguments: %s*
  Emitted when positional-only arguments have been passed as keyword arguments.
  Remove the keywords for the affected arguments in the function call.
:missing-timeout (W3101): *Missing timeout argument for method '%s' can cause your program to hang indefinitely*
  Used when a method needs a 'timeout' parameter in order to avoid waiting for
  a long time. If no timeout is specified explicitly the default value is used.
  For example for 'requests' the program will never time out (i.e. hang
  indefinitely).


Metrics checker
~~~~~~~~~~~~~~~

Verbatim name of the checker is ``metrics``.

Metrics checker Reports
^^^^^^^^^^^^^^^^^^^^^^^
:RP0701: Raw metrics


Miscellaneous checker
~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``miscellaneous``.

See also :ref:`miscellaneous checker's options' documentation <miscellaneous-options>`

Miscellaneous checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:fixme (W0511):
  Used when a warning note as FIXME or XXX is detected.
:use-symbolic-message-instead (I0023):
  Used when a message is enabled or disabled by id.


Modified Iteration checker
~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``modified_iteration``.

Modified Iteration checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:modified-iterating-dict (E4702): *Iterated dict '%s' is being modified inside for loop body, iterate through a copy of it instead.*
  Emitted when items are added or removed to a dict being iterated through.
  Doing so raises a RuntimeError.
:modified-iterating-set (E4703): *Iterated set '%s' is being modified inside for loop body, iterate through a copy of it instead.*
  Emitted when items are added or removed to a set being iterated through.
  Doing so raises a RuntimeError.
:modified-iterating-list (W4701): *Iterated list '%s' is being modified inside for loop body, consider iterating through a copy of it instead.*
  Emitted when items are added or removed to a list being iterated through.
  Doing so can result in unexpected behaviour, that is why it is preferred to
  use a copy of the list.


Nested Min Max checker
~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``nested_min_max``.

Nested Min Max checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:nested-min-max (W3301): *Do not use nested call of '%s'; it's possible to do '%s' instead*
  Nested calls ``min(1, min(2, 3))`` can be rewritten as ``min(1, 2, 3)``.


Newstyle checker
~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``newstyle``.

Newstyle checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^
:bad-super-call (E1003): *Bad first argument %r given to super()*
  Used when another argument than the current class is given as first argument
  of the super builtin.


Nonascii-Checker checker
~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``nonascii-checker``.

Nonascii-Checker checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:non-ascii-file-name (W2402): *%s name "%s" contains a non-ASCII character.*
  Under python 3.5, PEP 3131 allows non-ascii identifiers, but not non-ascii
  file names.Since Python 3.5, even though Python supports UTF-8 files, some
  editors or tools don't.
:non-ascii-name (C2401): *%s name "%s" contains a non-ASCII character, consider renaming it.*
  Used when the name contains at least one non-ASCII unicode character. See
  https://peps.python.org/pep-0672/#confusing-features for a background why
  this could be bad. If your programming guideline defines that you are
  programming in English, then there should be no need for non ASCII characters
  in Python Names. If not you can simply disable this check.
:non-ascii-module-import (C2403): *%s name "%s" contains a non-ASCII character, use an ASCII-only alias for import.*
  Used when the name contains at least one non-ASCII unicode character. See
  https://peps.python.org/pep-0672/#confusing-features for a background why
  this could be bad. If your programming guideline defines that you are
  programming in English, then there should be no need for non ASCII characters
  in Python Names. If not you can simply disable this check.


Refactoring checker
~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``refactoring``.

See also :ref:`refactoring checker's options' documentation <refactoring-options>`

Refactoring checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:simplifiable-condition (R1726): *Boolean condition "%s" may be simplified to "%s"*
  Emitted when a boolean condition is able to be simplified.
:condition-evals-to-constant (R1727): *Boolean condition '%s' will always evaluate to '%s'*
  Emitted when a boolean condition can be simplified to a constant value.
:simplify-boolean-expression (R1709): *Boolean expression may be simplified to %s*
  Emitted when redundant pre-python 2.5 ternary syntax is used.
:consider-using-in (R1714): *Consider merging these comparisons with 'in' by using '%s %sin (%s)'. Use a set instead if elements are hashable.*
  To check if a variable is equal to one of many values, combine the values
  into a set or tuple and check if the variable is contained "in" it instead of
  checking for equality against each of the values. This is faster and less
  verbose.
:consider-merging-isinstance (R1701): *Consider merging these isinstance calls to isinstance(%s, (%s))*
  Used when multiple consecutive isinstance calls can be merged into one.
:use-dict-literal (R1735): *Consider using '%s' instead of a call to 'dict'.*
  Emitted when using dict() to create a dictionary instead of a literal '{ ...
  }'. The literal is faster as it avoids an additional function call.
:consider-using-max-builtin (R1731): *Consider using '%s' instead of unnecessary if block*
  Using the max builtin instead of a conditional improves readability and
  conciseness.
:consider-using-min-builtin (R1730): *Consider using '%s' instead of unnecessary if block*
  Using the min builtin instead of a conditional improves readability and
  conciseness.
:consider-using-sys-exit (R1722): *Consider using 'sys.exit' instead*
  Contrary to 'exit()' or 'quit()', 'sys.exit' does not rely on the site module
  being available (as the 'sys' module is always available).
:consider-using-with (R1732): *Consider using 'with' for resource-allocating operations*
  Emitted if a resource-allocating assignment or call may be replaced by a
  'with' block. By using 'with' the release of the allocated resources is
  ensured even in the case of an exception.
:super-with-arguments (R1725): *Consider using Python 3 style super() without arguments*
  Emitted when calling the super() builtin with the current class and instance.
  On Python 3 these arguments are the default and they can be omitted.
:use-list-literal (R1734): *Consider using [] instead of list()*
  Emitted when using list() to create an empty list instead of the literal [].
  The literal is faster as it avoids an additional function call.
:consider-using-dict-comprehension (R1717): *Consider using a dictionary comprehension*
  Emitted when we detect the creation of a dictionary using the dict() callable
  and a transient list. Although there is nothing syntactically wrong with this
  code, it is hard to read and can be simplified to a dict comprehension. Also
  it is faster since you don't need to create another transient list
:consider-using-generator (R1728): *Consider using a generator instead '%s(%s)'*
  If your container can be large using a generator will bring better
  performance.
:consider-using-set-comprehension (R1718): *Consider using a set comprehension*
  Although there is nothing syntactically wrong with this code, it is hard to
  read and can be simplified to a set comprehension. Also it is faster since
  you don't need to create another transient list
:consider-using-get (R1715): *Consider using dict.get for getting values from a dict if a key is present or a default if not*
  Using the builtin dict.get for getting a value from a dictionary if a key is
  present or a default if not, is simpler and considered more idiomatic,
  although sometimes a bit slower
:consider-using-join (R1713): *Consider using str.join(sequence) for concatenating strings from an iterable*
  Using str.join(sequence) is faster, uses less memory and increases
  readability compared to for-loop iteration.
:consider-using-ternary (R1706): *Consider using ternary (%s)*
  Used when one of known pre-python 2.5 ternary syntax is used.
:consider-swap-variables (R1712): *Consider using tuple unpacking for swapping variables*
  You do not have to use a temporary variable in order to swap variables. Using
  "tuple unpacking" to directly swap variables makes the intention more clear.
:trailing-comma-tuple (R1707): *Disallow trailing comma tuple*
  In Python, a tuple is actually created by the comma symbol, not by the
  parentheses. Unfortunately, one can actually create a tuple by misplacing a
  trailing comma, which can lead to potential weird bugs in your code. You
  should always use parentheses explicitly for creating a tuple.
:stop-iteration-return (R1708): *Do not raise StopIteration in generator, use return statement instead*
  According to PEP479, the raise of StopIteration to end the loop of a
  generator may lead to hard to find bugs. This PEP specify that raise
  StopIteration has to be replaced by a simple return statement
:inconsistent-return-statements (R1710): *Either all return statements in a function should return an expression, or none of them should.*
  According to PEP8, if any return statement returns an expression, any return
  statements where no value is returned should explicitly state this as return
  None, and an explicit return statement should be present at the end of the
  function (if reachable)
:redefined-argument-from-local (R1704): *Redefining argument with the local name %r*
  Used when a local name is redefining an argument, which might suggest a
  potential error. This is taken in account only for a handful of name binding
  operations, such as for iteration, with statement assignment and exception
  handler assignment.
:chained-comparison (R1716): *Simplify chained comparison between the operands*
  This message is emitted when pylint encounters boolean operation like "a < b
  and b < c", suggesting instead to refactor it to "a < b < c"
:simplifiable-if-expression (R1719): *The if expression can be replaced with %s*
  Used when an if expression can be replaced with 'bool(test)' or simply 'test'
  if the boolean cast is implicit.
:simplifiable-if-statement (R1703): *The if statement can be replaced with %s*
  Used when an if statement can be replaced with 'bool(test)'.
:too-many-nested-blocks (R1702): *Too many nested blocks (%s/%s)*
  Used when a function or a method has too many nested blocks. This makes the
  code less understandable and maintainable.
:no-else-break (R1723): *Unnecessary "%s" after "break", %s*
  Used in order to highlight an unnecessary block of code following an if
  containing a break statement. As such, it will warn when it encounters an
  else following a chain of ifs, all of them containing a break statement.
:no-else-continue (R1724): *Unnecessary "%s" after "continue", %s*
  Used in order to highlight an unnecessary block of code following an if
  containing a continue statement. As such, it will warn when it encounters an
  else following a chain of ifs, all of them containing a continue statement.
:no-else-raise (R1720): *Unnecessary "%s" after "raise", %s*
  Used in order to highlight an unnecessary block of code following an if, or a
  try/except containing a raise statement. As such, it will warn when it
  encounters an else following a chain of ifs, all of them containing a raise
  statement.
:no-else-return (R1705): *Unnecessary "%s" after "return", %s*
  Used in order to highlight an unnecessary block of code following an if, or a
  try/except containing a return statement. As such, it will warn when it
  encounters an else following a chain of ifs, all of them containing a return
  statement.
:unnecessary-dict-index-lookup (R1733): *Unnecessary dictionary index lookup, use '%s' instead*
  Emitted when iterating over the dictionary items (key-item pairs) and
  accessing the value by index lookup. The value can be accessed directly
  instead.
:unnecessary-list-index-lookup (R1736): *Unnecessary list index lookup, use '%s' instead*
  Emitted when iterating over an enumeration and accessing the value by index
  lookup. The value can be accessed directly instead.
:unnecessary-comprehension (R1721): *Unnecessary use of a comprehension, use %s instead.*
  Instead of using an identity comprehension, consider using the list, dict or
  set constructor. It is faster and simpler.
:use-yield-from (R1737): *Use 'yield from' directly instead of yielding each element one by one*
  Yielding directly from the iterator is faster and arguably cleaner code than
  yielding each element one by one in the loop.
:use-a-generator (R1729): *Use a generator instead '%s(%s)'*
  Comprehension inside of 'any', 'all', 'max', 'min' or 'sum' is unnecessary. A
  generator would be sufficient and faster.
:useless-return (R1711): *Useless return at end of function or method*
  Emitted when a single "return" or "return None" statement is found at the end
  of function or method definition. This statement can safely be removed
  because Python will implicitly return None
:use-implicit-booleaness-not-comparison (C1803): *"%s" can be simplified to "%s", if it is strictly a sequence, as an empty %s is falsey*
  Empty sequences are considered false in a boolean context. Following this
  check blindly in weakly typed code base can create hard to debug issues. If
  the value can be something else that is falsey but not a sequence (for
  example ``None``, an empty string, or ``0``) the code will not be equivalent.
:use-implicit-booleaness-not-comparison-to-string (C1804): *"%s" can be simplified to "%s", if it is strictly a string, as an empty string is falsey*
  Empty string are considered false in a boolean context. Following this check
  blindly in weakly typed code base can create hard to debug issues. If the
  value can be something else that is falsey but not a string (for example
  ``None``, an empty sequence, or ``0``) the code will not be equivalent.
:use-implicit-booleaness-not-comparison-to-zero (C1805): *"%s" can be simplified to "%s", if it is strictly an int, as 0 is falsey*
  0 is considered false in a boolean context. Following this check blindly in
  weakly typed code base can create hard to debug issues. If the value can be
  something else that is falsey but not an int (for example ``None``, an empty
  string, or an empty sequence) the code will not be equivalent.
:unnecessary-negation (C0117): *Consider changing "%s" to "%s"*
  Used when a boolean expression contains an unneeded negation, e.g. when two
  negation operators cancel each other out.
:consider-iterating-dictionary (C0201): *Consider iterating the dictionary directly instead of calling .keys()*
  Emitted when the keys of a dictionary are iterated through the ``.keys()``
  method or when ``.keys()`` is used for a membership check. It is enough to
  iterate through the dictionary itself, ``for key in dictionary``. For
  membership checks, ``if key in dictionary`` is faster.
:consider-using-dict-items (C0206): *Consider iterating with .items()*
  Emitted when iterating over the keys of a dictionary and accessing the value
  by index lookup. Both the key and value can be accessed by iterating using
  the .items() method of the dictionary instead.
:consider-using-enumerate (C0200): *Consider using enumerate instead of iterating with range and len*
  Emitted when code that iterates with range and len is encountered. Such code
  can be simplified by using the enumerate builtin.
:use-implicit-booleaness-not-len (C1802): *Do not use `len(SEQUENCE)` without comparison to determine if a sequence is empty*
  Empty sequences are considered false in a boolean context. You can either
  remove the call to 'len' (``if not x``) or compare the length against a
  scalar (``if len(x) > 1``).
:consider-using-f-string (C0209): *Formatting a regular string which could be an f-string*
  Used when we detect a string that is being formatted with format() or % which
  could potentially be an f-string. The use of f-strings is preferred. Requires
  Python 3.6 and ``py-version >= 3.6``.
:use-maxsplit-arg (C0207): *Use %s instead*
  Emitted when accessing only the first or last element of str.split(). The
  first and last element can be accessed by using str.split(sep, maxsplit=1)[0]
  or str.rsplit(sep, maxsplit=1)[-1] instead.
:use-sequence-for-iteration (C0208): *Use a sequence type when iterating over values*
  When iterating over values, sequence types (e.g., ``lists``, ``tuples``,
  ``ranges``) are more efficient than ``sets``.


Similarities checker
~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``similarities``.

See also :ref:`similarities checker's options' documentation <similarities-options>`

Similarities checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:duplicate-code (R0801): *Similar lines in %s files*
  Indicates that a set of similar lines has been detected among multiple file.
  This usually means that the code should be refactored to avoid this
  duplication.

Similarities checker Reports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:RP0801: Duplication


Spelling checker
~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``spelling``.

See also :ref:`spelling checker's options' documentation <spelling-options>`

Spelling checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^
:invalid-characters-in-docstring (C0403): *Invalid characters %r in a docstring*
  Used when a word in docstring cannot be checked by enchant.
:wrong-spelling-in-comment (C0401): *Wrong spelling of a word '%s' in a comment:*
  Used when a word in comment is not spelled correctly.
:wrong-spelling-in-docstring (C0402): *Wrong spelling of a word '%s' in a docstring:*
  Used when a word in docstring is not spelled correctly.


Stdlib checker
~~~~~~~~~~~~~~

Verbatim name of the checker is ``stdlib``.

Stdlib checker Messages
^^^^^^^^^^^^^^^^^^^^^^^
:invalid-envvar-value (E1507): *%s does not support %s type argument*
  Env manipulation functions support only string type arguments. See
  https://docs.python.org/3/library/os.html#os.getenv.
:singledispatch-method (E1519): *singledispatch decorator should not be used with methods, use singledispatchmethod instead.*
  singledispatch should decorate functions and not class/instance methods. Use
  singledispatchmethod for those cases.
:singledispatchmethod-function (E1520): *singledispatchmethod decorator should not be used with functions, use singledispatch instead.*
  singledispatchmethod should decorate class/instance methods and not
  functions. Use singledispatch for those cases.
:bad-open-mode (W1501): *"%s" is not a valid mode for open.*
  Python supports: r, w, a[, x] modes with b, +, and U (only with r) options.
  See https://docs.python.org/3/library/functions.html#open
:invalid-envvar-default (W1508): *%s default type is %s. Expected str or None.*
  Env manipulation functions return None or str values. Supplying anything
  different as a default may cause bugs. See
  https://docs.python.org/3/library/os.html#os.getenv.
:method-cache-max-size-none (W1518): *'lru_cache(maxsize=None)' or 'cache' will keep all method args alive indefinitely, including 'self'*
  By decorating a method with lru_cache or cache the 'self' argument will be
  linked to the function and therefore never garbage collected. Unless your
  instance will never need to be garbage collected (singleton) it is
  recommended to refactor code to avoid this pattern or add a maxsize to the
  cache. The default value for maxsize is 128.
:subprocess-run-check (W1510): *'subprocess.run' used without explicitly defining the value for 'check'.*
  The ``check`` keyword is set to False by default. It means the process
  launched by ``subprocess.run`` can exit with a non-zero exit code and fail
  silently. It's better to set it explicitly to make clear what the error-
  handling behavior is.
:forgotten-debug-statement (W1515): *Leaving functions creating breakpoints in production code is not recommended*
  Calls to breakpoint(), sys.breakpointhook() and pdb.set_trace() should be
  removed from code that is not actively being debugged.
:redundant-unittest-assert (W1503): *Redundant use of %s with constant value %r*
  The first argument of assertTrue and assertFalse is a condition. If a
  constant is passed as parameter, that condition will be always true. In this
  case a warning should be emitted.
:shallow-copy-environ (W1507): *Using copy.copy(os.environ). Use os.environ.copy() instead.*
  os.environ is not a dict object but proxy object, so shallow copy has still
  effects on original object. See https://bugs.python.org/issue15373 for
  reference.
:boolean-datetime (W1502): *Using datetime.time in a boolean context.*
  Using datetime.time in a boolean context can hide subtle bugs when the time
  they represent matches midnight UTC. This behaviour was fixed in Python 3.5.
  See https://bugs.python.org/issue13936 for reference. This message can't be
  emitted when using Python >= 3.5.
:deprecated-argument (W4903): *Using deprecated argument %s of method %s()*
  The argument is marked as deprecated and will be removed in the future.
:deprecated-attribute (W4906): *Using deprecated attribute %r*
  The attribute is marked as deprecated and will be removed in the future.
:deprecated-class (W4904): *Using deprecated class %s of module %s*
  The class is marked as deprecated and will be removed in the future.
:deprecated-decorator (W4905): *Using deprecated decorator %s()*
  The decorator is marked as deprecated and will be removed in the future.
:deprecated-method (W4902): *Using deprecated method %s()*
  The method is marked as deprecated and will be removed in the future.
:unspecified-encoding (W1514): *Using open without explicitly specifying an encoding*
  It is better to specify an encoding when opening documents. Using the system
  default implicitly can create problems on other operating systems. See
  https://peps.python.org/pep-0597/
:subprocess-popen-preexec-fn (W1509): *Using preexec_fn keyword which may be unsafe in the presence of threads*
  The preexec_fn parameter is not safe to use in the presence of threads in
  your application. The child process could deadlock before exec is called. If
  you must use it, keep it trivial! Minimize the number of libraries you call
  into. See https://docs.python.org/3/library/subprocess.html#popen-constructor
:bad-thread-instantiation (W1506): *threading.Thread needs the target function*
  The warning is emitted when a threading.Thread class is instantiated without
  the target function being passed as a kwarg or as a second argument. By
  default, the first parameter is the group param, not the target param.


String checker
~~~~~~~~~~~~~~

Verbatim name of the checker is ``string``.

See also :ref:`string checker's options' documentation <string-options>`

String checker Messages
^^^^^^^^^^^^^^^^^^^^^^^
:bad-string-format-type (E1307): *Argument %r does not match format type %r*
  Used when a type required by format string is not suitable for actual
  argument type
:format-needs-mapping (E1303): *Expected mapping for format string, not %s*
  Used when a format string that uses named conversion specifiers is used with
  an argument that is not a mapping.
:truncated-format-string (E1301): *Format string ends in middle of conversion specifier*
  Used when a format string terminates before the end of a conversion
  specifier.
:missing-format-string-key (E1304): *Missing key %r in format string dictionary*
  Used when a format string that uses named conversion specifiers is used with
  a dictionary that doesn't contain all the keys required by the format string.
:mixed-format-string (E1302): *Mixing named and unnamed conversion specifiers in format string*
  Used when a format string contains both named (e.g. '%(foo)d') and unnamed
  (e.g. '%d') conversion specifiers. This is also used when a named conversion
  specifier contains * for the minimum field width and/or precision.
:too-few-format-args (E1306): *Not enough arguments for format string*
  Used when a format string that uses unnamed conversion specifiers is given
  too few arguments
:bad-str-strip-call (E1310): *Suspicious argument in %s.%s call*
  The argument to a str.{l,r,}strip call contains a duplicate character,
:too-many-format-args (E1305): *Too many arguments for format string*
  Used when a format string that uses unnamed conversion specifiers is given
  too many arguments.
:bad-format-character (E1300): *Unsupported format character %r (%#02x) at index %d*
  Used when an unsupported format character is used in a format string.
:anomalous-unicode-escape-in-string (W1402): *Anomalous Unicode escape in byte string: '%s'. String constant might be missing an r or u prefix.*
  Used when an escape like \u is encountered in a byte string where it has no
  effect.
:anomalous-backslash-in-string (W1401): *Anomalous backslash in string: '%s'. String constant might be missing an r prefix.*
  Used when a backslash is in a literal string but not as an escape.
:duplicate-string-formatting-argument (W1308): *Duplicate string formatting argument %r, consider passing as named argument*
  Used when we detect that a string formatting is repeating an argument instead
  of using named string arguments
:format-combined-specification (W1305): *Format string contains both automatic field numbering and manual field specification*
  Used when a PEP 3101 format string contains both automatic field numbering
  (e.g. '{}') and manual field specification (e.g. '{0}').
:bad-format-string-key (W1300): *Format string dictionary key should be a string, not %s*
  Used when a format string that uses named conversion specifiers is used with
  a dictionary whose keys are not all strings.
:implicit-str-concat (W1404): *Implicit string concatenation found in %s*
  String literals are implicitly concatenated in a literal iterable definition
  : maybe a comma is missing ?
:bad-format-string (W1302): *Invalid format string*
  Used when a PEP 3101 format string is invalid.
:missing-format-attribute (W1306): *Missing format attribute %r in format specifier %r*
  Used when a PEP 3101 format string uses an attribute specifier ({0.length}),
  but the argument passed for formatting doesn't have that attribute.
:missing-format-argument-key (W1303): *Missing keyword argument %r for format string*
  Used when a PEP 3101 format string that uses named fields doesn't receive one
  or more required keywords.
:inconsistent-quotes (W1405): *Quote delimiter %s is inconsistent with the rest of the file*
  Quote delimiters are not used consistently throughout a module (with
  allowances made for avoiding unnecessary escaping).
:redundant-u-string-prefix (W1406): *The u prefix for strings is no longer necessary in Python >=3.0*
  Used when we detect a string with a u prefix. These prefixes were necessary
  in Python 2 to indicate a string was Unicode, but since Python 3.0 strings
  are Unicode by default.
:unused-format-string-argument (W1304): *Unused format argument %r*
  Used when a PEP 3101 format string that uses named fields is used with an
  argument that is not required by the format string.
:unused-format-string-key (W1301): *Unused key %r in format string dictionary*
  Used when a format string that uses named conversion specifiers is used with
  a dictionary that contains keys not required by the format string.
:f-string-without-interpolation (W1309): *Using an f-string that does not have any interpolated variables*
  Used when we detect an f-string that does not use any interpolation
  variables, in which case it can be either a normal string or a bug in the
  code.
:format-string-without-interpolation (W1310): *Using formatting for a string that does not have any interpolated variables*
  Used when we detect a string that does not have any interpolation variables,
  in which case it can be either a normal string without formatting or a bug in
  the code.
:invalid-format-index (W1307): *Using invalid lookup key %r in format specifier %r*
  Used when a PEP 3101 format string uses a lookup specifier ({a[1]}), but the
  argument passed for formatting doesn't contain or doesn't have that key as an
  attribute.


Threading checker
~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``threading``.

Threading checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^
:useless-with-lock (W2101): *'%s()' directly created in 'with' has no effect*
  Used when a new lock instance is created by using with statement which has no
  effect. Instead, an existing instance should be used to acquire lock.


Typecheck checker
~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``typecheck``.

See also :ref:`typecheck checker's options' documentation <typecheck-options>`

Typecheck checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^
:unsupported-assignment-operation (E1137): *%r does not support item assignment*
  Emitted when an object does not support item assignment (i.e. doesn't define
  __setitem__ method).
:unsupported-delete-operation (E1138): *%r does not support item deletion*
  Emitted when an object does not support item deletion (i.e. doesn't define
  __delitem__ method).
:invalid-unary-operand-type (E1130):
  Emitted when a unary operand is used on an object which does not support this
  type of operation.
:unsupported-binary-operation (E1131):
  Emitted when a binary arithmetic operation between two operands is not
  supported.
:no-member (E1101): *%s %r has no %r member%s*
  Used when a variable is accessed for a nonexistent member.
:not-callable (E1102): *%s is not callable*
  Used when an object being called has been inferred to a non callable object.
:unhashable-member (E1143): *'%s' is unhashable and can't be used as a %s in a %s*
  Emitted when a dict key or set member is not hashable (i.e. doesn't define
  __hash__ method).
:await-outside-async (E1142): *'await' should be used within an async function*
  Emitted when await is used outside an async function.
:redundant-keyword-arg (E1124): *Argument %r passed by position and keyword in %s call*
  Used when a function call would result in assigning multiple values to a
  function parameter, one value from a positional argument and one from a
  keyword argument.
:assignment-from-no-return (E1111): *Assigning result of a function call, where the function has no return*
  Used when an assignment is done on a function call but the inferred function
  doesn't return anything.
:assignment-from-none (E1128): *Assigning result of a function call, where the function returns None*
  Used when an assignment is done on a function call but the inferred function
  returns nothing but None.
:not-context-manager (E1129): *Context manager '%s' doesn't implement __enter__ and __exit__.*
  Used when an instance in a with statement doesn't implement the context
  manager protocol(__enter__/__exit__).
:repeated-keyword (E1132): *Got multiple values for keyword argument %r in function call*
  Emitted when a function call got multiple values for a keyword.
:invalid-metaclass (E1139): *Invalid metaclass %r used*
  Emitted whenever we can detect that a class is using, as a metaclass,
  something which might be invalid for using as a metaclass.
:missing-kwoa (E1125): *Missing mandatory keyword argument %r in %s call*
  Used when a function call does not pass a mandatory keyword-only argument.
:no-value-for-parameter (E1120): *No value for argument %s in %s call*
  Used when a function call passes too few arguments.
:not-an-iterable (E1133): *Non-iterable value %s is used in an iterating context*
  Used when a non-iterable value is used in place where iterable is expected
:not-a-mapping (E1134): *Non-mapping value %s is used in a mapping context*
  Used when a non-mapping value is used in place where mapping is expected
:invalid-sequence-index (E1126): *Sequence index is not an int, slice, or instance with __index__*
  Used when a sequence type is indexed with an invalid type. Valid types are
  ints, slices, and objects with an __index__ method.
:invalid-slice-index (E1127): *Slice index is not an int, None, or instance with __index__*
  Used when a slice index is not an integer, None, or an object with an
  __index__ method.
:invalid-slice-step (E1144): *Slice step cannot be 0*
  Used when a slice step is 0 and the object doesn't implement a custom
  __getitem__ method.
:too-many-function-args (E1121): *Too many positional arguments for %s call*
  Used when a function call passes too many positional arguments.
:unexpected-keyword-arg (E1123): *Unexpected keyword argument %r in %s call*
  Used when a function call passes a keyword argument that doesn't correspond
  to one of the function's parameter names.
:dict-iter-missing-items (E1141): *Unpacking a dictionary in iteration without calling .items()*
  Emitted when trying to iterate through a dict without calling .items()
:unsupported-membership-test (E1135): *Value '%s' doesn't support membership test*
  Emitted when an instance in membership test expression doesn't implement
  membership protocol (__contains__/__iter__/__getitem__).
:unsubscriptable-object (E1136): *Value '%s' is unsubscriptable*
  Emitted when a subscripted value doesn't support subscription (i.e. doesn't
  define __getitem__ method or __class_getitem__ for a class).
:kwarg-superseded-by-positional-arg (W1117): *%r will be included in %r since a positional-only parameter with this name already exists*
  Emitted when a function is called with a keyword argument that has the same
  name as a positional-only parameter and the function contains a keyword
  variadic parameter dict.
:keyword-arg-before-vararg (W1113): *Keyword argument before variable positional arguments list in the definition of %s function*
  When defining a keyword argument before variable positional arguments, one
  can end up in having multiple values passed for the aforementioned parameter
  in case the method is called with keyword arguments.
:non-str-assignment-to-dunder-name (W1115): *Non-string value assigned to __name__*
  Emitted when a non-string value is assigned to __name__
:arguments-out-of-order (W1114): *Positional arguments appear to be out of order*
  Emitted when the caller's argument names fully match the parameter names in
  the function signature but do not have the same order.
:isinstance-second-argument-not-valid-type (W1116): *Second argument of isinstance is not a type*
  Emitted when the second argument of an isinstance call is not a type.
:c-extension-no-member (I1101): *%s %r has no %r member%s, but source is unavailable. Consider adding this module to extension-pkg-allow-list if you want to perform analysis based on run-time introspection of living objects.*
  Used when a variable is accessed for non-existent member of C extension. Due
  to unavailability of source static analysis is impossible, but it may be
  performed by introspecting living objects in run-time.


Unicode Checker checker
~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``unicode_checker``.

Unicode Checker checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:bidirectional-unicode (E2502): *Contains control characters that can permit obfuscated code executed differently than displayed*
  bidirectional unicode are typically not displayed characters required to
  display right-to-left (RTL) script (i.e. Chinese, Japanese, Arabic, Hebrew,
  ...) correctly. So can you trust this code? Are you sure it displayed
  correctly in all editors? If you did not write it or your language is not
  RTL, remove the special characters, as they could be used to trick you into
  executing code, that does something else than what it looks like. More
  Information: https://en.wikipedia.org/wiki/Bidirectional_text
  https://trojansource.codes/
:invalid-character-backspace (E2510): *Invalid unescaped character backspace, use "\b" instead.*
  Moves the cursor back, so the character after it will overwrite the character
  before.
:invalid-character-carriage-return (E2511): *Invalid unescaped character carriage-return, use "\r" instead.*
  Moves the cursor to the start of line, subsequent characters overwrite the
  start of the line.
:invalid-character-esc (E2513): *Invalid unescaped character esc, use "\x1B" instead.*
  Commonly initiates escape codes which allow arbitrary control of the
  terminal.
:invalid-character-nul (E2514): *Invalid unescaped character nul, use "\0" instead.*
  Mostly end of input for python.
:invalid-character-sub (E2512): *Invalid unescaped character sub, use "\x1A" instead.*
  Ctrl+Z "End of text" on Windows. Some programs (such as type) ignore the rest
  of the file after it.
:invalid-character-zero-width-space (E2515): *Invalid unescaped character zero-width-space, use "\u200B" instead.*
  Invisible space character could hide real code execution.
:invalid-unicode-codec (E2501): *UTF-16 and UTF-32 aren't backward compatible. Use UTF-8 instead*
  For compatibility use UTF-8 instead of UTF-16/UTF-32. See also
  https://bugs.python.org/issue1503789 for a history of this issue. And
  https://softwareengineering.stackexchange.com/questions/102205/ for some
  possible problems when using UTF-16 for instance.
:bad-file-encoding (C2503): *PEP8 recommends UTF-8 as encoding for Python files*
  PEP8 recommends UTF-8 default encoding for Python files. See
  https://peps.python.org/pep-0008/#source-file-encoding


Unnecessary-Dunder-Call checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``unnecessary-dunder-call``.

Unnecessary-Dunder-Call checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:unnecessary-dunder-call (C2801): *Unnecessarily calls dunder method %s. %s.*
  Used when a dunder method is manually called instead of using the
  corresponding function/method/operator.


Unnecessary Ellipsis checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``unnecessary_ellipsis``.

Unnecessary Ellipsis checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:unnecessary-ellipsis (W2301): *Unnecessary ellipsis constant*
  Used when the ellipsis constant is encountered and can be avoided. A line of
  code consisting of an ellipsis is unnecessary if there is a docstring on the
  preceding line or if there is a statement in the same scope.


Unsupported Version checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``unsupported_version``.

Unsupported Version checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:using-assignment-expression-in-unsupported-version (W2605): *Assignment expression is not supported by all versions included in the py-version setting*
  Used when the py-version set by the user is lower than 3.8 and pylint
  encounters an assignment expression (walrus) operator.
:using-exception-groups-in-unsupported-version (W2603): *Exception groups are not supported by all versions included in the py-version setting*
  Used when the py-version set by the user is lower than 3.11 and pylint
  encounters ``except*`` or `ExceptionGroup``.
:using-f-string-in-unsupported-version (W2601): *F-strings are not supported by all versions included in the py-version setting*
  Used when the py-version set by the user is lower than 3.6 and pylint
  encounters an f-string.
:using-generic-type-syntax-in-unsupported-version (W2604): *Generic type syntax (PEP 695) is not supported by all versions included in the py-version setting*
  Used when the py-version set by the user is lower than 3.12 and pylint
  encounters generic type syntax.
:using-positional-only-args-in-unsupported-version (W2606): *Positional-only arguments are not supported by all versions included in the py-version setting*
  Used when the py-version set by the user is lower than 3.8 and pylint
  encounters positional-only arguments.
:using-final-decorator-in-unsupported-version (W2602): *typing.final is not supported by all versions included in the py-version setting*
  Used when the py-version set by the user is lower than 3.8 and pylint
  encounters a ``typing.final`` decorator.


Variables checker
~~~~~~~~~~~~~~~~~

Verbatim name of the checker is ``variables``.

See also :ref:`variables checker's options' documentation <variables-options>`

Variables checker Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^
:unpacking-non-sequence (E0633): *Attempting to unpack a non-sequence%s*
  Used when something which is not a sequence is used in an unpack assignment
:invalid-all-format (E0605): *Invalid format for __all__, must be tuple or list*
  Used when __all__ has an invalid format.
:potential-index-error (E0643): *Invalid index for iterable length*
  Emitted when an index used on an iterable goes beyond the length of that
  iterable.
:invalid-all-object (E0604): *Invalid object %r in __all__, must contain only strings*
  Used when an invalid (non-string) object occurs in __all__.
:no-name-in-module (E0611): *No name %r in module %r*
  Used when a name cannot be found in a module.
:possibly-used-before-assignment (E0606): *Possibly using variable %r before assignment*
  Emitted when a local variable is accessed before its assignment took place in
  both branches of an if/else switch.
:undefined-variable (E0602): *Undefined variable %r*
  Used when an undefined variable is accessed.
:undefined-all-variable (E0603): *Undefined variable name %r in __all__*
  Used when an undefined variable name is referenced in __all__.
:used-before-assignment (E0601): *Using variable %r before assignment*
  Emitted when a local variable is accessed before its assignment took place.
  Assignments in try blocks are assumed not to have occurred when evaluating
  associated except/finally blocks. Assignments in except blocks are assumed
  not to have occurred when evaluating statements outside the block, except
  when the associated try block contains a return statement.
:cell-var-from-loop (W0640): *Cell variable %s defined in loop*
  A variable used in a closure is defined in a loop. This will result in all
  closures using the same value for the closed-over variable.
:global-variable-undefined (W0601): *Global variable %r undefined at the module level*
  Used when a variable is defined through the "global" statement but the
  variable is not defined in the module scope.
:self-cls-assignment (W0642): *Invalid assignment to %s in method*
  Invalid assignment to self or cls in instance or class method respectively.
:unbalanced-dict-unpacking (W0644): *Possible unbalanced dict unpacking with %s: left side has %d label%s, right side has %d value%s*
  Used when there is an unbalanced dict unpacking in assignment or for loop
:unbalanced-tuple-unpacking (W0632): *Possible unbalanced tuple unpacking with sequence %s: left side has %d label%s, right side has %d value%s*
  Used when there is an unbalanced tuple unpacking in assignment
:possibly-unused-variable (W0641): *Possibly unused variable %r*
  Used when a variable is defined but might not be used. The possibility comes
  from the fact that locals() might be used, which could consume or not the
  said variable
:redefined-builtin (W0622): *Redefining built-in %r*
  Used when a variable or function override a built-in.
:redefined-outer-name (W0621): *Redefining name %r from outer scope (line %s)*
  Used when a variable's name hides a name defined in an outer scope or except
  handler.
:unused-import (W0611): *Unused %s*
  Used when an imported module or variable is not used.
:unused-argument (W0613): *Unused argument %r*
  Used when a function or method argument is not used.
:unused-wildcard-import (W0614): *Unused import(s) %s from wildcard import of %s*
  Used when an imported module or variable is not used from a `'from X import
  *'` style import.
:unused-variable (W0612): *Unused variable %r*
  Used when a variable is defined but not used.
:global-variable-not-assigned (W0602): *Using global for %r but no assignment is done*
  When a variable defined in the global scope is modified in an inner scope,
  the 'global' keyword is required in the inner scope only if there is an
  assignment operation done in the inner scope.
:undefined-loop-variable (W0631): *Using possibly undefined loop variable %r*
  Used when a loop variable (i.e. defined by a for loop or a list comprehension
  or a generator expression) is used outside the loop.
:global-statement (W0603): *Using the global statement*
  Used when you use the "global" statement to update a global variable. Pylint
  discourages its usage. That doesn't mean you cannot use it!
:global-at-module-level (W0604): *Using the global statement at the module level*
  Used when you use the "global" statement at the module level since it has no
  effect.
````

## File: doc/user_guide/checkers/index.rst
````
Checkers
========

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   features
   extensions
````

## File: doc/user_guide/configuration/all-options.rst
````
.. This file is auto-generated. Make any changes to the associated
.. docs extension in 'doc/exts/pylint_options.py'.

.. _all-options:

Standard Checkers
^^^^^^^^^^^^^^^^^


.. _main-options:

``Main`` **Checker**
--------------------
--analyse-fallback-blocks
"""""""""""""""""""""""""
*Analyse import fallback blocks. This can be used to support both Python 2 and 3 compatible code, which means that the block might have code that exists only in one or another interpreter, leading to false positives when analysed.*

**Default:**  ``False``


--clear-cache-post-run
""""""""""""""""""""""
*Clear in-memory caches upon conclusion of linting. Useful if running pylint in a server-like mode.*

**Default:**  ``False``


--confidence
""""""""""""
*Only show warnings with the listed confidence levels. Leave empty to show all. Valid levels: HIGH, CONTROL_FLOW, INFERENCE, INFERENCE_FAILURE, UNDEFINED.*

**Default:**  ``['HIGH', 'CONTROL_FLOW', 'INFERENCE', 'INFERENCE_FAILURE', 'UNDEFINED']``


--disable
"""""""""
*Disable the message, report, category or checker with the given id(s). You can either give multiple identifiers separated by comma (,) or put this option multiple times (only on the command line, not in the configuration file where it should appear only once). You can also use "--disable=all" to disable everything first and then re-enable specific checks. For example, if you want to run only the similarities checker, you can use "--disable=all --enable=similarities". If you want to run only the classes checker, but have no Warning level messages displayed, use "--disable=all --enable=classes --disable=W".*

**Default:**  ``()``


--enable
""""""""
*Enable the message, report, category or checker with the given id(s). You can either give multiple identifier separated by comma (,) or put this option multiple time (only on the command line, not in the configuration file where it should appear only once). See also the "--disable" option for examples.*

**Default:**  ``()``


--evaluation
""""""""""""
*Python expression which should return a score less than or equal to 10. You have access to the variables 'fatal', 'error', 'warning', 'refactor', 'convention', and 'info' which contain the number of messages in each category, as well as 'statement' which is the total number of statements analyzed. This score is used by the global evaluation report (RP0004).*

**Default:**  ``max(0, 0 if fatal else 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10))``


--exit-zero
"""""""""""
*Always return a 0 (non-error) status code, even if lint errors are found. This is primarily useful in continuous integration scripts.*

**Default:**  ``False``


--extension-pkg-allow-list
""""""""""""""""""""""""""
*A comma-separated list of package or module names from where C extensions may be loaded. Extensions are loading into the active Python interpreter and may run arbitrary code.*

**Default:**  ``[]``


--extension-pkg-whitelist
"""""""""""""""""""""""""
*A comma-separated list of package or module names from where C extensions may be loaded. Extensions are loading into the active Python interpreter and may run arbitrary code. (This is an alternative name to extension-pkg-allow-list for backward compatibility.)*

**Default:**  ``[]``


--fail-on
"""""""""
*Return non-zero exit code if any of these messages/categories are detected, even if score is above --fail-under value. Syntax same as enable. Messages specified are enabled, while categories only check already-enabled messages.*

**Default:** ``""``


--fail-under
""""""""""""
*Specify a score threshold under which the program will exit with error.*

**Default:**  ``10``


--from-stdin
""""""""""""
*Interpret the stdin as a python script, whose filename needs to be passed as the module_or_package argument.*

**Default:**  ``False``


--ignore
""""""""
*Files or directories to be skipped. They should be base names, not paths.*

**Default:**  ``('CVS',)``


--ignore-paths
""""""""""""""
*Add files or directories matching the regular expressions patterns to the ignore-list. The regex matches against paths and can be in Posix or Windows format. Because '\\' represents the directory delimiter on Windows systems, it can't be used as an escape character.*

**Default:**  ``[]``


--ignore-patterns
"""""""""""""""""
*Files or directories matching the regular expression patterns are skipped. The regex matches against base names, not paths. The default value ignores Emacs file locks*

**Default:**  ``(re.compile('^\\.#'),)``


--ignored-modules
"""""""""""""""""
*List of module names for which member attributes should not be checked and will not be imported (useful for modules/projects where namespaces are manipulated during runtime and thus existing member attributes cannot be deduced by static analysis). It supports qualified module names, as well as Unix pattern matching.*

**Default:**  ``()``


--jobs
""""""
*Use multiple processes to speed up Pylint. Specifying 0 will auto-detect the number of processors available to use, and will cap the count on Windows to avoid hangs.*

**Default:**  ``1``


--limit-inference-results
"""""""""""""""""""""""""
*Control the amount of potential inferred values when inferring a single object. This can help the performance when dealing with large functions or complex, nested conditions.*

**Default:**  ``100``


--load-plugins
""""""""""""""
*List of plugins (as comma separated values of python module names) to load, usually to register additional checkers.*

**Default:**  ``()``


--msg-template
""""""""""""""
*Template used to display messages. This is a python new-style format string used to format the message information. See doc for all details.*

**Default:** ``""``


--output-format
"""""""""""""""
*Set the output format. Available formats are: 'text', 'parseable', 'colorized', 'json2' (improved json format), 'json' (old json format), msvs (visual studio) and 'github' (GitHub actions). You can also give a reporter class, e.g. mypackage.mymodule.MyReporterClass.*

**Default:**  ``text``


--persistent
""""""""""""
*Pickle collected data for later comparisons.*

**Default:**  ``True``


--prefer-stubs
""""""""""""""
*Resolve imports to .pyi stubs if available. May reduce no-member messages and increase not-an-iterable messages.*

**Default:**  ``False``


--py-version
""""""""""""
*Minimum Python version to use for version dependent checks. Will default to the version used to run pylint.*

**Default:**  ``sys.version_info[:2]``


--recursive
"""""""""""
*Discover python modules and packages in the file system subtree.*

**Default:**  ``False``


--reports
"""""""""
*Tells whether to display a full report or only the messages.*

**Default:**  ``False``


--score
"""""""
*Activate the evaluation score.*

**Default:**  ``True``


--source-roots
""""""""""""""
*Add paths to the list of the source roots. Supports globbing patterns. The source root is an absolute path or a path relative to the current working directory used to determine a package namespace for modules located under the source root.*

**Default:**  ``()``


--unsafe-load-any-extension
"""""""""""""""""""""""""""
*Allow loading of arbitrary C extensions. Extensions are imported into the active Python interpreter and may run arbitrary code.*

**Default:**  ``False``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.main]
   analyse-fallback-blocks = false

   clear-cache-post-run = false

   confidence = ["HIGH", "CONTROL_FLOW", "INFERENCE", "INFERENCE_FAILURE", "UNDEFINED"]

   disable = ["bad-inline-option", "consider-using-augmented-assign", "deprecated-pragma", "file-ignored", "locally-disabled", "prefer-typing-namedtuple", "raw-checker-failed", "suppressed-message", "use-implicit-booleaness-not-comparison-to-string", "use-implicit-booleaness-not-comparison-to-zero", "use-symbolic-message-instead", "useless-suppression"]

   enable = []

   evaluation = "max(0, 0 if fatal else 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10))"

   exit-zero = false

   extension-pkg-allow-list = []

   extension-pkg-whitelist = []

   fail-on = []

   fail-under = 10

   from-stdin = false

   ignore = ["CVS"]

   ignore-paths = []

   ignore-patterns = ["^\\.#"]

   ignored-modules = []

   jobs = 1

   limit-inference-results = 100

   load-plugins = []

   msg-template = ""

   # output-format =

   persistent = true

   prefer-stubs = false

   py-version = "sys.version_info[:2]"

   recursive = false

   reports = false

   score = true

   source-roots = []

   unsafe-load-any-extension = false



.. raw:: html

   </details>


.. _basic-options:

``Basic`` **Checker**
---------------------
--argument-naming-style
"""""""""""""""""""""""
*Naming style matching correct argument names.*

**Default:**  ``snake_case``


--argument-rgx
""""""""""""""
*Regular expression matching correct argument names. Overrides argument-naming-style. If left empty, argument names will be checked with the set naming style.*

**Default:**  ``None``


--attr-naming-style
"""""""""""""""""""
*Naming style matching correct attribute names.*

**Default:**  ``snake_case``


--attr-rgx
""""""""""
*Regular expression matching correct attribute names. Overrides attr-naming-style. If left empty, attribute names will be checked with the set naming style.*

**Default:**  ``None``


--bad-names
"""""""""""
*Bad variable names which should always be refused, separated by a comma.*

**Default:**  ``('foo', 'bar', 'baz', 'toto', 'tutu', 'tata')``


--bad-names-rgxs
""""""""""""""""
*Bad variable names regexes, separated by a comma. If names match any regex, they will always be refused*

**Default:** ``""``


--class-attribute-naming-style
""""""""""""""""""""""""""""""
*Naming style matching correct class attribute names.*

**Default:**  ``any``


--class-attribute-rgx
"""""""""""""""""""""
*Regular expression matching correct class attribute names. Overrides class-attribute-naming-style. If left empty, class attribute names will be checked with the set naming style.*

**Default:**  ``None``


--class-const-naming-style
""""""""""""""""""""""""""
*Naming style matching correct class constant names.*

**Default:**  ``UPPER_CASE``


--class-const-rgx
"""""""""""""""""
*Regular expression matching correct class constant names. Overrides class-const-naming-style. If left empty, class constant names will be checked with the set naming style.*

**Default:**  ``None``


--class-naming-style
""""""""""""""""""""
*Naming style matching correct class names.*

**Default:**  ``PascalCase``


--class-rgx
"""""""""""
*Regular expression matching correct class names. Overrides class-naming-style. If left empty, class names will be checked with the set naming style.*

**Default:**  ``None``


--const-naming-style
""""""""""""""""""""
*Naming style matching correct constant names.*

**Default:**  ``UPPER_CASE``


--const-rgx
"""""""""""
*Regular expression matching correct constant names. Overrides const-naming-style. If left empty, constant names will be checked with the set naming style.*

**Default:**  ``None``


--docstring-min-length
""""""""""""""""""""""
*Minimum line length for functions/classes that require docstrings, shorter ones are exempt.*

**Default:**  ``-1``


--function-naming-style
"""""""""""""""""""""""
*Naming style matching correct function names.*

**Default:**  ``snake_case``


--function-rgx
""""""""""""""
*Regular expression matching correct function names. Overrides function-naming-style. If left empty, function names will be checked with the set naming style.*

**Default:**  ``None``


--good-names
""""""""""""
*Good variable names which should always be accepted, separated by a comma.*

**Default:**  ``('i', 'j', 'k', 'ex', 'Run', '_')``


--good-names-rgxs
"""""""""""""""""
*Good variable names regexes, separated by a comma. If names match any regex, they will always be accepted*

**Default:** ``""``


--include-naming-hint
"""""""""""""""""""""
*Include a hint for the correct naming format with invalid-name.*

**Default:**  ``False``


--inlinevar-naming-style
""""""""""""""""""""""""
*Naming style matching correct inline iteration names.*

**Default:**  ``any``


--inlinevar-rgx
"""""""""""""""
*Regular expression matching correct inline iteration names. Overrides inlinevar-naming-style. If left empty, inline iteration names will be checked with the set naming style.*

**Default:**  ``None``


--method-naming-style
"""""""""""""""""""""
*Naming style matching correct method names.*

**Default:**  ``snake_case``


--method-rgx
""""""""""""
*Regular expression matching correct method names. Overrides method-naming-style. If left empty, method names will be checked with the set naming style.*

**Default:**  ``None``


--module-naming-style
"""""""""""""""""""""
*Naming style matching correct module names.*

**Default:**  ``snake_case``


--module-rgx
""""""""""""
*Regular expression matching correct module names. Overrides module-naming-style. If left empty, module names will be checked with the set naming style.*

**Default:**  ``None``


--name-group
""""""""""""
*Colon-delimited sets of names that determine each other's naming style when the name regexes allow several styles.*

**Default:**  ``()``


--no-docstring-rgx
""""""""""""""""""
*Regular expression which should only match function or class names that do not require a docstring.*

**Default:**  ``re.compile('^_')``


--property-classes
""""""""""""""""""
*List of decorators that produce properties, such as abc.abstractproperty. Add to this list to register other decorators that produce valid properties. These decorators are taken in consideration only for invalid-name.*

**Default:**  ``('abc.abstractproperty',)``


--typealias-rgx
"""""""""""""""
*Regular expression matching correct type alias names. If left empty, type alias names will be checked with the set naming style.*

**Default:**  ``None``


--typevar-rgx
"""""""""""""
*Regular expression matching correct type variable names. If left empty, type variable names will be checked with the set naming style.*

**Default:**  ``None``


--variable-naming-style
"""""""""""""""""""""""
*Naming style matching correct variable names.*

**Default:**  ``snake_case``


--variable-rgx
""""""""""""""
*Regular expression matching correct variable names. Overrides variable-naming-style. If left empty, variable names will be checked with the set naming style.*

**Default:**  ``None``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.basic]
   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   argument-naming-style = "snake_case"

   # argument-rgx =

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   attr-naming-style = "snake_case"

   # attr-rgx =

   bad-names = ["foo", "bar", "baz", "toto", "tutu", "tata"]

   bad-names-rgxs = []

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   class-attribute-naming-style = "any"

   # class-attribute-rgx =

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   class-const-naming-style = "UPPER_CASE"

   # class-const-rgx =

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   class-naming-style = "PascalCase"

   # class-rgx =

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   const-naming-style = "UPPER_CASE"

   # const-rgx =

   docstring-min-length = -1

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   function-naming-style = "snake_case"

   # function-rgx =

   good-names = ["i", "j", "k", "ex", "Run", "_"]

   good-names-rgxs = []

   include-naming-hint = false

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   inlinevar-naming-style = "any"

   # inlinevar-rgx =

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   method-naming-style = "snake_case"

   # method-rgx =

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   module-naming-style = "snake_case"

   # module-rgx =

   name-group = []

   no-docstring-rgx = "^_"

   property-classes = ["abc.abstractproperty"]

   # typealias-rgx =

   # typevar-rgx =

   # Possible choices: ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE', 'any']
   variable-naming-style = "snake_case"

   # variable-rgx =



.. raw:: html

   </details>


.. _classes-options:

``Classes`` **Checker**
-----------------------
--check-protected-access-in-special-methods
"""""""""""""""""""""""""""""""""""""""""""
*Warn about protected attribute access inside special methods*

**Default:**  ``False``


--defining-attr-methods
"""""""""""""""""""""""
*List of method names used to declare (i.e. assign) instance attributes.*

**Default:**  ``('__init__', '__new__', 'setUp', 'asyncSetUp', '__post_init__')``


--exclude-protected
"""""""""""""""""""
*List of member names, which should be excluded from the protected access warning.*

**Default:**  ``('_asdict', '_fields', '_replace', '_source', '_make', 'os._exit')``


--valid-classmethod-first-arg
"""""""""""""""""""""""""""""
*List of valid names for the first argument in a class method.*

**Default:**  ``('cls',)``


--valid-metaclass-classmethod-first-arg
"""""""""""""""""""""""""""""""""""""""
*List of valid names for the first argument in a metaclass class method.*

**Default:**  ``('mcs',)``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.classes]
   check-protected-access-in-special-methods = false

   defining-attr-methods = ["__init__", "__new__", "setUp", "asyncSetUp", "__post_init__"]

   exclude-protected = ["_asdict", "_fields", "_replace", "_source", "_make", "os._exit"]

   valid-classmethod-first-arg = ["cls"]

   valid-metaclass-classmethod-first-arg = ["mcs"]



.. raw:: html

   </details>


.. _design-options:

``Design`` **Checker**
----------------------
--exclude-too-few-public-methods
""""""""""""""""""""""""""""""""
*List of regular expressions of class ancestor names to ignore when counting public methods (see R0903)*

**Default:**  ``[]``


--ignored-parents
"""""""""""""""""
*List of qualified class names to ignore when counting class parents (see R0901)*

**Default:**  ``()``


--max-args
""""""""""
*Maximum number of arguments for function / method.*

**Default:**  ``5``


--max-attributes
""""""""""""""""
*Maximum number of attributes for a class (see R0902).*

**Default:**  ``7``


--max-bool-expr
"""""""""""""""
*Maximum number of boolean expressions in an if statement (see R0916).*

**Default:**  ``5``


--max-branches
""""""""""""""
*Maximum number of branch for function / method body.*

**Default:**  ``12``


--max-complexity
""""""""""""""""
*McCabe complexity cyclomatic threshold*

**Default:**  ``10``


--max-locals
""""""""""""
*Maximum number of locals for function / method body.*

**Default:**  ``15``


--max-parents
"""""""""""""
*Maximum number of parents for a class (see R0901).*

**Default:**  ``7``


--max-positional-arguments
""""""""""""""""""""""""""
*Maximum number of positional arguments for function / method.*

**Default:**  ``5``


--max-public-methods
""""""""""""""""""""
*Maximum number of public methods for a class (see R0904).*

**Default:**  ``20``


--max-returns
"""""""""""""
*Maximum number of return / yield for function / method body.*

**Default:**  ``6``


--max-statements
""""""""""""""""
*Maximum number of statements in function / method body.*

**Default:**  ``50``


--min-public-methods
""""""""""""""""""""
*Minimum number of public methods for a class (see R0903).*

**Default:**  ``2``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.design]
   exclude-too-few-public-methods = []

   ignored-parents = []

   max-args = 5

   max-attributes = 7

   max-bool-expr = 5

   max-branches = 12

   max-complexity = 10

   max-locals = 15

   max-parents = 7

   max-positional-arguments = 5

   max-public-methods = 20

   max-returns = 6

   max-statements = 50

   min-public-methods = 2



.. raw:: html

   </details>


.. _exceptions-options:

``Exceptions`` **Checker**
--------------------------
--overgeneral-exceptions
""""""""""""""""""""""""
*Exceptions that will emit a warning when caught.*

**Default:**  ``('builtins.BaseException', 'builtins.Exception')``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.exceptions]
   overgeneral-exceptions = ["builtins.BaseException", "builtins.Exception"]



.. raw:: html

   </details>


.. _format-options:

``Format`` **Checker**
----------------------
--expected-line-ending-format
"""""""""""""""""""""""""""""
*Expected format of line ending, e.g. empty (any line ending), LF or CRLF.*

**Default:** ``""``


--ignore-long-lines
"""""""""""""""""""
*Regexp for a line that is allowed to be longer than the limit.*

**Default:**  ``^\s*(# )?<?https?://\S+>?$``


--indent-after-paren
""""""""""""""""""""
*Number of spaces of indent required inside a hanging or continued line.*

**Default:**  ``4``


--indent-string
"""""""""""""""
*String used as indentation unit. This is usually "    " (4 spaces) or "\t" (1 tab).*

**Default:**  ``    ``


--max-line-length
"""""""""""""""""
*Maximum number of characters on a single line.*

**Default:**  ``100``


--max-module-lines
""""""""""""""""""
*Maximum number of lines in a module.*

**Default:**  ``1000``


--single-line-class-stmt
""""""""""""""""""""""""
*Allow the body of a class to be on the same line as the declaration if body contains single statement.*

**Default:**  ``False``


--single-line-if-stmt
"""""""""""""""""""""
*Allow the body of an if to be on the same line as the test if there is no else.*

**Default:**  ``False``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.format]
   # Possible choices: ['', 'LF', 'CRLF']
   expected-line-ending-format = ""

   ignore-long-lines = "^\\s*(# )?<?https?://\\S+>?$"

   indent-after-paren = 4

   indent-string = "    "

   max-line-length = 100

   max-module-lines = 1000

   single-line-class-stmt = false

   single-line-if-stmt = false



.. raw:: html

   </details>


.. _imports-options:

``Imports`` **Checker**
-----------------------
--allow-any-import-level
""""""""""""""""""""""""
*List of modules that can be imported at any level, not just the top level one.*

**Default:**  ``()``


--allow-reexport-from-package
"""""""""""""""""""""""""""""
*Allow explicit reexports by alias from a package __init__.*

**Default:**  ``False``


--allow-wildcard-with-all
"""""""""""""""""""""""""
*Allow wildcard imports from modules that define __all__.*

**Default:**  ``False``


--deprecated-modules
""""""""""""""""""""
*Deprecated modules which should not be used, separated by a comma.*

**Default:**  ``()``


--ext-import-graph
""""""""""""""""""
*Output a graph (.gv or any supported image format) of external dependencies to the given file (report RP0402 must not be disabled).*

**Default:** ``""``


--import-graph
""""""""""""""
*Output a graph (.gv or any supported image format) of all (i.e. internal and external) dependencies to the given file (report RP0402 must not be disabled).*

**Default:** ``""``


--int-import-graph
""""""""""""""""""
*Output a graph (.gv or any supported image format) of internal dependencies to the given file (report RP0402 must not be disabled).*

**Default:** ``""``


--known-standard-library
""""""""""""""""""""""""
*Force import order to recognize a module as part of the standard compatibility libraries.*

**Default:**  ``()``


--known-third-party
"""""""""""""""""""
*Force import order to recognize a module as part of a third party library.*

**Default:**  ``('enchant',)``


--preferred-modules
"""""""""""""""""""
*Couples of modules and preferred modules, separated by a comma.*

**Default:**  ``()``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.imports]
   allow-any-import-level = []

   allow-reexport-from-package = false

   allow-wildcard-with-all = false

   deprecated-modules = []

   ext-import-graph = ""

   import-graph = ""

   int-import-graph = ""

   known-standard-library = []

   known-third-party = ["enchant"]

   preferred-modules = []



.. raw:: html

   </details>


.. _logging-options:

``Logging`` **Checker**
-----------------------
--logging-format-style
""""""""""""""""""""""
*The type of string formatting that logging methods do. `old` means using % formatting, `new` is for `{}` formatting.*

**Default:**  ``old``


--logging-modules
"""""""""""""""""
*Logging modules to check that the string format arguments are in logging function parameter format.*

**Default:**  ``('logging',)``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.logging]
   # Possible choices: ['old', 'new']
   logging-format-style = "old"

   logging-modules = ["logging"]



.. raw:: html

   </details>


.. _method_args-options:

``Method_args`` **Checker**
---------------------------
--timeout-methods
"""""""""""""""""
*List of qualified names (i.e., library.method) which require a timeout parameter e.g. 'requests.api.get,requests.api.post'*

**Default:**  ``('requests.api.delete', 'requests.api.get', 'requests.api.head', 'requests.api.options', 'requests.api.patch', 'requests.api.post', 'requests.api.put', 'requests.api.request')``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.method_args]
   timeout-methods = ["requests.api.delete", "requests.api.get", "requests.api.head", "requests.api.options", "requests.api.patch", "requests.api.post", "requests.api.put", "requests.api.request"]



.. raw:: html

   </details>


.. _miscellaneous-options:

``Miscellaneous`` **Checker**
-----------------------------
--check-fixme-in-docstring
""""""""""""""""""""""""""
*Whether or not to search for fixme's in docstrings.*

**Default:**  ``False``


--notes
"""""""
*List of note tags to take in consideration, separated by a comma.*

**Default:**  ``('FIXME', 'XXX', 'TODO')``


--notes-rgx
"""""""""""
*Regular expression of note tags to take in consideration.*

**Default:** ``""``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.miscellaneous]
   check-fixme-in-docstring = false

   notes = ["FIXME", "XXX", "TODO"]

   notes-rgx = ""



.. raw:: html

   </details>


.. _refactoring-options:

``Refactoring`` **Checker**
---------------------------
--max-nested-blocks
"""""""""""""""""""
*Maximum number of nested blocks for function / method body*

**Default:**  ``5``


--never-returning-functions
"""""""""""""""""""""""""""
*Complete name of functions that never returns. When checking for inconsistent-return-statements if a never returning function is called then it will be considered as an explicit return statement and no message will be printed.*

**Default:**  ``('sys.exit', 'argparse.parse_error')``


--suggest-join-with-non-empty-separator
"""""""""""""""""""""""""""""""""""""""
*Let 'consider-using-join' be raised when the separator to join on would be non-empty (resulting in expected fixes of the type: ``"- " + "
- ".join(items)``)*

**Default:**  ``True``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.refactoring]
   max-nested-blocks = 5

   never-returning-functions = ["sys.exit", "argparse.parse_error"]

   suggest-join-with-non-empty-separator = true



.. raw:: html

   </details>


.. _similarities-options:

``Similarities`` **Checker**
----------------------------
--ignore-comments
"""""""""""""""""
*Comments are removed from the similarity computation*

**Default:**  ``True``


--ignore-docstrings
"""""""""""""""""""
*Docstrings are removed from the similarity computation*

**Default:**  ``True``


--ignore-imports
""""""""""""""""
*Imports are removed from the similarity computation*

**Default:**  ``True``


--ignore-signatures
"""""""""""""""""""
*Signatures are removed from the similarity computation*

**Default:**  ``True``


--min-similarity-lines
""""""""""""""""""""""
*Minimum lines number of a similarity.*

**Default:**  ``4``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.similarities]
   ignore-comments = true

   ignore-docstrings = true

   ignore-imports = true

   ignore-signatures = true

   min-similarity-lines = 4



.. raw:: html

   </details>


.. _spelling-options:

``Spelling`` **Checker**
------------------------
--max-spelling-suggestions
""""""""""""""""""""""""""
*Limits count of emitted suggestions for spelling mistakes.*

**Default:**  ``4``


--spelling-dict
"""""""""""""""
*Spelling dictionary name. Available dictionaries depends on your local enchant installation*

**Default:** ``""``


--spelling-ignore-comment-directives
""""""""""""""""""""""""""""""""""""
*List of comma separated words that should be considered directives if they appear at the beginning of a comment and should not be checked.*

**Default:**  ``fmt: on,fmt: off,noqa:,noqa,nosec,isort:skip,mypy:``


--spelling-ignore-words
"""""""""""""""""""""""
*List of comma separated words that should not be checked.*

**Default:** ``""``


--spelling-private-dict-file
""""""""""""""""""""""""""""
*A path to a file that contains the private dictionary; one word per line.*

**Default:** ``""``


--spelling-store-unknown-words
""""""""""""""""""""""""""""""
*Tells whether to store unknown words to the private dictionary (see the --spelling-private-dict-file option) instead of raising a message.*

**Default:**  ``n``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.spelling]
   max-spelling-suggestions = 4

   # Possible choices: Values from 'enchant.Broker().list_dicts()' depending on your local enchant installation
   spelling-dict = ""

   spelling-ignore-comment-directives = "fmt: on,fmt: off,noqa:,noqa,nosec,isort:skip,mypy:"

   spelling-ignore-words = ""

   spelling-private-dict-file = ""

   spelling-store-unknown-words = false



.. raw:: html

   </details>


.. _string-options:

``String`` **Checker**
----------------------
--check-quote-consistency
"""""""""""""""""""""""""
*This flag controls whether inconsistent-quotes generates a warning when the character used as a quote delimiter is used inconsistently within a module.*

**Default:**  ``False``


--check-str-concat-over-line-jumps
""""""""""""""""""""""""""""""""""
*This flag controls whether the implicit-str-concat should generate a warning on implicit string concatenation in sequences defined over several lines.*

**Default:**  ``False``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.string]
   check-quote-consistency = false

   check-str-concat-over-line-jumps = false



.. raw:: html

   </details>


.. _typecheck-options:

``Typecheck`` **Checker**
-------------------------
--contextmanager-decorators
"""""""""""""""""""""""""""
*List of decorators that produce context managers, such as contextlib.contextmanager. Add to this list to register other decorators that produce valid context managers.*

**Default:**  ``['contextlib.contextmanager']``


--generated-members
"""""""""""""""""""
*List of members which are set dynamically and missed by pylint inference system, and so shouldn't trigger E1101 when accessed. Python regular expressions are accepted.*

**Default:**  ``()``


--ignore-mixin-members
""""""""""""""""""""""
*Tells whether missing members accessed in mixin class should be ignored. A class is considered mixin if its name matches the mixin-class-rgx option.*

**Default:**  ``True``


--ignore-none
"""""""""""""
*Tells whether to warn about missing members when the owner of the attribute is inferred to be None.*

**Default:**  ``True``


--ignore-on-opaque-inference
""""""""""""""""""""""""""""
*This flag controls whether pylint should warn about no-member and similar checks whenever an opaque object is returned when inferring. The inference can return multiple potential results while evaluating a Python object, but some branches might not be evaluated, which results in partial inference. In that case, it might be useful to still emit no-member and other checks for the rest of the inferred objects.*

**Default:**  ``True``


--ignored-checks-for-mixins
"""""""""""""""""""""""""""
*List of symbolic message names to ignore for Mixin members.*

**Default:**  ``['no-member', 'not-async-context-manager', 'not-context-manager', 'attribute-defined-outside-init']``


--ignored-classes
"""""""""""""""""
*List of class names for which member attributes should not be checked (useful for classes with dynamically set attributes). This supports the use of qualified names.*

**Default:**  ``('optparse.Values', 'thread._local', '_thread._local', 'argparse.Namespace')``


--missing-member-hint
"""""""""""""""""""""
*Show a hint with possible names when a member name was not found. The aspect of finding the hint is based on edit distance.*

**Default:**  ``True``


--missing-member-hint-distance
""""""""""""""""""""""""""""""
*The maximum edit distance a name should have in order to be considered a similar match for a missing member name.*

**Default:**  ``1``


--missing-member-max-choices
""""""""""""""""""""""""""""
*The total number of similar names that should be taken in consideration when showing a hint for a missing member.*

**Default:**  ``1``


--mixin-class-rgx
"""""""""""""""""
*Regex pattern to define which classes are considered mixins.*

**Default:**  ``.*[Mm]ixin``


--signature-mutators
""""""""""""""""""""
*List of decorators that change the signature of a decorated function.*

**Default:**  ``[]``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.typecheck]
   contextmanager-decorators = ["contextlib.contextmanager"]

   generated-members = []

   ignore-mixin-members = true

   ignore-none = true

   ignore-on-opaque-inference = true

   ignored-checks-for-mixins = ["no-member", "not-async-context-manager", "not-context-manager", "attribute-defined-outside-init"]

   ignored-classes = ["optparse.Values", "thread._local", "_thread._local", "argparse.Namespace"]

   missing-member-hint = true

   missing-member-hint-distance = 1

   missing-member-max-choices = 1

   mixin-class-rgx = ".*[Mm]ixin"

   signature-mutators = []



.. raw:: html

   </details>


.. _variables-options:

``Variables`` **Checker**
-------------------------
--additional-builtins
"""""""""""""""""""""
*List of additional names supposed to be defined in builtins. Remember that you should avoid defining new builtins when possible.*

**Default:**  ``()``


--allow-global-unused-variables
"""""""""""""""""""""""""""""""
*Tells whether unused global variables should be treated as a violation.*

**Default:**  ``True``


--allowed-redefined-builtins
""""""""""""""""""""""""""""
*List of names allowed to shadow builtins*

**Default:**  ``()``


--callbacks
"""""""""""
*List of strings which can identify a callback function by name. A callback name must start or end with one of those strings.*

**Default:**  ``('cb_', '_cb')``


--dummy-variables-rgx
"""""""""""""""""""""
*A regular expression matching the name of dummy variables (i.e. expected to not be used).*

**Default:**  ``_+$|(_[a-zA-Z0-9_]*[a-zA-Z0-9]+?$)|dummy|^ignored_|^unused_``


--ignored-argument-names
""""""""""""""""""""""""
*Argument names that match this expression will be ignored.*

**Default:**  ``re.compile('_.*|^ignored_|^unused_')``


--init-import
"""""""""""""
*Tells whether we should check for unused import in __init__ files.*

**Default:**  ``False``


--redefining-builtins-modules
"""""""""""""""""""""""""""""
*List of qualified module names which can have objects that can redefine builtins.*

**Default:**  ``('six.moves', 'past.builtins', 'future.builtins', 'builtins', 'io')``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.variables]
   additional-builtins = []

   allow-global-unused-variables = true

   allowed-redefined-builtins = []

   callbacks = ["cb_", "_cb"]

   dummy-variables-rgx = "_+$|(_[a-zA-Z0-9_]*[a-zA-Z0-9]+?$)|dummy|^ignored_|^unused_"

   ignored-argument-names = "_.*|^ignored_|^unused_"

   init-import = false

   redefining-builtins-modules = ["six.moves", "past.builtins", "future.builtins", "builtins", "io"]



.. raw:: html

   </details>


Extensions
^^^^^^^^^^


.. _broad_try_clause-options:

``Broad_try_clause`` **Checker**
--------------------------------
--max-try-statements
""""""""""""""""""""
*Maximum number of statements allowed in a try clause*

**Default:**  ``1``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.broad_try_clause]
   max-try-statements = 1



.. raw:: html

   </details>


.. _code_style-options:

``Code_style`` **Checker**
--------------------------
--max-line-length-suggestions
"""""""""""""""""""""""""""""
*Max line length for which to sill emit suggestions. Used to prevent optional suggestions which would get split by a code formatter (e.g., black). Will default to the setting for ``max-line-length``.*

**Default:**  ``0``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.code_style]
   max-line-length-suggestions = 0



.. raw:: html

   </details>


.. _deprecated_builtins-options:

``Deprecated_builtins`` **Checker**
-----------------------------------
--bad-functions
"""""""""""""""
*List of builtins function names that should not be used, separated by a comma*

**Default:**  ``['map', 'filter']``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.deprecated_builtins]
   bad-functions = ["map", "filter"]



.. raw:: html

   </details>


.. _dunder-options:

``Dunder`` **Checker**
----------------------
--good-dunder-names
"""""""""""""""""""
*Good dunder names which should always be accepted.*

**Default:**  ``[]``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.dunder]
   good-dunder-names = []



.. raw:: html

   </details>


.. _magic-value-options:

``Magic-value`` **Checker**
---------------------------
--valid-magic-values
""""""""""""""""""""
*List of valid magic values that `magic-value-compare` will not detect. Supports integers, floats, negative numbers, for empty string enter ``''``, for backslash values just use one backslash e.g \n.*

**Default:**  ``(0, -1, 1, '', '__main__')``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.magic-value]
   valid-magic-values = [0, -1, 1, "", "__main__"]



.. raw:: html

   </details>


.. _parameter_documentation-options:

``Parameter_documentation`` **Checker**
---------------------------------------
--accept-no-param-doc
"""""""""""""""""""""
*Whether to accept totally missing parameter documentation in the docstring of a function that has parameters.*

**Default:**  ``True``


--accept-no-raise-doc
"""""""""""""""""""""
*Whether to accept totally missing raises documentation in the docstring of a function that raises an exception.*

**Default:**  ``True``


--accept-no-return-doc
""""""""""""""""""""""
*Whether to accept totally missing return documentation in the docstring of a function that returns a statement.*

**Default:**  ``True``


--accept-no-yields-doc
""""""""""""""""""""""
*Whether to accept totally missing yields documentation in the docstring of a generator.*

**Default:**  ``True``


--default-docstring-type
""""""""""""""""""""""""
*If the docstring type cannot be guessed the specified docstring type will be used.*

**Default:**  ``default``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.parameter_documentation]
   accept-no-param-doc = true

   accept-no-raise-doc = true

   accept-no-return-doc = true

   accept-no-yields-doc = true

   # Possible choices: ['sphinx', 'epytext', 'google', 'numpy', 'default']
   default-docstring-type = "default"



.. raw:: html

   </details>


.. _typing-options:

``Typing`` **Checker**
----------------------
--runtime-typing
""""""""""""""""
*Set to ``no`` if the app / library does **NOT** need to support runtime introspection of type annotations. If you use type annotations **exclusively** for type checking of an application, you're probably fine. For libraries, evaluate if some users want to access the type hints at runtime first, e.g., through ``typing.get_type_hints``. Applies to Python versions 3.7 - 3.9*

**Default:**  ``True``



.. raw:: html

   <details>
   <summary><a>Example configuration section</a></summary>

**Note:** Only ``tool.pylint`` is required, the section title is not. These are the default values.

.. code-block:: toml

   [tool.pylint.typing]
   runtime-typing = true



.. raw:: html

   </details>
````

## File: doc/user_guide/configuration/index.rst
````
.. _all-configurations-options:

=============
Configuration
=============

Pylint is highly configurable. There are a lot of options to follow the needs of
various projects and a lot of checks to activate if they suit your style.

You can generate a sample configuration file with ``--generate-toml-config``
or ``--generate-rcfile``. Every option present on the command line before this
will be included in the file.

For example::

    pylint --disable=bare-except,invalid-name --class-rgx='[A-Z][a-z]+' --generate-toml-config

In practice, it is often better to create a minimal configuration file which only contains
configuration overrides. For all other options, Pylint will use its default values.

.. note::

    The internals that create the configuration files fall back to the default values if
    no other value was given. This means that some values depend on the interpreter that
    was used to generate the file. Most notably ``py-version`` which defaults to the
    current interpreter.

.. toctree::
   :maxdepth: 2
   :titlesonly:

   all-options
````

## File: doc/user_guide/installation/ide_integration/flymake-emacs.rst
````
.. _pylint_in_flymake:

Using Pylint through Flymake in Emacs
=====================================

.. warning::
    epylint was deprecated in 2.16.0 and targeted for deletion in 3.0.0.
    All emacs and flymake related files were removed and their support will
    now happen in an external repository: https://github.com/emacsorphanage/pylint.
````

## File: doc/user_guide/installation/ide_integration/index.rst
````
.. _ide-integration:

###########################
 Editor and IDE integration
###########################

Pylint can be integrated in various editors and IDE's.
Below you can find tutorials for some of the most common ones.

- Eclipse_
- Emacs_
- `Eric IDE`_ in the `Project > Check` menu,
- gedit_ (`another option for gedit`_)
- :ref:`Flymake <pylint_in_flymake>`
- `Jupyter Notebook`_
- Komodo_
- `Pycharm`_
- PyDev_
- pyscripter_ in the `Tool -> Tools` menu.
- Spyder_ in the `View -> Panes -> Static code analysis`
- `Sublime Text`_
- :ref:`TextMate <pylint_in_textmate>`
- Vim_
- `Visual Studio Code`_ in the `Preferences -> Settings` menu
- `Visual Studio Code Pylint Extension`_
- `Visual Studio`_ in the `Python > Run PyLint` command on a project's context menu.
- WingIDE_

.. _Eclipse: https://www.pydev.org/manual_adv_pylint.html
.. _Emacs: https://www.emacswiki.org/emacs/PythonProgrammingInEmacs
.. _Eric IDE: https://eric-ide.python-projects.org/
.. _gedit: https://launchpad.net/gedit-pylint-2
.. _another option for gedit: https://wiki.gnome.org/Apps/Gedit/PylintPlugin
.. _Jupyter Notebook:  https://github.com/nbQA-dev/nbQA
.. _Komodo: https://mateusz.loskot.net/post/2006/01/15/running-pylint-from-komodo/
.. _Pycharm: https://stackoverflow.com/a/46409649/2519059
.. _pydev: https://www.pydev.org/manual_adv_pylint.html
.. _pyscripter: https://github.com/pyscripter/pyscripter
.. _spyder: https://docs.spyder-ide.org/current/panes/pylint.html
.. _Sublime Text: https://packagecontrol.io/packages/SublimeLinter-pylint
.. _Vim: https://www.vim.org/scripts/script.php?script_id=891
.. _Visual Studio: https://docs.microsoft.com/visualstudio/python/code-pylint
.. _Visual Studio Code: https://code.visualstudio.com/docs/python/linting
.. _Visual Studio Code Pylint Extension: https://marketplace.visualstudio.com/items?itemName=ms-python.pylint
.. _WingIDE: https://wingware.com/doc/warnings/external-checkers

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   flymake-emacs.rst
   textmate.rst
````

## File: doc/user_guide/installation/ide_integration/textmate.rst
````
.. _pylint_in_textmate:

Integrate Pylint with TextMate
==============================

Install Pylint in the usual way::

    pip install pylint

Install the `Python bundle for TextMate <https://github.com/textmate/python.tmbundle>`_:

#.  select *TextMate* > *Preferences*
#.  select the *Bundles* tab
#.  find and tick the *Python* bundle in the list

You should now see it in *Bundles* > *Python*.

In *Preferences*, select the *Variables* tab. If a ``TM_PYCHECKER`` variable is not already listed, add
it, with the value ``pylint``.

The default keyboard shortcut to run the syntax checker is *Control-Shift-V* - open a ``.py`` file
in Textmate, and try it.

You should see the output in a new window:

    PyCheckMate 1.2 – Pylint 1.4.4

    No config file found, using default configuration

Then all is well, and most likely Pylint will have expressed some opinions about your Python code
(or will exit with ``0`` if your code already conforms to its expectations).

If you receive a message:

    Please install PyChecker, PyFlakes, Pylint, PEP 8 or flake8 for more extensive code checking.

That means that Pylint wasn't found, which is likely an issue with command paths - TextMate needs
be looking for Pylint on the right paths.

Check where Pylint has been installed, using ``which``::

    $ which pylint
    /usr/local/bin/pylint

The output will tell you where Pylint can be found; in this case, in ``/usr/local/bin``.

#. select *TextMate* > *Preferences*
#. select the *Variables* tab
#. find and check that a ``PATH`` variable exists, and that it contains the appropriate path (if
   the path to Pylint were ``/usr/local/bin/pylint`` as above, then the variable would need to
   contain ``/usr/local/bin``). An actual example in this case might be
   ``$PATH:/opt/local/bin:/usr/local/bin:/usr/texbin``, which includes other paths.

... and try running Pylint again.
````

## File: doc/user_guide/installation/badge.rst
````
.. _badge:

Show your usage
---------------

You can place this badge in your README to let others know your project uses pylint.

    .. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
        :target: https://github.com/pylint-dev/pylint

Use the badge in your project's README.md (or any other Markdown file)::

    [![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

Use the badge in your project's README.rst (or any other rst file)::

    .. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
        :target: https://github.com/pylint-dev/pylint


If you use GitHub Actions, and one of your CI workflows begins with "name: pylint", you
can use GitHub's `workflow status badges <https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge#using-the-workflow-file-name>`_
to show an up-to-date indication of whether pushes to your default branch pass pylint.
For more detailed information, check the documentation.
````

## File: doc/user_guide/installation/command_line_installation.rst
````
.. _installation:

Command line installation
-------------------------

Pylint is installable using a package manager. Your package manager will find a version that
works with your interpreter. We recommend ``pip``:

.. code-block:: sh

   pip install pylint

Or if you want to also check spelling with ``enchant`` (you might need to
`install the enchant C library <https://pyenchant.github.io/pyenchant/install.html#installing-the-enchant-c-library>`_):

.. code-block:: sh

   pip install pylint[spelling]

The newest pylint supports all Python interpreters that are not past end of life.

We recommend to use the latest interpreter because we rely on the ``ast`` builtin
module that gets better with each new Python interpreter. For example a Python
3.6 interpreter can't analyse 3.8 syntax (amongst others, because of the new walrus operator) while a 3.8
interpreter can also deal with Python 3.6. See :ref:`using pylint with multiple interpreters <continuous-integration>` for more details.

.. note::
    You can also use ``conda`` or your system package manager on debian based OS.
    These package managers lag a little behind as they are maintained by a separate
    entity on a slower release cycle.

    .. code-block:: sh

       conda install pylint

    .. code-block:: sh

       sudo apt-get install pylint
````

## File: doc/user_guide/installation/index.rst
````
Installation
============

Pylint can be installed:

- :ref:`As a command line tool <installation>`
- :ref:`Integrated in your editor/ide <ide-integration>`
- :ref:`As a pre-commit hook <pre-commit-integration>`
- :ref:`For multiple python interpreters in your continuous integration <continuous-integration>`

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   command_line_installation.rst
   ide_integration/index
   pre-commit-integration.rst
   with-multiple-interpreters.rst
   badge
   upgrading_pylint.rst
````

## File: doc/user_guide/installation/pre-commit-integration.rst
````
.. _pre-commit-integration:

Pre-commit integration
======================

``pylint`` can be used as a `pre-commit <https://pre-commit.com>`_ hook. We however
discourage it as pylint -- due to its speed -- is more suited to a continuous integration
job or a git ``pre-push`` hook, especially if your repository is large.

Since ``pylint`` needs to import modules and dependencies to work correctly, the
hook only works with a local installation of ``pylint`` (in your environment). It means
it can't be used with ``pre-commit.ci``, and you will need to add the following to your
``.pre-commit-config.yaml`` ::

.. sourcecode:: yaml

    ci:
      skip: [pylint]

Another limitation is that pylint should analyse all your code at once in order to best infer the
actual values that result from calls. If only some of the files are given, pylint might
miss a particular value's type and produce inferior inference for the subset. Since pre-commit slices
the files given to it in order to parallelize the processing, the result can be degraded.
It can also be unexpectedly different when the file set changes because the new slicing can change
the inference. Thus the ``require_serial`` option should be set to ``true`` if correctness and determinism
are more important than parallelization to you.

If you installed ``pylint`` locally it can be added to ``.pre-commit-config.yaml``
as follows:

.. sourcecode:: yaml

  - repo: local
    hooks:
      - id: pylint
        name: pylint
        entry: pylint
        language: system
        types: [python]
        require_serial: true
        args:
          [
            "-rn", # Only display messages
            "-sn", # Don't display the score
          ]

You can use ``args`` to pass command line arguments as described in the :ref:`tutorial`.
A hook with more arguments could look something like this:

.. sourcecode:: yaml

  - repo: local
    hooks:
      - id: pylint
        name: pylint
        entry: pylint
        language: system
        types: [python]
        args:
          [
            "-rn", # Only display messages
            "-sn", # Don't display the score
            "--rcfile=pylintrc", # Link to your config file
            "--load-plugins=pylint.extensions.docparams", # Load an extension
          ]
````

## File: doc/user_guide/installation/upgrading_pylint.rst
````
.. _upgrading_pylint:

Upgrading pylint
================

You should probably set the version of pylint in your development environment in order to
choose when you actually upgrade pylint's warnings. pylint is following semver versioning.
But we can't guarantee that the output between version will stays the same. What this means
is that:

.. include:: ../../development_guide/contributor_guide/patch_release.rst

You can expect less messages if you set the minor and upgrade to a new patch version.
But still, if you enable ``useless-suppression`` it still means you can get a new
``useless-suppression`` when a false positive that you disabled is now fixed. Also,
if a library you're using was upgraded and is understood better or worse than the
previous one, you could get new messages too.

.. include:: ../../development_guide/contributor_guide/minor_release.rst

You can expect a lot more change in output, the main one being new checks.

.. include:: ../../development_guide/contributor_guide/major_release.rst

You could have to change the command you're launching or the plugin and
editor integration you're using.
````

## File: doc/user_guide/installation/with-multiple-interpreters.rst
````
.. _continuous-integration:

Installation with multiple interpreters
=======================================

It's possible to analyse code written for older or multiple interpreters by using
the ``py-version`` option and setting it to the oldest supported interpreter of your code. For example you can check
that there are no ``f-strings`` in Python 3.5 code using Python 3.8 with an up-to-date
pylint even if Python 3.5 is past end of life (EOL) and the version of pylint you use is not
compatible with it.

We do not guarantee that ``py-version`` will work for all EOL Python interpreters indefinitely,
(for anything before Python 3.5, it probably won't). If a newer version does not work for you,
the best available pylint might be an old version that works with your old interpreter but
without the bug fixes and features of later versions.
````

## File: doc/user_guide/messages/index.rst
````
.. _messages:

########
Messages
########

.. toctree::
  :maxdepth: 1
  :hidden:

  messages_overview.rst
  message_control.rst

Messages categories
===================

Pylint can emit various messages. These are categorized according
to categories corresponding to bit-encoded exit codes:

* :ref:`Fatal <fatal-category>` (1)
* :ref:`Error <error-category>` (2)
* :ref:`Warning <warning-category>` (4)
* :ref:`Convention <convention-category>` (8)
* :ref:`Refactor <refactor-category>` (16)
* :ref:`Information <information-category>` (NA)

An overview of these messages can be found in :ref:`messages-overview`

Disabling messages
==================

``pylint`` has an advanced message control for its checks, offering the ability
to enable / disable a message either from the command line or from the configuration
file, as well as from the code itself.

For more detail see :ref:`message-control`
````

## File: doc/user_guide/messages/message_control.rst
````
.. _message-control:

Messages control
================

In order to control messages, ``pylint`` accepts the following values:

* a symbolic message: ``no-member``, ``undefined-variable`` etc.

* a numerical ID: ``E1101``, ``E1102`` etc.

* The name of the group of checks. You can grab those with ``pylint --list-groups``.
  For example, you can disable / enable all the checks related to type checking, with
  ``typecheck`` or all the checks related to variables with ``variables``

* Corresponding category of the checks

  * ``C`` convention related checks
  * ``R`` refactoring related checks
  * ``W`` various warnings
  * ``E`` errors, for probable bugs in the code
  * ``F`` fatal, if an error occurred which prevented ``pylint`` from doing further processing.

* All the checks with ``all``

.. _block_disables:

Block disables
--------------

This describes how the pragma controls operate at a code level.

The pragma controls can disable / enable:

* All the violations on a single line

.. sourcecode:: python

    a, b = ... # pylint: disable=unbalanced-tuple-unpacking

* All the violations on the following line

.. sourcecode:: python

    # pylint: disable-next=unbalanced-tuple-unpacking
    a, b = ...

* All the violations in a single scope

.. sourcecode:: python

    def test():
        # Disable all the no-member violations in this function
        # pylint: disable=no-member
        ...

* All the violations in a `block`. For instance, each separate branch of an
  ``if`` statement is considered a separate block, as in the following example:

.. sourcecode:: python

    def meth5(self):
        # pylint: disable=no-member
        # no error
        print(self.bla)
        if self.blop:
            # pylint: enable=no-member
            # enable all no-members for this block
            print(self.blip)
        else:
            # This is affected by the scope disable
            print(self.blip)
        # pylint: enable=no-member
        print(self.blip)
        if self.blop:
            # pylint: disable=no-member
            # disable all no-members for this block
            print(self.blip)
        else:
            # This emits a violation
            print(self.blip)


* If the violation occurs on a block starting line, then it applies only to that line

.. sourcecode:: python

    if self.blop: # pylint: disable=no-member; applies only to this line
        # Here we get an error
        print(self.blip)
    else:
        # error
        print(self.blip)



Here's an example with all these rules in a single place:

.. sourcecode:: python

    """pylint option block-disable"""

    __revision__ = None

    class Foo(object):
        """block-disable test"""

        def __init__(self):
            pass

        def meth1(self, arg):
            """this issues a message"""
            print(self)

        def meth2(self, arg):
            """and this one not"""
            # pylint: disable=unused-argument
            print(self\
                  + "foo")

        def meth3(self):
            """test one line disabling"""
            # no error
            print(self.bla) # pylint: disable=no-member
            # error
            print(self.blop)

        def meth4(self):
            """test re-enabling"""
            # pylint: disable=no-member
            # no error
            print(self.bla)
            print(self.blop)
            # pylint: enable=no-member
            # error
            print(self.blip)

        def meth5(self):
            """test IF sub-block re-enabling"""
            # pylint: disable=no-member
            # no error
            print(self.bla)
            if self.blop:
                # pylint: enable=no-member
                # error
                print(self.blip)
            else:
                # no error
                print(self.blip)
            # no error
            print(self.blip)

        def meth6(self):
            """test TRY/EXCEPT sub-block re-enabling"""
            # pylint: disable=no-member
            # no error
            print(self.bla)
            try:
                # pylint: enable=no-member
                # error
                print(self.blip)
            except UndefinedName: # pylint: disable=undefined-variable
                # no error
                print(self.blip)
            # no error
            print(self.blip)

        def meth7(self):
            """test one line block opening disabling"""
            if self.blop: # pylint: disable=no-member
                # error
                print(self.blip)
            else:
                # error
                print(self.blip)
            # error
            print(self.blip)

        def meth8(self):
            """test late disabling"""
            # error
            print(self.blip)
            # pylint: disable=no-member
            # no error
            print(self.bla)
            print(self.blop)

        def meth9(self):
            """test next line disabling"""
            # no error
            # pylint: disable-next=no-member
            print(self.bla)
            # error
            print(self.blop)


Detecting useless disables
--------------------------

As pylint gets better and false positives are removed,
disables that became useless can accumulate and clutter the code.
In order to clean them you can enable the ``useless-suppression`` warning.
````

## File: doc/user_guide/messages/messages_overview.rst
````
.. _messages-overview:

#################
Messages overview
#################


.. This file is auto-generated. Make any changes to the associated
.. docs extension in 'doc/exts/pylint_messages.py'.

Pylint can emit the following messages:


.. _fatal-category:

Fatal
*****

All messages in the fatal category:

.. toctree::
   :maxdepth: 2
   :titlesonly:

   fatal/astroid-error
   fatal/config-parse-error
   fatal/fatal
   fatal/method-check-failed
   fatal/parse-error

All renamed messages in the fatal category:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   fatal/old-import-error

.. _error-category:

Error
*****

All messages in the error category:

.. toctree::
   :maxdepth: 2
   :titlesonly:

   error/abstract-class-instantiated
   error/access-member-before-definition
   error/assigning-non-slot
   error/assignment-from-no-return
   error/assignment-from-none
   error/await-outside-async
   error/bad-configuration-section
   error/bad-except-order
   error/bad-exception-cause
   error/bad-format-character
   error/bad-plugin-value
   error/bad-reversed-sequence
   error/bad-str-strip-call
   error/bad-string-format-type
   error/bad-super-call
   error/bare-name-capture-pattern
   error/bidirectional-unicode
   error/broken-collections-callable
   error/broken-noreturn
   error/catching-non-exception
   error/class-variable-slots-conflict
   error/declare-non-slot
   error/dict-iter-missing-items
   error/duplicate-argument-name
   error/duplicate-bases
   error/format-needs-mapping
   error/function-redefined
   error/import-error
   error/inconsistent-mro
   error/inherit-non-class
   error/init-is-generator
   error/invalid-all-format
   error/invalid-all-object
   error/invalid-bool-returned
   error/invalid-bytes-returned
   error/invalid-character-backspace
   error/invalid-character-carriage-return
   error/invalid-character-esc
   error/invalid-character-nul
   error/invalid-character-sub
   error/invalid-character-zero-width-space
   error/invalid-class-object
   error/invalid-enum-extension
   error/invalid-envvar-value
   error/invalid-field-call
   error/invalid-format-returned
   error/invalid-getnewargs-ex-returned
   error/invalid-getnewargs-returned
   error/invalid-hash-returned
   error/invalid-index-returned
   error/invalid-length-hint-returned
   error/invalid-length-returned
   error/invalid-metaclass
   error/invalid-repr-returned
   error/invalid-sequence-index
   error/invalid-slice-index
   error/invalid-slice-step
   error/invalid-slots
   error/invalid-slots-object
   error/invalid-star-assignment-target
   error/invalid-str-returned
   error/invalid-unary-operand-type
   error/invalid-unicode-codec
   error/logging-format-truncated
   error/logging-too-few-args
   error/logging-too-many-args
   error/logging-unsupported-format
   error/method-hidden
   error/misplaced-bare-raise
   error/misplaced-format-function
   error/missing-format-string-key
   error/missing-kwoa
   error/mixed-format-string
   error/modified-iterating-dict
   error/modified-iterating-set
   error/no-member
   error/no-method-argument
   error/no-name-in-module
   error/no-self-argument
   error/no-value-for-parameter
   error/non-iterator-returned
   error/nonexistent-operator
   error/nonlocal-and-global
   error/nonlocal-without-binding
   error/not-a-mapping
   error/not-an-iterable
   error/not-async-context-manager
   error/not-callable
   error/not-context-manager
   error/not-in-loop
   error/notimplemented-raised
   error/positional-only-arguments-expected
   error/possibly-used-before-assignment
   error/potential-index-error
   error/raising-bad-type
   error/raising-non-exception
   error/redundant-keyword-arg
   error/relative-beyond-top-level
   error/repeated-keyword
   error/return-arg-in-generator
   error/return-in-init
   error/return-outside-function
   error/singledispatch-method
   error/singledispatchmethod-function
   error/star-needs-assignment-target
   error/syntax-error
   error/too-few-format-args
   error/too-many-format-args
   error/too-many-function-args
   error/too-many-star-expressions
   error/truncated-format-string
   error/undefined-all-variable
   error/undefined-variable
   error/unexpected-keyword-arg
   error/unexpected-special-method-signature
   error/unhashable-member
   error/unpacking-non-sequence
   error/unrecognized-inline-option
   error/unrecognized-option
   error/unsubscriptable-object
   error/unsupported-assignment-operation
   error/unsupported-binary-operation
   error/unsupported-delete-operation
   error/unsupported-membership-test
   error/used-before-assignment
   error/used-prior-global-declaration
   error/yield-inside-async-function
   error/yield-outside-function

All renamed messages in the error category:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   error/bad-context-manager
   error/bad-exception-context
   error/bad-option-value
   error/maybe-no-member
   error/old-non-iterator-returned-2
   error/old-unbalanced-tuple-unpacking
   error/unhashable-dict-key

.. _warning-category:

Warning
*******

All messages in the warning category:

.. toctree::
   :maxdepth: 2
   :titlesonly:

   warning/abstract-method
   warning/anomalous-backslash-in-string
   warning/anomalous-unicode-escape-in-string
   warning/arguments-differ
   warning/arguments-out-of-order
   warning/arguments-renamed
   warning/assert-on-string-literal
   warning/assert-on-tuple
   warning/attribute-defined-outside-init
   warning/bad-builtin
   warning/bad-chained-comparison
   warning/bad-dunder-name
   warning/bad-format-string
   warning/bad-format-string-key
   warning/bad-indentation
   warning/bad-open-mode
   warning/bad-staticmethod-argument
   warning/bad-thread-instantiation
   warning/bare-except
   warning/binary-op-exception
   warning/boolean-datetime
   warning/break-in-finally
   warning/broad-exception-caught
   warning/broad-exception-raised
   warning/cell-var-from-loop
   warning/comparison-with-callable
   warning/confusing-with-statement
   warning/consider-ternary-expression
   warning/contextmanager-generator-missing-cleanup
   warning/continue-in-finally
   warning/dangerous-default-value
   warning/deprecated-argument
   warning/deprecated-attribute
   warning/deprecated-class
   warning/deprecated-decorator
   warning/deprecated-method
   warning/deprecated-module
   warning/deprecated-typing-alias
   warning/differing-param-doc
   warning/differing-type-doc
   warning/duplicate-except
   warning/duplicate-key
   warning/duplicate-string-formatting-argument
   warning/duplicate-value
   warning/eq-without-hash
   warning/eval-used
   warning/exec-used
   warning/expression-not-assigned
   warning/f-string-without-interpolation
   warning/fixme
   warning/forgotten-debug-statement
   warning/format-combined-specification
   warning/format-string-without-interpolation
   warning/global-at-module-level
   warning/global-statement
   warning/global-variable-not-assigned
   warning/global-variable-undefined
   warning/implicit-flag-alias
   warning/implicit-str-concat
   warning/import-self
   warning/inconsistent-quotes
   warning/invalid-envvar-default
   warning/invalid-format-index
   warning/invalid-overridden-method
   warning/isinstance-second-argument-not-valid-type
   warning/keyword-arg-before-vararg
   warning/kwarg-superseded-by-positional-arg
   warning/logging-format-interpolation
   warning/logging-fstring-interpolation
   warning/logging-not-lazy
   warning/lost-exception
   warning/method-cache-max-size-none
   warning/misplaced-future
   warning/missing-any-param-doc
   warning/missing-format-argument-key
   warning/missing-format-attribute
   warning/missing-param-doc
   warning/missing-parentheses-for-call-in-test
   warning/missing-raises-doc
   warning/missing-return-doc
   warning/missing-return-type-doc
   warning/missing-timeout
   warning/missing-type-doc
   warning/missing-yield-doc
   warning/missing-yield-type-doc
   warning/modified-iterating-list
   warning/multiple-constructor-doc
   warning/named-expr-without-context
   warning/nan-comparison
   warning/nested-min-max
   warning/non-ascii-file-name
   warning/non-parent-init-called
   warning/non-str-assignment-to-dunder-name
   warning/overlapping-except
   warning/overridden-final-method
   warning/pointless-exception-statement
   warning/pointless-statement
   warning/pointless-string-statement
   warning/possibly-unused-variable
   warning/preferred-module
   warning/protected-access
   warning/raise-missing-from
   warning/raising-format-tuple
   warning/redeclared-assigned-name
   warning/redefined-builtin
   warning/redefined-loop-name
   warning/redefined-outer-name
   warning/redefined-slots-in-subclass
   warning/redundant-returns-doc
   warning/redundant-u-string-prefix
   warning/redundant-unittest-assert
   warning/redundant-yields-doc
   warning/reimported
   warning/return-in-finally
   warning/self-assigning-variable
   warning/self-cls-assignment
   warning/shadowed-import
   warning/shallow-copy-environ
   warning/signature-differs
   warning/subclassed-final-class
   warning/subprocess-popen-preexec-fn
   warning/subprocess-run-check
   warning/super-init-not-called
   warning/super-without-brackets
   warning/too-many-try-statements
   warning/try-except-raise
   warning/unbalanced-dict-unpacking
   warning/unbalanced-tuple-unpacking
   warning/undefined-loop-variable
   warning/unknown-option-value
   warning/unnecessary-ellipsis
   warning/unnecessary-lambda
   warning/unnecessary-pass
   warning/unnecessary-semicolon
   warning/unreachable
   warning/unspecified-encoding
   warning/unused-argument
   warning/unused-format-string-argument
   warning/unused-format-string-key
   warning/unused-import
   warning/unused-private-member
   warning/unused-variable
   warning/unused-wildcard-import
   warning/useless-else-on-loop
   warning/useless-param-doc
   warning/useless-parent-delegation
   warning/useless-type-doc
   warning/useless-with-lock
   warning/using-assignment-expression-in-unsupported-version
   warning/using-constant-test
   warning/using-exception-groups-in-unsupported-version
   warning/using-f-string-in-unsupported-version
   warning/using-final-decorator-in-unsupported-version
   warning/using-generic-type-syntax-in-unsupported-version
   warning/using-positional-only-args-in-unsupported-version
   warning/while-used
   warning/wildcard-import
   warning/wrong-exception-operation

All renamed messages in the warning category:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   warning/broad-except
   warning/cache-max-size-none
   warning/implicit-str-concat-in-sequence
   warning/lru-cache-decorating-method
   warning/old-assignment-from-none
   warning/old-deprecated-argument
   warning/old-deprecated-class
   warning/old-deprecated-decorator
   warning/old-deprecated-method
   warning/old-deprecated-module
   warning/old-empty-docstring
   warning/old-missing-param-doc
   warning/old-missing-returns-doc
   warning/old-missing-type-doc
   warning/old-missing-yields-doc
   warning/old-non-iterator-returned-1
   warning/old-unidiomatic-typecheck
   warning/old-unpacking-non-sequence
   warning/useless-super-delegation

.. _convention-category:

Convention
**********

All messages in the convention category:

.. toctree::
   :maxdepth: 2
   :titlesonly:

   convention/bad-classmethod-argument
   convention/bad-docstring-quotes
   convention/bad-file-encoding
   convention/bad-mcs-classmethod-argument
   convention/bad-mcs-method-argument
   convention/consider-iterating-dictionary
   convention/consider-using-any-or-all
   convention/consider-using-dict-items
   convention/consider-using-enumerate
   convention/consider-using-f-string
   convention/dict-init-mutate
   convention/disallowed-name
   convention/docstring-first-line-empty
   convention/empty-docstring
   convention/import-outside-toplevel
   convention/import-private-name
   convention/invalid-characters-in-docstring
   convention/invalid-name
   convention/line-too-long
   convention/misplaced-comparison-constant
   convention/missing-class-docstring
   convention/missing-final-newline
   convention/missing-function-docstring
   convention/missing-module-docstring
   convention/mixed-line-endings
   convention/multiple-imports
   convention/multiple-statements
   convention/non-ascii-module-import
   convention/non-ascii-name
   convention/single-string-used-for-slots
   convention/singleton-comparison
   convention/superfluous-parens
   convention/too-many-lines
   convention/trailing-newlines
   convention/trailing-whitespace
   convention/typevar-double-variance
   convention/typevar-name-incorrect-variance
   convention/typevar-name-mismatch
   convention/unexpected-line-ending-format
   convention/ungrouped-imports
   convention/unidiomatic-typecheck
   convention/unnecessary-direct-lambda-call
   convention/unnecessary-dunder-call
   convention/unnecessary-lambda-assignment
   convention/unnecessary-negation
   convention/use-implicit-booleaness-not-comparison
   convention/use-implicit-booleaness-not-comparison-to-string
   convention/use-implicit-booleaness-not-comparison-to-zero
   convention/use-implicit-booleaness-not-len
   convention/use-maxsplit-arg
   convention/use-sequence-for-iteration
   convention/useless-import-alias
   convention/wrong-import-order
   convention/wrong-import-position
   convention/wrong-spelling-in-comment
   convention/wrong-spelling-in-docstring

All renamed messages in the convention category:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   convention/blacklisted-name
   convention/compare-to-empty-string
   convention/compare-to-zero
   convention/len-as-condition
   convention/missing-docstring
   convention/old-misplaced-comparison-constant
   convention/old-non-ascii-name
   convention/unneeded-not

.. _refactor-category:

Refactor
********

All messages in the refactor category:

.. toctree::
   :maxdepth: 2
   :titlesonly:

   refactor/chained-comparison
   refactor/comparison-of-constants
   refactor/comparison-with-itself
   refactor/condition-evals-to-constant
   refactor/confusing-consecutive-elif
   refactor/consider-alternative-union-syntax
   refactor/consider-merging-isinstance
   refactor/consider-refactoring-into-while-condition
   refactor/consider-swap-variables
   refactor/consider-using-alias
   refactor/consider-using-assignment-expr
   refactor/consider-using-augmented-assign
   refactor/consider-using-dict-comprehension
   refactor/consider-using-from-import
   refactor/consider-using-generator
   refactor/consider-using-get
   refactor/consider-using-in
   refactor/consider-using-join
   refactor/consider-using-max-builtin
   refactor/consider-using-min-builtin
   refactor/consider-using-namedtuple-or-dataclass
   refactor/consider-using-set-comprehension
   refactor/consider-using-sys-exit
   refactor/consider-using-ternary
   refactor/consider-using-tuple
   refactor/consider-using-with
   refactor/cyclic-import
   refactor/duplicate-code
   refactor/else-if-used
   refactor/empty-comment
   refactor/inconsistent-return-statements
   refactor/literal-comparison
   refactor/magic-value-comparison
   refactor/no-classmethod-decorator
   refactor/no-else-break
   refactor/no-else-continue
   refactor/no-else-raise
   refactor/no-else-return
   refactor/no-self-use
   refactor/no-staticmethod-decorator
   refactor/prefer-typing-namedtuple
   refactor/property-with-parameters
   refactor/redefined-argument-from-local
   refactor/redefined-variable-type
   refactor/redundant-typehint-argument
   refactor/simplifiable-condition
   refactor/simplifiable-if-expression
   refactor/simplifiable-if-statement
   refactor/simplify-boolean-expression
   refactor/stop-iteration-return
   refactor/super-with-arguments
   refactor/too-complex
   refactor/too-few-public-methods
   refactor/too-many-ancestors
   refactor/too-many-arguments
   refactor/too-many-boolean-expressions
   refactor/too-many-branches
   refactor/too-many-instance-attributes
   refactor/too-many-locals
   refactor/too-many-nested-blocks
   refactor/too-many-positional-arguments
   refactor/too-many-public-methods
   refactor/too-many-return-statements
   refactor/too-many-statements
   refactor/trailing-comma-tuple
   refactor/unnecessary-comprehension
   refactor/unnecessary-default-type-args
   refactor/unnecessary-dict-index-lookup
   refactor/unnecessary-list-index-lookup
   refactor/use-a-generator
   refactor/use-dict-literal
   refactor/use-list-literal
   refactor/use-set-for-membership
   refactor/use-yield-from
   refactor/useless-object-inheritance
   refactor/useless-option-value
   refactor/useless-return

All renamed messages in the refactor category:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   refactor/old-no-self-use
   refactor/old-simplifiable-if-statement
   refactor/old-too-many-nested-blocks

.. _information-category:

Information
***********

All messages in the information category:

.. toctree::
   :maxdepth: 2
   :titlesonly:

   information/bad-inline-option
   information/c-extension-no-member
   information/deprecated-pragma
   information/file-ignored
   information/locally-disabled
   information/raw-checker-failed
   information/suppressed-message
   information/use-symbolic-message-instead
   information/useless-suppression

All renamed messages in the information category:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   information/deprecated-disable-all
````

## File: doc/user_guide/usage/index.rst
````
Usage
=====

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   run
   output
````

## File: doc/user_guide/usage/output.rst
````
Pylint output
-------------

Output options
''''''''''''''''''''''''''''
Output by default is written to stdout. The simplest way to output to a file is
with the ``--output=<filename>`` option.

The default format for the output is raw text. You can change this by passing
pylint the ``--output-format=<value>`` option. Possible values are:

* ``text``
* ``parseable``
* ``colorized``
* ``json2``: improved json format
* ``json``: old json format
* ``msvs``: visual studio
* ``github``: `GitHub action messages <https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions>`_

Multiple output formats can be used at the same time by passing
a comma-separated list of formats to ``--output-format``.
This output can be redirected to a file by giving a filename after a colon.

For example, to save a json report to ``somefile.json`` and print
a colorized report to stdout at the same time:
::

  --output-format=json:somefile.json,colorized


Custom message formats
''''''''''''''''''''''

You can customize the exact way information are displayed using the
`--msg-template=<format string>` option. The `format string` uses the
`Python new format syntax`_ and the following fields are available :

path
    relative path to the file
abspath
    absolute path to the file
line
    line number
column
    column number
end_line
    line number of the end of the node
end_column
    column number of the end of the node
module
    module name
obj
    object within the module (if any)
msg
    text of the message
msg_id
    the message code (eg. I0011)
symbol
    symbolic name of the message (eg. locally-disabled)
C
    one letter indication of the message category
category
    fullname of the message category

For example, the former (pre 1.0) default format can be obtained with::

  pylint --msg-template='{msg_id}:{line:3d},{column}: {obj}: {msg}'

A few other examples:

* the default format::

    {path}:{line}:{column}: {msg_id}: {msg} ({symbol})

* Visual Studio compatible format (former 'msvs' output format)::

    {path}({line}): [{msg_id}{obj}] {msg}

* Parseable (Emacs and all, former 'parseable' output format) format::

    {path}:{line}: [{msg_id}({symbol}), {obj}] {msg}

The ``--msg-template`` option can only be combined with text-based reporters (``--output-format`` either unspecified or one of: parseable, colorized or msvs).
If both ``--output-format`` and ``--msg-template`` are specified, the ``--msg-template`` option will take precedence over the default line format defined by the reporter class.

If ``end_line`` or ``end_column`` are ``None``, they will be represented as an empty string
by the default ``TextReporter``.

.. _Python new format syntax: https://docs.python.org/2/library/string.html#formatstrings

Source code analysis section
''''''''''''''''''''''''''''

For each python module, Pylint will first display a few '*' characters followed
by the name of the module. Then, a number of messages with the following format:
::

  MESSAGE_TYPE: LINE_NUM:[OBJECT:] MESSAGE

You can get another output format, useful since it's recognized by
most editors or other development tools using the ``--output-format=parseable``
option.

The message type can be:

  * [I]nformational messages that Pylint emits (do not contribute to your analysis score)
  * [R]efactor for a "good practice" metric violation
  * [C]onvention for coding standard violation
  * [W]arning for stylistic problems, or minor programming issues
  * [E]rror for important programming issues (i.e. most probably bug)
  * [F]atal for errors which prevented further processing

Sometimes the line of code which caused the error is displayed with
a caret pointing to the error. This may be generalized in future
versions of Pylint.

Example (extracted from a run of Pylint on itself...):

::

  ************* Module pylint.checkers.format
  W: 50: Too long line (86/80)
  W:108: Operator not followed by a space
       print >>sys.stderr, 'Unable to match %r', line
              ^
  W:141: Too long line (81/80)
  W: 74:searchall: Unreachable code
  W:171:FormatChecker.process_tokens: Redefining built-in (type)
  W:150:FormatChecker.process_tokens: Too many local variables (20/15)
  W:150:FormatChecker.process_tokens: Too many branches (13/12)


Reports section
'''''''''''''''

Following the analysis message, Pylint can display a set of reports,
each one focusing on a particular aspect of the project, such as number
of messages by categories, modules dependencies. These features can
be enabled through the ``--reports=y`` option, or its shorthand
version ``-ry``.

For instance, the metrics report displays summaries gathered from the
current run.

  * the number of processed modules
  * for each module, the percentage of errors and warnings
  * the total number of errors and warnings
  * percentage of classes, functions and modules with docstrings, and
    a comparison from the previous run
  * percentage of classes, functions and modules with correct name
    (according to the coding standard), and a comparison from the
    previous run
  * a list of external dependencies found in the code, and where they appear

Score section
'''''''''''''

Finally, Pylint displays a global evaluation score for the code, rated out of a
maximum score of 10.0. This output can be suppressed through the ``--score=n``
option, or its shorthand version ``-sn``.

The evaluation formula can be overridden with the
``--evaluation=<python_expression>`` option.
````

## File: doc/user_guide/usage/run.rst
````
================
 Running Pylint
================

On module packages or directories
---------------------------------

Pylint is meant to be called from the command line. The usage is ::

   pylint [options] modules_or_packages

By default the ``pylint`` command only accepts a list of python modules and packages.
On versions below 2.15, specifying a directory that is not an explicit package
(with ``__init__.py``) results in an error::

    pylint mydir
    ************* Module mydir
    mydir/__init__.py:1:0: F0010: error while code parsing: Unable to load file mydir/__init__.py:
    [Errno 2] No such file or directory: 'mydir/__init__.py' (parse-error)

Thus, on versions before 2.15 using the ``--recursive=y`` option allows for linting a namespace package::

    pylint --recursive=y mydir mymodule mypackage

This option makes ``pylint`` attempt to discover all modules (files ending with ``.py`` extension)
and all explicit packages (all directories containing a ``__init__.py`` file).

Pylint **will not import** this package or module, but it does use Python internals
to locate them and as such is subject to the same rules and configuration.
You should pay attention to your ``PYTHONPATH``, since it is a common error
to analyze an installed version of a module instead of the development version.

On files
--------

It is also possible to analyze Python files, with a few restrictions. As a convenience,
you can give it a file name if it's possible to guess a module name from the file's
path using the python path. Some examples:

``pylint mymodule.py`` should always work since the current working
directory is automatically added on top of the python path

``pylint directory/mymodule.py`` will work if: ``directory`` is a python
package (i.e. has an ``__init__.py`` file), an implicit namespace package
or if ``directory`` is in the python path.

With implicit namespace packages
--------------------------------

If the analyzed sources use implicit namespace packages (PEP 420), the source root(s) should
be specified using the ``--source-roots`` option. Otherwise, the package names are
detected incorrectly, since implicit namespace packages don't contain an ``__init__.py``.

Globbing support
----------------

It is also possible to specify both directories and files using globbing patterns::

   pylint [options] packages/*/src

Command line options
--------------------

.. _run_command_line:

First of all, we have two basic (but useful) options.

--version             show program's version number and exit
-h, --help            show help about the command line options

Pylint is architected around several checkers. You can disable a specific
checker or some of its messages or message categories by specifying
``--disable=<symbol>``. If you want to enable only some checkers or some
message symbols, first use ``--disable=all`` then
``--enable=<symbol>`` with ``<symbol>`` being a comma-separated list of checker
names and message symbols. See the list of available features for a
description of provided checkers with their functionalities.
The ``--disable`` and ``--enable`` options can be used with comma-separated lists
mixing checkers, message ids and categories like ``-d C,W,no-error,design``

It is possible to disable all messages with ``--disable=all``. This is
useful to enable only a few checkers or a few messages by first
disabling everything, and then re-enabling only what you need.

Each checker has some specific options, which can take either a yes/no
value, an integer, a python regular expression, or a comma-separated
list of values (which are generally used to override a regular
expression in special cases). For a full list of options, use ``--help``

Specifying all the options suitable for your setup and coding
standards can be tedious, so it is possible to use a configuration file to
specify the default values.  You can specify a configuration file on the
command line using the ``--rcfile`` option.  Otherwise, Pylint searches for a
configuration file in the following order and uses the first one it finds:

#. ``pylintrc`` in the current working directory
#. ``pylintrc.toml`` in the current working directory,
   providing it has at least one ``tool.pylint.`` section.
#. ``.pylintrc`` in the current working directory
#. ``.pylintrc.toml`` in the current working directory,
   providing it has at least one ``tool.pylint.`` section.
#. ``pyproject.toml`` in the current working directory,
   providing it has at least one ``tool.pylint.`` section.
   The ``pyproject.toml`` must prepend section names with ``tool.pylint.``,
   for example ``[tool.pylint.'MESSAGES CONTROL']``. They can also be passed
   in on the command line.
#. ``setup.cfg`` in the current working directory,
   providing it has at least one ``pylint.`` section
#. ``tox.ini`` in the current working directory,
   providing it has at least one ``pylint.`` section
#. Pylint will search for the ``pyproject.toml`` file up the directories hierarchy
   unless it's found, or a ``.git``/``.hg`` directory is found, or the file system root
   is approached.
#. If the current working directory is in a Python package, Pylint searches \
   up the hierarchy of Python packages until it finds a ``pylintrc`` file. \
   This allows you to specify coding standards on a module-by-module \
   basis.  Of course, a directory is judged to be a Python package if it \
   contains an ``__init__.py`` file.
#. The file named by environment variable ``PYLINTRC``
#. if you have a home directory which isn't ``/root``:

   #. ``.pylintrc`` in your home directory
   #. ``.config/pylintrc`` in your home directory

#. ``/etc/pylintrc``

The ``--generate-toml-config`` option will generate a commented configuration file
on standard output according to the current configuration and exit. This
includes:

* Any configuration file found as explained above
* Options appearing before ``--generate-toml-config`` on the Pylint command line

Of course you can also start with the default values and hand-tune the
configuration.

Other useful global options include:

--ignore=<file[,file...]>  Files or directories to be skipped. They should be
                           base names, not paths.
--output-format=<format>   Select output format (text, json, custom).
--msg-template=<template>  Modify text output message template.
--list-msgs                Generate pylint's messages.
--list-msgs-enabled        Display a list of what messages are enabled and
                           disabled with the given configuration.
--full-documentation       Generate pylint's full documentation, in reST
                             format.

Parallel execution
------------------

It is possible to speed up the execution of Pylint. If the running computer
has more CPUs than one, then the work for checking all files could be spread across all
cores via Pylints's sub-processes.

This functionality is exposed via the ``-j`` command-line parameter.
If the provided number is 0, then the total number of CPUs will be autodetected and used.

Example::

  pylint -j 4 mymodule1.py mymodule2.py mymodule3.py mymodule4.py

This will spawn 4 parallel Pylint sub-process, where each provided module will
be checked in parallel. Discovered problems by checkers are not displayed
immediately. They are shown just after checking a module is complete.

You can also do your own parallelization by launching pylint multiple times on subsets
of your files (like ``pre-commit`` with the default ``require_serial=false`` does).
Be aware, though: pylint should analyse all your code at once in order to best infer
the actual values that result from calls. If only some of the files are given, pylint
might miss a particular value's type and produce inferior inference for the subset.
It can also be unexpectedly different when the file set changes because the new
slicing can change the inference. So, don't do this if correctness and determinism
are important to you.

Exit codes
----------

Pylint returns bit-encoded exit codes.

=========  =========================
exit code  meaning
=========  =========================
0          no error
1          fatal message issued
2          error message issued
4          warning message issued
8          refactor message issued
16         convention message issued
32         usage error
=========  =========================

For example, an exit code of ``20`` means there was at least one warning message (4)
and at least one convention message (16) and nothing else.
````

## File: doc/whatsnew/0/0.x.rst
````
What's New in Pylint 0.28.0?
============================
Release date: 2013-04-25

* bitbucket #1: fix "dictionary changed size during iteration" crash

* #74013: new E1310[bad-str-strip-call] message warning when a call to a
  {l,r,}strip method contains duplicate characters (patch by Torsten Marek)

* #123233: new E0108[duplicate-argument-name] message reporting duplicate
  argument names

* #81378: emit W0120[useless-else-on-loop] for loops without break

* #124660: internal dependencies should not appear in external dependencies
  report

* #124662: fix name error causing crash when symbols are included in output
  messages

* #123285: apply pragmas for warnings attached to lines to physical source
  code lines

* #123259: do not emit E0105 for yield expressions inside lambdas

* #123892: don't crash when attempting to show source code line that can't
  be encoded with the current locale settings

* Simplify checks for dangerous default values by unifying tests for all
  different mutable compound literals.

* Improve the description for E1124[redundant-keyword-arg]


What's New in Pylint 0.27.0?
============================
Release date: 2013-02-26

* #20693: replace pylint.el by Ian Eure version (patch by J.Kotta)

* #105327: add support for --disable=all option and deprecate the
  'disable-all' inline directive in favour of 'skip-file' (patch by
  A.Fayolle)

* #110840: add messages I0020 and I0021 for reporting of suppressed
  messages and useless suppression pragmas. (patch by Torsten Marek)

* #112728: add warning E0604 for non-string objects in __all__
  (patch by Torsten Marek)

* #120657: add warning W0110/deprecated-lambda when a map/filter
  of a lambda could be a comprehension (patch by Martin Pool)

* #113231: logging checker now looks at instances of Logger classes
  in addition to the base logging module. (patch by Mike Bryant)

* #111799: don't warn about octal escape sequence, but warn about \o
  which is not octal in Python (patch by Martin Pool)

* #110839: bind <F5> to Run button in pylint-gui

* #115580: fix erroneous W0212 (access to protected member) on super call
  (patch by Martin Pool)

* #110853: fix a crash when an __init__ method in a base class has been
  created by assignment rather than direct function definition (patch by
  Torsten Marek)

* #110838: fix pylint-gui crash when include-ids is activated (patch by
  Omega Weapon)

* #112667: fix emission of reimport warnings for mixed imports and extend
  the testcase (patch by Torsten Marek)

* #112698: fix crash related to non-inferable __all__ attributes and
  invalid __all__ contents (patch by Torsten Marek)

* Python 3 related fixes:

* #110213: fix import of checkers broken with python 3.3, causing
    "No such message id W0704" breakage

* #120635: redefine cmp function used in pylint.reporters

* Include full warning id for I0020 and I0021 and make sure to flush
  warnings after each module, not at the end of the pylint run.
  (patch by Torsten Marek)

* Changed the regular expression for inline options so that it must be
  preceded by a # (patch by Torsten Marek)

* Make dot output for import graph predictable and not depend
  on ordering of strings in hashes. (patch by Torsten Marek)

* Add hooks for import path setup and move pylint's sys.path
  modifications into them. (patch by Torsten Marek)


What's New in Pylint 0.26.0?
============================
Release date: 2012-10-05

* #106534: add --ignore-imports option to code similarity checking
  and 'symilar' command line tool (patch by Ry4an Brase)

* #104571: check for anomalous backslash escape, introducing new
  W1401 and W1402 messages (patch by Martin Pool)

* #100707: check for boolop being used as exception class, introducing
  new W0711 message (patch by Tim Hatch)

* #4014: improve checking of metaclass methods first args, introducing
  new C0204 message (patch by lothiraldan@gmail.com finalized by sthenault)

* #4685: check for consistency of a module's __all__ variable,
  introducing new E0603 message

* #105337: allow custom reporter in output-format (patch by Kevin Jing Qiu)

* #104420: check for protocol completeness and avoid false R0903
  (patch by Peter Hammond)

* #100654: fix grammatical error for W0332 message (using 'l' as
  long int identifier)

* #103656: fix W0231 false positive for missing call to object.__init__
  (patch by lothiraldan@gmail.com)

* #63424: fix similarity report disabling by properly renaming it to RP0801

* #103949: create a console_scripts entry point to be used by
  easy_install, buildout and pip

* fix cross-interpreter issue (non compatible access to __builtins__)

* stop including tests files in distribution, they causes crash when
  installed with python3 (#72022, #82417, #76910)


What's New in Pylint 0.25.2?
============================
Release date: 2012-07-17

* #93591: Correctly emit warnings about clobbered variable names when an
  except handler contains a tuple of names instead of a single name.
  (patch by tmarek@google.com)

* #7394: W0212 (access to protected member) not emitted on assignments
  (patch by lothiraldan@gmail.com)

* #18772; no prototype consistency check for mangled methods (patch by
  lothiraldan@gmail.com)

* #92911: emit W0102 when sets are used as default arguments in functions
  (patch by tmarek@google.com)

* #77982: do not emit E0602 for loop variables of comprehensions
  used as argument values inside a decorator (patch by tmarek@google.com)

* #89092: don't emit E0202 (attribute hiding a method) on @property methods

* #92584: fix pylint-gui crash due to internal API change

* #87192: fix crash when decorators are accessed through more than one dot
  (for instance @a.b is fine, @a.b.c crash)

* #88914: fix parsing of --generated-members options, leading to crash
  when using a regexp value set

* fix potential crashes with utils.safe_infer raising InferenceError


What's New in Pylint 0.25.1?
============================
Release date: 2011-12-08

* #81078: Warn if names in  exception handlers clobber overwrite
  existing names (patch by tmarek@google.com)

* #81113: Fix W0702 messages appearing with the wrong line number.
  (patch by tmarek@google.com)

* #50461, #52020, #51222: Do not issue warnings when using 2.6's
  property.setter/deleter functionality (patch by dneil@google.com)

* #9188, #4024: Do not trigger W0631 if a loop variable is assigned
  in the else branch of a for loop.


What's New in Pylint 0.25.0?
============================
Release date: 2011-10-7

* #74742: make allowed name for first argument of class method configurable
  (patch by Google)

* #74087: handle case where inference of a module return YES; this avoid
  some cases of "TypeError: '_Yes' object does not support indexing" (patch
  by Google)

* #74745: make "too general" exception names configurable (patch by Google)

* #74747: crash occurs when lookup up a special attribute in class scope
  (patch by google)

* #76920: crash if on e.g. "pylint --rcfile" (patch by Torsten Marek)

* #77237: warning for E0202 may be very misleading

* #73941: HTML report messages table is badly rendered


What's New in Pylint 0.24.0?
============================
Release date: 2011-07-18

* #69738: add regular expressions support for "generated-members"

* ids of logging and string_format checkers have been changed:
  logging: 65 -> 12, string_format: 99 -> 13
  Also add documentation to say that ids of range 1-50 shall be reserved
  to pylint internal checkers

* #69993: Additional string format checks for logging module:
  check for missing arguments, too many arguments, or invalid string
  formats in the logging checker module. Contributed by Daniel Arena

* #69220: add column offset to the reports. If you've a custom reporter,
  this change may break it has now location gain a new item giving the
  column offset.

* #60828: Fix false positive in reimport check

* #70495: absolute imports fail depending on module path (patch by Jacek Konieczny)

* #22273: Fix --ignore option documentation to match reality


What's New in Pylint 0.23.0?
============================
Release date: 2011-01-11

* documentation update, add manpages

* several performance improvements

* finalize python3 support

* new W0106 warning 'Expression "%s" is assigned to nothing'

* drop E0501 and E0502 messages about wrong source encoding: not anymore
  interesting since it's a syntax error for python >= 2.5 and we now only
  support this python version and above.

* don't emit W0221 or W0222 when methods as variable arguments (e.g. \*arg
  and/or \*\*args). Patch submitted by Charles Duffy.


What's New in Pylint 0.22.0?
============================
Release date: 2010-11-15

* python versions: minimal python3.x support; drop python < 2.5 support


What's New in Pylint 0.21.4?
============================
Release date: 2010-10-27

* fix #48066: pylint crashes when redirecting output containing non-ascii characters

* fix #19799: "pylint -blah" exit with status 2

* update documentation


What's New in Pylint 0.21.3?
============================
Release date: 2010-09-28

* restored python 2.3 compatibility. Along with logilab-astng
  0.21.3 and logilab-common 0.52, this will much probably be the
  latest release supporting python < 2.5.


What's New in Pylint 0.21.2?
============================
Release date: 2010-08-26

* fix #36193: import checker raise exception on cyclic import

* fix #28796: regression in --generated-members introduced pylint 0.20

* some documentation cleanups


What's New in Pylint 0.21.1?
============================
Release date: 2010-06-04

* fix #28962: pylint crash with new options, due to missing stats data while
  writing the Statistics by types report

* updated man page to 0.21 or greater command line usage (fix debian #582494)


What's New in Pylint 0.21.0?
============================
Release date: 2010-05-11

* command line updated (closes #9774, #9787, #9992, #22962):

* all enable-* / disable-* options have been merged into --enable / --disable

* BACKWARD INCOMPATIBLE CHANGE: short name of --errors-only becomes -E, -e being
  affected to --enable

* pylint --help output much simplified, with --long-help available to get the
  complete one

* revisited gui, thanks to students from Toronto university (they are great
  contributors to this release!)

* fix #21591: html reporter produces no output if reports is set to 'no'

* fix #4581: not Missing docstring (C0111) warning if a method is overridden

* fix #4683: Non-ASCII characters count double if utf8 encode

* fix #9018: when using defining-attr-method, method order matters

* fix #4595: Comma not followed by a space should not occurs on trailing comma
  in list/tuple/dict definition

* fix #22585: [Patch] fix man warnings for pyreverse.1 manpage

* fix #20067: AttributeError: 'NoneType' object has no attribute 'name' with with


What's New in Pylint 0.20.0?
============================
Release date: 2010-03-01

* fix #19498: fix windows batch file

* fix #19339: pylint.el : non existing py-mod-map
  (closes Debian Bug report logs - #475939)

* implement #18860, new W0199 message on assert (a, b)

* implement #9776, 'W0150' break or return statement in finally block may
  swallow exception.

* fix #9263, __init__ and __new__ are checked for unused arguments

* fix #20991, class scope definitions ignored in a genexpr

* fix #5975, Abstract intermediate class not recognized as such

* fix #5977, yield and return statement have their own counters, no more R0911
  (Too many return statements) when a function have many yield stamtements

* implement #5564, function / method arguments with leading "_" are ignored in
  arguments / local variables count.

* implement #9982, E0711 specific error message when raising NotImplemented

* remove --cache-size option


What's New in Pylint 0.19.0?
============================
Release date: 2009-12-18

* implement #18947, #5561: checker for function arguments

* include James Lingard string format checker

* include simple message (ids) listing by Vincent Ferotin (#9791)

* --errors-only does not hide fatal error anymore

* include james Lingard patches for ++/-- and duplicate key in dicts

* include James Lingard patches for function call arguments checker

* improved Flymake code and doc provided by Derek Harland

* refactor and fix the imports checker

* fix #18862: E0601 false positive with lambda functions

* fix #8764: More than one statement on a single line false positive with
  try/except/finally

* fix #9215: false undefined variable error in lambda function

* fix for w0108 false positive (Nathaniel)

* fix test/fulltest.sh

* #5821 added a utility function to run pylint in another process (patch provide by Vincent Ferotin)


What's New in Pylint 0.18.0?
============================
Release date: 2009-03-25

* tests ok with python 2.4, 2.5, 2.6. 2.3 not tested

* fix #8687, W0613 false positive on inner function

* fix #8350, C0322 false positive on multi-line string

* fix #8332: set E0501 line no to the first line where non ascii character
  has been found

* avoid some E0203 / E0602 false negatives by detecting respectively
  AttributeError / NameError

* implements #4037: don't issue W0142 (* or ** magic) when they are barely
  passed from */** arguments

* complete #5573: more complete list of special methods, also skip W0613
  for python internal method

* don't show information messages by default

* integration of Yuen Ho Wong's patches on Emacs lisp files


What's New in Pylint 0.17.0?
============================
Release date: 2009-03-19

* semicolon check : move W0601 to W0301

* remove rpython : remove all rpython checker, modules and tests

* astng 0.18 compatibility: support for _ast module modifies interfaces


What's New in Pylint 0.16.0?
============================
Release date: 2009-01-28

* change [en|dis]able-msg-cat options: only accept message categories
  identified by their first letter (e.g. IRCWEF) without the need for comma
  as separator

* add epylint.bat script to fix Windows installation

* setuptools/easy_install support

* include a modified version of Maarten ter Huurne patch to avoid W0613
  warning on arguments from overridden method

* implement #5575  drop dumb W0704 message) by adding W0704 to ignored
  messages by default

* new W0108 message, checking for suspicious lambda (provided by  Nathaniel
  Manista)

* fix W0631, false positive reported by Paul Hachmann

* fix #6951: false positive with W0104

* fix #6949

* patches by Mads Kiilerich:

* implement #4691, make pylint exits with a non zero return
  status if any messages other then Information are issued

* fix #3711, #5626 (name resolution bug w/ decorator and class members)

* fix #6954


What's New in Pylint 0.15.2?
============================
Release date: 2008-10-13

* fix #5672: W0706 weirdness ( W0706 removed )

* fix #5998: documentation points to wrong url for mailing list

* fix #6022: no error message on wrong module names

* fix #6040: pytest doesn't run test/func_test.py


What's New in Pylint 0.15.1?
============================
Release date: 2008-09-15

* fix #4910: default values are missing in manpage

* fix #5991: missing files in 0.15.0 tarball

* fix #5993: epylint should work with python 2.3


What's New in Pylint 0.15.0?
============================
Release date: 2008-09-10

* include pyreverse package and class diagram generation

* included Stefan Rank's patch to deal with 2.4 relative import

* included Robert Kirkpatrick's tutorial and typos fixes

* fix bug in reenabling message

* fix #2473: invoking pylint on __init__.py (hopefully)

* typecheck: acquired-members option has been dropped in favor of the more
  generic generated-members option. If the zope option is set, the behaviour
  is now to add some default values to generated-members.

* Flymake integration: added bin/epylint and elisp/pylint-flymake.el


What's New in Pylint 0.14.0?
============================
Release date: 2008-01-14

* fix #3733: Messages (dis)appear depending on order of file names

* fix #4026: pylint.el should require compile

* fix a bug in colorized reporter, spotted by Dave Borowitz

* applied patch from Stefan Rank to avoid W0410 false positive when
  multiple "from __future__" import statements

* implement #4012: flag back tick as deprecated (new W0333 message)

* new ignored-class option on typecheck checker allowing to skip members
  checking based on class name (patch provided by Thomas W Barr)


What's New in Pylint 0.13.2?
============================
Release date: 2007-06-07

* fix disable-checker option so that it won't accidentally enable the
  rpython checker which is disabled by default

* added note about the gedit plugin into documentation


What's New in Pylint 0.13.1?
============================
Release date: 2007-03-02

* fix some unexplained 0.13.0 packaging issue which led to a bunch of
  files missing from the distribution


What's New in Pylint 0.13.0?
============================
Release date: 2007-02-28

* new RPython (Restricted Python) checker for PyPy fellow or people
  wanting to get a compiled version of their python program using the
  translator of the PyPy project. For more information about PyPy or
  RPython, visit https://www.pypy.org, previously codespeak.net/pypy/

* new E0104 and E0105 messages introduced to respectively warn about
  "return" and "yield" outside function or method

* new E0106 message when "yield" and "return something" are mixed in a
  function or method

* new W0107 message for unnecessary pass statement

* new W0614 message to differentiate between unused ``import X`` and
  unused `from X import *` (#3209, patch submitted by Daniel Drake)

* included Daniel Drake's patch to have a different message E1003 instead of
  E1001 when a missing member is found but an inference failure has been
  detected

* msvs reporter for Visual Studio line number reporting (#3285)

* allow disable-all option inline (#3218, patch submitted by Daniel Drake)

* --init-hook option to call arbitrary code necessary to set
  environment (e.g. sys.path) (#3156)

* One more Daniel's patch fixing a command line option parsing
  problem, this'll definitely be the DDrake release :)

* fix #3184: crashes on "return" outside function

* fix #3205: W0704 false positive

* fix #3123: W0212 false positive on static method

* fix #2485: W0222 false positive

* fix #3259: when a message is explicitly enabled, check the checker
  emitting it is enabled


What's New in Pylint 0.12.2?
============================
Release date: 2006-11-23

* fix #3143: W0233 bug w/ YES objects

* fix #3119: Off-by-one error counting lines in a file

* fix #3117: ease sys.stdout overriding for reporters

* fix #2508: E0601 false positive with lambda

* fix #3125: E1101 false positive and a message duplication. Only the last part
  is actually fixed since the initial false positive is due to dynamic setting of
  attributes on the decimal.Context class.

* fix #3149: E0101 false positives and introduced E0100 for generator __init__
  methods

* fixed some format checker false positives


What's New in Pylint 0.12.1?
============================
Release date: 2006-09-25

* fixed python >= 2.4 format false positive with multiple lines statement

* fixed some 2.5 issues

* fixed generator expression scope bug (depends on astng 0.16.1)

* stop requiring __revision__


What's New in Pylint 0.12.0?
============================
Release date: 2006-08-10

* usability changes:

    * parseable, html and color options are now handled by a single
      output-format option

    * enable-<checkerid> and disable-all options are now handled by
      two (exclusive) enable-checker and disable-checker options
      taking a comma separated list of checker names as value

    * renamed debug-mode option to errors-only

* started a reference user manual

* new W0212 message for access to protected member from client code
  (Closes #14081)

* new W0105 and W0106 messages extracted from W0104 (statement seems
  to have no effect) respectively when the statement is actually string
  (that's sometimes used instead of comments for documentation) or an
  empty  statement generated by a useless semicolon

* reclassified W0302 to C0302

* fix so that global messages are not anymore connected to the last
  analyzed module (Closes #10106)

* fix some bugs related to local disabling of messages

* fix cr/lf pb when generating the rc file on windows platforms


What's New in Pylint 0.11.0?
============================
Release date: 2006-04-19

* fix crash caused by the exceptions checker in some case

* fix some E1101 false positive with abstract method or classes defining
  __getattr__

* dirty fix to avoid "_socketobject" has not "connect" member. The actual
  problem is that astng isn't able to understand the code used to create
  socket.socket object with exec

* added an option in the similarity checker to ignore docstrings, enabled
  by default

* included patch from Benjamin Niemann to allow block level
  enabling/disabling of messages


What's New in Pylint 0.10.0?
============================
Release date: 2006-03-06

* WARNING, this release include some configuration changes (see below),
  so you may have to check and update your own configuration file(s) if
  you use one

* this release require the 0.15 version of astng or superior (it will save
  you a lot of pylint crashes...)

* W0705 has been reclassified to E0701, and is now detecting more
  inheriting problem, and a false positive when empty except clause is
  following an Exception catch has been fixed (Closes #10422)

* E0212 and E0214 (metaclass/class method should have mcs/cls as first
  argument have been reclassified to C0202 and C0203 since this not as
  well established as "self" for instance method (E0213)

* W0224 has been reclassified into F0220 (failed to resolve interfaces
  implemented by a class)

* a new typecheck checker, introducing the following checks:

    - E1101, access to nonexistent member (implements #10430), remove
      the need of E0201 and so some options has been moved from the
      classes checker to this one
    - E1102, calling a non callable object
    - E1111 and W1111 when an assignment is done on a function call but the
      inferred function returns None (implements #10431)

* change in the base checker:

    - checks module level and instance attribute names (new const-rgx
      and attr-rgx configuration option) (implements #10209  and
      #10440)
    - list comprehension and generator expression variables have their
      own regular expression  (the inlinevar-rgx option) (implements
      #9146)
    - the C0101 check with its min-name-length option has
      been removed (this can be specified in the regxp after all...)
    - W0103 and W0121 are now handled by the variables checker
      (W0103 is now W0603 and W0604 has been split into different messages)
    - W0131 and W0132 messages  have been reclassified to C0111 and
      C0112 respectively
    - new W0104 message on statement without effect

* regexp support for dummy-variables (dummy-variables-rgx option
  replace dummy-variables) (implements #10027)

* better global statement handling, see W0602, W0603, W0604 messages
  (implements #10344 and #10236)

* --debug-mode option, disabling all checkers without error message
  and filtering others to only display error

* fixed some R0201 (method could be a function) false positive


What's New in Pylint 0.9.0?
============================
Release date: 2006-01-10

* a lot of updates to follow astng 0.14 API changes, so install
  logilab-astng  0.14 or greater before using this version of pylint

* checker number 10 ! newstyle will search for problems regarding old
  style / new style classes usage problems (rely on astng 0.14 new
  style detection feature)

* new 'load-plugins' options to load additional pylint plugins (usable
  from the command line or from a configuration file) (implements
  #10031)

* check if a "pylintrc" file exists in the current working directory
  before using the one specified in the PYLINTRC environment variable
  or the default ~/.pylintrc or /etc/pylintrc

* fixed W0706 (Identifier used to raise an exception is assigned...)
  false positive and reraising a caught exception instance

* fixed E0611 (No name get in module blabla) false positive when accessing
  to a class'__dict__

* fixed some E0203 ("access to member before its definition") false
  positive

* fixed E0214 ("metaclass method first argument should be mcs) false
  positive with staticmethod used on a metaclass

* fixed packaging which was missing the test/regrtest_data directory

* W0212 (method could be a function) has been reclassified in the
  REFACTOR category as R0201, and is no more considerer when a method
  overrides an abstract method from an ancestor class

* include module name in W0401 (wildcard import), as suggested by
  Amaury

* when using the '--parseable', path are written relative to the
  current working directory if in a sub-directory of it (#9789)

* 'pylint --version' shows logilab-astng and logilab-common versions

* fixed pylint.el to handle space in file names

* misc lint style fixes


What's New in Pylint 0.8.1?
============================
Release date: 2005-11-07

* fix "deprecated module" false positive when the code imports a
  module whose name starts with a deprecated module's name (close
  #10061)

* fix "module has no name __dict__" false positive (Closes #10039)

* fix "access to undefined variable __path__" false positive (close
  #10065)

* fix "explicit return in __init__" false positive when return is
  actually in an inner function (Closes #10075)


What's New in Pylint 0.8.0?
============================
Release date: 2005-10-21

* check names imported from a module exists in the module (E0611),
  patch contributed by Amaury Forgeot d'Arc

* print a warning (W0212) for methods that could be a function
  (implements #9100)

* new --defining-attr-methods option on classes checker

* new --acquired-members option on the classes checker, used when
  --zope=yes to avoid false positive on acquired attributes (listed
  using this new option) (Closes #8616)

* generate one E0602 for each use of an undefined variable
  (previously, only one for the first use but not for the following)
  (implements #1000)

* make profile option saveable

* fix Windows .bat file,  patch contributed by Amaury Forgeot d'Arc

* fix one more false positive for E0601 (access before definition)
  with for loop such as "for i in range(10): print i" (test
  func_noerror_defined_and_used_on_same_line)

* fix false positive for E0201 (undefined member) when accessing to
  __name__ on a class object

* fix astng checkers traversal order

* fix bug in format checker when parsing a file from a platform
  using different new line characters (Closes #9239)

* fix encoding detection regexp

* fix --rcfile handling (support for --rcfile=file, Closes #9590)


What's New in Pylint 0.7.0?
============================
Release date: 2005-05-27

* WARNING: pylint is no longer a logilab subpackage. Users may have to
  manually remove the old logilab/pylint directory.

* introduce a new --additional-builtins option to handle user defined
  builtins

* --reports option has now -r as short alias, and -i for --include-ids

* fix a bug in the variables checker which may causing some false
  positives when variables are defined and used within the same
  statement (test func_noerror_defined_and_used_on_same_line)

* this time, real fix of the "disable-msg in the config file" problem,
  test added to unittest_lint

* fix bug with --list-messages and python -OO

* fix possible false positive for W0201


What's New in Pylint 0.6.4?
===========================
Release date: 2005-04-14

* allow to parse files without extension when a path is given on the
  command line (test noext)

* don't fail if we are unable to read an inline option  (e.g. inside a
  module), just produce an information message (test func_i0010)

* new message E0103 for break or continue outside loop (Closes #8883,
  test func_continue_not_in_loop)

* fix bug in the variables checker, causing non detection of some
  actual name error (Closes #8884, test
  func_nameerror_on_string_substitution)

* fix bug in the classes checker which was making pylint crash if
  "object" is assigned in a class inheriting from it (test
  func_noerror_object_as_class_attribute)

* fix problem with the similar checker when related options are
  defined in a configuration file

* new --generate-man option to generate pylint's man page (require the
  latest logilab.common (>= 0.9.3)

* packaged (generated...) man page


What's New in Pylint 0.6.3?
===========================
Release date: 2005-02-24

* fix scope problem which may cause false positive and true negative
  on E0602

* fix problem with some options such as disable-msg causing error when
  they are coming from the configuration file


What's New in Pylint 0.6.2?
============================
Release date: 2005-02-16

* fix false positive on E0201 ("access to undefined member") with
  metaclasses

* fix false positive on E0203 ("access to member before its
  definition") when attributes are defined in a parent class

* fix false positive on W0706 ("identifier used to raise an exception
  assigned to...")

* fix interpretation of "\t" as value for the indent-string
  configuration variable

* fix --rcfile so that --rcfile=pylintrc (only --rcfile pylintrc was
  working in earlier release)

* new raw checker example in the examples/ directory


What's New in Pylint 0.6.1?
===========================
Release date: 2005-02-04

* new --rcfile option to specify the configuration file without the
  PYLINTRC environment variable

* added an example module for a custom pylint checker (see the
  example/ directory)

* some fixes to handle fixes in common 0.9.1 (should however still working
  with common 0.9.0, even if upgrade is recommended)


What's New in Pylint 0.6.0?
===========================
Release date: 2005-01-20

* refix pylint Emacs mode

* no more traceback when just typing "pylint"

* fix a bug which may cause crashes on resolving parent classes

* fix problems with the format checker: don't chock on files
  containing multiple CR, avoid C0322, C0323, C0324 false positives
  with triple quoted string with quote inside

* correctly detect access to member defined latter in __init__ method

* now depends on common 0.8.1 to fix problem with interface resolution
  (Closes #8606)

* new --list-msgs option describing available checkers and their
  messages

* added windows specific documentation to the README file, contributed
  by Brian van den Broek

* updated doc/features.txt (actually this file is now generated using
  the --list-msgs option), more entries into the FAQ

* improved tests coverage


What's New in Pylint 0.5.0?
===========================
Release date: 2004-10-19

* avoid importing analyzed modules !

* new Refactor and Convention message categories. Some Warnings have been
  remapped into those new categories

* added "similar", a tool to find copied and pasted lines of code,
  both using a specific command line tool and integrated as a
  pylint's checker

* imports checker may report import dependencies as a dot graph

* new checker regrouping most Refactor detection (with some new metrics)

* more command line options storable in the configuration file

* fix bug with total / undocumented number of methods


What's New in Pylint 0.4.2?
===========================
Release date: 2004-07-08

* fix pylint Emacs mode

* fix classes checkers to handler twisted interfaces


What's New in Pylint 0.4.1?
===========================
Release date: 2004-05-14

* fix the setup.py script to allow bdist_winst (well, the generated
  installer has not been tested...) with the necessary
  logilab/__init__.py file

* fix file naming convention as suggested by Andreas Amoroso

* fix stupid crash bug with bad method names


What's New in Pylint 0.4.0?
===========================
Release date: 2004-05-10

* fix file path with --parsable

* --parsable option has been renamed to --parseable

* added patch from Andreas Amoroso to output message to files instead
  of standard output

* added Run to the list of correct variable names

* fix variable names regexp and checking of local classes names

* some basic handling of metaclasses

* no-docstring-rgx apply now on classes too

* new option to specify a different regexp for methods than for
  functions

* do not display the evaluation report when no statements has been
  analysed

* fixed crash with a class nested in a method

* fixed format checker to deals with triple quoted string and
  lines with code and comment mixed

* use logilab.common.ureports to layout reports


What's New in Pylint 0.3.3?
===========================
Release date: 2004-02-17

* added a parsable text output, used when the --parsable option is
  provided

* added an Emacs mode using this output, available in the distrib's
  elisp directory

* fixed some typos in messages

* change include-ids options to yn, and allow it to be in the
  configuration file

* do not chock on corrupted stats files

* fixed bug in the format checker which may stop pylint execution

* provide scripts for unix and windows to wrap the minimal pylint tk
  gui


What's New in Pylint 0.3.2?
===========================
Release date: 2003-12-23

* html-escape messages in the HTML reporter (bug reported by Juergen
  Hermann)

* added "TODO" to the list of default note tags

* added "rexec" to the list of default deprecated modules

* fixed typos in some messages


What's New in Pylint 0.3.1?
===========================
Release date: 2003-12-05

* bug fix in format and classes checkers

* remove print statement from imports checkers

* provide a simple tk gui, essentially useful for windows users


What's New in Pylint 0.3.0?
===========================
Release date: 2003-11-20

* new exceptions checker, checking for string exception and empty
  except clauses.

* imports checker checks for reimport of modules

* classes checker checks for calls to ancestor's __init__ and abstract
  method not overridden. It doesn't complain anymore for unused import in
  __init__ files, and provides a new option ignore-interface-methods,
  useful when you're using zope Interface implementation in your project

* base checker checks for disallowed builtins call (controlled by the
  bad-functions option) and for use of * and **

* format checker checks for use of <> and "l" as long int marker

* major internal API changes

* use the rewrite of astng, based on compiler.ast

* added unique id for messages, as suggested by Wolfgang Grafen

* added unique id for reports

* can take multiple modules or files as argument

* new options command line options : --disable-msg, --enable-msg,
  --help-msg, --include-ids, --reports, --disable-report, --cache-size

* --version shows the version of the python interpreter

* removed some options which are now replaced by [en|dis]able-msg, or
  disable-report

* read disable-msg and enable-msg options in source files (should be
  in comments on the top of the file, in the form
  "# pylint: disable-msg=W0402"

* new message for modules importing themselves instead of the "cyclic
  import" message

* fix bug with relative and cyclic imports

* fix bug in imports checker (cycle was not always detected)

* still fixes in format checker : don't check comment and docstring,
  check first line after an indent

* allowed/prohibited names now apply to all identifiers, not only
  variables,  so changed the configuration option from
  (good|bad)-variable-names to (good|bad)-names

* added string, rexec and Bastion to the default list of deprecated
  modules

* do not print redefinition warning for function/class/method defined
  in mutually exclusive branches


What's New in Pylint 0.2.1?
===========================
Release date: 2003-10-10

* added some documentation, fixed some typos

* set environment variable PYLINT_IMPORT to 1 during pylint execution.

* check that variables "imported" using the global statement exist

* indentation problems are now warning instead of errors

* fix checkers.initialize to try to load all files with a known python
  extension (patch from wrobell)

* fix a bunch of messages

* fix sample configuration file

* fix the bad-construction option

* fix encoding checker

* fix format checker


What's New in Pylint 0.2.0?
===========================
Release date: 2003-09-12

* new source encoding / FIXME checker (pep 263)

* new --zope option which trigger Zope import. Useful to check Zope
  products code.

* new --comment option which enable the evaluation note comment
  (disabled by default).

* a ton of bug fixes

* easy functional test infrastructure


What's New in Pylint 0.1.2?
===========================
Release date: 2003-06-18

* bug fix release

* remove dependency to pyreverse


What's New in Pylint 0.1.1?
===========================
Release date: 2003-06-01

* much more functionalities !


What's New in Pylint 0.1?
===========================
Release date: 2003-05-19

* initial release
````

## File: doc/whatsnew/0/index.rst
````
0.x
===

.. include:: ../full_changelog_explanation.rst

Ticket numbers are almost always internal to Logilab, some come from bitbucket.

.. toctree::
   :maxdepth: 2

   0.x.rst
````

## File: doc/whatsnew/1/1.6/full.rst
````
Full changelog
==============

What's new in Pylint 1.6.3?
----------------------------
Release date: 2016-07-18

* Do not crash when inferring uninferable exception types for docparams extension

  Closes #998


What's new in Pylint 1.6.2?
----------------------------
Release date: 2016-07-15

* Do not crash when printing the help of options with default regular expressions

  Closes #990

* More granular versions for deprecated modules.

  Closes #991


What's new in Pylint 1.6.1?
----------------------------
Release date: 2016-07-07

* Use environment markers for supporting conditional dependencies.


What's New in Pylint 1.6.0?
---------------------------
Release date: 2016-07-03

* Added a new extension, ``pylint.extensions.mccabe``, for warning
  about complexity in code.

* Deprecate support for --optimize-ast

  Fixes part of #975

* Deprecate support for the HTML output

  Fixes part of #975

* Deprecate support for --output-files

  Fixes part of #975

* Fixed a documentation error for the check_docs extension.

  Closes #735

* Made the list of property-defining decorators configurable.

* Fix a bug where the top name of a qualified import was detected as unused variable.

  Closes #923

* bad-builtin is now an extension check.

* generated-members support qualified name through regular expressions.

  For instance, one can specify a regular expression as --generated-members=astroid.node_classes.*
  for ignoring every no-member error that is accessed as in ``astroid.node_classes.missing.object``.

* Add the ability to ignore files based on regex matching, with the new ``--ignore-patterns``
  option. Allow for multiple ignore patterns to be specified. Rather than clobber the existing
  ignore option, we introduced a new one called ignore-patterns.

  Closes #156

* Added a new error, 'trailing-newlines', which is emitted when a file
  has trailing new lines.

  Closes #682

* Add a new option, 'redefining-builtins-modules', for controlling the modules
  which can redefine builtins, such as six.moves and future.builtins.

  Closes #464

* 'reimported' is emitted when the same name is imported from different module.

  Closes #162

* Add a new recommendation checker, 'consider-iterating-dictionary', which is emitted
  which is emitted when a dictionary is iterated through .keys().

  Closes #699

* Use the configparser backport for Python 2

  This fixes a problem we were having with comments inside values, which is fixed
  in Python 3's configparser.

  Closes #828

* A new error was added, 'invalid-length-returned', when the ``__len__``
  special method returned something else than a non-negative number.

  Closes #557

* Switch to using isort internally for wrong-import-order.

  Closes #879

* check_docs extension can find constructor parameters in __init__.

  Closes #887

* Don't warn about invalid-sequence-index if the indexed object has unknown base
  classes.

  Closes #867

* Don't crash when checking, for super-init-not-called, a method defined in an if block.

* Do not emit import-error or no-name-in-module for fallback import blocks by default.

  Until now, we warned with these errors when a fallback import block (a TryExcept block
  that contained imports for Python 2 and 3) was found, but this gets cumbersome when
  trying to write compatible code. As such, we don't check these blocks by default,
  but the analysis can be enforced by using the new ``--analyse-fallback-block`` flag.

  Closes #769.
````

## File: doc/whatsnew/1/1.6/index.rst
````
**************************
  What's New In Pylint 1.6
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

Ticket numbers can be internal to logilab or come from bitbucket.

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/1/1.6/summary.rst
````
:Release: 1.6.0
:Date: 2016-07-07

Summary -- Release highlights
=============================

Nothing major.


New checkers
============

* We added a new recommendation check, ``consider-iterating-dictionary``,
  which is emitted when a dictionary is iterated by using ``.keys()``.

  For instance, the following code would trigger this warning, since
  the dictionary's keys can be iterated without calling the method explicitly.

  .. code-block:: python

      for key in dictionary.keys():
          ...

      # Can be refactored to:
      for key in dictionary:
          ...

* ``trailing-newlines`` check was added, which is emitted when a file has trailing newlines.


* ``invalid-length-returned`` check was added, which is emitted when the ``__len__``
  special method returns something else than a non-negative number. For instance, this
  example is triggering it::

      class Container(object):
          def __len__(self):
              return self._items # Oups, forgot to call len() over it.



* Add a new check to the *check_docs* extension for looking for duplicate
  constructor parameters in a class constructor docstring or in a class docstring.

  The check ``multiple-constructor-doc`` is emitted when the parameter is documented
  in both places.


* We added a new extension plugin, ``pylint.extensions.mccabe``, which can be used
  for warning about the complexity in the code.

  You can enable it as in::

      $ pylint module_or_project --load-plugins=pylint.extensions.mccabe

  See more at :ref:`pylint.extensions.mccabe`


New features
============

* ``generated-members`` now supports qualified names through regular expressions.

  For instance, for ignoring all the errors generated by ``numpy.core``'s attributes, we can
  now use::

      $ pylint a.py --generated-members=numpy.*


* Add the ability to ignore files based on regex matching, with the new ``--ignore-patterns`` option.

  Rather than clobber the existing ``ignore`` option, we decided to have a separate
  option for it. For instance, for ignoring all the test files, we can now use::

      $ pylint myproject --ignore-patterns=test.*?py


* We added a new option, ``redefining-builtins-modules``, which is used for
  defining the modules which can redefine builtins.
  *pylint* will emit an error when a builtin is redefined, such as defining
  a variable called ``next``. But in some cases, the builtins can be
  redefined in the case they are imported from other places, different
  than the ``builtins`` module, such is the case for ``six.moves``, which
  contains more forward-looking functions::

      $ cat a.py
      # Oups, now pylint emits a redefined-builtin message.
      from six.moves import open
      $ pylint a.py --redefining-builtins-modules=six.moves

  Default values: ``six.moves,future.builtins``



Bug fixes
=========

* Fixed a bug where the top name of a qualified import was detected as an unused variable.

* We don't warn about ``invalid-sequence-index`` if the indexed object has unknown
  base classes, that Pylint cannot deduce.



Other Changes
=============


* The ``bad-builtin`` check was moved into an extension.

  The check was complaining about used builtin functions which
  were supposed to not be used. For instance, ``map`` and ``filter``
  were falling into this category, since better alternatives can
  be used, such as list comprehensions. But the check was annoying,
  since using ``map`` or ``filter`` can have its use cases and as
  such, we decided to move it to an extension check instead.
  It can now be enabled through ``--load-plugins=pylint.extensions.bad_builtin``.

* We use the ``configparser`` backport internally, for Python 2.

  This allows having comments inside list values, in the configuration,
  such as::

      disable=no-member,
              # Don't like this check
              bad-indentation

* We now use the isort_ package internally.

  This improves the ```wrong-import-order`` check, so now
  we should have less false positives regarding the import order.


* We do not emit ``import-error`` or ``no-name-in-module`` for fallback import blocks by default.

  A fallback import block can be considered a TryExcept block, which contains imports in both
  branches, such as::

      try:
          import urllib.request as request
      except ImportError:
          import urllib2 as request

  In the case where **pylint** can not find one import from the ``except`` branch, then
  it will emit an ``import-error``, but this gets cumbersome when trying to write
  compatible code for both Python versions. As such, we don't check these blocks by default,
  but the analysis can be enforced by using the new ``--analyse-fallback-block`` flag.

* ``reimported`` is emitted when the same name is imported from different module, as in::

      from collections import deque, OrderedDict, deque


Deprecated features
===================

* The HTML support was deprecated and will be eventually removed
  in Pylint 1.7.0.

  This feature was lately a second class citizen in Pylint, being
  often neglected and having a couple of bugs. Since we now have
  the JSON reporter, this can be used as a basis for more prettier
  HTML outputs than what Pylint can currently offer.

* The ``--files-output`` option was deprecated and will be eventually
  removed in Pylint 1.7.0.

* The ``--optimize-ast`` option was deprecated and will be eventually
  removed in Pylint 1.7.0.

  The option was initially added for handling pathological cases,
  such as joining too many strings using the addition operator, which
  was leading pylint to have a recursion error when trying to figure
  out what the string was. Unfortunately, we decided to ignore the
  issue, since the pathological case would have happen when the
  code was parsed by Python as well, without actually reaching the
  runtime step and as such, we will remove the option in the future.

* The ``check_docs`` extension is now deprecated. The extension is still available
  under the ``docparams`` name, so this should work::

      $ pylint module_or_package --load-extensions=pylint.extensions.docparams

  The old name is still kept for backward compatibility, but it will be
  eventually removed.


Removed features
================

* None yet

.. _isort: https://pypi.org/project/isort/
````

## File: doc/whatsnew/1/1.7/full.rst
````
Full changelog
==============

What's New in Pylint 1.7.1?
---------------------------
Release date: 2017-04-17

* Fix a false positive which occurred when an exception was reraised

  Closes #1419

* Fix a false positive of ``disallow-trailing-tuple``

  The check was improved by verifying for non-terminating newlines, which
  should exempt function calls and function definitions from the check

  Closes #1424


What's New in Pylint 1.7?
-------------------------

Release date: 2017-04-13

* Don't emit missing-final-newline or trailing-whitespace for formfeeds (page breaks).

  Closes #1218 and #1219

* Don't emit by default no-member if we have opaque inference objects in the inference results

  This is controlled through the new flag ignore-on-opaque-inference, which is by
  default True. The inference can return  multiple potential results while
  evaluating a Python object, but some branches might not be evaluated, which
  results in partial inference. In that case, it might be useful to still emit
  no-member and other checks for the rest of the inferred objects.

* Added new message ``assign-to-new-keyword`` to warn about assigning to names which
  will become a keyword in future Python releases.

  Closes #1351

* Split the 'missing or differing' in parameter documentation in different error.
  'differing-param-doc' covers the differing part of the old 'missing-param-doc',
  and 'differing-type-doc' covers the differing part of the old 'missing-type-doc'

  Closes #1342

* Added a new error, 'used-prior-global-declaration', which is emitted when a name
  is used prior a global declaration in a function. This causes a SyntaxError in
  Python 3.6

  Closes #1257

* The protocol checks are emitting their messages when a special method is set to None.

  Closes #1263

* Properly detect if imported name is assigned to same name in different
  scope.

  Closes #636, #848, #851, and #900

* Require one space for annotations with type hints, as per PEP 8.

* 'trailing-comma-tuple' check was added

  This message is emitted when pylint finds an one-element tuple,
  created by a stray comma. This can suggest a potential problem in the
  code and it is recommended to use parentheses in order to emphasise the
  creation of a tuple, rather than relying on the comma itself.

* Don't emit not-callable for instances with unknown bases.

  Closes #1213

* Treat keyword only arguments the same as positional arguments with regard to unused-argument check

* Don't try to access variables defined in a separate scope when checking for ``protected-access``

* Added new check to detect incorrect usage of len(SEQUENCE) inside
  test conditions.

* Added new extension to detect comparisons against empty string constants

* Added new extension to detect comparisons of integers against zero

* Added new error conditions for 'bad-super-call'

  Now detects ``super(type(self), self)`` and ``super(self.__class__, self)``
  which can lead to recursion loop in derived classes.

* PyLinter.should_analyze_file has a new optional parameter, called ``is_argument``

  Closes #1079

* Add attribute hints for missing members

  Closes #1035

* Add a new warning, 'redefined-argument-from-local'

  Closes #649

* Support inline comments for comma separated values in the config file

  Closes #1024

* epylint.py_run's *script* parameter was removed.

* epylint.py_run now uses ``shell=False`` for running the underlying process.

  Closes #441

* Added a new warning, 'useless-super-delegation'

  Close 839.

* Added a new error, 'invalid-metaclass', raised when
  we can detect that a class is using an improper metaclass.

  Closes #579

* Added a new refactoring message, 'literal-comparison'.

  Closes #786

* arguments-differ takes in consideration kwonlyargs and variadics

  Closes #983

* Removed --optimized-ast

  Fixes part of #975

* Removed --files-output option

  Fixes part of #975

* Removed pylint-gui from the package.

* Removed the HTML reporter

  Fixes part of #975

* ignored-argument-names is now used for ignoring arguments for unused-variable check.

  This option was used for ignoring arguments when computing the correct number of arguments
  a function should have, but for handling the arguments with regard
  to unused-variable check, dummy-variables-rgx was used instead. Now, ignored-argument-names
  is used for its original purpose and also for ignoring the matched arguments for
  the unused-variable check. This offers a better control of what should be ignored
  and how.
  Also, the same option was moved from the design checker to the variables checker,
  which means that the option now appears under the ``[VARIABLES]`` section inside
  the configuration file.

  Closes #862.

* Fix a false positive for keyword variadics with regard to keyword only arguments.

  If a keyword only argument was necessary for a function, but that function was called
  with keyword variadics (\**kwargs), then we were emitting a missing-kwoa false positive,
  which is now fixed.

  Closes #934.

* Fix some false positives with unknown sized variadics.

  Closes #878

* Added a new extension, check_docstring, for checking PEP 257 conventions.

  Closes #868.

* config files with BOM markers can now be read.

  Closes #864.

* epylint.py_run does not crash on big files, using .communicate() instead of .wait()

  Closes #599

* Disable reports by default and show the evaluation score by default

  The reports were disabled by default in order to simplify the interaction
  between the tool and the users. The score is still shown by default, as
  a way of closely measuring when it increases or decreases due to changes
  brought to the code.

  Refs #746

* Disable the information category messages by default. This is a step towards
  making pylint more sane.

  Refs #746.

* Catch more cases as not proper iterables for __slots__ with
  regard to invalid-slots pattern.

  Closes #775

* empty indent strings are rejected.

* Added a new error, 'relative-beyond-top-level', which is emitted
  when a relative import was attempted beyond the top level package.

  Closes #588

* Added a new warning, 'unsupported-assignment-operation', which is
  emitted when item assignment is tried on an object which doesn't
  have this ability.

  Closes #591

* Added a new warning, 'unsupported-delete-operation', which is
  emitted when item deletion is tried on an object which doesn't
  have this ability.

  Closes #592

* Fix a false positive of 'redundant-returns-doc', occurred when the documented
  function was using *yield* instead of *return*.

  Closes #984.

* Fix false positives of 'missing-[raises|params|type]-doc' due to not
  recognizing keyword synonyms supported by Sphinx.

* Added a new refactoring message, 'consider-merging-isinstance', which is
  emitted whenever we can detect that consecutive isinstance calls can be
  merged together.

  Closes #968

* Fix a false positive of 'missing-param-doc' and 'missing-type-doc',
  occurred when a class docstring uses the 'For the parameters, see'
  magic string but the class __init__ docstring does not, or vice versa.

* ``redefined-outer-name`` is now also emitted when a nested loop's target
  variable is the same as a target variable in an outer loop.

  Closes #911.

* Added proper exception type inference for 'missing-raises-doc'.

* Added InvalidMessageError exception class to replace asserts in
  pylint.utils.

* More thorough validation in MessagesStore.register_messages() to avoid
  one message accidentally overwriting another.

* InvalidMessageError, UnknownMessage, and EmptyReport exceptions are
  moved to the new pylint.exceptions submodule.

* UnknownMessage and EmptyReport are renamed to UnknownMessageError and
  EmptyReportError.

* Warnings 'missing-returns-type-doc' and 'missing-yields-type-doc'
  have each been split into two warnings - 'missing-[return|yield]-doc'
  and 'missing-[return|yield]-type-doc'.

* Added epytext support to docparams extension.

  Closes #1029

* Support having plugins with the same name and with options defined

  Closes #1018

* Sort configuration options in a section

  Closes #1087

* Added a new Python 3 warning around implementing '__div__', '__idiv__', or
  '__rdiv__' as those methods are phased out in Python 3.

* Added a new warning, 'overlapping-except', which is
  emitted when two exceptions in the same except-clause are aliases
  for each other or one exceptions is an ancestor of another.

* Avoid crashing on ill-formatted strings when checking for string formatting errors.

* Added a new Python 3 warning for calling 'str.encode' or 'str.decode' with a non-text
  encoding.

* Added new coding convention message, 'single-string-used-for-slots'.

  Closes #1166

* Added a new Python 3 check for accessing 'sys.maxint' which was removed in Python 3 in favor
  of 'sys.maxsize'

* Added a new Python 3 check for bad imports.

* Added a new Python 3 check for accessing deprecated string functions.

* Do not warn about unused arguments or function being redefined in singledispatch
  registered implementations.

  Closes #1032 and #1034

* Added refactoring message 'no-else-return'.

* Improve unused-variable checker to warn about unused variables in module scope.

  Closes #919

* Ignore modules import as _ when checking for unused imports.

  Closes #1190

* Improve handing of Python 3 classes with metaclasses declared in nested scopes.

  Closes #1177

* Added refactoring message 'consider-using-ternary'.

  Closes #1204

* Bug-fix for false-positive logging-format-interpolation` when format specifications
  are used in formatted string.

  Closes #572

* Added a new switch ``single-line-class-stmt`` to allow single-line declaration
  of empty class bodies.

  Closes #738

* Protected access in form ``type(self)._attribute`` are now allowed.

  Closes #1031

* Let the user modify msg-template when Pylint is called from a Python script

  Closes #1269

* Imports checker supports new switch ``allow-wildcard-with-all`` which disables
  warning on wildcard import when imported module defines ``__all__`` variable.

  Closes #831

* ``too-many-format-args`` and ``too-few-format-args`` are emitted correctly when
  starred expression are used in RHS tuple.

  Closes #957

* ``cyclic-import`` checker supports local disable clauses. When one
  of cycle imports was done in scope where disable clause was active,
  cycle is not reported as violation.

  Closes #59
````

## File: doc/whatsnew/1/1.7/index.rst
````
**************************
  What's New In Pylint 1.7
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/1/1.7/summary.rst
````
:Release: 1.7
:Date: 2017-04-13

Summary -- Release highlights
=============================

New checkers
============

* ``single-string-used-for-slots`` check was added, which is used
  whenever a class is using a single string as a slot value. While this
  is technically not a problem per se, it might trip users when manipulating
  the slots value as an iterable, which would in turn iterate over characters
  of the slot value. In order to be more straight-forward, always try to use
  a container such as a list or a tuple for defining slot values.

* We added a new check, ``literal-comparison``, which is used
  whenever **pylint** can detect a comparison to a literal. This is usually
  not what we want and, potentially, error prone. For instance, in the given example,
  the first string comparison returns true, since smaller strings are interned
  by the interpreter, while for larger ones, it will return False:

  .. rstcheck: ignore-next-code-block
  .. code-block:: python

       mystring = "ok"
       if mystring is "ok": # Returns true
          ...

       mystring = "a" * 1000
       if mystring is ("a" * 1000): # This will return False
          ...

  Instead of using the ``is`` operator, you should use the ``==`` operator for
  this use case.


* We added a new refactoring message, ``consider-merging-isinstance``, which is
  emitted whenever we can detect that consecutive *isinstance* calls can be merged
  together.
  For instance, in this example, we can merge the first two *isinstance* calls:

  .. code-block:: python

      # $ cat a.py
      if isinstance(x, int) or isinstance(x, float):
          pass
      if isinstance(x, (int, float)) or isinstance(x, str):
          pass
      # $ pylint a.py
      # R:  1, 0: Consider merging these isinstance calls to isinstance(x, (float, int)) (consider-merging-isinstance)
      # R:  3, 0: Consider merging these isinstance calls to isinstance(x, (int, float, str)) (consider-merging-isinstance)

* A new error check was added, ``invalid-metaclass``, which is used whenever *pylint*
  can detect that a given class is using a metaclass which is invalid for the purpose
  of the class. This usually might indicate a problem in the code, rather than
  something done on purpose.

  .. code-block:: python

       # Needs to inherit from *type* in order to be valid
       class SomeClass(object):
           ...

       class MyClass(metaclass=SomeClass):
           pass

* A new warning was added, ``useless-super-delegation``, which is used whenever
  we can detect that an overridden method is useless, relying on *super()* delegation
  to do the same thing as another method from the MRO.

  For instance, in this example, the first two methods are useless, since they
  do the exact same thing as the methods from the base classes, while the next
  two methods are not, since they do some extra operations with the passed
  arguments.

  .. code-block:: python

      class Impl(Base):

          def __init__(self, param1, param2):
              super(Impl, self).__init__(param1, param2)

          def useless(self, first, second):
              return super(Impl, self).useless(first, second)

          def not_useless(self, first, **kwargs):
              debug = kwargs.pop('debug', False)
              if debug:
                  ...
              return super(Impl, self).not_useless(first, **kwargs)

          def not_useless_1(self, first, *args):
              return super(Impl, self).not_useless_1(first + some_value, *args)

* A new warning was added, ``len-as-condition``, which is used whenever
  we detect that a condition uses ``len(SEQUENCE)`` incorrectly. Instead
  one could use ``if SEQUENCE`` or ``if not SEQUENCE``.

  For instance, all of the examples below:

  .. code-block:: python

      if len(S):
        pass

      if not len(S):
        pass

      if len(S) > 0:
        pass

      if len(S) != 0:
        pass

      if len(S) == 0:
        pass

  can be written in a more natural way:

  .. code-block:: python

      if S:
        pass

      if not S:
        pass

  See https://peps.python.org/pep-0008/#programming-recommendations
  for more information.

* A new extension was added, ``emptystring.py`` which detects whenever
  we detect comparisons to empty string constants. This extension is disabled
  by default. For instance, the examples below:

  .. code-block:: python

      if S != "":
        pass

      if S == '':
        pass

  can be written in a more natural way:

  .. code-block:: python

      if S:
        pass

      if not S:
        pass

  An exception to this is when empty string is an allowed value whose meaning
  is treated differently than ``None``. For example the meaning could be
  user selected no additional options vs. user has not made their selection yet!

  You can activate this checker by adding the line::

      load-plugins=pylint.extensions.emptystring

  to the ``MAIN`` section of your ``.pylintrc`` or using the command::

      $ pylint a.py --load-plugins=pylint.extensions.emptystring

* A new extension was added, ``comparetozero.py`` which detects whenever
  we compare integers to zero. This extension is disabled by default.
  For instance, the examples below:

  .. code-block:: python

      if X != 0:
        pass

      if X == 0:
        pass

  can be written in a more natural way:

  .. code-block:: python

      if X:
        pass

      if not X:
        pass

  An exception to this is when zero is an allowed value whose meaning
  is treated differently than ``None``. For example the meaning could be
  ``None`` means no limit, while ``0`` means the limit it zero!

  You can activate this checker by adding the line::

      load-plugins=pylint.extensions.comparetozero

  to the ``MAIN`` section of your ``.pylintrc`` or using the command::

      $ pylint a.py --load-plugins=pylint.extensions.comparetozero

* We've added new error conditions for ``bad-super-call`` which now detect
  the usage of ``super(type(self), self)`` and ``super(self.__class__, self)``
  patterns. These can lead to recursion loop in derived classes. The problem
  is visible only if you override a class that uses these incorrect invocations
  of ``super()``.

  For instance, ``Derived.__init__()`` will correctly call ``Base.__init__``.
  At this point ``type(self)`` will be equal to ``Derived`` and the call again
  goes to ``Base.__init__`` and we enter a recursion loop.

  .. code-block:: python

      class Base(object):
          def __init__(self, param1, param2):
              super(type(self), self).__init__(param1, param2)

      class Derived(Base):
          def __init__(self, param1, param2):
              super(Derived, self).__init__(param1, param2)

* The warnings ``missing-returns-doc`` and ``missing-yields-doc`` have each
  been replaced with two new warnings - ``missing-[return|yield]-doc`` and
  ``missing-[return|yield]-type-doc``. Having these as separate warnings
  allows the user to choose whether their documentation style requires
  text descriptions of function return/yield, specification of return/yield
  types, or both.

  .. code-block:: python

      # This will raise missing-return-type-doc but not missing-return-doc
      def my_sphinx_style_func(self):
          """This is a Sphinx-style docstring.

          :returns: Always False
          """
          return False

      # This will raise missing-return-doc but not missing-return-type-doc
      def my_google_style_func(self):
          """This is a Google-style docstring.

          Returns:
              bool:
          """
          return False

* A new refactoring check was added, ``redefined-argument-from-local``, which is
  emitted when **pylint** can detect than a function argument is redefined locally
  in some potential error prone cases. For instance, in the following piece of code,
  we have a bug, since the check will never return ``True``, given the fact that we
  are comparing the same object to its attributes.

  .. code-block:: python

      def test(resource):
          for resource in resources:
              # The ``for`` is reusing ``resource``, which means that the following
              # ``resource`` is not what we wanted to check against.
              if resource.resource_type == resource:
                 call_resource(resource)

  Other places where this check looks are *with* statement name bindings and
  except handler's name binding.

* A new refactoring check was added, ``no-else-return``, which is
  emitted when pylint encounters an else following a chain of ifs,
  all of them containing a return statement.

  .. code-block:: python

    def foo1(x, y, z):
        if x:
            return y
        else:  # This is unnecessary here.
            return z


  We could fix it deleting the ``else`` statement.

  .. code-block:: python

    def foo1(x, y, z):
        if x:
            return y
        return z

* A new Python 3 check was added, ``eq-without-hash``, which enforces classes that implement
  ``__eq__`` *also* implement ``__hash__``.  The behavior around classes which implement ``__eq__``
  but not ``__hash__`` changed in Python 3; in Python 2 such classes would get ``object.__hash__``
  as their default implementation.  In Python 3, aforementioned classes get ``None`` as their
  implementation thus making them unhashable.

  .. code-block:: python

      class JustEq(object):
         def __init__(self, x):
           self.x = x

         def __eq__(self, other):
           return self.x == other.x

      class Neither(object):
        def __init__(self, x):
          self.x = x

      class HashAndEq(object):
         def __init__(self, x):
           self.x = x

         def __eq__(self, other):
           return self.x == other.x

         def __hash__(self):
           return hash(self.x)

      {Neither(1), Neither(2)}  # OK in Python 2 and Python 3
      {HashAndEq(1), HashAndEq(2)}  # OK in Python 2 and Python 3
      {JustEq(1), JustEq(2)}  # Works in Python 2, throws in Python 3


  In general, this is a poor practice which motivated the behavior change.

  .. code-block:: python

      as_set = {JustEq(1), JustEq(2)}
      print(JustEq(1) in as_set)  # prints False
      print(JustEq(1) in list(as_set))  # prints True


  In order to fix this error and avoid behavior differences between Python 2 and Python 3, classes
  should either explicitly set ``__hash__`` to ``None`` or implement a hashing function.

  .. code-block:: python

      class JustEq(object):
         def __init__(self, x):
           self.x = x

         def __eq__(self, other):
           return self.x == other.x

         __hash__ = None

      {JustEq(1), JustEq(2)}  # Now throws an exception in both Python 2 and Python 3.

* 3 new Python 3 checkers were added, ``div-method``, ``idiv-method`` and ``rdiv-method``.
  The magic methods ``__div__`` and ``__idiv__`` have been phased out in Python 3 in favor
  of ``__truediv__``.  Classes implementing ``__div__`` that still need to be used from Python
  2 code not using ``from __future__ import division`` should implement ``__truediv__`` and
  alias ``__div__`` to that implementation.

  .. code-block:: python

      from __future__ import division

      class DivisibleThing(object):
         def __init__(self, x):
           self.x = x

         def __truediv__(self, other):
           return DivisibleThing(self.x / other.x)

         __div__ = __truediv__

* A new Python 3 checker was added to warn about accessing the ``message`` attribute on
  Exceptions.  The message attribute was deprecated in Python 2.7 and was removed in Python 3.
  See https://peps.python.org/pep-0352/#retracted-ideas for more information.

  .. code-block:: python

      try:
        raise Exception("Oh No!!")
      except Exception as e:
        print(e.message)

  Instead of relying on the ``message`` attribute, you should explicitly cast the exception to a
  string:

  .. code-block:: python

      try:
        raise Exception("Oh No!!")
      except Exception as e:
        print(str(e))


* A new Python 3 checker was added to warn about using ``encode`` or ``decode`` on strings
  with non-text codecs.  This check also checks calls to ``open`` with the keyword argument
  ``encoding``.  See https://docs.python.org/3/whatsnew/3.4.html#improvements-to-codec-handling
  for more information.

  .. code-block:: python

      'hello world'.encode('hex')

  Instead of using the ``encode`` method for non-text codecs use the ``codecs`` module.

  .. code-block:: python

      import codecs
      codecs.encode('hello world', 'hex')


* A new warning was added, ``overlapping-except``, which is emitted
  when an except handler treats two exceptions which are *overlapping*.
  This means that one exception is an ancestor of the other one or it is
  just an alias.

  For example, in Python 3.3+, IOError is an alias for OSError. In addition, socket.error is
  an alias for OSError. The intention is to find cases like the following:

  .. code-block:: python

      import socket
      try:
          pass
      except (ConnectionError, IOError, OSError, socket.error):
          pass

* A new Python 3 checker was added to warn about accessing ``sys.maxint``.  This attribute was
  removed in Python 3 in favor of ``sys.maxsize``.

  .. code-block:: python

      import sys
      print(sys.maxint)

  Instead of using ``sys.maxint``, use ``sys.maxsize``

  .. code-block:: python

      import sys
      print(sys.maxsize)

* A new Python 3 checker was added to warn about importing modules that have either moved or been
  removed from the standard library.

  One of the major undertakings with Python 3 was a reorganization of the standard library to
  remove old or supplanted modules and reorganize some of the existing modules.  As a result,
  roughly 100 modules that exist in Python 2 no longer exist in Python 3.  See
  https://peps.python.org/pep-3108/ and https://peps.python.org/pep-0004/ for more
  information.  There were suggestions on how to handle this, at
  pythonhosted.org/six/#module-six.moves (dead link) or python3porting.com/stdlib.html (dead link).

  .. code-block:: python

      from cStringIO import StringIO

  Instead of directly importing the deprecated module, either use ``six.moves`` or a conditional
  import.

  .. code-block:: python

      from six.moves import cStringIO as StringIO

      if sys.version_info[0] >= 3:
          from io import StringIO
      else:
          from cStringIO import StringIO

  This checker will assume any imports that happen within a conditional or a ``try/except`` block
  are valid.

* A new Python 3 checker was added to warn about accessing deprecated functions on the string
  module.  Python 3 removed functions that were duplicated from the builtin ``str`` class.  See
  https://docs.python.org/2/library/string.html#deprecated-string-functions for more information.

  .. code-block:: python

      import string
      print(string.upper('hello world!'))

  Instead of using ``string.upper``, call the ``upper`` method directly on the string object.

  .. code-block:: python

      "hello world!".upper()


* A new Python 3 checker was added to warn about calling ``str.translate`` with the removed
  ``deletechars`` parameter.  ``str.translate`` is frequently used as a way to remove characters
  from a string.

  .. code-block:: python

      'hello world'.translate(None, 'low')

  Unfortunately, there is not an idiomatic way of writing this call in a 2and3 compatible way.  If
  this code is not in the critical path for your application and the use of ``translate`` was a
  premature optimization, consider using ``re.sub`` instead:

  .. code-block:: python

      import re
      chars_to_remove = re.compile('[low]')
      chars_to_remove.sub('', 'hello world')

  If this code is in your critical path and must be as fast as possible, consider declaring a
  helper method that varies based upon Python version.

  .. code-block:: python

      if six.PY3:
          def _remove_characters(text, deletechars):
              return text.translate({ord(x): None for x in deletechars})
      else:
          def _remove_characters(text, deletechars):
              return text.translate(None, deletechars)

* A new refactoring check was added, ``consider-using-ternary``, which is
  emitted when pylint encounters constructs which were used to emulate
  ternary statement before it was introduced in Python 2.5.

  .. code-block:: python

    value = condition and truth_value or false_value


  Warning can be fixed by using standard ternary construct:

  .. code-block:: python

    value = truth_value if condition else false_value


* A new refactoring check was added, ``trailing-comma-tuple``, which is emitted
  when pylint finds an one-element tuple, created by a stray comma. This can
  suggest a potential problem in the code and it is recommended to use parentheses
  in order to emphasise the creation of a tuple, rather than relying on the comma
  itself.

  The warning is emitted for such a construct:

  .. code-block:: python

     a = 1,

  The warning can be fixed by adding parentheses:

  .. code-block:: python

     a = (1, )


* Two new check were added for detecting an unsupported operation
  over an instance, ``unsupported-assignment-operation`` and ``unsupported-delete-operation``.
  The first one is emitted whenever an object does not support item assignment, while
  the second is emitted when an object does not support item deletion:

  .. code-block:: python

      class A:
          pass
      instance = A()
      instance[4] = 4 # unsupported-assignment-operation
      del instance[4] # unsupported-delete-operation

* A new check was added, ``relative-beyond-top-level``, which is emitted
  when a relative import tries to access too many levels in the current package.

* A new check was added, ``trailing-newlines``, which is emitted when a file
  has trailing new lines.

* ``invalid-length-returned`` check was added, which is emitted when a ``__len__``
  implementation does not return a non-negative integer.

* There is a new extension, ``pylint.extensions.mccabe``, which can be used for
  computing the McCabe complexity of classes and functions.

  You can enable this extension through ``--load-plugins=pylint.extensions.mccabe``

* A new check was added, ``used-prior-global-declaration``. This is emitted when
  a name is used prior a global declaration, resulting in a SyntaxError in Python 3.6.

* A new message was added, ``assign-to-new-keyword``. This is emitted when used name
  is known to become a keyword in future Python release. Assignments to keywords
  would result in ``SyntaxError`` after switching to newer interpreter version.

  .. rstcheck: ignore-next-code-block
  .. code-block:: python

      # While it's correct in Python 2.x, it raises a SyntaxError in Python 3.x
      True = 1
      False = 0

      # Same as above, but it'll be a SyntaxError starting from Python 3.7
      async = "async"
      await = "await"


Other Changes
=============

* We don't emit by default ``no-member`` if we have opaque inference objects in the inference results

  This is controlled through the new flag ``--ignore-on-opaque-inference``, which is by
  default True. The inference can return  multiple potential results while
  evaluating a Python object, but some branches might not be evaluated, which
  results in partial inference. In that case, it might be useful to still emit
  no-member and other checks for the rest of the inferred objects.

* Namespace packages are now supported by pylint. This includes both explicit namespace
  packages and implicit namespace packages, supported in Python 3 through PEP 420.

* A new option was added, ``--analyse-fallback-block``.

  This can be used to support both Python 2 and 3 compatible import block code,
  which means that the import block might have code that exists only in one or another
  interpreter, leading to false positives when analysed. By default, this is false, you
  can enable the analysis for both branches using this flag.

* ``ignored-argument-names`` option is now used for ignoring arguments
  for unused-variable check.

  This option was used for ignoring arguments when computing the correct number of arguments
  a function should have, but for handling the arguments with regard
  to unused-variable check, dummy-variables-rgx was used instead. Now, ignored-argument-names
  is used for its original purpose and also for ignoring the matched arguments for
  the unused-variable check. This offers a better control of what should be ignored
  and how.
  Also, the same option was moved from the design checker to the variables checker,
  which means that the option now appears under the ``[VARIABLES]`` section inside
  the configuration file.

* A new option was added, ``redefining-builtins-modules``, for controlling the modules
  which can redefine builtins, such as six.moves and future.builtins.

* A new option was added, ``ignore-patterns``, which is used for building a
  ignore list of directories and files matching the regex patterns, similar to the
  ``ignore`` option.


* The reports are now disabled by default, as well as the information category
  warnings.

* ``arguments-differ`` check was rewritten to take in consideration
  keyword only parameters and variadics.

  Now it also complains about losing or adding capabilities to a method,
  by introducing positional or keyword variadics. For instance, *pylint*
  now complains about these cases:

  .. code-block:: python

       class Parent(object):

           def foo(self, first, second):
               ...

           def bar(self, **kwargs):
               ...

           def baz(self, *, first):
               ...

       class Child(Parent):

           # Why subclassing in the first place?
           def foo(self, *args, **kwargs):
               # mutate args or kwargs.
               super(Child, self).foo(*args, **kwargs)

           def bar(self, first=None, second=None, **kwargs):
               ...
               # The overridden method adds two new parameters,
               # which can also be passed as positional arguments,
               # breaking the contract of the parent's method.

           def baz(self, first):
               ...
               # Not keyword-only

* ``redefined-outer-name`` is now also emitted when a
  nested loop's target variable is the same as an outer loop.

  .. code-block:: python

      for i, j in [(1, 2), (3, 4)]:
          for j in range(i):
              print(j)

* relax character limit for method and function names that starts with ``_``.
  This will let people to use longer descriptive names for methods and
  functions with a shorter scope (considered as private). The same idea
  applies to variable names, only with an inverse rule: you want long
  descriptive names for variables with bigger scope, like globals.

* Add ``InvalidMessageError`` exception class and replace ``assert`` in
  pylint.utils with ``raise InvalidMessageError``.

* ``UnknownMessageError`` (formerly ``UnknownMessage``) and
  ``EmptyReportError`` (formerly ``EmptyReport``) are now provided by the new
  ``pylint.exceptions`` submodule instead of ``pylint.utils`` as before.

* We now support inline comments for comma separated values in the configurations

  For instance, you can now use the **#** sign for having comments inside
  comma separated values, as seen below::

      disable=no-member, # Don't care about it for now
              bad-indentation, # No need for this
              import-error

  Of course, interweaving comments with values is also working::

      disable=no-member,
              # Don't care about it for now
              bad-indentation # No need for this


  This works by setting the `inline comment prefixes`_ accordingly.

* Added epytext docstring support to the docparams extension.

* We added support for providing hints when not finding a missing member.

  For example, given the following code, it should be obvious that
  the programmer intended to use the ``mail`` attribute, rather than
  ``email``.

  .. code-block:: python

    class Contribution:
        def __init__(self, name, email, date):
            self.name = name
            self.mail = mail
            self.date = date

    for c in contributions:
        print(c.email) # Oups

  **pylint** will now warn that there is a chance of having a typo,
  suggesting new names that could be used instead.

  .. code-block:: sh

    $ pylint a.py
    E: 8,10: Instance of 'Contribution' has no 'email' member; maybe 'mail'?

  The behaviour is controlled through the ``--missing-member-hint`` option.
  Other options that come with this change are ``--missing-member-max-choices``
  for choosing the total number of choices that should be picked in this
  situation and ``--missing-member-hint-distance``, which specifies a metric
  for computing the distance between the names (this is based on Levenshtein
  distance, which means the lower the number, the more pickier the algorithm
  will be).

* ``PyLinter.should_analyze_file`` has a new parameter, ``is_argument``,
  which specifies if the given path is a **pylint** argument or not.

  ``should_analyze_file`` is called whenever **pylint** tries to determine
  if a file should be analyzed, defaulting to files with the ``.py``
  extension, but this function gets called only in the case where the said
  file is not passed as a command line argument to **pylint**. This usually
  means that pylint will analyze a file, even if that file has a different
  extension, as long as the file was explicitly passed at command line.
  Since ``should_analyze_file`` cannot be overridden to handle all the cases,
  the check for the provenience of files was moved into ``should_analyze_file``.
  This means we now can write something similar with this example, for ignoring
  every file respecting the desired property, disregarding the provenience of the
  file, being it a file passed as CLI argument or part of a package.

  .. code-block:: python

     from pylint.lint import Run, PyLinter

     class CustomPyLinter(PyLinter):

          def should_analyze_file(self, modname, path, is_argument=False):
              if respect_condition(path):
                  return False
              return super().should_analyze_file(modname, path, is_argument=is_argument)


     class CustomRun(Run):
          LinterClass = CustomPyLinter

     CustomRun(sys.argv[1:])

* Imports aliased with underscore are skipped when checking for unused imports.

* ``bad-builtin`` and ``redefined-variable-type`` are now extensions,
  being disabled by default. They can be enabled through:
  ``--load-plugins=pylint.extensions.redefined_variable_type,pylint.extensions.bad_builtin``

  * Imports checker supports new switch ``allow-wildcard-with-all`` which disables
    warning on wildcard import when imported module defines ``__all__`` variable.

* ``differing-param-doc`` is now used for the differing part of the old ``missing-param-doc``,
  and ``differing-type-doc`` for the differing part of the old ``missing-type-doc``.


Bug fixes
=========

* Fix a false positive of ``redundant-returns-doc``, occurred when the documented
  function was using *yield* instead of *return*.

* Fix a false positive of ``missing-param-doc`` and ``missing-type-doc``,
  occurred when a class docstring uses the ``For the parameters, see``
  magic string but the class ``__init__`` docstring does not, or vice versa.

* Added proper exception type inference for ``missing-raises-doc``. Now:

  .. code-block:: python

      def my_func():
          """"My function."""
          ex = ValueError('foo')
          raise ex

  will properly be flagged for missing documentation of
  ``:raises ValueError:`` instead of ``:raises ex:``, among other scenarios.

* Fix false positives of ``missing-[raises|params|type]-doc`` due to not
  recognizing valid keyword synonyms supported by Sphinx.

* More thorough validation in ``MessagesStore.register_messages()`` to detect
  conflicts between a new message and any existing message id, symbol,
  or ``old_names``.

* We now support having plugins that shares the same name and with each one
  providing options.

  A plugin can be logically split into multiple classes, each class providing
  certain capabilities, all of them being tied under the same name. But when
  two or more such classes are also adding options, then **pylint** crashed,
  since it already added the first encountered section. Now, these should
  work as expected.

  .. code-block:: python

     from pylint.checkers import BaseChecker


     class DummyPlugin1(BaseChecker):
         name = 'dummy_plugin'
         msgs = {'I9061': ('Dummy short desc 01', 'dummy-message-01', 'Dummy long desc')}
         options = (
             ('dummy_option_1', {
                 'type': 'string',
                 'metavar': '<string>',
                 'help': 'Dummy option 1',
             }),
         )


     class DummyPlugin2(BaseChecker):
         name = 'dummy_plugin'
         msgs = {'I9060': ('Dummy short desc 02', 'dummy-message-02', 'Dummy long desc')}
         options = (
             ('dummy_option_2', {
                 'type': 'string',
                 'metavar': '<string>',
                 'help': 'Dummy option 2',
             }),
         )


     def register(linter):
         linter.register_checker(DummyPlugin1(linter))
         linter.register_checker(DummyPlugin2(linter))

* We do not yield ``unused-argument`` for singledispatch implementations and
  do not warn about ``function-redefined`` for multiple implementations with same name.

  .. code-block:: python

     from functools import singledispatch

     @singledispatch
     def f(x):
         return 2*x

     @f.register(str)
     def _(x):
         return -1

     @f.register(int)
     @f.register(float)
     def _(x):
         return -x

* ``unused-variable`` checker has new functionality of warning about unused
  variables in global module namespace. Since globals in module namespace
  may be a part of exposed API, this check is disabled by default. For
  enabling it, set ``allow-global-unused-variables`` option to false.

* Fix a false-positive ``logging-format-interpolation`` message, when format
  specifications are used in formatted string. In general, these operations
  are not always convertible to old-style formatting used by logging module.

* Added a new switch ``single-line-class-stmt`` to allow single-line declaration
  of empty class bodies (as seen in the example below). Pylint won't emit a
  ``multiple-statements`` message when this option is enabled.

  .. code-block:: python

     class MyError(Exception): pass

  * ``too-many-format-args`` and ``too-few-format-args`` are emitted correctly
    (or not emitted at all, when exact count of elements in RHS cannot be
    inferred) when starred expressions are used in RHS tuple. For example,
    code block as shown below detects correctly that the used tuple has in
    fact three elements, not two.

  .. code-block:: python

    meat = ['spam', 'ham']
    print('%s%s%s' % ('eggs', *meat))

* ``cyclic-import`` checker supports local disable clauses. When one
  of cycle imports was done in scope where disable clause was active,
  cycle is not reported as violation.

Removed Changes
===============

* ``pylint-gui`` was removed, because it was deemed unfit for being included
  in *pylint*. It had a couple of bugs and misfeatures, its usability was subpar
  and since its development was neglected, we decided it is best to move on without it.


* The HTML reporter was removed, including the ``--output-format=html`` option.
  It was lately a second class citizen in Pylint, being mostly neglected.
  Since we now have the JSON reporter, it can be used as a basis for building
  more prettier HTML reports than what Pylint can currently generate. This is
  part of the effort of removing cruft from Pylint, by removing less used
  features.

* The ``--files-output`` option was removed. While the same functionality cannot
  be easily replicated, the JSON reporter, for instance, can be used as a basis
  for generating the messages per each file.

* ``--required-attributes`` option was removed.

* ``--ignore-iface-methods`` option was removed.

* The ``--optimize-ast`` flag was removed.

  The option was initially added for handling pathological cases,
  such as joining too many strings using the addition operator, which
  was leading pylint to have a recursion error when trying to figure
  out what the string was. Unfortunately, we decided to ignore the
  issue, since the pathological case would have happen when the
  code was parsed by Python as well, without actually reaching the
  runtime step and as such, we decided to remove the error altogether.

* ``epylint.py_run``'s *script* parameter was removed.

  Now ``epylint.py_run`` is always using the underlying ``epylint.lint``
  method from the current interpreter. This avoids some issues when multiple
  instances of **pylint** are installed, which means that ``epylint.py_run``
  might have ran a different ``epylint`` script than what was intended.

.. _`inline comment prefixes`: https://docs.python.org/3/library/configparser.html#customizing-parser-behaviour
````

## File: doc/whatsnew/1/1.8/full.rst
````
Full changelog
==============

What's New in Pylint 1.8.1?
---------------------------
Release date: 2017-12-15

* Wrong version number in __pkginfo__.


What's New in Pylint 1.8?
-------------------------

Release date: 2017-12-15

* Respect disable=... in config file when running with --py3k.

* New warning ``shallow-copy-environ`` added

  Shallow copy of os.environ doesn't work as people may expect. os.environ
  is not a dict object but rather a proxy object, so any changes made
  on copy may have unexpected effects on os.environ

  Instead of copy.copy(os.environ) method os.environ.copy() should be
  used.

  See https://bugs.python.org/issue15373 for details.

  Closes #1301

* Do not display no-absolute-import warning multiple times per file.

* ``trailing-comma-tuple`` refactor check now extends to assignment with
   more than one element (such as lists)

  Closes #1713

* Fixing u'' string in superfluous-parens message

  Closes #1420

* ``abstract-class-instantiated`` is now emitted for all inference paths.

  Closes #1673

* Add set of predefined naming style to ease configuration of checking
  naming conventions.

  Closes #1013

* Added a new check, ``keyword-arg-before-vararg``

  This is emitted for function definitions
  in which keyword arguments are placed before variable
  positional arguments (\*args).

  This may lead to args list getting modified if keyword argument's value
  is not provided in the function call assuming it will take default value
  provided in the definition.

* The ``invalid-name`` check contains the name of the template that caused the failure

  Closes #1176

* Using the -j flag won't start more child linters than needed.

  Closes #1614

* Fix a false positive with bad-python3-import on relative imports

  Closes #1608

* Added a new Python 3 check, ``non-ascii-bytes-literals``

  Closes #1545

* Added a couple of new Python 3 checks for accessing dict methods in non-iterable context

* Protocol checks (not-a-mapping, not-an-iterable and co.) aren't emitted on classes with dynamic getattr

* Added a new warning, 'bad-thread-instantiation'

  This message is emitted when the threading.Thread class does not
  receive the target argument, but receives just one argument, which
  is by default the group parameter.

  Closes #1327

* In non-quiet mode, absolute path of used config file is logged to
  standard error.

  Closes #1519

* Raise meaningful exception for invalid reporter class being selected

  When unknown reporter class will be selected as Pylint reporter,
  meaningful error message would be raised instead of bare ``ImportError``
  or ``AttributeError`` related to module or reporter class being not found.

  Closes #1388

* Added a new Python 3 check for accessing removed functions from itertools
  like ``izip`` or ``ifilterfalse``

* Added a new Python 3 check for accessing removed fields from the types
  module like ``UnicodeType`` or ``XRangeType``

* Added a new Python 3 check for declaring a method ``next`` that would have
  been treated as an iterator in Python 2 but a normal function in Python 3.

* Added a new key-value pair in json output. The key is ``message-id``
  and the value is the message id.

  Closes #1512

* Added a new Python 3.0 check for raising a StopIteration inside a generator.
  The check about raising a StopIteration inside a generator is also valid if the exception
  raised inherit from StopIteration.

  Closes #1385

* Added a new warning, ``raising-format-tuple``, to detect multi-argument
  exception construction instead of message string formatting.

* Added a new check for method of logging module that concatenate string via + operator

  Closes #1479

* Added parameter for limiting number of suggestions in spellchecking checkers

* Fix a corner-case in ``consider-using-ternary`` checker.

  When object ``A`` used in  ``X and A or B`` was falsy in boolean context,
  Pylint incorrectly emitted non-equivalent ternary-based suggestion.
  After a change message is correctly not emitted for this case.

  Closes #1559

* Added ``suggestion-mode`` configuration flag. When flag is enabled, informational
  message is emitted instead of cryptic error message for attributes accessed on
  c-extensions.

  Closes #1466

* Fix a false positive ``useless-super-delegation`` message when
  parameters default values are different from those used in the base class.

  Closes #1085

* Disabling 'wrong-import-order', 'wrong-import-position', or
  'ungrouped-imports' for a single line now prevents that line from
  triggering violations on subsequent lines.

  Closes #1336

* Added a new Python check for inconsistent return statements inside method or function.

  Closes #1267

* Fix ``superfluous-parens`` false positive related to handling logical statements
  involving ``in`` operator.

  Closes #574

* ``function-redefined`` message is no longer emitted for functions and
  methods which names matches dummy variable name regular expression.

  Closes #1369

* Fix ``missing-param-doc`` and ``missing-type-doc`` false positives when
  mixing ``Args`` and ``Keyword Args`` in Google docstring.

  Closes #1409

 * Fix ``missing-docstring`` false negatives when modules, classes, or methods
   consist of compound statements that exceed the ``docstring-min-length``

* Fix ``useless-else-on-loop`` false positives when break statements are
  deeply nested inside loop.

  Closes #1661

* Fix no ``wrong-import-order`` message emitted on ordering of first and third party
  libraries. With this fix, pylint distinguishes third and first party
  modules when checking import order.

  Closes #1702

* Fix ``pylint disable=fixme`` directives ignored for comments following the
  last statement in a file.

  Closes #1681

* Fix ``line-too-long`` message deactivated by wrong disable directive.
  The directive ``disable=fixme`` doesn't deactivate anymore the emission
  of ``line-too-long`` message for long commented lines.

  Closes #1741

* If the rcfile specified on the command line doesn't exist, then an
  IOError exception is raised.

  Closes #1747

* Fix the wrong scope of the ``disable=`` directive after a commented line.
  For example when a ``disable=line-too-long`` directive is at the end of
  a long commented line, it no longer disables the emission of ``line-too-long``
  message for lines that follow.

  Closes #1742
````

## File: doc/whatsnew/1/1.8/index.rst
````
**************************
  What's New In Pylint 1.8
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/1/1.8/summary.rst
````
:Release: 1.8
:Date: 2017-12-15


Summary -- Release highlights
=============================

* None so far

New checkers
============

* A new check was added, ``shallow-copy-environ``.

  This warning message is emitted when shallow copy of os.environ is created.
  Shallow copy of os.environ doesn't work as people may expect. os.environ
  is not a dict object but rather a proxy object, so any changes made
  on copy may have unexpected effects on os.environ

  Instead of copy.copy(os.environ) method os.environ.copy() should be used.

  See https://bugs.python.org/issue15373 for details.

  .. code-block:: python

     import copy
     import os
     wrong_env_copy = copy.copy(os.environ)  # will emit pylint warning
     wrong_env_copy['ENV_VAR'] = 'new_value'  # changes os.environ
     assert os.environ['ENV_VAR'] == 'new_value'

     good_env_copy = dict(os.environ)  # the right way
     good_env_copy['ENV_VAR'] = 'different_value'  # doesn't change os.environ
     assert os.environ['ENV_VAR'] == 'new_value'

* A new check was added, ``keyword-arg-before-vararg``.

  This warning message is emitted when a function is defined with a keyword
  argument appearing before variable-length positional arguments (\*args).
  This may lead to args list getting modified if keyword argument's value is
  not provided in the function call assuming it will take default value provided
  in the definition.

  .. rstcheck: ignore-next-code-block
  .. code-block:: python

     def foo(a, b=3, *args):
         print(a, b, args)

     # Case1: a=0, b=2, args=(4,5)
     foo(0,2,4,5) # 0 2 (4,5) ==> Observed values are same as expected values

     # Case2: a=0, b=<default_value>, args=(4,5)
     foo(0,4,5) # 0 4 (5,) ==> args list got modified as well as the observed value of b

     # Case3: Syntax Error if tried as follows
     foo(0,b=2,4,5) # syntax error

* A new check was added, ``simplify-boolean-expression``.

  This message is emitted when ``consider-using-ternary`` check would emit
  not equivalent code, due to truthy element being falsy in boolean context.

  .. code-block:: python

     value = condition and False or other_value

  This flawed construct may be simplified to:

  .. code-block:: python

     value = other_value

* A new check was added, ``bad-thread-instantiation``.

  This message is emitted when the threading.Thread class does not
  receive the target argument, but receives just one argument, which
  is by default the group parameter.

  In the following example, the instantiation will fail, which is definitely
  not desired:

  .. code-block:: python

     import threading
     threading.Thread(lambda: print(1)) # Oups, this is the group parameter

* A new Python 3 checker was added to warn about accessing functions that have been
  removed from the itertools module ``izip``, ``imap``, ``iflter``, ``izip_longest``, and ``ifilterfalse``.

  .. code-block:: python

      from itertools import izip
      print(list(izip([1, 2], [3])))

  Instead use ``six.moves`` to import a Python 2 and Python 3 compatible function:

  .. code-block:: python

      from six.moves import zip
      print(list(zip([1, 2], [3])))

* A new Python 3 checker was added to warn about accessing deprecated fields from
  the types module like ``ListType`` or ``IntType``

  .. code-block:: python

      from types import ListType
      print(isinstance([], ListType))

  Instead use the declarations in the builtin namespace:

  .. code-block:: python

      print(isinstance([], list))

* A new Python 3 checker was added to warn about declaring a ``next`` method that
  would have implemented the ``Iterator`` protocol in Python 2 but is now a normal
  method in Python 3.

  .. code-block:: python

      class Foo(object):
          def next(self):
              return 42

  Instead implement a ``__next__`` method and use ``six.Iterator`` as a base class
  or alias ``next`` to ``__next__``:

  .. code-block:: python

      class Foo(object):
          def __next__(self):
              return 42
          next = __next__

* Three new Python 3 checkers were added to warn about using dictionary methods
  in non-iterating contexts.

  For example, the following are returning iterators in Python 3::

  .. code-block:: python

     d = {}
     d.keys()[0]
     d.items()[0]
     d.values() + d.keys()

* A new Python 3 porting check was added, ``non-ascii-bytes-literals``

  This message is emitted whenever we detect that a bytes string contain
  non-ASCII characters, which results in a SyntaxError on Python 3.

* A new warning, ``raising-format-tuple``, will catch situations where the
  intent was likely raising an exception with a formatted message string,
  but the actual code did omit the formatting and instead passes template
  string and value parameters as separate arguments to the exception
  constructor.  So it detects things like

  .. code-block:: python

      raise SomeError('message about %s', foo)
      raise SomeError('message about {}', foo)

  which likely were meant instead as

  .. code-block:: python

      raise SomeError('message about %s' % foo)
      raise SomeError('message about {}'.format(foo))

  This warning can be ignored on projects which deliberately use lazy
  formatting of messages in all user-facing exception handlers.

* Following the recommendations of PEP479_ ,a new Python 3.0 checker was added to warn about raising a ``StopIteration`` inside
  a generator. Raising a ``StopIteration`` inside a generator may be due a direct call
  to ``raise StopIteration``:

  .. code-block:: python

      def gen_stopiter():
          yield 1
          yield 2
          yield 3
          raise StopIteration

  Instead use a simple ``return`` statement

  .. code-block:: python

      def gen_stopiter():
          yield 1
          yield 2
          yield 3
          return

  Raising a ``StopIteration`` may also be due to the call to ``next`` function with a generator
  as argument:

  .. code-block:: python

      def gen_next_raises_stopiter():
          g = gen_ok()
          while True:
              yield next(g)

  In this case, surround the call to ``next`` with a try/except block:

  .. code-block:: python

      def gen_next_raises_stopiter():
          g = gen_ok()
          while True:
              try:
                  yield next(g)
              except StopIteration:
                  return

* The check about raising a StopIteration inside a generator is also valid if the exception
  raised inherit from StopIteration.

  Closes #1385

 .. _PEP479: https://peps.python.org/pep-0479

* A new Python checker was added to warn about using a ``+`` operator inside call of logging methods
  when one of the operands is a literal string:

  .. code-block:: python

     import logging
     var = "123"
     logging.log(logging.INFO, "Var: " + var)

  Instead use formatted string and positional arguments :

  .. code-block:: python

     import logging
     var = "123"
     logging.log(logging.INFO, "Var: %s", var)

* A new Python checker was added to warn about ``inconsistent-return-statements``. A function or a method
  has inconsistent return statements if it returns both explicit and implicit values :

  .. code-block:: python

    def mix_implicit_explicit_returns(arg):
        if arg < 10:
            return True
        elif arg < 20:
            return

  According to PEP8_, if any return statement returns an expression,
  any return statements where no value is returned should explicitly state this as return None,
  and an explicit return statement should be present at the end of the function (if reachable).
  Thus, the previous function should be written:

  .. code-block:: python

    def mix_implicit_explicit_returns(arg):
        if arg < 10:
            return True
        elif arg < 20:
            return None

  Closes #1267

 .. _PEP8: https://peps.python.org/pep-0008

Other Changes
=============

* Fixing u'' string in superfluous-parens message.

* Configuration options of invalid name checker are significantly redesigned.
  Predefined rules for common naming styles were introduced. For typical
  setups, user friendly options like ``--function-naming-style=camelCase`` may
  be used in place of hand-written regular expressions. Default linter config
  enforce PEP8-compatible naming style. See documentation for details.

* Raise meaningful exception in case of invalid reporter class (output format)
  being selected.

* The docparams extension now allows a property docstring to document both
  the property and the setter. Therefore setters can also have no docstring.

* The docparams extension now understands property type syntax.

  .. code-block:: python

      class Foo(object):
          @property
          def foo(self):
              """My Sphinx style docstring description.

              :type: int
              """
              return 10

  .. code-block:: python

    class Foo(object):
        @property
        def foo(self):
            """int: My Numpy and Google docstring style description."""
            return 10

* In case of ``--output-format=json``, the dictionary returned holds a new key-value pair.
  The key is ``message-id`` and the value the message id.

* Spelling checker has a new configuration parameter ``max-spelling-suggestions``, which
  affects maximum count of suggestions included in emitted message.

* The **invalid-name** check contains the name of the template that caused the failure.

  For the given code, **pylint** used to emit ``invalid-name`` in the form ``Invalid constant name var``,
  without offering any context why ``var`` is not such a good name.

  With this change, it is now more clear what should be improved for a name to be accepted according to
  its corresponding template.

* New configuration flag, ``suggestion-mode`` was introduced. When enabled, pylint would
  attempt to emit user-friendly suggestions instead of spurious errors for some known
  false-positive scenarios. Flag is enabled by default.

* ``superfluous-parens`` is no longer wrongly emitted for logical statements involving ``in`` operator
  (see example below for what used to be false-positive).

  .. code-block:: python

    foo = None
    if 'bar' in (foo or {}):
      pass

* Redefinition of dummy function is now possible. ``function-redefined`` message won't be emitted anymore when
  dummy functions are redefined.

* ``missing-param-doc`` and ``missing-type-doc`` are no longer emitted when
  ``Args`` and ``Keyword Args`` are mixed in Google docstring.

* Fix of false positive ``useless-super-delegation`` message when
  parameters default values are different from those used in the base class.

* Fix of false positive ``useless-else-on-loop`` message when break statements
  are deeply nested inside loop.

* The Python 3 porting checker no longer emits multiple ``no-absolute-import`` per file.

* The Python 3 porting checker respects disabled checkers found in the config file.

* Modules, classes, or methods consist of compound statements that exceed the ``docstring-min-length``
  are now correctly emitting ``missing-docstring``

* Fix no ``wrong-import-order`` message emitted on ordering of first and third party libraries.
  With this fix, pylint distinguishes first and third party modules when checking
  import order.

* Fix the ignored ``pylint disable=fixme`` directives for comments following
  the last statement in a file.

* Fix ``line-too-long`` message deactivated by wrong disable directive.
  The directive ``disable=fixme`` doesn't deactivate anymore the emission
  of ``line-too-long`` message for long commented lines.

* If the rcfile specified on the command line doesn't exist, then an
  IOError exception is raised.

* Fix the wrong scope of ``disable=`` directive after a commented line.
  For example when a ``disable=line-too-long`` directive is at the end of a
  long commented line, it no longer disables the emission of ``line-too-long``
  message for lines that follow.
````

## File: doc/whatsnew/1/1.9/full.rst
````
Full changelog
==============

What's New in Pylint 1.9?
-------------------------

Release date: 2018-05-15

* Added two new Python 3 porting checks, ``exception-escape`` and ``comprehension-escape``

  These two are emitted whenever pylint detects that a variable defined in the
  said blocks is used outside of the given block. On Python 3 these values are deleted.

* Added a new ``deprecated-sys-function``, emitted when accessing removed sys members.

* Added ``xreadlines-attribute``, emitted when the ``xreadlines()`` attribute is accessed.

* The Python 3 porting mode can now run with Python 3 as well.

* docparams extension allows abstract methods to document what overriding
  implementations should return, and to raise NotImplementedError without
  documenting it.

  Closes #2044

* Special methods do not count towards ``too-few-methods``,
  and are considered part of the public API.

* Enum classes do not trigger ``too-few-methods``

  Closes #605

* Added a new Python 2/3 check for accessing ``operator.div``, which is removed in Python 3

  Closes #1936

* Added a new Python 2/3 check for accessing removed urllib functions

  Closes #1997
````

## File: doc/whatsnew/1/1.9/index.rst
````
**************************
  What's New In Pylint 1.9
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/1/1.9/summary.rst
````
:Release: 1.9
:Date: 2018-05-15


Summary -- Release highlights
=============================

* None so far

New checkers
============

* A new Python 3 checker was added to warn about the removed ``operator.div`` function.

* A new Python 3 checker was added to warn about accessing functions that have been
  moved from the urllib module in corresponding subpackages, such as ``urllib.request``.

  .. code-block:: python

      from urllib import urlencode

  Instead the previous code should use ``urllib.parse`` or ``six.moves`` to import a
  module in a Python 2 and 3 compatible fashion:

  .. code-block:: python

      from six.moves.urllib.parse import urlencode


  To have this working on Python 3 as well, please use the ``six`` library:

  .. code-block:: python

      six.reraise(Exception, "value", tb)


* A new check was added to warn about using unicode raw string literals. This is
  a syntax error in Python 3:

  .. rstcheck: ignore-next-code-block
  .. code-block:: python

      a = ur'...'

* Added a new ``deprecated-sys-function`` check, emitted when accessing removed ``sys`` members.

* Added ``xreadlines-attribute`` check, emitted when the ``xreadlines()`` attribute is accessed
  on a file object.

* Added two new Python 3 porting checks, ``exception-escape`` and ``comprehension-escape``

  These two are emitted whenever pylint detects that a variable defined in the
  said blocks is used outside of the given block. On Python 3 these values are deleted.

  .. code-block:: python

      try:
        1/0
      except ZeroDivisionError as exc:
         ...
      print(exc) # This will raise a NameError on Python 3

      [i for i in some_iterator if some_condition(i)]
      print(i) # This will raise a NameError on Python 3


Other Changes
=============

* ``defaultdict`` and subclasses of ``dict`` are now handled for `dict-iter-*` checks. That
  means that the following code will now emit warnings for when ``iteritems`` and friends
  are accessed:

  .. code-block:: python

      some_dict = defaultdict(list)
      ...
      some_dict.iterkeys()

* Enum classes no longer trigger ``too-few-methods``

* Special methods now count towards ``too-few-methods``,
  and are considered part of the public API.
  They are still not counted towards the number of methods for
  ``too-many-methods``.

* docparams allows abstract methods to document returns documentation even
  if the default implementation does not return something.
  They also no longer need to document raising a NotImplementedError.
````

## File: doc/whatsnew/1/1.0.rst
````
**************************
  What's New In Pylint 1.0
**************************

Release date: 2013-08-06

* Add check for the use of 'exec' function

* New --msg-template option to control output, deprecating "msvc" and
  "parseable" output formats as well as killing ``--include-ids`` and ``--symbols``
  options

* Do not emit [fixme] for every line if the config value 'notes'
  is empty, but [fixme] is enabled.

* Emit warnings about lines exceeding the column limit when
  those lines are inside multiline docstrings.

* Do not double-check parameter names with the regex for parameters and
  inline variables.

* Added a new warning missing-final-newline (C0304) for files missing
  the final newline.

* Methods that are decorated as properties are now treated as attributes
  for the purposes of name checking.

* Names of derived instance class member are not checked any more.

* Names in global statements are now checked against the regular
  expression for constants.

* For toplevel name assignment, the class name regex will be used if
  pylint can detect that value on the right-hand side is a class
  (like collections.namedtuple()).

* Simplified invalid-name message

* Added a new warning invalid-encoded-data (W0512) for files that
  contain data that cannot be decoded with the specified or
  default encoding.

* New warning bad-open-mode (W1501) for calls to open (or file) that
  specify invalid open modes (Original implementation by Sasha Issayev).

* New warning old-style-class (C1001) for classes that do not have any
  base class.

* Add new name type 'class_attribute' for attributes defined
  in class scope. By default, allow both const and variable names.

* New warning trailing-whitespace (C0303) that warns about
  trailing whitespace.

* Added a new warning unpacking-in-except (W0712) about unpacking
  exceptions in handlers, which is unsupported in Python 3.

* Add a configuration option for missing-docstring to
  optionally exempt short functions/methods/classes from
  the check.

* Add the type of the offending node to missing-docstring
  and empty-docstring.

* New utility classes for per-checker unittests in testutils.py

* Do not warn about redefinitions of variables that match the
  dummy regex.

* Do not treat all variables starting with _ as dummy variables,
  only _ itself.

* Make the line-too-long warning configurable by adding a regex for lines
  for with the length limit should not be enforced

* Do not warn about a long line if a pylint disable
  option brings it above the length limit

* Do not flag names in nested with statements as undefined.

* Added a new warning 'old-raise-syntax' for the deprecated syntax
  raise Exception, args

* Support for PEP 3102 and new missing-kwoa (E1125) message for missing
  mandatory keyword argument

  Closes Logilab #107788

* Fix spelling of max-branchs option, now max-branches

* Added a new base class and interface for checkers that work on the
  tokens rather than the syntax, and only tokenize the input file
  once.

* Follow astng renaming to astroid

* Check for unbalanced unpacking in assignments

  Closes BitBucket #37

* Fix incomplete-protocol false positive for read-only containers like tuple

  Closes BitBucket #25

* Fix False positive E1003 on Python 3 for argument-less super()

  Closes BitBucket #16

* Put back documentation in source distribution

  Closes BitBucket #6

* epylint shouldn't hang anymore when there is a large output on pylint'stderr

  Closes BitBucket #15

* Fix epylint w/ python3

  Closes BitBucket #7

* Remove string module from the default list of deprecated modules

  Closes BitBucket #3
````

## File: doc/whatsnew/1/1.1.rst
````
**************************
  What's New In Pylint 1.1
**************************

Release date: 2013-12-22

* Add new check for use of deprecated pragma directives "pylint:disable-msg"
  or "pylint:enable-msg" (I0022, deprecated-pragma) which was previously
  emitted as a regular warn().

* Avoid false used-before-assignment for except handler defined
  identifier used on the same line.

  Closes #111

* Combine 'no-space-after-operator', 'no-space-after-comma' and
  'no-space-before-operator' into a new warning 'bad-whitespace'.

* Add a new warning 'superfluous-parens' for unnecessary
  parentheses after certain keywords.

* Fix a potential crash in the redefine-in-handler warning
  if the redefined name is a nested getattr node.

* Add a new option for the multi-statement warning to
  allow single-line if statements.

* Add 'bad-context-manager' error, checking that '__exit__'
  special method accepts the right number of arguments.

* Run pylint as a python module 'python -m pylint' (Anatoly Techtonik).

* Check for non-exception classes inside an except clause.

* epylint support options to give to pylint after the file to analyze and
  have basic input validation, patches provided by
  felipeochoa and Brian Lane.

  Closes BitBucket #53
  Closes BitBucket #54

* Added a new warning, 'non-iterator-returned', for non-iterators
  returned by '__iter__'.

* Add new checks for unpacking non-sequences in assignments
  (unpacking-non-sequence) as well as unbalanced tuple unpacking
  (unbalanced-tuple-unpacking).

* useless-else-on-loop not emitted if there is a break in the
  else clause of inner loop.

  Closes #117

* don't mark ``input`` as a bad function when using python3.

  Closes #110

* badly-implemented-container caused several problems in its
  current implementation. Deactivate it until we have something
  better.

  Refs #112

* Use attribute regexp for properties in python3, as in python2

* Create the ``PYLINTHOME`` directory when needed, it might fail and lead to
  spurious warnings on import of pylint.config.

* Fix setup.py so that pylint properly install on Windows when using python3

* Various documentation fixes and enhancements

* Fix a false-positive trailing-whitespace on Windows

  Closes #55
````

## File: doc/whatsnew/1/1.2.rst
````
**************************
  What's New In Pylint 1.2
**************************

Release date: 2014-04-30

* Restore the ability to specify the init-hook option via the
  configuration file, which was accidentally broken in 1.2.0.

* Add a new warning [bad-continuation] for badly indented continued
  lines.

* Emit [assignment-from-none] when the function contains bare returns.

  Closes BitBucket #191

* Added a new warning for closing over variables that are
  defined in loops.

  Closes BitBucket #176

* Do not warn about \u escapes in string literals when Unicode literals
  are used for Python 2.*.

  Closes BitBucket #151

* Extend the checking for unbalanced-tuple-unpacking and
  unpacking-non-sequence to instance attribute unpacking as well.

* Fix explicit checking of python script (1.2 regression)

  Closes #219

* Restore --init-hook, renamed accidentally into --init-hooks in 1.2.0

  Closes #211

* Add 'indexing-exception' warning, which detects that indexing
  an exception occurs in Python 2 (behaviour removed in Python 3).


What's New in Pylint 1.2.0?
===========================
Release date: 2014-04-18

* Pass the current python paths to pylint process when invoked via
  epylint.

  Closes BitBucket #133.

* Add -i / --include-ids and -s / --symbols back as completely ignored
  options.

  Closes BitBucket #180.

* Extend the number of cases in which logging calls are detected.

  Closes BitBucket #182.

* Improve pragma handling to not detect pylint:* strings in non-comments.

  Closes BitBucket #79.

* Do not crash with UnknownMessage if an unknown message ID/name appears
  in disable or enable in the configuration. Patch by Cole Robinson.

  Closes BitBucket #170

* Add new warning 'eval-used', checking that the builtin function ``eval`` was used.

* Make it possible to show a naming hint for invalid name by setting
  include-naming-hint. Also make the naming hints configurable.

  Closes BitBucket #138

* Added support for enforcing multiple, but consistent name styles for
  different name types inside a single module; based on a patch written
  by morbo@google.com.

* Also warn about empty docstrings on overridden methods; contributed
  by sebastianu@google.com.

* Also inspect arguments to constructor calls, and emit relevant
  warnings; contributed by sebastianu@google.com.

* Added a new configuration option logging-modules to make the list
  of module names that can be checked for 'logging-not-lazy' et. al.
  configurable; contributed by morbo@google.com.

* ensure init-hooks is evaluated before other options, notably load-plugins

  Closes #166

* Python 2.5 support restored: fixed small issues preventing pylint to run
  on python 2.5.

  Closes BitBucket #50
  Closes BitBucket #62

* pylint doesn't crash when looking for used-before-assignment in context manager assignments.

  Closes BitBucket #128

* Add new warning, 'bad-reversed-sequence', for checking that the
  reversed() builtin receive a sequence (implements ``__getitem__`` and ``__len__``,
  without being a dict or a dict subclass) or an instance which implements
  ``__reversed__``.

* Mark ``file`` as a bad function when using python2

  Closes #8

* Add new warning 'bad-exception-context', checking
  that ``raise ... from ...`` uses a proper exception context
  (None or an exception).

* Enhance the check for 'used-before-assignment' to look
  for 'nonlocal' uses.

* Emit 'undefined-all-variable' if a package's __all__
  variable contains a missing submodule.

  Closes #126

* Add a new warning 'abstract-class-instantiated' for checking
  that abstract classes created with ``abc`` module and
  with abstract methods are instantiated.

* Do not warn about 'return-arg-in-generator' in Python 3.3+.

* Do not warn about 'abstract-method' when the abstract method
  is implemented through assignment

  Closes #155

* Improve cyclic import detection in the case of packages, patch by Buck Golemon

* Add new warnings for checking proper class __slots__:
  ``invalid-slots-object`` and ``invalid-slots``.

* Search for rc file in `~/.config/pylintrc` if `~/.pylintrc`
  doesn't exists

  Closes #121

* Don't register the new style checker w/ python >= 3

* Fix unused-import false positive w/ augment assignment

  Closes #78

* Fix access-member-before-definition false negative wrt aug assign

  Closes #164

* Do not attempt to analyze non python file, e.g. .so file

  Closes #122
````

## File: doc/whatsnew/1/1.3.rst
````
**************************
  What's New In Pylint 1.3
**************************

Release date: 2014-07-26

* Allow hanging continued indentation for implicitly concatenated
  strings.

  Closes #232.

* Pylint works under Python 2.5 again, and its test suite passes.

* Fix some false positives for the cellvar-from-loop warnings.

  Closes #233.

* Return new astroid class nodes when the inferencer can detect that
  that result of a function invocation on a type (like ``type`` or
  `abc.ABCMeta`) is requested.

  Closes #205.

* Emit 'undefined-variable' for undefined names when using the
  Python 3 ``metaclass=`` argument.

* Checkers respect priority now.

  Closes #229

* Fix a false positive regarding W0511.

  Closes #149.

* Fix unused-import false positive with Python 3 metaclasses

  Closes #143

* Don't warn with 'bad-format-character' when encountering
  the 'a' format on Python 3.

* Add multiple checks for PEP 3101 advanced string formatting:
  'bad-format-string', 'missing-format-argument-key',
  'unused-format-string-argument', 'format-combined-specification',
  'missing-format-attribute' and 'invalid-format-index'.

* Issue broad-except and bare-except even if the number
  of except handlers is different than 1.

  Closes #113

* Issue attribute-defined-outside-init for all cases, not just
  for the last assignment.

  Closes #262

* Emit 'not-callable' when calling properties.

  Closes #268.

* Fix a false positive with unbalanced iterable unpacking,
  when encountering starred nodes.

  Closes #273.

* Add new checks, 'invalid-slice-index' and 'invalid-sequence-index'
  for invalid sequence and slice indices.

* Add 'assigning-non-slot' warning, which detects assignments to
  attributes not defined in slots.

* Don't emit 'no-name-in-module' for ignored modules.

  Closes #223.

* Fix an 'unused-variable' false positive, where the variable is
  assigned through an import.

  Closes #196.

* Definition order is considered for classes, function arguments
  and annotations.

  Closes #257.

* Don't emit 'unused-variable' when assigning to a nonlocal.

  Closes #275.

* Do not let ImportError propagate from the import checker, leading to crash
  in some namespace package related cases.

  Closes #203.

* Don't emit 'pointless-string-statement' for attribute docstrings.

  Closes #193.

* Use the proper mode for pickle when opening and writing the stats file.

  Closes #148.

* Don't emit hidden-method message when the attribute has been
  monkey-patched, you're on your own when you do that.

* Only emit attribute-defined-outside-init for definition within the same
  module as the offended class, avoiding to mangle the output in some cases.

* Don't emit 'unnecessary-lambda' if the body of the lambda call contains
  call chaining.

  Closes #243.

* Don't emit 'missing-docstring' when the actual docstring uses ``.format``.

  Closes #281.
````

## File: doc/whatsnew/1/1.4.rst
````
**************************
  What's New In Pylint 1.4
**************************

What's New in Pylint 1.4.3?
===========================
Release date: 2015-03-14

* Remove three warnings: star-args, abstract-class-little-used,
  abstract-class-not-used. These warnings don't add any real value
  and they don't imply errors or problems in the code.

* Added a new option for controlling the peephole optimizer in astroid.
  The option ``--optimize-ast`` will control the peephole optimizer,
  which is used to optimize a couple of AST subtrees. The current problem
  solved by the peephole optimizer is when multiple joined strings,
  with the addition operator, are encountered. If the numbers of such
  strings is high enough, Pylint will then fail with a maximum recursion
  depth exceeded error, due to its visitor architecture. The peephole
  just transforms such calls, if it can, into the final resulting string
  and this exhibit a problem, because the visit_binop method stops being
  called (in the optimized AST it will be a Const node).


What's New in Pylint 1.4.2?
===========================
Release date: 2015-03-11

* Don't require a docstring for empty modules.

  Closes #261

* Fix a false positive with ``too-few-format-args`` string warning,
  emitted when the string format contained a normal positional
  argument ('{0}'), mixed with a positional argument which did
  an attribute access ('{0.__class__}').

  Closes #463

* Take in account all the methods from the ancestors
  when checking for too-few-public-methods.

  Closes #471

* Catch enchant errors and emit 'invalid-characters-in-docstring'
  when checking for spelling errors.

  Closes #469

* Use all the inferred statements for the super-init-not-called
  check.

  Closes #389

* Add a new warning, 'unichr-builtin', emitted by the Python 3
  porting checker, when the unichr builtin is found.

  Closes #472

* Add a new warning, 'intern-builtin', emitted by the Python 3
  porting checker, when the intern builtin is found.

  Closes #473

* Add support for editable installations.

* The HTML output accepts the ``--msg-template`` option. Patch by
  Dan Goldsmith.

* Add 'map-builtin-not-iterating' (replacing 'implicit-map-evaluation'),
  'zip-builtin-not-iterating', 'range-builtin-not-iterating', and
  'filter-builtin-not-iterating' which are emitted by ``--py3k`` when the
  appropriate built-in is not used in an iterating context (semantics
  taken from 2to3).

* Add a new warning, 'unidiomatic-typecheck', emitted when an explicit
  typecheck uses type() instead of isinstance(). For example,
  `type(x) == Y` instead of `isinstance(x, Y)`. Patch by Chris Rebert.

  Closes #299

* Add support for combining the Python 3 checker mode with the --jobs
  flag (--py3k and --jobs).

  Closes #467

* Add a new warning for the Python 3 porting checker, 'using-cmp-argument',
  emitted when the ``cmp`` argument for the ``list.sort`` or ``sorted builtin``
  is encountered.

* Make the --py3k flag commutative with the -E flag. Also, this patch
  fixes the leaks of error messages from the Python 3 checker when
  the errors mode was activated.

  Closes #437


What's New in Pylint 1.4.1?
===========================
Release date: 2015-01-16

* Look only in the current function's scope for bad-super-call.

  Closes #403

* Check the return of properties when checking for not-callable.

  Closes #406

* Warn about using the input() or round() built-ins for Python 3.

  Closes #411

* Proper abstract method lookup while checking for abstract-class-instantiated.

  Closes #401

* Use a mro traversal for finding abstract methods.

  Closes #415

* Fix a false positive with catching-non-exception and tuples of exceptions.

* Fix a false negative with raising-non-exception, when the raise used
  an uninferrable exception context.

* Fix a false positive on Python 2 for raising-bad-type, when
  raising tuples in the form 'raise (ZeroDivisionError, None)'.

* Fix a false positive with invalid-slots-objects, where the slot entry
  was a unicode string on Python 2.

  Closes #421

* Add a new warning, 'redundant-unittest-assert', emitted when using
  unittest's methods assertTrue and assertFalse with constant value
  as argument. Patch by Vlad Temian.

* Add a new JSON reporter, usable through -f flag.

* Add the method names for the 'signature-differs' and 'argument-differs'
  warnings.

  Closes #433

* Don't compile test files when installing.

* Fix a crash which occurred when using multiple jobs and the files
  given as argument didn't exist at all.

What's New in Pylint 1.4.0?
===========================
Release date: 2014-11-23

* Added new options for controlling the loading of C extensions.
  By default, only C extensions from the stdlib will be loaded
  into the active Python interpreter for inspection, because they
  can run arbitrary code on import. The option
  ``--extension-pkg-whitelist`` can be used to specify modules
  or packages that are safe to load.

* Change default max-line-length to 100 rather than 80

* Drop BaseRawChecker class which were only there for backward
  compatibility for a while now

* Don't try to analyze string formatting with objects coming from
  function arguments.

  Closes #373

* Port source code to be Python 2/3 compatible. This drops the
  need for 2to3, but does drop support for Python 2.5.

* Each message now comes with a confidence level attached, and
  can be filtered base on this level. This allows to filter out
  all messages that were emitted even though an inference failure
  happened during checking.

* Improved presenting unused-import message.

  Closes #293

* Add new checker for finding spelling errors. New messages:
  wrong-spelling-in-comment, wrong-spelling-in-docstring.
  New options: spelling-dict, spelling-ignore-words.

* Add new '-j' option for running checks in sub-processes.

* Added new checks for line endings if they are mixed (LF vs CRLF)
  or if they are not as expected. New messages: mixed-line-endings,
  unexpected-line-ending-format. New option: expected-line-ending-format.

* 'dangerous-default-value' no longer evaluates the value of the arguments,
  which could result in long error messages or sensitive data being leaked.

  Closes #282

* Fix a false positive with string formatting checker, when
  encountering a string which uses only position-based arguments.

  Closes #285

* Fix a false positive with string formatting checker, when using
  keyword argument packing.

  Closes #288

* Proper handle class level scope for lambdas.

* Handle 'too-few-format-args' or 'too-many-format-args' for format
  strings with both named and positional fields.

  Closes #286

* Analyze only strings by the string format checker.

  Closes #287

* Properly handle nested format string fields.

  Closes #294

* Don't emit 'attribute-defined-outside-init' if the attribute
  was set by a function call in a defining method.

  Closes #192

* Properly handle unicode format strings for Python 2.

  Closes #296

* Don't emit 'import-error' if an import was protected by a try-except,
  which excepted ImportError.

* Fix an 'unused-import' false positive, when the error was emitted
  for all the members imported with 'from import' form.

  Closes #304

* Don't emit 'invalid-name' when assigning a name in an
  ImportError handler.

  Closes #302

* Don't count branches from nested functions.

* Fix a false positive with 'too-few-format-args', when the format
  strings contains duplicate manual position arguments.

  Closes #310

* fixme regex handles comments without spaces after the hash.

  Closes #311

* Don't emit 'unused-import' when a special object is imported
  (__all__, __doc__ etc.).

  Closes #309

* Look in the metaclass, if defined, for members not found in the current
  class.

  Closes #306

* Don't emit 'protected-access' if the attribute is accessed using
  a property defined at the class level.

* Detect calls of the parent's __init__, through a binded super() call.

* Check that a class has an explicitly defined metaclass before
  emitting 'old-style-class' for Python 2.

* Emit 'catching-non-exception' for non-class nodes.

  Closes #303

* Order of reporting is consistent.

* Add a new warning, 'boolean-datetime', emitted when an instance
  of 'datetime.time' is used in a boolean context.

  Closes #239

* Fix a crash which occurred while checking for 'method-hidden',
  when the parent frame was something different than a function.

* Generate html output for missing files.

  Closes #320

* Fix a false positive with 'too-many-format-args', when the format
  string contains mixed attribute access arguments and manual
  fields.

  Closes #322

* Extend the cases where 'undefined-variable' and 'used-before-assignment'
  can be detected.

  Closes #291

* Add support for customising callback identifiers, by adding a new
  '--callbacks' command line option.

  Closes #326

* Add a new warning, 'logging-format-interpolation', emitted when .format()
  string interpolation is used within logging function calls.

* Don't emit 'unbalanced-tuple-unpacking' when the rhs of the assignment
  is a variable length argument.

  Closes #329

* Add a new warning, 'inherit-non-class', emitted when a class inherits
  from something which is not a class.

  Closes #331

* Fix another false positives with 'undefined-variable', where the variable
  can be found as a class assignment and used in a function annotation.

  Closes #342

* Handle assignment of the string format method to a variable.

  Closes #351

* Support wheel packaging format for PyPi.

  Closes #334

* Check that various built-ins that do not exist in Python 3 are not
  used: apply, basestring, buffer, cmp, coerce, execfile, file, long
  raw_input, reduce, StandardError, unicode, reload and xrange.

* Warn for magic methods which are not used in any way in Python 3:
  __coerce__, __delslice__, __getslice__, __setslice__, __cmp__,
  __oct__, __nonzero__ and __hex__.

* Don't emit 'assigning-non-slot' when the assignment is for a property.

  Closes #359

* Fix for regression: '{path}' was no longer accepted in '--msg-template'.

* Report the percentage of all messages, not just for errors and warnings.

  Closes #319

* 'too-many-public-methods' is reported only for methods defined in a class,
  not in its ancestors.

  Closes #248

* 'too-many-lines' disable pragma can be located on any line, not only the
  first.

  Closes #321

* Warn in Python 2 when an import statement is found without a
  corresponding ``from __future__ import absolute_import``.

* Warn in Python 2 when a non-floor division operation is found without
  a corresponding ``from __future__ import division``.

* Add a new option, 'exclude-protected', for excluding members
  from the protected-access warning.

  Closes #48

* Warn in Python 2 when using dict.iter*(), dict.view*(); none of these
  methods are available in Python 3.

* Warn in Python 2 when calling an object's next() method; Python 3 uses
  __next__() instead.

* Warn when assigning to __metaclass__ at a class scope; in Python 3 a
  metaclass is specified as an argument to the 'class' statement.

* Warn when performing parameter tuple unpacking; it is not supported in
  Python 3.

* 'abstract-class-instantiated' is also emitted for Python 2.
  It was previously disabled.

* Add 'long-suffix' error, emitted when encountering the long suffix
  on numbers.

* Add support for disabling a checker, by specifying an 'enabled'
  attribute on the checker class.

* Add a new CLI option, --py3k, for enabling Python 3 porting mode. This
  mode will disable all other checkers and will emit warnings and
  errors for constructs which are invalid or removed in Python 3.

* Add 'old-octal-literal' to Python 3 porting checker, emitted when
  encountering octals with the old syntax.

* Add 'implicit-map-evaluation' to Python 3 porting checker, emitted
  when encountering the use of map builtin, without explicit evaluation.
````

## File: doc/whatsnew/1/1.5.rst
````
**************************
  What's New In Pylint 1.5
**************************

What's New in Pylint 1.5.5?
===========================
Release date: 2016-03-21

* Let visit_importfrom from Python 3 porting checker be called when everything is disabled

  Because the visit method was filtering the patterns it was expecting to be activated,
  it didn't run when everything but one pattern was disabled, leading to spurious false
  positives

  Closes #852

* Don't emit unsubscriptable-value for classes with unknown
  base classes.

  Closes #776.

* Use an OrderedDict for storing the configuration elements

  This fixes an issue related to impredictible order of the disable / enable
  elements from a config file. In certain cases, the disable was coming before
  the enable which resulted in classes of errors to be enabled, even though the intention
  was to disable them. The best example for this was in the context of running multiple
  processes, each one of it having different enables / disables that affected the output.

  Closes #815

* Don't consider bare and broad except handlers as ignoring NameError,
  AttributeError and similar exceptions, in the context of checkers for
  these issues.

  Closes #826


What's New in Pylint 1.5.4?
===========================
Release date: 2016-01-15


* Merge StringMethodChecker with StringFormatChecker. This fixes a
  bug where disabling all the messages and enabling only a handful of
  messages from the StringFormatChecker would have resulted in no
  messages at all.

* Don't apply unneeded-not over sets.


What's New in Pylint 1.5.3?
===========================
Release date: 2016-01-11

* Handle the import fallback idiom with regard to wrong-import-order.

  Closes #750

* Decouple the displaying of reports from the displaying of messages

  Some reporters are aggregating the messages instead of displaying
  them when they are available. The actual displaying was conflatted
  in the generate_reports. Unfortunately this behaviour was flaky
  and in the case of the JSON reporter, the messages weren't shown
  at all if a file had syntax errors or if it was missing.
  In order to fix this, the aggregated messages can now be
  displayed with Reporter.display_message, while the reports are
  displayed with display_reports.

  Closes #766
  Closes #765

* Ignore function calls with variadic arguments without a context.

  Inferring variadic positional arguments and keyword arguments
  will result into empty Tuples and Dicts, which can lead in
  some cases to false positives with regard to no-value-for-parameter.
  In order to avoid this, until we'll have support for call context
  propagation, we're ignoring such cases if detected.

  Closes #722

* Treat AsyncFunctionDef just like FunctionDef nodes,
  by implementing visit_asyncfunctiondef in terms of
  visit_functiondef.

  Closes #767

* Take in account kwonlyargs when verifying that arguments
  are defined with the check_docs extension.

  Closes #745

* Suppress reporting 'unneeded-not' inside ``__ne__`` methods

  Closes #749


What's New in Pylint 1.5.2?
===========================
Release date: 2015-12-21

* Don't crash if graphviz is not installed, instead emit a
  warning letting the user to know.

  Closes #168

* Accept only functions and methods for the deprecated-method checker.

  This prevents a crash which can occur when an object doesn't have
  .qname() method after the inference.

* Don't emit super-on-old-class on classes with unknown bases.

  Closes #721

* Allow statements in ``if`` or ``try`` blocks containing imports.

  Closes #714


What's New in Pylint 1.5.1?
===========================
Release date: 2015-12-02


* Fix a crash which occurred when old visit methods are encountered
  in plugin modules.

  Closes #711

* Add wrong-import-position to check_messages's decorator arguments
  for ImportChecker.leave_module
  This fixes an esoteric bug which occurs when ungrouped-imports and
  wrong-import-order are disabled and pylint is executed on multiple files.
  What happens is that without wrong-import-position in check_messages,
  leave_module will never be called, which means that the first non-import node
  from other files might leak into the current file,
  leading to wrong-import-position being emitted by pylint.

* Fix a crash which occurred when old visit methods are encountered
  in plugin modules.

  Closes #711

* Don't emit import-self and cyclic-import for relative imports
  of modules with the same name as the package itself.

  Closes #708
  Closes #706.


What's New in Pylint 1.5.0?
===========================
Release date: 2015-11-29

* Added multiple warnings related to imports. 'wrong-import-order'
  is emitted when PEP 8 recommendations regarding imports are not
  respected (that is, standard imports should be followed by third-party
  imports and then by local imports). 'ungrouped-imports' is emitted
  when imports from the same package or module are not placed
  together, but scattered around in the code. 'wrong-import-position'
  is emitted when code is mixed with imports, being recommended for the
  latter to be at the top of the file, in order to figure out easier by
  a human reader what dependencies a module has.

  Closes #692

* Added a new refactoring warning, 'unneeded-not', emitted
  when an expression with the not operator could be simplified.

  Closes #670

* Added a new refactoring warning, 'simplifiable-if-statement',
  used when an if statement could be reduced to a boolean evaluation
  of its test.

  Closes #698

* Added a new refactoring warning, 'too-many-boolean-expressions',
  used when an if statement contains too many boolean expressions,
  which makes the code less maintainable and harder to understand.

  Closes #677

* Property methods are shown as attributes instead of functions in
  pyreverse class diagrams.

  Closes #284

* Add a new refactoring error, 'too-many-nested-blocks', which is emitted
  when a function or a method has too many nested blocks, which makes the
  code less readable and harder to understand.

  Closes #668

* Add a new error, 'unsubscriptable-object', that is emitted when
  value used in subscription expression doesn't support subscription
  (i.e. doesn't define __getitem__ method).

* Don't warn about abstract classes instantiated in their own body.

  Closes #627

* Obsolete options are not present by default in the generated
  configuration file.

  Closes #632

* non-iterator-returned can detect classes with iterator-metaclasses.

  Closes #679

* Add a new error, 'unsupported-membership-test', emitted when value
  to the right of the 'in' operator doesn't support membership test
  protocol (i.e. doesn't define __contains__/__iter__/__getitem__)

* Add new errors, 'not-an-iterable', emitted when non-iterable value
  is used in an iterating context (starargs, for-statement,
  comprehensions, etc), and 'not-a-mapping', emitted when non-mapping
  value is used in a mapping context.

  Closes #563

* Make 'no-self-use' checker not emit a warning if there is a 'super()'
  call inside the method.

  Closes #667

* Add checker to identify multiple imports on one line.

  Closes #598

* Fix unused-argument false positive when the "+=" operator is used.

  Closes #518

* Don't emit import-error for ignored modules. PyLint will not emit import
  errors for any import which is, or is a subpackage of, a module in
  the ignored-modules list.

  Closes #223

* Fix unused-import false positive when the import is used in a
  class assignment.

  Closes #475

* Add a new error, 'not-context-manager', emitted when something
  that doesn't implement __enter__ and __exit__ is used in a with
  statement.

* Add a new warning, 'confusing-with-statement', emitted by the
  base checker, when an ambiguous looking with statement is used.
  For example `with open() as first, second` which looks like a
  tuple assignment but is actually 2 context managers.

* Add a new warning, 'duplicate-except', emitted when there is an
  exception handler which handles an exception type that was handled
  before.

  Closes #485

* A couple of warnings got promoted to errors, since they could uncover
  potential bugs in the code. These warnings are: assignment-from-none,
  unbalanced-tuple-unpacking, unpacking-non-sequence, non-iterator-returned.

  Closes #388

* Allow ending a pragma control with a semicolon. In this way, users
  can continue a pragma control with a reason for why it is used,
  as in `# pylint: disable=old-style-class;reason=...`.

  Closes #449

* --jobs can be used with --load-plugins now.

  Closes #456

* Improve the performance of --jobs when dealing only with a package name.

  Closes #479

* Don't emit an unused-wildcard-import when the imported name comes
  from another module and it is in fact a __future__ name.

* The colorized reporter now works on Windows.

  Closes #96.

* Remove pointless-except warning. It was previously disabled by
  default and it wasn't very useful.

  Closes #506.

* Fix a crash on Python 3 related to the string checker, which
  crashed when it encountered a bytes string with a .format
  method called.

* Don't warn about no-self-use for builtin properties.

* Fix a false positive for bad-reversed-sequence, when a subclass
  of a ``dict`` provides a __reversed__ method.

* Change the default no-docstring-rgx so missing-docstring isn't
  emitted for private functions.

* Don't emit redefined-outer-name for __future__ directives.

  Closes #520.

* Provide some hints for the bad-builtin message.

  Closes #522.

* When checking for invalid arguments to a callable, in typecheck.py,
  look up for the __init__ in case the found __new__ comes from builtins.

  Since the __new__ comes from builtins, it will not have attached any
  information regarding what parameters it expects, so the check
  will be useless. Retrieving __init__ in that case will at least
  detect a couple of false negatives.

  Closes #429.

* Don't emit no-member for classes with unknown bases.

  Since we don't know what those bases might add, we simply ignore
  the error in this case.

* Lookup in the implicit metaclass when checking for no-member,
  if the class in question has an implicit metaclass, which is
  True for new style classes.

  Closes #438.

* Add two new warnings, duplicate-bases and inconsistent-mro.

  duplicate-bases is emitted when a class has the same bases
  listed more than once in its bases definition, while inconsistent-mro
  is emitted when no sane mro hierarchy can be determined.

  Closes #526.

* Remove interface-not-implemented warning.

  Closes #532.

* Remove the rest of interface checks: interface-is-not-class,
  missing-interface-method, unresolved-interface. The reason is that
  it's better to start recommending ABCs instead of the old Zope era
  of interfaces. One side effect of this change is that ignore-iface-methods
  becomes a noop, it's deprecated and it will be removed at some time.

* Emit a proper deprecation warning for reporters.BaseReporter.add_message.

  The alternative way is to use handle_message. add_message will be removed in
  Pylint 1.6.

* Added new module 'extensions' for optional checkers with the test
  directory 'test/extensions' and documentation file 'doc/extensions.rst'.

* Added new checker 'extensions.check_docs' that verifies parameter
  documentation in Sphinx, Google, and Numpy style.

* Detect undefined variable cases, where the "definition" of an undefined
  variable was in del statement. Instead of emitting used-before-assignment,
  which is totally misleading, it now emits undefined-variable.

  Closes #528.

* Don't emit attribute-defined-outside-init and access-member-before-definition
  for mixin classes. Actual errors can occur in mixin classes, but this is
  controlled by the ignore-mixin-members option.

  Closes #412.

* Improve the detection of undefined variables and variables used before
  assignment for variables used as default arguments to function,
  where the variable was first defined in the class scope.

  Closes #342 and issue #404.

* Add a new warning, 'unexpected-special-method-signature', which is emitted
  when a special method (dunder method) doesn't have the expected signature,
  which can lead to actual errors in the application code.

  Closes #253.

* Remove 'bad-context-manager' due to the inclusion of 'unexpected-special-method-signature'.

* Don't emit no-name-in-module if the import is guarded by an ImportError, Exception or
  a bare except clause.

* Don't emit no-member if the attribute access node is protected by an
  except handler, which handles AttributeError, Exception or it is a
  bare except.

* Don't emit import-error if the import is guarded by an ImportError, Exception or a
  bare except clause.

* Don't emit undefined-variable if the node is guarded by a NameError, Exception
  or bare except clause.

* Add a new warning, 'using-constant-test', which is emitted when a conditional
  statement (If, IfExp) uses a test which is always constant, such as numbers,
  classes, functions etc. This is most likely an error from the user's part.

  Closes #524.

* Don't emit 'raising-non-exception' when the exception has unknown
  bases. We don't know what those bases actually are and it's better
  to assume that the user knows what he is doing rather than emitting
  a message which can be considered a false positive.

* Look for a .pylintrc configuration file in the current folder,
  if pylintrc is not found. Dotted pylintrc files will not be searched
  in the parents of the current folder, as it is done for pylintrc.

* Add a new error, 'invalid-unary-type-operand', emitted when
  an unary operand is used on something which doesn't support that
  operation (for instance, using the unary bitwise inversion operator
  on an instance which doesn't implement __invert__).

* Take in consideration differences between arguments of various
  type of functions (classmethods, staticmethods, properties)
  when checking for ``arguments-differ``.

  Closes #548.

* astroid.inspector was moved to pylint.pyreverse, since it belongs
  there and it doesn't need to be in astroid.

* astroid.utils.LocalsVisitor was moved to pylint.pyreverse.LocalsVisitor.

* pylint.checkers.utils.excepts_import_error was removed.
  Use pylint.checkers.utils.error_of_type instead.

* Don't emit undefined-all-variables for nodes which can't be
  inferred (YES nodes).

* yield-outside-func is also emitted for ``yield from``.

* Add a new error, 'too-many-star-expressions', emitted when
  there are more than one starred expression (`*x`) in an assignment.
  The warning is emitted only on Python 3.

* Add a new error, 'invalid-star-assignment-target', emitted when
  a starred expression (`*x`) is used as the lhs side of an assignment,
  as in `*x = [1, 2]`. This is not a SyntaxError on Python 3 though.

* Detect a couple of objects which can't be base classes (bool,
  slice, range and memoryview, which weren't detected until now).

* Add a new error for the Python 3 porting checker, ``import-star-module-level``,
  which is used when a star import is detected in another scope than the
  module level, which is an error on Python 3. Using this will emit a
  SyntaxWarning on Python 2.

* Add a new error, 'star-needs-assignment-target', emitted on Python 3 when
  a Starred expression (`*x`) is not used in an assignment target. This is not
  caught when parsing the AST on Python 3, so it needs to be a separate check.

* Add a new error, 'unsupported-binary-operation', emitted when
  two a binary arithmetic operation is executed between two objects
  which don't support it (a number plus a string for instance).
  This is currently disabled, since the it exhibits way too many false
  positives, but it will be re-enabled as soon as possible.

* New imported features from astroid into pyreverse: pyreverse.inspector.Project,
  pyreverse.inspector.project_from_files and pyreverse.inspector.interfaces.

  These were moved since they didn't belong in astroid.

* Enable misplaced-future for Python 3.

  Closes #580.

* Add a new error, 'nonlocal-and-global', which is emitted when a
  name is found to be both nonlocal and global in the same scope.

  Closes #581.

* ignored-classes option can work with qualified names (ignored-classes=optparse.Values)

  Closes #297

* ignored-modules can work with qualified names as well as with Unix pattern
  matching for recursive ignoring.

  Closes #244

* Improve detection of relative imports in non-packages, as well as importing
  missing modules with a relative import from a package.

* Don't emit no-init if not all the bases from a class are known.

  Closes #604.

* --no-space-check option accepts ``empty-line`` as a possible option.

  Closes #541.

* --generate-rcfile generates by default human readable symbols
  for the --disable option.

  Closes #608.

* Improved the not-in-loop checker to properly detect more cases.

* Add a new error, 'continue-in-finally', which is emitted when
  the ``continue`` keyword is found inside a ``finally`` clause, which
  is a SyntaxError.

* The --zope flag is deprecated and it is slated for removal
  in Pylint 1.6.

  The reason behind this removal is the fact that it's a specialized
  flag and there are solutions for the original problem:
  use --generated-members with the members that causes problems
  when using Zope or add AST transforms tailored to the zope
  project.

  At the same time, --include-ids and --symbols will also be removed
  in Pylint 1.6.

  Closes #570.

* missing-module-attribute was removed and the corresponding
  CLI option, required-attributes, which is slated for removal
  in Pylint 1.6.

* missing-reversed-argument was removed.

  The reason behind this is that this kind of errors should be
  detected by the type checker for *all* the builtins and not
  as a special case for the reversed builtin. This will happen
  shortly in the future.

* --comment flag is obsolete and it will be removed in Pylint 1.6.

* --profile flag is obsolete and it will be removed in Pylint 1.6.

* Add a new error, 'misplaced-bare-raise'.

  The error is used when a bare raise is not used inside an except clause.
  This can generate a RuntimeError in Python, if there are no active exceptions
  to be reraised. While it works in Python 2 due to the fact that the exception
  leaks outside of the except block, it's nevertheless a behaviour that
  a user shouldn't depend upon, since it's not obvious to the reader of the code
  what exception will be raised and it will not be compatible with Python 3 anyhow.

  Closes #633.

* Bring logilab-common's ureports into pylint.reporters.

  With this change, we moved away from depending on logilab-common,
  having in Pylint all the components that were used from logilab-common.
  The API should be considered an implementation detail and can change at
  some point in the future.

  Closes #621.

* ``reimported`` is emitted for reimported objects on the same line.

  Closes #639.

* Abbreviations of command line options are not supported anymore.

  Using abbreviations for CLI options was never considered to be
  a feature of pylint, this fact being only a side effect of using optparse.
  As this was the case, using --load-plugin or other abbreviation
  for --load-plugins never actually worked, while it also didn't raise
  an error.

  Closes #424.

* Add a new error, 'nonlocal-without-binding'

  The error is emitted on Python 3 when a nonlocal name is not bound
  to any variable in the parents scopes.

  Closes #582.

* 'deprecated-module' can be shown for modules which aren't
   available.

  Closes #362.

* Don't consider a class abstract if its members can't
  be properly inferred.

  This fixes a false positive related to abstract-class-instantiated.

  Closes #648.

* Add a new checker for the async features added by PEP 492.

* Add a new error, 'yield-inside-async-function', emitted on
  Python 3.5 and upwards when the ``yield`` statement is found inside
  a new coroutine function (PEP 492).

* Add a new error, 'not-async-context-manager', emitted when
  an async context manager block is used with an object which doesn't
  support this protocol (PEP 492).

* Add a new convention warning, 'singleton-comparison', emitted when
  comparison to True, False or None is found.

* Don't emit 'assigning-non-slot' for descriptors.

  Closes #652.

* Add a new error, 'repeated-keyword', when a keyword argument is passed
  multiple times into a function call.

  This is similar with redundant-keyword-arg, but it's mildly different
  that it needs to be a separate error.

* --enable=all can now be used.

  Closes #142.

* Add a new convention message, 'misplaced-comparison-constant',
  emitted when a constant is placed in the left hand side of a comparison,
  as in '5 == func()'. This is also called Yoda condition, since the
  flow of code reminds of the Star Wars green character, conditions usually
  encountered in languages with variabile assignments in conditional
  statements.

* Add a new convention message, 'consider-using-enumerate', which is
  emitted when code that uses ``range`` and ``len`` for iterating is encountered.

  Closes #684.

* Added two new refactoring messages, 'no-classmethod-decorator' and
  'no-staticmethod-decorator', which are emitted when a static method or a class
  method is declared without using decorators syntax.

  Closes #675.
````

## File: doc/whatsnew/1/index.rst
````
1.x
===

.. include:: ../full_changelog_explanation.rst
.. include:: ../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   1.9/index
   1.8/index
   1.7/index
   1.6/index

Ticket numbers are almost can be internal to Logilab, or from bitbucket. In latest
version it's also github issues.

.. toctree::
   :maxdepth: 2

   1.5.rst
   1.4.rst
   1.3.rst
   1.2.rst
   1.1.rst
   1.0.rst
````

## File: doc/whatsnew/2/2.0/full.rst
````
Full changelog
==============

What's New in Pylint 2.0?
-------------------------

Release date: 2018-07-15

* ``try-except-raise`` should not be emitted if there are any parent exception class handlers.

  Closes #2284

* ``trailing-comma-tuple`` can be emitted for ``return`` statements as well.

  Closes #2269

* Fix a false positive ``inconsistent-return-statements`` message when exception is raised
  inside an else statement.

  Closes #1782

* ``ImportFrom`` nodes correctly use the full name for the import sorting checks.

  Closes #2181

* [].extend and similar builtin operations don't emit `dict-*-not-iterating` with the Python 3 porting checker

  Closes #2187

* Add a check ``consider-using-dict-comprehension`` which is emitted if for dict initialization
  the old style with list comprehensions is used.

* Add a check ``consider-using-set-comprehension`` which is emitted if for set initialization
  the old style with list comprehensions is used.

* ``logging-not-lazy`` is emitted whenever pylint infers that a string is built with addition

  Closes #2193

* Add a check ``chained-comparison`` which is emitted if a boolean operation can be simplified
  by chaining some of its operations.
  e.g "a < b and b < c", can be simplified as "a < b < c".

  Closes #2032

* Add a check ``consider-using-in`` for comparisons of a variable against
  multiple values with "==" and "or"s instead of checking if the variable
  is contained "in" a tuple of those values.

* ``in`` is considered iterating context for some of the Python 3 porting checkers

  Closes #2186

* Add ``--ignore-none`` flag to control if pylint should warn about ``no-member`` where the owner is None

* Fix a false positive related to ``too-many-arguments`` and bounded ``__get__`` methods

  Closes #2172

* ``mcs`` as the first parameter of metaclass's ``__new__`` method was replaced by ``cls``

  Closes #2028

* ``assignment-from-no-return`` considers methods as well.

  Closes #2081

* Support typing.TYPE_CHECKING for *unused-import* errors

  Closes #1948

* Inferred classes at a function level no longer emit ``invalid-name``
  when they don't respect the variable regular expression

  Closes #1049

* Added basic support for postponed evaluation of function annotations.

  Closes #2069

* Fix a bug with ``missing-kwoa`` and variadics parameters

  Closes #1111

* ``simplifiable-if-statement`` takes in account only when assigning to same targets

  Closes #1984

* Make ``len-as-condition`` test more cases, such as ``len() < 1`` or ``len <= 0``

* Fix false-positive ``line-too-long`` message emission for
  commented line at the end of a module

  Closes #1950

* Fix false-positive ``bad-continuation`` for with statements

  Closes #461

* Don't warn about ``stop-iteration-return`` when using ``next()`` over ``itertools.count``

  Closes #2158

* Add a check ``consider-using-get`` for unidiomatic usage of value/default-retrieval
  for a key from a dictionary

  Closes #2076

* invalid-slice-index is not emitted when the slice is used as index for a complex object.

  We only use a handful of known objects (list, set and friends) to figure out if
  we should emit invalid-slice-index when the slice is used to subscript an object.

* Don't emit ``unused-import`` anymore for typing imports used in type comments.

* Add a new check 'useless-import-alias'.

  Closes #2052

* Add ``comparison-with-callable`` to warn for comparison with bare callable, without calling it.

  Closes #2082

* Don't warn for ``missing-type-doc`` and/or ``missing-return-type-doc``, if type
  annotations exist on the function signature for a parameter and/or return type.

  Closes #2083

* Add ``--exit-zero`` option for continuous integration scripts to more
  easily call Pylint in environments that abort when a program returns a
  non-zero (error) status code.

  Closes #2042

* Warn if the first argument of an instance/ class method gets assigned

  Closes #977

* New check ``comparison-with-itself`` to check comparison between same value.

  Closes #2051

* Add a new warning, 'logging-fstring-interpolation', emitted when f-string
  is used within logging function calls.

  Closes #1998

* Don't show 'useless-super-delegation' if the subclass method has different type annotations.

  Closes #1923

* Add ``unhashable-dict-key`` check.

  Closes #586

* Don't warn that a global variable is unused if it is defined by an import

  Closes #1453

* Skip wildcard import check for ``__init__.py``.

  Closes #2026

* The Python 3 porting mode can now run with Python 3 as well.

* ``too-few-public-methods`` is not emitted for dataclasses.

  Closes #1793

* New verbose mode option, enabled with ``--verbose`` command line flag, to
  display of extra non-checker-related output. It is disabled by default.

  Closes #1863

* ``undefined-loop-variable`` takes in consideration non-empty iterred objects before emitting

  Closes #2039

* Add support for numpydoc optional return value names.

  Closes #2030

* ``singleton-comparison`` accounts for negative checks

  Closes #2037

* Add a check ``consider-using-in`` for comparisons of a variable against
  multiple values with "==" and "or"s instead of checking if the variable
  is contained "in" a tuple of those values.

  Closes #1977

* defaultdict and subclasses of dict are now handled for dict-iter-* checks

  Closes #2005

* ``logging-format-interpolation`` also emits when f-strings are used instead of % syntax.

  Closes #1788

* Don't trigger misplaced-bare-raise when the raise is in a finally clause

  Closes #1924

* Add a new check, ``possibly-unused-variable``.

  This is similar to ``unused-variable``, the only difference is that it is
  emitted when we detect a locals() call in the scope of the unused variable.
  The ``locals()`` call could potentially use the said variable, by consuming
  all values that are present up to the point of the call. This new check
  allows to disable this error when the user intentionally uses ``locals()``
  to consume everything.

  Closes #1909.

* ``no-else-return`` accounts for multiple cases

   The check was a bit overrestrictive because we were checking for
   return nodes in the .orelse node. At that point though the if statement
   can be refactored to not have the orelse. This improves the detection of
   other cases, for instance it now detects TryExcept nodes that are part of
   the .else branch.

  Closes #1852

* Added two new checks, ``invalid-envvar-value`` and ``invalid-envvar-default``.

  The former is trigger whenever pylint detects that environment variable manipulation
  functions uses a different type than strings, while the latter is emitted whenever
  the said functions are using a default variable of different type than expected.

* Add a check ``consider-using-join`` for concatenation of strings using str.join(sequence)

  Closes #1952

* Add a check ``consider-swap-variables`` for swapping variables with tuple unpacking

  Closes #1922

* Add new checker ``try-except-raise`` that warns the user if an except handler block
  has a ``raise`` statement as its first operator. The warning is shown when there is
  a bare raise statement, effectively re-raising the exception that was caught or the
  type of the exception being raised is the same as the one being handled.

* Don't crash on invalid strings when checking for ``logging-format-interpolation``

  Closes #1944

* Exempt ``__doc__`` from triggering a ``redefined-builtin``

  ``__doc__`` can be used to specify a docstring for a module without
  passing it as a first-statement string.

* Fix false positive bad-whitespace from function arguments with default
  values and annotations

  Closes #1831

* Fix stop-iteration-return false positive when next builtin has a
  default value in a generator

  Closes #1830

* Fix emission of false positive ``no-member`` message for class with  "private" attributes whose name is mangled.

  Closes #1643

* Fixed a crash which occurred when ``Uninferable`` wasn't properly handled in ``stop-iteration-return``

  Closes #1779

* Use the proper node to get the name for redefined functions (#1792)

  Closes #1774

* Don't crash when encountering bare raises while checking inconsistent returns

  Closes #1773

* Fix a false positive ``inconsistent-return-statements`` message when if statement is inside try/except.

  Closes #1770

* Fix a false positive ``inconsistent-return-statements`` message when while loop are used.

  Closes #1772

* Correct column number for whitespace conventions.

  Previously the column was stuck at 0

  Closes #1649

* Fix ``unused-argument`` false positives with overshadowed variable in
  dictionary comprehension.

  Closes #1731

* Fix false positive ``inconsistent-return-statements`` message when never
  returning functions are used (i.e sys.exit for example).

  Closes #1771

* Fix error when checking if function is exception, as in ``bad-exception-context``.

* Fix false positive ``inconsistent-return-statements`` message when a
  function is defined under an if statement.

  Closes #1794

* New ``useless-return`` message when function or method ends with a "return" or
  "return None" statement and this is the only return statement in the body.

* Fix false positive ``inconsistent-return-statements`` message by
  avoiding useless exception inference if the exception is not handled.

  Closes #1794 (second part)

* Fix bad thread instantiation check when target function is provided in args.

  Closes #1840

* Fixed false positive when a numpy Attributes section follows a Parameters
  section

  Closes #1867

* Fix incorrect file path when file absolute path contains multiple ``path_strip_prefix`` strings.

  Closes #1120

* Fix false positive undefined-variable for lambda argument in class definitions

  Closes #1824

* Add of a new checker that warns the user if some messages are enabled or disabled
  by id instead of symbol.

  Closes #1599

* Suppress false-positive ``not-callable`` messages from certain
  staticmethod descriptors

  Closes #1699

* Fix indentation handling with tabs

  Closes #1148

* Fix false-positive ``bad-continuation`` error

  Closes #638

* Fix false positive unused-variable in lambda default arguments

  Closes #1921
  Closes #1552
  Closes #1099
  Closes #210

* Updated the default report format to include paths that can be clicked on in some terminals (e.g. iTerm).

* Fix inline def behavior with ``too-many-statements`` checker

  Closes #1978

* Fix ``KeyError`` raised when using docparams and NotImplementedError is documented.

  Closes #2102

* Fix 'method-hidden' raised when assigning to a property or data descriptor.

* Fix emitting ``useless-super-delegation`` when changing the default value of keyword arguments.

  Closes #2022

* Expand ignored-argument-names include starred arguments and keyword arguments

  Closes #2214

* Fix false-positive undefined-variable in nested lambda

  Closes #760

* Fix false-positive ``bad-whitespace`` message for typing annoatations
  with ellipses in them

  Close 1992

* Broke down "missing-docstrings" between "module", "class" and "function"

  For this to work we had to make multiple messages with the same old name
  possible.

  Closes #1164
````

## File: doc/whatsnew/2/2.0/index.rst
````
**************************
  What's New In Pylint 2.0
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.0/summary.rst
````
:Release: 2.0
:Date: 2018-07-15

Summary -- Release highlights
=============================

* Dropped support for Python 2. This release will work only on Python 3.4+.

  If you need to use ``pylint`` with Python 2, you can use Pylint 1.9+. We'll continue
  to do bug releases until 2020, when Python 2 goes officially EOL.
  ``pylint`` will gain the ability to analyze Python 2 files, but some checks might not work
  as they will assume that their running environment is Python 2.

* Given the dropping of Python 2, the Python 3 porting mode (enabled via ``--py3k``) can now
  also run with Python 3.

  The porting mode used to be a no-op on Python 3, but most of the messages can now be emitted
  when the running interpreter is Python 3. The only messages that won't be emitted are those that
  rely on a particular syntax specific to Python 2, for instance ``print`` as a statement.


New checkers
============
* A new check was added, ``useless-object-inheritance``.

  This refactoring message is emitted when pylint detects that a class inherits from object,
  which is redundant as in Python 3, every class implicitly inherits from object.

  .. code-block:: python

    class A(object):
        pass

    class A:    # better
        pass

* A new check was added, ``comparison-with-callable``.

  This refactoring message is emitted when pylint detects that a comparison with a callable was
  made, which might suggest that some parenthesis were omitted, resulting in potential unwanted
  behaviour.

  .. code-block:: python

    def foo():
        return None

    def goo():
        return None

    if foo == 786:  # bad
        pass

    if foo() == 786:    # good
        pass

* A new check was added, ``chained-comparison``.

  This refactoring message is emitted if a boolean operation can be simplified by chaining some
  of its operations. check below example:

  .. code-block:: python

    if a < b and b < c:
        pass

    if a < b < c:   # better
        pass

* A new check was added, ``useless-import-alias``.

  This refactoring message is emitted when an import alias does not rename the original package.

  .. code-block:: python

    import numpy as numpy # bad
    import numpy as np # good
    from collection import OrderedDict as OrderedDict # bad
    from collection import OrderedDict as ordered_dict # good

* A new check was added, ``comparison-with-itself``.

  This refactoring message is emitted when a variable is compared against itself.

  .. code-block:: python

    if variable == variable:  # bad
        pass

* A new check was added, ``consider-using-in``.

  This refactoring message is emitted when a variable is compared against multiple
  values concatenated by ors instead of using the faster, more idiomatic "in" check.

  .. code-block:: python

    if variable == 1 or variable == 2 or variable == 3:  # bad
        pass

    if variable in (1, 2, 3):  # good
        pass

* A new check was added, ``consider-using-get``.

  This refactoring message is emitted when manually checking if a key is in a dictionary
  and getting its value if it is (and optionally a default if not)
  instead of the more idiomatic dict.get.

  .. code-block:: python

    if 'key' in dictionary:  # bad
        variable = dictionary['key']
    else:
        variable = 'default'

    variable = dictionary.get('key', 'default')  # good

* A new check was added, ``consider-using-join``.

  This refactoring message is emitted when using a for loop over an iterable to join strings
  instead of the faster, less memory consuming and more idiomatic str.join(sequence).

  .. code-block:: python

    result = ''  # bad
    for number in ['1', '2', '3']:
        result += number

    result = ''.join(['1', '2', '3'])  # good

* New ``useless-return`` message when function or method ends with a "return" or
  "return None" statement and this is the only return statement in the body.

* New ``use-symbolic-message-instead`` message when a message is activated or
  deactivated by id instead of symbol.
  The use of symbol is more explicit and easier to remind.

* A new check was added, ``consider-swap-variables``.

  This refactoring message is emitted when using a temporary variable in order
  to swap the values of two variables instead of the shorter, more idiomatic
  approach with tuple-unpacking.

  Instead of a temporary variable, the one-line syntax with commas should be used.

  See this `style guide`_ document or the Pycon 2007 `swap values presentation` for details.

  .. code-block:: python

     temp = a  # the wrong way
     a = b
     b = temp

     a, b = b, a  # the right way

* Two new checks, ``invalid-envvar-value`` and ``invalid-envvar-default``, were added.

  The former is trigger whenever pylint detects that environment variable manipulation
  functions uses a different type than strings, while the latter is emitted whenever
  the said functions are using a default variable of different type than expected.

* A new check was added, ``subprocess-popen-preexec-fn``,

  This refactoring message is emitted when using the keyword argument preexec_fn
  when creating subprocess.Popen instances which may be unsafe when used in
  the presence of threads.

  See `subprocess.Popen <https://docs.python.org/3/library/subprocess.html#popen-constructor>`_
  for full warning details.

* New ``try-except-raise`` message when an except handler block has a bare
  ``raise`` statement as its first operator or the exception type being raised
  is the same as the one being handled.

*  New ``possibly-unused-variable`` check added.

  This is similar to ``unused-variable``, the only difference is that it is
  emitted when we detect a locals() call in the scope of the unused variable.
  The ``locals()`` call could potentially use the said variable, by consuming
  all values that are present up to the point of the call. This new check
  allows to disable this error when the user intentionally uses ``locals()``
  to consume everything.

  For instance, the following code will now trigger this new error:

  .. code-block:: python

     def func():
         some_value = some_call()
         return locals()

* New ``unhashable-dict-key`` check added to detect dict lookups using
  unhashable keys such as lists or dicts.

* New ``self-cls-assignment`` warning check added.

  This is warning if the first argument of an instance/ class method gets
  assigned

  .. code-block:: python

     class Foo(object):
         def foo(self, bar):
             self = bar

* New verbose mode option ``--verbose`` to display of extra non-checker-related output. Disabled by default.

* Two new checks were added for recommending dict and set comprehensions where possible.

  These two checks are going to flag the following examples:

  .. code-block:: python

     dict([(k, v) for (k, v) in ...]) # better as {k: v for k, v in ...}
     set([k for k in ...]) # better as {k for k in ...}

Other Changes
=============

* A couple of performance improvements brought to ``astroid`` should make
  ``pylint`` should be a bit faster as well.

  We added a new flag, ``max_inferable_values`` on ``astroid.MANAGER`` for
  limiting the maximum amount of values that ``astroid`` can infer when inferring
  values. This change should improve the performance when dealing with large frameworks
  such as ``django``.
  You can also control this behaviour with ``pylint --limit-inference-results``

  We also rewrote how ``nodes_of_class`` and ``get_children`` methods operate which
  should result in a performance boost for a couple of checks.

* Fix a false positive ``inconsistent-return-statements`` message when exception is raised inside
  an else statement.

* Don't warn for ``missing-type-doc`` and/or ``missing-return-type-doc``, if type annotations
  exist on the function signature for a parameter and/or return type.

* Fix a false positive ``inconsistent-return-statements`` message when if
  statement is inside try/except.

* Fix a false positive ``inconsistent-return-statements`` message when
  ``while`` loop are used.

* Fix emission of false positive ``no-member`` message for class with
  "private" attributes whose name is mangled.

* Fix ``unused-argument`` false positives with overshadowed variable in dictionary comprehension.

* Fixing false positive ``inconsistent-return-statements`` when
  never returning functions are used (i.e such as sys.exit).

* Fix false positive ``inconsistent-return-statements`` message when a
  function is defined under an if statement.

* Fix false positive ``inconsistent-return-statements`` message by
  avoiding useless exception inference if the exception is not handled.

* Fix false positive ``undefined-variable`` for lambda argument in class definitions

* Suppress false-positive ``not-callable`` messages from certain staticmethod descriptors

* Expand ``ignored-argument-names`` include starred arguments and keyword arguments

* ``singleton-comparison`` will suggest better boolean conditions for negative conditions.

* ``undefined-loop-variable`` takes in consideration non-empty iterred objects before emitting.

  For instance, if the loop iterable is not empty, this check will no longer be emitted.

* Enum classes no longer trigger ``too-few-methods``

* Special methods now count towards ``too-few-methods``,
  and are considered part of the public API.
  They are still not counted towards the number of methods for
  ``too-many-methods``.

* ``docparams`` extension allows abstract methods to document returns
  documentation even if the default implementation does not return something.
  They also no longer need to document raising a ``NotImplementedError.``

* Skip wildcard import check for ``__init__.py``.

* Don't warn 'useless-super-delegation' if the subclass method has different type annotations.

* Don't warn that a global variable is unused if it is defined by an import

  .. code-block:: python

    def func():
        global sys
        import sys

* Added basic support for postponed evaluation of function annotations.

  If ``pylint`` detects the corresponding ``from __future__ import annotations`` import,
  it will not emit ``used-before-assignment`` and ``undefined-variable`` in the cases
  triggered by the annotations.

  More details on the postponed evaluation of annotations can be read in
  `PEP 563`_.

* A new command line option was added, ``--exit-zero``, for the use of continuous integration
  scripts which abort if a command returns a non-zero status code.  If the
  option is specified, and Pylint runs successfully, it will exit with 0
  regardless of the number of lint issues detected.

  Configuration errors, parse errors, and calling Pylint with invalid
  command-line options all still return a non-zero error code, even if
  ``--exit-zero`` is specified.

* Don't emit ``unused-import`` anymore for typing imports used in type comments. For instance,
  in the following example pylint used to complain that ``Any`` and ``List`` are not used,
  while they should be considered used by a type checker.

  .. code-block:: python

      from typing import Any, List
      a = 1 # type: List[Any]

* Fix false positive ``line-too-long`` for commented lines at the end of module

* Fix emitting ``useless-super-delegation`` when changing the default value of keyword arguments.

* Support ``typing.TYPE_CHECKING`` for *unused-import* errors

  When modules are imported under ``typing.TYPE_CHECKING`` guard, ``pylint``
  will no longer emit *unused-import*.

* Fix false positive ``unused-variable`` in lambda default arguments

* ``assignment-from-no-return`` considers methods as well as functions.

  If you have a method that doesn't return a value, but later on you assign
  a value to a function call to that method (so basically it will be ``None``),
  then ``pylint`` is going to emit an ``assignment-from-no-return`` error.

* A new flag was added, ``--ignore-none`` which controls the ``no-member``
  behaviour with respect to ``None`` values.

  Previously ``pylint`` was not emitting ``no-member`` if it inferred that
  the owner of an attribute access is a ``None`` value. In some cases,
  this might actually cause bugs, so if you want to check for ``None`` values
  as well, pass ``--ignore-none=n`` to pylint.

* Fix false-positive ``bad-continuation`` for with statements

* Fix false-positive ``bad-whitespace`` message for typing annoatations
  with ellipses in them

* Fix false-positive ``undefined-variable`` for nested lambdas


.. _PEP 563: https://peps.python.org/pep-0563/
.. _style guide: https://docs.python-guide.org/writing/style/
````

## File: doc/whatsnew/2/2.1/full.rst
````
Full changelog
==============

What's New in Pylint 2.1.1?
---------------------------
Release date: 2018-08-07

* fix pylint crash due to ``misplaced-format-function`` not correctly handling class attribute.

  Closes #2384

* Do not emit \*-builtin for Python 3 builtin checks when the builtin is used inside a try-except

  Closes #2228

* ``simplifiable-if-statement`` not emitted when dealing with subscripts


What's New in Pylint 2.1?
-------------------------

Release date: 2018-08-01

* ``trailing-comma-tuple`` gets emitted for ``yield`` statements as well.

  Closes #2363

* Get only the arguments of the scope function for ``redefined-argument-from-local``

  Closes #2364

* Add a check ``misplaced-format-function`` which is emitted if format function is used on
  non str object.

  Closes #2200

* ``chain.from_iterable`` no longer emits `dict-{}-not-iterating` when dealing with dict values and keys

* Demote the ``try-except-raise`` message from an error to a warning (E0705 -> W0706)

  Closes #2323

* Correctly handle the new name of the Python implementation of the ``abc`` module.

  Closes pylint-dev/astroid#2288

* Modules with ``__getattr__`` are exempted by default from ``no-member``

  There's no easy way to figure out if a module has a particular member when
  the said module uses ``__getattr__``, which is a new addition to Python 3.7.
  Instead we assume the safe thing to do, in the same way we do for classes,
  and skip those modules from checking.

  Closes #2331

* Fix a false positive ``invalid name`` message when method or attribute name is longer then 30 characters.

  Closes #2047

* Include the type of the next branch in ``no-else-return``

  Closes #2295

* Fix inconsistent behaviour for bad-continuation on first line of file

  Closes #2281

 * Fix not being able to disable certain messages on the last line through
   the global disable option

  Closes #2278

* Don't emit ``useless-return`` when we have a single statement that is the return itself

  We still want to be explicit when a function is supposed to return
  an optional value; even though ``pass`` could still work, it's not explicit
  enough and the function might look like it's missing an implementation.

  Closes #2300

* Fix false-positive undefined-variable for self referential class name in lamdbas

  Closes #704

* Don't crash when ``pylint`` is unable to infer the value of an argument to ``next()``

  Closes #2316

* Don't emit ``not-an-iterable`` when dealing with async iterators.

  But do emit it when using the usual iteration protocol against
  async iterators.

  Closes #2311

* Can specify a default docstring type for when the check cannot guess the type

  Closes #1169
````

## File: doc/whatsnew/2/2.1/index.rst
````
**************************
  What's New In Pylint 2.1
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.1/summary.rst
````
:Release: 2.1
:Date: 2018-08-01

Summary -- Release highlights
=============================

* This release mostly includes fixes for bugs found after the launch of 2.0.

New checkers
============

* A new check was added, ``misplaced-format-function``.

  This message is emitted when pylint detects that a format function is called on non str object.
  This can occur due to wrong placement of closing bracket, e.g

  .. code-block:: python

    print('value: {}').format(123) # bad

    print('value: {}'.format(123)) # good


Other Changes
=============

* ``try-except-raise`` check was demoted from an error to a warning, as part of issue #2323.

* Correctly handle the new name of the Python implementation of the ``abc`` module.

  In Python 3.7, the ``abc`` module has both a C implementation as well as a Python one,
  but the Python implementation has a different file name that what ``pylint`` was expecting,
  resulting in some checks getting confused.

* Modules with ``__getattr__`` are exempted by default from ``no-member``

  There's no easy way to figure out if a module has a particular member when
  the said module uses ``__getattr__``, which is a new addition to Python 3.7.
  Instead we assume the safe thing to do, in the same way we do for classes,
  and skip those modules from checking.


* ``invalid name`` is no longer triggered for function and attribute names longer
  than 30 characters. The upper limit was removed completely.


* Fix false-positive ``undefined-variable`` for self referential class name in lamdbas

* ``no-else-return`` also specifies the type of the branch that is causing the error.

* Fixed inconsistent behaviour for bad-continuation on first line of file.

* Fixed a bug where ``pylint`` was not able to disable certain messages on the last line through
  the global disable option.

* ``pylint`` no longer emits ``useless-return`` when it finds a single statement that is the ``return`` itself

  We still want to be explicit when a function is supposed to return
  an optional value; even though ``pass`` could still work, it's not explicit
  enough and the function might look like it's missing an implementation.

* Fixed a bug where ``pylint`` was crashing when being unable to infer the value of an argument to ``next()``


* ``pylint`` no longer emit ``not-an-iterable`` when dealing with async iterators.

* ``pylint`` gained the ability to specify a default docstring type for when the check cannot guess the type

  For this we added a ``--default-docstring-type`` command line option.
````

## File: doc/whatsnew/2/2.10/full.rst
````
Full changelog
==============

What's New in Pylint 2.10.2?
----------------------------
Release date: 2021-08-21

* We now use platformdirs instead of appdirs since the latter is not maintained.

  Closes #4886

* Fix a crash in the checker raising ``shallow-copy-environ`` when failing to infer
  on ``copy.copy``

  Closes #4891



What's New in Pylint 2.10.1?
----------------------------
Release date: 2021-08-20

* pylint does not crash when PYLINT_HOME does not exist.

  Closes #4883


What's New in Pylint 2.10.0?
----------------------------
Release date: 2021-08-20

* pyreverse: add option to produce colored output.

  Closes #4488

* pyreverse: add output in PlantUML format.

  Closes #4498

* ``consider-using-with`` is no longer triggered if a context manager is returned from a function.

  Closes #4748

* pylint does not crash with a traceback anymore when a file is problematic. It
  creates a template text file for opening an issue on the bug tracker instead.
  The linting can go on for other non problematic files instead of being impossible.

* pyreverse: Show class has-a relationships inferred from the type-hint

  Closes #4744

* Fixed a crash when importing beyond the top level package during ``import-error``
  message creation

  Closes #4775

* Added ``ignored-parents`` option to the design checker to ignore specific
  classes from the ``too-many-ancestors`` check (R0901).

  Fixes part of #3057

* Added ``unspecified-encoding``: Emitted when open() is called without specifying an encoding

  Closes #3826

* Improved the Similarity checker performance. Fix issue with ``--min-similarity-lines`` used with ``--jobs``.

  Closes #4120
  Closes #4118

* Don't emit ``no-member`` error if guarded behind if statement.

  Refs #1162
  Closes #1990
  Closes #4168

* The default for ``PYLINTHOME`` is now the standard ``XDG_CACHE_HOME``, and pylint now uses ``appdirs``.

  Closes #3878

* Added ``use-list-literal``: Emitted when ``list()`` is called with no arguments instead of using ``[]``

  Closes #4365

* Added ``use-dict-literal``: Emitted when ``dict()`` is called with no arguments instead of using ``{}``

  Closes #4365

* Added optional extension ``consider-ternary-expression``: Emitted whenever a variable is assigned in both branches of an if/else block.

  Closes # 4366

* Added optional extension ``while-used``: Emitted whenever a ``while`` loop is used.

  Closes # 4367

* Added ``forgotten-debug-statement``: Emitted when ``breakpoint``, ``pdb.set_trace`` or ``sys.breakpointhook`` calls are found

  Closes #3692

* Fix false-positive of ``unused-private-member`` when using nested functions in a class

  Closes #4673

* Fix crash for ``unused-private-member`` that occurred with nested attributes.

  Closes #4755

* Fix a false positive for ``unused-private-member`` with class names

  Closes #4681

* Fix false positives for ``superfluous-parens`` with walrus operator, ternary operator and inside list comprehension.

  Closes #2818
  Closes #3249
  Closes #3608
  Closes #4346

* Added ``format-string-without-interpolation`` checker: Emitted when formatting is applied to a string without any variables to be replaced

  Closes #4042

* Refactor of ``--list-msgs`` & ``--list-msgs-enabled``: both options now show whether messages are emittable with the current interpreter.

  Closes #4778

* Fix false negative for ``used-before-assignment`` when the variable is assigned
  in an exception handler, but used outside of the handler.

  Closes #626

* Added ``disable-next`` option: allows using `# pylint: disable-next=msgid` to disable a message for the following line

  Closes #1682

* Added ``redundant-u-string-prefix`` checker: Emitted when the u prefix is added to a string

  Closes #4102

* Fixed ``cell-var-from-loop`` checker: handle cell variables in comprehensions within functions,
  and function default argument expressions. Also handle basic variable shadowing.

  Closes #2846
  Closes #3107

* Fixed bug with ``cell-var-from-loop`` checker: it no longer has false negatives when
  both ``unused-variable`` and ``used-before-assignment`` are disabled.

* Fix false positive for ``invalid-all-format`` if the list or tuple builtin functions are used

  Closes #4711

* Config files can now contain environment variables

  Closes #3839

* Fix false-positive ``used-before-assignment`` with an assignment expression in a ``Return`` node

  Closes #4828

* Added ``use-sequence-for-iteration``: Emitted when iterating over an in-place defined ``set``.

* ``CodeStyleChecker``

  * Limit ``consider-using-tuple`` to be emitted only for in-place defined ``lists``.

  * Emit ``consider-using-tuple`` even if list contains a ``starred`` expression.

* Ignore decorators lines by similarities checker when ignore signatures flag enabled

  Closes #4839

* Allow ``true`` and ``false`` values in ``pylintrc`` for better compatibility with ``toml`` config.

* Class methods' signatures are ignored the same way as functions' with similarities "ignore-signatures" option enabled

  Closes #4653

* Improve performance when inferring ``Call`` nodes, by utilizing caching.

* Improve error message for invalid-metaclass when the node is an Instance.
````

## File: doc/whatsnew/2/2.10/index.rst
````
***************************
  What's New In Pylint 2.10
***************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.10/summary.rst
````
:Release: 2.10
:Date: 2021-08-20

Summary -- Release highlights
=============================

In 2.10, we added several new default check, like ``unspecified-encoding``, ``forgotten-debug-statement`` or
``use-dict-literal``. There's also a few opinionated optional one. You can now forbid while loop or
profess your exclusive love of ternary expressions publicly. We promise you hours of arguing fun with
your whole team if you add those to your configuration.

We've also fixed some long standing bugs, false positives, or missing options like ``ignore-signature`` that
will now work on inner function's signatures.

A new option to disable the next line, ``disable-next``, has been added. It's also possible to export
colored diagrams, and plantuml diagram using pyreverse. ``PYLINT_HOME`` is now ``XDG_CACHE_HOME`` if not set.

The performance of the similarity checker has been improved, as well as several small performance fixes.

We're going to continue working on improving performance during 2.11. We're also going to finalize
a new ``possible-forgotten-f-prefix`` check that had too much false positives at release time.
Check the `possible-forgotten-f-prefix`_ issue if you want to provide knowledge or use case :)

.. _possible-forgotten-f-prefix: https://github.com/pylint-dev/pylint/pull/4787

New checkers
============

* Added ``unspecified-encoding``: Emitted when open() is called without specifying an encoding

  Closes #3826

* Added ``use-list-literal``: Emitted when ``list()`` is called with no arguments instead of using ``[]``

  Closes #4365

* Added ``use-dict-literal``: Emitted when ``dict()`` is called with no arguments instead of using ``{}``

  Closes #4365

* Added ``forgotten-debug-statement``: Emitted when ``breakpoint``, ``pdb.set_trace`` or ``sys.breakpointhook`` calls are found

  Closes #3692

* Added ``use-sequence-for-iteration``: Emitted when iterating over an in-place defined ``set``.


* Added ``format-string-without-interpolation`` checker: Emitted when formatting is applied to a string without any variables to be replaced

  Closes #4042

* Added ``redundant-u-string-prefix`` checker: Emitted when the u prefix is added to a string

  Closes #4102

Extensions
==========

* ``CodeStyleChecker``

  * Limit ``consider-using-tuple`` to be emitted only for in-place defined ``lists``.

  * Emit ``consider-using-tuple`` even if list contains a ``starred`` expression.

* Added optional extension ``consider-ternary-expression``: Emitted whenever a variable is assigned in both branches of an if/else block.

  Closes # 4366

* Added optional extension ``while-used``: Emitted whenever a ``while`` loop is used.

  Closes # 4367

Other Changes
=============

* pyreverse now permit to produce colored generated diagram by using the ``colorized`` option.

* Pyreverse - add output in PlantUML format

* ``consider-using-with`` is no longer triggered if a context manager is returned from a function.

* pylint does not crash with a traceback anymore when a file is problematic. It
  creates a template text file for opening an issue on the bug tracker instead.
  The linting can go on for other non problematic files instead of being impossible.

* Pyreverse - Show class has-a relationships inferred from type-hints

* Performance of the Similarity checker has been improved.

* Added ``time.clock`` to deprecated functions/methods for python 3.3

* Added ``ignored-parents`` option to the design checker to ignore specific
  classes from the ``too-many-ancestors`` check (R0901).

* Don't emit ``no-member`` error if guarded behind if statement.

  Refs #1162
  Closes #1990
  Closes #4168

* Fix false positives for ``superfluous-parens`` with walrus operator, ternary operator and inside list comprehension.

  Closes #2818
  Closes #3249
  Closes #3608
  Closes #4346

* Refactor of ``--list-msgs`` & ``--list-msgs-enabled``: both options now show whether messages are emittable with the current interpreter.

  Closes #4778

* Fix false negative for ``used-before-assignment`` when the variable is assigned
  in an exception handler, but used outside of the handler.

  Closes #626

* Added ``disable-next`` option: allows using `# pylint: disable-next=msgid` to disable a message for the following line

  Closes #1682

* Fixed ``cell-var-from-loop`` checker: handle cell variables in comprehensions within functions,
  and function default argument expressions. Also handle basic variable shadowing.

  Closes #2846
  Closes #3107

* Fixed bug with ``cell-var-from-loop`` checker: it no longer has false negatives when
  both ``unused-variable`` and ``used-before-assignment`` are disabled.

* Class methods' signatures are now ignored the same way as functions' with similarities "ignore-signatures" option enabled

  Closes #4653
````

## File: doc/whatsnew/2/2.11/full.rst
````
Full changelog
==============

What's New in Pylint 2.11.1?
----------------------------
Release date: 2021-09-16

* ``unspecified-encoding`` now checks the encoding of ``pathlib.Path()`` correctly

  Closes #5017


What's New in Pylint 2.11.0?
----------------------------
Release date: 2021-09-16

* The python3 porting mode checker and its ``py3k`` option were removed. You can still find it in older pylint
  versions.

* ``raising-bad-type`` is now properly emitted when  raising a string

* Added new extension ``SetMembershipChecker`` with ``use-set-for-membership`` check:
  Emitted when using an in-place defined ``list`` or ``tuple`` to do a membership test. ``sets`` are better optimized for that.

  Closes #4776

* Added ``py-version`` config key (if ``[MASTER]`` section). Used for version dependent checks.
  Will default to whatever Python version pylint is executed with.

* ``CodeStyleChecker``: Added ``consider-using-assignment-expr``: Emitted when an assignment is directly followed by an if statement
  and both can be combined by using an assignment expression ``:=``. Requires Python 3.8

  Closes #4862

* Added ``consider-using-f-string``: Emitted when .format() or '%' is being used to format a string.

  Closes #3592

* Fix false positive for ``consider-using-with`` if a context manager is assigned to a
  variable in different paths of control flow (e. g. if-else clause).

  Closes #4751

* https is now preferred in the documentation and http://pylint.pycqa.org correctly redirect to https://pylint.pycqa.org

  Closes #3802

* Fix false positive for ``function-redefined`` for simple type annotations

  Closes #4936

* Fix false positive for ``protected-access`` if a protected member is used in type hints of function definitions

* Fix false positive ``dict-iter-missing-items`` for dictionaries only using tuples as keys

  Closes #3282

* The ``unspecified-encoding`` checker now also checks calls to ``pathlib.Path().read_text()``
  and ``pathlib.Path().write_text()``

  Closes #4945

* Fix false positive ``superfluous-parens`` for tuples created with inner tuples

  Closes #4907

* Fix false positive ``unused-private-member`` for accessing attributes in a class using ``cls``

  Closes #4849

* Fix false positive ``unused-private-member`` for private staticmethods accessed in classmethods.

  Closes #4849

* Extended ``consider-using-in`` check to work for attribute access.

* Setting ``min-similarity-lines`` to 0 now makes the similarty checker stop checking for duplicate code

  Closes #4901

* Fix a bug where pylint complained if the cache's parent directory does not exist

  Closes #4900

* The ``global-variable-not-assigned`` checker now catches global variables that are never reassigned in a
  local scope and catches (reassigned) functions

  Closes #1375
  Closes #330

* Fix false positives for invalid-all-format that are lists or tuples at runtime

  Closes #4711

* Fix ``no-self-use`` and ``docparams extension`` for async functions and methods.

* Add documentation for ``pyreverse`` and ``symilar``

  Closes #4616

* Non symbolic messages with the wrong capitalisation now correctly trigger ``use-symbolic-message-instead``

  Closes #5000

* The ``consider-iterating-dictionary`` checker now also considers membership checks

  Closes #4069

* The ``invalid-name`` message is now more detailed when using multiple naming style regexes.
````

## File: doc/whatsnew/2/2.11/index.rst
````
***************************
 What's New in Pylint 2.11
***************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.11/summary.rst
````
:Release: 2.11
:Date: 2021-09-16

Summary -- Release highlights
=============================

In 2.11, we added a new default checker to advise using f-string as it's
the most efficient way of formatting strings right now. You can use
`pyupgrade`_, `ruff`_ or `flynt`_ to migrate your old ``%`` and ``format()`` automatically.

We added a new extension ``SetMembershipChecker`` that will advise the
use of set for membership test, as it's more performant than lists or tuples.
The ``CodeStyleChecker`` also got some love, check it out if you're not already
using it.

We fixed some long standing bugs, false positives, or false negatives and
we added small quality of life options like ``min-similarity-lines`` that
disable the duplication check when set to 0.

Under the hood the code for both pylint and astroid is progressively more typed,
which could be helpful to you if you're using them as libraries. In order for
this new typing to make more sense and stay simple, we deprecated some functions
or type that will be removed in the next major version. This is an ongoing effort.

The future ``possible-forgotten-f-prefix`` check still had too much false positives,
and is delayed again. Check the `possible-forgotten-f-prefix`_ issue if you want
to provide knowledge or use case :)

.. _possible-forgotten-f-prefix: https://github.com/pylint-dev/pylint/pull/4787
.. _pyupgrade: https://github.com/asottile/pyupgrade
.. _flynt: https://github.com/ikamensh/flynt
.. _ruff: https://docs.astral.sh/ruff/

New checkers
============

* Added ``consider-using-f-string``: Emitted when .format() or '%' is being used to format a string.

  Closes #3592

Removed checkers
================

* The python3 porting mode checker and its ``py3k`` option were removed. You can still find it in older pylint
  versions.

Extensions
==========

* Added new extension ``SetMembershipChecker`` with ``use-set-for-membership`` check:
  Emitted when using an in-place defined ``list`` or ``tuple`` to do a membership test. ``sets`` are better optimized for that.

  Closes #4776

CodeStyleChecker
----------------

* Added ``consider-using-assignment-expr``: Emitted when an assignment is directly followed by an if statement
  and both can be combined by using an assignment expression ``:=``. Requires Python 3.8

  Closes #4862


Other Changes
=============

* Added ``py-version`` config key (if ``[MAIN]`` section). Used for version dependent checks.
  Will default to whatever Python version pylint is executed with.

* The ``invalid-name`` message is now more detailed when using multiple naming style regexes.

* Fix false positive for ``consider-using-with`` if a context manager is assigned to a
  variable in different paths of control flow (e. g. if-else clause).

  Closes #4751

* Fix false positive for ``function-redefined`` for simple type annotations

  Closes #4936

* Fix false positive for ``protected-access`` if a protected member is used in type hints of function definitions

* Fix false positive ``dict-iter-missing-items`` for dictionaries only using tuples as keys

  Closes #3282

* The ``unspecified-encoding`` checker now also checks calls to ``pathlib.Path().read_text()``
  and ``pathlib.Path().write_text()``

  Closes #4945

* Fix false positive ``superfluous-parens`` for tuples created with inner tuples

  Closes #4907

* Fix false positive ``unused-private-member`` for accessing attributes in a class using ``cls``

  Closes #4849

* Extended ``consider-using-in`` check to work for attribute access.

* Setting ``min-similarity-lines`` to 0 now makes the similarty checker stop checking for duplicate code

  Closes #4901

* Fix a bug where pylint complained if the cache's parent directory does not exist

  Closes #4900

* The ``global-variable-not-assigned`` checker now catches global variables that are never reassigned in a
  local scope and catches (reassigned) functions

  Closes #1375
  Closes #330

* The ``consider-iterating-dictionary`` checker now also considers membership checks

  Closes #4069
````

## File: doc/whatsnew/2/2.12/full.rst
````
Full changelog
==============

What's New in Pylint 2.12.2?
----------------------------
Release date: 2021-11-25

* Fixed a false positive for ``unused-import`` where everything
  was not analyzed properly inside typing guards.

* Fixed a false-positive regression for ``used-before-assignment`` for
  typed variables in the body of class methods that reference the same class

  Closes #5342

* Specified that the ``ignore-paths`` option considers "\" to represent a
  windows directory delimiter instead of a regular expression escape
  character.

* Fixed a crash with the ``ignore-paths`` option when invoking the option
  via the command line.

  Closes #5437

* Fixed handling of Sphinx-style parameter docstrings with asterisks. These
  should be escaped with by prepending a "\".

  Closes #5406

* Add ``endLine`` and ``endColumn`` keys to output of ``JSONReporter``.

  Closes #5380

* Fixed handling of Google-style parameter specifications where descriptions
  are on the line following the parameter name. These were generating
  false positives for ``missing-param-doc``.

  Closes #5452

* Fix false negative for ``consider-iterating-dictionary`` during membership checks encapsulated in iterables
  or ``not in`` checks

  Closes #5323

* ``unused-import`` now check all ancestors for typing guards

  Closes #5316


What's New in Pylint 2.12.1?
----------------------------
Release date: 2021-11-25

* Require Python ``3.6.2`` to run pylint.

  Closes #5065


What's New in Pylint 2.12.0?
----------------------------
Release date: 2021-11-24

* Upgrade astroid to 2.9.0

  Closes #4982

* Add ability to add ``end_line`` and ``end_column`` to the ``--msg-template`` option.
  With the standard ``TextReporter`` this will add the line and column number of the
  end of a node to the output of Pylint. If these numbers are unknown, they are represented
  by an empty string.

* Introduced primer tests and a configuration tests framework. The helper classes available in
  ``pylint/testutil/`` are still unstable and might be modified in the near future.

  Closes #4412 #5287

* Fix ``install graphiz`` message which isn't needed for puml output format.

* ``MessageTest`` of the unittest ``testutil`` now requires the ``confidence`` attribute
  to match the expected value. If none is provided it is set to ``UNDEFINED``.

* ``add_message`` of the unittest ``testutil`` now actually handles the ``col_offset`` parameter
  and allows it to be checked against actual output in a test.

* Fix a crash in the ``check_elif`` extensions where an undetected if in a comprehension
  with an if statement within an f-string resulted in an out of range error. The checker no
  longer relies on counting if statements anymore and uses known if statements locations instead.
  It should not crash on badly parsed if statements anymore.

* Fix ``simplify-boolean-expression`` when condition can be inferred as False.

  Closes #5200

* Fix exception when pyreverse parses ``property function`` of a class.

* The functional ``testutils`` now accept ``end_lineno`` and ``end_column``. Expected
  output files without these will trigger a ``DeprecationWarning``. Expected output files
  can be easily updated with the ``python tests/test_functional.py --update-functional-output`` command.

* The functional ``testutils`` now correctly check the distinction between ``HIGH`` and
  ``UNDEFINED`` confidence. Expected output files without defined ``confidence`` levels will now
  trigger a ``DeprecationWarning``. Expected output files can be easily updated with the
  ``python tests/test_functional.py --update-functional-output`` command.

* The functional test runner now supports the option ``min_pyver_end_position`` to control on which python
  versions the ``end_lineno`` and ``end_column`` attributes should be checked. The default value is 3.8.

* Fix ``accept-no-yields-doc`` and ``accept-no-return-doc`` not allowing missing ``yield`` or
  ``return`` documentation when a docstring is partially correct

  Closes #5223

* Add an optional extension ``consider-using-any-or-all`` : Emitted when a ``for`` loop only
  produces a boolean and could be replaced by ``any`` or ``all`` using a generator. Also suggests
  a suitable any or all statement.

  Closes #5008

* Properly identify parameters with no documentation and add new message called ``missing-any-param-doc``

  Closes #3799

* Add checkers ``overridden-final-method`` & ``subclassed-final-class``

  Closes #3197

* Fixed ``protected-access`` for accessing of attributes and methods of inner classes

  Closes #3066

* Added support for ``ModuleNotFoundError`` (``import-error`` and ``no-name-in-module``).
  ``ModuleNotFoundError`` inherits from ``ImportError`` and was added in Python ``3.6``

* ``undefined-variable`` now correctly flags variables which only receive a type annotations
  and never get assigned a value

  Closes #5140

* ``undefined-variable`` now correctly considers the line numbering and order of classes
  used in metaclass declarations

  Closes #4031

* ``used-before-assignment`` now correctly considers references to classes as type annotation
  or default values in first-level methods

  Closes #3771

* ``undefined-variable`` and ``unused-variable`` now correctly trigger for assignment expressions
  in functions defaults

  Refs #3688

* ``undefined-variable`` now correctly triggers for assignment expressions in if ... else statements
  This includes a basic form of control flow inference for if ... else statements using
  constant boolean values

  Closes #3688

* Added the ``--enable-all-extensions`` command line option. It will load all available extensions
  which can be listed by running ``--list-extensions``

* Fix bug with importing namespace packages with relative imports

  Closes #2967 and #5131

* Improve and flatten ``unused-wildcard-import`` message

  Closes #3859

* In length checker, ``len-as-condition`` has been renamed as
  ``use-implicit-booleaness-not-len`` in order to be consistent with
  ``use-implicit-booleaness-not-comparison``.

* Created new ``UnsupportedVersionChecker`` checker class that includes checks for features
  not supported by all versions indicated by a ``py-version``.

  * Added ``using-f-string-in-unsupported-version`` checker. Issued when ``py-version``
    is set to a version that does not support f-strings (< 3.6)

* Fix ``useless-super-delegation`` false positive when default keyword argument is a variable.

* Properly emit ``duplicate-key`` when Enum members are duplicate dictionary keys

  Closes #5150

* Use ``py-version`` setting for alternative union syntax check (PEP 604),
  instead of the Python interpreter version.

* Subclasses of ``dict`` are regarded as reversible by the ``bad-reversed-sequence`` checker
  (Python 3.8 onwards).

  Closes #4981

* Support configuring mixin class pattern via ``mixin-class-rgx``

* Added new checker ``use-implicit-booleaness-not-comparison``: Emitted when
  collection literal comparison is being used to check for emptiness.

  Closes #4774

* ``missing-param-doc`` now correctly parses asterisks for variable length and
  keyword parameters

  Closes #3733

* ``missing-param-doc`` now correctly handles Numpy parameter documentation without
  explicit typing

  Closes #5222

* ``pylint`` no longer crashes when checking assignment expressions within if-statements

  Closes #5178

* Update ``literal-comparison``` checker to ignore tuple literals

  Closes #3031

* Normalize the input to the ``ignore-paths`` option to allow both Posix and
  Windows paths

  Closes #5194

* Fix double emitting of ``not-callable`` on inferable ``properties``

  Closes #4426

* ``self-cls-assignment`` now also considers tuple assignment

* Fix ``missing-function-docstring`` not being able to check ``__init__`` and other
  magic methods even if the ``no-docstring-rgx`` setting was set to do so

* Added ``using-final-decorator-in-unsupported-version`` checker. Issued when ``py-version``
  is set to a version that does not support ``typing.final`` (< 3.8)

* Added configuration option ``exclude-too-few-public-methods`` to allow excluding
  classes from the ``min-public-methods`` checker.

  Closes #3370

* The ``--jobs`` parameter now fallbacks to 1 if the host operating system does not
  have functioning shared semaphore implementation.

  Closes #5216

* Fix crash for ``unused-private-member`` when checking private members on ``__class__``

  Closes #5261

* Crashes when a list is encountered in a toml configuration do not happen anymore.

  Closes #4580

* Moved ``misplaced-comparison-constant`` to its own extension ``comparison_placement``.
  This checker was opinionated and now no longer a default. It can be reactived by adding
  ``pylint.extensions.comparison_placement`` to ``load-plugins`` in your config.

  Closes #1064

* A new ``bad-configuration-section`` checker was added that will emit for misplaced option
  in pylint's top level namespace for toml configuration. Top-level dictionaries or option defined
  in the wrong section will still silently not be taken into account, which is tracked in a
  follow-up issue.

  Follow-up in #5259

* Fix crash for ``protected-access`` on (outer) class traversal

* Added new checker ``useless-with-lock`` to find incorrect usage of with statement and threading module locks.
  Emitted when ``with threading.Lock():`` is used instead of ``with lock_instance:``.

  Closes #5208

* Make yn validator case insensitive, to allow for ``True`` and ``False`` in config files.

* Fix crash on ``open()`` calls when the ``mode`` argument is not a simple string.

  Fixes part of #5321

* Inheriting from a class that implements ``__class_getitem__`` no longer raises ``inherit-non-class``.

* Pyreverse - Add the project root directory to sys.path

  Closes #2479

* Don't emit ``consider-using-f-string`` if ``py-version`` is set to Python < ``3.6``.
  ``f-strings`` were added in Python ``3.6``

  Closes #5019

* Fix regression for ``unspecified-encoding`` with ``pathlib.Path.read_text()``

  Closes #5029

* Don't emit ``consider-using-f-string`` if the variables to be interpolated include a backslash

* Fixed false positive for ``cell-var-from-loop`` when variable is used as the default
  value for a keyword-only parameter.

  Closes #5012

* Fix false-positive ``undefined-variable`` with ``Lambda``, ``IfExp``, and
  assignment expression.

* Fix false-positive ``useless-suppression`` for ``wrong-import-order``

  Closes #2366

* Fixed ``toml`` dependency issue

  Closes #5066

* Fix false-positive ``useless-suppression`` for ``line-too-long``

  Closes #4212

* Fixed ``invalid-name`` not checking parameters of overwritten base ``object`` methods

  Closes #3614

* Fixed crash in ``consider-using-f-string`` if ``format`` is not called

  Closes #5058

* Fix crash with ``AssignAttr`` in ``if TYPE_CHECKING`` blocks.

  Closes #5111

* Improve node information for ``invalid-name`` on function argument.

* Prevent return type checkers being called on functions with ellipses as body

  Closes #4736

* Add ``is_sys_guard`` and ``is_typing_guard`` helper functions from astroid
  to ``pylint.checkers.utils``.

* Fix regression on ClassDef inference

  Closes #5030
  Closes #5036

* Fix regression on Compare node inference

  Closes #5048

* Fix false-positive ``isinstance-second-argument-not-valid-type`` with ``typing.Callable``.

  Closes #3507
  Closes #5087

* It is now recommended to do ``pylint`` development on ``Python`` 3.8 or higher. This
  allows using the latest ``ast`` parser.

* All standard jobs in the ``pylint`` CI now run on ``Python`` 3.8 by default. We still
  support python 3.6 and 3.7 and run tests for those interpreters.

* ``TypingChecker``

  * Fix false-negative for ``deprecated-typing-alias`` and ``consider-using-alias``
    with ``typing.Type`` + ``typing.Callable``.
````

## File: doc/whatsnew/2/2.12/index.rst
````
***************************
 What's New in Pylint 2.12
***************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.12/summary.rst
````
:Release: 2.12
:Date: 2021-11-24

Summary -- Release highlights
=============================

In 2.12, we introduced a new option ``py-version`` that permits to analyse code for a python
version that may differ from your current python interpreter. This does not affect all checkers but
permits, for example, to check for python 3.5 code smells (using f-string's) while using pylint with python 3.6.
The minimum version to run pylint is now 3.6.2, while the last working version for python 3.6.0
and 3.6.1 was pylint 2.9.3.

On top of fixing a lot of false positives and bugs, we also added new default checks, like
``use-implicit-booleaness-not-comparison``, ``overridden-final-method``, and ``useless-with-lock``.
There's also better check for TOML configurations.

Lastly, in addition to the information we already had about start line and start column,
we introduced new information about the end line and end column of messages. This
will permit to have more precise visual clue in IDE like in pylint for vs-code. The default
will stay the same to not break compatibility but it can be retrieved by adding ``end_line``
and ``end_column`` to the ``--msg-template`` option. For better result stick to python 3.8+.

The checker for Yoda conditions is now an extension, you might want to enable it if you were
relying on this check. There's also a new extension checker, ``consider-using-any-or-all`` that
detects for loops that could be replaced by any or all, entirely contributed by @areveny,
welcome to the team !

New checkers
============

* Added ``missing-any-param-doc`` triggered when a function has neither parameter nor parameter type
  documentation. Undocumented parameters are now being properly identified. A warning might start to
  appear unexpectedly if ``missing-param-doc`` and ``missing-type-doc`` were disabled, as a new message
  ``missing-any-param-doc`` will be emitted instead.

  Closes #3799

typing.final
------------

* Added ``overridden-final-method``: Emitted when a method which is annotated with ``typing.final`` is overridden

* Added ``subclassed-final-class``: Emitted when a class which is annotated with ``typing.final`` is subclassed

  Closes #3197

* Created new ``UnsupportedVersionChecker`` checker class that includes checks for features
  not supported by all versions indicated by a ``py-version``.

  * Added ``using-f-string-in-unsupported-version`` checker. Issued when ``py-version``
    is set to a version that does not support f-strings (< 3.6)

* Added new checker ``use-implicit-booleaness-not-comparison``: Emitted when
  collection literal comparison is being used to check for emptiness.

  Closes #4774

* Added ``using-final-decorator-in-unsupported-version`` checker. Issued when ``py-version``
  is set to a version that does not support typing.final (< 3.8)

* Added new checker ``useless-with-lock`` to find incorrect usage of with statement and threading module locks.
  Emitted when ``with threading.Lock():`` is used instead of ``with lock_instance:``.

  Closes #5208

* A new ``bad-configuration-section`` checker was added that will emit for misplaced option
  in pylint's top level namespace for toml configuration. Top-level dictionaries or option defined
  in the wrong section will still silently not be taken into account, which is tracked in a
  follow-up issue.

  Follow-up in #5259

* ``MessageTest`` of the unittest ``testutil`` now requires the ``confidence`` attribute
  to match the expected value. If none is provided it is set to ``UNDEFINED``.

* ``add_message`` of the unittest ``testutil`` now actually handles the ``col_offset`` parameter
  and allows it to be checked against actual output in a test.

Extensions
==========

* Added an optional extension ``consider-using-any-or-all``: Emitted when a ``for`` loop only
  produces a boolean and could be replaced by ``any`` or ``all`` using a generator. Also suggests
  a suitable any/all statement if it is concise.

  Closes #5008

* Moved ``misplaced-comparison-constant`` to its own extension ``comparison_placement``.
  This checker was opinionated and now no longer a default. It can be reactived by adding
  ``pylint.extensions.comparison_placement`` to ``load-plugins`` in your config.

  Closes #1064

Other Changes
=============

* Fix ``install graphiz`` message which isn't needed for puml output format.

* ``pylint`` no longer crashes when checking assignment expressions within if-statements

  Closes #5178

* Added configuration option ``exclude-too-few-public-methods`` to allow excluding
  classes from the ``min-public-methods`` checker.

  Closes #3370

* Fix ``accept-no-yields-doc`` and ``accept-no-return-doc`` not allowing missing ``yield`` or
  ``return`` documentation when a docstring is partially correct

  Closes #5223

* Fix ``simplify-boolean-expression`` when condition can be inferred as False.

  Closes #5200

* Fix exception when pyreverse parses ``property function`` of a class.

* Improve and flatten ``unused-wildcard-import`` message

  Closes #3859

* In length checker, ``len-as-condition`` has been renamed as
  ``use-implicit-booleaness-not-len`` in order to be consistent with
  ``use-implicit-booleaness-not-comparison``.

* Fixed ``protected-access`` for accessing of attributes and methods of inner classes

  Closes #3066

* Update ``literal-comparison``` checker to ignore tuple literals

  Closes #3031

* The functional ``testutils`` now accept ``end_lineno`` and ``end_column``. Expected
  output files without these will trigger a ``DeprecationWarning``. Expected output files
  can be easily updated with the ``python tests/test_functional.py --update-functional-output`` command.

* The functional ``testutils`` now correctly check the distinction between ``HIGH`` and
  ``UNDEFINED`` confidence. Expected output files without defined ``confidence`` levels will now
  trigger a ``DeprecationWarning``. Expected output files can be easily updated with the
  ``python tests/test_functional.py --update-functional-output`` command.

* The functional test runner now supports the option ``min_pyver_end_position`` to control on which python
  versions the ``end_lineno`` and ``end_column`` attributes should be checked. The default value is 3.8.

* ``undefined-variable`` now correctly flags variables which only receive a type annotations
  and never get assigned a value

  Closes #5140

* ``undefined-variable`` now correctly considers the line numbering and order of classes
  used in metaclass declarations

  Closes #4031

* ``used-before-assignment`` now correctly considers references to classes as type annotation
  or default values in first-level methods

  Closes #3771

* ``undefined-variable`` and ``unused-variable`` now correctly trigger for assignment expressions
  in functions defaults

  Refs #3688

* ``self-cls-assignment`` now also considers tuple assignment

* ``undefined-variable`` now correctly triggers for assignment expressions in if ... else statements
  This includes a basic form of control flow inference for if ... else statements using
  constant boolean values

  Closes #3688

* Fix crash for ``unused-private-member`` when checking private members on ``__class__``

  Closes #5261

* Fix double emitting of ``not-callable`` on inferable ``properties``

  Closes #4426

* Support configuring mixin class pattern via ``mixin-class-rgx``

* Normalize the input to the ``ignore-paths`` option to allow both Posix and
  Windows paths

  Closes #5194

* ``missing-param-doc`` now correctly parses asterisks for variable length and
  keyword parameters

  Closes #3733

* ``missing-param-doc`` now correctly handles Numpy parameter documentation without
  explicit typing

  Closes #5222

* The ``--jobs`` parameter now falls back to 1 if the host operating system does not
  have functioning shared semaphore implementation.

  Closes #5216

* Crashes when a list is encountered in a toml configuration do not happen anymore.

  Closes #4580

* Fix crash for ``protected-access`` on (outer) class traversal

* Fix ``useless-super-delegation`` false positive when default keyword argument is a variable.

* Make yn validator case insensitive, to allow for ``True`` and ``False`` in config files.

* The last version compatible with python '3.6.0' and '3.6.1' is pylint '2.9.3'. We did not
  realize that when adding incompatible typing at the time, and all versions since are broken
  for this interpreter. 2.12.0 meta-information will permit to download pylint on those
  interpreters but the installation will fail and tell you to install '2.9.3' instead.
  pylint 2.12.1 will require python >= 3.6.2.

  Closes #5171
  Follow-up in #5065

* Added the ``--enable-all-extensions`` command line option. It will load all available extensions
  which can be listed by running ``--list-extensions``

* It is now recommended to do ``pylint`` development on ``Python`` 3.8 or higher. This
  allows using the latest ``ast`` parser.

* All standard jobs in the ``pylint`` CI now run on ``Python`` 3.8 by default. We still
  support python 3.6 and 3.7 and run tests for those interpreters.

* Fix crash on ``open()`` calls when the ``mode`` argument is not a simple string.

  Fixes part of #5321

* Add ability to add ``end_line`` and ``end_column`` to the ``--msg-template`` option.
  With the standard ``TextReporter`` this will add the line and column number of the
  end of a node to the output of Pylint. If these numbers are unknown, they are represented
  by an empty string.

* Introduced primer tests and a configuration tests framework. The helper classes available in
  ``pylint/testutil/`` are still unstable and might be modified in the near future.

  Closes #4412 #5287

* Add ``endLine`` and ``endColumn`` keys to output of ``JSONReporter``.

  Closes #5380

* Fix false negative for ``consider-iterating-dictionary`` during membership checks encapsulated in iterables
  or ``not in`` checks

  Closes #5323
````

## File: doc/whatsnew/2/2.13/full.rst
````
Full changelog
==============

What's New in Pylint 2.13.9?
----------------------------
Release date: 2022-05-13


* Respect ignore configuration options with ``--recursive=y``.

  Closes #6471

* Fix false positives for ``no-name-in-module`` and ``import-error`` for ``numpy.distutils`` and ``pydantic``.

  Closes #6497

* Fix ``IndexError`` crash in ``uninferable_final_decorators`` method.

  Refs #6531

* Fix a crash in ``unnecessary-dict-index-lookup`` when subscripting an attribute.

  Closes #6557

* Fix a crash when accessing ``__code__`` and assigning it to a variable.

  Closes #6539

* Fix a false positive for ``undefined-loop-variable`` when using ``enumerate()``.

  Closes #6593


What's New in Pylint 2.13.8?
----------------------------
Release date: 2022-05-02

* Fix a false positive for ``undefined-loop-variable`` for a variable used in a lambda
  inside the first of multiple loops.

  Closes #6419

* Fix a crash when linting a file that passes an integer ``mode=`` to
  ``open``

  Closes #6414

* Avoid reporting ``superfluous-parens`` on expressions using the ``is not`` operator.

  Closes #5930

* Fix a false positive for ``undefined-loop-variable`` when the ``else`` of a ``for``
  loop raises or returns.

  Closes #5971

* Fix false positive for ``unused-variable`` for classes inside functions
  and where a metaclass is provided via a call.

  Closes #4020

* Fix false positive for ``unsubscriptable-object`` in Python 3.8 and below for
  statements guarded by ``if TYPE_CHECKING``.

  Closes #3979


What's New in Pylint 2.13.7?
----------------------------
Release date: 2022-04-20

* Fix a crash caused by using the new config from 2.14.0 in 2.13.x code.

  Closes #6408


What's New in Pylint 2.13.6?
----------------------------
Release date: 2022-04-20

* Fix a crash in the ``unsupported-membership-test`` checker when assigning
  multiple constants to class attributes including ``__iter__`` via unpacking.

  Closes #6366

* Asterisks are no longer required in Sphinx and Google style parameter documentation
  for ``missing-param-doc`` and are parsed correctly.

  Closes #5815
  Closes #5406

* Fixed a false positive for ``unused-variable`` when a builtin specified in
  ``--additional-builtins`` is given a type annotation.

  Closes #6388

* Fixed an ``AstroidError`` in 2.13.0 raised by the ``duplicate-code`` checker with
  ``ignore-imports`` or ``ignore-signatures`` enabled.

  Closes #6301


What's New in Pylint 2.13.5?
----------------------------
Release date: 2022-04-06

* Fix false positive regression in 2.13.0 for ``used-before-assignment`` for
  homonyms between variable assignments in try/except blocks and variables in
  subscripts in comprehensions.

  Closes #6069
  Closes #6136

* ``lru-cache-decorating-method`` has been renamed to ``cache-max-size-none`` and
  will only be emitted when ``maxsize`` is ``None``.

  Closes #6180

* Fix false positive for ``unused-import`` when disabling both ``used-before-assignment`` and ``undefined-variable``.

  Closes #6089

* Narrow the scope of the ``unnecessary-ellipsis`` checker to:
  * functions & classes which contain both a docstring and an ellipsis.
  * A body which contains an ellipsis ``nodes.Expr`` node & at least one other statement.

* Fix false positive for ``used-before-assignment`` for assignments taking place via
  nonlocal declarations after an earlier type annotation.

  Closes #5394

* Fix crash for ``redefined-slots-in-subclass`` when the type of the slot is not a const or a string.

  Closes #6100

* Only raise ``not-callable`` when all the inferred values of a property are not callable.

  Closes #5931


* Fix a false negative for ``subclassed-final-class`` when a set of other messages were disabled.


What's New in Pylint 2.13.4?
----------------------------
Release date: 2022-03-31

* Fix false positive regression in 2.13.0 for ``used-before-assignment`` for
  homonyms between variable assignments in try/except blocks and variables in
  a comprehension's filter.

  Closes #6035

* Include ``testing_pylintrc`` in source and wheel distributions.

  Closes #6028

* Fix crash in ``super-init-not-called`` checker when using ``ctypes.Union``.

  Closes #6027


* Fix crash for ``unnecessary-ellipsis`` checker when an ellipsis is used inside of a container or a lambda expression.

  Closes #6036
  Closes #6037
  Closes #6048


What's New in Pylint 2.13.3?
----------------------------
Release date: 2022-03-29

* Fix false positive for ``unnecessary-ellipsis`` when using an ellipsis as a default argument.

  Closes #5973

* Fix crash involving unbalanced tuple unpacking.

  Closes #5998

* Fix false positive for 'nonexistent-operator' when repeated '-' are
  separated (e.g. by parens).

  Closes #5769


What's New in Pylint 2.13.2?
----------------------------
Release date: 2022-03-27

* Fix crash when subclassing a ``namedtuple``.

  Closes #5982

* Fix false positive for ``superfluous-parens`` for patterns like
  "return (a or b) in iterable".

  Closes #5803

* Fix a false negative regression in 2.13.0 where ``protected-access`` was not
  raised on functions.

  Closes #5989

* Better error messages in case of crash if pylint can't write the issue template.

  Refs #5987


What's New in Pylint 2.13.1?
----------------------------
Release date: 2022-03-26

* Fix a regression in 2.13.0 where ``used-before-assignment`` was emitted for
  the usage of a nonlocal in a try block.

  Closes #5965

* Avoid emitting ``raising-bad-type`` when there is inference ambiguity on
  the variable being raised.

  Closes #2793

* Loosen TypeVar default name pattern a bit to allow names with multiple uppercase
  characters. E.g. ``HVACModeT`` or ``IPAddressT``.

  Closes #5981

* Fixed false positive for ``unused-argument`` when a ``nonlocal`` name is used
  in a nested function that is returned without being called by its parent.

  Closes #5187

* Fix program crash for ``modified_iterating-list/set/dict`` when the list/dict/set
  being iterated through is a function call.

  Closes #5969

* Don't emit ``broken-noreturn`` and ``broken-collections-callable`` errors
  inside ``if TYPE_CHECKING`` blocks.


What's New in Pylint 2.13.0?
----------------------------
Release date: 2022-03-24

* Add missing dunder methods to ``unexpected-special-method-signature`` check.

* No longer emit ``no-member`` in for loops that reference ``self`` if the binary operation that
  started the for loop uses a ``self`` that is encapsulated in tuples or lists.

  Refs pylint-dev/astroid#1360
  Closes #4826

* Output better error message if unsupported file formats are used with ``pyreverse``.

  Closes #5950

* Fix pyreverse diagrams type hinting for classmethods and staticmethods.

* Fix pyreverse diagrams type hinting for methods returning None.

* Fix matching ``--notes`` options that end in a non-word character.

  Closes #5840

* Updated the position of messages for class and function definitions to no longer cover
  the complete definition. Only the ``def`` or ``class`` + the name of the class/function
  are covered.

  Closes #5466

* ``using-f-string-in-unsupported-version`` and ``using-final-decorator-in-unsupported-version`` msgids
    were renamed from ``W1601`` and ``W1602`` to ``W2601`` and ``W2602``. Disabling using these msgids will break.
    This is done in order to restore consistency with the already existing msgids for ``apply-builtin`` and
    ``basestring-builtin`` from the now deleted python 3K+ checker. There is now a check that we're not using
    existing msgids or symbols from deleted checkers.

  Closes #5729

* The line numbering for messages related to function arguments is now more accurate. This can
  require some message disables to be relocated to updated positions.

* Add ``--recursive`` option to allow recursive discovery of all modules and packages in subtree. Running pylint with
  ``--recursive=y`` option will check all discovered ``.py`` files and packages found inside subtree of directory provided
  as parameter to pylint.

  Closes #352

* Add ``modified-iterating-list``, ``modified-iterating-dict`` and ``modified-iterating-set``,
  emitted when items are added to or removed from respectively a list, dictionary or
  set being iterated through.

  Closes #5348

* Fix false-negative for ``assignment-from-none`` checker using list.sort() method.

  Closes #5722

* New extension ``import-private-name``: indicate imports of external private packages
  and objects (prefixed with ``_``). It can be loaded using ``load-plugins=pylint.extensions.private_import``.

  Closes #5463

* Fixed crash from ``arguments-differ`` and ``arguments-renamed`` when methods were
  defined outside the top level of a class.

  Closes #5648

* Removed the deprecated ``check_docs`` extension. You can use the ``docparams`` checker
  to get the checks previously included in ``check_docs``.

  Closes #5322

* Added a ``testutil`` extra require to the packaging, as ``gitpython`` should not be a dependency
  all the time but is still required to use the primer helper code in ``pylint.testutil``. You can
  install it with ``pip install pylint[testutil]``.

  Closes #5486

* Reinstated checks from the python3 checker that are still useful for python 3
  (``eq-without-hash``). This is now in the ``pylint.extensions.eq_without_hash`` optional
  extension.

  Closes #5025

* Fixed an issue where ``ungrouped-imports`` could not be disabled without raising
  ``useless-suppression``.

  Refs #2366

* Added several checkers to deal with unicode security issues
  (see `Trojan Sources <https://trojansource.codes/>`_ and
  `PEP 672 <https://peps.python.org/pep-0672/>`_ for details) that also
  concern the readability of the code. In detail the following checks were added:

  * ``bad-file-encoding`` checks that the file is encoded in UTF-8 as suggested by
    `PEP8 <https://peps.python.org/pep-0008/#source-file-encoding>`_.
    UTF-16 and UTF-32 are `not supported by Python <https://bugs.python.org/issue1503789>`_
    at the moment. If this ever changes
    ``invalid-unicode-codec`` checks that they aren't used, to allow for backwards
    compatibility.

  * ``bidirectional-unicode`` checks for bidirectional unicode characters that
    could make code execution different than what the user expects.

  * ``invalid-character-backspace``, ``invalid-character-carriage-return``,
    ``invalid-character-sub``, ``invalid-character-esc``,
    ``invalid-character-zero-width-space`` and ``invalid-character-nul``
    to check for possibly harmful unescaped characters.

  Closes #5281

* Use the ``tomli`` package instead of ``toml`` to parse ``.toml`` files.

  Closes #5885

* Fix false positive - Allow unpacking of ``self`` in a subclass of ``typing.NamedTuple``.

  Closes #5312

* Fixed false negative ``unpacking-non-sequence`` when value is an empty list.

  Closes #5707

* Better warning messages for useless else or elif when a function returns early.

  Closes #5614

* Fixed false positive ``consider-using-dict-comprehension`` when creating a dict
  using a list of tuples where key AND value vary depending on the same condition.

  Closes #5588

* Fixed false positive for ``global-variable-undefined`` when ``global`` is used with a class name

  Closes #3088

* Fixed false positive for ``unused-variable`` when a ``nonlocal`` name is assigned as part of a multi-name assignment.

  Closes #3781

* Fixed a crash in ``unspecified-encoding`` checker when providing ``None``
  to the ``mode`` argument of an ``open()`` call.

  Closes #5731

* Fixed a crash involving a ``NewType`` named with an f-string.

  Closes #5770
  Ref pylint-dev/astroid#1400

* Improved ``bad-open-mode`` message when providing ``None`` to the ``mode``
  argument of an ``open()`` call.

  Closes #5733

* Added ``lru-cache-decorating-method`` checker with checks for the use of ``functools.lru_cache``
  on class methods. This is unrecommended as it creates memory leaks by never letting the instance
  getting garbage collected.

  Closes #5670

* Fixed crash with recursion error for inference of class attributes that referenced
  the class itself.

  Closes #5408
  Ref pylint-dev/astroid#1392

* Fixed false positive for ``unused-argument`` when a method overridden in a subclass
  does nothing with the value of a keyword-only argument.

  Closes #5771
  Ref pylint-dev/astroid#1382

* The issue template for crashes is now created for crashes which were previously not covered
  by this mechanism.

  Closes #5668

* Rewrote checker for ``non-ascii-name``.
   It now ensures __all__ Python names are ASCII and also properly
   checks the names of imports (``non-ascii-module-import``) as
   well as file names (``non-ascii-file-name``) and emits their respective new warnings.

   Non ASCII characters could be homoglyphs (look alike characters) and hard to
   enter on a non specialized keyboard.
   See `Confusable Characters in PEP 672`_

* When run in parallel mode ``pylint`` now pickles the data passed to subprocesses with
  the ``dill`` package. The ``dill`` package has therefore been added as a dependency.

* An astroid issue where symlinks were not being taken into account
  was fixed

  Closes #1470
  Closes #3499
  Closes #4302
  Closes #4798
  Closes #5081

* Fix a crash in ``unused-private-member`` checker when analyzing code using
  ``type(self)`` in bound methods.

  Closes #5569

* Optimize parsing of long lines when ``missing-final-newline`` is enabled.

  Closes #5724

* Fix false positives for ``used-before-assignment`` from using named
  expressions in a ternary operator test and using that expression as
  a call argument.

  Closes #5177, #5212

* Fix false positive for ``undefined-variable`` when ``namedtuple`` class
  attributes are used as return annotations.

  Closes #5568

* Fix false negative for ``undefined-variable`` and related variable messages
  when the same undefined variable is used as a type annotation and is
  accessed multiple times, or is used as a default argument to a function.

  Closes #5399

* Pyreverse - add output in mermaidjs format

* Emit ``used-before-assignment`` instead of ``undefined-variable`` when attempting
  to access unused type annotations.

  Closes #5713

* Added confidence level ``CONTROL_FLOW`` for warnings relying on assumptions
  about control flow.

* ``used-before-assignment`` now considers that assignments in a try block
  may not have occurred when the except or finally blocks are executed.

  Closes #85, #2615

* Fixed false negative for ``used-before-assignment`` when a conditional
  or context manager intervened before the try statement that suggested
  it might fail.

  Closes #4045

* Fixed false negative for ``used-before-assignment`` in finally blocks
  if an except handler did not define the assignment that might have failed
  in the try block.

* Fixed extremely long processing of long lines with comma's.

  Closes #5483

* Fixed crash on properties and inherited class methods when comparing them for
  equality against an empty dict.

  Closes #5646

* Fixed a false positive for ``assigning-non-slot`` when the slotted class
  defined ``__setattr__``.

  Closes #3793

* Fixed a false positive for ``invalid-class-object`` when the object
  being assigned to the ``__class__`` attribute is uninferable.

* Fixed false positive for ``used-before-assignment`` with self-referential type
  annotation in conditional statements within class methods.

  Closes #5499

* Add checker ``redefined-slots-in-subclass``: Emitted when a slot is redefined in a subclass.

  Closes #5617

* Fixed false positive for ``global-variable-not-assigned`` when the ``del`` statement is used

  Closes #5333

* By default, pylint does no longer take files starting with ``.#`` into account. Those are
  considered ``Emacs file locks``. See
  https://www.gnu.org/software/emacs/manual/html_node/elisp/File-Locks.html.
  This behavior can be reverted by redefining the ``ignore-patterns`` option.

  Closes #367

* Fixed a false positive for ``used-before-assignment`` when a named expression
  appears as the first value in a container.

  Closes #5112

* ``used-before-assignment`` now assumes that assignments in except blocks
  may not have occurred and warns accordingly.

  Closes #4761

* When evaluating statements after an except block, ``used-before-assignment``
  assumes that assignments in the except blocks took place if the
  corresponding try block contained a return statement.

  Closes #5500

* Fixed a false negative for ``used-before-assignment`` when some but not all
  except handlers defined a name relied upon after an except block when the
  corresponding try block contained a return statement.

  Closes #5524

* When evaluating statements in the ``else`` clause of a loop, ``used-before-assignment``
  assumes that assignments in the except blocks took place if the
  except handlers constituted the only ways for the loop to finish without
  breaking early.

  Closes #5683

* ``used-before-assignment`` now checks names in try blocks.

* Fixed false positive with ``used-before-assignment`` for assignment expressions
  in lambda statements.

  Closes #5360, #3877

* Fixed a false positive (affecting unreleased development) for
  ``used-before-assignment`` involving homonyms between filtered comprehensions
  and assignments in except blocks.

  Closes #5586

* Fixed crash with slots assignments and annotated assignments.

  Closes #5479

* Fixed crash on list comprehensions that used ``type`` as inner variable name.

  Closes #5461

* Fixed crash in ``use-maxsplit-arg`` checker when providing the ``sep`` argument
  to ``str.split()`` by keyword.

  Closes #5737

* Fix false positive for ``unused-variable`` for a comprehension variable matching
  an outer scope type annotation.

  Closes #5326

* Fix false negative for ``undefined-variable`` for a variable used multiple times
  in a comprehension matching an unused outer scope type annotation.

  Closes #5654

* Some files in ``pylint.testutils`` were deprecated. In the future imports should be done from the
  ``pylint.testutils.functional`` namespace directly.

* Fixed false positives for ``no-value-for-parameter`` with variadic
  positional arguments.

  Closes #5416

* ``safe_infer`` no longer makes an inference when given two function
  definitions with differing numbers of arguments.

  Closes #3675

* Fix ``comparison-with-callable`` false positive for callables that raise, such
  as typing constants.

  Closes #5557

* Fixed a crash on ``__init__`` nodes when the attribute was previously uninferable due to a cache
  limit size. This limit can be hit when the inheritance pattern of a class (and therefore of the ``__init__`` attribute) is very large.

  Closes #5679

* Fix false positive for ``used-before-assignment`` from a class definition
  nested under a function subclassing a class defined outside the function.

  Closes #4590

* Fix ``unnecessary_dict_index_lookup`` false positive when deleting a dictionary's entry.

  Closes #4716

* Fix false positive for ``used-before-assignment`` when an except handler
  shares a name with a test in a filtered comprehension.

  Closes #5817

* Fix crash in ``unnecessary-dict-index-lookup`` checker if the output of
  ``items()`` is assigned to a 1-tuple.

  Closes #5504

* When invoking ``pylint``, ``epylint``, ``symilar`` or ``pyreverse`` by importing them in a python file
  you can now pass an ``argv`` keyword besides patching ``sys.argv``.

  Closes #5320

* The ``PyLinter`` class will now be initialized with a ``TextReporter``
  as its reporter if none is provided.

* Fix ``super-init-not-called`` when parent or ``self`` is a ``Protocol``

  Closes #4790

* Fix false positive ``not-callable`` with attributes that alias ``NamedTuple``

  Fixes part of #1730

* Emit ``redefined-outer-name`` when a nested except handler shadows an outer one.

  Closes #4434
  Closes #5370

* Fix false positive ``super-init-not-called`` for classes that inherit their ``init`` from
  a parent.

  Closes #4941

* ``encoding`` can now be supplied as a positional argument to calls that open
  files without triggering ``unspecified-encoding``.

  Closes #5638

* Fatal errors now emit a score of 0.0 regardless of whether the linted module
  contained any statements

  Closes #5451

* ``fatal`` was added to the variables permitted in score evaluation expressions.

* The default score evaluation now uses a floor of 0.

  Closes #2399

* Fix false negative for ``consider-iterating-dictionary`` during membership checks encapsulated in iterables
  or ``not in`` checks

  Closes #5323

* Fixed crash on uninferable decorators on Python 3.6 and 3.7

* Add checker ``unnecessary-ellipsis``: Emitted when the ellipsis constant is used unnecessarily.

  Closes #5460

* Disable checker ``bad-docstring-quotes`` for Python <= 3.7, because in these versions the line
  numbers for decorated functions and classes are not reliable which interferes with the checker.

  Closes #3077

* Fixed incorrect classification of Numpy-style docstring as Google-style docstring for
  docstrings with property setter documentation.
  Docstring classification is now based on the highest amount of matched sections instead
  of the order in which the docstring styles were tried.

* Fixed detection of ``arguments-differ`` when superclass static
  methods lacked a ``@staticmethod`` decorator.

  Closes #5371

* ``TypingChecker``

  * Added new check ``broken-noreturn`` to detect broken uses of ``typing.NoReturn``
    if ``py-version`` is set to Python ``3.7.1`` or below.
    https://bugs.python.org/issue34921

  * Added new check ``broken-collections-callable`` to detect broken uses of ``collections.abc.Callable``
    if ``py-version`` is set to Python ``3.9.1`` or below.
    https://bugs.python.org/issue42965

* The ``testutils`` for unittests now accept ``end_lineno`` and ``end_column``. Tests
  without these will trigger a ``DeprecationWarning``.

* ``arguments-differ`` will no longer complain about method redefinitions with extra parameters
  that have default values.

  Closes #1556, #5338

* Fixed false positive ``unexpected-keyword-arg`` for decorators.

  Closes #258

* Importing the deprecated stdlib module ``xml.etree.cElementTree`` now emits ``deprecated_module``.

  Closes #5862

* Disables for ``deprecated-module`` and similar warnings for stdlib features deprecated
  in newer versions of Python no longer raise ``useless-suppression`` when linting with
  older Python interpreters where those features are not yet deprecated.

* Importing the deprecated stdlib module ``distutils`` now emits ``deprecated_module`` on Python 3.10+.

* ``missing-raises-doc`` will now check the class hierarchy of the raised exceptions

  .. code-block:: python

    def my_function():
      """My function.

      Raises:
        Exception: if something fails
      """
      raise ValueError

  Closes #4955

* Disable spellchecking of mypy rule names in ignore directives.

  Closes #5929

* Allow disabling ``duplicate-code`` with a disable comment when running through
  pylint.

  Closes #214

* Improve ``invalid-name`` check for ``TypeVar`` names.
  The accepted pattern can be customized with ``--typevar-rgx``.

  Closes #3401

* Added new checker ``typevar-name-missing-variance``. Emitted when a covariant
  or contravariant ``TypeVar`` does not end with  ``_co`` or ``_contra`` respectively or
  when a ``TypeVar`` is not either but has a suffix.

* Allow usage of mccabe 0.7.x release

  Closes #5878

* Fix ``unused-private-member`` false positive when accessing private methods through ``property``.

  Closes #4756

.. _`Confusable Characters in PEP 672`: https://peps.python.org/pep-0672/#confusable-characters-in-identifiers
````

## File: doc/whatsnew/2/2.13/index.rst
````
***************************
 What's New in Pylint 2.13
***************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.13/summary.rst
````
:Release: 2.13
:Date: 2022-03-24

Summary -- Release highlights
=============================

In 2.13, we introduced a new check to deal with unicode security issues. On top of that a lot of work was
done inside the unicode checker by @CarliJoy. We also introduced a new check when importing private name
and for unnecessary ellipsis among other.

We fixed long standing issues related to duplicate code that could not be disabled, line numbers
that were not accurate some of the time, and added the ability to lint all files in a directory without
specifying each one. One of the most anticipated issue from the repository. Thank you @matusvalo !

A lot of ``undefined-variables`` and ``used-before-assignment`` issues were resolved thanks to @jacobtylerwalls.

We started integrating ``pylint-error`` the documentation created by @vald-phoenix a developer from Hlyniane,
Ukraine. We hope he's doing well despite the current situation. The deployment is set up but `there's still a lot to do so we welcome any community effort
help to review, integrate, and add good/bad examples <https://github.com/pylint-dev/pylint/issues/5953>`_. This should be doable
without any pylint or astroid knowledge, so this is the perfect entrypoint if you want to contribute
to pylint without investing any time learning the internals.

This release is the last one to support interpreter below 3.7.2, 3.6 end of life was reached in december 2021.

New checkers
============

* Added several checkers to deal with unicode security issues
  (see `Trojan Sources <https://trojansource.codes/>`_ and
  `PEP 672 <https://peps.python.org/pep-0672/>`_ for details) that also
  concern the readability of the code. In detail the following checks were added:

  * ``bad-file-encoding`` checks that the file is encoded in UTF-8 as suggested by
    `PEP8 <https://peps.python.org/pep-0008/#source-file-encoding>`_.
    UTF-16 and UTF-32 are `not supported by Python <https://bugs.python.org/issue1503789>`_
    at the moment. If this ever changes
    ``invalid-unicode-codec`` checks that they aren't used, to allow for backwards
    compatibility.

  * ``bidirectional-unicode`` checks for bidirectional unicode characters that
    could make code execution different than what the user expects.

  * ``invalid-character-backspace``, ``invalid-character-carriage-return``,
    ``invalid-character-sub``, ``invalid-character-esc``,
    ``invalid-character-zero-width-space`` and ``invalid-character-nul``
    to check for possibly harmful unescaped characters.

  Closes #5281

* ``unnecessary-ellipsis``: Emitted when the ellipsis constant is used unnecessarily.

  Closes #5460

* Added new checker ``typevar-name-missing-variance``. Emitted when a covariant
  or contravariant ``TypeVar`` does not end with  ``_co`` or ``_contra`` respectively or
  when a ``TypeVar`` is not either but has a suffix.

* Add ``modified-iterating-list``, ``modified-iterating-dict``, and ``modified-iterating-set``,
  emitted when items are added to or removed from respectively a list, dictionary or
  set being iterated through.

  Closes #5348

* Add checker ``redefined-slots-in-subclass``: Emitted when a slot is redefined in a subclass.

  Closes #5617

* Rewrote Checker of ``non-ascii-name``.
   It now ensures __all__ Python names are ASCII and also properly
   checks the names of imports (``non-ascii-module-import``) as
   well as file names (``non-ascii-file-name``) and emits their respective new warnings.

   Non ASCII characters could be homoglyphs (look alike characters) and hard to
   enter on a non specialized keyboard.
   See `Confusable Characters in PEP 672`_

.. _`Confusable Characters in PEP 672`: https://peps.python.org/pep-0672/#confusable-characters-in-identifiers

* Added ``cache-max-size-none`` checker with checks for the use of ``functools.lru_cache``
  on class methods with a ``maxsize`` of ``None``. This is unrecommended as it
  creates memory leaks by never letting the instance get garbage collected.

  Closes #5670
  Closes #6180

Removed checkers
================

* Removed the deprecated ``check_docs`` extension. You can use the ``docparams`` checker
  to get the checks previously included in ``check_docs``.

  Closes #5322

Extensions
==========
* New extension ``import-private-name``: indicate imports of external private packages
  and objects (prefixed with ``_``). It can be loaded using ``load-plugins=pylint.extensions.private_import``.

  Closes #5463

* Pyreverse - add output in mermaid-js format and html which is an mermaid js diagram with html boilerplate

* ``TypingChecker``

  * Added new check ``broken-noreturn`` to detect broken uses of ``typing.NoReturn``
    if ``py-version`` is set to Python ``3.7.1`` or below.
    https://bugs.python.org/issue34921

  * Added new check ``broken-collections-callable`` to detect broken uses of ``collections.abc.Callable``
    if ``py-version`` is set to Python ``3.9.1`` or below.
    https://bugs.python.org/issue42965

* ``DocstringParameterChecker``

  * Fixed incorrect classification of Numpy-style docstring as Google-style docstring for
    docstrings with property setter documentation.
    Docstring classification is now based on the highest amount of matched sections instead
    of the order in which the docstring styles were tried.

* ``DocStringStyleChecker``

    * Disable checker ``bad-docstring-quotes`` for Python <= 3.7, because in these versions the line
      numbers for decorated functions and classes are not reliable which interferes with the checker.

   Closes #3077

Other Changes
=============

* Include ``testing_pylintrc`` in source and wheel distributions.

  Closes #6028

* Fix false positive for ``unused-import`` when disabling both ``used-before-assignment`` and ``undefined-variable``.

  Closes #6089

* Fix false positive for ``unnecessary-ellipsis`` when using an ellipsis as a default argument.

  Closes #5973

* Add missing dunder methods to ``unexpected-special-method-signature`` check.

* No longer emit ``no-member`` in for loops that reference ``self`` if the binary operation that
  started the for loop uses a ``self`` that is encapsulated in tuples or lists.

  Refs pylint-dev/astroid#1360
  Closes #4826

* Fix matching ``--notes`` options that end in a non-word character.

  Closes #5840

* The line numbering for messages related to function arguments is now more accurate. This can
  require some message disables to be relocated to updated positions.

* ``using-f-string-in-unsupported-version`` and ``using-final-decorator-in-unsupported-version`` msgids
    were renamed from ``W1601`` and ``W1602`` to ``W2601`` and ``W2602``. Disables using these msgids will break.
    This is done in order to restore consistency with the already existing msgids for ``apply-builtin`` and
    ``basestring-builtin`` from the now deleted python 3K+ checker. There is now a check that we're not using
    existing msgids or symbols from deleted checkers.

  Closes #5729

* Add ``--recursive`` option to allow recursive discovery of all modules and packages in subtree. Running pylint with
  ``--recursive=y`` option will check all discovered ``.py`` files and packages found inside subtree of directory provided
  as parameter to pylint.

  Closes #352

* Updated the position of messages for class and function definitions to no longer cover
  the complete definition. Only the ``def`` or ``class`` + the name of the class/function
  are covered.

  Closes #5466

* Reinstated checks from the python3 checker that are still useful for python 3
  (``eq-without-hash``). This is now in the ``pylint.extensions.eq_without_hash`` optional
  extension.

  Closes #5025

* Fix false-negative for ``assignment-from-none`` checker with list.sort() method.

  Closes #5722

* Fix ``unused-private-member`` false positive when accessing private methods through ``property``.

  Closes #4756

* Fixed crash from ``arguments-differ`` and ``arguments-renamed`` when methods were
  defined outside the top level of a class.

  Closes #5648

* Better warning messages for useless else or elif when a function returns early.

  Closes #5614

* Asterisks are no longer required in Sphinx and Google style parameter documentation
  for ``missing-param-doc`` and are parsed correctly.

  Closes #5815
  Closes #5406

* Fixed an ``AstroidError`` in 2.13.0 raised by the ```duplicate-code``` checker with
  ``ignore-imports`` or ``ignore-signatures`` enabled.

  Closes #6301

* Use the ``tomli`` package instead of ``toml`` to parse ``.toml`` files.

  Closes #5885

* Fixed false positive ``consider-using-dict-comprehension`` when creating a dict
  using a list of tuples where key AND value vary depending on the same condition.

  Closes #5588

* When run in parallel mode ``pylint`` now pickles the data passed to subprocesses with
  the ``dill`` package. The ``dill`` package has therefore been added as a dependency.

* Fixed false positive for ``global-variable-undefined`` when ``global`` is used with a class name

  Closes #3088

* Fixed crash on properties and inherited class methods when comparing them for
  equality against an empty dict.

  Closes #5646

* By default, pylint does no longer take files starting with ``.#`` into account. Those are
  considered `Emacs file locks`_. This behavior can be reverted by redefining the
  ``ignore-patterns`` option.

  Closes #367

.. _`Emacs file locks`: https://www.gnu.org/software/emacs/manual/html_node/elisp/File-Locks.html

* Fix ``super-init-not-called`` when parent or ``self`` is a ``Protocol``

  Closes #4790

* The issue template for crashes is now created for crashes which were previously not covered
  by this mechanism.

  Closes #5668

* An astroid issue where symlinks were not being taken into account
  was fixed

  Closes #1470
  Closes #3499
  Closes #4302
  Closes #4798
  Closes #5081

* Fix false negative for ``undefined-variable`` and related variable messages
  when the same undefined variable is used as a type annotation and is
  accessed multiple times, or is used as a default argument to a function.

  Closes #5399

* Emit ``used-before-assignment`` instead of ``undefined-variable`` when attempting
  to access unused type annotations.

  Closes #5713

* Fixed an issue where ``ungrouped-imports`` could not be disabled without raising
  ``useless-suppression``.

  Refs #2366

* Fixed a crash on ``__init__`` nodes when the attribute was previously uninferable due to a cache
  limit size. This limit can be hit when the inheritance pattern of a class (and therefore of the ``__init__`` attribute) is very large.

  Closes #5679

* Fixed extremely long processing of long lines with comma's.

  Closes #5483

* Fix false positive ``super-init-not-called`` for classes that inherit their ``init`` from
  a parent.

  Closes #4941

* Fix false positives for ``used-before-assignment`` from using named
  expressions in a ternary operator test and using that expression as
  a call argument.

  Closes #5177, #5212

* Fixed crash with recursion error for inference of class attributes that referenced
  the class itself.

  Closes #5408
  Refs pylint-dev/astroid#1392

* Fixed false positive for ``unused-argument`` when a method overridden in a subclass
  does nothing with the value of a keyword-only argument.

  Closes #5771
  Refs pylint-dev/astroid#1382

* Optimize parsing of long lines when ``missing-final-newline`` is enabled.

  Closes #5724

* Fix false positive for ``used-before-assignment`` from a class definition
  nested under a function subclassing a class defined outside the function.

  Closes #4590

* Fix ``unnecessary_dict_index_lookup`` false positive when deleting a dictionary's entry.

  Closes #4716

* Fix false positive for ``used-before-assignment`` when an except handler
  shares a name with a test in a filtered comprehension.

  Closes #5817

* Fix a crash in ``unused-private-member`` checker when analyzing code using
  ``type(self)`` in bound methods.

  Closes #5569

* Fix crash in ``unnecessary-dict-index-lookup`` checker if the output of
  ``items()`` is assigned to a 1-tuple.

  Closes #5504

* Fixed crash with slots assignments and annotated assignments.

  Closes #5479

* Fixed a crash in ``unspecified-encoding`` checker when providing ``None``
  to the ``mode`` argument of an ``open()`` call.

  Closes #5731

* Fixed a crash involving a ``NewType`` named with an f-string.

  Closes #5770
  Refs pylint-dev/astroid#1400

* Improved ``bad-open-mode`` message when providing ``None`` to the ``mode``
  argument of an ``open()`` call.

  Closes #5733

* Fix false negative for ``consider-iterating-dictionary`` during membership checks encapsulated in iterables
  or ``not in`` checks

  Closes #5323

* Allow disabling ``duplicate-code`` with a disable comment when running through
  pylint.

  Closes #214

* Fix false positive for ``undefined-variable`` when ``namedtuple`` class
  attributes are used as return annotations.

  Closes #5568

* Added confidence level ``CONTROL_FLOW`` for warnings relying on assumptions
  about control flow.

* ``used-before-assignment`` now considers that assignments in a try block
  may not have occurred when the except or finally blocks are executed.

  Closes #85, #2615

* Fixed false negative for ``used-before-assignment`` when a conditional
  or context manager intervened before the try statement that suggested
  it might fail.

  Closes #4045

* Fixed false negative for ``used-before-assignment`` in finally blocks
  if an except handler did not define the assignment that might have failed
  in the try block.

* Fix a false positive for ``assigning-non-slot`` when the slotted class
  defined ``__setattr__``.

  Closes #3793

* Fixed a false positive for ``invalid-class-object`` when the object
  being assigned to the ``__class__`` attribute is uninferable.

* Added a ``testutil`` extra require to the packaging, as ``gitpython`` should not be a dependency
  all the time but is still required to use the primer helper code in ``pylint.testutil``. You can
  install it with ``pip install pylint[testutil]``.

  Closes #5486

* Fixed a false positive for ``used-before-assignment`` when a named expression
  appears as the first value in a container.

  Closes #5112

* Fixed false positive for ``used-before-assignment`` with self-referential type
  annotation in conditional statements within class methods.

  Closes #5499

* ``used-before-assignment`` now assumes that assignments in except blocks
  may not have occurred and warns accordingly.

  Closes #4761

* When evaluating statements after an except block, ``used-before-assignment``
  assumes that assignments in the except blocks took place if the
  corresponding try block contained a return statement.

  Closes #5500

* Fixed a false negative for ``used-before-assignment`` when some but not all
  except handlers defined a name relied upon after an except block when the
  corresponding try block contained a return statement.

  Closes #5524

* When evaluating statements in the ``else`` clause of a loop, ``used-before-assignment``
  assumes that assignments in the except blocks took place if the
  except handlers constituted the only ways for the loop to finish without
  breaking early.

  Closes #5683

* ``used-before-assignment`` now checks names in try blocks.

* Fixed false positive with ``used-before-assignment`` for assignment expressions
  in lambda statements.

  Closes #5360, #3877

* Improve ``invalid-name`` check for ``TypeVar`` names.
  The accepted pattern can be customized with ``--typevar-rgx``.

  Closes #3401

* Fixed a false positive (affecting unreleased development) for
  ``used-before-assignment`` involving homonyms between filtered comprehensions
  and assignments in except blocks.

  Closes #5586

* Fixed crash on list comprehensions that used ``type`` as inner variable name.

  Closes #5461

* Fixed crash in ``use-maxsplit-arg`` checker when providing the ``sep`` argument
  to ``str.split()`` by keyword.

  Closes #5737

* Fix false positive for ``unused-variable`` for a comprehension variable matching
  an outer scope type annotation.

  Closes #5326

* Fix false negative for ``undefined-variable`` for a variable used multiple times
  in a comprehension matching an unused outer scope type annotation.

  Closes #5654

* Require Python ``3.6.2`` to run pylint.

  Closes #5065

* Fixed crash on uninferable decorators on Python 3.6 and 3.7

* Emit ``redefined-outer-name`` when a nested except handler shadows an outer one.

  Closes #4434
  Closes #5370

* ``encoding`` can now be supplied as a positional argument to calls that open
  files without triggering ``unspecified-encoding``.

  Closes #5638

* Fatal errors now emit a score of 0.0 regardless of whether the linted module
  contained any statements

  Closes #5451

* ``fatal`` was added to the variables permitted in score evaluation expressions.

* The default score evaluation now uses a floor of 0.

  Closes #2399

* Fix ``comparison-with-callable`` false positive for callables that raise, such
  as typing constants.

  Closes #5557

* When invoking ``pylint``, ``epylint``, ``symilar`` or ``pyreverse`` by importing them in a python file
  you can now pass an ``argv`` keyword besides patching ``sys.argv``.

  Closes #5320

* The ``PyLinter`` class will now be initialized with a ``TextReporter``
  as its reporter if none is provided.

* Fix false positive ``not-callable`` with attributes that alias ``NamedTuple``

  Fixes part of #1730

* The ``testutils`` for unittests now accept ``end_lineno`` and ``end_column``. Tests
  without these will trigger a ``DeprecationWarning``.

* ``arguments-differ`` will no longer complain about method redefinitions with extra parameters
  that have default values.

  Closes #1556, #5338

* Disables for ``deprecated-module`` and similar warnings for stdlib features deprecated
  in newer versions of Python no longer raise ``useless-suppression`` when linting with
  older Python interpreters where those features are not yet deprecated.

* Importing the deprecated stdlib module ``xml.etree.cElementTree`` now emits ``deprecated_module``.

  Closes #5862

* Importing the deprecated stdlib module ``distutils`` now emits ``deprecated_module`` on Python 3.10+.

* Fixed false positive ``unexpected-keyword-arg`` for decorators.

  Closes #258

* ``missing-raises-doc`` will now check the class hierarchy of the raised exceptions

  .. code-block:: python

    def my_function():
      """My function.

      Raises:
        Exception: if something fails
      """
      raise ValueError

  Closes #4955

* Fixed false positive for ``unused-variable`` when a ``nonlocal`` name is assigned as part of a multi-name assignment.

  Closes #3781

* Fix false positive - Allow unpacking of ``self`` in a subclass of ``typing.NamedTuple``.

  Closes #5312

* Fixed false negative ``unpacking-non-sequence`` when value is an empty list.

  Closes #5707

* Fixed false positive for ``global-variable-not-assigned`` when the ``del`` statement is used

  Closes #5333

* Fix type hints in class diagrams generated by pyreverse for class methods and methods returning None.

* Output better error message if unsupported file formats are used with ``pyreverse``.

  Closes #5950

* Fixed false positive for ``unused-argument`` when a ``nonlocal`` name is used
  in a nested function that is returned without being called by its parent.

  Closes #5187

* Avoid emitting ``raising-bad-type`` when there is inference ambiguity on
  the variable being raised.

  Closes #2793

* Fix false positive for ``superfluous-parens`` for patterns like
  "return (a or b) in iterable".

  Closes #5803

* Fix a crash in the ``unsupported-membership-test`` checker when assigning
  multiple constants to class attributes including ``__iter__`` via unpacking.

  Closes #6366

* Fix false positive for ``used-before-assignment`` for assignments taking place via
  nonlocal declarations after an earlier type annotation.

  Closes #5394

* Fixed a false positive for ``unused-variable`` when a builtin specified in
  ``--additional-builtins`` is given a type annotation.

  Closes #6388

* Fix false positive for 'nonexistent-operator' when repeated '-' are
  separated (e.g. by parens).

  Closes #5769

* Fix a false positive for ``undefined-loop-variable`` when the ``else`` of a ``for``
  loop raises or returns.

  Closes #5971

* Only raise ``not-callable`` when all the inferred values of a property are not callable.

  Closes #5931

* Fix false positive for ``unused-variable`` for classes inside functions
  and where a metaclass is provided via a call.

  Closes #4020

* Avoid reporting ``superfluous-parens`` on expressions using the ``is not`` operator.

  Closes #5930

* Fix a false positive for ``undefined-loop-variable`` for a variable used in a lambda
  inside the first of multiple loops.

  Closes #6419

* Fix false positive for ``unsubscriptable-object`` in Python 3.8 and below for
  statements guarded by ``if TYPE_CHECKING``.

  Closes #3979

* Fix a crash when accessing ``__code__`` and assigning it to a variable.

  Closes #6539

* Fix a crash when linting a file that passes an integer ``mode=`` to
  ``open``

  Closes #6414

* Fix false positives for ``no-name-in-module`` and ``import-error`` for ``numpy.distutils``
  and ``pydantic``.

  Closes #6497

* Fix ``IndexError`` crash in ``uninferable_final_decorators`` method.

  Refs #6531

* Fix a crash in ``unnecessary-dict-index-lookup`` when subscripting an attribute.

  Closes #6557

* Fix a false positive for ``undefined-loop-variable`` when using ``enumerate()``.

  Closes #6593
````

## File: doc/whatsnew/2/2.14/full.rst
````
Full changelog
==============


What's New in Pylint 2.14.5?
----------------------------
Release date: 2022-07-17


* Fixed a crash in the ``undefined-loop-variable`` check when ``enumerate()`` is used
  in a ternary expression.

  Closes #7131

* Fixed handling of ``--`` as separator between positional arguments and flags.

  Closes #7003

* Fixed the disabling of ``fixme`` and its interaction with ``useless-suppression``.

* Allow lists of default values in parameter documentation for ``Numpy`` style.

  Closes #4035


What's New in Pylint 2.14.4?
----------------------------
Release date: 2022-06-29

* The ``differing-param-doc`` check was triggered by positional only arguments.

  Closes #6950

* Fixed an issue where scanning `.` directory recursively with ``--ignore-path=^path/to/dir`` is not
  ignoring the `path/to/dir` directory.

  Closes #6964

* Fixed regression that didn't allow quoted ``init-hooks`` in option files.

  Closes #7006

* Fixed a false positive for ``modified-iterating-dict`` when updating an existing key.

  Closes #6179

* Fixed an issue where many-core Windows machines (>~60 logical processors) would hang when
  using the default jobs count.

  Closes #6965

* Fixed an issue with the recognition of ``setup.cfg`` files.
  Only ``.cfg`` files that are exactly named ``setup.cfg`` require section names that
  start with ``pylint.``.

  Closes #3630

* Don't report ``import-private-name`` for relative imports.

  Closes #7078


What's New in Pylint 2.14.3?
----------------------------
Release date: 2022-06-18

* Fixed two false positives for ``bad-super-call`` for calls that refer to a non-direct parent.

  Closes #4922, Closes #2903

* Fixed a false positive for ``useless-super-delegation`` for subclasses that specify the number of
  of parameters against a parent that uses a variadic argument.

  Closes #2270

* Allow suppressing ``undefined-loop-variable`` and ``undefined-variable`` without raising ``useless-suppression``.

* Fixed false positive for ``undefined-variable`` for ``__class__`` in inner methods.

  Closes #4032


What's New in Pylint 2.14.2?
----------------------------
Release date: 2022-06-15

* Fixed a false positive for ``unused-variable`` when a function returns an
  ``argparse.Namespace`` object.

  Closes #6895

* Avoided raising an identical ``undefined-loop-variable`` message twice on the same line.

* Don't crash if ``lint.run._query_cpu()`` is run within a Kubernetes Pod, that has only
  a fraction of a cpu core assigned. Just go with one process then.

  Closes #6902

* Fixed a false positive in ``consider-using-f-string`` if the left side of a ``%`` is not a string.

  Closes #6689

* Fixed a false positive in ``unnecessary-list-index-lookup`` and ``unnecessary-dict-index-lookup``
  when the subscript is updated in the body of a nested loop.

  Closes #6818

* Fixed an issue with multi-line ``init-hook`` options which did not record the line endings.

  Closes #6888

* Fixed a false positive for ``used-before-assignment`` when a try block returns
  but an except handler defines a name via type annotation.

* ``--errors-only`` no longer enables previously disabled messages. It was acting as
  "emit *all* and only error messages" without being clearly documented that way.

  Closes #6811


What's New in Pylint 2.14.1?
----------------------------
Release date: 2022-06-06

* Avoid reporting ``unnecessary-dict-index-lookup`` or ``unnecessary-list-index-lookup``
  when the index lookup is part of a destructuring assignment.

  Closes #6788

* Fixed parsing of unrelated options in ``tox.ini``.

  Closes #6800

* Fixed a crash when linting ``__new__()`` methods that return a call expression.

  Closes #6805

* Don't crash if we can't find the user's home directory.

  Closes #6802

* Fixed false positives for ``unused-import`` when aliasing ``typing`` e.g. as ``t``
  and guarding imports under ``t.TYPE_CHECKING``.

  Closes #3846

* Fixed a false positive regression in 2.13 for ``used-before-assignment`` where it is safe to rely
  on a name defined only in an ``except`` block because the ``else`` block returned.

  Closes #6790

* Fixed the use of abbreviations for some special options on the command line.

  Closes #6810

* Fix a crash in the optional ``pylint.extensions.private_import`` extension.

  Closes #6624

* ``bad-option-value`` (E0012) is now a warning ``unknown-option-value`` (W0012). Deleted messages that do not exist
  anymore in pylint now raise ``useless-option-value`` (R0022) instead of ``bad-option-value``. This allows to
  distinguish between genuine typos and configuration that could be cleaned up.  Existing message disables for
  ``bad-option-value`` will still work on both new messages.

  Refs #6794


What's New in Pylint 2.14.0?
----------------------------
Release date: 2022-06-01


* The refactoring checker now also raises 'consider-using-generator' messages for
  ``max()``, ``min()`` and ``sum()``.

  Refs #6595

* We have improved our recognition of inline disable and enable comments. It is
  now possible to disable ``bad-option-value`` inline  (as long as you disable it before
  the bad option value is raised, i.e. ``disable=bad-option-value,bad-message`` not ``disable=bad-message,bad-option-value`` ) as well as certain other previously unsupported messages.

  Closes #3312

* Fixed a crash in the ``unused-private-member`` checker involving chained private attributes.

  Closes #6709

* Added new checker ``comparison-of-constants``.

  Closes #6076

* ``pylint.pyreverse.ASTWalker`` has been removed, as it was only used internally by a single child class.

  Refs #6712

* ``pyreverse``: Resolving and displaying implemented interfaces that are defined by the ``__implements__``
  attribute has been deprecated and will be removed in 3.0.

  Refs #6713

* Fix syntax for return type annotations in MermaidJS diagrams produced with ``pyreverse``.

  Closes #6467

* Fix type annotations of class and instance attributes using the alternative union syntax in ``pyreverse`` diagrams.

* Fix ``unexpected-special-method-signature`` false positive for ``__init_subclass__`` methods with one or more arguments.

  Closes #6644

* Started ignoring underscore as a local variable for ``too-many-locals``.

  Closes #6488

* Improved wording of the message of ``deprecated-module``

  Closes #6169

* ``Pylint`` now requires Python 3.7.2 or newer to run.

  Closes #4301

* ``BaseChecker`` classes now require the ``linter`` argument to be passed.

* Fix a failure to respect inline disables for ``fixme`` occurring on the last line
  of a module when pylint is launched with ``--enable=fixme``.

* Update ``invalid-slots-object`` message to show bad object rather than its inferred value.

  Closes #6101

* The main checker name is now ``main`` instead of ``master``. The configuration does not need to be updated as sections' name are optional.

  Closes #5467

* Don't report ``useless-super-delegation`` for the ``__hash__`` method in classes that also override the ``__eq__`` method.

  Closes #3934

* Added new checker ``typevar-name-mismatch``: TypeVar must be assigned to a variable with the same name as its name argument.

  Closes #5224

* Pylint can now be installed with an extra-require called ``spelling`` (``pip install pylint[spelling]``).
  This will add ``pyenchant`` to pylint's dependencies. You will still need to install the
  requirements for ``pyenchant`` (the ``enchant`` library and any dictionaries) yourself. You will also
  need to set the ``spelling-dict`` option.

  Refs #6462

* Removed the ``assign-to-new-keyword`` message as there are no new keywords in the supported Python
  versions any longer.

  Closes #4683

* Fixed a crash in the ``not-an-iterable`` checker involving multiple starred expressions
  inside a call.

  Closes #6372

* Fixed a crash in the ``docparams`` extension involving raising the result of a function.

* Fixed failure to enable ``deprecated-module`` after a ``disable=all``
  by making ``ImportsChecker`` solely responsible for emitting ``deprecated-module`` instead
  of sharing responsibility with ``StdlibChecker``. (This could have led to double messages.)

* The ``no-init`` (W0232) warning has been removed. It's ok to not have an ``__init__`` in a class.

  Closes #2409

* The ``config`` attribute of ``BaseChecker`` has been deprecated. You can use ``checker.linter.config``
  to access the global configuration object instead of a checker-specific object.

  Refs #5392

* The ``level`` attribute of ``BaseChecker`` has been deprecated: everything is now
  displayed in ``--help``, all the time.

  Refs #5392

* The ``options_providers`` attribute of ``ArgumentsManager`` has been deprecated.

  Refs #5392

* The ``option_groups`` attribute of ``PyLinter`` has been deprecated.

  Refs #5392

* All ``Interface`` classes in ``pylint.interfaces`` have been deprecated. You can subclass
  the respective normal classes to get the same behaviour. The ``__implements__`` functionality
  was based on a rejected PEP from 2001:
  https://peps.python.org/pep-0245/

  Closes #2287

* The ``set_option`` method of ``BaseChecker`` has been deprecated. You can use ``checker.linter.set_option``
  to set an option on the global configuration object instead of a checker-specific object.

  Refs #5392

* ``implicit-str-concat`` will now be raised on calls like ``open("myfile.txt" "a+b")`` too.

  Closes #6441

* The ``config`` attribute of ``PyLinter`` is now of the ``argparse.Namespace`` type instead of
  ``optparse.Values``.

  Refs #5392

* ``MapReduceMixin`` has been deprecated. ``BaseChecker`` now implements ``get_map_data`` and
  ``reduce_map_data``. If a checker actually needs to reduce data it should define ``get_map_data``
  as returning something different than ``None`` and let its ``reduce_map_data`` handle a list
  of the types returned by ``get_map_data``.
  An example can be seen by looking at ``pylint/checkers/similar.py``.

* ``UnsupportedAction`` has been deprecated.

  Refs #5392

* ``OptionsManagerMixIn`` has been deprecated.

  Refs #5392

* ``OptionParser`` has been deprecated.

  Refs #5392

* ``Option`` has been deprecated.

  Refs #5392

* ``OptionsProviderMixIn`` has been deprecated.

  Refs #5392

* ``ConfigurationMixIn`` has been deprecated.

  Refs #5392

* ``get_global_config`` has been deprecated. You can now access all global options from
  ``checker.linter.config``.

  Refs #5392

* ``OptionsManagerMixIn`` has been replaced with ``ArgumentsManager``. ``ArgumentsManager`` is considered
  private API and most methods that were public on ``OptionsManagerMixIn`` have now been deprecated and will
  be removed in a future release.

  Refs #5392

* ``OptionsProviderMixIn`` has been replaced with ``ArgumentsProvider``. ``ArgumentsProvider`` is considered
  private API and most methods that were public on ``OptionsProviderMixIn`` have now been deprecated and will
  be removed in a future release.

  Refs #5392

* ``interfaces.implements`` has been deprecated and will be removed in 3.0. Please use standard inheritance
  patterns instead of ``__implements__``.

  Refs #2287

* ``invalid-enum-extension``: Used when a class tries to extend an inherited Enum class.

  Closes #5501

* Added the ``unrecognized-option`` message. Raised if we encounter any unrecognized options.

  Closes #5259

* Added new checker ``typevar-double-variance``: The "covariant" and "contravariant" keyword arguments
  cannot both be set to "True" in a TypeVar.

  Closes #5895

* Re-enable checker ``bad-docstring-quotes`` for Python <= 3.7.

  Closes #6087

* Removed the broken ``generate-man`` option.

  Closes #5283
  Closes #1887

* Fix false negative for ``bad-string-format-type`` if the value to be formatted is passed in
  as a variable holding a constant.

* Add new check ``unnecessary-dunder-call`` for unnecessary dunder method calls.

  Closes #5936
  Closes #6074

* The ``cache-max-size-none`` checker has been renamed to ``method-cache-max-size-none``.

  Closes #5670

* The ``method-cache-max-size-none`` checker will now also check ``functools.cache``.

  Closes #5670

* ``unnecessary-lambda-assignment``: Lambda expression assigned to a variable.
  Define a function using the "def" keyword instead.
  ``unnecessary-direct-lambda-call``: Lambda expression called directly.
  Execute the expression inline instead.

  Closes #5976

* ``potential-index-error``: Emitted when the index of a list or tuple exceeds its length.
  This checker is currently quite conservative to avoid false positives. We welcome
  suggestions for improvements.

  Closes #578

* Added optional extension ``redefined-loop-name`` to emit messages when a loop variable
  is redefined in the loop body.

  Closes #5072

* Changed message type from ``redefined-outer-name`` to ``redefined-loop-name``
  (optional extension) for redefinitions of outer loop variables by inner loops.

  Closes #5608

* The ``ignore-mixin-members`` option has been deprecated. You should now use the new
  ``ignored-checks-for-mixins`` option.

  Closes #5205

* ``bad-option-value`` will be emitted whenever a configuration value or command line invocation
  includes an unknown message.

  Closes #4324

* Avoid reporting ``superfluous-parens`` on expressions using the ``is not`` operator.

  Closes #5930

* Added the ``super-without-brackets`` checker, raised when a super call is missing its brackets.

  Closes #4008

* Added the ``generate-toml-config`` option.

  Refs #5462

* Added new checker ``unnecessary-list-index-lookup`` for indexing into a list while
  iterating over ``enumerate()``.

  Closes #4525

* Fix falsely issuing ``useless-suppression`` on the ``wrong-import-position`` checker.

  Closes #5219

* Fixed false positive ``no-member`` for Enums with self-defined members.

  Closes #5138

* Fix false negative for ``no-member`` when attempting to assign an instance
  attribute to itself without any prior assignment.

  Closes #1555

* The concept of checker priority has been removed.

* Add a new command line option ``--minimal-messages-config`` for ``pytest``, which disables all
  irrelevant messages when running the functional tests.

* ``duplicate-argument-name`` now only raises once for each set of duplicated arguments.

* Fix bug where specifically enabling just ``await-outside-async`` was not possible.

* The ``set_config_directly`` decorator has been removed.

* Added new message called ``duplicate-value`` which identifies duplicate values inside sets.

  Closes #5880

* Pylint now expands the user path (i.e. ``~`` to ``home/yusef/``) and expands environment variables (i.e. ``home/$USER/$project``
  to ``home/yusef/pylint`` for ``USER=yusef`` and ``project=pylint``) for pyreverse's ``output-directory``,
  ``import-graph``, ``ext-import-graph``,  ``int-import-graph`` options, and the spell checker's ``spelling-private-dict-file``
  option.

  Refs #6493

* Created ``NoSelfUseChecker`` extension and moved the ``no-self-use`` check.
  You now need to explicitly enable this check using
  ``load-plugins=pylint.extensions.no_self_use``.

  Closes #5502

* Fix saving of persistent data files in environments where the user's cache
  directory and the linted file are on a different drive.

  Closes #6394

* Don't emit ``unsubscriptable-object`` for string annotations.
  Pylint doesn't check if class is only generic in type stubs only.

  Closes #4369 and #6523

* Fix pyreverse crash ``RuntimeError: dictionary changed size during iteration``

  Refs #6612

* Fix bug where it writes a plain text error message to stdout, invalidating output formats.

  Closes #6597

* ``is_class_subscriptable_pep585_with_postponed_evaluation_enabled`` has been deprecated.
  Use ``is_postponed_evaluation_enabled(node) and is_node_in_type_annotation_context(node)``
  instead.

  Refs #6536

* Update ranges for ``using-constant-test`` and ``missing-parentheses-for-call-in-test``
  error messages.

* Don't emit ``no-member`` inside type annotations with
  ``from __future__ import annotations``.

  Closes #6594
````

## File: doc/whatsnew/2/2.14/index.rst
````
***************************
 What's New in Pylint 2.14
***************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.14/summary.rst
````
:Release: 2.14
:Date: 2022-06-01

Summary -- Release highlights
=============================

With 2.14 ``pylint`` only supports Python version 3.7.2 and above.

We introduced several new checks among which ``duplicate-value`` for sets,
``comparison-of-constants``, and checks related to lambdas. We removed ``no-init`` and
made ``no-self-use`` optional as they were too opinionated. We also added an option
to generate a toml configuration: ``--generate-toml-config``.

We migrated to ``argparse`` from ``optparse`` and refactored the configuration handling
thanks to Daniël van Noord. On the user side it should change the output of the
``--help`` command, and some inconsistencies and bugs should disappear. The behavior
between options set in a config file versus on the command line will be more consistent. For us,
it will permit to maintain this part of the code easily in the future.

As a result of the refactor there are a lot of internal deprecations. If you're a library
maintainer that depends on pylint, please verify that you're ready for pylint 3.0
by activating deprecation warnings.

We continued the integration of ``pylint-error`` and are now at 33%!. We still welcome any community effort
to help review, integrate, and add good/bad examples <https://github.com/pylint-dev/pylint/issues/5953>`_. This should be doable
without any ``pylint`` or ``astroid`` knowledge, so this is the perfect entrypoint if you want
to contribute to ``pylint`` or open source without any experience with our code!

New checkers
============

* Added new checker ``comparison-of-constants``.

  Closes #6076

* Added new checker ``typevar-name-mismatch``: TypeVar must be assigned to a variable with the same name as its name argument.

  Closes #5224

* ``invalid-enum-extension``: Used when a class tries to extend an inherited Enum class.

  Closes #5501

* Added new checker ``typevar-double-variance``: The "covariant" and "contravariant" keyword arguments
  cannot both be set to "True" in a TypeVar.

  Closes #5895

* Add new check ``unnecessary-dunder-call`` for unnecessary dunder method calls.

  Closes #5936

* ``unnecessary-lambda-assignment``: Lambda expression assigned to a variable.
  Define a function using the "def" keyword instead.
  ``unnecessary-direct-lambda-call``: Lambda expression called directly.
  Execute the expression inline instead.

  Closes #5976

* ``potential-index-error``: Emitted when the index of a list or tuple exceeds its length.
  This checker is currently quite conservative to avoid false positives. We welcome
  suggestions for improvements.

  Closes #578

* Added new checker ``unnecessary-list-index-lookup`` for indexing into a list while
  iterating over ``enumerate()``.

  Closes #4525

* Added new message called ``duplicate-value`` which identifies duplicate values inside sets.

  Closes #5880

* Added the ``super-without-brackets`` checker, raised when a super call is missing its brackets.

  Closes #4008

Removed checkers
================

* The ``no-init`` (W0232) warning has been removed. It's ok to not have an ``__init__`` in a class.

  Closes #2409

* Removed the ``assign-to-new-keyword`` message as there are no new keywords in the supported Python
  versions any longer.

  Closes #4683

* Moved ``no-self-use`` check to optional extension.
  You now need to explicitly enable this check using
  ``load-plugins=pylint.extensions.no_self_use``.

  Closes #5502


Extensions
==========

* ``RedefinedLoopNameChecker``

    * Added optional extension ``redefined-loop-name`` to emit messages when a loop variable
      is redefined in the loop body.

   Closes #5072

* ``DocStringStyleChecker``

    * Re-enable checker ``bad-docstring-quotes`` for Python <= 3.7.

   Closes #6087

* ``NoSelfUseChecker``

    * Added ``no-self-use`` check, previously enabled by default.

   Closes #5502


Other Changes
=============

* Started ignoring underscore as a local variable for ``too-many-locals``.

  Closes #6488

* Pylint can now be installed with an extra-require called ``spelling`` (``pip install pylint[spelling]``).
  This will add ``pyenchant`` to pylint's dependencies. You will still need to install the
  requirements for ``pyenchant`` (the ``enchant`` library and any dictionaries) yourself. You will also
  need to set the ``spelling-dict`` option.

  Refs #6462

* Improved wording of the message of ``deprecated-module``

  Closes #6169

* ``Pylint`` now requires Python 3.7.2 or newer to run.

  Closes #4301

* We made a greater effort to reraise failures stemming from the ``astroid``
  library as ``AstroidError``, with the effect that pylint emits ``astroid-error``
  rather than merely ``fatal``. Regardless, please report any such issues you encounter!

* We have improved our recognition of inline disable and enable comments. It is
  now possible to disable ``bad-option-value`` inline (as long as you disable it before
  the bad option value is raised, i.e. ``disable=bad-option-value,bad-message`` not ``disable=bad-message,bad-option-value`` ) as well as certain other
  previously unsupported messages.

  Closes #3312

* The main checker name is now ``main`` instead of ``master``. The configuration does not need to be updated as sections' name are optional.

  Closes #5467

* Update ``invalid-slots-object`` message to show bad object rather than its inferred value.

  Closes #6101

* Fixed a crash in the ``not-an-iterable`` checker involving multiple starred expressions
  inside a call.

  Closes #6372

* Fixed a crash in the ``unused-private-member`` checker involving chained private attributes.

  Closes #6709

* Disable spellchecking of mypy rule names in ignore directives.

  Closes #5929

* ``implicit-str-concat`` will now be raised on calls like ``open("myfile.txt" "a+b")`` too.

  Closes #6441

* Fix a failure to respect inline disables for ``fixme`` occurring on the last line
  of a module when pylint is launched with ``--enable=fixme``.

* Removed the broken ``generate-man`` option.

  Closes #5283
  Closes #1887

* Fixed failure to enable ``deprecated-module`` after a ``disable=all``
  by making ``ImportsChecker`` solely responsible for emitting ``deprecated-module`` instead
  of sharing responsibility with ``StdlibChecker``. (This could have led to double messages.)

* Added the ``generate-toml-config`` option.

  Refs #5462

* ``bad-option-value`` will be emitted whenever a configuration value or command line invocation
  includes an unknown message.

  Closes #4324

* Added the ``unrecognized-option`` message. Raised if we encounter any unrecognized options.

  Closes #5259

* Fix false negative for ``bad-string-format-type`` if the value to be formatted is passed in
  as a variable holding a constant.

* The concept of checker priority has been removed.

* The ``cache-max-size-none`` checker has been renamed to ``method-cache-max-size-none``.

  Closes #5670

* The ``method-cache-max-size-none`` checker will now also check ``functools.cache``.

  Closes #5670

* ``BaseChecker`` classes now require the ``linter`` argument to be passed.

* The ``set_config_directly`` decorator has been removed.

* Don't report ``useless-super-delegation`` for the ``__hash__`` method in classes that also override the ``__eq__`` method.

  Closes #3934

* Fix falsely issuing ``useless-suppression`` on the ``wrong-import-position`` checker.

  Closes #5219

* Fixed false positive ``no-member`` for Enums with self-defined members.

  Closes #5138

* Fix false negative for ``no-member`` when attempting to assign an instance
  attribute to itself without any prior assignment.

  Closes #1555

* Changed message type from ``redefined-outer-name`` to ``redefined-loop-name``
  (optional extension) for redefinitions of outer loop variables by inner loops.

  Closes #5608

* By default the similarity checker will now ignore imports and ignore function signatures when computing
  duplication. If you want to keep the previous behaviour set ``ignore-imports`` and ``ignore-signatures`` to ``False``.

* Pylint now expands the user path (i.e. ``~`` to ``home/yusef/``) and expands environment variables (i.e. ``home/$USER/$project``
  to ``home/yusef/pylint`` for ``USER=yusef`` and ``project=pylint``) for pyreverse's ``output-directory``,
  ``import-graph``, ``ext-import-graph``,  ``int-import-graph`` options, and the spell checker's ``spelling-private-dict-file``
  option.

  Refs #6493

* Don't emit ``unsubscriptable-object`` for string annotations.
  Pylint doesn't check if class is only generic in type stubs only.

  Closes #4369 and #6523

* Fix pyreverse crash ``RuntimeError: dictionary changed size during iteration``

  Refs #6612

* Fix syntax for return type annotations in MermaidJS diagrams produced with ``pyreverse``.

  Closes #6467

* Fix type annotations of class and instance attributes using the alternative union syntax in ``pyreverse`` diagrams.

* Fix bug where it writes a plain text error message to stdout, invalidating output formats.

  Closes #6597

* The refactoring checker now also raises 'consider-using-a-generator' messages for
  ``max()``, ``min()`` and ``sum()``.

  Refs #6595

* Update ranges for ``using-constant-test`` and ``missing-parentheses-for-call-in-test``
  error messages.

* Don't emit ``no-member`` inside type annotations with
  ``from __future__ import annotations``.

  Closes #6594

* Fix ``unexpected-special-method-signature`` false positive for ``__init_subclass__`` methods with one or more arguments.

  Closes #6644


Deprecations
============

* The ``ignore-mixin-members`` option has been deprecated. You should now use the new
  ``ignored-checks-for-mixins`` option.

  Closes #5205

* ``interfaces.implements`` has been deprecated and will be removed in 3.0. Please use standard inheritance
  patterns instead of ``__implements__``.

  Refs #2287

* All ``Interface`` classes in ``pylint.interfaces`` have been deprecated. You can subclass
  the respective normal classes to get the same behaviour. The ``__implements__`` functionality
  was based on a rejected PEP from 2001:
  https://peps.python.org/pep-0245/

  Closes #2287

* ``MapReduceMixin`` has been deprecated. ``BaseChecker`` now implements ``get_map_data`` and
  ``reduce_map_data``. If a checker actually needs to reduce data it should define ``get_map_data``
  as returning something different than ``None`` and let its ``reduce_map_data`` handle a list
  of the types returned by ``get_map_data``.
  An example can be seen by looking at ``pylint/checkers/similar.py``.


* The ``config`` attribute of ``BaseChecker`` has been deprecated. You can use ``checker.linter.config``
  to access the global configuration object instead of a checker-specific object.

  Refs #5392

* The ``level`` attribute of ``BaseChecker`` has been deprecated: everything is now
  displayed in ``--help``, all the time.

  Refs #5392

* The ``set_option`` method of ``BaseChecker`` has been deprecated. You can use ``checker.linter.set_option``
  to set an option on the global configuration object instead of a checker-specific object.

  Refs #5392

* The ``options_providers`` attribute of ``ArgumentsManager`` has been deprecated.

  Refs #5392

* Fix saving of persistent data files in environments where the user's cache
  directory and the linted file are on a different drive.

  Closes #6394

* The ``method-cache-max-size-none`` checker will now also check ``functools.cache``.

* The ``config`` attribute of ``PyLinter`` is now of the ``argparse.Namespace`` type instead of
  ``optparse.Values``.

  Refs #5392

* ``UnsupportedAction`` has been deprecated.

  Refs #5392

* ``OptionsManagerMixIn`` has been deprecated.

  Refs #5392

* ``OptionParser`` has been deprecated.

  Refs #5392

* ``Option`` has been deprecated.

  Refs #5392

* ``OptionsProviderMixIn`` has been deprecated.

  Refs #5392

* ``ConfigurationMixIn`` has been deprecated.

* The ``option_groups`` attribute of ``PyLinter`` has been deprecated.

  Refs #5392

* ``get_global_config`` has been deprecated. You can now access all global options from
  ``checker.linter.config``.

  Refs #5392

* ``OptionsManagerMixIn`` has been replaced with ``ArgumentsManager``. ``ArgumentsManager`` is considered
  private API and most methods that were public on ``OptionsManagerMixIn`` have now been deprecated and will
  be removed in a future release.

  Refs #5392

* ``OptionsProviderMixIn`` has been replaced with ``ArgumentsProvider``. ``ArgumentsProvider`` is considered
  private API and most methods that were public on ``OptionsProviderMixIn`` have now been deprecated and will
  be removed in a future release.

  Refs #5392

* ``pylint.pyreverse.ASTWalker`` has been removed, as it was only used internally by a single child class.

  Refs #6712

* ``pyreverse``: Resolving and displaying implemented interfaces that are defined by the ``__implements__``
  attribute has been deprecated and will be removed in 3.0.

  Refs #6713

* ``is_class_subscriptable_pep585_with_postponed_evaluation_enabled`` has been deprecated.
  Use ``is_postponed_evaluation_enabled(node) and is_node_in_type_annotation_context(node)``
  instead.

  Refs #6536
````

## File: doc/whatsnew/2/2.15/index.rst
````
***************************
 What's New in Pylint 2.15
***************************

.. toctree::
   :maxdepth: 2

:Release: 2.15
:Date: 2022-08-26

Summary -- Release highlights
=============================

In pylint 2.15.0, we added a new check ``missing-timeout`` to warn of
default timeout values that could cause a program to be hanging indefinitely.

We improved ``pylint``'s handling of namespace packages. More packages should
be linted without resorting to using the ``--recursive=y`` option.

We still welcome any community effort to help review, integrate, and add good/bad examples to the doc for
<https://github.com/pylint-dev/pylint/issues/5953>`_. This should be doable without any ``pylint`` or ``astroid``
knowledge, so this is the perfect entrypoint if you want to contribute to ``pylint`` or open source without
any experience with our code!

Internally, we changed the way we generate the release notes, thanks to DudeNr33.
There will be no more conflict resolution to do in the changelog, and every contributor rejoice.

Marc Byrne became a maintainer, welcome to the team !

.. towncrier release notes start

What's new in Pylint 2.15.10?
-----------------------------
Release date: 2023-01-09


False Positives Fixed
---------------------

- Fix ``use-sequence-for-iteration`` when unpacking a set with ``*``.

  Closes #5788 (`#5788 <https://github.com/pylint-dev/pylint/issues/5788>`_)

- Fix false positive ``assigning-non-slot`` when a class attribute is
  re-assigned.

  Closes #6001 (`#6001 <https://github.com/pylint-dev/pylint/issues/6001>`_)

- Fixes ``used-before-assignment`` false positive when the walrus operator
  is used in a ternary operator.

  Closes #7779 (`#7779 <https://github.com/pylint-dev/pylint/issues/7779>`_)

- Prevent ``used-before-assignment`` when imports guarded by ``if
  TYPE_CHECKING``
  are guarded again when used.

  Closes #7979 (`#7979 <https://github.com/pylint-dev/pylint/issues/7979>`_)



Other Bug Fixes
---------------

- Using custom braces in ``msg-template`` will now work properly.

  Closes #5636 (`#5636 <https://github.com/pylint-dev/pylint/issues/5636>`_)


What's new in Pylint 2.15.9?
----------------------------
Release date: 2022-12-17


False Positives Fixed
---------------------

- Fix false-positive for ``used-before-assignment`` in pattern matching
  with a guard.

  Closes #5327 (`#5327 <https://github.com/pylint-dev/pylint/issues/5327>`_)



Other Bug Fixes
---------------

- Pylint will no longer deadlock if a parallel job is killed but fail
  immediately instead.

  Closes #3899 (`#3899 <https://github.com/pylint-dev/pylint/issues/3899>`_)

- When pylint exit due to bad arguments being provided the exit code will now
  be the expected ``32``.

  Refs #7931 (`#7931 <https://github.com/pylint-dev/pylint/issues/7931>`_)

- Fixes a ``ModuleNotFound`` exception when running pylint on a Django project
  with the ``pylint_django`` plugin enabled.

  Closes #7938 (`#7938 <https://github.com/pylint-dev/pylint/issues/7938>`_)


What's new in Pylint 2.15.8?
----------------------------
Release date: 2022-12-05


False Positives Fixed
---------------------

- Document a known false positive for ``useless-suppression`` when disabling
  ``line-too-long`` in a module with only comments and no code.

  Closes #3368 (`#3368 <https://github.com/pylint-dev/pylint/issues/3368>`_)

- Fix ``logging-fstring-interpolation`` false positive raised when logging and
  f-string with ``%s`` formatting.

  Closes #4984 (`#4984 <https://github.com/pylint-dev/pylint/issues/4984>`_)

- Fixes false positive ``abstract-method`` on Protocol classes.

  Closes #7209 (`#7209 <https://github.com/pylint-dev/pylint/issues/7209>`_)

- Fix ``missing-param-doc`` false positive when function parameter has an
  escaped underscore.

  Closes #7827 (`#7827 <https://github.com/pylint-dev/pylint/issues/7827>`_)

- ``multiple-statements`` no longer triggers for function stubs using inlined
  ``...``.

  Closes #7860 (`#7860 <https://github.com/pylint-dev/pylint/issues/7860>`_)


What's new in Pylint 2.15.7?
----------------------------
Release date: 2022-11-27


False Positives Fixed
---------------------

- Fix ``deprecated-method`` false positive when alias for method is similar to
  name of deprecated method.

  Closes #5886 (`#5886 <https://github.com/pylint-dev/pylint/issues/5886>`_)

- Fix a false positive for ``used-before-assignment`` for imports guarded by
  ``typing.TYPE_CHECKING`` later used in variable annotations.

  Closes #7609 (`#7609 <https://github.com/pylint-dev/pylint/issues/7609>`_)



Other Bug Fixes
---------------

- Pylint will now filter duplicates given to it before linting. The output
  should
  be the same whether a file is given/discovered multiple times or not.

  Closes #6242, #4053 (`#6242 <https://github.com/pylint-dev/pylint/issues/6242>`_)

- Fixes a crash in ``stop-iteration-return`` when the ``next`` builtin is
  called without arguments.

  Closes #7828 (`#7828 <https://github.com/pylint-dev/pylint/issues/7828>`_)


What's new in Pylint 2.15.6?
----------------------------
Release date: 2022-11-19


False Positives Fixed
---------------------

- Fix false positive for ``unhashable-member`` when subclassing ``dict`` and
  using the subclass as a dictionary key.

  Closes #7501 (`#7501 <https://github.com/pylint-dev/pylint/issues/7501>`_)

- ``unnecessary-list-index-lookup`` will not be wrongly emitted if
  ``enumerate`` is called with ``start``.

  Closes #7682 (`#7682 <https://github.com/pylint-dev/pylint/issues/7682>`_)

- Don't warn about ``stop-iteration-return`` when using ``next()`` over
  ``itertools.cycle``.

  Closes #7765 (`#7765 <https://github.com/pylint-dev/pylint/issues/7765>`_)



Other Bug Fixes
---------------

- Messages sent to reporter are now copied so a reporter cannot modify the
  message sent to other reporters.

  Closes #7214 (`#7214 <https://github.com/pylint-dev/pylint/issues/7214>`_)

- Fixes edge case of custom method named ``next`` raised an astroid error.

  Closes #7610 (`#7610 <https://github.com/pylint-dev/pylint/issues/7610>`_)

- Fix crash that happened when parsing files with unexpected encoding starting
  with 'utf' like ``utf13``.

  Closes #7661 (`#7661 <https://github.com/pylint-dev/pylint/issues/7661>`_)

- Fix a crash when a child class with an ``__init__`` method inherits from a
  parent class with an ``__init__`` class attribute.

  Closes #7742 (`#7742 <https://github.com/pylint-dev/pylint/issues/7742>`_)


What's new in Pylint 2.15.5?
----------------------------
Release date: 2022-10-21


False Positives Fixed
---------------------

- Fix a false positive for ``simplify-boolean-expression`` when multiple values
  are inferred for a constant.

  Closes #7626 (`#7626 <https://github.com/pylint-dev/pylint/issues/7626>`_)



Other Bug Fixes
---------------

- Remove ``__index__`` dunder method call from ``unnecessary-dunder-call``
  check.

  Closes #6795 (`#6795 <https://github.com/pylint-dev/pylint/issues/6795>`_)

- Fixed a multi-processing crash that prevents using any more than 1 thread on
  MacOS.

  The returned module objects and errors that were cached by the linter plugin
  loader
  cannot be reliably pickled. This means that ``dill`` would throw an error
  when
  attempting to serialise the linter object for multi-processing use.

  Closes #7635. (`#7635 <https://github.com/pylint-dev/pylint/issues/7635>`_)



Other Changes
-------------

- Add a keyword-only ``compare_constants`` argument to ``safe_infer``.

  Refs #7626 (`#7626 <https://github.com/pylint-dev/pylint/issues/7626>`_)

- Sort ``--generated-rcfile`` output.

  Refs #7655 (`#7655 <https://github.com/pylint-dev/pylint/issues/7655>`_)


What's new in Pylint 2.15.4?
----------------------------
Release date: 2022-10-10


False Positives Fixed
---------------------

- Fix the message for ``unnecessary-dunder-call`` for ``__aiter__`` and
  ``__anext__``. Also
  only emit the warning when ``py-version`` >= 3.10.

  Closes #7529 (`#7529 <https://github.com/pylint-dev/pylint/issues/7529>`_)



Other Bug Fixes
---------------

- Fix bug in detecting ``unused-variable`` when iterating on variable.

  Closes #3044 (`#3044 <https://github.com/pylint-dev/pylint/issues/3044>`_)

- Fixed handling of ``--`` as separator between positional arguments and flags.
  This was not actually fixed in 2.14.5.

  Closes #7003, Refs #7096 (`#7003
  <https://github.com/pylint-dev/pylint/issues/7003>`_)

- Report ``no-self-argument`` rather than ``no-method-argument`` for methods
  with variadic arguments.

  Closes #7507 (`#7507 <https://github.com/pylint-dev/pylint/issues/7507>`_)

- Fixed an issue where ``syntax-error`` couldn't be raised on files with
  invalid encodings.

  Closes #7522 (`#7522 <https://github.com/pylint-dev/pylint/issues/7522>`_)

- Fix false positive for ``redefined-outer-name`` when aliasing ``typing``
  e.g. as ``t`` and guarding imports under ``t.TYPE_CHECKING``.

  Closes #7524 (`#7524 <https://github.com/pylint-dev/pylint/issues/7524>`_)

- Fixed a crash of the ``modified_iterating`` checker when iterating on a set
  defined as a class attribute.

  Closes #7528 (`#7528 <https://github.com/pylint-dev/pylint/issues/7528>`_)

- Fix bug in scanning of names inside arguments to ``typing.Literal``.
  See https://peps.python.org/pep-0586/#literals-enums-and-forward-references
  for details.

  Refs #3299 (`#3299 <https://github.com/pylint-dev/pylint/issues/3299>`_)


Other Changes
-------------

- Add method name to the error messages of ``no-method-argument`` and
  ``no-self-argument``.

  Closes #7507 (`#7507 <https://github.com/pylint-dev/pylint/issues/7507>`_)


What's new in Pylint 2.15.3?
----------------------------
Release date: 2022-09-19


- Fixed a crash in the ``unhashable-member`` checker when using a ``lambda`` as a dict key.

  Closes #7453 (`#7453 <https://github.com/pylint-dev/pylint/issues/7453>`_)
- Fix a crash in the ``modified-iterating-dict`` checker involving instance attributes.

  Closes #7461 (`#7461 <https://github.com/pylint-dev/pylint/issues/7461>`_)
- ``invalid-class-object`` does not crash anymore when ``__class__`` is assigned alongside another variable.

  Closes #7467 (`#7467 <https://github.com/pylint-dev/pylint/issues/7467>`_)
- Fix false positive for ``global-variable-not-assigned`` when a global variable is re-assigned via an ``ImportFrom`` node.

  Closes #4809 (`#4809 <https://github.com/pylint-dev/pylint/issues/4809>`_)
- Fix false positive for ``undefined-loop-variable`` in ``for-else`` loops that use a function
  having a return type annotation of ``NoReturn`` or ``Never``.

  Closes #7311 (`#7311 <https://github.com/pylint-dev/pylint/issues/7311>`_)
- ``--help-msg`` now accepts a comma-separated list of message IDs again.

  Closes #7471 (`#7471 <https://github.com/pylint-dev/pylint/issues/7471>`_)

What's new in Pylint 2.15.2?
----------------------------
Release date: 2022-09-07

- Fixed a case where custom plugins specified by command line could silently fail.

  Specifically, if a plugin relies on the ``init-hook`` option changing ``sys.path`` before
  it can be imported, this will now emit a ``bad-plugin-value`` message. Before this
  change, it would silently fail to register the plugin for use, but would load
  any configuration, which could have unintended effects.

  Fixes part of #7264. (`#7264 <https://github.com/pylint-dev/pylint/issues/7264>`_)
- Fix ``used-before-assignment`` for functions/classes defined in type checking guard.

  Closes #7368 (`#7368 <https://github.com/pylint-dev/pylint/issues/7368>`_)
- Update ``modified_iterating`` checker to fix a crash with ``for`` loops on empty list.

  Closes #7380 (`#7380 <https://github.com/pylint-dev/pylint/issues/7380>`_)
- The ``docparams`` extension now considers typing in Numpy style docstrings
  as "documentation" for the ``missing-param-doc`` message.

  Refs #7398 (`#7398 <https://github.com/pylint-dev/pylint/issues/7398>`_)
- Fix false positive for ``unused-variable`` and ``unused-import`` when a name is only used in a string literal type annotation.

  Closes #3299 (`#3299 <https://github.com/pylint-dev/pylint/issues/3299>`_)
- Fix false positive for ``too-many-function-args`` when a function call is assigned to a class attribute inside the class where the function is defined.

  Closes #6592 (`#6592 <https://github.com/pylint-dev/pylint/issues/6592>`_)
- Fix ignored files being linted when passed on stdin.

  Closes #4354 (`#4354 <https://github.com/pylint-dev/pylint/issues/4354>`_)
- ``missing-return-doc``, ``missing-raises-doc`` and ``missing-yields-doc`` now respect
  the ``no-docstring-rgx`` option.

  Closes #4743 (`#4743 <https://github.com/pylint-dev/pylint/issues/4743>`_)
- Don't crash on ``OSError`` in config file discovery.

  Closes #7169 (`#7169 <https://github.com/pylint-dev/pylint/issues/7169>`_)
- ``disable-next`` is now correctly scoped to only the succeeding line.

  Closes #7401 (`#7401 <https://github.com/pylint-dev/pylint/issues/7401>`_)
- Update ``modified_iterating`` checker to fix a crash with ``for`` loops on empty list.

  Closes #7380 (`#7380 <https://github.com/pylint-dev/pylint/issues/7380>`_)

What's new in Pylint 2.15.1?
----------------------------
Release date: 2022-09-06

This is a "github only release", it was mistakenly released as ``2.16.0-dev`` on pypi. Replaced by ``2.15.2``.

What's new in Pylint 2.15.0?
----------------------------

New Checks
----------

- Added new checker ``missing-timeout`` to warn of default timeout values that could cause
  a program to be hanging indefinitely.

  Refs #6780 (`#6780 <https://github.com/pylint-dev/pylint/issues/6780>`_)


False Positives Fixed
---------------------

- Don't report ``super-init-not-called`` for abstract ``__init__`` methods.

  Closes #3975 (`#3975 <https://github.com/pylint-dev/pylint/issues/3975>`_)
- Don't report ``unsupported-binary-operation`` on Python <= 3.9 when using the ``|`` operator
  with types, if one has a metaclass that overloads ``__or__`` or ``__ror__`` as appropriate.

  Closes #4951 (`#4951 <https://github.com/pylint-dev/pylint/issues/4951>`_)
- Don't report ``no-value-for-parameter`` for dataclasses fields annotated with ``KW_ONLY``.

  Closes #5767 (`#5767 <https://github.com/pylint-dev/pylint/issues/5767>`_)
- Fixed inference of ``Enums`` when they are imported under an alias.

  Closes #5776 (`#5776 <https://github.com/pylint-dev/pylint/issues/5776>`_)
- Prevent false positives when accessing ``PurePath.parents`` by index (not slice) on Python 3.10+.

  Closes #5832 (`#5832 <https://github.com/pylint-dev/pylint/issues/5832>`_)
- ``unnecessary-list-index-lookup`` is now more conservative to avoid potential false positives.

  Closes #6896 (`#6896 <https://github.com/pylint-dev/pylint/issues/6896>`_)
- Fix double emitting ``trailing-whitespace`` for multi-line docstrings.

  Closes #6936 (`#6936 <https://github.com/pylint-dev/pylint/issues/6936>`_)
- ``import-error`` now correctly checks for ``contextlib.suppress`` guards on import statements.

  Closes #7270 (`#7270 <https://github.com/pylint-dev/pylint/issues/7270>`_)
- Fix false positive for `no-self-argument`/`no-method-argument` when a staticmethod is applied to a function but uses a different name.

  Closes #7300 (`#7300 <https://github.com/pylint-dev/pylint/issues/7300>`_)
- Fix `undefined-loop-variable` with `break` and `continue` statements in `else` blocks.

  Refs #7311 (`#7311 <https://github.com/pylint-dev/pylint/issues/7311>`_)
- Improve default TypeVar name regex. Disallow names prefixed with ``T``.
  E.g. use ``AnyStrT`` instead of ``TAnyStr``.

  Refs #7322 (`#7322 <https://github.com/pylint-dev/pylint/issues/7322>`_`)


False Negatives Fixed
---------------------

- Emit ``used-before-assignment`` when relying on a name that is reimported later in a function.

  Closes #4624 (`#4624 <https://github.com/pylint-dev/pylint/issues/4624>`_)
- Emit ``used-before-assignment`` for self-referencing named expressions (``:=``) lacking
  prior assignments.

  Closes #5653 (`#5653 <https://github.com/pylint-dev/pylint/issues/5653>`_)
- Emit ``used-before-assignment`` for self-referencing assignments under if conditions.

  Closes #6643 (`#6643 <https://github.com/pylint-dev/pylint/issues/6643>`_)
- Emit ``modified-iterating-list`` and analogous messages for dicts and sets when iterating
  literals, or when using the ``del`` keyword.

  Closes #6648 (`#6648 <https://github.com/pylint-dev/pylint/issues/6648>`_)
- Emit ``used-before-assignment`` when calling nested functions before assignment.

  Closes #6812 (`#6812 <https://github.com/pylint-dev/pylint/issues/6812>`_)
- Emit ``nonlocal-without-binding`` when a nonlocal name has been assigned at a later point in the same scope.

  Closes #6883 (`#6883 <https://github.com/pylint-dev/pylint/issues/6883>`_)
- Emit ``using-constant-test`` when testing the truth value of a variable or call result
  holding a generator.

  Closes #6909 (`#6909 <https://github.com/pylint-dev/pylint/issues/6909>`_)
- Rename ``unhashable-dict-key`` to ``unhashable-member`` and emit when creating sets and dicts,
  not just when accessing dicts.

  Closes #7034, Closes #7055 (`#7034 <https://github.com/pylint-dev/pylint/issues/7034>`_)


Other Bug Fixes
---------------

- Fix a failure to lint packages with ``__init__.py`` contained in directories lacking ``__init__.py``.

  Closes #1667 (`#1667 <https://github.com/pylint-dev/pylint/issues/1667>`_)
- Fixed a syntax-error crash that was not handled properly when the declared encoding of a file
  was ``utf-9``.

  Closes #3860 (`#3860 <https://github.com/pylint-dev/pylint/issues/3860>`_)
- Fix a crash in the ``not-callable`` check when there is ambiguity whether an instance is being incorrectly provided to ``__new__()``.

  Closes #7109 (`#7109 <https://github.com/pylint-dev/pylint/issues/7109>`_)
- Fix crash when regex option raises a `re.error` exception.

  Closes #7202 (`#7202 <https://github.com/pylint-dev/pylint/issues/7202>`_)
- Fix `undefined-loop-variable` from walrus in comprehension test.

  Closes #7222 (`#7222 <https://github.com/pylint-dev/pylint/issues/7222>`_)
- Check for `<cwd>` before removing first item from `sys.path` in `modify_sys_path`.

  Closes #7231 (`#7231 <https://github.com/pylint-dev/pylint/issues/7231>`_)
- Fix sys.path pollution in parallel mode.

  Closes #7246 (`#7246 <https://github.com/pylint-dev/pylint/issues/7246>`_)
- Prevent `useless-parent-delegation` for delegating to a builtin
  written in C (e.g. `Exception.__init__`) with non-self arguments.

  Closes #7319 (`#7319 <https://github.com/pylint-dev/pylint/issues/7319>`_)


Other Changes
-------------

- ``bad-exception-context`` has been renamed to ``bad-exception-cause`` as it is about the cause and not the context.

  Closes #3694 (`#3694 <https://github.com/pylint-dev/pylint/issues/3694>`_)
- The message for ``literal-comparison`` is now more explicit about the problem and the
  solution.

  Closes #5237 (`#5237 <https://github.com/pylint-dev/pylint/issues/5237>`_)
- ``useless-super-delegation`` has been renamed to ``useless-parent-delegation`` in order to be more generic.

  Closes #6953 (`#6953 <https://github.com/pylint-dev/pylint/issues/6953>`_)
- Pylint now uses ``towncrier`` for changelog generation.

  Refs #6974 (`#6974 <https://github.com/pylint-dev/pylint/issues/6974>`_)
- Update ``astroid`` to 2.12.

  Refs #7153 (`#7153 <https://github.com/pylint-dev/pylint/issues/7153>`_)
- Fix crash when a type-annotated `__slots__` with no value is declared.

  Closes #7280 (`#7280 <https://github.com/pylint-dev/pylint/issues/7280>`_)


Internal Changes
----------------

- Fixed an issue where it was impossible to update functional tests output when the existing
  output was impossible to parse. Instead of raising an error we raise a warning message and
  let the functional test fail with a default value.

  Refs #6891 (`#6891 <https://github.com/pylint-dev/pylint/issues/6891>`_)
- ``pylint.testutils.primer`` is now a private API.

  Refs #6905 (`#6905 <https://github.com/pylint-dev/pylint/issues/6905>`_)
- We changed the way we handle the changelog internally by using towncrier.
  If you're a contributor you won't have to fix merge conflicts in the
  changelog anymore.

  Closes #6974 (`#6974 <https://github.com/pylint-dev/pylint/issues/6974>`_)
- Pylint is now using Scorecards to implement security recommendations from the
  `OpenSSF <https://openssf.org/>`_. This is done in order to secure our supply chains using a combination
  of automated tooling and best practices, most of which were already implemented before.

  Refs #7267 (`#7267 <https://github.com/pylint-dev/pylint/issues/7267>`_)
````

## File: doc/whatsnew/2/2.16/index.rst
````
***************************
 What's New in Pylint 2.16
***************************

.. toctree::
   :maxdepth: 2

:Release: 2.16
:Date: 2023-02-01

Summary -- Release highlights
=============================

In 2.16.0 we added aggregation and composition understanding in ``pyreverse``, and a way to clear
the cache in between run in server mode (originally for the VS Code integration). Apart from the bug
fixes there's also a lot of new checks, and new extensions that have been asked for for a long time
that were implemented.

If you want to benefit from all the new checks load the following plugins::

    pylint.extensions.dict_init_mutate,
    pylint.extensions.dunder,
    pylint.extensions.typing,
    pylint.extensions.magic_value,

We still welcome any community effort to help review, integrate, and add good/bad examples to the doc for
<https://github.com/pylint-dev/pylint/issues/5953>`_. This should be doable without any ``pylint`` or ``astroid``
knowledge, so this is the perfect entrypoint if you want to contribute to ``pylint`` or open source without
any experience with our code!

Last but not least @clavedeluna and @nickdrozd became triagers, welcome to the team !

.. towncrier release notes start

What's new in Pylint 2.16.4?
----------------------------
Release date: 2023-03-06


False Positives Fixed
---------------------

- Fix false positive for isinstance-second-argument-not-valid-type with union
  types.

  Closes #8205 (`#8205 <https://github.com/pylint-dev/pylint/issues/8205>`_)


What's new in Pylint 2.16.3?
----------------------------
Release date: 2023-03-03


False Positives Fixed
---------------------

- Fix false positive for ``wrong-spelling-in-comment`` with class names in a
  python 2 type comment.

  Closes #8370 (`#8370 <https://github.com/pylint-dev/pylint/issues/8370>`_)



Other Bug Fixes
---------------

- Prevent emitting ``invalid-name`` for the line on which a ``global``
  statement is declared.

  Closes #8307 (`#8307 <https://github.com/pylint-dev/pylint/issues/8307>`_)


What's new in Pylint 2.16.2?
----------------------------
Release date: 2023-02-13


New Features
------------

- Add `--version` option to `pyreverse`.

  Refs #7851 (`#7851 <https://github.com/pylint-dev/pylint/issues/7851>`_)



False Positives Fixed
---------------------

- Fix false positive for ``used-before-assignment`` when
  ``typing.TYPE_CHECKING`` is used with if/elif/else blocks.

  Closes #7574 (`#7574 <https://github.com/pylint-dev/pylint/issues/7574>`_)

- Fix false positive for ``used-before-assignment`` for named expressions
  appearing after the first element in a list, tuple, or set.

  Closes #8252 (`#8252 <https://github.com/pylint-dev/pylint/issues/8252>`_)



Other Bug Fixes
---------------

- Fix ``used-before-assignment`` false positive when the walrus operator
  is used with a ternary operator in dictionary key/value initialization.

  Closes #8125 (`#8125 <https://github.com/pylint-dev/pylint/issues/8125>`_)

- Fix ``no-name-in-module`` false positive raised when a package defines a
  variable with the
  same name as one of its submodules.

  Closes #8148 (`#8148 <https://github.com/pylint-dev/pylint/issues/8148>`_)

- Fix ``nested-min-max`` suggestion message to indicate it's possible to splat
  iterable objects.

  Closes #8168 (`#8168 <https://github.com/pylint-dev/pylint/issues/8168>`_)

- Fix a crash happening when a class attribute was negated in the start
  argument of an enumerate.

  Closes #8207 (`#8207 <https://github.com/pylint-dev/pylint/issues/8207>`_)


What's new in Pylint 2.16.1?
----------------------------
Release date: 2023-02-02


Other Bug Fixes
---------------

- Fix a crash happening for python interpreter < 3.9 following a failed typing
  update.

  Closes #8161 (`#8161 <https://github.com/pylint-dev/pylint/issues/8161>`_)


What's new in Pylint 2.16.0?
----------------------------
Release date: 2023-02-01


Changes requiring user actions
------------------------------

- The ``accept-no-raise-doc`` option related to ``missing-raises-doc`` will now
  be correctly taken into account all the time.

  Pylint will no longer raise missing-raises-doc (W9006) when no exceptions are
  documented and accept-no-raise-doc is true (issue #7208).
  If you were expecting missing-raises-doc errors to be raised in that case,
  you
  will now have to add ``accept-no-raise-doc=no`` in your configuration to keep
  the same behavior.

  Closes #7208 (`#7208 <https://github.com/pylint-dev/pylint/issues/7208>`_)



New Features
------------

- Added the ``no-header`` output format. If enabled with
  ``--output-format=no-header``, it will not include the module name in the
  output.

  Closes #5362 (`#5362 <https://github.com/pylint-dev/pylint/issues/5362>`_)

- Added configuration option ``clear-cache-post-run`` to support server-like
  usage.
  Use this flag if you expect the linted files to be altered between runs.

  Refs #5401 (`#5401 <https://github.com/pylint-dev/pylint/issues/5401>`_)

- Add ``--allow-reexport-from-package`` option to configure the
  ``useless-import-alias`` check not to emit a warning if a name
  is reexported from a package.

  Closes #6006 (`#6006 <https://github.com/pylint-dev/pylint/issues/6006>`_)

- Update ``pyreverse`` to differentiate between aggregations and compositions.
  ``pyreverse`` checks if it's an Instance or a Call of an object via method
  parameters (via type hints)
  to decide if it's a composition or an aggregation.

  Refs #6543 (`#6543 <https://github.com/pylint-dev/pylint/issues/6543>`_)



New Checks
----------

- Adds a ``pointless-exception-statement`` check that emits a warning when an
  Exception is created and not assigned, raised or returned.

  Refs #3110 (`#3110 <https://github.com/pylint-dev/pylint/issues/3110>`_)

- Add a ``shadowed-import`` message for aliased imports.

  Closes #4836 (`#4836 <https://github.com/pylint-dev/pylint/issues/4836>`_)

- Add new check called ``unbalanced-dict-unpacking`` to check for unbalanced
  dict unpacking
  in assignment and for loops.

  Closes #5797 (`#5797 <https://github.com/pylint-dev/pylint/issues/5797>`_)

- Add new checker ``positional-only-arguments-expected`` to check for cases
  when
  positional-only arguments have been passed as keyword arguments.

  Closes #6489 (`#6489 <https://github.com/pylint-dev/pylint/issues/6489>`_)

- Added ``singledispatch-method`` which informs that ``@singledispatch`` should
  decorate functions and not class/instance methods.
  Added ``singledispatchmethod-function`` which informs that
  ``@singledispatchmethod`` should decorate class/instance methods and not
  functions.

  Closes #6917 (`#6917 <https://github.com/pylint-dev/pylint/issues/6917>`_)

- Rename ``broad-except`` to ``broad-exception-caught`` and add new checker
  ``broad-exception-raised``
  which will warn if general exceptions ``BaseException`` or ``Exception`` are
  raised.

  Closes #7494 (`#7494 <https://github.com/pylint-dev/pylint/issues/7494>`_)

- Added ``nested-min-max`` which flags ``min(1, min(2, 3))`` to simplify to
  ``min(1, 2, 3)``.

  Closes #7546 (`#7546 <https://github.com/pylint-dev/pylint/issues/7546>`_)

- Extended ``use-dict-literal`` to also warn about call to ``dict()`` when
  passing keyword arguments.

  Closes #7690 (`#7690 <https://github.com/pylint-dev/pylint/issues/7690>`_)

- Add ``named-expr-without-context`` check to emit a warning if a named
  expression is used outside a context like ``if``, ``for``, ``while``, or
  a comprehension.

  Refs #7760 (`#7760 <https://github.com/pylint-dev/pylint/issues/7760>`_)

- Add ``invalid-slice-step`` check to warn about a slice step value of ``0``
  for common builtin sequences.

  Refs #7762 (`#7762 <https://github.com/pylint-dev/pylint/issues/7762>`_)

- Add ``consider-refactoring-into-while-condition`` check to recommend
  refactoring when
  a while loop is defined with a constant condition with an immediate ``if``
  statement to check for ``break`` condition as a first statement.

  Closes #8015 (`#8015 <https://github.com/pylint-dev/pylint/issues/8015>`_)



Extensions
----------

- Add new extension checker ``dict-init-mutate`` that flags mutating a
  dictionary immediately
  after the dictionary was created.

  Closes #2876 (`#2876 <https://github.com/pylint-dev/pylint/issues/2876>`_)

- Added ``bad-dunder-name`` extension check, which flags bad or misspelled
  dunder methods.
  You can use the ``good-dunder-names`` option to allow specific dunder names.

  Closes #3038 (`#3038 <https://github.com/pylint-dev/pylint/issues/3038>`_)

- Added ``consider-using-augmented-assign`` check for ``CodeStyle`` extension
  which flags ``x = x + 1`` to simplify to ``x += 1``.
  This check is disabled by default. To use it, load the code style extension
  with ``load-plugins=pylint.extensions.code_style`` and add
  ``consider-using-augmented-assign`` in the ``enable`` option.

  Closes #3391 (`#3391 <https://github.com/pylint-dev/pylint/issues/3391>`_)

- Add ``magic-number`` plugin checker for comparison with constants instead of
  named constants or enums.
  You can use it with ``--load-plugins=pylint.extensions.magic_value``.

  Closes #7281 (`#7281 <https://github.com/pylint-dev/pylint/issues/7281>`_)

- Add ``redundant-typehint-argument`` message for `typing` plugin for duplicate
  assign typehints.
  Enable the plugin to enable the message with:
  ``--load-plugins=pylint.extensions.typing``.

  Closes #7636 (`#7636 <https://github.com/pylint-dev/pylint/issues/7636>`_)



False Positives Fixed
---------------------

- Fix false positive for ``unused-variable`` and ``unused-import`` when a name
  is only used in a string literal type annotation.

  Closes #3299 (`#3299 <https://github.com/pylint-dev/pylint/issues/3299>`_)

- Document a known false positive for ``useless-suppression`` when disabling
  ``line-too-long`` in a module with only comments and no code.

  Closes #3368 (`#3368 <https://github.com/pylint-dev/pylint/issues/3368>`_)

- ``trailing-whitespaces`` is no longer reported within strings.

  Closes #3822 (`#3822 <https://github.com/pylint-dev/pylint/issues/3822>`_)

- Fix false positive for ``global-variable-not-assigned`` when a global
  variable is re-assigned via an ``ImportFrom`` node.

  Closes #4809 (`#4809 <https://github.com/pylint-dev/pylint/issues/4809>`_)

- Fix false positive for ``use-maxsplit-arg`` with custom split method.

  Closes #4857 (`#4857 <https://github.com/pylint-dev/pylint/issues/4857>`_)

- Fix ``logging-fstring-interpolation`` false positive raised when logging and
  f-string with ``%s`` formatting.

  Closes #4984 (`#4984 <https://github.com/pylint-dev/pylint/issues/4984>`_)

- Fix false-positive for ``used-before-assignment`` in pattern matching
  with a guard.

  Closes #5327 (`#5327 <https://github.com/pylint-dev/pylint/issues/5327>`_)

- Fix ``use-sequence-for-iteration`` when unpacking a set with ``*``.

  Closes #5788 (`#5788 <https://github.com/pylint-dev/pylint/issues/5788>`_)

- Fix ``deprecated-method`` false positive when alias for method is similar to
  name of deprecated method.

  Closes #5886 (`#5886 <https://github.com/pylint-dev/pylint/issues/5886>`_)

- Fix false positive ``assigning-non-slot`` when a class attribute is
  re-assigned.

  Closes #6001 (`#6001 <https://github.com/pylint-dev/pylint/issues/6001>`_)

- Fix false positive for ``too-many-function-args`` when a function call is
  assigned to a class attribute inside the class where the function is defined.

  Closes #6592 (`#6592 <https://github.com/pylint-dev/pylint/issues/6592>`_)

- Fixes false positive ``abstract-method`` on Protocol classes.

  Closes #7209 (`#7209 <https://github.com/pylint-dev/pylint/issues/7209>`_)

- Pylint now understands the ``kw_only`` keyword argument for ``dataclass``.

  Closes #7290, closes #6550, closes #5857 (`#7290
  <https://github.com/pylint-dev/pylint/issues/7290>`_)

- Fix false positive for ``undefined-loop-variable`` in ``for-else`` loops that
  use a function
  having a return type annotation of ``NoReturn`` or ``Never``.

  Closes #7311 (`#7311 <https://github.com/pylint-dev/pylint/issues/7311>`_)

- Fix ``used-before-assignment`` for functions/classes defined in type checking
  guard.

  Closes #7368 (`#7368 <https://github.com/pylint-dev/pylint/issues/7368>`_)

- Fix false positive for ``unhashable-member`` when subclassing ``dict`` and
  using the subclass as a dictionary key.

  Closes #7501 (`#7501 <https://github.com/pylint-dev/pylint/issues/7501>`_)

- Fix the message for ``unnecessary-dunder-call`` for ``__aiter__`` and
  ``__aneext__``. Also
  only emit the warning when ``py-version`` >= 3.10.

  Closes #7529 (`#7529 <https://github.com/pylint-dev/pylint/issues/7529>`_)

- Fix ``used-before-assignment`` false positive when else branch calls
  ``sys.exit`` or similar terminating functions.

  Closes #7563 (`#7563 <https://github.com/pylint-dev/pylint/issues/7563>`_)

- Fix a false positive for ``used-before-assignment`` for imports guarded by
  ``typing.TYPE_CHECKING`` later used in variable annotations.

  Closes #7609 (`#7609 <https://github.com/pylint-dev/pylint/issues/7609>`_)

- Fix a false positive for ``simplify-boolean-expression`` when multiple values
  are inferred for a constant.

  Closes #7626 (`#7626 <https://github.com/pylint-dev/pylint/issues/7626>`_)

- ``unnecessary-list-index-lookup`` will not be wrongly emitted if
  ``enumerate`` is called with ``start``.

  Closes #7682 (`#7682 <https://github.com/pylint-dev/pylint/issues/7682>`_)

- Don't warn about ``stop-iteration-return`` when using ``next()`` over
  ``itertools.cycle``.

  Closes #7765 (`#7765 <https://github.com/pylint-dev/pylint/issues/7765>`_)

- Fixes ``used-before-assignment`` false positive when the walrus operator
  is used in a ternary operator.

  Closes #7779 (`#7779 <https://github.com/pylint-dev/pylint/issues/7779>`_)

- Fix ``missing-param-doc`` false positive when function parameter has an
  escaped underscore.

  Closes #7827 (`#7827 <https://github.com/pylint-dev/pylint/issues/7827>`_)

- Fixes ``method-cache-max-size-none`` false positive for methods inheriting
  from ``Enum``.

  Closes #7857 (`#7857 <https://github.com/pylint-dev/pylint/issues/7857>`_)

- ``multiple-statements`` no longer triggers for function stubs using inlined
  ``...``.

  Closes #7860 (`#7860 <https://github.com/pylint-dev/pylint/issues/7860>`_)

- Fix a false positive for ``used-before-assignment`` when a name guarded by
  ``if TYPE_CHECKING:`` is used as a type annotation in a function body and
  later re-imported in the same scope.

  Closes #7882 (`#7882 <https://github.com/pylint-dev/pylint/issues/7882>`_)

- Prevent ``used-before-assignment`` when imports guarded by ``if
  TYPE_CHECKING``
  are guarded again when used.

  Closes #7979 (`#7979 <https://github.com/pylint-dev/pylint/issues/7979>`_)

- Fixes false positive for ``try-except-raise`` with multiple exceptions in one
  except statement if exception are in different namespace.

  Closes #8051 (`#8051 <https://github.com/pylint-dev/pylint/issues/8051>`_)

- Fix ``invalid-name`` errors for ``typing_extension.TypeVar``.

  Refs #8089 (`#8089 <https://github.com/pylint-dev/pylint/issues/8089>`_)

- Fix ``no-kwoa`` false positive for context managers.

  Closes #8100 (`#8100 <https://github.com/pylint-dev/pylint/issues/8100>`_)

- Fix a false positive for ``redefined-variable-type`` when ``async`` methods
  are present.

  Closes #8120 (`#8120 <https://github.com/pylint-dev/pylint/issues/8120>`_)



False Negatives Fixed
---------------------

- Code following a call to  ``quit``,  ``exit``, ``sys.exit`` or ``os._exit``
  will be marked as `unreachable`.

  Refs #519 (`#519 <https://github.com/pylint-dev/pylint/issues/519>`_)

- Emit ``used-before-assignment`` when function arguments are redefined inside
  an inner function and accessed there before assignment.

  Closes #2374 (`#2374 <https://github.com/pylint-dev/pylint/issues/2374>`_)

- Fix a false negative for ``unused-import`` when one module used an import in
  a type annotation that was also used in another module.

  Closes #4150 (`#4150 <https://github.com/pylint-dev/pylint/issues/4150>`_)

- Flag ``superfluous-parens`` if parentheses are used during string
  concatenation.

  Closes #4792 (`#4792 <https://github.com/pylint-dev/pylint/issues/4792>`_)

- Emit ``used-before-assignment`` when relying on names only defined under
  conditions always testing false.

  Closes #4913 (`#4913 <https://github.com/pylint-dev/pylint/issues/4913>`_)

- ``consider-using-join`` can now be emitted for non-empty string separators.

  Closes #6639 (`#6639 <https://github.com/pylint-dev/pylint/issues/6639>`_)

- Emit ``used-before-assignment`` for further imports guarded by
  ``TYPE_CHECKING``

  Previously, this message was only emitted for imports guarded directly under
  ``TYPE_CHECKING``, not guarded two if-branches deep, nor when
  ``TYPE_CHECKING``
  was imported from ``typing`` under an alias.

  Closes #7539 (`#7539 <https://github.com/pylint-dev/pylint/issues/7539>`_)

- Fix a false negative for ``unused-import`` when a constant inside
  ``typing.Annotated`` was treated as a reference to an import.

  Closes #7547 (`#7547 <https://github.com/pylint-dev/pylint/issues/7547>`_)

- ``consider-using-any-or-all`` message will now be raised in cases when
  boolean is initialized, reassigned during loop, and immediately returned.

  Closes #7699 (`#7699 <https://github.com/pylint-dev/pylint/issues/7699>`_)

- Extend ``invalid-slice-index`` to emit an warning for invalid slice indices
  used with string and byte sequences, and range objects.

  Refs #7762 (`#7762 <https://github.com/pylint-dev/pylint/issues/7762>`_)

- Fixes ``unnecessary-list-index-lookup`` false negative when ``enumerate`` is
  called with ``iterable`` as a kwarg.

  Closes #7770 (`#7770 <https://github.com/pylint-dev/pylint/issues/7770>`_)

- ``no-else-return`` or ``no-else-raise`` will be emitted if ``except`` block
  always returns or raises.

  Closes #7788 (`#7788 <https://github.com/pylint-dev/pylint/issues/7788>`_)

- Fix ``dangerous-default-value`` false negative when ``*`` is used.

  Closes #7818 (`#7818 <https://github.com/pylint-dev/pylint/issues/7818>`_)

- ``consider-using-with`` now triggers for ``pathlib.Path.open``.

  Closes #7964 (`#7964 <https://github.com/pylint-dev/pylint/issues/7964>`_)



Other Bug Fixes
---------------

- Fix bug in detecting ``unused-variable`` when iterating on variable.

  Closes #3044 (`#3044 <https://github.com/pylint-dev/pylint/issues/3044>`_)

- Fix bug in scanning of names inside arguments to ``typing.Literal``.
  See https://peps.python.org/pep-0586/#literals-enums-and-forward-references
  for details.

  Refs #3299 (`#3299 <https://github.com/pylint-dev/pylint/issues/3299>`_)

- Update ``disallowed-name`` check to flag module-level variables.

  Closes #3701 (`#3701 <https://github.com/pylint-dev/pylint/issues/3701>`_)

- Pylint will no longer deadlock if a parallel job is killed but fail
  immediately instead.

  Closes #3899 (`#3899 <https://github.com/pylint-dev/pylint/issues/3899>`_)

- Fix ignored files being linted when passed on stdin.

  Closes #4354 (`#4354 <https://github.com/pylint-dev/pylint/issues/4354>`_)

- Fix ``no-member`` false negative when augmented assign is done manually,
  without ``+=``.

  Closes #4562 (`#4562 <https://github.com/pylint-dev/pylint/issues/4562>`_)

- Any assertion on a populated tuple will now receive a ``assert-on-tuple``
  warning.

  Closes #4655 (`#4655 <https://github.com/pylint-dev/pylint/issues/4655>`_)

- ``missing-return-doc``, ``missing-raises-doc`` and ``missing-yields-doc`` now
  respect
  the ``no-docstring-rgx`` option.

  Closes #4743 (`#4743 <https://github.com/pylint-dev/pylint/issues/4743>`_)

- Update ``reimported`` help message for clarity.

  Closes #4836 (`#4836 <https://github.com/pylint-dev/pylint/issues/4836>`_)

- ``consider-iterating-dictionary`` will no longer be raised if bitwise
  operations are used.

  Closes #5478 (`#5478 <https://github.com/pylint-dev/pylint/issues/5478>`_)

- Using custom braces in ``msg-template`` will now work properly.

  Closes #5636 (`#5636 <https://github.com/pylint-dev/pylint/issues/5636>`_)

- Pylint will now filter duplicates given to it before linting. The output
  should
  be the same whether a file is given/discovered multiple times or not.

  Closes #6242, #4053 (`#6242 <https://github.com/pylint-dev/pylint/issues/6242>`_)

- Remove ``__index__`` dunder method call from ``unnecessary-dunder-call``
  check.

  Closes #6795 (`#6795 <https://github.com/pylint-dev/pylint/issues/6795>`_)

- Fixed handling of ``--`` as separator between positional arguments and flags.
  This was not actually fixed in 2.14.5.

  Closes #7003, Refs #7096 (`#7003
  <https://github.com/pylint-dev/pylint/issues/7003>`_)

- Don't crash on ``OSError`` in config file discovery.

  Closes #7169 (`#7169 <https://github.com/pylint-dev/pylint/issues/7169>`_)

- Messages sent to reporter are now copied so a reporter cannot modify the
  message sent to other reporters.

  Closes #7214 (`#7214 <https://github.com/pylint-dev/pylint/issues/7214>`_)

- Fixed a case where custom plugins specified by command line could silently
  fail.

  Specifically, if a plugin relies on the ``init-hook`` option changing
  ``sys.path`` before
  it can be imported, this will now emit a ``bad-plugin-value`` message. Before
  this
  change, it would silently fail to register the plugin for use, but would load
  any configuration, which could have unintended effects.

  Fixes part of #7264. (`#7264 <https://github.com/pylint-dev/pylint/issues/7264>`_)

- Update ``modified_iterating`` checker to fix a crash with ``for`` loops on
  empty list.

  Closes #7380 (`#7380 <https://github.com/pylint-dev/pylint/issues/7380>`_)

- Update wording for ``arguments-differ`` and ``arguments-renamed`` to clarify
  overriding object.

  Closes #7390 (`#7390 <https://github.com/pylint-dev/pylint/issues/7390>`_)

- ``disable-next`` is now correctly scoped to only the succeeding line.

  Closes #7401 (`#7401 <https://github.com/pylint-dev/pylint/issues/7401>`_)

- Fixed a crash in the ``unhashable-member`` checker when using a ``lambda`` as
  a dict key.

  Closes #7453 (`#7453 <https://github.com/pylint-dev/pylint/issues/7453>`_)

- Add ``mailcap`` to deprecated modules list.

  Closes #7457 (`#7457 <https://github.com/pylint-dev/pylint/issues/7457>`_)

- Fix a crash in the ``modified-iterating-dict`` checker involving instance
  attributes.

  Closes #7461 (`#7461 <https://github.com/pylint-dev/pylint/issues/7461>`_)

- ``invalid-class-object`` does not crash anymore when ``__class__`` is
  assigned alongside another variable.

  Closes #7467 (`#7467 <https://github.com/pylint-dev/pylint/issues/7467>`_)

- ``--help-msg`` now accepts a comma-separated list of message IDs again.

  Closes #7471 (`#7471 <https://github.com/pylint-dev/pylint/issues/7471>`_)

- Allow specifying non-builtin exceptions in the ``overgeneral-exception``
  option
  using an exception's qualified name.

  Closes #7495 (`#7495 <https://github.com/pylint-dev/pylint/issues/7495>`_)

- Report ``no-self-argument`` rather than ``no-method-argument`` for methods
  with variadic arguments.

  Closes #7507 (`#7507 <https://github.com/pylint-dev/pylint/issues/7507>`_)

- Fixed an issue where ``syntax-error`` couldn't be raised on files with
  invalid encodings.

  Closes #7522 (`#7522 <https://github.com/pylint-dev/pylint/issues/7522>`_)

- Fix false positive for ``redefined-outer-name`` when aliasing ``typing``
  e.g. as ``t`` and guarding imports under ``t.TYPE_CHECKING``.

  Closes #7524 (`#7524 <https://github.com/pylint-dev/pylint/issues/7524>`_)

- Fixed a crash of the ``modified_iterating`` checker when iterating on a set
  defined as a class attribute.

  Closes #7528 (`#7528 <https://github.com/pylint-dev/pylint/issues/7528>`_)

- Use ``py-version`` to determine if a message should be emitted for messages
  defined with ``max-version`` or ``min-version``.

  Closes #7569 (`#7569 <https://github.com/pylint-dev/pylint/issues/7569>`_)

- Improve ``bad-thread-instantiation`` check to warn if ``target`` is not
  passed in as a keyword argument
  or as a second argument.

  Closes #7570 (`#7570 <https://github.com/pylint-dev/pylint/issues/7570>`_)

- Fixes edge case of custom method named ``next`` raised an astroid error.

  Closes #7610 (`#7610 <https://github.com/pylint-dev/pylint/issues/7610>`_)

- Fixed a multi-processing crash that prevents using any more than 1 thread on
  MacOS.

  The returned module objects and errors that were cached by the linter plugin
  loader
  cannot be reliably pickled. This means that ``dill`` would throw an error
  when
  attempting to serialise the linter object for multi-processing use.

  Closes #7635. (`#7635 <https://github.com/pylint-dev/pylint/issues/7635>`_)

- Fix crash that happened when parsing files with unexpected encoding starting
  with 'utf' like ``utf13``.

  Closes #7661 (`#7661 <https://github.com/pylint-dev/pylint/issues/7661>`_)

- Fix a crash when a child class with an ``__init__`` method inherits from a
  parent class with an ``__init__`` class attribute.

  Closes #7742 (`#7742 <https://github.com/pylint-dev/pylint/issues/7742>`_)

- Fix ``valid-metaclass-classmethod-first-arg`` default config value from "cls"
  to "mcs"
  which would cause both a false-positive and false-negative.

  Closes #7782 (`#7782 <https://github.com/pylint-dev/pylint/issues/7782>`_)

- Fixes a crash in the ``unnecessary_list_index_lookup`` check when using
  ``enumerate`` with ``start`` and a class attribute.

  Closes #7821 (`#7821 <https://github.com/pylint-dev/pylint/issues/7821>`_)

- Fixes a crash in ``stop-iteration-return`` when the ``next`` builtin is
  called without arguments.

  Closes #7828 (`#7828 <https://github.com/pylint-dev/pylint/issues/7828>`_)

- When pylint exit due to bad arguments being provided the exit code will now
  be the expected ``32``.

  Refs #7931 (`#7931 <https://github.com/pylint-dev/pylint/issues/7931>`_)

- Fixes a ``ModuleNotFound`` exception when running pylint on a Django project
  with the ``pylint_django`` plugin enabled.

  Closes #7938 (`#7938 <https://github.com/pylint-dev/pylint/issues/7938>`_)

- Fixed a crash when inferring a value and using its qname on a slice that was
  being incorrectly called.

  Closes #8067 (`#8067 <https://github.com/pylint-dev/pylint/issues/8067>`_)

- Use better regex to check for private attributes.

  Refs #8081 (`#8081 <https://github.com/pylint-dev/pylint/issues/8081>`_)

- Fix issue with new typing Union syntax in runtime context for Python 3.10+.

  Closes #8119 (`#8119 <https://github.com/pylint-dev/pylint/issues/8119>`_)



Other Changes
-------------

- Pylint now provides basic support for Python 3.11.

  Closes #5920 (`#5920 <https://github.com/pylint-dev/pylint/issues/5920>`_)

- Update message for ``abstract-method`` to include child class name.

  Closes #7124 (`#7124 <https://github.com/pylint-dev/pylint/issues/7124>`_)

- Update Pyreverse's dot and plantuml printers to detect when class methods are
  abstract and show them with italic font.
  For the dot printer update the label to use html-like syntax.

  Closes #7346 (`#7346 <https://github.com/pylint-dev/pylint/issues/7346>`_)

- The ``docparams`` extension now considers typing in Numpy style docstrings
  as "documentation" for the ``missing-param-doc`` message.

  Refs #7398 (`#7398 <https://github.com/pylint-dev/pylint/issues/7398>`_)

- Relevant ``DeprecationWarnings`` are now raised with ``stacklevel=2``, so
  they have the callsite attached in the message.

  Closes #7463 (`#7463 <https://github.com/pylint-dev/pylint/issues/7463>`_)

- Add a ``minimal`` option to ``pylint-config`` and its toml generator.

  Closes #7485 (`#7485 <https://github.com/pylint-dev/pylint/issues/7485>`_)

- Add method name to the error messages of ``no-method-argument`` and
  ``no-self-argument``.

  Closes #7507 (`#7507 <https://github.com/pylint-dev/pylint/issues/7507>`_)

- Prevent leaving the pip install cache in the Docker image.

  Refs #7544 (`#7544 <https://github.com/pylint-dev/pylint/issues/7544>`_)

- Add a keyword-only ``compare_constants`` argument to ``safe_infer``.

  Refs #7626 (`#7626 <https://github.com/pylint-dev/pylint/issues/7626>`_)

- Add ``default_enabled`` option to optional message dict. Provides an option
  to disable a checker message by default.
  To use a disabled message, the user must enable it explicitly by adding the
  message to the ``enable`` option.

  Refs #7629 (`#7629 <https://github.com/pylint-dev/pylint/issues/7629>`_)

- Sort ``--generated-rcfile`` output.

  Refs #7655 (`#7655 <https://github.com/pylint-dev/pylint/issues/7655>`_)

- epylint is now deprecated and will be removed in pylint 3.0.0. All emacs and
  flymake related
  files were removed and their support will now happen in an external
  repository :
  https://github.com/emacsorphanage/pylint.

  Closes #7737 (`#7737 <https://github.com/pylint-dev/pylint/issues/7737>`_)

- Adds test for existing preferred-modules configuration functionality.

  Refs #7957 (`#7957 <https://github.com/pylint-dev/pylint/issues/7957>`_)



Internal Changes
----------------

- Add and fix regression tests for plugin loading.

  This shores up the tests that cover the loading of custom plugins as affected
  by any changes made to the ``sys.path`` during execution of an ``init-hook``.
  Given the existing contract of allowing plugins to be loaded by fiddling with
  the path in this way, this is now the last bit of work needed to close Github
  issue #7264.

  Closes #7264 (`#7264 <https://github.com/pylint-dev/pylint/issues/7264>`_)
````

## File: doc/whatsnew/2/2.17/index.rst
````
***************************
 What's New in Pylint 2.17
***************************

.. toctree::
   :maxdepth: 2

:Release: 2.17
:Date: 2023-03-08

Summary -- Release highlights
=============================

2.17 is a small release that is the first to support python 3.11
officially with the addition of TryStar nodes.

There's still two new default checks: ``bad-chained-comparison`` and
``implicit-flag-alias``, one of them already fixed a previously
undetected bug in sentry.

Thanks to the community effort our documentation is almost complete,
and every messages should have a proper documentation now. A big thank
you to everyone who participated !

The next release is going to be ``3.0.0``, bring breaking changes and enact long
announced deprecations. There's going to be frequent beta releases,
before the official releases, everyone is welcome to try the betas
so we find problems before the actual release.

.. towncrier release notes start

What's new in Pylint 2.17.7?
----------------------------
Release date: 2023-09-30


False Positives Fixed
---------------------

- Fix a regression in pylint 2.17.6 / astroid 2.15.7 causing various
  messages for code involving ``TypeVar``.

  Closes #9069 (`#9069 <https://github.com/pylint-dev/pylint/issues/9069>`_)



Other Bug Fixes
---------------

- Fix crash in refactoring checker when unary operand used with variable in for
  loop.

  Closes #9074 (`#9074 <https://github.com/pylint-dev/pylint/issues/9074>`_)


What's new in Pylint 2.17.6?
----------------------------
Release date: 2023-09-24


Other Bug Fixes
---------------

- When parsing comma-separated lists of regular expressions in the config,
  ignore
  commas that are inside braces since those indicate quantifiers, not
  delineation
  between expressions.

  Closes #7229 (`#7229 <https://github.com/pylint-dev/pylint/issues/7229>`_)

- ``sys.argv`` is now always correctly considered as impossible to infer
  (instead of
  using the actual values given to pylint).

  Closes #7710 (`#7710 <https://github.com/pylint-dev/pylint/issues/7710>`_)

- Don't show class fields more than once in Pyreverse diagrams.

  Closes #8189 (`#8189 <https://github.com/pylint-dev/pylint/issues/8189>`_)

- Don't show arrows more than once in Pyreverse diagrams.

  Closes #8522 (`#8522 <https://github.com/pylint-dev/pylint/issues/8522>`_)

- Don't show duplicate type annotations in Pyreverse diagrams.

  Closes #8888 (`#8888 <https://github.com/pylint-dev/pylint/issues/8888>`_)

- Don't add `Optional` to `|` annotations with `None` in Pyreverse diagrams.

  Closes #9014 (`#9014 <https://github.com/pylint-dev/pylint/issues/9014>`_)


What's new in Pylint 2.17.5?
----------------------------
Release date: 2023-07-26


False Positives Fixed
---------------------

- Fix a false positive for ``unused-variable`` when there is an import in a
  ``if TYPE_CHECKING:`` block and ``allow-global-unused-variables`` is set to
  ``no`` in the configuration.

  Closes #8696 (`#8696 <https://github.com/pylint-dev/pylint/issues/8696>`_)

- Fix false positives generated when supplying arguments as ``**kwargs`` to IO
  calls like open().

  Closes #8719 (`#8719 <https://github.com/pylint-dev/pylint/issues/8719>`_)

- Fix a false positive where pylint was ignoring method calls annotated as
  ``NoReturn`` during the ``inconsistent-return-statements`` check.

  Closes #8747 (`#8747 <https://github.com/pylint-dev/pylint/issues/8747>`_)

- Exempt parents with only type annotations from the ``invalid-enum-extension``
  message.

  Closes #8830 (`#8830 <https://github.com/pylint-dev/pylint/issues/8830>`_)



Other Bug Fixes
---------------

- Fixed crash when a call to ``super()`` was placed after an operator (e.g.
  ``not``).

  Closes #8554 (`#8554 <https://github.com/pylint-dev/pylint/issues/8554>`_)

- Fix crash for ``modified-while-iterating`` checker when deleting
  members of a dict returned from a call.

  Closes #8598 (`#8598 <https://github.com/pylint-dev/pylint/issues/8598>`_)

- Fix crash in ``invalid-metaclass`` check when a metaclass had duplicate
  bases.

  Closes #8698 (`#8698 <https://github.com/pylint-dev/pylint/issues/8698>`_)

- Avoid ``consider-using-f-string`` on modulos with brackets in template.

  Closes #8720. (`#8720 <https://github.com/pylint-dev/pylint/issues/8720>`_)

- Fix a crash when ``__all__`` exists but cannot be inferred.

  Closes #8740 (`#8740 <https://github.com/pylint-dev/pylint/issues/8740>`_)

- Fix crash when a variable is assigned to a class attribute of identical name.

  Closes #8754 (`#8754 <https://github.com/pylint-dev/pylint/issues/8754>`_)

- Fixed a crash when calling ``copy.copy()`` without arguments.

  Closes #8774 (`#8774 <https://github.com/pylint-dev/pylint/issues/8774>`_)



Other Changes
-------------

- Fix a crash when a ``nonlocal`` is defined at module-level.

  Closes #8735 (`#8735 <https://github.com/pylint-dev/pylint/issues/8735>`_)


What's new in Pylint 2.17.4?
----------------------------
Release date: 2023-05-06


False Positives Fixed
---------------------

- Fix a false positive for ``bad-dunder-name`` when there is a user-defined
  ``__index__`` method.

  Closes #8613 (`#8613 <https://github.com/pylint-dev/pylint/issues/8613>`_)



Other Bug Fixes
---------------

- ``pyreverse``: added escaping of vertical bar character in annotation labels
  produced by DOT printer to ensure it is not treated as field separator of
  record-based nodes.

  Closes #8603 (`#8603 <https://github.com/pylint-dev/pylint/issues/8603>`_)

- Fixed a crash when generating a configuration file:
  ``tomlkit.exceptions.TOMLKitError: Can't add a table to a dotted key``
  caused by tomlkit ``v0.11.8``.

  Closes #8632 (`#8632 <https://github.com/pylint-dev/pylint/issues/8632>`_)


What's new in Pylint 2.17.3?
----------------------------
Release date: 2023-04-24


False Positives Fixed
---------------------

- Fix `unused-argument` false positive when `__new__` does not use all the
  arguments of `__init__`.

  Closes #3670 (`#3670 <https://github.com/pylint-dev/pylint/issues/3670>`_)

- Fix ``unused-import`` false positive for usage of ``six.with_metaclass``.

  Closes #7506 (`#7506 <https://github.com/pylint-dev/pylint/issues/7506>`_)

- `logging-not-lazy` is not longer emitted for explicitly concatenated string
  arguments.

  Closes #8410 (`#8410 <https://github.com/pylint-dev/pylint/issues/8410>`_)

- Fix false positive for isinstance-second-argument-not-valid-type when union
  types contains None.

  Closes #8424 (`#8424 <https://github.com/pylint-dev/pylint/issues/8424>`_)

- Fixed `unused-import` so that it observes the `dummy-variables-rgx` option.

  Closes #8500 (`#8500 <https://github.com/pylint-dev/pylint/issues/8500>`_)

- `Union` typed variables without assignment are no longer treated as
  `TypeAlias`.

  Closes #8540 (`#8540 <https://github.com/pylint-dev/pylint/issues/8540>`_)

- Fix false positive for ``positional-only-arguments-expected`` when a function
  contains both a positional-only parameter that has a default value, and
  ``**kwargs``.

  Closes #8555 (`#8555 <https://github.com/pylint-dev/pylint/issues/8555>`_)

- Fix false positive for ``keyword-arg-before-vararg`` when a positional-only
  parameter with a default value precedes ``*args``.

  Closes #8570 (`#8570 <https://github.com/pylint-dev/pylint/issues/8570>`_)



Other Bug Fixes
---------------

- Improve output of ``consider-using-generator`` message for ``min()`` calls
  with ``default`` keyword.

  Closes #8563 (`#8563 <https://github.com/pylint-dev/pylint/issues/8563>`_)


What's new in Pylint 2.17.2?
----------------------------
Release date: 2023-04-03


False Positives Fixed
---------------------

- ``invalid-name`` now allows for integers in ``typealias`` names:
  - now valid: ``Good2Name``, ``GoodName2``.
  - still invalid: ``_1BadName``.

  Closes #8485 (`#8485 <https://github.com/pylint-dev/pylint/issues/8485>`_)

- No longer consider ``Union`` as type annotation as type alias for naming
  checks.

  Closes #8487 (`#8487 <https://github.com/pylint-dev/pylint/issues/8487>`_)

- ``unnecessary-lambda`` no longer warns on lambdas which use its parameters in
  their body (other than the final arguments), e.g.
  ``lambda foo: (bar if foo else baz)(foo)``.

  Closes #8496 (`#8496 <https://github.com/pylint-dev/pylint/issues/8496>`_)



Other Bug Fixes
---------------

- Fix a crash in pyreverse when "/" characters are used in the output filename
  e.g pyreverse -o png -p name/ path/to/project.

  Closes #8504 (`#8504 <https://github.com/pylint-dev/pylint/issues/8504>`_)


What's new in Pylint 2.17.1?
----------------------------
Release date: 2023-03-22


False Positives Fixed
---------------------

- Adds ``asyncSetUp`` to the default ``defining-attr-methods`` list to silence
  ``attribute-defined-outside-init`` warning when using
  ``unittest.IsolatedAsyncioTestCase``.

  Refs #8403 (`#8403 <https://github.com/pylint-dev/pylint/issues/8403>`_)



Other Bug Fixes
---------------

- ``--clear-cache-post-run`` now also clears LRU caches for pylint utilities
  holding references to AST nodes.

  Closes #8361 (`#8361 <https://github.com/pylint-dev/pylint/issues/8361>`_)

- Fix a crash when ``TYPE_CHECKING`` is used without importing it.

  Closes #8434 (`#8434 <https://github.com/pylint-dev/pylint/issues/8434>`_)

- Fix a regression of ``preferred-modules`` where a partial match was used
  instead of the required full match.

  Closes #8453 (`#8453 <https://github.com/pylint-dev/pylint/issues/8453>`_)



Internal Changes
----------------

- The following utilities are deprecated in favor of the more robust
  ``in_type_checking_block``
  and will be removed in pylint 3.0:

    - ``is_node_in_guarded_import_block``
    - ``is_node_in_typing_guarded_import_block``
    - ``is_typing_guard``

  ``is_sys_guard`` is still available, which was part of
  ``is_node_in_guarded_import_block``.

  Refs #8433 (`#8433 <https://github.com/pylint-dev/pylint/issues/8433>`_)


What's new in Pylint 2.17.0?
----------------------------
Release date: 2023-03-08


New Features
------------

- `pyreverse` now supports custom color palettes with the `--color-palette`
  option.

  Closes #6738 (`#6738 <https://github.com/pylint-dev/pylint/issues/6738>`_)

- Add ``invalid-name`` check for ``TypeAlias`` names.

  Closes #7081. (`#7081 <https://github.com/pylint-dev/pylint/issues/7081>`_)

- Accept values of the form ``<class name>.<attribute name>`` for the
  ``exclude-protected`` list.

  Closes #7343 (`#7343 <https://github.com/pylint-dev/pylint/issues/7343>`_)

- Add `--version` option to `pyreverse`.

  Refs #7851 (`#7851 <https://github.com/pylint-dev/pylint/issues/7851>`_)

- Adds new functionality with preferred-modules configuration to detect
  submodules.

  Refs #7957 (`#7957 <https://github.com/pylint-dev/pylint/issues/7957>`_)

- Support implicit namespace packages (PEP 420).

  Closes #8154 (`#8154 <https://github.com/pylint-dev/pylint/issues/8154>`_)

- Add globbing pattern support for ``--source-roots``.

  Closes #8290 (`#8290 <https://github.com/pylint-dev/pylint/issues/8290>`_)

- Support globbing pattern when defining which file/directory/module to lint.

  Closes #8310 (`#8310 <https://github.com/pylint-dev/pylint/issues/8310>`_)

- pylint now supports ``TryStar`` nodes from Python 3.11 and should be fully
  compatible with Python 3.11.

  Closes #8387 (`#8387 <https://github.com/pylint-dev/pylint/issues/8387>`_)



New Checks
----------

- Add a ``bad-chained-comparison`` check that emits a warning when
  there is a chained comparison where one expression is semantically
  incompatible with the other.

  Closes #6559 (`#6559 <https://github.com/pylint-dev/pylint/issues/6559>`_)

- Adds an ``implicit-flag-alias`` check that emits a warning when a class
  derived from ``enum.IntFlag`` assigns distinct integer values that share
  common bit positions.

  Refs #8102 (`#8102 <https://github.com/pylint-dev/pylint/issues/8102>`_)



False Positives Fixed
---------------------

- Fix various false positives for functions that return directly from
  structural pattern matching cases.

  Closes #5288 (`#5288 <https://github.com/pylint-dev/pylint/issues/5288>`_)

- Fix false positive for ``used-before-assignment`` when
  ``typing.TYPE_CHECKING`` is used with if/elif/else blocks.

  Closes #7574 (`#7574 <https://github.com/pylint-dev/pylint/issues/7574>`_)

- Fix false positive for isinstance-second-argument-not-valid-type with union
  types.

  Closes #8205 (`#8205 <https://github.com/pylint-dev/pylint/issues/8205>`_)

- Fix false positive for ``used-before-assignment`` for named expressions
  appearing after the first element in a list, tuple, or set.

  Closes #8252 (`#8252 <https://github.com/pylint-dev/pylint/issues/8252>`_)

- Fix false positive for ``wrong-spelling-in-comment`` with class names in a
  python 2 type comment.

  Closes #8370 (`#8370 <https://github.com/pylint-dev/pylint/issues/8370>`_)



False Negatives Fixed
---------------------

- Fix a false negative for 'missing-parentheses-for-call-in-test' when
  inference
  failed for the internal of the call as we did not need that information to
  raise
  correctly.

  Refs #8185 (`#8185 <https://github.com/pylint-dev/pylint/issues/8185>`_)

- Fix false negative for inconsistent-returns with while-loops.

  Closes #8280 (`#8280 <https://github.com/pylint-dev/pylint/issues/8280>`_)



Other Bug Fixes
---------------

- Fix ``used-before-assignment`` false positive when the walrus operator
  is used with a ternary operator in dictionary key/value initialization.

  Closes #8125 (`#8125 <https://github.com/pylint-dev/pylint/issues/8125>`_)

- Fix ``no-name-in-module`` false positive raised when a package defines a
  variable with the
  same name as one of its submodules.

  Closes #8148 (`#8148 <https://github.com/pylint-dev/pylint/issues/8148>`_)

- Fix a crash happening for python interpreter < 3.9 following a failed typing
  update.

  Closes #8161 (`#8161 <https://github.com/pylint-dev/pylint/issues/8161>`_)

- Fix ``nested-min-max`` suggestion message to indicate it's possible to splat
  iterable objects.

  Closes #8168 (`#8168 <https://github.com/pylint-dev/pylint/issues/8168>`_)

- Fix a crash happening when a class attribute was negated in the start
  argument of an enumerate.

  Closes #8207 (`#8207 <https://github.com/pylint-dev/pylint/issues/8207>`_)

- Prevent emitting ``invalid-name`` for the line on which a ``global``
  statement is declared.

  Closes #8307 (`#8307 <https://github.com/pylint-dev/pylint/issues/8307>`_)



Other Changes
-------------

- Update explanation for ``global-variable-not-assigned`` and add confidence.

  Closes #5073 (`#5073 <https://github.com/pylint-dev/pylint/issues/5073>`_)

- The governance model and the path to become a maintainer have been documented
  as
  part of our effort to guarantee that the software supply chain in which
  pylint is
  included is secure.

  Refs #8329 (`#8329 <https://github.com/pylint-dev/pylint/issues/8329>`_)
````

## File: doc/whatsnew/2/2.2/full.rst
````
Full changelog
==============

What's New in Pylint 2.2.2?
---------------------------
Release date: 2018-11-28

* Change the ``logging-format-style`` to use name identifier instead of their
  corresponding Python identifiers

  This is to prevent users having to think about escaping the default value for
  ``logging-format-style`` in the generated config file. Also our config parsing
  utilities don't quite support escaped values when it comes to ``choices`` detection,
  so this would have needed various hacks around that.

  Closes #2614


What's New in Pylint 2.2.1?
---------------------------
Release date: 2018-11-27

* Fix a crash caused by ``implicit-str-concat-in-sequence`` and multi-bytes characters.

  Closes #2610


What's New in Pylint 2.2?
-------------------------

Release date: 2018-11-25

* Consider ``range()`` objects for ``undefined-loop-variable`` leaking from iteration.

  Closes #2533

* ``deprecated-method`` can use the attribute name for identifying a deprecated method

 Previously we were using the fully qualified name, which we still do, but the fully
 qualified name for some ``unittest`` deprecated aliases leads to a generic
 deprecation function. Instead on relying on that, we now also rely on the attribute
 name, which should solve some false positives.

  Closes #1653
  Closes #1946

* Fix compatibility with changes to stdlib tokenizer.

* ``pylint`` is less eager to consume the whole line for pragmas

  Closes #2485

* Obtain the correct number of CPUs for virtualized or containerized environments.

  Closes #2519

* Change ``unbalanced-tuple-unpacking`` back to a warning.

 It used to be a warning until a couple of years ago, after it was promoted to
 an error. But the check might be suggesting the wrong thing in some cases,
 for instance when checking against ``sys.argv`` which cannot be known at static
 analysis time. Given it might rely on potential unknown data, it's best to
 have it as a warning.

  Closes #2522

* Remove ``enumerate`` usage suggestion when defining ``__iter__`` (C0200)

  Closes #2477

* Emit ``too-many-starred-assignment`` only when the number of Starred nodes is per assignment elements

  Closes #2513

* ``try-except-raise`` checker now handles multilevel inheritance hirerachy for exceptions correctly.

  Closes #2484

* Add a new check, ``simplifiable-if-expression`` for expressions like ``True if cond else False``.

  Closes #2487

* ``too-few-public-methods`` is not reported for ``typing.NamedTuple``

  Closes #2459

* ```too-few-public-methods`` is not reported for dataclasses created with options.

  Closes #2488

* Remove wrong modules from 'bad-python3-import'.

  Closes #2453

* The ``json`` reporter prints an empty list when no messages are emitted

  Closes #2446

* Add a new check, ``duplicate-string-formatting-argument``

 This new check is emitted whenever a duplicate string formatting argument
 is found.

  Closes #497

* ``assignment-from-no-return`` is not emitted for coroutines.

  Closes #1715

* Report format string type mismatches.

* ``consider-using-ternary`` and ``simplified-boolean-expression`` no longer emit for sequence based checks

  Closes #2473

* Handle ``AstroidSyntaxError`` when trying to import a module.

  Closes #2313

* Allow ``__module__`` to be redefined at a class level.

  Closes #2451

* ``pylint`` used to emit an ``unused-variable`` error if unused import was found in the function. Now instead of
  ``unused-variable``, ``unused-import`` is emitted.

  Closes #2421

* Handle asyncio.coroutine when looking for ``not-an-iterable`` check.

  Closes #996

* The ``locally-enabled`` check is gone.

  Closes #2442

* Infer decorated methods when looking for method-hidden

  Closes #2369

* Pick the latest value from the inferred values when looking for ``raising-non-exception``

  Closes #2431

* Extend the TYPE_CHECKING guard to TYPE_CHECKING name as well, not just the attribute

  Closes #2411

* Ignore import x.y.z as z cases for checker ``useless-import-alias``.

  Closes #2309

* Fix false positive ``undefined-variable`` and ``used-before-assignment`` with nonlocal keyword usage.

  Closes #2049

* Stop ``protected-access`` exception for missing class attributes

* Don't emit ``assignment-from-no-return`` for decorated function nodes

  Closes #2385

* ``unnecessary-pass`` is now also emitted when a function or class contains only docstring and pass statement.

  In Python, stubbed functions often have a body that contains just a single ``pass`` statement,
  indicating that the function doesn't do anything. However, a stubbed function can also have just a
  docstring, and function with a docstring and no body also does nothing.

  Closes #2208

* ``duplicate-argument-name`` is emitted for more than one duplicate argument per function

  Closes #1712

* Allow double indentation levels for more distinguishable indentations

  Closes #741

* Consider tuples in exception handler for ``try-except-raise``.

  Closes #2389

* Fix astroid.ClassDef check in checkers.utils.is_subclass_of

* Fix wildcard imports being ignored by the import checker

* Fix external/internal distinction being broken in the import graph

* Fix wildcard import check not skipping ``__init__.py``

  Closes #2430

* Add new option to logging checker, ``logging_format_style``

* Fix --ignore-imports to understand multi-line imports

  Closes #1422
  Closes #2019

* Add a new check 'implicit-str-concat-in-sequence' to spot string concatenation inside lists, sets & tuples.

* ``literal-comparison`` is now emitted for 0 and 1 literals.
````

## File: doc/whatsnew/2/2.2/index.rst
````
**************************
  What's New In Pylint 2.2
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.2/summary.rst
````
:Release: 2.2
:Date: 2018-11-25

Summary -- Release highlights
=============================


New checkers
============

* String checker now reports format string type mismatches.

* ``duplicate-string-formatting-argument`` was added for detecting duplicate string
  formatting arguments that should be passed instead as named arguments.

* ``logging-format-style`` is a new option for the logging checker for usage of
  str.format() style format strings in calls to loggers.

  It accepts two options: ``--logging-format-style=old`` for using `%` style formatting,
  which is the assumed default, and ``--logging-format-style=new`` for using `{}` style formatting.

* ``implicit-str-concat-in-sequence`` detects string concatenation inside lists, sets & tuples.

  Example of code that would generate such warning:

  .. code-block:: python

    woops = ('a', 'b' 'c')


Other Changes
=============

* ``try-except-raise`` checker now handles multilevel inheritance hirerachy for exceptions correctly.

  Closes #2484

* Ignore import x.y.z as z cases for checker ``useless-import-alias``.

* ``unnecessary-pass`` is now also emitted when a function or class contains only docstring and pass statement,
  in which case, docstring is enough for empty definition.

* Fix false positive ``undefined-variable`` and ``used-before-assignment`` with nonlocal keyword usage.

* Fix exceptions being raised when one of the params is not a ClassDef for ``checkers.utils.is_subclass_of``.

* ``pylint`` now picks the latest value from the inferred values of the exception that gets
  raised, when looking for ``raising-non-exception``. This helps when reusing a variable name
  for multiple types, since ``pylint`` was picking just the first inferred value, leading
  to spurious false positives.

  Closes #2431

* ``pylint`` used to emit a ``not-an-iterable`` error when looking at coroutines built
  with ``asyncio.coroutine``. This is no longer the case as we handle coroutines explicitly.

  Closes #996

* ``pylint`` used to emit an ``unused-variable`` error if unused import was found in the function. Now instead of
  ``unused-variable``, ``unused-import`` is emitted.

  Closes #2421
````

## File: doc/whatsnew/2/2.3/full.rst
````
Full changelog
==============

What's New in Pylint 2.3.0?
---------------------------
Release date: 2019-02-27

* Protect against ``NonDeducibleTypeHierarchy`` when calling semi-private ``is_subtype``

  ``astroid.helpers.is_subtype`` raises ``NonDeducibleTypeHierarchy`` when it cannot infer
  the base classes of the given types, but that makes sense in its context given that
  the method is mostly used to inform the inference process about the hierarchy of classes.
  Doesn't make that much sense for ``pylint`` itself, which is why we're handling the
  exception here, rather than in ``astroid``

  Closes pylint-dev/astroid#644

* Added a new command line option ``list-groups`` for listing all the check groups ``pylint`` knows about.

* Allow ``BaseException`` for emitting ``broad-except``, just like ``Exception``.

  Closes #2741

* Fixed a crash that occurred for ``bad-str-strip-call`` when ``strip()`` received ``None``

  Closes #2743

* Don't emit ``*-not-iterating`` checks for builtins consumed by ``itertools``

  Closes #2731

* Fix a crash caused by iterating over ``Uninferable`` in a string formatting check.

  Closes #2727

* Fixed false positives for ``no-self-argument`` and ``unsubscriptable-object`` when using ``__class_getitem__`` (new in Python 3.7)

  Closes #2416

* Support ``Ellipsis`` as a synonym for ``pass`` statements.

  Closes #2718

* ``fixme`` gets triggered only on comments.

  Closes #2321

* Fixed a false positive for ``unused-variable`` and ``nonlocal`` assignments

  Closes #2671

* Added ``load_configuration()`` hook for plugins

  New optional hook for plugins is added: ``load_configuration()``.
  This hook is executed after configuration is loaded to prevent
  overwriting plugin specific configuration via user-based
  configuration.

  Closes #2635

* Fix missing-raises-doc false positive (W9006)

  Closes #1502

* Exempt starred unpacking from ``*-not-iterating`` Python 3 checks

  Closes #2651

* Make ``compare-to-zero`` less zealous by checking against equality and identity

  Closes #2645

* Add ``no-else-raise`` warning (R1720)

  Closes #2558

* Exempt ``yield from`` from ``*-not-iterating`` Python 3 checks.

  Closes #2643

* Fix incorrect generation of ``no-else-return`` warnings (R1705)

  Fixed issue where ``if`` statements with nested ``if`` statements
  were incorrectly being flagged as ``no-else-return`` in some cases and
  not being flagged as ``no-else-return`` in other cases.  Added tests
  for verification and updated pylint source files to eliminate newly
  exposed warnings.

* Fix false positive with ``not-async-context-manager`` caused by not understanding ``contextlib.asynccontextmanager``

  Closes #2440

* Refactor ``bad-reversed-sequence`` to account for more objects that can define ``__reversed__``

  One such object would be an enum class, for which ``__reversed__`` yields each individual enum.
  As such, the check for ``bad-reversed-sequence`` needs to not differentiate between classes
  and instances when it comes for checking of ``__reversed__`` presence.

  Closes #2598

* Added ``wrong-exception-operation``

  Used when an operation is done against an exception, but the operation
  is not valid for the exception in question. Usually emitted when having
  binary operations between exceptions in except handlers.

  Closes #2494

* ``no-member`` is emitted for enums when they lack a member

  Previously we weren't doing this because we detected a
  ``__getattr__`` implementation on the ``Enum`` class
  (and this check is skipped for classes with ``__getattr__``),
  but that is fine for Enums, given that they are inferred in a customised
  way in astroid.

  Closes #2565

* Generalize ``chained-comparison``

  Previous version incorrectly detects `a < b < c and b < d` and fails to
  detect `a < b < c and c < d`.

* Avoid popping __main__ when using multiple jobs

  Closes #2689

* Add a new option 'check-str-concat-over-line-jumps' to check 'implicit-str-concat-in-sequence'

* Fixes for the new style logging format linter.

  The number of arguments was not handled properly, leading to an always
  successful check.

* Fix false positive ``not-callable`` for uninferable properties.

* Fix false positive ``useless-else-on-loop`` if the break is deep in the else
  of an inner loop.

* Minor improvements to the help text for a few options.
````

## File: doc/whatsnew/2/2.3/index.rst
````
**************************
  What's New In Pylint 2.3
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.3/summary.rst
````
:Release: 2.3
:Date: 2019-02-27


Summary -- Release highlights
=============================

* This release improves the performance of the 2.X series after it was affected by a performance regression a couple of releases ago.

New checkers
============

* We added a new check message ``wrong-exception-operation``.
  This is emitted when an operation is done against an exception, but the operation
  is not valid for the exception in question. Usually emitted when having
  binary operations between exceptions in except handlers.

  Closes #2494

* We added a new ``no-else-raise`` warning similar to ``no-else-return``

  Closes #2558

* We added a new option ``check-str-concat-over-line-jumps`` to check
  ``implicit-str-concat-in-sequence`` over multiple lines.


Other Changes
=============

Quite a lot of bug fixes and improvements went into this release, here's a handful of them.
For the full changes, check the full changelog.

* We no longer emit ``*-not-iterating`` checks for builtins consumed by ``itertools``

* We fixed some false positives for ``no-self-argument`` and ``unsubscriptable-object``
  when using ``__class_getitem__`` (new in Python 3.7)

* ``pylint`` now supports ``Ellipsis`` as a synonym for ``pass`` statements.

* ``fixme`` gets triggered only on comments.

* ``pylint`` exempts starred unpacking from ``*-not-iterating`` Python 3 checks.

* ``compare-to-zero`` is now less zealous by checking against equality and identity.

*``yield from`` is exempted from ``*-not-iterating`` Python 3 checks.

* A false positive with ``not-async-context-manager`` caused by not understanding
  ``contextlib.asynccontextmanager`` was fixed.

* We refactored ``bad-reversed-sequence`` to account for more objects that can define ``__reversed__``.

* ``no-member`` is now emitted for enums when they lack a member.

* Plugins can now use the ``load_configuration()`` hook.
  This hook is executed after configuration is loaded to prevent overwriting plugin
  specific configuration via user-based configuration.

* There's a new command line option ``list-groups`` for listing all the check groups
  ``pylint`` knows about. This is useful to know what groups you can disable or enable
  individually.
````

## File: doc/whatsnew/2/2.4/full.rst
````
Full changelog
==============

What's New in Pylint 2.4.4?
---------------------------
Release date: 2019-11-13

* Exempt all the names found in type annotations from ``unused-import``

  The previous code was assuming that only ``typing`` names need to be
  exempted, but we need to do that for the rest of the type comment
  names as well.

  Closes #3112

* Relax type import detection for names that do not come from the ``typing`` module

  Closes #3191


What's New in Pylint 2.4.3?
---------------------------
Release date: 2019-10-18

* Fix an issue with ``unnecessary-comprehension`` in comprehensions with additional repacking of elements.

  Closes #3148

* ``import-outside-toplevel`` is emitted for ``ImportFrom`` nodes as well.

  Closes #3175

* Do not emit ``no-method-argument`` for functions using positional only args.

  Closes #3161

* ``consider-using-sys-exit`` is no longer emitted when ``exit`` is imported in the local scope.

  Closes #3147

* ``invalid-overridden-method`` takes ``abc.abstractproperty`` in account

  Closes #3150

* Fixed ``missing-yield-type-doc`` getting incorrectly raised when
  a generator does not document a yield type but has a type annotation.

  Closes #3185

* ``typing.overload`` functions are exempted from ``too-many-function-args``

  Closes #3170


What's New in Pylint 2.4.2?
---------------------------
Release date: 2019-09-30


* ``ignored-modules`` can skip submodules.

  Closes #3135

* ``self-assigning-variable`` skips class level assignments.

  Closes #2930

* ``consider-using-sys-exit`` is exempted when ``exit()`` is imported from ``sys``

  Closes #3145

* Exempt annotated assignments without variable from ``class-variable-slots-conflict``

  Closes #3141

* Fix ``utils.is_error`` to account for functions returning early.

  This fixes a false negative with ``unused-variable`` which was no longer triggered
  when a function raised an exception as the last instruction, but the body of the function
  still had unused variables.

  Closes #3028


What's New in Pylint 2.4.1?
---------------------------
Release date: 2019-09-25


* Exempt type checking definitions defined in both clauses of a type checking guard

  Closes #3127


* Exempt type checking definitions inside the type check guard

  In a7f236528bb3758886b97285a56f3f9ce5b13a99 we added basic support
  for emitting ``used-before-assignment`` if a variable was only defined
  inside a type checking guard (using ``TYPE_CHECKING`` variable from `typing`)
  Unfortunately that missed the case of using those type checking imports
  inside the guard itself, which triggered spurious used-before-assignment errors.

  Closes #3119

* Require astroid >= 2.3 to avoid any compatibility issues.


What's New in Pylint 2.4.0?
---------------------------
Release date: 2019-09-24

* New check: ``import-outside-toplevel``

  This check warns when modules are imported from places other than a
  module toplevel, e.g. inside a function or a class.

* Handle inference ambiguity for ``invalid-format-index``

  Closes #2752

* Removed Python 2 specific checks such as ``relative-import``,
  ``invalid-encoded-data``, ``missing-super-argument``.

* Support forward references for ``function-redefined`` check.

  Closes #2540

* Handle redefinitions in case of type checking imports.

  Closes #2834

* Added a new check, ``consider-using-sys-exit``

  This check is emitted when we detect that a quit() or exit() is invoked
  instead of sys.exit(), which is the preferred way of exiting in program.

  Closes #2925

* ``useless-suppression`` check now ignores ``cyclic-import`` suppressions,
  which could lead to false positives due to incomplete context at the time
  of the check.

  Closes #3064

* Added new checks, ``no-else-break`` and ``no-else-continue``

  These checks highlight unnecessary ``else`` and ``elif`` blocks after
  ``break`` and ``continue`` statements.

  Closes #2327

* Don't emit ``protected-access`` when a single underscore prefixed attribute
  is used inside a special method

  Closes #1802

* Fix the "statement" values in the PyLinter's stats reports by module.

* Added a new check, ``invalid-overridden-method``

  This check is emitted when we detect that a method is overridden
  as a property or a property is overridden as a method. This can indicate
  a bug in the application code that will trigger a runtime error.

  Closes #2670

* Added a new check, ``arguments-out-of-order``

  This check warns if you have arguments with names that match those in
  a function's signature but you are passing them in to the function
  in a different order.

  Closes #2975

* Added a new check, ``redeclared-assigned-name``

  This check is emitted when ``pylint`` detects that a name
  was assigned one or multiple times in the same assignment,
  which indicate a potential bug.

  Closes #2898

* Ignore lambda calls with variadic arguments without a context.

  Inferring variadic positional arguments and keyword arguments
  will result into empty Tuples and Dicts, which can lead in
  some cases to false positives with regard to no-value-for-parameter.
  In order to avoid this, until we'll have support for call context
  propagation, we're ignoring such cases if detected.
  We already did that for function calls, but the previous fix
  was not taking in consideration ``lambdas``

  Closes #2918

* Added a new check, ``self-assigning-variable``. This check is emitted
  when we detect that a variable is assigned to itself, which might
  indicate a potential bug in the code application.

  Closes #2930

* Added a new check, ``property-with-parameters``.

  This check is emitted when we detect that a defined property also
  has parameters, which are useless.

  Closes #3006

* Excluded protocol classes from a couple of checks.

  Closes #3002.

* Add a check ``unnecessary-comprehension`` that detects unnecessary comprehensions.

  This check is emitted when ``pylint`` finds list-, set- or dict-comprehensions,
  that are unnecessary and can be rewritten with the list-, set- or dict-constructors.

  Closes #2905

* Excluded PEP 526 instance and class variables from ``no-member``.

  Closes #2945

* Excluded ``attrs`` from ``too-few-public-methods`` check.

  Closes #2988.

* ``unused-import`` emitted for the right import names in function scopes.

  Closes #2928

* Dropped support for Python 3.4.

* ``assignment-from-no-return`` not triggered for async methods.

  Closes #2902

* Don't emit ``attribute-defined-outside-init`` for variables defined in setters.

  Closes #409

* Syntax errors report the column number.

  Closes #2914

* Support fully qualified typing imports for type annotations.

  Closes #2915

* Exclude ``__dict__`` from ``attribute-defined-outside-init``

* Fix pointer on spelling check when the error are more than one time in the same line.

  Closes #2895

* Fix crash happening when parent of called object cannot be determined

* Allow of in ``GoogleDocstring.re_multiple_type``

* Added ``subprocess-run-check`` to handle subrocess.run without explicitly set ``check`` keyword.

  Closes #2848

* When we can't infer bare except handlers, skip ``try-except-raise``

  Closes #2853

* Handle more ``unnecessary-lambda`` cases when dealing with additional kwargs in wrapped calls

  Closes #2845

* Better postponed evaluation of annotations handling

  Closes #2847

* Support postponed evaluation of annotations for variable annotations.

  Closes #2838

* ``epylint.py_run`` defaults to ``python`` in case the current executable is not a Python one.

  Closes #2837

* Ignore raw docstrings when running Similarities checker with ``ignore-docstrings=yes`` option

* Fix crash when calling ``inherit_from_std_ex`` on a class which is its own ancestor

  Closes #2680

* Added a new check that warns the user if a function call is used inside a test but parentheses are missing.

  Closes #2658

* ``len-as-condition`` now only fires when a ``len(x)`` call is made without an explicit comparison

  The message and description accompanying this checker has been changed
  reflect this new behavior, by explicitly asking to either rely on the
  fact that empty sequence are false or to compare the length with a scalar.

  Closes #2684

* Add ``preferred-module`` checker that notify if an import has a replacement module that should be used.

  This check is emitted when ``pylint`` finds an imported module that has a
  preferred replacement listed in ``preferred-modules``.

* ``assigning-non-slot`` not emitted for classes with unknown base classes.

  Closes #2807

* ``old-division`` is not emitted for non-Const nodes.

  Closes #2808

* Added method arguments to the dot writer for pyreverse.

  Closes #2139

* Support for linting file from stdin.

  IDEs may benefit from the support for linting from an in-memory file.

  Closes #1187

* Added a new check ``class-variable-slots-conflict``

  This check is emitted when ``pylint`` finds a class variable that conflicts with a slot
  name, which would raise a ``ValueError`` at runtime.

* Added new check: dict-iter-missing-items (E1141)

  Closes #2761

* Fix issue with pylint name in output of python -m pylint --version

  Closes #2764

* Relicense logo material under the CC BY-SA 4.0 license.

* Skip ``if`` expressions from f-strings for the ``check_elif`` checker

  Closes #2816

* C0412 (ungrouped-import) is now compatible with isort.

  Closes #2806

* Added new extension to detect too much code in a try clause

  Closes #2877

* ``signature-mutators`` option was added.
  With this option, users can choose to ignore ``too-many-function-args``, ``unexpected-keyword-arg``,
  and ``no-value-for-parameter`` for functions decorated with decorators that change
  the signature of a decorated function.

  Closes #259

* Fixed a pragma comment on its own physical line being ignored when part
  of a logical line with the previous physical line.

  Closes #199

* Fixed false ``undefined-loop-variable`` for a function defined in the loop,
  that uses the variable defined in that loop.

  Closes #202

* Fixed ``unused-argument`` and ``function-redefined`` getting raised for
  functions decorated with ``typing.overload``.

  Closes #1581

* Fixed a false positive with ``consider-using-dict-comprehension`` for constructions that can't be converted to a comprehension

  Closes #2963

* Added ``__post_init__`` to ``defining-attr-methods`` in order to avoid ``attribute-defined-outside-init`` in dataclasses.

  Closes #2581

* Changed description of W0199 to use the term 2-item-tuple instead of 2-uple.

* Allow a ``.`` as a prefix for Sphinx name resolution.

* Checkers must now keep a 1 to 1 relationship between "msgid" (ie: C1234) and "symbol" (i.e. : human-readable-symbol)

* In checkers, an old_names can now be used for multiple new messages and pylint is now a little faster

  It means if you do a partial old_names for a message definition an exception will tell you that you
  must rename the associated identification.

* Allow the choice of f-strings as a valid way of formatting logging strings.

  Closes #2395

* Added ``--list-msgs-enabled`` command to list all enabled and disabled messages given the current RC file and command line arguments.
````

## File: doc/whatsnew/2/2.4/index.rst
````
**************************
  What's New In Pylint 2.4
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.4/summary.rst
````
:Release: 2.4
:Date: 2019-09-24


Summary -- Release highlights
=============================


New checkers
============

* ``import-outside-toplevel``

  This check warns when modules are imported from places other than a
  module toplevel, e.g. inside a function or a class.

* Added a new check, ``consider-using-sys-exit``

  This check is emitted when we detect that a quit() or exit() is invoked
  instead of sys.exit(), which is the preferred way of exiting in program.

  Closes #2925

* Added a new check, ``arguments-out-of-order``

  This check warns if you have arguments with names that match those in
  a function's signature but you are passing them in to the function
  in a different order.

  Closes #2975

* Added new checks, ``no-else-break`` and ``no-else-continue``

  These checks highlight unnecessary ``else`` and ``elif`` blocks after
  ``break`` and ``continue`` statements.

  Closes #2327

* Added ``unnecessary-comprehension`` that detects unnecessary comprehensions.

  This check is emitted when ``pylint`` finds list-, set- or dict-comprehensions,
  that are unnecessary and can be rewritten with the list-, set- or dict-constructors.

  Closes #2905

* Added a new check, ``invalid-overridden-method``

  This check is emitted when we detect that a method is overridden
  as a property or a property is overridden as a method. This can indicate
  a bug in the application code that will trigger a runtime error.

  Closes #2670

* Added a new check, ``redeclared-assigned-name``

  This check is emitted when ``pylint`` detects that a name was assigned one or multiple times in the same assignment,
  which indicate a potential bug.

  Closes #2898

* Added a new check, ``self-assigning-variable``

  This check is emitted when we detect that a variable is assigned
  to itself, which might indicate a potential bug in the code application.

  For example, the following would raise this warning::

    def new_a(attr, attr2):
      a_inst = Aclass()
      a_inst.attr2 = attr2
      # should be: a_inst.attr = attr, but have a typo
      attr = attr
      return a_inst

  Closes #2930

* Added a new check ``property-with-parameters`` which detects when a property
  has more than a single argument.

  Closes #3006

* Added ``subprocess-run-check`` to handle subprocess.run without explicitly set ``check`` keyword.

  Closes #2848

* We added a new check message ``dict-iter-missing-items``.
  This is emitted when trying to iterate through a dict in a for loop without calling its .items() method.

  Closes #2761

* We added a new check message ``missing-parentheses-for-call-in-test``.
  This is emitted in case a call to a function is made inside a test but
  it misses parentheses.

* A new check ``class-variable-slots-conflict`` was added.

  This check is emitted when ``pylint`` finds a class variable that conflicts with a slot
  name, which would raise a ``ValueError`` at runtime.

  For example, the following would raise an error::

    class A:
        __slots__ = ('first', 'second')
        first = 1

* A new check ``preferred-module`` was added.

  This check is emitted when ``pylint`` finds an imported module that has a
  preferred replacement listed in ``preferred-modules``.

  For example, you can set the preferred modules as ``xml:defusedxml,json:ujson``
  to make ``pylint`` suggest using ``defusedxml`` instead of ``xml``
  and ``ujson`` rather than ``json``.

* A new extension ``broad_try_clause`` was added.

  This extension enforces a configurable maximum number of statements inside
  of a try clause. This facilitates enforcing PEP 8's guidelines about try / except
  statements and the amount of code in the try clause.

  You can enable this extension using ``--load-plugins=pylint.extensions.broad_try_clause``
  and you can configure the amount of statements in a try statement using
  ``--max-try-statements``.


Other Changes
=============

* Don't emit ``protected-access`` when a single underscore prefixed attribute is used
  inside a special method

  Closes #1802

* ``len-as-condition`` now only fires when a ``len(x)`` call is made without an explicit comparison.

  The message and description accompanying this checker has been changed
  reflect this new behavior, by explicitly asking to either rely on the
  fact that empty sequence are false or to compare the length with a scalar.

  OK::

    if len(x) == 0:
      pass

    while not len(x) == 0:
      pass

    assert len(x) > 5, message

  KO::

    if not len(x):
      pass

    while len(x) and other_cond:
      pass

    assert len(x), message

* A file is now read from stdin if the ``--from-stdin`` flag is used on the
  command line. In addition to the ``--from-stdin`` flag a (single) file
  name needs to be specified on the command line, which is needed for the
  report.

* The checker for ungrouped imports is now more permissive.

The import can now be sorted alphabetically by import style.
This makes pylint compatible with isort.

The following imports do not trigger an ``ungrouped-imports`` anymore ::

    import unittest
    import zipfile
    from unittest import TestCase
    from unittest.mock import MagicMock

* The checker for missing return documentation is now more flexible.

The following does not trigger a ``missing-return-doc`` anymore ::

    def my_func(self):
        """This is a docstring.

        Returns
        -------
        :obj:`list` of :obj:`str`
            List of strings
        """
        return ["hi", "bye"] #@

* ``signature-mutators`` CLI and config option was added.

With this option, users can choose to ignore ``too-many-function-args``, ``unexpected-keyword-arg``,
and ``no-value-for-parameter`` for functions decorated with decorators that change
the signature of a decorated function.

For example a test may want to make use of hypothesis.
Adding ``hypothesis.extra.numpy.arrays`` to ``signature_mutators``
would mean that ``no-value-for-parameter`` would not be raised for::

    @given(img=arrays(dtype=np.float32, shape=(3, 3, 3, 3)))
    def test_image(img):
        ...

* Allow the option of f-strings as a valid logging string formatting method.

``logging-fstring--interpolation`` has been merged into
``logging-format-interpolation`` to allow the ``logging-format-style`` option
to control which logging string format style is valid.
To allow this, a new ``fstr`` value is valid for the ``logging-format-style``
option.

* ``--list-msgs-enabled`` command was added.

When enabling/disabling several messages and groups in a config file,
it can be unclear which messages are actually enabled and which are disabled.
This new command produces the final resolved lists of enabled/disabled messages,
sorted by symbol but with the ID provided for use with ``--help-msg``.
````

## File: doc/whatsnew/2/2.5/full.rst
````
Full changelog
==============

What's New in Pylint 2.5.3?
---------------------------
Release date: 2020-06-8

* Fix a regression where disable comments that have checker names with numbers in them are not parsed correctly

  Closes #3666

* ``property-with-parameters`` properly handles abstract properties

  Closes #3600

* ``continue-in-finally`` no longer emitted on Python 3.8 where it's now valid

  Closes #3612

* Fix a regression where messages with dash are not fully parsed

  Closes #3604

* In a TOML configuration file, it's now possible to use rich (non-string) types, such as list, integer or boolean instead of strings. For example, one can now define a *list* of message identifiers to enable like this::

    enable = [
        "use-symbolic-message-instead",
        "useless-suppression",
    ]

  Closes #3538

* Fix a regression where the score was not reported with multiple jobs

  Closes #3547

* Protect against ``AttributeError`` when checking ``cell-var-from-loop``

  Closes #3646


What's New in Pylint 2.5.2?
---------------------------
Release date: 2020-05-05

* ``pylint.Run`` accepts ``do_exit`` as a deprecated parameter

  Closes #3590


What's New in Pylint 2.5.1?
---------------------------
Release date: 2020-05-05

* Fix a crash in ``method-hidden`` lookup for unknown base classes

  Closes #3527

* Revert pylint.Run's ``exit`` parameter to ``do_exit``

  This has been inadvertently changed several releases ago to ``do_exit``.

  Closes #3533

* ``no-value-for-parameter`` variadic detection has improved for assign statements

  Closes #3563

* Allow package files to be properly discovered with multiple jobs

  Closes #3524

* Allow linting directories without ``__init__.py`` which was a regression in 2.5.

  Closes #3528


What's New in Pylint 2.5.0?
---------------------------
Release date: 2020-04-27

* Fix a false negative for ``undefined-variable`` when using class attribute in comprehension.

  Closes #3494

* Fix a false positive for ``undefined-variable`` when using class attribute in decorator or as type hint.

  Closes #511
  Closes #1976

* Remove HTML quoting of messages in JSON output.

  Closes #2769

* Adjust the ``invalid-name`` rule to work with non-ASCII identifiers and add the ``non-ascii-name`` rule.

  Closes #2725

* Positional-only arguments are taken in account for ``useless-super-delegation``

* ``unidiomatic-typecheck`` is no longer emitted for ``in`` and ``not in`` operators

  Closes #3337

* Positional-only argument annotations are taken in account for ``unused-import``

  Closes #3462

* Add a command to list available extensions.

* Allow used variables to be properly consumed when different checks are enabled / disabled

  Closes #3445

* Fix dangerous-default-value rule to account for keyword argument defaults

  Closes #3373

* Fix a false positive of ``self-assigning-variable`` on tuple unpacking.

  Closes #3433

* ``no-self-use`` is no longer emitted for typing stubs.

  Closes #3439

* Fix a false positive for ``undefined-variable`` when ``__class__`` is used

  Closes #3090

* Emit ``invalid-name`` for variables defined in loops at module level.

  Closes #2695

* Add a check for cases where the second argument to ``isinstance`` is not a type.

  Closes #3308

* Add 'notes-rgx' option, to be used for fixme check.

  Closes #2874

* ``function-redefined`` exempts function redefined on a condition.

  Closes #2410

* ``typing.overload`` functions are exempted from docstring checks

  Closes #3350

* Emit ``invalid-overridden-method`` for improper async def overrides.

  Closes #3355

* Do not allow ``python -m pylint ...`` to import user code

  ``python -m pylint ...`` adds the current working directory as the first element
  of ``sys.path``. This opens up a potential security hole where ``pylint`` will import
  user level code as long as that code resides in modules having the same name as stdlib
  or pylint's own modules.

  Closes #3386

* Add ``dummy-variables-rgx`` option for ``_redeclared-assigned-name`` check.

  Closes #3341

* Fixed graph creation for relative paths

* Add a check for asserts on string literals.

  Closes #3284

* ``not in`` is considered iterating context for some of the Python 3 porting checkers.

* A new check ``inconsistent-quotes`` was added.

* Add a check for non string assignment to __name__ attribute.

  Closes #583

* ``__pow__``, ``__imatmul__``, ``__trunc__``, ``__floor__``, and ``__ceil__`` are recognized as special method names.

  Closes #3281

* Added errors for protocol functions when invalid return types are detected.
  E0304 (invalid-bool-returned): __bool__ did not return a bool
  E0305 (invalid-index-returned): __index__ did not return an integer
  E0306 (invalid-repr-returned): __repr__ did not return a string
  E0307 (invalid-str-returned): __str__ did not return a string
  E0308 (invalid-bytes-returned): __bytes__ did not return a string
  E0309 (invalid-hash-returned): __hash__ did not return an integer
  E0310 (invalid-length-hint-returned): __length_hint__ did not return a non-negative integer
  E0311 (invalid-format-returned): __format__ did not return a string
  E0312 (invalid-getnewargs-returned): __getnewargs__ did not return a tuple
  E0313 (invalid-getnewargs-ex-returned): __getnewargs_ex__ did not return a tuple of the form (tuple, dict)

  Closes #560

* ``missing-*-docstring`` can look for ``__doc__`` assignments.

  Closes #3301

* ``undefined-variable`` can now find undefined loop iterables

  Closes #498

* ``safe_infer`` can infer a value as long as all the paths share the same type.

  Closes #2503

* Add a --fail-under <score> flag, also configurable in a .pylintrc file. If the final score is more than the specified score, it's considered a success and pylint exits with exitcode 0. Otherwise, it's considered a failure and pylint exits with its current exitcode based on the messages issued.

  Closes #2242

* Don't emit ``line-too-long`` for multilines when ``disable=line-too-long`` comment stands at their end

  Closes #2957

* Fixed an ``AttributeError`` caused by improper handling of ``dataclasses`` inference in ``pyreverse``

  Closes #3256

* Do not exempt bare except from ``undefined-variable`` and similar checks

  If a node was wrapped in a ``TryExcept``, ``pylint`` was taking a hint
  from the except handler when deciding to emit or not a message.
  We were treating bare except as a fully fledged ignore but only
  the corresponding exceptions should be handled that way (e.g. ``NameError`` or ``ImportError``)

  Closes #3235

* No longer emit ``assignment-from-no-return`` when a function only raises an exception

  Closes #3218

* Allow import aliases to exempt ``import-error`` when used in type annotations.

  Closes #3178

* ``Ellipsis` is exempted from ``multiple-statements`` for function overloads.

  Closes #3224

* No longer emit ``invalid-name`` for non-constants found at module level.

  Pylint was taking the following statement from PEP-8 too far, considering
  all module level variables as constants, which is not what the statement is saying:

  `Constants are usually defined on a module level and written in
  all capital letters with underscores separating words.`

  Closes #3111
  Closes #3132

* Allow ``implicit-str-concat-in-sequence`` to be emitted for string juxtaposition

  Closes #3030

* ``implicit-str-concat-in-sequence`` was renamed ``implicit-str-concat``

* The ``json`` reporter no longer bypasses ``redirect_stdout``.

  Closes #3227

* Move ``NoFileError``, ``OutputLine``, ``FunctionalTestReporter``,
  ``FunctionalTestFile``, ``LintModuleTest`` and related methods from
  ``test_functional.py`` to ``pylint.testutils`` to help testing for 3rd
  party pylint plugins.

* Can read config from a setup.cfg or pyproject.toml file.

  Closes #617

* Fix exception-escape false positive with generators

  Closes #3128

* ``inspect.getargvalues`` is no longer marked as deprecated.

* A new check ``f-string-without-interpolation`` was added

  Closes #3190

* Flag mutable ``collections.*`` utilities as dangerous defaults

  Closes #3183

* ``docparams`` extension supports multiple types in raises sections.

  Multiple types can also be separated by commas in all valid sections.

  Closes #2729

* Allow parallel linting when run under Prospector

* Fixed false positives of ``method-hidden`` when a subclass defines the method that is being hidden.

  Closes #414

* Python 3 porting mode is 30-50% faster on most codebases

* Python 3 porting mode no longer swallows syntax errors

  Closes #2956

* Pass the actual PyLinter object to sub processes to allow using custom
  PyLinter classes.

  PyLinter object (and all its members except reporter) needs to support
  pickling so the PyLinter object can be passed to worker processes.

* Clean up setup.py

  Make pytest-runner a requirement only if running tests, similar to McCabe.

  Clean up the setup.py file, resolving a number of warnings around it.

* Handle SyntaxError in files passed via ``--from-stdin`` option

  Pylint no longer outputs a traceback, if a file, read from stdin,
  contains a syntaxerror.

* Fix uppercase style to disallow 3+ uppercase followed by lowercase.

* Fixed ``undefined-variable`` and ``unused-import`` false positives
  when using a metaclass via an attribute.

  Closes #1603

* Emit ``unused-argument`` for functions that partially uses their argument list before raising an exception.

  Closes #3246

* Fixed ``broad_try_clause`` extension to check try/finally statements and to
  check for nested statements (e.g., inside of an ``if`` statement).

* Recognize classes explicitly inheriting from ``abc.ABC`` or having an
  ``abc.ABCMeta`` metaclass as abstract. This makes them not trigger W0223.

  Closes #3098

* Fix overzealous ``arguments-differ`` when overridden function uses variadics

  No message is emitted if the overriding function provides positional or
  keyword variadics in its signature that can feasibly accept and pass on
  all parameters given by the overridden function.

  Closes #1482
  Closes #1553

* Multiple types of string formatting are allowed in logging functions.

  The ``logging-fstring-interpolation`` message has been brought back to allow
  multiple types of string formatting to be used.

  Closes #3361
````

## File: doc/whatsnew/2/2.5/index.rst
````
**************************
  What's New In Pylint 2.5
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.5/summary.rst
````
:Release: 2.5
:Date: 2020-04-27


Summary -- Release highlights
=============================


New checkers
============

* A new check ``isinstance-second-argument-not-valid-type`` was added.

   This check is emitted whenever **pylint** finds a call to the ``isinstance``
   function with a second argument that is not a type. Such code is likely
   unintended as it will cause a TypeError to be thrown at runtime error.

* A new check ``assert-on-string-literal`` was added.

   This check is emitted whenever **pylint** finds an assert statement
   with a string literal as its first argument. Such assert statements
   are probably unintended as they will always pass.

* A new check ``f-string-without-interpolation`` was added.

   This check is emitted whenever **pylint** detects the use of an
   f-string without having any interpolated values in it, which means
   that the f-string can be a normal string.

* Multiple checks for invalid return types of protocol functions were added:

   * ``invalid-bool-returned``: ``__bool__`` did not return a bool
   * ``invalid-index-returned``: ``__index__`` did not return an integer
   * ``invalid-repr-returned)``: ``__repr__`` did not return a string
   * ``invalid-str-returned)``: ``__str__`` did not return a string
   * ``invalid-bytes-returned)``: ``__bytes__`` did not return a string
   * ``invalid-hash-returned)``: ``__hash__`` did not return an integer
   * ``invalid-length-hint-returned)``: ``__length_hint__`` did not return a non-negative integer
   * ``invalid-format-returned)``: ``__format__`` did not return a string
   * ``invalid-getnewargs-returned)``: ``__getnewargs__`` did not return a tuple
   * ``invalid-getnewargs-ex-returned)``: ``__getnewargs_ex__`` did not return a tuple of the form (tuple, dict)

* A new check ``inconsistent-quotes`` was added.

   This check is emitted when quotes delimiters (``"`` and ``'``) are not used
   consistently throughout a module.  It allows avoiding unnecessary escaping,
   allowing, for example, ``"Don't error"`` in a module in which single-quotes
   otherwise delimit strings so that the single quote in ``Don't`` doesn't need to be escaped.

* A new check ``non-str-assignment-to-dunder-name`` was added to ensure that only strings are assigned to ``__name__`` attributes.


Other Changes
=============

* Configuration can be read from a setup.cfg or pyproject.toml file in the current directory.
  A setup.cfg must prepend pylintrc section names with ``pylint.``, for example ``[pylint.MESSAGES CONTROL]``.
  A pyproject.toml file must prepend section names with ``tool.pylint.``, for example ``[tool.pylint.'MESSAGES CONTROL']``.
  These files can also be passed in on the command line.

* Add new ``good-names-rgx`` and ``bad-names-rgx`` to enable permitting or disallowing of names via regular expressions

  To enable better handling of permitted/disallowed names, we added two new config options: good-names-rgxs: a comma-
  separated list of regexes, that if a name matches will be exempt from naming-checking. bad-names-rgxs: a comma-
  separated list of regexes, that if a name matches will be always marked as a disallowed name.

* Mutable ``collections.*`` are now flagged as dangerous defaults.

* Add new ``--fail-under`` flag for setting the threshold for the score to fail overall tests. If the score is over the fail-under threshold, pylint will complete SystemExit with value 0 to indicate no errors.

* Added a new option ``notes-rgx`` to make fixme warnings more flexible. Now either ``notes`` or ``notes-rgx`` option can be used to detect fixme warnings.

* Non-ASCII characters are now allowed by ``invalid-name``.

* ``pylint`` no longer emits ``invalid-name`` for non-constants found at module level.

  Pylint was considering all module level variables as constants, which is not what PEP 8 is actually mandating.

* A new check ``non-ascii-name`` was added to detect identifiers with non-ASCII characters.

* Overloaded typing functions no longer trigger ``no-self-use``, ``unused-argument``, ``missing-docstring`` and similar checks
  that assumed that overloaded functions are normal functions.

* ``python -m pylint`` can no longer be made to import files from the local directory.

* A new command ``--list-extensions`` was added.

  This command lists all extensions present in ``pylint.extensions``.

* Various false positives have been fixed which you can read more about in the Changelog files.

* Multiple types of string formatting are allowed in logging functions.

The ``logging-fstring-interpolation`` message has been brought back to allow
multiple types of string formatting to be used.
The type of formatting to use is chosen through enabling and disabling messages
rather than through the logging-format-style option.
The fstr value of the logging-format-style option is not valid.
````

## File: doc/whatsnew/2/2.6/full.rst
````
Full changelog
==============

What's New in Pylint 2.6.1?
---------------------------
Release date: 2021-02-16

* Astroid version has been set as < 2.5

  Closes #4093


What's New in Pylint 2.6.0?
---------------------------
Release date: 2020-08-20

* Fix various scope-related bugs in ``undefined-variable`` checker

  Closes #1082, #3434, #3461

* bad-continuation and bad-whitespace have been removed, black or another formatter can help you with this better than Pylint

  Closes #246, #289, #638, #747, #1148, #1179, #1943, #2041, #2301, #2304, #2944, #3565

* The no-space-check option has been removed. It's no longer possible to consider empty line like a ``trailing-whitespace`` by using clever options

  Closes #1368

* ``missing-kwoa`` is no longer emitted when dealing with overload functions

  Closes #3655

* mixed-indentation has been removed, it is no longer useful since TabError is included directly in python3

  Closes #2984 #3573

* Add ``super-with-arguments`` check for flagging instances of Python 2 style super calls.

* Add an faq detailing which messages to disable to avoid duplicates w/ other popular linters

* Fix superfluous-parens false-positive for the walrus operator

  Closes #3383

* Fix ``fail-under`` not accepting floats

* Fix a bug with ``ignore-docstrings`` ignoring all lines in a module

* Fix ``pre-commit`` config that could lead to undetected duplicate lines of code

* Fix a crash in parallel mode when the module's filepath is not set

  Closes #3564

* Add ``raise-missing-from`` check for exceptions that should have a cause.

* Support both isort 4 and isort 5. If you have pinned isort 4 in your project requirements, nothing changes. If you use isort 5, though, note that the ``known-standard-library`` option is not interpreted the same in isort 4 and isort 5 (see the migration guide in isort documentation for further details). For compatibility's sake for most pylint users, the ``known-standard-library`` option in pylint now maps to ``extra-standard-library`` in isort 5. If you really want what ``known-standard-library`` now means in isort 5, you must disable the ``wrong-import-order`` check in pylint and run isort manually with a proper isort configuration file.

  Closes #3722

* Fix a crash caused by not guarding against ``InferenceError`` when calling ``infer_call_result``

  Closes #3690

* Fix a crash in parallel mode when the module's filepath is not set

  Closes #3564
````

## File: doc/whatsnew/2/2.6/index.rst
````
**************************
  What's New In Pylint 2.6
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.6/summary.rst
````
:Release: 2.6
:Date: 2020-08-20

Summary -- Release highlights
=============================

* ``bad-continuation`` and ``bad-whitespace`` have been removed. ``black`` or another formatter can help you with this better than Pylint
* Added support for isort 5

New checkers
============

* Add ``super-with-arguments`` check for flagging instances of Python 2 style super calls.

* Add ``raise-missing-from`` check for exceptions that should have a cause.

Other Changes
=============

* ``bad-continuation`` and ``bad-whitespace`` have been removed. ``black`` or another formatter can help you with this better than Pylint

* The ``no-space-check`` option has been removed, it's no longer possible to consider empty line like a ``trailing-whitespace`` by using clever options.

* ``mixed-indentation`` has been removed, it is no longer useful since TabError is included directly in python3

* Fix superfluous-parens false-positive for the walrus operator

* Add support for both isort 4 and isort 5. If you have pinned isort 4 in your project requirements, nothing changes. If you use isort 5, though, note that the ``known-standard-library`` option is not interpreted the same in isort 4 and isort 5 (see `the migration guide in isort documentation` (no longer available) for further details). For compatibility's sake for most pylint users, the ``known-standard-library`` option in pylint now maps to ``extra-standard-library`` in isort 5. If you really want what ``known-standard-library`` now means in isort 5, you must disable the ``wrong-import-order`` check in pylint and run isort manually with a proper isort configuration file.
````

## File: doc/whatsnew/2/2.7/full.rst
````
Full changelog
==============

What's New in Pylint 2.7.4?
---------------------------
Release date: 2021-03-30


* Fix a problem with disabled msgid not being ignored

  Closes #4265

* Fix issue with annotated class constants

  Closes #4264


What's New in Pylint 2.7.3?
---------------------------
Release date: 2021-03-29

* Introduce logic for checking deprecated attributes in DeprecationMixin.

* Reduce usage of blacklist/whitelist terminology. Notably, ``extension-pkg-allow-list`` is an
  alternative to ``extension-pkg-whitelist`` and the message ``blacklisted-name`` is now emitted as
  ``disallowed-name``. The previous names are accepted to maintain backward compatibility.

* Move deprecated checker to ``DeprecatedMixin``

  Closes #4086

* Bump ``astroid`` version to ``2.5.2``

* Fix false positive for ``method-hidden`` when using private attribute and method

  Closes #3936

* ``use-symbolic-message-instead`` now also works on legacy messages like ``C0111`` (``missing-docstring``).

* Remove unwanted print to stdout from ``_emit_no_member``

* Introduce a command-line option to specify pyreverse output directory

  Closes #4159

* Fix issue with Enums and ``class-attribute-naming-style=snake_case``

  Closes #4149

* Add ``allowed-redefined-builtins`` option for fine tuning ``redefined-builtin`` check.

  Closes #3263

* Fix issue when executing with ``python -m pylint``

  Closes #4161

* Exempt ``typing.TypedDict`` from ``too-few-public-methods`` check.

  Closes #4180

* Fix false-positive ``no-member`` for typed annotations without default value.

  Closes #3167

* Add ``--class-const-naming-style`` for Enum constants and class variables annotated
  with ``typing.ClassVar``

  Closes #4181

* Fix astroid.Inference error for undefined-variables with ``len()```

  Closes #4215

* Fix column index on FIXME warning messages

  Closes #4218

* Improve handling of assignment expressions, better edge case handling

  Closes #3763, #4238

* Improve check if class is subscriptable PEP585

* Fix documentation and filename handling of --import-graph

* Fix false-positive for ``unused-import`` on class keyword arguments

  Closes #3202

* Fix regression with plugins on PYTHONPATH if latter is cwd

  Closes #4252


What's New in Pylint 2.7.2?
---------------------------
Release date: 2021-02-28

* Fix False Positive on ``Enum.__members__.items()``, ``Enum.__members__.values``, and ``Enum.__members__.keys``

  Closes #4123

* Properly strip dangerous sys.path entries (not just the first one)

  Closes #3636

* Workflow and packaging improvements


What's New in Pylint 2.7.1?
---------------------------
Release date: 2021-02-23

* Expose ``UnittestLinter`` in pylint.testutils

* Don't check directories starting with '.' when using register_plugins

  Closes #4119


What's New in Pylint 2.7.0?
---------------------------
Release date: 2021-02-21

* Introduce DeprecationMixin for reusable deprecation checks.

  Closes #4049

* Fix false positive for ``builtin-not-iterating`` when ``map`` receives iterable

  Closes #4078

* Python 3.6+ is now required.

* Fix false positive for ``builtin-not-iterating`` when ``zip`` receives iterable

* Add ``nan-comparison`` check for NaN comparisons

* Bug fix for empty-comment message line number.

  Closes #4009

* Only emit ``bad-reversed-sequence`` on dictionaries if below py3.8

  Closes #3940

* Handle class decorators applied to function.

  Closes #3882

* Add check for empty comments

* Fix minor documentation issue in contribute.rst

* Enums are now required to be named in UPPER_CASE by ``invalid-name``.

  Closes #3834

* Add missing checks for deprecated functions.

* Postponed evaluation of annotations are now recognized by default if python version is above 3.10

  Closes #3992

* Fix column metadata for anomalous backslash lints

* Drop support for Python 3.5

* Add support for pep585 with postponed evaluation

  Closes #3320

* Check alternative union syntax - PEP 604

  Closes #4065

* Fix multiple false positives with assignment expressions

  Closes #3347, #3953, #3865, #3275

* Fix TypedDict inherit-non-class false-positive Python 3.9+

  Closes #1927

* Fix issue with nested PEP 585 syntax

* Fix issue with nested PEP 604 syntax

* Fix a crash in ``undefined-variable`` caused by chained attributes in metaclass

  Closes #3742

* Fix false positive for ``not-async-context-manager`` when ``contextlib.asynccontextmanager`` is used

  Closes #3862

* Fix linter multiprocessing pool shutdown (triggered warnings when ran in parallels with other pytest plugins)

  Closes #3779

* Fix a false-positive emission of ``no-self-use`` and ``unused-argument`` for methods
  of generic structural types (`Protocol[T]`)

  Closes #3885

* Fix bug that lead to duplicate messages when using ``--jobs 2`` or more.

  Closes #3584

* Adds option ``check-protected-access-in-special-methods`` in the ClassChecker to activate/deactivate
  ``protected-access`` message emission for single underscore prefixed attribute in special methods.

  Closes #3120

* Fix vulnerable regular expressions in ``pyreverse``

  Closes #3811

* ``inconsistent-return-statements`` message is now emitted if one of ``try/except`` statement
  is not returning explicitly while the other do.

  Closes #3468

* Fix ``useless-super-delegation`` false positive when default keyword argument is a dictionary.

  Closes #3773

* Fix a crash when a specified config file does not exist

* Add support to ``ignored-argument-names`` in DocstringParameterChecker and adds ``useless-param-doc`` and ``useless-type-doc`` messages.

  Closes #3800

* Enforce docparams consistently when docstring is not present

  Closes #2738

* Fix ``duplicate-code`` false positive when lines only contain whitespace and non-alphanumeric characters (e.g. parentheses, bracket, comma, etc.)

* Improve lint message for ``singleton-comparison`` with bools

* Fix spell-checker crash on indented docstring lines that look like # comments

  Closes #3786

* Fix AttributeError in checkers/refactoring.py

* Improve sphinx directives spelling filter

* Fix a bug with postponed evaluation when using aliases for annotations.

  Closes #3798

* Fix minor documentation issues

* Improve the performance of the line length check.

* Removed incorrect deprecation of ``inspect.getfullargspec``

* Fix ``signature-differs`` false positive for functions with variadics

  Closes #3737

* Fix a crash in ``consider-using-enumerate`` when encountering ``range()`` without arguments

  Closes #3735

* ``len-as-conditions`` is now triggered only for classes that are inheriting directly from list, dict, or set and not implementing the ``__bool__`` function, or from generators like range or list/dict/set comprehension. This should reduce the false positives for other classes, like pandas's DataFrame or numpy's Array.

  Closes #1879

* Fixes duplicate-errors not working with -j2+

  Closes #3314

* ``generated-members`` now matches the qualified name of members

  Closes #2498

* Add check for bool function to ``len-as-condition``

* Add ``simplifiable-condition`` check for extraneous constants in conditionals using and/or.

* Add ``condition-evals-to-constant`` check for conditionals using and/or that evaluate to a constant.

  Closes #3407

* Changed setup.py to work with `distlib <https://pypi.org/project/distlib>`_

  Closes #3555

* New check: ``consider-using-generator``

  This check warns when a comprehension is used inside an ``any`` or ``all`` function,
  since it is unnecessary and should be replaced by a generator instead.
  Using a generator would be less code and way faster.

  Closes #3165

* Add Github Actions to replace Travis and AppVeyor in the future
````

## File: doc/whatsnew/2/2.7/index.rst
````
**************************
  What's New In Pylint 2.7
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.7/summary.rst
````
:Release: 2.7
:Date: 2021-02-21

Summary -- Release highlights
=============================

* Python 3.6+ is now required.
* No more duplicate messages when using multiple jobs.
* Handling of the new typing provided by mypy 0.8
* Reduced the number of false positives in general
* Reduced the occurrence of genuinely large recursion that went above system limit (See #3836, for a fix for pandas)

New checkers
============

* Add ``nan-comparison`` check for comparison of NaN values

* Add support to ``ignored-argument-names`` in DocstringParameterChecker and
  adds ``useless-param-doc`` and ``useless-type-doc`` messages.

* Add ``empty-comment`` check for empty comments.

* Add ``simplifiable-condition`` check for extraneous constants in conditionals using and/or.

* Add ``condition-evals-to-constant`` check for conditionals using and/or that evaluate to a constant.

* Add ``consider-using-generator`` check for the use of list comprehension inside ``any`` or ``all`` function.

Other Changes
=============

* Fix false positive for ``builtin-not-iterating`` when ``zip`` or ``map`` receives iterable

* Fix linter multiprocessing pool shutdown which triggered warnings when ran in parallels with other pytest plugins.

* Enums are now required to be named in UPPER_CASE by ``invalid-name``.

* Fix bug that lead to duplicate messages when using ``--jobs 2`` or more.

* Adds option ``check-protected-access-in-special-methods`` in the ClassChecker to activate/deactivate
  ``protected-access`` message emission for single underscore prefixed attribute in special methods.

* ``inconsistent-return-statements`` message is now emitted if one of ``try/except`` statement
  is not returning explicitly while the other do.

* Fix false positive message ``useless-super-delegation`` when default keyword argument is a dictionary.

* Fix vulnerable regular expressions in ``pyreverse``. The ambiguities of vulnerable regular expressions are removed, making the repaired regular expressions safer and faster matching.

* ``len-as-conditions`` is now triggered only for classes that are inheriting directly from list, dict, or set and not implementing the ``__bool__`` function, or from generators like range or list/dict/set comprehension. This should reduce the false positive for other classes, like pandas's DataFrame or numpy's Array.

* Fixes duplicate code detection for --jobs=2+

* New option ``allowed-redefined-builtins`` defines variable names allowed to shadow builtins.

* Improved protected access checks to allow access inside class methods
````

## File: doc/whatsnew/2/2.8/full.rst
````
Full changelog
==============

What's New in Pylint 2.8.3?
---------------------------
Release date: 2021-05-31

* Astroid has been pinned to 2.5.6 for the 2.8 branch.

  Refs #4527


What's New in Pylint 2.8.2?
---------------------------
Release date: 2021-04-26

* Keep ``__pkginfo__.numversion`` a tuple to avoid breaking pylint-django.

  Closes #4405

* scm_setuptools has been added to the packaging.

* Pylint's tags are now the standard form ``vX.Y.Z`` and not ``pylint-X.Y.Z`` anymore.

* New warning message ``deprecated-class``. This message is emitted if import or call deprecated class of the
  standard library (like ``collections.Iterable`` that will be removed in Python 3.10).

  Closes #4388


What's New in Pylint 2.8.1?
---------------------------
Release date: 2021-04-25

* Add numversion back (temporarily) in ``__pkginfo__`` because it broke Pylama and revert the unnecessary
  ``pylint.version`` breaking change.

  Closes #4399


What's New in Pylint 2.8.0?
---------------------------
Release date: 2021-04-24

* New refactoring message ``consider-using-with``. This message is emitted if resource-allocating functions or methods of the
  standard library (like ``open()`` or ``threading.Lock.acquire()``) that can be used as a context manager are called without
  a ``with`` block.

  Closes #3413

* Resolve false positives on unused variables in decorator functions

  Closes #4252

* Add new extension ``ConfusingConsecutiveElifChecker``. This optional checker emits a refactoring message (R5601 ``confusing-consecutive-elif``)
  if if/elif statements with different indentation levels follow directly one after the other.

* New option ``--output=<file>`` to output result to a file rather than printing to stdout.

  Closes #1070

* Use a prescriptive message for ``unidiomatic-typecheck``

  Closes #3891

* Apply ``const-naming-style`` to module constants annotated with
  ``typing.Final``

* The packaging is now done via setuptools exclusively. ``doc``, ``tests``, ``man``, ``elisp`` and ``Changelog`` are
  not packaged anymore - reducing the size of the package by 75%.

* Debian packaging is now  (officially) done in https://salsa.debian.org/python-team/packages/pylint.

* The 'doc' extra-require has been removed.

* ``__pkginfo__`` now only contain ``__version__`` (also accessible with ``pylint.__version__``), other meta-information are still
  accessible with ``from importlib import metadata;metadata.metadata('pylint')``.

* COPYING has been renamed to LICENSE for standardization.

* Fix false-positive ``used-before-assignment`` in function returns.

  Closes #4301

* Updated ``astroid`` to 2.5.3

  Closes #2822, #4206, #4284

* Add ``consider-using-min-max-builtin`` check for if statement which could be replaced by Python builtin min or max

  Closes #3406

* Don't auto-enable postponed evaluation of type annotations with Python 3.10

* Update ``astroid`` to 2.5.4

* Add new extension ``TypingChecker``. This optional checker can detect the use of deprecated typing aliases
  and can suggest the use of the alternative union syntax where possible.
  (For example, 'typing.Dict' can be replaced by 'dict', and 'typing.Unions' by '|', etc.)
  Make sure to check the config options if you plan on using it!

* Reactivates old counts in report mode.

  Closes #3819

* During detection of ``inconsistent-return-statements`` consider that ``assert False`` is a return node.

  Closes #4019

* Run will not fail if score exactly equals ``config.fail_under``.

* Functions that never returns may declare ``NoReturn`` as type hints, so that
  ``inconsistent-return-statements`` is not emitted.

  Closes #4122, #4188

* Improved protected access checks to allow access inside class methods

  Closes #1159

* Fix issue with PEP 585 syntax and the use of ``collections.abc.Set``

* Fix issue that caused class variables annotated with ``typing.ClassVar`` to be
  identified as class constants. Now, class variables annotated with
  ``typing.Final`` are identified as such.

  Closes #4277

* Continuous integration with read the doc has been added.

  Closes #3850

* Don't show ``DuplicateBasesError`` for attribute access

* Fix crash when checking ``setup.cfg`` for pylint config when there are non-ascii characters in there

  Closes #4328

* Allow code flanked in backticks to be skipped by spellchecker

  Closes #4319

* Allow Python tool directives (for black, flake8, zimports, isort, mypy, bandit, pycharm) at beginning of comments to be skipped by spellchecker

  Closes #4320

* Fix issue that caused Emacs pylint to fail when used with tramp

* Improve check for invalid PEP 585 syntax inside functions
  if postponed evaluation of type annotations is enabled

* Improve check for invalid PEP 585 syntax as default function arguments
````

## File: doc/whatsnew/2/2.8/index.rst
````
**************************
  What's New In Pylint 2.8
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.8/summary.rst
````
:Release: 2.8
:Date: 2021-04-24

Summary -- Release highlights
=============================

Breaking changes
================

* The 'doc' extra-require has been removed. `__pkginfo__`` does not contain the package metadata anymore
  (except ``numversion``, until 3.0). Meta-information are accessible with

```python
from importlib import metadata
metadata.metadata('pylint')
```
Prefer that to an import from ``__pkginfo__``.

New checkers
============

* New refactoring message ``consider-using-with``. This message is emitted if resource-allocating functions or methods of the
  standard library (like ``open()`` or ``threading.Lock.acquire()``) that can be used as a context manager are called without
  a ``with`` block.

* Add ``deprecated-argument`` check for deprecated arguments.

* Add new extension ``ConfusingConsecutiveElifChecker``. This optional checker emits a refactoring message (R5601 ``confusing-consecutive-elif``)
  if if/elif statements with different indentation levels follow directly one after the other.

* Add ``consider-using-min-max-builtin`` check for if statement which could be replaced by Python builtin min or max.

* Add new extension ``TypingChecker``. This optional checker can detect the use of deprecated typing aliases
  and can suggest the use of the alternative union syntax where possible.
  (For example, 'typing.Dict' can be replaced by 'dict', and 'typing.Unions' by '|', etc.)
  Make sure to check the config options if you plan on using it!

* Add ``deprecated-class`` check for deprecated classes.

Other Changes
=============

* New option ``--output=<file>`` to output result to a file rather than printing to stdout.

  Closes #1070

* Reduce usage of blacklist/whitelist terminology. Notably, ``extension-pkg-allow-list`` is an
  alternative to ``extension-pkg-whitelist`` and the message ``blacklisted-name`` is now emitted as
  ``disallowed-name``. The previous names are accepted to maintain backward compatibility.

* The packaging is now done via setuptools exclusively. ``doc``, ``tests``, ``man``, ``elisp`` and ``Changelog`` are
  not packaged anymore - reducing the size of the package by 75%.

* Updated ``astroid`` to 2.5.4

* COPYING has been renamed to LICENSE for standardization.
````

## File: doc/whatsnew/2/2.9/full.rst
````
Full changelog
==============

What's New in Pylint 2.9.6?
---------------------------
Release date: 2021-07-28

* Fix a false positive ``undefined-variable`` when variable name in decoration
  matches function argument

  Closes #3791


What's New in Pylint 2.9.5?
---------------------------
Release date: 2021-07-21

* Fix a crash when there would be a 'TypeError object does not support
  item assignment' in the code we parse.

  Closes #4439

* Fix crash if a callable returning a context manager was assigned to a list or dict item

  Closes #4732

* Fix a crash when an AttributeInferenceError was not handled properly when
  failing to infer the real name of an import in astroid.

  Closes #4692


What's New in Pylint 2.9.4?
---------------------------
Release date: 2021-07-20

* Added ``time.clock`` to deprecated functions/methods for python 3.3

* Fix bug in which --fail-on can return a zero exit code even when the specified issue is present

  Closes #4296
  Closes #3363

* Fix hard failure when handling missing attribute in a class with duplicated bases

  Closes #4687

* Fix false-positive ``consider-using-with`` (R1732) if a ternary conditional is used together with ``with``

  Closes #4676

* Fix false-positive ``deprecated-module`` when relative import uses deprecated module name.

  Closes #4629

* Fix false-positive ``consider-using-with`` (R1732) if ``contextlib.ExitStack`` takes care of calling the ``__exit__`` method

  Closes #4654

* Fix a false positive for ``unused-private-member`` when mutating a private attribute
  with ``cls``

  Closes #4657

* Fix ignored empty functions by similarities checker with "ignore-signatures" option enabled

  Closes #4652

* Fix false-positive of ``use-maxsplit-arg`` when index is incremented in
  a loop

  Closes #4664

* Don't emit ``cyclic-import`` message if import is guarded by ``typing.TYPE_CHECKING``.

  Closes #3525

* Fix false-positive ``not-callable`` with alternative ``TypedDict`` syntax

  Closes #4715

* Clarify documentation for consider-using-from-import

* Don't emit ``unreachable`` warning for empty generator functions

  Closes #4698

* Don't emit ``import-error``, ``no-name-in-module``, and ``ungrouped-imports``
  for imports guarded by ``sys.version_info`` or ``typing.TYPE_CHECKING``.

  Closes #3285
  Closes #3382

* Fix ``invalid-overridden-method`` with nested property

  Closes #4368

* Fix false-positive of ``unused-private-member`` when using ``__new__`` in a class

  Closes #4668

* No longer emit ``consider-using-with`` for ``ThreadPoolExecutor`` and ``ProcessPoolExecutor``
  as they have legitimate use cases without a ``with`` block.

  Closes #4689

* Fix crash when inferring variables assigned in match patterns

  Closes #4685

* Fix a crash when a StopIteration was raised when inferring
  a faulty function in a context manager.

  Closes #4723


What's New in Pylint 2.9.3?
---------------------------
Release date: 2021-07-01


* Fix a crash that happened when analysing empty function with docstring
  in the ``similarity`` checker.

  Closes #4648

* The ``similarity`` checker no longer add three trailing whitespaces for
  empty lines in its report.


What's New in Pylint 2.9.2?
---------------------------
Release date: 2021-07-01

* Fix a crash that happened when analysing code using ``type(self)`` to access
  a class attribute in the ``unused-private-member`` checker.

  Closes #4638

* Fix a false positive for ``unused-private-member`` when accessing a private variable
  with ``self``

  Closes #4644

* Fix false-positive of ``unnecessary-dict-index-lookup`` and ``consider-using-dict-items``
  for reassigned dict index lookups

  Closes #4630


What's New in Pylint 2.9.1?
---------------------------
Release date: 2021-06-30

* Upgrade astroid to 2.6.2

  Closes #4631
  Closes #4633


What's New in Pylint 2.9.0?
---------------------------
Release date: 2021-06-29

* Python 3.10 is now supported.

* Add type annotations to pyreverse dot files

  Closes #1548

* Fix missing support for detecting deprecated aliases to existing
  functions/methods.

  Closes #4618

* astroid has been upgraded to 2.6.1

* Added various deprecated functions/methods for python 3.10, 3.7, 3.6 and 3.3

* Fix false positive ``useless-type-doc`` on ignored argument using ``pylint.extensions.docparams``
  when a function was typed using pep484 but not inside the docstring.

  Closes #4117
  Closes #4593

* ``setuptools_scm`` has been removed and replaced by ``tbump`` in order to not
  have hidden runtime dependencies to setuptools

* Fix a crash when a test function is decorated with ``@pytest.fixture`` and astroid can't
  infer the name of the decorator when using ``open`` without ``with``.

  Closes #4612

* Added ``deprecated-decorator``: Emitted when deprecated decorator is used.

  Closes #4429

* Added ``ignore-paths`` behaviour. Defined regex patterns are matched against full file path.

  Closes #2541

* Fix false negative for ``consider-using-with`` if calls like ``open()`` were used outside of assignment expressions.

* The warning for ``arguments-differ`` now signals explicitly the difference it detected
  by naming the argument or arguments that changed and the type of change that occurred.

* Suppress ``consider-using-with`` inside context managers.

  Closes #4430

* Added ``--fail-on`` option to return non-zero exit codes regardless of ``--fail-under`` value.

* numversion tuple contains integers again to fix multiple pylint's plugins that relied on it

  Closes #4420

* Fix false-positive ``too-many-ancestors`` when inheriting from builtin classes,
  especially from the ``collections.abc`` module

  Closes #4166
  Closes #4415

* Stdlib deprecated modules check is moved to stdlib checker. New deprecated
  modules are added.

* Fix raising false-positive ``no-member`` on abstract properties

* Created new error message called ``arguments-renamed`` which identifies any changes at the parameter
  names of overridden functions.

  Closes #3536

* New checker ``consider-using-dict-items``. Emitted  when iterating over dictionary keys and then
  indexing the same dictionary with the key within loop body.

  Closes #3389

* Don't emit ``import-error`` if import guarded behind ``if sys.version_info >= (x, x)``

* Fix incompatibility with Python 3.6.0 caused by ``typing.Counter`` and ``typing.NoReturn`` usage

  Closes #4412

* New checker ``use-maxsplit-arg``. Emitted either when accessing only the first or last
  element of ``str.split()``.

  Closes #4440

* Add ignore_signatures to duplicate code checker

  Closes #3619

* Fix documentation errors in "Block disables" paragraph of User Guide.

* New checker ``unnecessary-dict-index-lookup``. Emitted when iterating over dictionary items
  (key-value pairs) and accessing the value by index lookup.

  Closes #4470

* New checker``consider-using-from-import``. Emitted when a submodule/member of a package is imported and aliased
  with the same name.

  Closes #2309

* Allow comma-separated list in ``output-format`` and separate output files for
  each specified format.

  Closes #1798

* Make ``using-constant-test`` detect constant tests consisting of list literals like ``[]`` and
  ``[1, 2, 3]``.

* Improved error message of ``unnecessary-comprehension`` checker by providing code suggestion.

  Closes #4499

* New checker ``unused-private-member``. Emitted when a private member (i.e., starts with ``__``) of a class
  is defined but not used.

  Closes #4483

* Fix false negative of ``consider-using-enumerate`` when iterating over an attribute.

  Closes #3657

* New checker ``invalid-class-object``. Emitted when a non-class is assigned to a ``__class__`` attribute.

  Closes #585

* Fix a crash when a plugin from the configuration could not be loaded and raise an error
  'bad-plugin-value' instead

  Closes #4555

* Added handling of floating point values when parsing configuration from pyproject.toml

  Closes #4518

* ``invalid-length-returned``, now also works when nothing at all is returned
  following an upgrade in astroid.

* ``logging-format-interpolation`` and ``logging-not-lazy``, now works on logger
  class created from renamed logging import following an upgrade in astroid.

* Fix false-positive ``no-member`` with generic base class

  Closes pylint-dev/astroid#942

* Fix ``assigning-non-slot`` false-positive with base that inherits from ``typing.Generic``

  Closes #4509
  Closes pylint-dev/astroid#999

* New checker ``invalid-all-format``. Emitted when ``__all__`` has an invalid format,
  i.e. isn't a ``tuple`` or ``list``.

* Fix false positive ``unused-variable`` and ``undefined-variable`` with
  Pattern Matching in Python 3.10

* New checker ``await-outside-async``. Emitted when await is used outside an async function.

* Clarify documentation for ``typing`` extension.

  Closes #4545

* Add new extension ``CodeStyleChecker``. It includes checkers that can improve code
  consistency. As such they don't necessarily provide a performance benefit
  and are often times opinionated.

* New checker ``consider-using-tuple``. Emitted when an in-place defined
  list or set can be replaced by a tuple.

* New checker ``consider-using-namedtuple-or-dataclass``. Emitted when dictionary values
  can be replaced by namedtuples or dataclass instances.

* Fix error that occurred when using ``slice`` as subscript for dict.

* Reduce false-positives around inference of ``.value`` and ``.name``
  properties on ``Enum`` subclasses, following an upgrade in astroid

  Closes #1932
  Closes #2062

* Fix issue with ``cached_property`` that caused ``invalid-overridden-method`` error
  when overriding a ``property``.

  Closes #4023

* Fix ``unused-import`` false positive for imported modules referenced in
  attribute lookups in type comments.

  Closes #4603
````

## File: doc/whatsnew/2/2.9/index.rst
````
**************************
  What's New In Pylint 2.9
**************************

.. include:: ../../full_changelog_explanation.rst
.. include:: ../../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   summary.rst
   full.rst
````

## File: doc/whatsnew/2/2.9/summary.rst
````
:Release: 2.9
:Date: 2021-06-29

Summary -- Release highlights
=============================

Pylint is now compatible with python 3.10.

A lot of new checks have been added, some non-opinionated performance warnings
like ``use-maxsplit-arg``, some consensual style warnings like
``unnecessary-dict-index-lookup`` or new deprecation checks.

We're aiming to reduce pylint noise for first time users and making some
new checks optional is a step in that direction. In order to do that we
created an optional code style checker that can be loaded using
``pylint.extensions.code_style`` with the ``load-plugins`` options.
More than ever, if as a veteran you want the most checks you can possibly get,
`you should check the list of pylint extensions. <https://pylint.readthedocs.io/en/latest/user_guide/checkers/extensions.html#optional-checkers>`_.


New checkers
============

* ``deprecated-decorator``: Emitted when deprecated decorator is used.

* ``consider-using-dict-items``: Emitted when iterating over dictionary keys and then
  indexing the same dictionary with the key within loop body.

* ``use-maxsplit-arg``: Emitted either when accessing only the first or last
  element of ``str.split()``.

* An ``ignore_signatures`` option has been added to the similarity checker. It will permits  to reduce false positives when multiple functions have the same parameters.

* ``unnecessary-dict-index-lookup``: Emitted when iterating over dictionary items
  (key-value pairs) and accessing the value by index lookup.

* ``consider-using-from-import``: Emitted when a submodule/member of a package is imported and aliased with the same name.

* New checker ``unused-private-member``: Emitted when a private member (i.e., starts with ``__``) of a class is defined but not used.

* New checker ``invalid-class-object``: Emitted when a non-class is assigned to a ``__class__`` attribute.

* ``invalid-all-format``: Emitted when ``__all__`` has an invalid format,
  i.e. isn't a ``tuple`` or ``list``.

* New checker ``await-outside-async``: Emitted when await is used outside an async function.

* Add new extension ``CodeStyleChecker``. It includes checkers that can improve code
  consistency. As such they don't necessarily provide a performance benefit
  and are often times opinionated.

  * ``consider-using-tuple``: Emitted when an in-place defined list or set can be replaced by a tuple.

  * ``consider-using-namedtuple-or-dataclass``: Emitted when dictionary values
    can be replaced by namedtuples or dataclass instances.


Other Changes
=============

* Fix false-positive ``consider-using-with`` (R1732) if a ternary conditional is used together with ``with``

* Fix false-positive ``consider-using-with`` (R1732) if ``contextlib.ExitStack`` takes care of calling the ``__exit__`` method

* Add type annotations to pyreverse dot files

* Pylint's tags are now the standard form ``vX.Y.Z`` and not ``pylint-X.Y.Z`` anymore.

* Fix false-positive ``too-many-ancestors`` when inheriting from builtin classes,
  especially from the ``collections.abc`` module

* The output messages for ``arguments-differ`` error message have been customized based on the different error cases.

* New option ``--fail-on=<msg ids>`` to return non-zero exit codes regardless of ``fail-under`` value.

* A new error called ``arguments-renamed`` has been created, which identifies any changes at the parameter names
  of overridden functions. It aims to separate the functionality of ``arguments-differ``.

* Fix incompatibility with Python 3.6.0 caused by ``typing.Counter`` and ``typing.NoReturn`` usage

* Allow comma-separated list in ``output-format`` and separate output files for
  each specified format.  Each output file can be defined after a semicolon for example : ``--output-format=json:myfile.json,colorized``

* The ``using-constant-test`` checker now detects constant tests consisting of list literals
  like ``[]`` and ``[1, 2, 3]``.

* ``ignore-paths`` configuration directive has been added. Defined regex patterns are matched against file path.

* Added handling of floating point values when parsing configuration from pyproject.toml

* Fix false positive ``useless-type-doc`` on ignored argument using ``pylint.extensions.docparams`` when a function
  was typed using pep484 but not inside the docstring.

* Fix missing support for detecting deprecated aliases to existing functions/methods.
  functions/methods.

* Added various deprecated functions/methods for python 3.10, 3.7, 3.6 and 3.3

* No longer emit ``consider-using-with`` for ``ThreadPoolExecutor`` and ``ProcessPoolExecutor``
  as they have legitimate use cases without a ``with`` block.

* Fix crash if a callable returning a context manager was assigned to a list or dict item
````

## File: doc/whatsnew/2/index.rst
````
2.x
===

.. include:: ../full_changelog_explanation.rst
.. include:: ../summary_explanation.rst

.. toctree::
   :maxdepth: 2

   2.17/index
   2.16/index
   2.15/index
   2.14/index
   2.13/index
   2.12/index
   2.11/index
   2.10/index
   2.9/index
   2.8/index
   2.7/index
   2.6/index
   2.5/index
   2.4/index
   2.3/index
   2.2/index
   2.1/index
   2.0/index
````

## File: doc/whatsnew/3/3.0/index.rst
````
*************************
 What's New in Pylint 3.0
*************************

.. toctree::
   :maxdepth: 2

:Release: 3.0.0
:Date: 2023-10-02


Summary -- Release highlights
=============================

Pylint now support python 3.12 officially.

This long anticipated major version also provides some important usability
and performance improvements, along with enacting necessary breaking changes
and long-announced deprecations. The documentation of each message with an
example is very close too.

The required ``astroid`` version is now 3.0.0. See the
`astroid changelog <https://pylint.readthedocs.io/projects/astroid/en/latest/changelog.html#what-s-new-in-astroid-3-0-0>`_
for additional fixes, features, and performance improvements applicable to pylint.

Our code is now fully typed. The ``invalid-name`` message no longer checks for a minimum length of 3 characters by default. Dependencies
like wrapt or setuptools were removed.

A new ``json2`` reporter has been added. It features an enriched output that is
easier to parse and provides more info, here's a sample output.

.. code-block:: json

    {
        "messages": [
            {
                "type": "convention",
                "symbol": "line-too-long",
                "message": "Line too long (1/2)",
                "messageId": "C0301",
                "confidence": "HIGH",
                "module": "0123",
                "obj": "",
                "line": 1,
                "column": 0,
                "endLine": 1,
                "endColumn": 4,
                "path": "0123",
                "absolutePath": "0123"
            }
        ],
        "statistics": {
            "messageTypeCount": {
                "fatal": 0,
                "error": 0,
                "warning": 0,
                "refactor": 0,
                "convention": 1,
                "info": 0
            },
            "modulesLinted": 1,
            "score": 5.0
        }
    }

.. towncrier release notes start

What's new in Pylint 3.0.4?
---------------------------
Release date: 2024-02-23


False Positives Fixed
---------------------

- ``used-before-assignment`` is no longer emitted when using a name in a loop and
  depending on an earlier name assignment in an ``except`` block paired with
  ``else: continue``.

  Closes #6804 (`#6804 <https://github.com/pylint-dev/pylint/issues/6804>`_)

- Avoid false positives for ``no-member`` involving function
  attributes supplied by decorators.

  Closes #9246 (`#9246 <https://github.com/pylint-dev/pylint/issues/9246>`_)

- Fixed false positive nested-min-max for nested lists.

  Closes #9307 (`#9307 <https://github.com/pylint-dev/pylint/issues/9307>`_)

- Fix false positive for ``used-before-assignment`` in a ``finally`` block
  when assignments took place in both the ``try`` block and each exception handler.

  Closes #9451 (`#9451 <https://github.com/pylint-dev/pylint/issues/9451>`_)



Other Bug Fixes
---------------

- Catch incorrect ValueError ``"generator already executing"`` for Python 3.12.0 - 3.12.2.
  This is fixed upstream in Python 3.12.3.

  Closes #9138 (`#9138 <https://github.com/pylint-dev/pylint/issues/9138>`_)



What's new in Pylint 3.0.3?
---------------------------
Release date: 2023-12-11


False Positives Fixed
---------------------

- Fixed false positive for ``unnecessary-lambda`` when the call has keyword arguments but not the lambda.

  Closes #9148 (`#9148 <https://github.com/pylint-dev/pylint/issues/9148>`_)

- Fixed incorrect suggestion for shallow copy in unnecessary-comprehension

  Example of the suggestion:
  #pylint: disable=missing-module-docstring
  a = [1, 2, 3]
  b = [x for x in a]
  b[0] = 0
  print(a) # [1, 2, 3]

  After changing b = [x for x in a] to b = a based on the suggestion, the script now prints [0, 2, 3]. The correct suggestion should be use list(a) to preserve the original behavior.

  Closes #9172 (`#9172 <https://github.com/pylint-dev/pylint/issues/9172>`_)

- Fix false positives for ``undefined-variable`` and ``unused-argument`` for
  classes and functions using Python 3.12 generic type syntax.

  Closes #9193 (`#9193 <https://github.com/pylint-dev/pylint/issues/9193>`_)

- Fixed ``pointless-string-statement`` false positive for docstrings
  on Python 3.12 type aliases.

  Closes #9268 (`#9268 <https://github.com/pylint-dev/pylint/issues/9268>`_)

- Fix false positive for ``invalid-exception-operation`` when concatenating tuples
  of exception types.

  Closes #9288 (`#9288 <https://github.com/pylint-dev/pylint/issues/9288>`_)



Other Bug Fixes
---------------

- Fix a bug where pylint was unable to walk recursively through a directory if the
  directory has an `__init__.py` file.

  Closes #9210 (`#9210 <https://github.com/pylint-dev/pylint/issues/9210>`_)



What's new in Pylint 3.0.2?
---------------------------
Release date: 2023-10-22


False Positives Fixed
---------------------

- Fix ``used-before-assignment`` false positive for generic type syntax (PEP 695, Python 3.12).

  Closes #9110 (`#9110 <https://github.com/pylint-dev/pylint/issues/9110>`_)



Other Bug Fixes
---------------

- Escape special symbols and newlines in messages.

  Closes #7874 (`#7874 <https://github.com/pylint-dev/pylint/issues/7874>`_)

- Fixes suggestion for ``nested-min-max`` for expressions with additive operators, list and dict comprehensions.

  Closes #8524 (`#8524 <https://github.com/pylint-dev/pylint/issues/8524>`_)

- Fixes ignoring conditional imports with ``ignore-imports=y``.

  Closes #8914 (`#8914 <https://github.com/pylint-dev/pylint/issues/8914>`_)

- Emit ``inconsistent-quotes`` for f-strings with 3.12 interpreter only if targeting pre-3.12 versions.

  Closes #9113 (`#9113 <https://github.com/pylint-dev/pylint/issues/9113>`_)


What's new in Pylint 3.0.1?
---------------------------
Release date: 2023-10-05


False Positives Fixed
---------------------

- Fixed false positive for ``inherit-non-class`` for generic Protocols.

  Closes #9106 (`#9106 <https://github.com/pylint-dev/pylint/issues/9106>`_)



Other Changes
-------------

- Fix a crash when an enum class which is also decorated with a ``dataclasses.dataclass`` decorator is defined.

  Closes #9100 (`#9100 <https://github.com/pylint-dev/pylint/issues/9100>`_)


What's new in Pylint 3.0.0?
---------------------------
Release date: 2023-10-02


Breaking Changes
----------------

- Enabling or disabling individual messages will now take effect even if an
  ``--enable=all`` or ``disable=all`` follows in the same configuration file
  (or on the command line).

  This means for the following example, ``fixme`` messages will now be emitted:

  .. code-block::

      pylint my_module --enable=fixme --disable=all

  To regain the prior behavior, remove the superfluous earlier option.

  Closes #3696 (`#3696 <https://github.com/pylint-dev/pylint/issues/3696>`_)

- Remove support for launching pylint with Python 3.7.
  Code that supports Python 3.7 can still be linted with the ``--py-version=3.7`` setting.

  Refs #6306 (`#6306 <https://github.com/pylint-dev/pylint/issues/6306>`_)

- Disables placed in a ``try`` block now apply to the ``except`` block.
  Previously, they only happened to do so in the presence of an ``else`` clause.

  Refs #7767 (`#7767 <https://github.com/pylint-dev/pylint/issues/7767>`_)

- `pyreverse` now uses a new default color palette that is more colorblind friendly.
  The color scheme is taken from `Paul Tol's Notes <https://personal.sron.nl/~pault/>`_.
  If you prefer other colors, you can use the `--color-palette` option to specify custom colors.

  Closes #8251 (`#8251 <https://github.com/pylint-dev/pylint/issues/8251>`_)

- Everything related to the ``__implements__`` construct was removed. It was based on PEP245
  that was proposed in 2001 and rejected in 2006.

  The capability from pyreverse to take ``__implements__`` into account when generating diagrams
  was also removed.

  Refs #8404 (`#8404 <https://github.com/pylint-dev/pylint/issues/8404>`_)

- ``pyreverse``: Support for the ``.vcg`` output format (Visualization of Compiler Graphs) has been dropped.

  Closes #8416 (`#8416 <https://github.com/pylint-dev/pylint/issues/8416>`_)

- The warning when the now useless old pylint cache directory (pylint.d) was
  found was removed. The cache dir is documented in
  `the FAQ <https://pylint.readthedocs.io/en/latest/faq.html#where-is-the-persistent-data-stored-to-compare-between-successive-runs>`_.

  Refs #8462 (`#8462 <https://github.com/pylint-dev/pylint/issues/8462>`_)

- Following a deprecation period, ``pylint.config.PYLINTRC`` was removed.
  Use the ``pylint.config.find_default_config_files`` generator instead.

  Closes #8862 (`#8862 <https://github.com/pylint-dev/pylint/issues/8862>`_)



Changes requiring user actions
------------------------------

- The ``invalid-name`` message no longer checks for a minimum length of 3 characters by default.
  (This was an unadvertised commingling of concerns between casing
  and name length, and users regularly reported this to be surprising.)

  If checking for a minimum length is still desired, it can be regained in two ways:

  - If you are content with a ``disallowed-name`` message (instead of
    ``invalid-name``), then simply add the option ``bad-names-rgxs="^..?$"``,
    which will fail 1-2 character-long names. (Ensure you enable
    ``disallowed-name``.)

  - If you would prefer an ``invalid-name`` message to be emitted, or would
    prefer finer-grained control over the circumstances in which messages are
    emitted (classes vs. methods, etc.), then avail yourself of the regex
    options described
    `here <https://pylint.readthedocs.io/en/stable/user_guide/configuration/all-options.html#main-checker>`_.
    (In particular, take note of the commented out options in the "example
    configuration" given at the bottom of the section.) The prior regexes can
    be found in the
    `pull request <https://github.com/pylint-dev/pylint/pull/8813>`_
    that removed the length requirements.

  Closes #2018 (`#2018 <https://github.com/pylint-dev/pylint/issues/2018>`_)

- The compare to empty string checker (``pylint.extensions.emptystring``) and the compare to
  zero checker (``pylint.extensions.compare-to-zero``) have been removed and their checks are
  now part of the implicit booleaness checker:

  - ``compare-to-zero`` was renamed ``use-implicit-booleaness-not-comparison-to-zero`` and
    ``compare-to-empty-string`` was renamed ``use-implicit-booleaness-not-comparison-to-string``
    and they now need to be enabled explicitly.

  - The ``pylint.extensions.emptystring`` and ``pylint.extensions.compare-to-zero`` extensions
    no longer exist and need to be removed from the ``load-plugins`` option.

  - Messages related to implicit booleaness were made more explicit and actionable.
    This permits to make their likeness explicit and will provide better performance as they
    share most of their conditions to be raised.

  Closes #6871 (`#6871 <https://github.com/pylint-dev/pylint/issues/6871>`_)

- epylint was removed. It now lives at: https://github.com/emacsorphanage/pylint.

  Refs #7737 (`#7737 <https://github.com/pylint-dev/pylint/issues/7737>`_)

- The ``overgeneral-exceptions`` option now only takes fully qualified names
  into account (``builtins.Exception`` not ``Exception``). If you overrode
  this option, you need to use the fully qualified name now.

  There's still a warning, but it will be removed in 3.1.0.

  Refs #8411 (`#8411 <https://github.com/pylint-dev/pylint/issues/8411>`_)

- Following a deprecation period, it's no longer possible to use ``MASTER``
  or ``master`` as configuration section in ``setup.cfg`` or ``tox.ini``. It's bad practice
  to not start a section title with the tool name. Please use ``pylint.main`` instead.

  Refs #8465 (`#8465 <https://github.com/pylint-dev/pylint/issues/8465>`_)

- Package stats are now printed when running Pyreverse and a ``--verbose`` flag was added to get the original output with parsed modules. You might need to activate the verbose option if you want to keep the old output.

  Closes #8973 (`#8973 <https://github.com/pylint-dev/pylint/issues/8973>`_)



New Features
------------

- A new ``json2`` reporter has been added. It features a more enriched output that is
  easier to parse and provides more info.

  Compared to ``json`` the only changes are that messages are now under the ``"messages"``
  key and that ``"message-id"`` now follows the camelCase convention and is renamed to
  ``"messageId"``.
  The new reporter also reports the "score" of the modules you linted as defined by the
  ``evaluation`` option and provides statistics about the modules you linted.

  We encourage users to use the new reporter as the ``json`` reporter will no longer
  be maintained.

  Closes #4741 (`#4741 <https://github.com/pylint-dev/pylint/issues/4741>`_)

- In Pyreverse package dependency diagrams, show when a module imports another only for type-checking.

  Closes #8112 (`#8112 <https://github.com/pylint-dev/pylint/issues/8112>`_)

- Add new option (``--show-stdlib``, ``-L``) to ``pyreverse``.
  This is similar to the behavior of ``--show-builtin`` in that standard library
  modules are now not included by default, and this option will include them.

  Closes #8181 (`#8181 <https://github.com/pylint-dev/pylint/issues/8181>`_)

- Add Pyreverse option to exclude standalone nodes from diagrams with `--no-standalone`.

  Closes #8476 (`#8476 <https://github.com/pylint-dev/pylint/issues/8476>`_)



New Checks
----------

- Added ``DataclassChecker`` module and ``invalid-field-call`` checker to check for invalid dataclasses.field() usage.

  Refs #5159 (`#5159 <https://github.com/pylint-dev/pylint/issues/5159>`_)

- Add ``return-in-finally`` to emit a message if a return statement was found in a finally clause.

  Closes #8260 (`#8260 <https://github.com/pylint-dev/pylint/issues/8260>`_)

- Add a new message ``kwarg-superseded-by-positional-arg`` to warn when a function is called with a keyword argument which shares a name with a positional-only parameter and the function contains a keyword variadic parameter dictionary. It may be surprising behaviour when the keyword argument is added to the keyword variadic parameter dictionary.

  Closes #8558 (`#8558 <https://github.com/pylint-dev/pylint/issues/8558>`_)



Extensions
----------

- Add new ``prefer-typing-namedtuple`` message to the ``CodeStyleChecker`` to suggest
  rewriting calls to ``collections.namedtuple`` as classes inheriting from ``typing.NamedTuple``
  on Python 3.6+.

  Requires ``load-plugins=pylint.extensions.code_style`` and ``enable=prefer-typing-namedtuple`` to be raised.

  Closes #8660 (`#8660 <https://github.com/pylint-dev/pylint/issues/8660>`_)



False Positives Fixed
---------------------

- Extend concept of "function ambiguity" in ``safe_infer()`` from
  differing number of function arguments to differing set of argument names.

  Solves false positives in ``tensorflow``.

  Closes #3613 (`#3613 <https://github.com/pylint-dev/pylint/issues/3613>`_)

- Fix `unused-argument` false positive when `__new__` does not use all the arguments of `__init__`.

  Closes #3670 (`#3670 <https://github.com/pylint-dev/pylint/issues/3670>`_)

- Fix a false positive for ``invalid-name`` when a type-annotated class variable in an ``enum.Enum`` class has no assigned value.

  Refs #7402 (`#7402 <https://github.com/pylint-dev/pylint/issues/7402>`_)

- Fix ``unused-import`` false positive for usage of ``six.with_metaclass``.

  Closes #7506 (`#7506 <https://github.com/pylint-dev/pylint/issues/7506>`_)

- Fix false negatives and false positives for ``too-many-try-statements``,
  ``too-complex``, and ``too-many-branches`` by correctly counting statements
  under a ``try``.

  Refs #7767 (`#7767 <https://github.com/pylint-dev/pylint/issues/7767>`_)

- When checking for unbalanced dict unpacking in for-loops, Pylint will now test whether the length of each value to be
  unpacked matches the number of unpacking targets. Previously, Pylint would test the number of values for the loop
  iteration, which would produce a false unbalanced-dict-unpacking warning.

  Closes #8156 (`#8156 <https://github.com/pylint-dev/pylint/issues/8156>`_)

- Fix false positive for ``used-before-assignment`` when usage and assignment
  are guarded by the same test in different statements.

  Closes #8167 (`#8167 <https://github.com/pylint-dev/pylint/issues/8167>`_)

- Adds ``asyncSetUp`` to the default ``defining-attr-methods`` list to silence
  ``attribute-defined-outside-init`` warning when using
  ``unittest.IsolatedAsyncioTestCase``.

  Refs #8403 (`#8403 <https://github.com/pylint-dev/pylint/issues/8403>`_)

- `logging-not-lazy` is not longer emitted for explicitly concatenated string arguments.

  Closes #8410 (`#8410 <https://github.com/pylint-dev/pylint/issues/8410>`_)

- Fix false positive for isinstance-second-argument-not-valid-type when union types contains None.

  Closes #8424 (`#8424 <https://github.com/pylint-dev/pylint/issues/8424>`_)

- ``invalid-name`` now allows for integers in ``typealias`` names:
  - now valid: ``Good2Name``, ``GoodName2``.
  - still invalid: ``_1BadName``.

  Closes #8485 (`#8485 <https://github.com/pylint-dev/pylint/issues/8485>`_)

- No longer consider ``Union`` as type annotation as type alias for naming checks.

  Closes #8487 (`#8487 <https://github.com/pylint-dev/pylint/issues/8487>`_)

- ``unnecessary-lambda`` no longer warns on lambdas which use its parameters in
  their body (other than the final arguments), e.g.
  ``lambda foo: (bar if foo else baz)(foo)``.

  Closes #8496 (`#8496 <https://github.com/pylint-dev/pylint/issues/8496>`_)

- Fixed `unused-import` so that it observes the `dummy-variables-rgx` option.

  Closes #8500 (`#8500 <https://github.com/pylint-dev/pylint/issues/8500>`_)

- `Union` typed variables without assignment are no longer treated as
  `TypeAlias`.

  Closes #8540 (`#8540 <https://github.com/pylint-dev/pylint/issues/8540>`_)

- Allow parenthesized implicitly concatenated strings when `check-str-concat-over-line-jumps` is enabled.

  Closes #8552. (`#8552 <https://github.com/pylint-dev/pylint/issues/8552>`_)

- Fix false positive for ``positional-only-arguments-expected`` when a function contains both a positional-only parameter that has a default value, and ``**kwargs``.

  Closes #8555 (`#8555 <https://github.com/pylint-dev/pylint/issues/8555>`_)

- Fix false positive for ``keyword-arg-before-vararg`` when a positional-only parameter with a default value precedes ``*args``.

  Closes #8570 (`#8570 <https://github.com/pylint-dev/pylint/issues/8570>`_)

- Fix false positive for ``arguments-differ`` when overriding `__init_subclass__`.

  Closes #8919 (`#8919 <https://github.com/pylint-dev/pylint/issues/8919>`_)

- Fix a false positive for ``no-value-for-parameter`` when a staticmethod is called in a class body.

  Closes #9036 (`#9036 <https://github.com/pylint-dev/pylint/issues/9036>`_)



False Negatives Fixed
---------------------

- Emit ``used-before-assignment`` when calling module-level functions before definition.

  Closes #1144 (`#1144 <https://github.com/pylint-dev/pylint/issues/1144>`_)

- Apply ``infer_kwarg_from_call()`` to more checks

  These mostly solve false negatives for various checks,
  save for one false positive for ``use-maxsplit-arg``.

  Closes #7761 (`#7761 <https://github.com/pylint-dev/pylint/issues/7761>`_)

- `TypeAlias` variables defined in functions are now checked for `invalid-name` errors.

  Closes #8536 (`#8536 <https://github.com/pylint-dev/pylint/issues/8536>`_)

- Fix false negative for ``no-value-for-parameter`` when a function, whose signature contains both a positional-only parameter ``name`` and also ``*kwargs``, is called with a keyword-argument for ``name``.

  Closes #8559 (`#8559 <https://github.com/pylint-dev/pylint/issues/8559>`_)

- Fix a false negative for ``too-many-arguments`` by considering positional-only and keyword-only parameters.

  Closes #8667 (`#8667 <https://github.com/pylint-dev/pylint/issues/8667>`_)

- Emit ``assignment-from-no-return`` for calls to builtin methods like ``dict.update()``.
  Calls to ``list.sort()`` now raise ``assignment-from-no-return``
  rather than ``assignment-from-none`` for consistency.

  Closes #8714
  Closes #8810 (`#8714 <https://github.com/pylint-dev/pylint/issues/8714>`_)

- ``consider-using-augmented-assign`` is now applied to dicts and lists as well.

  Closes #8959. (`#8959 <https://github.com/pylint-dev/pylint/issues/8959>`_)



Other Bug Fixes
---------------

- Support ``duplicate-code`` message when parallelizing with ``--jobs``.

  Closes #374 (`#374 <https://github.com/pylint-dev/pylint/issues/374>`_)

- Support ``cyclic-import`` message when parallelizing with ``--jobs``.

  Closes #4171 (`#4171 <https://github.com/pylint-dev/pylint/issues/4171>`_)

- ``--jobs`` can now be used with ``--load-plugins``.

  This had regressed in astroid 2.5.0.

  Closes #4874 (`#4874 <https://github.com/pylint-dev/pylint/issues/4874>`_)

- docparams extension considers type comments as type documentation.

  Closes #6287 (`#6287 <https://github.com/pylint-dev/pylint/issues/6287>`_)

- When parsing comma-separated lists of regular expressions in the config, ignore
  commas that are inside braces since those indicate quantifiers, not delineation
  between expressions.

  Closes #7229 (`#7229 <https://github.com/pylint-dev/pylint/issues/7229>`_)

- The ``ignored-modules`` option will now be correctly taken into account for ``no-name-in-module``.

  Closes #7578 (`#7578 <https://github.com/pylint-dev/pylint/issues/7578>`_)

- ``sys.argv`` is now always correctly considered as impossible to infer (instead of
  using the actual values given to pylint).

  Closes #7710 (`#7710 <https://github.com/pylint-dev/pylint/issues/7710>`_)

- Avoid duplicative warnings for unqualified exception names in the ``overgeneral-exceptions``
  setting when running with ``--jobs``.

  Closes #7774 (`#7774 <https://github.com/pylint-dev/pylint/issues/7774>`_)

- Don't show class fields more than once in Pyreverse diagrams.

  Closes #8189 (`#8189 <https://github.com/pylint-dev/pylint/issues/8189>`_)

- Fix ``used-before-assignment`` false negative when TYPE_CHECKING imports
  are used in multiple scopes.

  Closes #8198 (`#8198 <https://github.com/pylint-dev/pylint/issues/8198>`_)

- ``--clear-cache-post-run`` now also clears LRU caches for pylint utilities
  holding references to AST nodes.

  Closes #8361 (`#8361 <https://github.com/pylint-dev/pylint/issues/8361>`_)

- Fix a crash when ``TYPE_CHECKING`` is used without importing it.

  Closes #8434 (`#8434 <https://github.com/pylint-dev/pylint/issues/8434>`_)

- Fix a ``used-before-assignment`` false positive when imports
  are made under the ``TYPE_CHECKING`` else if branch.

  Closes #8437 (`#8437 <https://github.com/pylint-dev/pylint/issues/8437>`_)

- Fix a regression of ``preferred-modules`` where a partial match was used instead of the required full match.

  Closes #8453 (`#8453 <https://github.com/pylint-dev/pylint/issues/8453>`_)

- Fix a crash in pyreverse when "/" characters are used in the output filename e.g pyreverse -o png -p name/ path/to/project.

  Closes #8504 (`#8504 <https://github.com/pylint-dev/pylint/issues/8504>`_)

- Don't show arrows more than once in Pyreverse diagrams.

  Closes #8522 (`#8522 <https://github.com/pylint-dev/pylint/issues/8522>`_)

- Improve output of ``consider-using-generator`` message for ``min()`` calls with ``default`` keyword.

  Closes #8563 (`#8563 <https://github.com/pylint-dev/pylint/issues/8563>`_)

- Fixed a crash when generating a configuration file: ``tomlkit.exceptions.TOMLKitError: Can't add a table to a dotted key``
  caused by tomlkit ``v0.11.8``.

  Closes #8632 (`#8632 <https://github.com/pylint-dev/pylint/issues/8632>`_)

- Fix a line break error in Pyreverse dot output.

  Closes #8671 (`#8671 <https://github.com/pylint-dev/pylint/issues/8671>`_)

- Fix a false positive for ``method-hidden`` when using ``cached_property`` decorator.

  Closes #8753 (`#8753 <https://github.com/pylint-dev/pylint/issues/8753>`_)

- Dunder methods defined in lambda do not trigger ``unnecessary-dunder-call`` anymore, if they cannot be replaced by the non-dunder call.

  Closes #8769 (`#8769 <https://github.com/pylint-dev/pylint/issues/8769>`_)

- Don't show duplicate type annotations in Pyreverse diagrams.

  Closes #8888 (`#8888 <https://github.com/pylint-dev/pylint/issues/8888>`_)

- Fixing inconsistent hashing issue in `BaseChecker` causing some reports not being exported.

  Closes #9001 (`#9001 <https://github.com/pylint-dev/pylint/issues/9001>`_)

- Don't add `Optional` to `|` annotations with `None` in Pyreverse diagrams.

  Closes #9014 (`#9014 <https://github.com/pylint-dev/pylint/issues/9014>`_)

- Pyreverse doesn't show multiple class association arrows anymore, but only the strongest one.

  Refs #9045 (`#9045 <https://github.com/pylint-dev/pylint/issues/9045>`_)

- Prevented data loss in the linter stats for messages relating
  to the linter itself (e.g. ``unknown-option-value``), fixing
  problems with score, fail-on, etc.

  Closes #9059 (`#9059 <https://github.com/pylint-dev/pylint/issues/9059>`_)

- Fix crash in refactoring checker when unary operand used with variable in for loop.

  Closes #9074 (`#9074 <https://github.com/pylint-dev/pylint/issues/9074>`_)



Other Changes
-------------

- Pylint now exposes its type annotations.

  Closes #5488 and #2079 (`#5488 <https://github.com/pylint-dev/pylint/issues/5488>`_)

- Search for ``pyproject.toml`` recursively in parent directories up to a project or file system root.

  Refs #7163, Closes #3289 (`#7163 <https://github.com/pylint-dev/pylint/issues/7163>`_)

- All code related to the optparse config parsing has been removed.

  Refs #8405 (`#8405 <https://github.com/pylint-dev/pylint/issues/8405>`_)

- Pylint now supports python 3.12.

  Refs #8718 (`#8718 <https://github.com/pylint-dev/pylint/issues/8718>`_)

- Add a CITATION.cff file to the root of the repository containing the necessary metadata to cite Pylint.

  Closes #8760 (`#8760 <https://github.com/pylint-dev/pylint/issues/8760>`_)

- Renamed the "unneeded-not" error into "unnecessary_negation" to be clearer.

  Closes #8789 (`#8789 <https://github.com/pylint-dev/pylint/issues/8789>`_)



Internal Changes
----------------

- ``get_message_definition`` was removed from the base checker API. You can access
  message definitions through the ``MessageStore``.

  Refs #8401 (`#8401 <https://github.com/pylint-dev/pylint/issues/8401>`_)

- Everything related to the ``__implements__`` construct was removed. It was based on PEP245
  that was proposed in 2001 and rejected in 2006.

  All the classes inheriting ``Interface`` in ``pylint.interfaces`` were removed.
  ``Checker`` should only inherit ``BaseChecker`` or any of the other checker types
  from ``pylint.checkers``. ``Reporter`` should only inherit ``BaseReporter``.

  Refs #8404 (`#8404 <https://github.com/pylint-dev/pylint/issues/8404>`_)

- ``modname`` and ``msg_store`` are now required to be given in ``FileState``.
  ``collect_block_lines`` has also been removed. ``Pylinter.current_name``
  cannot be null anymore.

  Refs #8407 (`#8407 <https://github.com/pylint-dev/pylint/issues/8407>`_)

- ``Reporter.set_output`` was removed in favor of ``reporter.out = stream``.

  Refs #8408 (`#8408 <https://github.com/pylint-dev/pylint/issues/8408>`_)

- A number of old utility functions and classes have been removed:

  ``MapReduceMixin``: To make a checker reduce map data simply implement
  ``get_map_data`` and ``reduce_map_data``.

  ``is_inside_lambda``: Use ``utils.get_node_first_ancestor_of_type(x, nodes.Lambda)``

  ``check_messages``: Use ``utils.only_required_for_messages``

  ``is_class_subscriptable_pep585_with_postponed_evaluation_enabled``: Use
  ``is_postponed_evaluation_enabled(node)`` and ``is_node_in_type_annotation_context(node)``

  ``get_python_path``: assumption that there's always an __init__.py is not true since
  python 3.3 and is causing problems, particularly with PEP 420. Use ``discover_package_path``
  and pass source root(s).

  ``fix_import_path``: Use ``augmented_sys_path`` and pass additional ``sys.path``
  entries as an argument obtained from ``discover_package_path``.

  ``get_global_option``: Use ``checker.linter.config`` to get all global options.

  Related private objects have been removed as well.

  Refs #8409 (`#8409 <https://github.com/pylint-dev/pylint/issues/8409>`_)

- ``colorize_ansi`` now only accepts a ``MessageStyle`` object.

  Refs #8412 (`#8412 <https://github.com/pylint-dev/pylint/issues/8412>`_)

- Following a deprecation period, ``Pylinter.check`` now only works with sequences of strings, not strings.

  Refs #8463 (`#8463 <https://github.com/pylint-dev/pylint/issues/8463>`_)

- Following a deprecation period, ``ColorizedTextReporter`` only accepts ``ColorMappingDict``.

  Refs #8464 (`#8464 <https://github.com/pylint-dev/pylint/issues/8464>`_)

- Following a deprecation period, ``MessageTest``'s ``end_line`` and ``end_col_offset``
  must be accurate in functional tests (for python 3.8 or above on cpython, and for
  python 3.9 or superior on pypy).

  Refs #8466 (`#8466 <https://github.com/pylint-dev/pylint/issues/8466>`_)

- Following a deprecation period, the ``do_exit`` argument of the ``Run`` class (and of the ``_Run``
  class in testutils) were removed.

  Refs #8472 (`#8472 <https://github.com/pylint-dev/pylint/issues/8472>`_)

- Following a deprecation period, the ``py_version`` argument of the
  ``MessageDefinition.may_be_emitted`` function is now required. The most likely solution
  is to use 'linter.config.py_version' if you need to keep using this
  function, or to use 'MessageDefinition.is_message_enabled' instead.

  Refs #8473 (`#8473 <https://github.com/pylint-dev/pylint/issues/8473>`_)

- Following a deprecation period, the ``OutputLine`` class now requires
  the right number of argument all the time. The functional output can be
  regenerated automatically to achieve that easily.

  Refs #8474 (`#8474 <https://github.com/pylint-dev/pylint/issues/8474>`_)

- Following a deprecation period, ``is_typing_guard``, ``is_node_in_typing_guarded_import_block`` and
  ``is_node_in_guarded_import_block`` from ``pylint.utils`` were removed: use a combination of
  ``is_sys_guard`` and ``in_type_checking_block`` instead.

  Refs #8475 (`#8475 <https://github.com/pylint-dev/pylint/issues/8475>`_)

- Following a deprecation period, the ``location`` argument of the
  ``Message`` class must now be a ``MessageLocationTuple``.

  Refs #8477 (`#8477 <https://github.com/pylint-dev/pylint/issues/8477>`_)

- Following a deprecation period, the ``check_single_file`` function of the
  ``Pylinter`` is replaced by ``Pylinter.check_single_file_item``.

  Refs #8478 (`#8478 <https://github.com/pylint-dev/pylint/issues/8478>`_)



Performance Improvements
------------------------

- ``pylint`` runs (at least) ~5% faster after improvements to ``astroid``
  that make better use of the inference cache.

  Refs pylint-dev/astroid#529 (`#529 <https://github.com/pylint-dev/pylint/issues/529>`_)

- - Optimize ``is_trailing_comma()``.
  - Cache ``class_is_abstract()``.

  Refs #1954 (`#1954 <https://github.com/pylint-dev/pylint/issues/1954>`_)

- Exit immediately if all messages are disabled.

  Closes #8715 (`#8715 <https://github.com/pylint-dev/pylint/issues/8715>`_)
````

## File: doc/whatsnew/3/3.1/index.rst
````
***************************
 What's New in Pylint 3.1
***************************

.. toctree::
   :maxdepth: 2

:Release: 3.1
:Date: 2024-02-25

Summary -- Release highlights
=============================

Two new checks -- ``use-yield-from``, ``deprecated-attribute`` --
and a smattering of bug fixes.

.. towncrier release notes start

What's new in Pylint 3.1.1?
---------------------------
Release date: 2024-05-13


False Positives Fixed
---------------------

- Treat `attrs.define` and `attrs.frozen` as dataclass decorators in
  `too-few-public-methods` check.

  Closes #9345 (`#9345 <https://github.com/pylint-dev/pylint/issues/9345>`_)

- Fix a false positive with ``singledispatchmethod-function`` when a method is decorated with both ``functools.singledispatchmethod`` and ``staticmethod``.

  Closes #9531 (`#9531 <https://github.com/pylint-dev/pylint/issues/9531>`_)

- Fix a false positive for ``consider-using-dict-items`` when iterating using ``keys()`` and then deleting an item using the key as a lookup.

  Closes #9554 (`#9554 <https://github.com/pylint-dev/pylint/issues/9554>`_)



What's new in Pylint 3.1.0?
---------------------------
Release date: 2024-02-25


New Features
------------

- Skip ``consider-using-join`` check for non-empty separators if an ``suggest-join-with-non-empty-separator`` option is set to ``no``.

  Closes #8701 (`#8701 <https://github.com/pylint-dev/pylint/issues/8701>`_)

- Discover ``.pyi`` files when linting.

  These can be ignored with the ``ignore-patterns`` setting.

  Closes #9097 (`#9097 <https://github.com/pylint-dev/pylint/issues/9097>`_)

- Check ``TypeAlias`` and ``TypeVar`` (PEP 695) nodes for ``invalid-name``.

  Refs #9196 (`#9196 <https://github.com/pylint-dev/pylint/issues/9196>`_)

- Support for resolving external toml files named pylintrc.toml and .pylintrc.toml.

  Closes #9228 (`#9228 <https://github.com/pylint-dev/pylint/issues/9228>`_)

- Check for `.clear`, `.discard`, `.pop` and `remove` methods being called on a set while it is being iterated over.

  Closes #9334 (`#9334 <https://github.com/pylint-dev/pylint/issues/9334>`_)



New Checks
----------

- New message `use-yield-from` added to the refactoring checker. This message is emitted when yielding from a loop can be replaced by `yield from`.

  Closes #9229. (`#9229 <https://github.com/pylint-dev/pylint/issues/9229>`_)

- Added a ``deprecated-attribute`` message to check deprecated attributes in the stdlib.

  Closes #8855 (`#8855 <https://github.com/pylint-dev/pylint/issues/8855>`_)


False Positives Fixed
---------------------

- Fixed false positive for ``inherit-non-class`` for generic Protocols.

  Closes #9106 (`#9106 <https://github.com/pylint-dev/pylint/issues/9106>`_)

- Exempt ``TypedDict`` from ``typing_extensions`` from ``too-many-ancestor`` checks.

  Refs #9167 (`#9167 <https://github.com/pylint-dev/pylint/issues/9167>`_)



False Negatives Fixed
---------------------

- Extend broad-exception-raised and broad-exception-caught to except*.

  Closes #8827 (`#8827 <https://github.com/pylint-dev/pylint/issues/8827>`_)

- Fix a false-negative for unnecessary if blocks using a different than expected ordering of arguments.

  Closes #8947. (`#8947 <https://github.com/pylint-dev/pylint/issues/8947>`_)



Other Bug Fixes
---------------

- Improve the message provided for wrong-import-order check.  Instead of the import statement ("import x"), the message now specifies the import that is out of order and which imports should come after it.  As reported in the issue, this is particularly helpful if there are multiple imports on a single line that do not follow the PEP8 convention.

  The message will report imports as follows:
  For "import X", it will report "(standard/third party/first party/local) import X"
  For "import X.Y" and "from X import Y", it will report "(standard/third party/first party/local) import X.Y"
  The import category is specified to provide explanation as to why pylint has issued the message and guidance to the developer on how to fix the problem.

  Closes #8808 (`#8808 <https://github.com/pylint-dev/pylint/issues/8808>`_)



Other Changes
-------------

- Print how many files were checked in verbose mode.

  Closes #8935 (`#8935 <https://github.com/pylint-dev/pylint/issues/8935>`_)

- Fix a crash when an enum class which is also decorated with a ``dataclasses.dataclass`` decorator is defined.

  Closes #9100 (`#9100 <https://github.com/pylint-dev/pylint/issues/9100>`_)



Internal Changes
----------------

- Update astroid version to 3.1.0.

  Refs #9457 (`#9457 <https://github.com/pylint-dev/pylint/issues/9457>`_)
````

## File: doc/whatsnew/3/3.2/index.rst
````
***************************
 What's New in Pylint 3.2
***************************

.. toctree::
   :maxdepth: 2

:Release: 3.2
:Date: TBA

Summary -- Release highlights
=============================

.. towncrier release notes start

What's new in Pylint 3.2.7?
---------------------------
Release date: 2024-08-31


False Positives Fixed
---------------------

- Fixed a false positive `unreachable` for `NoReturn` coroutine functions.

  Closes #9840. (`#9840 <https://github.com/pylint-dev/pylint/issues/9840>`_)



Other Bug Fixes
---------------

- Fix crash in refactoring checker when calling a lambda bound as a method.

  Closes #9865 (`#9865 <https://github.com/pylint-dev/pylint/issues/9865>`_)

- Fix a crash in ``undefined-loop-variable`` when providing the ``iterable`` argument to ``enumerate()``.

  Closes #9875 (`#9875 <https://github.com/pylint-dev/pylint/issues/9875>`_)

- Fix to address indeterminacy of error message in case a module name is same as another in a separate namespace.

  Refs #9883 (`#9883 <https://github.com/pylint-dev/pylint/issues/9883>`_)



What's new in Pylint 3.2.6?
---------------------------
Release date: 2024-07-21


False Positives Fixed
---------------------

- Quiet false positives for `unexpected-keyword-arg` when pylint cannot
  determine which of two or more dynamically defined classes is being instantiated.

  Closes #9672 (`#9672 <https://github.com/pylint-dev/pylint/issues/9672>`_)

- Fix a false positive for ``missing-param-doc`` where a method which is decorated with ``typing.overload`` was expected to have a docstring specifying its parameters.

  Closes #9739 (`#9739 <https://github.com/pylint-dev/pylint/issues/9739>`_)

- Fix a regression that raised ``invalid-name`` on class attributes merely
  overriding invalid names from an ancestor.

  Closes #9765 (`#9765 <https://github.com/pylint-dev/pylint/issues/9765>`_)

- Treat `assert_never()` the same way when imported from `typing_extensions`.

  Closes #9780 (`#9780 <https://github.com/pylint-dev/pylint/issues/9780>`_)

- Fix a false positive for `consider-using-min-max-builtin` when the assignment target is an attribute.

  Refs #9800 (`#9800 <https://github.com/pylint-dev/pylint/issues/9800>`_)



Other Bug Fixes
---------------

- Fix an `AssertionError` arising from properties that return partial functions.

  Closes #9214 (`#9214 <https://github.com/pylint-dev/pylint/issues/9214>`_)

- Fix a crash when a subclass extends ``__slots__``.

  Closes #9814 (`#9814 <https://github.com/pylint-dev/pylint/issues/9814>`_)



What's new in Pylint 3.2.5?
---------------------------
Release date: 2024-06-28


Other Bug Fixes
---------------

- Fixed a false positive ``unreachable-code`` when using ``typing.Any`` as return type in python
  3.8, the ``typing.NoReturn`` are not taken into account anymore for python 3.8 however.

  Closes #9751 (`#9751 <https://github.com/pylint-dev/pylint/issues/9751>`_)



What's new in Pylint 3.2.4?
---------------------------
Release date: 2024-06-26


False Positives Fixed
---------------------

- Prevent emitting ``possibly-used-before-assignment`` when relying on names
  only potentially not defined in conditional blocks guarded by functions
  annotated with ``typing.Never`` or ``typing.NoReturn``.

  Closes #9674 (`#9674 <https://github.com/pylint-dev/pylint/issues/9674>`_)



Other Bug Fixes
---------------

- Fixed a crash when the lineno of a variable used as an annotation wasn't available for ``undefined-variable``.

  Closes #8866 (`#8866 <https://github.com/pylint-dev/pylint/issues/8866>`_)

- Fixed a crash when the ``start`` value in an ``enumerate`` was non-constant and impossible to infer
  (like in``enumerate(apples, start=int(random_apple_index)``) for ``unnecessary-list-index-lookup``.

  Closes #9078 (`#9078 <https://github.com/pylint-dev/pylint/issues/9078>`_)

- Fixed a crash in ``symilar`` when the ``-d`` or ``-i`` short option were not properly recognized.
  It's still impossible to do ``-d=1`` (you must do ``-d 1``).

  Closes #9343 (`#9343 <https://github.com/pylint-dev/pylint/issues/9343>`_)



What's new in Pylint 3.2.3?
---------------------------
Release date: 2024-06-06


False Positives Fixed
---------------------

- Classes with only an Ellipsis (``...``) in their body do not trigger 'multiple-statements'
  anymore if they are inlined (in accordance with black's 2024 style).

  Closes #9398 (`#9398 <https://github.com/pylint-dev/pylint/issues/9398>`_)

- Fix a false positive for ``redefined-outer-name`` when there is a name defined in an exception-handling block which shares the same name as a local variable that has been defined in a function body.

  Closes #9671 (`#9671 <https://github.com/pylint-dev/pylint/issues/9671>`_)

- Fix a false positive for ``use-yield-from`` when using the return value from the ``yield`` atom.

  Closes #9696 (`#9696 <https://github.com/pylint-dev/pylint/issues/9696>`_)



What's new in Pylint 3.2.2?
---------------------------
Release date: 2024-05-20


False Positives Fixed
---------------------

- Fix multiple false positives for generic class syntax added in Python 3.12 (PEP 695).

  Closes #9406 (`#9406 <https://github.com/pylint-dev/pylint/issues/9406>`_)

- Exclude context manager without cleanup from
  ``contextmanager-generator-missing-cleanup`` checks.

  Closes #9625 (`#9625 <https://github.com/pylint-dev/pylint/issues/9625>`_)



What's new in Pylint 3.2.1?
---------------------------
Release date: 2024-05-18


False Positives Fixed
---------------------

- Exclude if/else branches containing terminating functions (e.g. `sys.exit()`)
  from `possibly-used-before-assignment` checks.

  Closes #9627 (`#9627 <https://github.com/pylint-dev/pylint/issues/9627>`_)

- Don't emit ``typevar-name-incorrect-variance`` warnings for PEP 695 style TypeVars.
  The variance is inferred automatically by the type checker.
  Adding ``_co`` or ``_contra`` suffix can help to reason about TypeVar.

  Refs #9638 (`#9638 <https://github.com/pylint-dev/pylint/issues/9638>`_)

- Fix a false positive for `possibly-used-before-assignment` when using
  `typing.assert_never()` (3.11+) to indicate exhaustiveness.

  Closes #9643 (`#9643 <https://github.com/pylint-dev/pylint/issues/9643>`_)



Other Bug Fixes
---------------

- Fix a false negative for ``--ignore-patterns`` when the directory to be linted is specified using a dot(``.``) and all files are ignored instead of only the files whose name begin with a dot.

  Closes #9273 (`#9273 <https://github.com/pylint-dev/pylint/issues/9273>`_)

- Restore "errors / warnings by module" section to report output (with `-ry`).

  Closes #9145 (`#9145 <https://github.com/pylint-dev/pylint/issues/9145>`_)

- ``trailing-comma-tuple`` should now be correctly emitted when it was disabled globally
  but enabled via local message control, after removal of an over-optimisation.

  Refs #9608. (`#9608 <https://github.com/pylint-dev/pylint/issues/9608>`_)

- Add `--prefer-stubs=yes` option to opt-in to the astroid 3.2 feature
  that prefers `.pyi` stubs over same-named `.py` files. This has the
  potential to reduce `no-member` errors but at the cost of more errors
  such as `not-an-iterable` from function bodies appearing as `...`.

  Defaults to `no`.

  Closes #9626
  Closes #9623 (`#9626 <https://github.com/pylint-dev/pylint/issues/9626>`_)



Internal Changes
----------------

- Update astroid version to 3.2.1. This solves some reports of ``RecursionError``
  and also makes the *prefer .pyi stubs* feature in astroid 3.2.0 *opt-in*
  with the aforementioned ``--prefer-stubs=y`` option.

  Refs #9139 (`#9139 <https://github.com/pylint-dev/pylint/issues/9139>`_)



What's new in Pylint 3.2.0?
---------------------------
Release date: 2024-05-14


New Features
------------

- Understand `six.PY2` and `six.PY3` for conditional imports.

  Closes #3501 (`#3501 <https://github.com/pylint-dev/pylint/issues/3501>`_)

- A new `github` reporter has been added. This reporter  returns the output of `pylint` in a format that
  Github can use to automatically annotate code. Use it with `pylint --output-format=github` on your Github Workflows.

  Closes #9443. (`#9443 <https://github.com/pylint-dev/pylint/issues/9443>`_)



New Checks
----------

- Add check ``possibly-used-before-assignment`` when relying on names after an ``if/else``
  switch when one branch failed to define the name, raise, or return.

  Closes #1727 (`#1727 <https://github.com/pylint-dev/pylint/issues/1727>`_)

- Checks for generators that use contextmanagers that don't handle cleanup properly.
  Is meant to raise visibility on the case that a generator is not fully exhausted and the contextmanager is not cleaned up properly.
  A contextmanager must yield a non-constant value and not handle cleanup for GeneratorExit.
  The using generator must attempt to use the yielded context value `with x() as y` and not just `with x()`.

  Closes #2832 (`#2832 <https://github.com/pylint-dev/pylint/issues/2832>`_)



False Negatives Fixed
---------------------

- If and Try nodes are now checked for useless return statements as well.

  Closes #9449. (`#9449 <https://github.com/pylint-dev/pylint/issues/9449>`_)

- Fix false negative for ``property-with-parameters`` in the case of parameters which are ``positional-only``, ``keyword-only``, ``variadic positional`` or ``variadic keyword``.

  Closes #9584 (`#9584 <https://github.com/pylint-dev/pylint/issues/9584>`_)

False Positives Fixed
---------------------

pylint now understands the ``@overload`` decorator return values better.

Closes #4696 (`#4696 <https://github.com/pylint-dev/pylint/issues/4696>`_)
Refs #9606 (`#9606 <https://github.com/pylint-dev/pylint/issues/9606>`_)

Performance Improvements
------------------------


- Ignored modules are now not checked at all, instead of being checked and then
  ignored. This should speed up the analysis of large codebases which have
  ignored modules.

  Closes #9442 (`#9442 <https://github.com/pylint-dev/pylint/issues/9442>`_) (`#9442 <https://github.com/pylint-dev/pylint/issues/9442>`_)


- ImportChecker's logic has been modified to avoid context files when possible. This makes it possible
  to cache module searches on astroid and reduce execution times.

  Refs #9310. (`#9310 <https://github.com/pylint-dev/pylint/issues/9310>`_)

- An internal check for ``trailing-comma-tuple`` being enabled for a file or not is now
  done once per file instead of once for each token.

  Refs #9608. (`#9608 <https://github.com/pylint-dev/pylint/issues/9608>`_)
````

## File: doc/whatsnew/3/3.3/index.rst
````
***************************
 What's New in Pylint 3.3
***************************

.. toctree::
   :maxdepth: 2

:Release:3.3
:Date: 2024-09-20

Summary -- Release highlights
=============================

.. towncrier release notes start

What's new in Pylint 3.3.8?
---------------------------
Release date: 2025-08-09

This patch release includes an exceptional fix for a false negative issue.
For details, see: https://github.com/pylint-dev/pylint/pull/10482#issuecomment-3164514082

False Positives Fixed
---------------------

- Fix false positives for `possibly-used-before-assignment` when variables are exhaustively
  assigned within a `match` block.

  Closes #9668 (`#9668 <https://github.com/pylint-dev/pylint/issues/9668>`_)

- Fix false positive for `missing-raises-doc` and `missing-yield-doc` when the method length is less than docstring-min-length.

  Refs #10104 (`#10104 <https://github.com/pylint-dev/pylint/issues/10104>`_)

- Fix a false positive for ``unused-variable`` when multiple except handlers bind the same name under a try block.

  Closes #10426 (`#10426 <https://github.com/pylint-dev/pylint/issues/10426>`_)



False Negatives Fixed
---------------------

- Fix false-negative for ``used-before-assignment`` with ``from __future__ import annotations`` in function definitions.

  Refs #10482 (`#10482 <https://github.com/pylint-dev/pylint/issues/10482>`_)



Other Bug Fixes
---------------

- Fix a bug in Pyreverse where aggregations and associations were included in diagrams regardless of the selected --filter-mode (such as PUB_ONLY, ALL, etc.).

  Closes #10373 (`#10373 <https://github.com/pylint-dev/pylint/issues/10373>`_)

- Fix double underscores erroneously rendering as bold in pyreverse's Mermaid output.

  Closes #10402 (`#10402 <https://github.com/pylint-dev/pylint/issues/10402>`_)



What's new in Pylint 3.3.7?
---------------------------
Release date: 2025-05-04


False Positives Fixed
---------------------

- Comparisons between two calls to `type()` won't raise an ``unidiomatic-typecheck`` warning anymore, consistent with the behavior applied only for ``==`` previously.

  Closes #10161 (`#10161 <https://github.com/pylint-dev/pylint/issues/10161>`_)



Other Bug Fixes
---------------

- Fixed a crash when importing a class decorator that did not exist with the same name as a class attribute after the class definition.

  Closes #10105 (`#10105 <https://github.com/pylint-dev/pylint/issues/10105>`_)

- Fix a crash caused by malformed format strings when using `.format` with keyword arguments.

  Closes #10282 (`#10282 <https://github.com/pylint-dev/pylint/issues/10282>`_)

- Using a slice as a class decorator now raises a ``not-callable`` message instead of crashing. A lot of checks that dealt with decorators (too many to list) are now shortcut if the decorator can't immediately be inferred to a function or class definition.

  Closes #10334 (`#10334 <https://github.com/pylint-dev/pylint/issues/10334>`_)



Other Changes
-------------

- The algorithm used for ``no-member`` suggestions is now more efficient and cuts the
  calculation when the distance score is already above the threshold.

  Refs #10277 (`#10277 <https://github.com/pylint-dev/pylint/issues/10277>`_)



What's new in Pylint 3.3.6?
---------------------------
Release date: 2025-03-20


False Positives Fixed
---------------------

- Fix a false positive for `used-before-assignment` when an inner function's return type
  annotation is a class defined at module scope.

  Closes #9391 (`#9391 <https://github.com/pylint-dev/pylint/issues/9391>`_)



What's new in Pylint 3.3.5?
---------------------------
Release date: 2025-03-09


False Positives Fixed
---------------------

- Fix false positives for `use-implicit-booleaness-not-comparison`, `use-implicit-booleaness-not-comparison-to-string`
  and `use-implicit-booleaness-not-comparison-to-zero` when chained comparisons are checked.

  Closes #10065 (`#10065 <https://github.com/pylint-dev/pylint/issues/10065>`_)

- Fix a false positive for ``invalid-getnewargs-ex-returned`` when the tuple or dict has been assigned to a name.

  Closes #10208 (`#10208 <https://github.com/pylint-dev/pylint/issues/10208>`_)

- Remove `getopt` and `optparse` from the list of deprecated modules.

  Closes #10211 (`#10211 <https://github.com/pylint-dev/pylint/issues/10211>`_)



Other Bug Fixes
---------------

- Fixed conditional import x.y causing false positive possibly-used-before-assignment.

  Closes #10081 (`#10081 <https://github.com/pylint-dev/pylint/issues/10081>`_)

- Fix a crash when something besides a class is found in an except handler.

  Closes #10106 (`#10106 <https://github.com/pylint-dev/pylint/issues/10106>`_)

- Fixed raising invalid-name when using camelCase for private methods with two leading underscores.

  Closes #10189 (`#10189 <https://github.com/pylint-dev/pylint/issues/10189>`_)



Other Changes
-------------

- Upload release assets to PyPI via Trusted Publishing.

  Closes #10256 (`#10256 <https://github.com/pylint-dev/pylint/issues/10256>`_)



What's new in Pylint 3.3.4?
---------------------------
Release date: 2025-01-28


Other Bug Fixes
---------------

- Fixes "skipped files" count calculation; the previous method was displaying an arbitrary number.

  Closes #10073 (`#10073 <https://github.com/pylint-dev/pylint/issues/10073>`_)

- Fixes a crash that occurred when pylint was run in a container on a host with cgroupsv2 and restrictions on CPU usage.

  Closes #10103 (`#10103 <https://github.com/pylint-dev/pylint/issues/10103>`_)

- Relaxed the requirements for isort so pylint can benefit from isort 6.

  Closes #10203 (`#10203 <https://github.com/pylint-dev/pylint/issues/10203>`_)



What's new in Pylint 3.3.3?
---------------------------
Release date: 2024-12-23


False Positives Fixed
---------------------

- Fix false positives for ``undefined-variable`` for classes using Python 3.12
  generic type syntax.

  Closes #9335 (`#9335 <https://github.com/pylint-dev/pylint/issues/9335>`_)

- Fix a false positive for `use-implicit-booleaness-not-len`. No lint should be emitted for
  generators (`len` is not defined for generators).

  Refs #10100 (`#10100 <https://github.com/pylint-dev/pylint/issues/10100>`_)



Other Bug Fixes
---------------

- Fix ``Unable to import 'collections.abc' (import-error)`` on Python 3.13.1.

  Closes #10112 (`#10112 <https://github.com/pylint-dev/pylint/issues/10112>`_)



What's new in Pylint 3.3.2?
---------------------------
Release date: 2024-12-01


False Positives Fixed
---------------------

- Fix a false positive for `potential-index-error` when an indexed iterable
  contains a starred element that evaluates to more than one item.

  Closes #10076 (`#10076 <https://github.com/pylint-dev/pylint/issues/10076>`_)



Other Bug Fixes
---------------

- Fixes the issue with --source-root option not working when the source files are in a subdirectory of the source root (e.g. when using a /src layout).

  Closes #10026 (`#10026 <https://github.com/pylint-dev/pylint/issues/10026>`_)



What's new in Pylint 3.3.1?
---------------------------
Release date: 2024-09-24


False Positives Fixed
---------------------

- Fix regression causing some f-strings to not be inferred as strings.

  Closes #9947 (`#9947 <https://github.com/pylint-dev/pylint/issues/9947>`_)



What's new in Pylint 3.3.0?
---------------------------
Release date: 2024-09-20


Changes requiring user actions
------------------------------

- We migrated ``symilar`` to argparse, from getopt, so the error and help output changed
  (for the better). We exit with 2 instead of sometime 1, sometime 2. The error output
  is not captured by the runner anymore. It's not possible to use a value for the
  boolean options anymore (``--ignore-comments 1`` should become ``--ignore-comments``).

  Refs #9731 (`#9731 <https://github.com/pylint-dev/pylint/issues/9731>`_)



New Features
------------

- Add new `declare-non-slot` error which reports when a class has a `__slots__` member and a type hint on the class is not present in `__slots__`.

  Refs #9499 (`#9499 <https://github.com/pylint-dev/pylint/issues/9499>`_)



New Checks
----------

- Added `too-many-positional-arguments` to allow distinguishing the configuration for too many
  total arguments (with keyword-only params specified after `*`) from the configuration
  for too many positional-or-keyword or positional-only arguments.

  As part of evaluating whether this check makes sense for your project, ensure you
  adjust the value of `--max-positional-arguments`.

  Closes #9099 (`#9099 <https://github.com/pylint-dev/pylint/issues/9099>`_)

- Add `using-exception-groups-in-unsupported-version` and
  `using-generic-type-syntax-in-unsupported-version` for uses of Python 3.11+ or
  3.12+ features on lower supported versions provided with `--py-version`.

  Closes #9791 (`#9791 <https://github.com/pylint-dev/pylint/issues/9791>`_)

- Add `using-assignment-expression-in-unsupported-version` for uses of `:=` (walrus operator)
  on Python versions below 3.8 provided with `--py-version`.

  Closes #9820 (`#9820 <https://github.com/pylint-dev/pylint/issues/9820>`_)

- Add `using-positional-only-args-in-unsupported-version` for uses of positional-only args on
  Python versions below 3.8 provided with `--py-version`.

  Closes #9823 (`#9823 <https://github.com/pylint-dev/pylint/issues/9823>`_)

- Add ``unnecessary-default-type-args`` to the ``typing`` extension to detect the use
  of unnecessary default type args for ``typing.Generator`` and ``typing.AsyncGenerator``.

  Refs #9938 (`#9938 <https://github.com/pylint-dev/pylint/issues/9938>`_)



False Negatives Fixed
---------------------

- Fix computation of never-returning function: `Never` is handled in addition to `NoReturn`, and priority is given to the explicit `--never-returning-functions` option.

  Closes #7565. (`#7565 <https://github.com/pylint-dev/pylint/issues/7565>`_)

- Fix a false negative for `await-outside-async` when await is inside Lambda.

  Refs #9653 (`#9653 <https://github.com/pylint-dev/pylint/issues/9653>`_)

- Fix a false negative for ``duplicate-argument-name`` by including ``positional-only``, ``*args`` and ``**kwargs`` arguments in the check.

  Closes #9669 (`#9669 <https://github.com/pylint-dev/pylint/issues/9669>`_)

- Fix false negative for `multiple-statements` when multiple statements are present on `else` and `finally` lines of `try`.

  Refs #9759 (`#9759 <https://github.com/pylint-dev/pylint/issues/9759>`_)

- Fix false negatives when `isinstance` does not have exactly two arguments.
  pylint now emits a `too-many-function-args` or `no-value-for-parameter`
  appropriately for `isinstance` calls.

  Closes #9847 (`#9847 <https://github.com/pylint-dev/pylint/issues/9847>`_)



Other Bug Fixes
---------------

- `--enable` with `--disable=all` now produces an error, when an unknown msg code is used. Internal `pylint` messages are no longer affected by `--disable=all`.

  Closes #9403 (`#9403 <https://github.com/pylint-dev/pylint/issues/9403>`_)

- Impossible to compile regexes for paths in the configuration or argument given to pylint won't crash anymore but
  raise an argparse error and display the error message from ``re.compile`` instead.

  Closes #9680 (`#9680 <https://github.com/pylint-dev/pylint/issues/9680>`_)

- Fix a bug where a ``tox.ini`` file with pylint configuration was ignored and it exists in the current directory.

  ``.cfg`` and ``.ini`` files containing a ``Pylint`` configuration may now use a section named ``[pylint]``. This enhancement impacts the scenario where these file types are used as defaults when they are present and have not been explicitly referred to, using the ``--rcfile`` option.

  Closes #9727 (`#9727 <https://github.com/pylint-dev/pylint/issues/9727>`_)

- Improve file discovery for directories that are not python packages.

  Closes #9764 (`#9764 <https://github.com/pylint-dev/pylint/issues/9764>`_)



Other Changes
-------------

- Remove support for launching pylint with Python 3.8.
  Code that supports Python 3.8 can still be linted with the ``--py-version=3.8`` setting.

  Refs #9774 (`#9774 <https://github.com/pylint-dev/pylint/issues/9774>`_)

- Add support for Python 3.13.

  Refs #9852 (`#9852 <https://github.com/pylint-dev/pylint/issues/9852>`_)



Internal Changes
----------------

- All variables, classes, functions and file names containing the word 'similar', when it was,
  in fact, referring to 'symilar' (the standalone program for the duplicate-code check) were renamed
  to 'symilar'.

  Closes #9734 (`#9734 <https://github.com/pylint-dev/pylint/issues/9734>`_)

- Remove old-style classes (Python 2) code and remove check for new-style class since everything is new-style in Python 3. Updated doc for exception checker to remove reference to new style class.

  Refs #9925 (`#9925 <https://github.com/pylint-dev/pylint/issues/9925>`_)
````

## File: doc/whatsnew/3/index.rst
````
3.x
===

This is the full list of change in pylint 3.x minors, by categories.

.. toctree::
   :maxdepth: 2

   3.3/index
   3.2/index
   3.1/index
   3.0/index
````

## File: doc/whatsnew/4/4.0/index.rst
````
***************************
 What's New in Pylint 4.0
***************************

.. toctree::
   :maxdepth: 2

:Release:4.0
:Date: TBA

Summary -- Release highlights
=============================


.. towncrier release notes start
````

## File: doc/whatsnew/4/index.rst
````
4.x
===

This is the full list of change in pylint 4.x minors, by categories.

.. toctree::
   :maxdepth: 2

   4.0/index
````

## File: doc/whatsnew/fragments/_template.rst
````
{% set title = "What's new in Pylint " + versiondata.version + "?" %}
{{ title }}
{{ underlines[0] * (title|length) }}
Release date: {{ versiondata.date }}

{% for section, _ in sections.items() %}
{% set underline = underlines[0] %}{% if section %}{{section}}
{{ underline * section|length }}{% set underline = underlines[1] %}

{% endif %}

{% if sections[section] %}
{% for category, val in definitions.items() if category in sections[section]%}
{{ definitions[category]['name'] }}
{{ underline * definitions[category]['name']|length }}

{% if definitions[category]['showcontent'] %}
{% for text, values in sections[section][category].items() %}
- {{ text }} ({{ values|join(', ') }})

{% endfor %}

{% else %}
- {{ sections[section][category]['']|join(', ') }}

{% endif %}
{% if sections[section][category]|length == 0 %}
No significant changes.

{% else %}
{% endif %}

{% endfor %}
{% else %}
No significant changes.


{% endif %}
{% endfor %}
````

## File: doc/whatsnew/full_changelog_explanation.rst
````
From pylint's beginning to pylint 2.14.0 included, we had a changelog that contained *all*
nontrivial changes to Pylint, including changes that were
not user facing, i.e. change that might interest you only if you're a developer
working on pylint or pylint plugins or an open-source historian.
````

## File: doc/whatsnew/index.rst
````
.. _whatsnew-index:

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   4/index
   3/index
   2/index
   1/index
   0/index
````

## File: doc/whatsnew/summary_explanation.rst
````
From pylint 1.6.0 to 2.14.0, on top of the full changelog there was also a summary
of (mostly user facing) changes.
````

## File: doc/contact.rst
````
Contact
=======

Bug reports, feedback
---------------------
.. _bug reports, feedback:

You think you have found a bug in Pylint? Well, this may be the case
since Pylint and Python are under heavy development!

Please take the time to check if it is already in the issue tracker at
https://github.com/pylint-dev/pylint

Note that the issue might also be reported in one of Pylint's major dependencies,
astroid:

* https://github.com/pylint-dev/astroid

Discord server
--------------

You can discuss your problem using the discord server:

https://discord.com/invite/Egy6P8AMB5

Mailing lists
-------------

.. _Mailing lists:

The code-quality mailing list is shared with other tools that aim
at improving the quality of python code.

You can subscribe to this mailing list at
https://mail.python.org/mailman3/lists/code-quality.python.org/

Archives are available at
https://mail.python.org/pipermail/code-quality/

Archives before April 2013 are not available anymore. At
https://mail.python.org/pipermail/ it was under ``python-projects``.

Support
-------

.. image:: media/Tidelift_Logos_RGB_Tidelift_Shorthand_On-White.png
   :height: 150
   :alt: Tidelift
   :align: left
   :class: tideliftlogo

Professional support for pylint is available as part of the `Tidelift
Subscription`_.  Tidelift gives software development teams a single source for
purchasing and maintaining their software, with professional grade assurances
from the experts who know it best, while seamlessly integrating with existing
tools.

.. _Tidelift Subscription: https://tidelift.com/subscription/pkg/pypi-pylint?utm_source=pypi-pylint&utm_medium=referral&utm_campaign=readme
````

## File: doc/faq.rst
````
.. _faq:

==========================
Frequently Asked Questions
==========================

How do I install Pylint?
------------------------

.. include:: short_text_installation.rst

How do I contribute to Pylint?
------------------------------

.. include:: short_text_contribute.rst


Does Pylint follow a versioning scheme?
----------------------------------------

See :ref:`upgrading pylint in the installation guide <upgrading_pylint>`.

How do I find the name corresponding to a specific command line option?
-----------------------------------------------------------------------

See :ref:`the configuration documentation <all-configurations-options>`.

What is the format of the configuration file?
---------------------------------------------

The configuration file can be an ``ini`` or ``toml`` file. See the :ref:`exhaustive list of possible options <all-options>`.

How to disable a particular message?
------------------------------------

Read :ref:`message-control` for details and examples.

Pylint gave my code a negative rating out of ten. That can't be right!
----------------------------------------------------------------------

Prior to Pylint 2.13.0, the score formula used by default had no lower
bound. The new default score formula is ::

    max(0, 0 if fatal else 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10))

If your project contains a configuration file created by an earlier version of
Pylint, you can set ``evaluation`` to the above expression to get the new
behavior. Likewise, since negative values are still technically supported,
``evaluation`` can be set to a version of the above expression that does not
enforce a floor of zero.

How do I avoid getting unused argument warnings for API I do not control?
-------------------------------------------------------------------------

Prefix (ui) the callback's name by `cb_` (callback), as in cb_onclick(...). By
doing so arguments usage won't be checked. Another solution is to
use one of the names defined in the "dummy-variables" configuration
variable for unused argument ("_" and "dummy" by default).


Why are there a bunch of messages disabled by default?
------------------------------------------------------

Either because they are prone to false positives or that they are opinionated enough
to not be included as default messages.

You can see the plugin you need to explicitly :ref:`load in the technical reference
<user_guide/checkers/extensions:optional checkers>`.

I want to run pylint on each keystroke in my IDE. How do I do that?
---------------------------------------------------------------------

Pylint full suite of checks will never be fast enough to run on every keystroke.
However, some IDEs can run pylint  when the IDE opens or saves files.
See, for example, the `Microsoft plugin for VS Code`_.


That said, pylint is best suited for linting on save for small projects, for continuous
integration jobs, or a git ``pre-push`` hook for big projects. The larger your repository
is, the slower pylint will be.

If you want to make pylint faster for this type of use case, you can use the ``--errors-only``
option, which will remove all the refactor, convention, and warning checks. You can also disable
checks with inherently high complexity that need to analyse the full code base like
``duplicate-code`` or ``cyclic-import`` (this list is not exhaustive).

.. _`Microsoft plugin for VS Code`: https://github.com/microsoft/vscode-pylint#readme

Why do I have non-deterministic results when I try to parallelize pylint ?
--------------------------------------------------------------------------

pylint should analyse all your code at once in order to best infer the
actual values that result from calls. If only some of the files are given, pylint might
miss a particular value's type and produce inferior inference for the subset. Parallelization
of pylint is not easy; we also discourage the use of the ``-j`` option if this matters to you.


Which messages should I disable to avoid duplicates if I use other popular linters ?
------------------------------------------------------------------------------------

pycodestyle_: bad-indentation, bare-except, line-too-long, missing-final-newline, multiple-statements, singleton-comparison, trailing-newlines, trailing-whitespace, unnecessary-negation, unnecessary-semicolon, wrong-import-position

pyflakes_: undefined-variable, unused-import, unused-variable

mccabe_: too-many-branches

pydocstyle_: missing-module-docstring, missing-class-docstring, missing-function-docstring

pep8-naming_: invalid-name, bad-classmethod-argument, bad-mcs-classmethod-argument, no-self-argument

isort_ and flake8-import-order_: ungrouped-imports, wrong-import-order

.. _`pycodestyle`: https://github.com/PyCQA/pycodestyle
.. _`pyflakes`: https://github.com/PyCQA/pyflakes
.. _`mccabe`: https://github.com/PyCQA/mccabe
.. _`pydocstyle`: https://github.com/PyCQA/pydocstyle
.. _`pep8-naming`: https://github.com/PyCQA/pep8-naming
.. _`isort`: https://github.com/pycqa/isort
.. _`flake8-import-order`: https://github.com/PyCQA/flake8-import-order

How do I avoid "access to undefined member" messages in my mixin classes?
-------------------------------------------------------------------------

You should add the ``no-member`` message to your ``ignored-checks-for-mixins`` option
and name your mixin class with a name which ends with "Mixin" or "mixin" (default)
or change the default value by changing the ``mixin-class-rgx`` option.

Where is the persistent data stored to compare between successive runs?
-----------------------------------------------------------------------

Analysis data are stored as a pickle file in a directory which is
localized using the following rules:

* value of the PYLINTHOME environment variable if set
* "pylint" subdirectory of the user's XDG_CACHE_HOME if the environment variable is set, otherwise
    - Linux: "~/.cache/pylint"
    - macOS: "~/Library/Caches/pylint"
    - Windows: "C:\Users\<username>\AppData\Local\pylint"
* ".pylint.d" directory in the current directory

How does the website pylint dot org relate to this project?
-----------------------------------------------------------

Historically, pylint dot org served as the primary website for Pylint. However,
we no longer have access to the domain. The current owners are monetizing
this by displaying advertisements alongside outdated documentation without
contributing to pylint at all. For the latest and official Pylint documentation,
please visit `pylint.readthedocs.io <https://pylint.readthedocs.io/en/stable/>`_.

Please see `issue 8934 <https://github.com/pylint-dev/pylint/issues/8934>`_
for more details.
````

## File: doc/index.rst
````
.. include:: ../README.rst

.. toctree::
   :titlesonly:
   :hidden:

   tutorial

.. toctree::
   :caption: User Guide
   :titlesonly:
   :hidden:

   user_guide/installation/index
   user_guide/usage/index
   user_guide/messages/index
   user_guide/configuration/index
   user_guide/checkers/index

.. toctree::
   :caption: Developer Guide
   :maxdepth: 2
   :titlesonly:
   :hidden:

   development_guide/api/index
   development_guide/how_tos/index.rst
   development_guide/technical_reference/index.rst
   development_guide/contributor_guide/index

.. toctree::
   :caption: Additional tools
   :maxdepth: 3
   :titlesonly:
   :hidden:

   additional_tools/pyreverse/index
   additional_tools/symilar/index

.. toctree::
   :caption: Changelog
   :titlesonly:
   :hidden:

   whatsnew/index.rst

.. toctree::
   :caption: Support
   :titlesonly:
   :hidden:

   faq
   contact
````

## File: doc/readthedoc_requirements.txt
````
-r requirements.txt
-e .
````

## File: doc/requirements.txt
````
Sphinx==8.2.3
sphinx-reredirects<1
towncrier~=24.8
furo==2025.7.19
````

## File: doc/short_text_contribute.rst
````
.. include:: ../README.rst
   :start-after: This is used inside the doc to recover the start of the short text for contribution
   :end-before: This is used inside the doc to recover the end of the short text for contribution
````

## File: doc/short_text_installation.rst
````
.. include:: ../README.rst
   :start-after: This is used inside the doc to recover the start of the short text for installation
   :end-before: This is used inside the doc to recover the end of the short text for installation
````

## File: doc/tutorial.rst
````
.. _tutorial:

========
Tutorial
========

This tutorial is all about approaching coding standards with little or no
knowledge of in-depth programming or the code standards themselves.  It's the
equivalent of skipping the manual and jumping right in.

The command line prompt for these examples is:

.. sourcecode:: console

  tutor Desktop$

.. _PEP 8: https://peps.python.org/pep-0008/

Getting Started
---------------

Running Pylint with the ``--help`` arguments will give you an idea of the arguments
available. Do that now, i.e.:

.. sourcecode:: console

  pylint --help


A couple of the options that we'll focus on here are: ::

  Commands:
    --help-msg=<msg-id>
    --generate-toml-config
  Messages control:
    --disable=<msg-ids>
  Reports:
    --reports=<y or n>
    --output-format=<format>

If you need more detail, you can also ask for an even longer help message: ::

  pylint --long-help

Pay attention to the last bit of this longer help output. This gives you a
hint of what Pylint is going to ``pick on``: ::

  Output:
     Using the default text output, the message format is :
    MESSAGE_TYPE: LINE_NUM:[OBJECT:] MESSAGE
    There are 5 kind of message types :
    * (C) convention, for programming standard violation
    * (R) refactor, for bad code smell
    * (W) warning, for python specific problems
    * (E) error, for probable bugs in the code
    * (F) fatal, if an error occurred which prevented pylint from doing
    further processing.

When Pylint is first run on a fresh piece of code, a common complaint is that it
is too ``noisy``.  The default configuration enforce a lot of warnings.
We'll use some of the options we noted above to make it suit your
preferences a bit better.

Your First Pylint'ing
---------------------

We'll use a basic Python script with `black`_ already applied on it,
as fodder for our tutorial. The starting code we will use is called
``simplecaesar.py`` and is here in its entirety:

.. _`black`: https://github.com/psf/black

.. sourcecode:: python

    #!/usr/bin/env python3

    import string

    shift = 3
    choice = input("would you like to encode or decode?")
    word = input("Please enter text")
    letters = string.ascii_letters + string.punctuation + string.digits
    encoded = ""
    if choice == "encode":
        for letter in word:
            if letter == " ":
                encoded = encoded + " "
            else:
                x = letters.index(letter) + shift
                encoded = encoded + letters[x]
    if choice == "decode":
        for letter in word:
            if letter == " ":
                encoded = encoded + " "
            else:
                x = letters.index(letter) - shift
                encoded = encoded + letters[x]

    print(encoded)


Let's get started. If we run this:

.. sourcecode:: console

    tutor Desktop$ pylint simplecaesar.py
    ************* Module simplecaesar
    simplecaesar.py:1:0: C0114: Missing module docstring (missing-module-docstring)
    simplecaesar.py:5:0: C0103: Constant name "shift" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:8:0: C0103: Constant name "letters" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:9:0: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:13:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:15:12: C0103: Constant name "x" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:16:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:20:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:22:12: C0103: Constant name "x" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:23:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)

    -----------------------------------
    Your code has been rated at 4.74/10


We can see the second line is: ::

  "simplecaesar.py:1:0: C0114: Missing module docstring (missing-module-docstring)"

This basically means that line 1 at column 0 violates the convention ``C0114``.
Another piece of information is the message symbol between parens,
``missing-module-docstring``.

If we want to read up a bit more about that, we can go back to the
command line and try this:

.. sourcecode:: console

  tutor Desktop$ pylint --help-msg=missing-module-docstring
  :missing-module-docstring (C0114): *Missing module docstring*
    Used when a module has no docstring.Empty modules do not require a docstring.
    This message belongs to the basic checker.

That one was a bit of a no-brainer, but we can also run into error messages
where we are unfamiliar with the underlying code theory.

The Next Step
-------------

Now that we got some configuration stuff out of the way, let's see what we can
do with the remaining warnings. If we add a docstring to describe what the code
is meant to do that will help. There are ``invalid-name`` messages that we will
get to later. Here is the updated code:

.. sourcecode:: python

    #!/usr/bin/env python3

    """This script prompts a user to enter a message to encode or decode
    using a classic Caesar shift substitution (3 letter shift)"""

    import string

    shift = 3
    choice = input("would you like to encode or decode?")
    word = input("Please enter text")
    letters = string.ascii_letters + string.punctuation + string.digits
    encoded = ""
    if choice == "encode":
        for letter in word:
            if letter == " ":
                encoded = encoded + " "
            else:
                x = letters.index(letter) + shift
                encoded = encoded + letters[x]
    if choice == "decode":
        for letter in word:
            if letter == " ":
                encoded = encoded + " "
            else:
                x = letters.index(letter) - shift
                encoded = encoded + letters[x]

    print(encoded)

Here is what happens when we run it:

.. sourcecode:: console

    tutor Desktop$ pylint simplecaesar.py
    ************* Module simplecaesar
    simplecaesar.py:8:0: C0103: Constant name "shift" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:11:0: C0103: Constant name "letters" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:12:0: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:16:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:18:12: C0103: Constant name "x" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:19:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:23:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:25:12: C0103: Constant name "x" doesn't conform to UPPER_CASE naming style (invalid-name)
    simplecaesar.py:26:12: C0103: Constant name "encoded" doesn't conform to UPPER_CASE naming style (invalid-name)

    ------------------------------------------------------------------
    Your code has been rated at 5.26/10 (previous run: 4.74/10, +0.53)

Nice! Pylint told us how much our code rating has improved since our last run,
and we're down to just the ``invalid-name`` messages.

There are fairly well defined conventions around naming things like instance
variables, functions, classes, etc.  The conventions focus on the use of
UPPERCASE and lowercase as well as the characters that separate multiple words
in the name.  This lends itself well to checking via a regular expression, thus
the **should match (([A-Z\_][A-Z1-9\_]*)|(__.*__))$**.

In this case Pylint is telling us that those variables appear to be constants
and should be all UPPERCASE. This is an in-house convention that has lived with Pylint
since its inception. You too can create your own in-house naming
conventions but for the purpose of this tutorial, we want to stick to the `PEP 8`_
standard. In this case, the variables we declared should follow the convention
of all lowercase.  The appropriate rule would be something like:
"should match [a-z\_][a-z0-9\_]{2,30}$".  Notice the lowercase letters in the
regular expression (a-z versus A-Z).

If we run that rule using a ``--const-rgx='[a-z\_][a-z0-9\_]{2,30}$'`` option, it
will now be quite quiet:

.. sourcecode:: console

    tutor Desktop$ pylint simplecaesar.py --const-rgx='[a-z\_][a-z0-9\_]{2,30}$'
    ************* Module simplecaesar
    simplecaesar.py:18:12: C0103: Constant name "x" doesn't conform to '[a-z\\_][a-z0-9\\_]{2,30}$' pattern (invalid-name)
    simplecaesar.py:25:12: C0103: Constant name "x" doesn't conform to '[a-z\\_][a-z0-9\\_]{2,30}$' pattern (invalid-name)

    ------------------------------------------------------------------
    Your code has been rated at 8.95/10 (previous run: 5.26/10, +3.68)

You can `read up`_ on regular expressions or use `a website to help you`_.

.. tip::
 It would really be a pain to specify that regex on the command line all the time, particularly if we're using many other options.
 That's what a configuration file is for. We can configure our Pylint to
 store our options for us so we don't have to declare them on the command line.  Using a configuration file is a nice way of formalizing your rules and
 quickly sharing them with others. Invoking ``pylint --generate-toml-config`` will create a sample ``.toml`` section with all the options set and explained in comments.
 This can then be added to your ``pyproject.toml`` file or any other ``.toml`` file pointed to with the ``--rcfile`` option.

.. _`read up`: https://docs.python.org/library/re.html
.. _`a website to help you`: https://regex101.com/
````
