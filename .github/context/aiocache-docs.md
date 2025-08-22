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
  caches.rst
  decorators.rst
  index.rst
  locking.rst
  plugins.rst
  serializers.rst
  testing.rst
  v1_migration.rst
```

# Files

## File: docs/caches.rst
```
..  _caches:

Caches
======

You can use different caches according to your needs. All the caches implement the same interface.

Caches are always working together with a serializer which transforms data when storing and retrieving from the backend. It may also contain plugins that are able to enrich the behavior of your cache (like adding metrics, logs, etc).

This is the flow of the ``set`` command:

.. image:: images/set_operation_flow.png
  :align: center

Let's go with a more specific case. Let's pick Redis as the cache with namespace "test" and PickleSerializer as the serializer:

#. We receive ``set("key", "value")``.
#. Hook ``pre_set`` of all attached plugins (none by default) is called.
#. "key" will become "test:key" when calling ``build_key``.
#. "value" will become an array of bytes when calling ``serializer.dumps`` because of ``PickleSerializer``.
#. the byte array is stored together with the key using ``set`` cmd in Redis.
#. Hook ``post_set`` of all attached plugins is called.

By default, all commands are covered by a timeout that will trigger an ``asyncio.TimeoutError`` in case of timeout. Timeout can be set at instance level or when calling the command.

The supported commands are:

  - add
  - get
  - set
  - multi_get
  - multi_set
  - delete
  - exists
  - increment
  - expire
  - clear
  - raw

If you feel a command is missing here do not hesitate to `open an issue <https://github.com/argaen/aiocache/issues>`_


..  _basecache:

BaseCache
---------

.. autoclass:: aiocache.base.BaseCache
  :members:


..  _rediscache:

RedisCache
----------

.. autoclass:: aiocache.backends.redis.RedisCache
  :members:


..  _simplememorycache:

SimpleMemoryCache
-----------------

.. autoclass:: aiocache.SimpleMemoryCache
  :members:


..  _memcachedcache:

MemcachedCache
--------------

.. autoclass:: aiocache.backends.memcached.MemcachedCache
  :members:


..  _dynamodbcache:

Third-party caches
==================

Additional cache backends are available through other libraries.

DynamoDBCache
-------------

`aiocache-dynamodb <https://github.com/vonsteer/aiocache-dynamodb>`_ provides support for DynamoDB.

.. autoclass:: aiocache_dynamodb.DynamoDBCache
  :members:
```

## File: docs/decorators.rst
```
..  _decorators:

Decorators
==========

aiocache comes with a couple of decorators for caching results from asynchronous functions. Do not use the decorator in synchronous functions, it may lead to unexpected behavior.

..  _cached:

cached
------

.. automodule:: aiocache
  :members: cached

.. literalinclude:: ../examples/cached_decorator.py
  :language: python
  :linenos:

..  _multi_cached:

multi_cached
------------

.. automodule:: aiocache
  :members: multi_cached

.. literalinclude:: ../examples/multicached_decorator.py
  :language: python
  :linenos:
```

## File: docs/index.rst
```
.. aiocache documentation master file, created by
   sphinx-quickstart on Sat Oct  1 16:53:45 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aiocache's documentation!
====================================


Installing
----------

- ``pip install aiocache``
- ``pip install aiocache[redis]``
- ``pip install aiocache[memcached]``
- ``pip install aiocache[redis,memcached]``


Usage
-----

Using a cache is as simple as

.. code-block:: python

    >>> import asyncio
    >>> from aiocache import SimpleMemoryCache
    >>> cache = SimpleMemoryCache()
    >>> with asyncio.Runner() as runner:
    >>>     runner.run(cache.set("key", "value"))
    True
    >>>     runner.run(cache.get("key"))
    'value'

Here we are using the :ref:`simplememorycache` but you can use any other supported backends as listed in :ref:`caches`.
All caches contain the same minimum interface which consists of the following functions:

- ``add``: Only adds key/value if key does not exist. Otherwise raises ValueError.
- ``get``: Retrieve value identified by key.
- ``set``: Sets key/value.
- ``multi_get``: Retrieves multiple key/values.
- ``multi_set``: Sets multiple key/values.
- ``exists``: Returns True if key exists False otherwise.
- ``increment``: Increment the value stored in the given key.
- ``delete``: Deletes key and returns number of deleted items.
- ``clear``: Clears the items stored.
- ``raw``: Executes the specified command using the underlying client.

See the `examples folder <https://github.com/argaen/aiocache/tree/master/examples>`_ for different use cases:

- `Sanic, Aiohttp and Tornado <https://github.com/argaen/aiocache/tree/master/examples/frameworks>`_
- `Python object in Redis <https://github.com/argaen/aiocache/blob/master/examples/python_object.py>`_
- `Custom serializer for compressing data <https://github.com/argaen/aiocache/blob/master/examples/serializer_class.py>`_
- `TimingPlugin and HitMissRatioPlugin demos <https://github.com/argaen/aiocache/blob/master/examples/plugins.py>`_
- `Using marshmallow as a serializer <https://github.com/argaen/aiocache/blob/master/examples/marshmallow_serializer_class.py>`_
- `Using cached decorator <https://github.com/argaen/aiocache/blob/master/examples/cached_decorator.py>`_.
- `Using multi_cached decorator <https://github.com/argaen/aiocache/blob/master/examples/multicached_decorator.py>`_.


