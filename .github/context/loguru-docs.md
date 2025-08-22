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
- Only files matching these patterns are included: docs/**/*.{md,markdown,rmd,mdx,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  api/
    logger.rst
    type_hints_source.rst
    type_hints.rst
  project/
    changelog.rst
    contributing.rst
    license.rst
  resources/
    migration.rst
    recipes.rst
    troubleshooting.rst
  api.rst
  index.rst
  overview.rst
  project.rst
  resources.rst
```

# Files

## File: docs/api/logger.rst
```
``loguru.logger``
=================

.. automodule:: loguru._logger

.. autoclass:: loguru._logger.Logger()
   :members:
```

## File: docs/api/type_hints_source.rst
```
:orphan:

.. _type-hints-source:

Source Code of Type Hints
=========================

.. include:: ../../loguru/__init__.pyi
   :literal:
```

## File: docs/api/type_hints.rst
```
.. _type-hints:

Type Hints
==========

.. |str| replace:: :class:`str`
.. |namedtuple| replace:: :func:`namedtuple<collections.namedtuple>`
.. |dict| replace:: :class:`dict`

.. |Logger| replace:: :class:`~loguru._logger.Logger`
.. |catch| replace:: :meth:`~loguru._logger.Logger.catch()`
.. |contextualize| replace:: :meth:`~loguru._logger.Logger.contextualize()`
.. |complete| replace:: :meth:`~loguru._logger.Logger.complete()`
.. |bind| replace:: :meth:`~loguru._logger.Logger.bind()`
.. |patch| replace:: :meth:`~loguru._logger.Logger.patch()`
.. |opt| replace:: :meth:`~loguru._logger.Logger.opt()`
.. |level| replace:: :meth:`~loguru._logger.Logger.level()`

.. _stub file: https://www.python.org/dev/peps/pep-0484/#stub-files
.. _string literals: https://www.python.org/dev/peps/pep-0484/#forward-references
.. _postponed evaluation of annotations: https://www.python.org/dev/peps/pep-0563/
.. |future| replace:: ``__future__``
.. _future: https://www.python.org/dev/peps/pep-0563/#enabling-the-future-behavior-in-python-3-7
.. |loguru-mypy| replace:: ``loguru-mypy``
.. _loguru-mypy: https://github.com/kornicameister/loguru-mypy
.. |documentation of loguru-mypy| replace:: documentation of ``loguru-mypy``
.. _documentation of loguru-mypy:
    https://github.com/kornicameister/loguru-mypy/blob/master/README.md
.. _@kornicameister: https://github.com/kornicameister

Loguru relies on a `stub file`_ to document its types. This implies that these types are not
accessible during execution of your program, however they can be used by type checkers and IDE.
Also, this means that your Python interpreter has to support `postponed evaluation of annotations`_
to prevent error at runtime. This is achieved with a |future|_ import in Python 3.7+ or by using
`string literals`_ for earlier versions.

A basic usage example could look like this:

.. code-block:: python

    from __future__ import annotations

    import loguru
    from loguru import logger

    def good_sink(message: loguru.Message):
        print("My name is", message.record["name"])

    def bad_filter(record: loguru.Record):
        return record["invalid"]

    logger.add(good_sink, filter=bad_filter)


.. code-block::

    $ mypy test.py
    test.py:8: error: TypedDict "Record" has no key 'invalid'
    Found 1 error in 1 file (checked 1 source file)

There are several internal types to which you can be exposed using Loguru's public API, they are
listed here and might be useful to type hint your code:

- ``Logger``: the usual |logger| object (also returned by |opt|, |bind| and |patch|).
- ``Message``: the formatted logging message sent to the sinks (a |str| with ``record``
  attribute).
- ``Record``: the |dict| containing all contextual information of the logged message.
- ``Level``: the |namedtuple| returned by |level| (with ``name``, ``no``, ``color`` and ``icon``
  attributes).
- ``Catcher``: the context decorator returned by |catch|.
- ``Contextualizer``: the context decorator returned by |contextualize|.
- ``AwaitableCompleter``: the awaitable object returned by |complete|.
- ``RecordFile``: the ``record["file"]`` with ``name`` and ``path`` attributes.
- ``RecordLevel``: the ``record["level"]`` with ``name``, ``no`` and ``icon`` attributes.
- ``RecordThread``: the ``record["thread"]`` with ``id`` and ``name`` attributes.
- ``RecordProcess``: the ``record["process"]`` with ``id`` and ``name`` attributes.
- ``RecordException``: the ``record["exception"]`` with ``type``, ``value`` and ``traceback``
  attributes.

If that is not enough, one can also use the |loguru-mypy|_ library developed by `@kornicameister`_.
Plugin can be installed separately using::

    pip install loguru-mypy

It helps to catch several possible runtime errors by performing additional checks like:

- ``opt(lazy=True)`` loggers accepting only ``typing.Callable[[], typing.Any]`` arguments
- ``opt(record=True)`` loggers wrongly calling log handler like so ``logger.info(..., record={})``
- and even more...

For more details, go to official |documentation of loguru-mypy|_.


See also: :ref:`type-hints-source`.
```

## File: docs/project/changelog.rst
```
Changelog
#########

.. include:: ../../CHANGELOG.rst
```

## File: docs/project/contributing.rst
```
Contributing
############

.. include:: ../../CONTRIBUTING.rst
```

## File: docs/project/license.rst
```
License
#######

.. literalinclude:: ../../LICENSE
    :language: none
```

## File: docs/resources/migration.rst
```
Switching from Standard Logging to Loguru
=========================================

.. highlight:: python3

.. |getLogger| replace:: :func:`~logging.getLogger`
.. |addLevelName| replace:: :func:`~logging.addLevelName`
.. |getLevelName| replace:: :func:`~logging.getLevelName`
.. |Handler| replace:: :class:`~logging.Handler`
.. |Logger| replace:: :class:`~logging.Logger`
.. |Filter| replace:: :class:`~logging.Filter`
.. |Formatter| replace:: :class:`~logging.Formatter`
.. |LoggerAdapter| replace:: :class:`~logging.LoggerAdapter`
.. |LogRecord| replace:: :class:`~logging.LogRecord`
.. |logger.setLevel| replace:: :meth:`~logging.Logger.setLevel`
.. |logger.addFilter| replace:: :meth:`~logging.Logger.addFilter`
.. |makeRecord| replace:: :meth:`~logging.Logger.makeRecord`
.. |disable| replace:: :func:`~logging.disable`
.. |setLogRecordFactory| replace:: :func:`~logging.setLogRecordFactory`
.. |propagate| replace:: :attr:`~logging.Logger.propagate`
.. |addHandler| replace:: :meth:`~logging.Logger.addHandler`
.. |removeHandler| replace:: :meth:`~logging.Logger.removeHandler`
.. |handle| replace:: :meth:`~logging.Handler.handle`
.. |emit| replace:: :meth:`~logging.Handler.emit`
.. |handler.setLevel| replace:: :meth:`~logging.Handler.setLevel`
.. |handler.addFilter| replace:: :meth:`~logging.Handler.addFilter`
.. |setFormatter| replace:: :meth:`~logging.Handler.setFormatter`
.. |createLock| replace:: :meth:`~logging.Handler.createLock`
.. |acquire| replace:: :meth:`~logging.Handler.acquire`
.. |release| replace:: :meth:`~logging.Handler.release`
.. |isEnabledFor| replace:: :meth:`~logging.Logger.isEnabledFor`
.. |dictConfig| replace:: :func:`~logging.config.dictConfig`
.. |basicConfig| replace:: :func:`~logging.basicConfig`
.. |captureWarnings| replace:: :func:`~logging.captureWarnings`
.. |assertLogs| replace:: :meth:`~unittest.TestCase.assertLogs`
.. |unittest| replace:: :mod:`unittest`
.. |warnings| replace:: :mod:`warnings`
.. |warnings.showwarning| replace:: :func:`warnings.showwarning`

.. |add| replace:: :meth:`~loguru._logger.Logger.add()`
.. |remove| replace:: :meth:`~loguru._logger.Logger.remove()`
.. |bind| replace:: :meth:`~loguru._logger.Logger.bind`
.. |patch| replace:: :meth:`~loguru._logger.Logger.patch`
.. |opt| replace:: :meth:`~loguru._logger.Logger.opt()`
.. |level| replace:: :meth:`~loguru._logger.Logger.level()`
.. |configure| replace:: :meth:`~loguru._logger.Logger.configure()`

.. |pytest| replace:: ``pytest``
.. _pytest: https://docs.pytest.org/en/latest/
.. |caplog| replace:: ``caplog``
.. _caplog: https://docs.pytest.org/en/latest/logging.html?highlight=caplog#caplog-fixture
.. |pytest-loguru| replace:: ``pytest-loguru``
.. _pytest-loguru: https://github.com/mcarans/pytest-loguru

.. _@mcarans: https://github.com/mcarans

.. _`GH#59`: https://github.com/Delgan/loguru/issues/59
.. _`GH#474`: https://github.com/Delgan/loguru/issues/474


Introduction to logging in Python
---------------------------------

First and foremost, it is important to understand some basic concepts about logging in Python.

Logging is an essential part of any application, as it allows you to track the behavior of your code and diagnose issues. It associates messages with severity levels which are collected and dispatched to readable outputs called handlers.

For newcomers, take a look at the tutorial in the Python documentation: `Logging HOWTO <https://docs.python.org/3/howto/logging.html>`_.


Fundamental differences between ``logging`` and ``loguru``
----------------------------------------------------------

Although ``loguru`` is written "from scratch" and does not rely on standard ``logging`` internally, both libraries serve the same purpose: provide functionalities to implement a flexible event logging system. The main difference is that standard ``logging`` requires the user to explicitly instantiate named ``Logger`` and configure them with ``Handler``, ``Formatter`` and ``Filter``, while ``loguru`` tries to narrow down the amount of configuration steps.

Apart from that, usage is globally the same, once the ``logger`` object is created or imported you can start using it to log messages with the appropriate severity (``logger.debug("Dev message")``, ``logger.warning("Danger!")``, etc.), messages which are then sent to the configured handlers.

As for standard logging, default logs are sent to ``sys.stderr`` rather than ``sys.stdout``. The POSIX standard specifies that  ``stderr`` is the correct stream for "diagnostic output". The main compelling case in favor or logging to ``stderr`` is that it avoids mixing the actual output of the application with debug information. Consider for example pipe-redirection like ``python my_app.py | other_app`` which would not be possible if logs were emitted to ``stdout``. Another major benefit is that Python resolves encoding issues on ``sys.stderr`` by escaping faulty characters (``"backslashreplace"`` policy) while it raises an ``UnicodeEncodeError`` (``"strict"`` policy) on ``sys.stdout``.


Replacing ``getLogger()`` function
----------------------------------

It is usual to call |getLogger| at the beginning of each file to retrieve and use a logger across your module, like this: ``logger = logging.getLogger(__name__)``.

Using Loguru, there is no need to explicitly get and name a logger, ``from loguru import logger`` suffices. Each time this imported logger is used, a :ref:`record <record>` is created and will automatically contain the contextual ``__name__`` value.

As for standard logging, the ``name`` attribute can then be used to format and filter your logs.


Replacing ``Logger`` objects
----------------------------

Loguru replaces the standard |Logger| configuration by a proper :ref:`sink <sink>` definition. Instead of configuring a logger, you should |add| and parametrize your handlers. The |logger.setLevel| and |logger.addFilter| are suppressed by the configured sink ``level`` and ``filter`` parameters. The |propagate| attribute and |disable| function can be replaced by the ``filter`` option too. The |makeRecord| method can be replaced using the ``record["extra"]`` dict.

Sometimes, more fine-grained control is required over a particular logger. In such case, Loguru provides the |bind| method which can be in particular used to generate a specifically named logger.

For example, by calling ``other_logger = logger.bind(name="other")``, each :ref:`message <message>` logged using ``other_logger`` will populate the ``record["extra"]`` dict with the ``name`` value, while using ``logger`` won't. This permits differentiating logs from ``logger`` or ``other_logger`` from within your sink or filter function.

Let suppose you want a sink to log only some very specific messages::

    def specific_only(record):
        return "specific" in record["extra"]

    logger.add("specific.log", filter=specific_only)

    specific_logger = logger.bind(specific=True)

    logger.info("General message")          # This is filtered-out by the specific sink
    specific_logger.info("Module message")  # This is accepted by the specific sink (and others)

Another example, if you want to attach one sink to one named logger::

    # Only write messages from "a" logger
    logger.add("a.log", filter=lambda record: record["extra"].get("name") == "a")
    # Only write messages from "b" logger
    logger.add("b.log", filter=lambda record: record["extra"].get("name") == "b")

    logger_a = logger.bind(name="a")
    logger_b = logger.bind(name="b")

    logger_a.info("Message A")
    logger_b.info("Message B")


Replacing ``Handler``, ``Filter`` and ``Formatter`` objects
-----------------------------------------------------------

Standard ``logging`` requires you to create an |Handler| object and then call |addHandler|. Using Loguru, the handlers are started using |add|. The sink defines how the handler should manage incoming logging messages, as would do |handle| or |emit|. To log from multiple modules, you just have to import the logger, all messages will be dispatched to the added handlers.

While calling |add|, the ``level`` parameter replaces |handler.setLevel|, the ``format`` parameter replaces |setFormatter|, the ``filter`` parameter replaces |handler.addFilter|. The thread-safety is managed automatically by Loguru, so there is no need for |createLock|, |acquire| nor |release|. The equivalent method of |removeHandler| is |remove| which should be used with the identifier returned by |add|.

Note that you don't necessarily need to replace your |Handler| objects because |add| accepts them as valid sinks.

In short, you can replace::

    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler("spam.log")
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

With::

    fmt = "{time} - {name} - {level} - {message}"
    logger.add("spam.log", level="DEBUG", format=fmt)
    logger.add(sys.stderr, level="ERROR", format=fmt)


Replacing ``LogRecord`` objects
-------------------------------

In Loguru, the equivalence of a |LogRecord| instance is a simple ``dict`` which stores the details of a logged message. To find the correspondence with |LogRecord| attributes, please refer to :ref:`the "record dict" documentation <record>` which lists all available keys.

This ``dict`` is attached to each :ref:`logged message <message>` through a special ``record`` attribute of the ``str``-like object received by sinks. For example::

    def simple_sink(message):
        # A simple sink can use "message" as a basic string and ignore the "record" attribute.
        print(message, end="")

    def advanced_sink(message):
        # An advanced sink can use the "record" attribute to access contextual information.
        record = message.record

        if record["level"].no >= 50:
            file_path = record["file"].path
            print(f"Critical error in {file_path}", end="", file=sys.stderr)
        else:
            print(message, end="")

    logger.add(simple_sink)
    logger.add(advanced_sink)


As explained in the previous sections, the record dict is also available during invocation of filtering and formatting functions.

If you need to extend the record dict with custom information similarly to what was possible with |setLogRecordFactory|, you can simply use the |patch| method to add the desired keys to the ``record["extra"]`` dict.


Replacing ``%`` style formatting of messages
--------------------------------------------

Loguru only supports ``{}``-style formatting.

You have to replace ``logger.debug("Some variable: %s", var)`` with ``logger.debug("Some variable: {}", var)``. All ``*args`` and ``**kwargs`` passed to a logging function are used to call ``message.format(*args, **kwargs)``. Arguments which do not appear in the message string are simply ignored. Note that passing arguments to logging functions like this may be useful to (slightly) improve performances: it avoids formatting the message if the level is too low to pass any configured handler.

For converting the general format used by |Formatter|, refer to :ref:`list of available record tokens <record>`.

For converting the date format used by ``datefmt``, refer to :ref:`list of available date tokens<time>`.


Replacing ``exc_info`` argument
-------------------------------

While calling standard logging function, you can pass ``exc_info`` as an argument to add stacktrace to the message. Instead of that, you should use the |opt| method with ``exception`` parameter, replacing ``logger.debug("Debug error:", exc_info=True)`` with ``logger.opt(exception=True).debug("Debug error:")``.

The formatted exception will include the whole stacktrace and variables. To prevent that, make sure to use ``backtrace=False`` and ``diagnose=False`` while adding your sink.


Replacing ``extra`` argument and ``LoggerAdapter`` objects
----------------------------------------------------------

To pass contextual information to log messages, replace ``extra`` by inlining |bind| method::

    context = {"clientip": "192.168.0.1", "user": "fbloggs"}

    logger.info("Protocol problem", extra=context)   # Standard logging
    logger.bind(**context).info("Protocol problem")  # Loguru

This will add context information to the ``record["extra"]`` dict of your logged message, so make sure to configure your handler format adequately::

    fmt = "%(asctime)s %(clientip)s %(user)s %(message)s"     # Standard logging
    fmt = "{time} {extra[clientip]} {extra[user]} {message}"  # Loguru

You can also replace |LoggerAdapter| by calling ``logger = logger.bind(clientip="192.168.0.1")`` before using it, or by assigning the bound logger to a class instance::

    class MyClass:

        def __init__(self, clientip):
            self.logger = logger.bind(clientip=clientip)

        def func(self):
            self.logger.debug("Running func")


Replacing ``isEnabledFor()`` method
-----------------------------------

If you wish to log useful information for your debug logs, but don't want to pay the performance penalty in release mode while no debug handler is configured, standard logging provides the |isEnabledFor| method::

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Message data: %s", expensive_func())

You can replace this with the |opt| method and ``lazy`` option::

    # Arguments should be functions which will be called if needed
    logger.opt(lazy=True).debug("Message data: {}", expensive_func)


Replacing ``addLevelName()`` and ``getLevelName()`` functions
-------------------------------------------------------------

To add a new custom level, you can replace |addLevelName| with the |level| function::

    logging.addLevelName(33, "CUSTOM")                       # Standard logging
    logger.level("CUSTOM", no=45, color="<red>", icon="🚨")  # Loguru

The same function can be used to replace |getLevelName|::

    logger.getLevelName(33)  # => "CUSTOM"
    logger.level("CUSTOM")   # => (name='CUSTOM', no=33, color="<red>", icon="🚨")

Note that contrary to standard logging, Loguru doesn't associate severity number to any level, levels are only identified by their name.


Replacing ``basicConfig()`` and ``dictConfig()`` functions
----------------------------------------------------------

The |basicConfig| and |dictConfig| functions are replaced by the |configure| method.

This does not accept ``config.ini`` files, though, so you have to handle that yourself using your favorite format.


Replacing ``captureWarnings()`` function
----------------------------------------

The |captureWarnings| function which redirects alerts from the |warnings| module to the logging system can be implemented by simply replacing |warnings.showwarning| function as follow::

    import warnings
    from loguru import logger

    showwarning_ = warnings.showwarning

    def showwarning(message, *args, **kwargs):
        logger.warning(message)
        showwarning_(message, *args, **kwargs)

    warnings.showwarning = showwarning


.. _migration-assert-logs:

Replacing ``assertLogs()`` method from ``unittest`` library
-----------------------------------------------------------

The |assertLogs| method defined in the |unittest| from standard library is used to capture and test logged messages. However, it can't be made compatible with Loguru. It needs to be replaced with a custom context manager possibly implemented as follows::

    from contextlib import contextmanager

    @contextmanager
    def capture_logs(level="INFO", format="{level}:{name}:{message}"):
        """Capture loguru-based logs."""
        output = []
        handler_id = logger.add(output.append, level=level, format=format)
        yield output
        logger.remove(handler_id)

It provides the list of :ref:`logged messages <message>` for each of which you can access :ref:`the record attribute<record>`. Here is a usage example::

    def do_something(val):
        if val < 0:
            logger.error("Invalid value")
            return 0
        return val * 2


    class TestDoSomething(unittest.TestCase):
        def test_do_something_good(self):
            with capture_logs() as output:
                do_something(1)
            self.assertEqual(output, [])

        def test_do_something_bad(self):
            with capture_logs() as output:
                do_something(-1)
            self.assertEqual(len(output), 1)
            message = output[0]
            self.assertIn("Invalid value", message)
            self.assertEqual(message.record["level"].name, "ERROR")

.. seealso::

   See :ref:`testing logging <recipes-testing>` for more information.


.. _migration-caplog:

Replacing ``caplog`` fixture from ``pytest`` library
----------------------------------------------------

|pytest|_ is a very common testing framework. The |caplog|_ fixture captures logging output so that it can be tested against. For example::

    from loguru import logger

    def some_func(a, b):
        if a < 0:
            logger.warning("Oh no!")
        return a + b

    def test_some_func(caplog):
        assert some_func(-1, 3) == 2
        assert "Oh no!" in caplog.text

If you've followed all the migration guidelines thus far, you'll notice that this test will fail. This is because |pytest|_ links to the standard library's ``logging`` module.

So to fix things, we need to add a sink that propagates Loguru to the caplog handler.
This is done by overriding the |caplog|_ fixture to capture its handler. In your ``conftest.py`` file, add the following::

    import pytest
    from loguru import logger
    from _pytest.logging import LogCaptureFixture

    @pytest.fixture
    def caplog(caplog: LogCaptureFixture):
        handler_id = logger.add(
            caplog.handler,
            format="{message}",
            level=0,
            filter=lambda record: record["level"].no >= caplog.handler.level,
            enqueue=False,  # Set to 'True' if your test is spawning child processes.
        )
        yield caplog
        logger.remove(handler_id)

Run your tests and things should all be working as expected. Additional information can be found in `GH#59`_ and `GH#474`_. You can also install and use the |pytest-loguru|_ package created by `@mcarans`_.

Note that if you want Loguru logs to be propagated to Pytest terminal reporter, you can do so by overriding the ``reportlog`` fixture as follows::

    import pytest
    from loguru import logger

    @pytest.fixture
    def reportlog(pytestconfig):
        logging_plugin = pytestconfig.pluginmanager.getplugin("logging-plugin")
        handler_id = logger.add(logging_plugin.report_handler, format="{message}")
        yield
        logger.remove(handler_id)

Finally, when dealing with the ``--log-cli-level`` command-line flag, remember that this option controls the standard ``logging`` logs, not ``loguru`` ones. For this reason, you must first install a ``PropagateHandler`` for compatibility::

    @pytest.fixture(autouse=True)
    def propagate_logs():

        class PropagateHandler(logging.Handler):
            def emit(self, record):
                if logging.getLogger(record.name).isEnabledFor(record.levelno):
                    logging.getLogger(record.name).handle(record)

        logger.remove()
        logger.add(PropagateHandler(), format="{message}")
        yield

.. seealso::

   See :ref:`testing logging <recipes-testing>` for more information.
```

## File: docs/resources/recipes.rst
```
Code Snippets and Recipes for Loguru
====================================

.. highlight:: python3

.. |print| replace:: :func:`print()`
.. |open| replace:: :func:`open()`
.. |sys.__stdout__| replace:: :data:`sys.__stdout__`
.. |sys.stdout| replace:: :data:`sys.stdout`
.. |sys.stderr| replace:: :data:`sys.stderr`
.. |warnings| replace:: :mod:`warnings`
.. |warnings.showwarning| replace:: :func:`warnings.showwarning`
.. |warnings.warn| replace:: :func:`warnings.warn`
.. |contextlib.redirect_stdout| replace:: :func:`contextlib.redirect_stdout`
.. |copy.deepcopy| replace:: :func:`copy.deepcopy`
.. |os.fork| replace:: :func:`os.fork`
.. |os.umask| replace:: :func:`os.umask`
.. |multiprocessing| replace:: :mod:`multiprocessing`
.. |pickle| replace:: :mod:`pickle`
.. |traceback| replace:: :mod:`traceback`
.. |Thread| replace:: :class:`~threading.Thread`
.. |Process| replace:: :class:`~multiprocessing.Process`
.. |Pool| replace:: :class:`~multiprocessing.pool.Pool`
.. |Pool.map| replace:: :meth:`~multiprocessing.pool.Pool.map`
.. |Pool.apply| replace:: :meth:`~multiprocessing.pool.Pool.apply`
.. |sys.stdout.reconfigure| replace:: :meth:`sys.stdout.reconfigure() <io.TextIOWrapper.reconfigure>`
.. |UnicodeEncodeError| replace:: :exc:`UnicodeEncodeError`

.. |add| replace:: :meth:`~loguru._logger.Logger.add()`
.. |remove| replace:: :meth:`~loguru._logger.Logger.remove()`
.. |enable| replace:: :meth:`~loguru._logger.Logger.enable()`
.. |disable| replace:: :meth:`~loguru._logger.Logger.disable()`
.. |bind| replace:: :meth:`~loguru._logger.Logger.bind()`
.. |patch| replace:: :meth:`~loguru._logger.Logger.patch()`
.. |opt| replace:: :meth:`~loguru._logger.Logger.opt()`
.. |log| replace:: :meth:`~loguru._logger.Logger.log()`
.. |level| replace:: :meth:`~loguru._logger.Logger.level()`
.. |configure| replace:: :meth:`~loguru._logger.Logger.configure()`
.. |complete| replace:: :meth:`~loguru._logger.Logger.complete()`

.. _`unicode`: https://docs.python.org/3/howto/unicode.html

.. |if-name-equals-main| replace:: ``if __name__ == "__main__":``
.. _if-name-equals-main: https://docs.python.org/3/library/__main__.html#idiomatic-usage

.. |logot| replace:: ``logot``
.. _logot: https://logot.readthedocs.io/

.. |pytest| replace:: ``pytest``
.. _pytest: https://docs.pytest.org/en/latest/

.. |stackprinter| replace:: ``stackprinter``
.. _stackprinter: https://github.com/cknd/stackprinter

.. |zmq| replace:: ``zmq``
.. _zmq: https://github.com/zeromq/pyzmq

.. _`GH#132`: https://github.com/Delgan/loguru/issues/132


Security considerations when using Loguru
-----------------------------------------

Firstly, if you use |pickle| to load log messages (e.g. from the network), make sure the source is trustable or sign the data to verify its authenticity before deserializing it. If you do not take these precautions, malicious code could be executed by an attacker. You can read more details in this article: `What’s so dangerous about pickles? <https://intoli.com/blog/dangerous-pickles/>`_

.. code::

    import hashlib
    import hmac
    import pickle

    def client(connection):
        data = pickle.dumps("Log message")
        digest =  hmac.digest(b"secret-shared-key", data, hashlib.sha1)
        connection.send(digest + b" " + data)

    def server(connection):
        expected_digest, data = connection.read().split(b" ", 1)
        data_digest = hmac.digest(b"secret-shared-key", data, hashlib.sha1)
        if not hmac.compare_digest(data_digest, expected_digest):
            print("Integrity error")
        else:
            message = pickle.loads(data)
            logger.info(message)


You should also avoid logging a message that could be maliciously hand-crafted by an attacker. Calling ``logger.debug(message, value)`` is roughly equivalent to calling ``print(message.format(value))`` and the same safety rules apply. In particular, an attacker could force printing of assumed hidden variables of your application. Here is an article explaining the possible vulnerability: `Be Careful with Python's New-Style String Format <https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/>`_.

.. code::

    SECRET_KEY = 'Y0UC4NTS33Th1S!'

    class SomeValue:
        def __init__(self, value):
            self.value = value

    # If user types "{value.__init__.__globals__[SECRET_KEY]}" then the secret key is displayed.
    message = "[Custom message] " + input()
    logger.info(message, value=SomeValue(10))


Another danger due to external input is the possibility of a log injection attack. Consider that you may need to escape user values before logging them: `Is your Python code vulnerable to log injection? <https://dev.arie.bovenberg.net/blog/is-your-python-code-vulnerable-to-log-injection/>`_

.. code::

    logger.add("file.log", format="{level} {message}")

    # If value is "Josh logged in.\nINFO User James" then there will appear to be two log entries.
    username = external_data()
    logger.info("User " + username + " logged in.")


Note that by default, Loguru will display the value of existing variables when an ``Exception`` is logged. This is very useful for debugging but could lead to credentials appearing in log files. Make sure to turn it off in production (or set the ``LOGURU_DIAGNOSE=NO`` environment variable).

.. code::

    logger.add("out.log", diagnose=False)


Another thing you should consider is to change the access permissions of your log file. Loguru creates files using the built-in |open| function, which means by default they might be read by a different user than the owner. If this is not desirable, be sure to modify the default access rights.

.. code::

    def opener(file, flags):
        return os.open(file, flags, 0o600)

    logger.add("combined.log", opener=opener)


Avoiding logs to be printed twice on the terminal
-------------------------------------------------

The logger is pre-configured for convenience with a default handler which writes messages to |sys.stderr|. You should |remove| it first if you plan to |add| another handler logging messages to the console, otherwise you may end up with duplicated logs.

.. code::

    logger.remove()  # Remove all handlers added so far, including the default one.
    logger.add(sys.stderr, level="WARNING")


.. _changing-level-of-existing-handler:

Changing the level of an existing handler
-----------------------------------------

Once a handler has been added, it is actually not possible to update it. This is a deliberate choice in order to keep the Loguru's API minimal. Several solutions are possible, though, if you need to change the configured ``level`` of a handler. Chose the one that best fits your use case.

The most straightforward workaround is to |remove| your handler and then re-|add| it with the updated ``level`` parameter. To do so, you have to keep a reference to the identifier number returned while adding a handler::

    handler_id = logger.add(sys.stderr, level="WARNING")

    logger.info("Logging 'WARNING' or higher messages only")

    ...

    logger.remove(handler_id)  # For the default handler, it's actually '0'.
    logger.add(sys.stderr, level="DEBUG")

    logger.debug("Logging 'DEBUG' messages too")


Alternatively, you can combine the |bind| method with the ``filter`` argument to provide a function dynamically filtering logs based on their level::

    def my_filter(record):
        if record["extra"].get("warn_only"):  # "warn_only" is bound to the logger and set to 'True'
            return record["level"].no >= logger.level("WARNING").no
        return True  # Fallback to default 'level' configured while adding the handler


    logger.add(sys.stderr, filter=my_filter, level="DEBUG")

    # Use this logger first, debug messages are filtered out
    logger = logger.bind(warn_only=True)
    logger.warn("Initialization in progress")

    # Then you can use this one to log all messages
    logger = logger.bind(warn_only=False)
    logger.debug("Back to debug messages")


Finally, more advanced control over handler's level can be achieved by using a callable object as the ``filter``::

    min_level = logger.level("DEBUG").no

    def filter_by_level(record):
        return record["level"].no >= min_level


    logger.remove()
    logger.add(sys.stderr, filter=filter_by_level, level=0)

    logger.debug("Logged")

    min_level = logger.level("WARNING").no

    logger.debug("Not logged")


.. _configuring-loguru-as-lib-or-app:

Configuring Loguru to be used by a library or an application
------------------------------------------------------------

A clear distinction must be made between the use of Loguru within a library or an application.

In case of an application, you can add handlers from anywhere in your code. It's advised though to configure the logger from within a |if-name-equals-main|_ block inside the entry file of your script.

However, if your work is intended to be used as a library, you usually should not add any handler. This is user responsibility to configure logging according to its preferences, and it's better not to interfere with that. Indeed, since Loguru is based on a single common logger, handlers added by a library will also receive user logs, which is generally not desirable.

By default, a third-library should not emit logs except if specifically requested. For this reason, there exist the |disable| and |enable| methods. Make sure to first call ``logger.disable("mylib")``. This avoids library logs to be mixed with those of the user. The user can always call ``logger.enable("mylib")`` if he wants to access the logs of your library.

If you would like to ease logging configuration for your library users, it is advised to provide a function like ``configure_logger()`` in charge of adding the desired handlers. This will allow the user to activate the logging only if he needs to.

To summarize, let's look at this hypothetical package (none of the listed files are required, it all depends on how you plan your project to be used):

.. code:: text

    mypackage
    ├── __init__.py
    ├── __main__.py
    ├── main.py
    └── mymodule.py

Files relate to Loguru as follows:

* File ``__init__.py``:

    * It is the entry point when your project is used as a library (``import mypackage``).
    * It should contain ``logger.disable("mypackage")`` unconditionally at the top level.
    * It should not call ``logger.add()`` as it modifies handlers configuration.

* File ``__main__.py``:

    * It is the entry point when your project is used as an application (``python -m mypackage``).
    * It can contain logging configuration unconditionally at the top level.

* File ``main.py``:

    * It is the entry point when your project is used as a script (``python mypackage/main.py``).
    * It can contain logging configuration inside an ``if __name__ == "__main__":`` block.

* File ``mymodule.py``:

    * It is an internal module used by your project.
    * It can use the ``logger`` simply by importing it.
    * It does not need to configure anything.


.. _inter-process-communication:

Transmitting log messages across network, processes or Gunicorn workers
-----------------------------------------------------------------------

It is possible to send and receive logs between different processes and even between different computers if needed. Once the connection is established between the two Python programs, this requires serializing the logging record in one side while re-constructing the message on the other hand. Keep in mind though that `pickling is unsafe <https://intoli.com/blog/dangerous-pickles/>`_, you should use this with care.

The first thing you will need is to run a server responsible for receiving log messages emitted by other processes::

    # server.py
    import socketserver
    import pickle
    import struct
    import sys
    from loguru import logger


    class LoggingRequestHandler(socketserver.StreamRequestHandler):

        def handle(self):
            while True:
                chunk = self.connection.recv(4)
                if len(chunk) < 4:
                    break
                slen = struct.unpack(">L", chunk)[0]
                chunk = self.connection.recv(slen)
                while len(chunk) < slen:
                    chunk = chunk + self.connection.recv(slen - len(chunk))
                record = pickle.loads(chunk)
                level, message = record["level"].name, record["message"]
                logger.patch(lambda r, record=record: r.update(record)).log(level, message)


    if __name__ == "__main__":
        # Configure the logger with desired handlers.
        logger.configure(handlers=[{"sink": "server.log"}, {"sink": sys.stderr}])

        # Setup the server to receive log messages from other processes.
        with socketserver.TCPServer(("localhost", 9999), LoggingRequestHandler) as server:
            server.serve_forever()


Then, you need your clients to send messages using a specific handler::

    # client.py
    import socket
    import struct
    import time
    import pickle
    from loguru import logger


    class SocketHandler:

        def __init__(self, host, port):
            self._host = host
            self._port = port

        def write(self, message):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self._host, self._port))
            record = message.record
            data = pickle.dumps(record)
            slen = struct.pack(">L", len(data))
            sock.send(slen + data)


    if __name__ == "__main__":
        # Setup the handler sending log messages to the server.
        logger.configure(handlers=[{"sink": SocketHandler('localhost', 9999)}])

        # Proceed with standard logger usage.
        logger.info("Sending message from the client")


Make sure that the server is running while the clients are logging messages, and note that they must communicate on the same port.

Another example, when using Gunicorn and FastAPI you should add the previously defined ``SocketHandler`` to each of the running workers, possibly like so::

    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from loguru import logger

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Setup the server instance (executed once for each worker)."""
        logger.configure(handlers=[{"sink": SocketHandler("localhost", 9999)}])
        logger.debug("Worker is initializing")
        yield

    app = FastAPI(lifespan=lifespan)

When sharing the logger between processes is not technically possible, using a server handling TCP requests is the most reliable way of guaranteeing the integrity of logged messages.


Using ZMQ to send and receive log messages
------------------------------------------

Third-party libraries like |zmq|_ can be leveraged to exchange messages between multiple processes. Here is an example of a basic server and client:

.. code::

    # client.py
    import zmq
    from zmq.log.handlers import PUBHandler
    from logging import Formatter
    from loguru import logger

    socket = zmq.Context().socket(zmq.PUB)
    socket.connect("tcp://127.0.0.1:12345")
    handler = PUBHandler(socket)
    handler.setFormatter(Formatter("%(message)s"))
    logger.add(handler)

    logger.info("Logging from client")


.. code::

    # server.py
    import sys
    import zmq
    from loguru import logger

    socket = zmq.Context().socket(zmq.SUB)
    socket.bind("tcp://127.0.0.1:12345")
    socket.subscribe("")

    logger.configure(handlers=[{"sink": sys.stderr, "format": "{message}"}])

    while True:
        _, message = socket.recv_multipart()
        logger.info(message.decode("utf8").strip())



Resolving ``UnicodeEncodeError`` and other encoding issues
----------------------------------------------------------

When you write a log message, the handler may need to encode the received `unicode`_ string to a specific sequence of bytes. The ``encoding`` used to perform this operation varies depending on the sink type and your environment. Problem may occur if you try to write a character which is not supported by the handler ``encoding``. In such case, it's likely that Python will raise an |UnicodeEncodeError|.

For example, this may happen while printing to the terminal::

    print("天")
    # UnicodeEncodeError: 'charmap' codec can't encode character '\u5929' in position 0: character maps to <undefined>

A similar error may occur while writing to a file which has not been opened using an appropriate encoding. Most common problem happen while logging to standard output or to a file on Windows. So, how to avoid such error? Simply by properly configuring your handler so that it can process any kind of unicode string.

If you are encountering this error while logging to ``stdout``, you have several options:

* Use |sys.stderr| instead of |sys.stdout| (the former will escape faulty characters rather than raising exception)
* Set the :envvar:`PYTHONIOENCODING` environment variable to ``utf-8``
* Call |sys.stdout.reconfigure| with ``encoding='utf-8'`` and / or ``errors='backslashreplace'``

If you are using a file sink, you can configure the ``errors`` or ``encoding`` parameter while adding the handler like ``logger.add("file.log", encoding="utf8")`` for example.  All additional ``**kwargs`` argument are passed to the built-in |open| function.

For other types of handlers, you have to check if there is a way to parametrize encoding or fallback policy.


Logging entry and exit of functions with a decorator
----------------------------------------------------

In some cases, it might be useful to log entry and exit values of a function. Although Loguru doesn't provide such feature out of the box, it can be easily implemented by using Python decorators::

    import functools
    from loguru import logger


    def logger_wraps(*, entry=True, exit=True, level="DEBUG"):

        def wrapper(func):
            name = func.__name__

            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                logger_ = logger.opt(depth=1)
                if entry:
                    logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
                result = func(*args, **kwargs)
                if exit:
                    logger_.log(level, "Exiting '{}' (result={})", name, result)
                return result

            return wrapped

        return wrapper

You could then use it like this::

    @logger_wraps()
    def foo(a, b, c):
        logger.info("Inside the function")
        return a * b * c

    def bar():
        foo(2, 4, c=8)

    bar()


Which would result in:

.. code-block:: none

    2019-04-07 11:08:44.198 | DEBUG    | __main__:bar:30 - Entering 'foo' (args=(2, 4), kwargs={'c': 8})
    2019-04-07 11:08:44.198 | INFO     | __main__:foo:26 - Inside the function
    2019-04-07 11:08:44.198 | DEBUG    | __main__:bar:30 - Exiting 'foo' (result=64)


Here is another simple example to record timing of a function::

    def timeit(func):

        def wrapped(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
            return result

        return wrapped

Finally, here is an example of a generic wrapper that combines a success message with error handling during function execution::

    def with_logging(func):
        @functools.wraps(func)
        @logger.catch(message=f"Error in {func.__name__}")
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            logger.success(f"Successfully completed {func.__name__}")
            return result

        return wrapper

    @with_logging
    def may_fail(x):
        if x < 0:
            raise ValueError("Negative value!")
        return x * 2

    may_fail(10)  # Should log success
    may_fail(-5)  # Should log an error


Using logging function based on custom added levels
---------------------------------------------------

After adding a new level, it's habitually used with the |log| function::

    logger.level("foobar", no=33, icon="🤖", color="<blue>")

    logger.log("foobar", "A message")


For convenience, one can assign a new logging function which automatically uses the custom added level::

    from functools import partialmethod

    logger.__class__.foobar = partialmethod(logger.__class__.log, "foobar")

    logger.foobar("A message")


The new method need to be added only once and will be usable across all your files importing the ``logger``. Assigning the method to ``logger.__class__`` rather than ``logger`` directly ensures that it stays available even after calling ``logger.bind()``, ``logger.patch()`` and ``logger.opt()`` (because these functions return a new ``logger`` instance).


Setting permissions on created log files
----------------------------------------

To set desired permissions on created log files, use the ``opener`` argument to pass in a custom opener with permissions octal::

    def opener(file, flags):
        return os.open(file, flags, 0o600)  # read/write by owner only

    logger.add("foo.log", rotation="100 kB", opener=opener)

When using an opener argument, all created log files including ones created during rotation will use the initially provided opener.

Note that the provided mode will be masked out by the OS `umask <https://en.wikipedia.org/wiki/Umask>`_ value (describing which bits are *not* to be set when creating a file or directory). This value is conventionally equals to ``0o022``, which means specifying a ``0o666`` mode will result in a ``0o666 - 0o022 = 0o644`` file permission in this case (which is actually the default). It is possible to change the umask value by first calling |os.umask|, but this needs to be done with careful consideration, as it changes the value globally and can cause security issues.


Preserving an ``opt()`` parameter for the whole module
------------------------------------------------------

Supposing you wish to color each of your log messages without having to call ``logger.opt(colors=True)`` every time, you can add this at the very beginning of your module::

    logger = logger.opt(colors=True)

    logger.info("It <green>works</>!")

However, it should be noted that it's not possible to chain |opt| calls, using this method again will reset the ``colors`` option to its default value (which is ``False``). For this reason, it is also necessary to patch the |opt| method so that all subsequent calls continue to use the desired value::

    from functools import partial

    logger = logger.opt(colors=True)
    logger.opt = partial(logger.opt, colors=True)

    logger.opt(raw=True).info("It <green>still</> works!\n")


Serializing log messages using a custom function
------------------------------------------------

Each handler added with ``serialize=True`` will create messages by converting the logging record to a valid JSON string. Depending on the sink for which the messages are intended, it may be useful to make changes to the generated string. Instead of using the ``serialize`` parameter, you can implement your own serialization function and use it directly in your sink::

    def serialize(record):
        subset = {"timestamp": record["time"].timestamp(), "message": record["message"]}
        return json.dumps(subset)

    def sink(message):
        serialized = serialize(message.record)
        print(serialized)

    logger.add(sink)


If you need to send structured logs to a file (or any kind of sink in general), a similar result can be obtained by using a custom ``format`` function::

    def formatter(record):
        # Note this function returns the string to be formatted, not the actual message to be logged
        record["extra"]["serialized"] = serialize(record)
        return "{extra[serialized]}\n"

    logger.add("file.log", format=formatter)


You can also use |patch| for this, so the serialization function will be called only once in case you want to use it in multiple sinks::

    def patching(record):
        record["extra"]["serialized"] = serialize(record)

    logger = logger.patch(patching)

    # Note that if "format" is not a function, possible exception will be appended to the message
    logger.add(sys.stderr, format="{extra[serialized]}")
    logger.add("file.log", format="{extra[serialized]}")


Adapting colors and format of logged messages dynamically
---------------------------------------------------------

It is possible to customize the colors of your logs thanks to several :ref:`markup tags <color>`. Those are used to configure the ``format`` of your handler. By creating a appropriate formatting function, you can easily define colors depending on the logged message.

For example, if you want to associate each module with a unique color::

    from collections import defaultdict
    from random import choice

    colors = ["blue", "cyan", "green", "magenta", "red", "yellow"]
    color_per_module = defaultdict(lambda: choice(colors))

    def formatter(record):
        color_tag = color_per_module[record["name"]]
        return "<" + color_tag + ">[{name}]</> <bold>{message}</>\n{exception}"

    logger.add(sys.stderr, format=formatter)


If you need to dynamically colorize the ``record["message"]``, make sure that the color tags appear in the returned format instead of modifying the message::

    def rainbow(text):
        colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        chars = ("<{}>{}</>".format(colors[i % len(colors)], c) for i, c in enumerate(text))
        return "".join(chars)

    def formatter(record):
        rainbow_message = rainbow(record["message"])
        # Prevent '{}' in message (if any) to be incorrectly parsed during formatting
        escaped = rainbow_message.replace("{", "{{").replace("}", "}}")
        return "<b>{time}</> " + escaped + "\n{exception}"

    logger.add(sys.stderr, format=formatter)


Dynamically formatting messages to properly align values with padding
---------------------------------------------------------------------

The default formatter is unable to vertically align log messages because the length of ``{name}``, ``{function}`` and ``{line}`` are not fixed.

One workaround consists of using padding with some maximum value that should suffice most of the time. For this purpose, you can use Python's string formatting directives, like in this example::

    fmt = "{time} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}"
    logger.add(sys.stderr, format=fmt)

Here, ``<``, ``^`` and ``>`` will left, center, and right-align the respective keys, and pad them to a maximum length.

Other solutions are possible by using a formatting function or class. For example, it is possible to dynamically adjust the padding length based on previously encountered values::

    class Formatter:

        def __init__(self):
            self.padding = 0
            self.fmt = "{time} | {level: <8} | {name}:{function}:{line}{extra[padding]} | {message}\n{exception}"

        def format(self, record):
            length = len("{name}:{function}:{line}".format(**record))
            self.padding = max(self.padding, length)
            record["extra"]["padding"] = " " * (self.padding - length)
            return self.fmt

    formatter = Formatter()

    logger.remove()
    logger.add(sys.stderr, format=formatter.format)


Customizing the formatting of exceptions
----------------------------------------

Loguru will automatically add the traceback of occurring exception while using ``logger.exception()`` or ``logger.opt(exception=True)``::

    def inverse(x):
        try:
            1 / x
        except ZeroDivisionError:
            logger.exception("Oups...")

    if __name__ == "__main__":
        inverse(0)

.. code-block:: none

    2019-11-15 10:01:13.703 | ERROR    | __main__:inverse:8 - Oups...
    Traceback (most recent call last):
    File "foo.py", line 6, in inverse
        1 / x
    ZeroDivisionError: division by zero

If the handler is added with ``backtrace=True``, the traceback is extended to see where the exception came from:

.. code-block:: none

    2019-11-15 10:11:32.829 | ERROR    | __main__:inverse:8 - Oups...
    Traceback (most recent call last):
      File "foo.py", line 16, in <module>
        inverse(0)
    > File "foo.py", line 6, in inverse
        1 / x
    ZeroDivisionError: division by zero

If the handler is added with ``diagnose=True``, then the traceback is annotated to see what caused the problem:

.. code-block:: none

    Traceback (most recent call last):

    File "foo.py", line 6, in inverse
        1 / x
            └ 0

    ZeroDivisionError: division by zero

It is possible to further personalize the formatting of exception by adding an handler with a custom ``format`` function. For example, supposing you want to format errors using the |stackprinter|_ library::

    import stackprinter

    def format(record):
        format_ = "{time} {message}\n"

        if record["exception"] is not None:
            record["extra"]["stack"] = stackprinter.format(record["exception"])
            format_ += "{extra[stack]}\n"

        return format_

    logger.add(sys.stderr, format=format)

.. code-block:: none

    2019-11-15T10:46:18.059964+0100 Oups...
    File foo.py, line 17, in inverse
        15   def inverse(x):
        16       try:
    --> 17           1 / x
        18       except ZeroDivisionError:
        ..................................................
        x = 0
        ..................................................

    ZeroDivisionError: division by zero


Displaying a stacktrace without using the error context
-------------------------------------------------------

It may be useful in some cases to display the traceback at the time your message is logged, while no exceptions have been raised. Although this feature is not built-in into Loguru as it is more related to debugging than logging, it is possible to |patch| your logger and then display the stacktrace as needed (using the |traceback| module)::

    import traceback

    def add_traceback(record):
        extra = record["extra"]
        if extra.get("with_traceback", False):
            extra["traceback"] = "\n" + "".join(traceback.format_stack())
        else:
            extra["traceback"] = ""

    logger = logger.patch(add_traceback)
    logger.add(sys.stderr, format="{time} - {message}{extra[traceback]}")

    logger.info("No traceback")
    logger.bind(with_traceback=True).info("With traceback")

Here is another example that demonstrates how to prefix the logged message with the full call stack::

    import traceback
    from itertools import takewhile

    def tracing_formatter(record):
        # Filter out frames coming from Loguru internals
        frames = takewhile(lambda f: "/loguru/" not in f.filename, traceback.extract_stack())
        stack = " > ".join("{}:{}:{}".format(f.filename, f.name, f.lineno) for f in frames)
        record["extra"]["stack"] = stack
        return "{level} | {extra[stack]} - {message}\n{exception}"

    def foo():
        logger.info("Deep call")

    def bar():
        foo()

    logger.remove()
    logger.add(sys.stderr, format=tracing_formatter)

    bar()
    # Output: "INFO | script.py:<module>:23 > script.py:bar:18 > script.py:foo:15 - Deep call"


Manipulating newline terminator to write multiple logs on the same line
-----------------------------------------------------------------------

You can temporarily log a message on a continuous line by combining the use of |bind|, |opt| and a custom ``format`` function. This is especially useful if you want to illustrate a step-by-step process in progress, for example::

    def formatter(record):
        end = record["extra"].get("end", "\n")
        return "[{time}] {message}" + end + "{exception}"

    logger.add(sys.stderr, format=formatter)
    logger.add("foo.log", mode="w")

    logger.bind(end="").debug("Progress: ")

    for _ in range(5):
        logger.opt(raw=True).debug(".")

    logger.opt(raw=True).debug("\n")

    logger.info("Done")

.. code-block:: none

    [2020-03-26T22:47:01.708016+0100] Progress: .....
    [2020-03-26T22:47:01.709031+0100] Done

Note, however, that you may encounter difficulties depending on the sinks you use. Logging is not always appropriate for this type of end-user message.


Capturing standard ``stdout``, ``stderr`` and ``warnings``
----------------------------------------------------------

The use of logging should be privileged over |print|, yet, it may happen that you don't have plain control over code executed in your application. If you wish to capture standard output, you can suppress |sys.stdout| (and |sys.stderr|) with a custom stream object using |contextlib.redirect_stdout|. You have to take care of first removing the default handler, and not adding a new stdout sink once redirected or that would cause dead lock (you may use |sys.__stdout__| instead)::

    import contextlib
    import sys
    from loguru import logger

    class StreamToLogger:

        def __init__(self, level="INFO"):
            self._level = level

        def write(self, buffer):
            for line in buffer.rstrip().splitlines():
                logger.opt(depth=1).log(self._level, line.rstrip())

        def flush(self):
            pass

    logger.remove()
    logger.add(sys.__stdout__)

    stream = StreamToLogger()
    with contextlib.redirect_stdout(stream):
        print("Standard output is sent to added handlers.")


You may also capture warnings emitted by your application by replacing |warnings.showwarning|::

    import warnings
    from loguru import logger

    showwarning_ = warnings.showwarning

    def showwarning(message, *args, **kwargs):
        logger.opt(depth=2).warning(message)
        showwarning_(message, *args, **kwargs)

    warnings.showwarning = showwarning


Alternatively, if you want to emit warnings based on logged messages, you can simply use |warnings.warn| as a sink::


    logger.add(warnings.warn, format="{message}", filter=lambda record: record["level"].name == "WARNING")


Circumventing modules whose ``__name__`` value is absent
--------------------------------------------------------

Loguru makes use of the global variable ``__name__`` to determine from where the logged message is coming from. However, it may happen in very specific situation (like some Dask distributed environment) that this value is not set. In such case, Loguru will use ``None`` to make up for the lack of the value. This implies that if you want to |disable| messages coming from such special module, you have to explicitly call ``logger.disable(None)``.

Similar considerations should be taken into account while dealing with the ``filter`` attribute. As ``__name__`` is missing, Loguru will assign the ``None`` value to the ``record["name"]`` entry. It also means that once formatted in your log messages, the ``{name}`` token will be equals to ``"None"``. This can be worked around by manually overriding the ``record["name"]`` value using |patch| from inside the faulty module::

    # If Loguru fails to retrieve the proper "name" value, assign it manually
    logger = logger.patch(lambda record: record.update(name="my_module"))

You probably should not worry about all of this except if you noticed that your code is subject to this behavior.


Interoperability with ``tqdm`` iterations
-----------------------------------------

Trying to use the Loguru's ``logger`` during an iteration wrapped by the ``tqdm`` library may disturb the displayed progress bar. As a workaround, one can use the ``tqdm.write()`` function instead of writings logs directly to ``sys.stderr``::

    import time

    from loguru import logger
    from tqdm import tqdm

    logger.remove()
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

    logger.info("Initializing")

    for x in tqdm(range(100)):
        logger.info("Iterating #{}", x)
        time.sleep(0.1)


You may encounter problems with colorization of your logs after importing ``tqdm`` using Spyder on Windows. This issue is discussed in `GH#132`_. You can easily circumvent the problem by calling ``colorama.deinit()`` right after your import.


Using Loguru's ``logger`` within a Cython module
------------------------------------------------

Loguru and Cython do not interoperate very well. This is because Loguru (and logging generally) heavily relies on Python stack frames while Cython, being an alternative Python implementation, try to get rid of these frames for optimization reasons.

Calling the ``logger`` from code compiled with Cython may result in "incomplete" logs (missing call context):

.. code-block:: none

    2024-11-26 15:58:48.985 | INFO     | None:<unknown>:0 - Message from Cython!

This happens when Loguru tries to access a stack frame which has been suppressed by Cython. In such a case, there is no way for Loguru to retrieve contextual information of the logged message.

You can update the default ``format`` of your handlers and omit the uninteresting fields. You can also tries to |patch| the ``logger`` to manually add information you may know about the caller, for example::

    logger = logger.patch(lambda record: record.update(name="my_cython_module"))

Note that the ``"name"`` attribute of the log record is set to ``None`` when the frame is unavailable.


.. _creating-independent-loggers:

Creating independent loggers with separate set of handlers
----------------------------------------------------------

Loguru is fundamentally designed to be usable with exactly one global ``logger`` object dispatching logging messages to the configured handlers. In some circumstances, it may be useful to have specific messages logged to specific handlers.

For example, supposing you want to split your logs in two files based on an arbitrary identifier, you can achieve that by combining |bind| and ``filter``::

    from loguru import logger

    def task_A():
        logger_a = logger.bind(task="A")
        logger_a.info("Starting task A")
        do_something()
        logger_a.success("End of task A")

    def task_B():
        logger_b = logger.bind(task="B")
        logger_b.info("Starting task B")
        do_something_else()
        logger_b.success("End of task B")

    logger.add("file_A.log", filter=lambda record: record["extra"]["task"] == "A")
    logger.add("file_B.log", filter=lambda record: record["extra"]["task"] == "B")

    task_A()
    task_B()

That way, ``"file_A.log"`` and ``"file_B.log"`` will only contains logs from respectively the ``task_A()`` and ``task_B()`` function.

Now, supposing that you have a lot of these tasks. It may be a bit cumbersome to configure every handlers like this. Most importantly, it may unnecessarily slow down your application as each log will need to be checked by the ``filter`` function of each handler. In such case, it is recommended to rely on the |copy.deepcopy| built-in method that will create an independent ``logger`` object. If you add a handler to a deep copied ``logger``, it will not be shared with others functions using the original ``logger``::

    import copy
    from loguru import logger

    def task(task_id, logger):
        logger.info("Starting task {}", task_id)
        do_something(task_id)
        logger.success("End of task {}", task_id)

    logger.remove()

    for task_id in ["A", "B", "C", "D", "E"]:
        logger_ = copy.deepcopy(logger)
        logger_.add("file_%s.log" % task_id)
        task(task_id, logger_)

Note that you may encounter errors if you try to copy a ``logger`` to which non-picklable handlers have been added. For this reason, it is generally advised to remove all handlers before calling ``copy.deepcopy(logger)``.


.. _multiprocessing-compatibility:

Compatibility with ``multiprocessing`` using ``enqueue`` argument
-----------------------------------------------------------------

On Linux, thanks to |os.fork| there is no pitfall while using the ``logger`` inside another process started by the |multiprocessing| module. The child process will automatically inherit added handlers, the ``enqueue=True`` parameter is optional but is recommended as it would avoid concurrent access of your sink::

    # Linux implementation
    import multiprocessing
    from loguru import logger

    def my_process():
        logger.info("Executing function in child process")
        logger.complete()

    if __name__ == "__main__":
        logger.add("file.log", enqueue=True)

        process = multiprocessing.Process(target=my_process)
        process.start()
        process.join()

        logger.info("Done")

Things get a little more complicated on Windows. Indeed, this operating system does not support forking, so Python has to use an alternative method to create sub-processes called "spawning". This procedure requires the whole file where the child process is created to be reloaded from scratch. This does not interoperate very well with Loguru, causing handlers to be added twice without any synchronization or, on the contrary, not being added at all (depending on ``add()`` and ``remove()`` being called inside or outside the ``__main__`` branch). For this reason, the ``logger`` object need to be explicitly passed as an initializer argument of your child process::

    # Windows implementation
    import multiprocessing
    from loguru import logger

    def my_process(logger_):
        logger_.info("Executing function in child process")
        logger_.complete()

    if __name__ == "__main__":
        logger.remove()  # Default "sys.stderr" sink is not picklable
        logger.add("file.log", enqueue=True)

        process = multiprocessing.Process(target=my_process, args=(logger, ))
        process.start()
        process.join()

        logger.info("Done")

Windows requires the added sinks to be picklable or otherwise will raise an error while creating the child process. Many stream objects like standard output and file descriptors are not picklable. In such case, the ``enqueue=True`` argument is required as it will allow the child process to only inherit the queue object where logs are sent.

The |multiprocessing| library is also commonly used to start a pool of workers using for example |Pool.map| or |Pool.apply|. Again, it will work flawlessly on Linux, but it will require some tinkering on Windows. You will probably not be able to pass the ``logger`` as an argument for your worker functions because it needs to be picklable, but although handlers added using ``enqueue=True`` are "inheritable", they are not "picklable". Instead, you will need to make use of the ``initializer`` and ``initargs`` parameters while creating the |Pool| object in a way allowing your workers to access the shared ``logger``. You can either assign it to a class attribute or override the global logger of your child processes:

.. code::

    # workers_a.py
    class Worker:

        _logger = None

        @staticmethod
        def set_logger(logger_):
            Worker._logger = logger_

        def work(self, x):
            self._logger.info("Square rooting {}", x)
            return x**0.5


.. code::

    # workers_b.py
    from loguru import logger

    def set_logger(logger_):
        global logger
        logger = logger_

    def work(x):
        logger.info("Square rooting {}", x)
        return x**0.5


.. code::

    # main.py
    from multiprocessing import Pool
    from loguru import logger
    import workers_a
    import workers_b

    if __name__ == "__main__":
        logger.remove()
        logger.add("file.log", enqueue=True)

        worker = workers_a.Worker()
        with Pool(4, initializer=worker.set_logger, initargs=(logger, )) as pool:
            results = pool.map(worker.work, [1, 10, 100])

        with Pool(4, initializer=workers_b.set_logger, initargs=(logger, )) as pool:
            results = pool.map(workers_b.work, [1, 10, 100])

        logger.info("Done")

Independently of the operating system, note that the process in which a handler is added with ``enqueue=True`` is in charge of the queue internally used. This means that you should avoid to ``.remove()`` such handler from the parent process is any child is likely to continue using it. More importantly, note that a |Thread| is started internally to consume the queue. Therefore, it is recommended to call |complete| before leaving |Process| to make sure the queue is left in a stable state.

Another thing to keep in mind when dealing with multiprocessing is the fact that handlers created with ``enqueue=True`` create a queue internally in the default multiprocessing context. If they are passed through to a subprocesses instantiated within a different context (e.g. with ``multiprocessing.get_context("spawn")`` on linux, where the default context is ``"fork"``) it will most likely result in crashing the subprocess. This is also noted in the `python multiprocessing docs <https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods>`_. To prevent any problems, you should specify the context to be used by Loguru while adding the handler. This can be done by passing the ``context`` argument to the ``add()`` method::

    import multiprocessing
    from loguru import logger
    import workers_a

    if __name__ == "__main__":
        context = multiprocessing.get_context("spawn")

        logger.remove()
        logger.add("file.log", enqueue=True, context=context)

        worker = workers_a.Worker()
        with context.Pool(4, initializer=worker.set_logger, initargs=(logger, )) as pool:
            results = pool.map(worker.work, [1, 10, 100])


.. _recipes-testing:

Unit testing logs emitted by Loguru
-----------------------------------

Logging calls can be tested using |logot|_, a high-level log testing library with built-in support for Loguru::

    from logot import Logot, logged

    def test_something(logot: Logot) -> None:
        do_something()
        logot.assert_logged(logged.info("Something was done"))

Enable Loguru log capture in your |pytest|_ configuration:

.. code:: toml

   [tool.pytest.ini_options]
   logot_capturer = "logot.loguru.LoguruCapturer"

.. seealso::

    See `using logot with Loguru <https://logot.readthedocs.io/latest/integrations/loguru.html>`_ for more information
    about `configuring pytest <https://logot.readthedocs.io/latest/integrations/loguru.html#enabling-for-pytest>`_
    and `configuring unittest <https://logot.readthedocs.io/latest/integrations/loguru.html#enabling-for-unittest>`_.

.. note::

    When migrating an existing project from standard :mod:`logging`, it can be useful to migrate your existing test
    cases too. See :ref:`migrating assertLogs() <migration-assert-logs>` and :ref:`migrating caplog <migration-caplog>`
    for more information.
```

## File: docs/resources/troubleshooting.rst
```
Frequently Asked Questions and Troubleshooting Tips for Loguru
==============================================================

.. highlight:: python3

.. |sys.stdout| replace:: :data:`sys.stdout`
.. |sys.stderr| replace:: :data:`sys.stderr`
.. |str.format| replace:: :meth:`str.format()`
.. |isatty| replace:: :meth:`~io.IOBase.isatty`
.. |IOBase.close| replace:: :meth:`~io.IOBase.close`

.. |Logger| replace:: :class:`~loguru._logger.Logger`
.. |add| replace:: :meth:`~loguru._logger.Logger.add()`
.. |remove| replace:: :meth:`~loguru._logger.Logger.remove()`
.. |bind| replace:: :meth:`~loguru._logger.Logger.bind()`
.. |opt| replace:: :meth:`~loguru._logger.Logger.opt()`
.. |patch| replace:: :meth:`~loguru._logger.Logger.patch()`

.. |colorama| replace:: ``colorama``
.. _colorama: https://github.com/tartley/colorama

.. |if-name-equals-main| replace:: ``if __name__ == "__main__":``
.. _if-name-equals-main: https://docs.python.org/3/library/__main__.html#idiomatic-usage

.. |the-no-color-environment-variable| replace:: the ``NO_COLOR`` environment variable
.. _the-no-color-environment-variable: https://no-color.org/

.. _ANSI escape sequences: https://en.wikipedia.org/wiki/ANSI_escape_code


How do I create and configure a logger?
---------------------------------------

Loguru differs from standard logging as you don't need to create a logger. It is directly provided by Loguru, and you should just import it::

    from loguru import logger

    logger.info("Hello, World!")

This |Logger| object is unique and shared across all modules of your application. Import it into every file where you need to use it. It acts as a basic facade interface around a list of handlers. These handlers are responsible for receiving log messages, formatting them, and logging them to one or more desired destinations (file, console, etc.).

When you first import Loguru's logger, it comes pre-configured with a default handler that displays your logs on the standard error output (|sys.stderr|). However, you can easily change the logger's configuration to suit your needs. First, use |remove| to discard the default handler. Then, use |add| to register one or more handlers that will log messages to the desired destinations. For example::

    logger.remove()  # Remove the default handler.
    logger.add(sys.stderr, format="{time} - {level} - {message}")  # Log to console with custom format.
    logger.add("file.log", level="INFO", rotation="500 MB")  # Also log to a file, rotating every 500 MB.

The logger should be configured only once, at the entry point of your application (typically within a |if-name-equals-main|_ block). Other modules in your application will automatically inherit this configuration by simply importing Loguru's global ``logger``.

.. seealso::

   :ref:`Configuring Loguru to be used by a library or an application <configuring-loguru-as-lib-or-app>`


Why are my logs duplicated in the output?
-----------------------------------------

Remember that the initial ``logger`` has a default handler for convenience. If you plan to change the logging configuration, make sure to |remove| this default handler before to |add| a new one. Otherwise, messages will be duplicated because they will be sent to both the default handler and your new handler::

    # Replace the default handler with a new one.
    logger.remove()
    logger.add(sys.stderr, format="{time} - {level} - {message}")

Additionally, since there is a single ``logger`` shared across all modules in your application, you should configure it in one place only. Handlers will be added as many times as ``logger.add()`` is called, so be careful not to reconfigure it multiple times.

In particular when using ``multiprocessing`` (either directly or indirectly through a web framework, for instance), ensure that the ``logger`` configuration is guarded by an if |if-name-equals-main|_ block. Otherwise, each spawned child process will re-execute the configuration code. This can result in duplicated logs or unexpected configurations. See :ref:`this section of the documentation <multiprocessing-compatibility>` for details.

Finally, don't forget that the ``level`` argument of |add| defines a minimum threshold, not an exact filtering mechanism. It is generally a mistake to add two handlers with the same sink, as it will cause duplication unless they are configured with mutually exclusive ``filter`` functions. For example::

    def is_debug(record):
        return record["level"].no <= 10

    logger.add(sys.stderr, level="DEBUG", format="{time} - {name} - {message}", filter=is_debug)
    logger.add(sys.stderr, level="INFO", format="{message}", filter=lambda r: not is_debug(r))


How do I set the logging level?
-------------------------------

The :ref:`logging levels <levels>` allow filtering messages based on their importance. It is a minimum threshold above which messages are logged (or ignored otherwise). This makes it possible, for example, to adjust the verbosity of logs depending on the execution environment (development or production).

The |Logger| itself is not associated with any specific level. Instead, it is the level of each handler that individually determines whether a message is logged or not. This level is defined when configuring the handler and adding it to the logger using the ``level`` argument of the |add| method::

    logger.add(sys.stdout, level="WARNING")  # Log only messages with level "WARNING" or higher.
    logger.debug("Some debug message")  # Will be ignored.
    logger.error("Some error message")  # Will be displayed.

It is not possible to change the level of an existing handler. If you need to modify the logging level, you can |remove| the existing handler and |add| a new one with the desired level::

    logger.remove()  # Remove the default handler.
    logger.add(sys.stderr, level="INFO")

By default, the level of each handler is ``"DEBUG"``. You can adjust this value :ref:`using environment variables <env>`.

.. seealso::

   :ref:`Changing the level of an existing handler <changing-level-of-existing-handler>`


How do I customize the log format and re-use the default one?
-------------------------------------------------------------

The log format must be defined using the ``format`` argument of the |add| method::

    logger.add(sys.stderr, format="{time} - {level} - {message}")

Refer to :ref:`this section of the documentation <record>` to learn about the different formatting variables available. You can also use :ref:`color tags <color>`::

    logger.add(sys.stderr, format="<green>{time}</> - {level} - <lvl>{message}</>")

For advanced configuration, the ``format`` argument also accepts a function, allowing you to dynamically generate the desired format. Be aware that in this case, you have to explicitly include the line ending and exception field (since you gain full control over the formatting, while ``"\n{exception}"`` is added automatically when the ``format`` is a string). For example, to include the thread identifier but only for error messages and above::

        def custom_formatter(record):
            if record["level"].no >= 40:
                return "<green>{time}</> - {level} - <red>{thread}</> - <lvl>{message}</>\n{exception}"
            else:
                return "<green>{time}</> - {level} - <lvl>{message}</lvl>\n{exception}"

        logger.add(sys.stderr, format=custom_formatter)

Finally, note that accessing the default log format is not directly possible, as it would only be useful in a very limited number of cases. Instead, you need to explicitly redefine your desired format. To quickly copy-paste the default logging format, check out the ``LOGURU_FORMAT`` variable `in the source code <https://github.com/Delgan/loguru/blob/master/loguru/_defaults.py>`_.


Why are my logs not colored?
----------------------------

Log colors are configured using :ref:`special tags <color>` in the ``format`` of the handlers. If you use a custom ``format``, make sure that these tags are included, for example::

    logger.add(sys.stderr, format="<green>{time}</green> | <level>{message}</level>")

When adding a handler with ``colorize=None`` (the default), Loguru tries to automatically detect whether the added sink (such as ``sys.stderr`` in the above example) supports colors. If it's not the case, color tags will be stripped. Otherwise, they'll be converted to `ANSI escape sequences`_.

These sequences are generally only supported within a terminal. Therefore, it is normal that you don't see colors when logs are saved to a text file. Sinks that support colors are usually |sys.stderr| and |sys.stdout|::

    logger.add(sys.stderr)  # Can be colored.
    logger.add("file.log")  # Cannot be colored.

When such stream object is used for logging, Loguru will also call |isatty| to determine whether colors should be used. This method notably returns ``False`` if the stream is not connected to a terminal, which would make colorization pointless. For example, redirecting the output of your script to a file will disable colors:

.. code-block:: bash

    python my_script.py > output.log  # Colors will be disabled.

Additionally, it is not uncommon in some virtual environments for the standard output not to be considered as connected to a terminal, even though you can view the logs' output live without redirection. This is the case, for instance, in some cloud services. Check the value of ``sys.stderr.isatty()`` if you encounter any issues.

Various heuristics assist in determining whether colors should be enabled by default. Specifically, Loguru honors |the-no-color-environment-variable|_ and disables coloring if it is set to any value. Additionally, terminals identified by ``TERM=dumb`` are considered to lack color support.

In any case, you can always control log coloring by explicitly specifying the ``colorize`` argument of the |add| method::

    logger.add(sys.stderr, colorize=True)  # Force ANSI sequences in output.

Conversely, if raw ANSI sequences such as ``\x1b[31m`` or ``\x1b[0m`` appear in your logs, it certainly means the sink does not support colors, and you should disable them.

Note that on Windows, log coloring is handled using the |colorama|_ library.


Why are my logs not showing up?
-------------------------------

Ensure that you've added at least one sink using |add|. You can get an overview of the configured handlers by simply printing the logger object::

    print(logger)
    # Output: <loguru.logger handlers=[(id=0, level=10, sink=<stderr>)]>


Check also the logging level: messages below the set level won't appear::

    logger.add(sys.stderr, level="INFO")
    logger.debug("Some debug message")  # Won't be displayed since "DEBUG" is below "INFO".


Why is the captured exception missing from the formatted message?
-----------------------------------------------------------------

When ``logger.exception()`` or ``logger.opt(exception=True)`` is used within an ``except`` clause, Loguru automatically captures the exception information and includes it in :ref:`the logged message <message>`.

The position of the exception in the message is controlled by the ``"{exception}"`` field of the configured log format. By default, when the ``format`` argument of |add| is a string, the ``"{exception}"`` field is automatically appended to the format::

    # The "{exception}" placeholder is implicit here (at the end of the format).
    log_format = "{time} - {level} - {message}"
    logger.add(sys.stderr, format=log_format)


However, when using a custom function to define the format of logs, the user gets complete control over the desired format. This means the ``"{exception}"`` field must be explicitly included::

    def custom_formatter(record):
        return "{time} - {level} - {message}\n{exception}"

    logger.add(sys.stderr, format=custom_formatter)

If the field is missing, the formatted error will not appear in the log message. Always ensure the ``"{exception}"`` placeholder is present in your log format if you want exception details to appear in your logs.


How can I use different loggers in different modules of my application?
-----------------------------------------------------------------------

Since Loguru is designed on the use of a single ``logger``, it is fundamentally not possible to create different loggers for multiple modules. The idea is that modules should simply import the global ``logger`` from ``loguru``, and log differentiation should be handled through handlers (which should only be configured once, at the application's entry point).

Note that is generally possible to identify the origin of a log message via the ``record["name"]`` field in the record dict. This field contains the name of the module that emitted the message. For example, you can use this information to redirect messages based on their origin::

    logger.add("my_app.log")  # All messages.
    logger.add("module_1.log", filter="module_1")  # Messages from "module_1" only.
    logger.add("module_2.log", filter="module_2")  # Messages from "module_2" only.

For more advanced use cases, it is recommended to use the |bind| method, which returns a new instance of the ``logger`` tied to the given value. This allows you to identify logs more precisely::

    def is_specific_log(record):
        return record["extra"].get("is_specific") is True

    logger.add("specific.log", filter=is_specific_log)
    logger.add("other.log", filter=lambda r: not is_specific_log(r))

    specific_logger = logger.bind(is_specific=True)
    specific_logger.info("This message will go to 'specific.log' only.")

    logger.info("This message will go to 'other.log' only.")

.. seealso::

   :ref:`Creating independent loggers with separate set of handlers <creating-independent-loggers>`


Why are my log files sometimes duplicated or the content trimmed?
-----------------------------------------------------------------

Problem with logging files duplicated or trimmed is generally symptomatic of a configuration issue. More precisely, this can happen if |add| is inadvertently called multiple times with the same file path.

When this happens, the file is opened again by the newly created handler. Consequently, multiple handlers manage and write to the same file concurrently. This is an incorrect situation that inevitably leads to conflicts. If the problem isn't detected, handlers risk overwriting logs over each other, otherwise it can also result in duplicated files at the moment of the rotation.

If you observe such weird behavior, you should review your code carefully to ensure that the same file sink is not being added multiple times. This can occur if ``multiprocessing`` is used incorrectly (see :ref:`this section of the documentation <multiprocessing-compatibility>` for more details). You have to make sure that the logger is not configured repeatedly by different processes, and you should use a |if-name-equals-main|_ guard.

It is also a common issue with web frameworks like Gunicorn and Uvicorn, as they start multiple workers in parallel. In such cases, you need to set up a log server, and configure workers to send messages to it using a socket. Refer to :ref:`Transmitting log messages across network, processes or Gunicorn workers <inter-process-communication>` for details.


Why logging a message with f-string sometimes raises an exception?
------------------------------------------------------------------

When positional or keyword arguments are passed to the logging function, Loguru will integrate them to the message. For example::

    logger.info("My name is {name}", name="John")
    # Output: [INFO] My name is John

This is actually equivalent to using the |str.format| built-in Python method::

    message = "My name is {name}".format(name="John")
    logger.info(message)

However, the behavior described above can cause an error if the arguments passed were not intended to be formatted with the message (but rather just captured in the "extra" dict of the log record). This is particularly true if the message contains curly braces. The formatting function will then interpret them as placeholders and attempt to replace them with the passed arguments.

Here are some examples that result in various exceptions:

.. code-block::

    # KeyError: 'key1, key2'
    logger.warning("Config file missing keys: {key1, key2}", filename="app.cfg")

.. code-block::

    # ValueError: Single '{' encountered in format string
    logger.info("This is a curly bracket: {", foo="bar")

.. code-block::

    # AttributeError: 'dict' object has no attribute 'format'
    logger.debug({"key": "value"}, identifier=42)

.. code-block::

    # IndexError: Replacement index 0 out of range for positional args tuple
    logger.error("Use 'set()' not '{}' for empty set", strictness=9)


It is common to encounter these errors when using f-strings, as this can leads to the creation of a message that already contains curly braces. For example::

    data = {"foo": 42}

    # Will raise "KeyError" because it's equivalent to:
    #   logger.info("Processing '{'foo': 42}'", data=data)
    logger.info(f"Processing '{data}'", data=data)

Therefore, you must be careful not to inadvertently introduce curly braces into the message. Instead of using an f-string, you can let Loguru handle the formatting::

    logger.info("Processing '{data}'", data=data)

You can also use |bind| to add extra information to a message without formatting it::

    logger.bind(data=data).info(f"Processing '{data}'")

Finally, you can possibly disable formatting by doubling the curly braces::

    logger.info("Curly brackets are {{ and }}", data=data)


How do I fix "ValueError: I/O operation error on closed file"?
--------------------------------------------------------------

This error occurs because the logger is trying to write to a stream object (like ``sys.stderr`` or ``sys.stdout``) that has been closed, which is invalid (see |IOBase.close|).

When stream objects are used as logging sink, Loguru will not close them. This would be very inconvenient and incorrect (as the stream is global, it must remain usable after the sink has been removed). Since Loguru does not close such a stream by itself, this means something else closed the stream while it was still in use by the ``logger``.

This is generally due to some tools or specific environments that take the liberty of replacing ``sys.stdout`` and ``sys.stderr`` with their own stream object. In this way, they can capture what is written to the standard output. This is the case with some libraries, IDEs and cloud platforms.
The problem is that the ``logger`` will use this wrapped stream as well. If the third-party tool happens to clean up and close the stream, then the ``logger`` is left with an unusable sink.

Here is a simplified example to illustrate the issue::

    from contextlib import contextmanager
    import sys
    import io
    from loguru import logger


    @contextmanager
    def redirect_stdout(new_target):
        old_target, sys.stdout = sys.stdout, new_target
        try:
            yield new_target
        finally:
            sys.stdout = old_target
            new_target.close()


    if __name__ == "__main__":
        logger.remove()
        f = io.StringIO()

        with redirect_stdout(f):
            logger.add(sys.stdout)  # Logger is inadvertently configured with wrapped stream.
            logger.info("Hello")
            output = f.getvalue()

        print(f"Captured output: {output}")

        # ValueError: I/O operation on closed file.
        logger.info("World")


And here is another example causing the same error with Pytest::

    import sys
    from loguru import logger

    logger.remove()

    def test_1(capsys):
        # Here, "sys.stderr" is actually a mock object due to usage of "capsys" fixture.
        logger.add(sys.stderr, catch=False)
        logger.info("Test 1")


    def test_2():
        # After execution of the previous test, the mocked "sys.stderr" was closed by Pytest.
        # However, the handler was not removed from the Loguru logger. It'll raise a "ValueError" here.
        logger.info("Test 2", catch=False)


What you can possibly do in such a situation:

- identify any tool that could be manipulating ``sys.stdout``, try to call ``print(sys.stdout)`` to see if it's a wrapper object;
- make sure the ``logger`` is always fully re-initialized whenever your code is susceptible to clean up the wrapped ``sys.stdout``;
- configure the ``logger`` with ``logger.add(lambda m: sys.stdout.write(m))`` instead of ``logger.add(sys.stdout)``, so that the stream is dynamically retrieved and therefore not affected by changes.


How do I prevent "RuntimeError" due to "deadlock avoided"?
----------------------------------------------------------

The logging functions are not reentrant. This means you must not use the logger when it's already in use in the same thread. This situation can occur notably if you use the logger inside a sink (which itself is called by the logger). Logically, this would result in an infinite recursive loop. In practice, it would more likely cause your application to hang because logging is protected by an internal lock.

To prevent such problems, there is a mechanism that detects and prevents the logger from being called recursively. This is what might lead to a ``RuntimeError``. When faced with such an error, you need to ensure that the handlers you configure do not internally call the logger. This also applies to the logger from the standard ``logging`` library.

If you cannot prevent the use of the logger inside a handler, you should implement a ``filter`` to avoid recursive calls. For example::

    import sys
    from loguru import logger


    def my_sink(message):
        logger.debug("Within my sink")
        print(message, end="")


    def avoid_recursion(record):
        return record["function"] != "my_sink"


    if __name__ == "__main__":
        logger.remove()
        logger.add("file.log")
        logger.add(my_sink, filter=avoid_recursion)

        logger.info("First message")
        logger.debug("Another message")


Why is the source (name, file, function, line) of the log message incorrect or missing?
---------------------------------------------------------------------------------------

In some very specific circumstances, the module name might be ``None`` and the filename and function name might be ``"<unknown>"``.

.. code-block:: none

    2024-12-01 16:23:21.769 | INFO     | None:<unknown>:0 - Message from unknown source.

Such a situation indicates that the ``logger`` was unable to retrieve the caller's context. In particular, this can happen when Loguru is used with Dask or Cython. In such cases, this behavior is normal, and there is nothing to do unless you wish to implement a custom |patch| function::

    logger = logger.patch(lambda record: record.update(name="my_module"))

This issue may also result from improper use of the ``depth`` argument of the |opt| method. Make sure that the value of this argument is correct.


Why can't I access the ``Logger`` class and other types at runtime?
-------------------------------------------------------------------

The ``logger`` object imported from the ``loguru`` library is an instance of the |Logger| class. However, you should not attempt to instantiate a logger yourself. The |Logger| class is not public and will be unusable by your Python application. It is therefore expected that the following code will raise an error::

    from loguru import Logger
    # Output: ImportError: cannot import name 'Logger' from 'loguru'

It is only possible to use the |Logger| class in the context of type hints. In such cases, no error will be raised. Said otherwise, that means only type checkers can access the |Logger| class. Below is an example of how to use ``Logger`` for typing purposes, but without runtime access::

    from __future__ import annotations

    import typing

    from loguru import logger

    if typing.TYPE_CHECKING:
        from loguru import Logger

    def my_function(logger: Logger):
        logger.info("Hello, World!")

If for some reason you need to perform type checking at runtime, you can make a comparison with the type on the ``logger`` instance::

    import loguru
    import logging

    def my_function(logger: loguru.Logger | logging.Logger):
        if isinstance(logger, type(loguru.logger)):
            logger.info("Hello, {}!", "World")
        else:
            logger.info("Hello, %s!", "World")

.. seealso::

   :ref:`Type hints <type-hints>`
```

## File: docs/api.rst
```
API Reference
=============

.. automodule:: loguru

.. toctree::
   :hidden:
   :includehidden:

   api/logger.rst
   api/type_hints.rst


* :class:`~loguru._logger.Logger`

    * :meth:`~loguru._logger.Logger.add`

        * :ref:`sink`
        * :ref:`message`
        * :ref:`levels`
        * :ref:`record`
        * :ref:`time`
        * :ref:`file`
        * :ref:`color`
        * :ref:`env`

    * :meth:`~loguru._logger.Logger.remove`
    * :meth:`~loguru._logger.Logger.complete`
    * :meth:`~loguru._logger.Logger.catch`
    * :meth:`~loguru._logger.Logger.opt`
    * :meth:`~loguru._logger.Logger.bind`
    * :meth:`~loguru._logger.Logger.contextualize`
    * :meth:`~loguru._logger.Logger.patch`
    * :meth:`~loguru._logger.Logger.level`
    * :meth:`~loguru._logger.Logger.disable`
    * :meth:`~loguru._logger.Logger.enable`
    * :meth:`~loguru._logger.Logger.configure`
    * :meth:`~loguru._logger.Logger.reinstall`
    * :meth:`~loguru._logger.Logger.parse`
    * :meth:`~loguru._logger.Logger.trace`
    * :meth:`~loguru._logger.Logger.debug`
    * :meth:`~loguru._logger.Logger.info`
    * :meth:`~loguru._logger.Logger.success`
    * :meth:`~loguru._logger.Logger.warning`
    * :meth:`~loguru._logger.Logger.error`
    * :meth:`~loguru._logger.Logger.critical`
    * :meth:`~loguru._logger.Logger.log`
    * :meth:`~loguru._logger.Logger.exception`

* :ref:`type-hints`
```

## File: docs/index.rst
```
.. include:: ../README.md
   :parser: myst_parser.sphinx_
   :end-before: <!-- end-of-readme-intro -->

Table of Contents
=================

.. toctree::
   :includehidden:
   :maxdepth: 2

   overview.rst
   api.rst
   resources.rst
   project.rst
```

## File: docs/overview.rst
```
Overview
========

.. include:: ../README.md
   :parser: myst_parser.sphinx_
   :start-after: <!-- end-of-readme-intro -->
   :end-before: <!-- end-of-readme-usage -->
```

## File: docs/project.rst
```
Project Information
===================

.. toctree::

   project/contributing.rst
   project/license.rst
   project/changelog.rst
```

## File: docs/resources.rst
```
Help & Guides
=============

.. toctree::

   resources/migration.rst
   resources/troubleshooting.rst
   resources/recipes.rst
```