Contents
--------

.. toctree::

  caches
  serializers
  plugins
  decorators
  locking
  testing
  v1_migration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

## File: docs/locking.rst
```
..  _locking:

.. WARNING::
  This was added in version 0.7.0 and the API is new. This means its open to breaking changes in future versions until the API is considered stable.


Locking
=======


.. WARNING::
   The implementations provided are **NOT** intented for consistency/synchronization purposes. If you need a locking mechanism focused on consistency, consider implementing your mechanism based on more serious tools like https://zookeeper.apache.org/.


There are a couple of locking implementations than can help you to protect against different scenarios:


..  _redlock:

RedLock
-------

.. autoclass:: aiocache.lock.RedLock
  :members:


..  _optimisticlock:

OptimisticLock
--------------

.. autoclass:: aiocache.lock.OptimisticLock
  :members:
```

## File: docs/plugins.rst
```
..  _plugins:

Plugins
=======

Plugins can be used to enrich the behavior of the cache. By default all caches are configured without any plugin but can add new ones in the constructor or after initializing the cache class::

    >>> from aiocache import SimpleMemoryCache
    >>> from aiocache.plugins import TimingPlugin
    cache = SimpleMemoryCache(plugins=[HitMissRatioPlugin()])
    cache.plugins += [TimingPlugin()]

You can define your custom plugin by inheriting from `BasePlugin`_ and overriding the needed methods (the overrides NEED to be async). All commands have ``pre_<command_name>`` and ``post_<command_name>`` hooks.

.. WARNING::
  Both pre and post hooks are executed awaiting the coroutine. If you perform expensive operations with the hooks, you will add more latency to the command being executed and thus, there are more probabilities of raising a timeout error. If a timeout error is raised, be aware that previous actions **won't be rolled back**.

A complete example of using plugins:

.. literalinclude:: ../examples/plugins.py
  :language: python
  :linenos:


..  _baseplugin:

BasePlugin
----------

.. autoclass:: aiocache.plugins.BasePlugin
  :members:
  :undoc-members:

..  _timingplugin:

TimingPlugin
------------

.. autoclass:: aiocache.plugins.TimingPlugin
  :members:
  :undoc-members:

..  _hitmissratioplugin:

HitMissRatioPlugin
------------------

.. autoclass:: aiocache.plugins.HitMissRatioPlugin
  :members:
  :undoc-members:
```

## File: docs/serializers.rst
```
..  _serializers:

Serializers
===========

Serializers can be attached to backends in order to serialize/deserialize data sent and retrieved from the backend. This allows to apply transformations to data in case you want it to be saved in a specific format in your cache backend. For example, imagine you have your ``Model`` and want to serialize it to something that Redis can understand (Redis can't store python objects). This is the task of a serializer.

To use a specific serializer::

    >>> from aiocache import SimpleMemoryCache
    >>> from aiocache.serializers import PickleSerializer
    cache = SimpleMemoryCache(serializer=PickleSerializer())

Currently the following are built in:


..  _nullserializer:

NullSerializer
--------------
.. autoclass:: aiocache.serializers.NullSerializer
  :members:


..  _stringserializer:

StringSerializer
----------------

.. autoclass:: aiocache.serializers.StringSerializer
  :members:

..  _pickleserializer:

PickleSerializer
----------------

.. autoclass:: aiocache.serializers.PickleSerializer
  :members:

..  _jsonserializer:

JsonSerializer
--------------

.. autoclass:: aiocache.serializers.JsonSerializer
  :members:

..  _msgpackserializer:

MsgPackSerializer
-----------------

.. autoclass:: aiocache.serializers.MsgPackSerializer
  :members:

In case the current serializers are not covering your needs, you can always define your custom serializer as shown in ``examples/serializer_class.py``:

.. literalinclude:: ../examples/serializer_class.py
  :language: python
  :linenos:

You can also use marshmallow as your serializer (``examples/marshmallow_serializer_class.py``):

.. literalinclude:: ../examples/marshmallow_serializer_class.py
  :language: python
  :linenos:

By default cache backends assume they are working with ``str`` types. If your custom implementation transform data to bytes, you will need to set the class attribute ``encoding`` to ``None``.
```

## File: docs/testing.rst
```
Testing
=======

It's really easy to cut the dependency with aiocache functionality:

..  literalinclude:: ../examples/testing.py

Note that we are passing the :ref:`basecache` as the spec for the Mock.

Also, for debuging purposes you can use `AIOCACHE_DISABLE = 1 python myscript.py` to disable caching.
```

## File: docs/v1_migration.rst
```
..  _v1_migration:

Migrating from v0.x to v1
======

The v1 release of aiocache is a major release that introduces several breaking changes.

Changes to Cache Instantiation
---------

The abstraction and factories around cache instantiation have been removed in favor of a more direct approach.

* The `aiocache.Cache` class has been removed. Instead, use the specific cache class directly. For example, use `aiocache.RedisCache` instead of `aiocache.Cache.REDIS`.
* Caches should be fully instantiated when passed to decorators, rather than being instantiated with a factory function.
* Cache aliases have been removed. Create an instance of the cache class directly instead.
```
