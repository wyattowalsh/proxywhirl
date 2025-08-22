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
  abc.rst
  built_with.rst
  changes.rst
  client_middleware_cookbook.rst
  client_quickstart.rst
  client_reference.rst
  client.rst
  contributing-admins.rst
  contributing.rst
  deployment.rst
  essays.rst
  external.rst
  faq.rst
  glossary.rst
  http_request_lifecycle.rst
  index.rst
  logging.rst
  migration_to_2xx.rst
  misc.rst
  multipart_reference.rst
  multipart.rst
  new_router.rst
  powered_by.rst
  spelling_wordlist.txt
  streams.rst
  structures.rst
  testing.rst
  third_party.rst
  tracing_reference.rst
  utilities.rst
  web_advanced.rst
  web_exceptions.rst
  web_lowlevel.rst
  web_quickstart.rst
  web_reference.rst
  web.rst
  websocket_utilities.rst
  whats_new_1_1.rst
  whats_new_3_0.rst
```

# Files

## File: docs/abc.rst
````
.. module:: aiohttp.abc

.. _aiohttp-abc:

Abstract Base Classes
=====================

Abstract routing
----------------

aiohttp has abstract classes for managing web interfaces.

The most part of :mod:`aiohttp.web` is not intended to be inherited
but few of them are.

aiohttp.web is built on top of few concepts: *application*, *router*,
*request* and *response*.

*router* is a *pluggable* part: a library user may build a *router*
from scratch, all other parts should work with new router seamlessly.

:class:`aiohttp.abc.AbstractRouter` has the only mandatory method:
:meth:`aiohttp.abc.AbstractRouter.resolve` coroutine. It must return an
:class:`aiohttp.abc.AbstractMatchInfo` instance.

If the requested URL handler is found
:meth:`aiohttp.abc.AbstractMatchInfo.handler` is a :term:`web-handler` for
requested URL and :attr:`aiohttp.abc.AbstractMatchInfo.http_exception` is ``None``.

Otherwise :attr:`aiohttp.abc.AbstractMatchInfo.http_exception` is an instance of
:exc:`~aiohttp.web.HTTPException` like *404: NotFound* or *405: Method
Not Allowed*. :meth:`aiohttp.abc.AbstractMatchInfo.handler` raises
:attr:`~aiohttp.abc.AbstractMatchInfo.http_exception` on call.


.. class:: AbstractRouter

   Abstract router, :class:`aiohttp.web.Application` accepts it as
   *router* parameter and returns as
   :attr:`aiohttp.web.Application.router`.

   .. method:: resolve(request)
      :async:

      Performs URL resolving. It's an abstract method, should be
      overridden in *router* implementation.

      :param request: :class:`aiohttp.web.Request` instance for
                      resolving, the request has
                      :attr:`aiohttp.web.Request.match_info` equals to
                      ``None`` at resolving stage.

      :return: :class:`aiohttp.abc.AbstractMatchInfo` instance.


.. class:: AbstractMatchInfo

   Abstract *match info*, returned by :meth:`aiohttp.abc.AbstractRouter.resolve` call.

   .. attribute:: http_exception

      :exc:`aiohttp.web.HTTPException` if no match was found, ``None``
      otherwise.

   .. method:: handler(request)
      :async:

      Abstract method performing :term:`web-handler` processing.

      :param request: :class:`aiohttp.web.Request` instance for
                      resolving, the request has
                      :attr:`aiohttp.web.Request.match_info` equals to
                      ``None`` at resolving stage.
      :return: :class:`aiohttp.web.StreamResponse` or descendants.

      :raise: :class:`aiohttp.web.HTTPException` on error

   .. method:: expect_handler(request)
      :async:

      Abstract method for handling *100-continue* processing.


Abstract Class Based Views
--------------------------

For *class based view* support aiohttp has abstract
:class:`AbstractView` class which is *awaitable* (may be uses like
``await Cls()`` or ``yield from Cls()`` and has a *request* as an
attribute.

.. class:: AbstractView

   An abstract class, base for all *class based views* implementations.

   Methods ``__iter__`` and ``__await__`` should be overridden.

   .. attribute:: request

      :class:`aiohttp.web.Request` instance for performing the request.


Abstract Cookie Jar
-------------------

.. class:: AbstractCookieJar

   The cookie jar instance is available as :attr:`aiohttp.ClientSession.cookie_jar`.

   The jar contains :class:`~http.cookies.Morsel` items for storing
   internal cookie data.

   API provides a count of saved cookies::

       len(session.cookie_jar)

   These cookies may be iterated over::

       for cookie in session.cookie_jar:
           print(cookie.key)
           print(cookie["domain"])

   An abstract class for cookie storage. Implements
   :class:`collections.abc.Iterable` and
   :class:`collections.abc.Sized`.

   .. method:: update_cookies(cookies, response_url=None)

      Update cookies returned by server in ``Set-Cookie`` header.

      :param cookies: a :class:`collections.abc.Mapping`
         (e.g. :class:`dict`, :class:`~http.cookies.SimpleCookie`) or
         *iterable* of *pairs* with cookies returned by server's
         response.

      :param str response_url: URL of response, ``None`` for *shared
         cookies*.  Regular cookies are coupled with server's URL and
         are sent only to this server, shared ones are sent in every
         client request.

   .. method:: filter_cookies(request_url)

      Return jar's cookies acceptable for URL and available in
      ``Cookie`` header for sending client requests for given URL.

      :param str response_url: request's URL for which cookies are asked.

      :return: :class:`http.cookies.SimpleCookie` with filtered
         cookies for given URL.

   .. method:: clear(predicate=None)

      Removes all cookies from the jar if the predicate is ``None``. Otherwise remove only those :class:`~http.cookies.Morsel` that ``predicate(morsel)`` returns ``True``.

      :param predicate: callable that gets :class:`~http.cookies.Morsel` as a parameter and returns ``True`` if this :class:`~http.cookies.Morsel` must be deleted from the jar.

          .. versionadded:: 3.8

   .. method:: clear_domain(domain)

      Remove all cookies from the jar that belongs to the specified domain or its subdomains.

      :param str domain: domain for which cookies must be deleted from the jar.

      .. versionadded:: 3.8

Abstract Access Logger
-------------------------------

.. class:: AbstractAccessLogger

   An abstract class, base for all :class:`aiohttp.web.RequestHandler`
   ``access_logger`` implementations

   Method ``log`` should be overridden.

   .. method:: log(request, response, time)

      :param request: :class:`aiohttp.web.Request` object.

      :param response: :class:`aiohttp.web.Response` object.

      :param float time: Time taken to serve the request.

   .. attribute:: enabled

        Return True if logger is enabled.

        Override this property if logging is disabled to avoid the
        overhead of calculating details to feed the logger.

        This property may be omitted if logging is always enabled.


Abstract Resolver
-------------------------------

.. class:: AbstractResolver

   An abstract class, base for all resolver implementations.

   Method ``resolve`` should be overridden.

   .. method:: resolve(host, port, family)

      Resolve host name to IP address.

      :param str host: host name to resolve.

      :param int port: port number.

      :param int family: socket family.

      :return: list of :class:`aiohttp.abc.ResolveResult` instances.

   .. method:: close()

      Release resolver.

.. class:: ResolveResult

   Result of host name resolution.

   .. attribute:: hostname

      The host name that was provided.

   .. attribute:: host

      The IP address that was resolved.

   .. attribute:: port

      The port that was resolved.

   .. attribute:: family

      The address family that was resolved.

   .. attribute:: proto

      The protocol that was resolved.

   .. attribute:: flags

      The flags that were resolved.
````

## File: docs/built_with.rst
````
.. _aiohttp-built-with:

Built with aiohttp
==================

aiohttp is used to build useful libraries built on top of it,
and there's a page dedicated to list them: :ref:`aiohttp-3rd-party`.

There are also projects that leverage the power of aiohttp to
provide end-user tools, like command lines or software with
full user interfaces.

This page aims to list those projects. If you are using aiohttp
in your software and if it's playing a central role, you
can add it here in this list.

You can also add a **Built with aiohttp** link somewhere in your
project, pointing to `<https://github.com/aio-libs/aiohttp>`_.


* `Pulp <https://pulpproject.org>`_ Platform for managing repositories
  of software packages and making them available to consumers.
* `repo-peek <https://github.com/rahulunair/repo-peek>`_ CLI tool to open a remote repo locally quickly.
* `Molotov <http://molotov.readthedocs.io>`_ Load testing tool.
* `Arsenic <https://github.com/hde/arsenic>`_ Async WebDriver.
* `Home Assistant <https://home-assistant.io>`_ Home Automation Platform.
* `Backend.AI <https://backend.ai>`_ Code execution API service.
* `doh-proxy <https://github.com/facebookexperimental/doh-proxy>`_ DNS Over HTTPS Proxy.
* `Mariner <https://gitlab.com/radek-sprta/mariner>`_ Command-line torrent searcher.
* `DEEPaaS API <https://github.com/indigo-dc/DEEPaaS>`_ REST API for Machine learning, Deep learning and artificial intelligence applications.
* `BentoML <https://github.com/bentoml/BentoML>`_ Machine Learning model serving framework
* `salted <https://github.com/RuedigerVoigt/salted>`_ fast link check library (for HTML, Markdown, LaTeX, ...) with CLI
* `Unofficial Tabdeal API <https://github.com/MohsenHNSJ/unofficial_tabdeal_api>`_ A package to communicate with the *Tabdeal* trading platform.
````

## File: docs/changes.rst
````
.. _aiohttp_changes:

=========
Changelog
=========

.. only:: not is_release

   To be included in v\ |release| (if present)
   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   .. towncrier-draft-entries:: |release| [UNRELEASED DRAFT]

   Released versions
   ^^^^^^^^^^^^^^^^^

.. include:: ../CHANGES.rst
   :start-after: .. towncrier release notes start
````

## File: docs/client_middleware_cookbook.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-client-middleware-cookbook:

Client Middleware Cookbook
==========================

This cookbook provides examples of how client middlewares can be used for common use cases.

Simple Retry Middleware
-----------------------

It's very easy to create middlewares that can retry a connection on a given condition:

.. literalinclude:: code/client_middleware_cookbook.py
   :pyobject: retry_middleware

.. warning::

    It is recommended to ensure loops are bounded (e.g. using a ``for`` loop) to avoid
    creating an infinite loop.

Logging to an external service
------------------------------

If we needed to log our requests via an API call to an external server or similar, we could
create a simple middleware like this:

.. literalinclude:: code/client_middleware_cookbook.py
   :pyobject: api_logging_middleware

.. warning::

    Using the same session from within a middleware can cause infinite recursion if
    that request gets processed again by the middleware.

    To avoid such recursion a middleware should typically make requests with
    ``middlewares=()`` or else contain some condition to stop the request triggering
    the same logic when it is processed again by the middleware (e.g by whitelisting
    the API domain of the request).

Token Refresh Middleware
------------------------

If you need to refresh access tokens to continue accessing an API, this is also a good
candidate for a middleware. For example, you could check for a 401 response, then
refresh the token and retry:

.. literalinclude:: code/client_middleware_cookbook.py
   :pyobject: TokenRefresh401Middleware

If you have an expiry time for the token, you could refresh at the expiry time, to avoid the
failed request:

.. literalinclude:: code/client_middleware_cookbook.py
   :pyobject: TokenRefreshExpiryMiddleware

Or you could even refresh preemptively in a background task to avoid any API delays. This is probably more
efficient to implement without a middleware:

.. literalinclude:: code/client_middleware_cookbook.py
   :pyobject: token_refresh_preemptively_example

Or combine the above approaches to create a more robust solution.

.. note::

    These can also be adjusted to handle proxy auth by modifying
    :attr:`ClientRequest.proxy_headers`.

Server-side Request Forgery Protection
--------------------------------------

To provide protection against server-side request forgery, we could blacklist any internal
IPs or domains. We could create a middleware that rejects requests made to a blacklist:

.. literalinclude:: code/client_middleware_cookbook.py
   :pyobject: ssrf_middleware

.. warning::

   The above example is simplified for demonstration purposes. A production-ready
   implementation should also check IPv6 addresses (``::1``), private IP ranges,
   link-local addresses, and other internal hostnames. Consider using a well-tested
   library for SSRF protection in production environments.

If you know that your services correctly reject requests with an incorrect `Host` header, then
that may provide sufficient protection. Otherwise, we still have a concern with an attacker's
own domain resolving to a blacklisted IP. To provide complete protection, we can also
create a custom resolver:

.. literalinclude:: code/client_middleware_cookbook.py
   :pyobject: SSRFConnector

Using both of these together in a session should provide full SSRF protection.


Best Practices
--------------

1. **Keep middleware focused**: Each middleware should have a single responsibility.

2. **Order matters**: Middlewares execute in the order they're listed. Place logging first,
   authentication before retry, etc.

3. **Avoid infinite recursion**: When making HTTP requests inside middleware, either:

   - Use ``middlewares=()`` to disable middleware for internal requests
   - Check the request URL/host to skip middleware for specific endpoints
   - Use a separate session for internal requests

4. **Handle errors gracefully**: Don't let middleware errors break the request flow unless
   absolutely necessary.

5. **Use bounded loops**: Always use ``for`` loops with a maximum iteration count instead
   of unbounded ``while`` loops to prevent infinite retries.

6. **Consider performance**: Each middleware adds overhead. For simple cases like adding
   static headers, consider using session or request parameters instead.

7. **Test thoroughly**: Middleware can affect all requests in subtle ways. Test edge cases
   like network errors, timeouts, and concurrent requests.

See Also
--------

- :ref:`aiohttp-client-middleware` - Core middleware documentation
- :ref:`aiohttp-client-advanced` - Advanced client usage
- :class:`DigestAuthMiddleware` - Built-in digest authentication middleware
````

## File: docs/client_quickstart.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-client-quickstart:

===================
 Client Quickstart
===================

Eager to get started? This page gives a good introduction in how to
get started with aiohttp client API.

First, make sure that aiohttp is :ref:`installed
<aiohttp-installation>` and *up-to-date*

Let's get started with some simple examples.



Make a Request
==============

Begin by importing the aiohttp module, and asyncio::

    import aiohttp
    import asyncio

Now, let's try to get a web-page. For example let's query
``http://httpbin.org/get``::

    async def main():
        async with aiohttp.ClientSession() as session:
            async with session.get('http://httpbin.org/get') as resp:
                print(resp.status)
                print(await resp.text())

    asyncio.run(main())

Now, we have a :class:`ClientSession` called ``session`` and a
:class:`ClientResponse` object called ``resp``. We can get all the
information we need from the response.  The mandatory parameter of
:meth:`ClientSession.get` coroutine is an HTTP *url* (:class:`str` or
class:`yarl.URL` instance).

In order to make an HTTP POST request use :meth:`ClientSession.post` coroutine::

    session.post('http://httpbin.org/post', data=b'data')

Other HTTP methods are available as well::

    session.put('http://httpbin.org/put', data=b'data')
    session.delete('http://httpbin.org/delete')
    session.head('http://httpbin.org/get')
    session.options('http://httpbin.org/get')
    session.patch('http://httpbin.org/patch', data=b'data')

To make several requests to the same site more simple, the parameter ``base_url``
of :class:`ClientSession` constructor can be used. For example to request different
endpoints of ``http://httpbin.org`` can be used the following code::

    async with aiohttp.ClientSession('http://httpbin.org') as session:
        async with session.get('/get'):
            pass
        async with session.post('/post', data=b'data'):
            pass
        async with session.put('/put', data=b'data'):
            pass

.. note::

   Don't create a session per request. Most likely you need a session
   per application which performs all requests together.

   More complex cases may require a session per site, e.g. one for
   Github and other one for Facebook APIs. Anyway making a session for
   every request is a **very bad** idea.

   A session contains a connection pool inside. Connection reusage and
   keep-alive (both are on by default) may speed up total performance.

   You may find more information about creating persistent sessions
   in :ref:`aiohttp-persistent-session`.

A session context manager usage is not mandatory
but ``await session.close()`` method
should be called in this case, e.g.::

    session = aiohttp.ClientSession()
    async with session.get('...'):
        # ...
    await session.close()


Passing Parameters In URLs
==========================

You often want to send some sort of data in the URL's query string. If
you were constructing the URL by hand, this data would be given as key/value
pairs in the URL after a question mark, e.g. ``httpbin.org/get?key=val``.
aiohttp allows you to provide these arguments as a :class:`dict`, using the
``params`` keyword argument. As an example, if you wanted to pass
``key1=value1`` and ``key2=value2`` to ``httpbin.org/get``, you would use the
following code::

    params = {'key1': 'value1', 'key2': 'value2'}
    async with session.get('http://httpbin.org/get',
                           params=params) as resp:
        expect = 'http://httpbin.org/get?key1=value1&key2=value2'
        assert str(resp.url) == expect

You can see that the URL has been correctly encoded by printing the URL.

For sending data with multiple values for the same key
:class:`~multidict.MultiDict` may be used; the library support nested lists
(``{'key': ['value1', 'value2']}``) alternative as well.

It is also possible to pass a list of 2 item tuples as parameters, in
that case you can specify multiple values for each key::

    params = [('key', 'value1'), ('key', 'value2')]
    async with session.get('http://httpbin.org/get',
                           params=params) as r:
        expect = 'http://httpbin.org/get?key=value2&key=value1'
        assert str(r.url) == expect

You can also pass :class:`str` content as param, but beware -- content
is not encoded by library. Note that ``+`` is not encoded::

    async with session.get('http://httpbin.org/get',
                           params='key=value+1') as r:
            assert str(r.url) == 'http://httpbin.org/get?key=value+1'

.. note::

   *aiohttp* internally performs URL canonicalization before sending request.

   Canonicalization encodes *host* part by :term:`IDNA` codec and applies
   :term:`requoting` to *path* and *query* parts.

   For example ``URL('http://example.com/путь/%30?a=%31')`` is converted to
   ``URL('http://example.com/%D0%BF%D1%83%D1%82%D1%8C/0?a=1')``.

   Sometimes canonicalization is not desirable if server accepts exact
   representation and does not requote URL itself.

   To disable canonicalization use ``encoded=True`` parameter for URL construction::

      await session.get(
          URL('http://example.com/%30', encoded=True))

.. warning::

   Passing *params* overrides ``encoded=True``, never use both options.

Response Content and Status Code
================================

We can read the content of the server's response and its status
code. Consider the GitHub time-line again::

    async with session.get('https://api.github.com/events') as resp:
        print(resp.status)
        print(await resp.text())

prints out something like::

    200
    '[{"created_at":"2015-06-12T14:06:22Z","public":true,"actor":{...

``aiohttp`` automatically decodes the content from the server. You can
specify custom encoding for the :meth:`~ClientResponse.text` method::

    await resp.text(encoding='windows-1251')


Binary Response Content
=======================

You can also access the response body as bytes, for non-text requests::

    print(await resp.read())

::

    b'[{"created_at":"2015-06-12T14:06:22Z","public":true,"actor":{...

The ``gzip`` and ``deflate`` transfer-encodings are automatically
decoded for you.

You can enable ``brotli`` transfer-encodings support,
just install `Brotli <https://pypi.org/project/Brotli/>`_
or `brotlicffi <https://pypi.org/project/brotlicffi/>`_.

You can enable ``zstd`` transfer-encodings support,
install `zstandard <https://pypi.org/project/zstandard/>`_.
If you are using Python >= 3.14, no dependency should be required.

JSON Request
============

Any of session's request methods like :func:`request`,
:meth:`ClientSession.get`, :meth:`ClientSession.post` etc. accept
`json` parameter::

  async with aiohttp.ClientSession() as session:
      await session.post(url, json={'test': 'object'})


By default session uses python's standard :mod:`json` module for
serialization.  But it is possible to use different
``serializer``. :class:`ClientSession` accepts ``json_serialize``
parameter::

  import ujson

  async with aiohttp.ClientSession(
          json_serialize=ujson.dumps) as session:
      await session.post(url, json={'test': 'object'})

.. note::

   ``ujson`` library is faster than standard :mod:`json` but slightly
   incompatible.

JSON Response Content
=====================

There's also a built-in JSON decoder, in case you're dealing with JSON data::

    async with session.get('https://api.github.com/events') as resp:
        print(await resp.json())

In case that JSON decoding fails, :meth:`~ClientResponse.json` will
raise an exception. It is possible to specify custom encoding and
decoder functions for the :meth:`~ClientResponse.json` call.

.. note::

    The methods above reads the whole response body into memory. If you are
    planning on reading lots of data, consider using the streaming response
    method documented below.


Streaming Response Content
==========================

While methods :meth:`~ClientResponse.read`,
:meth:`~ClientResponse.json` and :meth:`~ClientResponse.text` are very
convenient you should use them carefully. All these methods load the
whole response in memory.  For example if you want to download several
gigabyte sized files, these methods will load all the data in
memory. Instead you can use the :attr:`~ClientResponse.content`
attribute. It is an instance of the :class:`aiohttp.StreamReader`
class. The ``gzip`` and ``deflate`` transfer-encodings are
automatically decoded for you::

    async with session.get('https://api.github.com/events') as resp:
        await resp.content.read(10)

In general, however, you should use a pattern like this to save what is being
streamed to a file::

    with open(filename, 'wb') as fd:
        async for chunk in resp.content.iter_chunked(chunk_size):
            fd.write(chunk)

It is not possible to use :meth:`~ClientResponse.read`,
:meth:`~ClientResponse.json` and :meth:`~ClientResponse.text` after
explicit reading from :attr:`~ClientResponse.content`.

More complicated POST requests
==============================

Typically, you want to send some form-encoded data -- much like an HTML form.
To do this, simply pass a dictionary to the *data* argument. Your
dictionary of data will automatically be form-encoded when the request is made::

    payload = {'key1': 'value1', 'key2': 'value2'}
    async with session.post('http://httpbin.org/post',
                            data=payload) as resp:
        print(await resp.text())

::

    {
      ...
      "form": {
        "key2": "value2",
        "key1": "value1"
      },
      ...
    }

If you want to send data that is not form-encoded you can do it by
passing a :class:`bytes` instead of a :class:`dict`. This data will be
posted directly and content-type set to 'application/octet-stream' by
default::

    async with session.post(url, data=b'\x00Binary-data\x00') as resp:
        ...

If you want to send JSON data::

    async with session.post(url, json={'example': 'test'}) as resp:
        ...

To send text with appropriate content-type just use ``data`` argument::

    async with session.post(url, data='Тест') as resp:
        ...

POST a Multipart-Encoded File
=============================

To upload Multipart-encoded files::

    url = 'http://httpbin.org/post'
    files = {'file': open('report.xls', 'rb')}

    await session.post(url, data=files)

You can set the ``filename`` and ``content_type`` explicitly::

    url = 'http://httpbin.org/post'
    data = aiohttp.FormData()
    data.add_field('file',
                   open('report.xls', 'rb'),
                   filename='report.xls',
                   content_type='application/vnd.ms-excel')

    await session.post(url, data=data)

If you pass a file object as data parameter, aiohttp will stream it to
the server automatically. Check :class:`~aiohttp.StreamReader`
for supported format information.

.. seealso:: :ref:`aiohttp-multipart`


Streaming uploads
=================

:mod:`aiohttp` supports multiple types of streaming uploads, which allows you to
send large files without reading them into memory.

As a simple case, simply provide a file-like object for your body::

    with open('massive-body', 'rb') as f:
       await session.post('http://httpbin.org/post', data=f)


Or you can use *asynchronous generator*::

  async def file_sender(file_name=None):
      async with aiofiles.open(file_name, 'rb') as f:
          chunk = await f.read(64*1024)
          while chunk:
              yield chunk
              chunk = await f.read(64*1024)

  # Then you can use file_sender as a data provider:

  async with session.post('http://httpbin.org/post',
                          data=file_sender(file_name='huge_file')) as resp:
      print(await resp.text())


Because the :attr:`~aiohttp.ClientResponse.content` attribute is a
:class:`~aiohttp.StreamReader` (provides async iterator protocol), you
can chain get and post requests together::

   resp = await session.get('http://python.org')
   await session.post('http://httpbin.org/post',
                      data=resp.content)

.. _aiohttp-client-websockets:


WebSockets
==========

:mod:`aiohttp` works with client websockets out-of-the-box.

You have to use the :meth:`aiohttp.ClientSession.ws_connect` coroutine
for client websocket connection. It accepts a *url* as a first
parameter and returns :class:`ClientWebSocketResponse`, with that
object you can communicate with websocket server using response's
methods::

   async with session.ws_connect('http://example.org/ws') as ws:
       async for msg in ws:
           if msg.type == aiohttp.WSMsgType.TEXT:
               if msg.data == 'close cmd':
                   await ws.close()
                   break
               else:
                   await ws.send_str(msg.data + '/answer')
           elif msg.type == aiohttp.WSMsgType.ERROR:
               break


You **must** use the only websocket task for both reading (e.g. ``await
ws.receive()`` or ``async for msg in ws:``) and writing but may have
multiple writer tasks which can only send data asynchronously (by
``await ws.send_str('data')`` for example).


.. _aiohttp-client-timeouts:

Timeouts
========

Timeout settings are stored in :class:`ClientTimeout` data structure.

By default *aiohttp* uses a *total* 300 seconds (5min) timeout, it means that the
whole operation should finish in 5 minutes. In order to allow time for DNS fallback,
the default ``sock_connect`` timeout is 30 seconds.

The value could be overridden by *timeout* parameter for the session (specified in seconds)::

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        ...

Timeout could be overridden for a request like :meth:`ClientSession.get`::

    async with session.get(url, timeout=timeout) as resp:
        ...

Supported :class:`ClientTimeout` fields are:

   ``total``

      The maximal number of seconds for the whole operation including connection
      establishment, request sending and response reading.

   ``connect``

      The maximal number of seconds for
      connection establishment of a new connection or
      for waiting for a free connection from a pool if pool connection
      limits are exceeded.

   ``sock_connect``

      The maximal number of seconds for connecting to a peer for a new connection, not
      given from a pool.

   ``sock_read``

      The maximal number of seconds allowed for period between reading a new
      data portion from a peer.

    ``ceil_threshold``

      The threshold value to trigger ceiling of absolute timeout values.

All fields are floats, ``None`` or ``0`` disables a particular timeout check, see the
:class:`ClientTimeout` reference for defaults and additional details.

Thus the default timeout is::

   aiohttp.ClientTimeout(total=5*60, connect=None,
                         sock_connect=None, sock_read=None, ceil_threshold=5)

.. note::

   *aiohttp* **ceils** timeout if the value is equal or greater than 5
   seconds. The timeout expires at the next integer second greater than
   ``current_time + timeout``.

   The ceiling is done for the sake of optimization, when many concurrent tasks
   are scheduled to wake-up at the almost same but different absolute times. It
   leads to very many event loop wakeups, which kills performance.

   The optimization shifts absolute wakeup times by scheduling them to exactly
   the same time as other neighbors, the loop wakes up once-per-second for
   timeout expiration.

   Smaller timeouts are not rounded to help testing; in the real life network
   timeouts usually greater than tens of seconds. However, the default threshold
   value of 5 seconds can be configured using the ``ceil_threshold`` parameter.
````

## File: docs/client_reference.rst
````
.. _aiohttp-client-reference:

Client Reference
================

.. currentmodule:: aiohttp


Client Session
--------------

Client session is the recommended interface for making HTTP requests.

Session encapsulates a *connection pool* (*connector* instance) and
supports keepalives by default. Unless you are connecting to a large,
unknown number of different servers over the lifetime of your
application, it is suggested you use a single session for the
lifetime of your application to benefit from connection pooling.

Usage example::

     import aiohttp
     import asyncio

     async def fetch(client):
         async with client.get('http://python.org') as resp:
             assert resp.status == 200
             return await resp.text()

     async def main():
         async with aiohttp.ClientSession() as client:
             html = await fetch(client)
             print(html)

     asyncio.run(main())


The client session supports the context manager protocol for self closing.

.. class:: ClientSession(base_url=None, *, \
                         connector=None, cookies=None, \
                         headers=None, skip_auto_headers=None, \
                         auth=None, json_serialize=json.dumps, \
                         request_class=ClientRequest, \
                         response_class=ClientResponse, \
                         ws_response_class=ClientWebSocketResponse, \
                         version=aiohttp.HttpVersion11, \
                         cookie_jar=None, \
                         connector_owner=True, \
                         raise_for_status=False, \
                         timeout=sentinel, \
                         auto_decompress=True, \
                         trust_env=False, \
                         requote_redirect_url=True, \
                         trace_configs=None, \
                         middlewares=(), \
                         read_bufsize=2**16, \
                         max_line_size=8190, \
                         max_field_size=8190, \
                         fallback_charset_resolver=lambda r, b: "utf-8", \
                         ssl_shutdown_timeout=0)

   The class for creating client sessions and making requests.


   :param base_url: Base part of the URL (optional)
      If set, allows to join a base part to relative URLs in request calls.
      If the URL has a path it must have a trailing ``/`` (as in
      https://docs.aiohttp.org/en/stable/).

      Note that URL joining follows :rfc:`3986`. This means, in the most
      common case the request URLs should have no leading slash, e.g.::

        session = ClientSession(base_url="http://example.com/foo/")

        await session.request("GET", "bar")
        # request for http://example.com/foo/bar

        await session.request("GET", "/bar")
        # request for http://example.com/bar

      .. versionadded:: 3.8

      .. versionchanged:: 3.12

         Added support for overriding the base URL with an absolute one in client sessions.

   :param aiohttp.BaseConnector connector: BaseConnector
      sub-class instance to support connection pooling.

   :param dict cookies: Cookies to send with the request (optional)

   :param headers: HTTP Headers to send with every request (optional).

                   May be either *iterable of key-value pairs* or
                   :class:`~collections.abc.Mapping`
                   (e.g. :class:`dict`,
                   :class:`~multidict.CIMultiDict`).

   :param skip_auto_headers: set of headers for which autogeneration
      should be skipped.

      *aiohttp* autogenerates headers like ``User-Agent`` or
      ``Content-Type`` if these headers are not explicitly
      passed. Using ``skip_auto_headers`` parameter allows to skip
      that generation. Note that ``Content-Length`` autogeneration can't
      be skipped.

      Iterable of :class:`str` or :class:`~multidict.istr` (optional)

   :param aiohttp.BasicAuth auth: an object that represents HTTP Basic
                                  Authorization (optional). It will be included
                                  with any request. However, if the
                                  ``_base_url`` parameter is set, the request
                                  URL's origin must match the base URL's origin;
                                  otherwise, the default auth will not be
                                  included.

   :param collections.abc.Callable json_serialize: Json *serializer* callable.

      By default :func:`json.dumps` function.

   :param aiohttp.ClientRequest request_class: Custom class to use for client requests.

   :param ClientResponse response_class: Custom class to use for client responses.

   :param ClientWebSocketResponse ws_response_class: Custom class to use for websocket responses.

   :param version: supported HTTP version, ``HTTP 1.1`` by default.

   :param cookie_jar: Cookie Jar, :class:`~aiohttp.abc.AbstractCookieJar` instance.

      By default every session instance has own private cookie jar for
      automatic cookies processing but user may redefine this behavior
      by providing own jar implementation.

      One example is not processing cookies at all when working in
      proxy mode.

      If no cookie processing is needed, a
      :class:`aiohttp.DummyCookieJar` instance can be
      provided.

   :param bool connector_owner:

      Close connector instance on session closing.

      Setting the parameter to ``False`` allows to share
      connection pool between sessions without sharing session state:
      cookies etc.

   :param bool raise_for_status:

      Automatically call :meth:`ClientResponse.raise_for_status` for
      each response, ``False`` by default.

      This parameter can be overridden when making a request, e.g.::

          client_session = aiohttp.ClientSession(raise_for_status=True)
          resp = await client_session.get(url, raise_for_status=False)
          async with resp:
              assert resp.status == 200

      Set the parameter to ``True`` if you need ``raise_for_status``
      for most of cases but override ``raise_for_status`` for those
      requests where you need to handle responses with status 400 or
      higher.

   :param timeout: a :class:`ClientTimeout` settings structure, 300 seconds (5min)
        total timeout, 30 seconds socket connect timeout by default.

      .. versionadded:: 3.3

      .. versionchanged:: 3.10.9

         The default value for the ``sock_connect`` timeout has been changed to 30 seconds.

   :param bool auto_decompress: Automatically decompress response body (``True`` by default).

      .. versionadded:: 2.3

   :param bool trust_env: Trust environment settings for proxy configuration if the parameter
      is ``True`` (``False`` by default). See :ref:`aiohttp-client-proxy-support` for
      more information.

      Get proxy credentials from ``~/.netrc`` file if present.

      Get HTTP Basic Auth credentials from :file:`~/.netrc` file if present.

      If :envvar:`NETRC` environment variable is set, read from file specified
      there rather than from :file:`~/.netrc`.

      .. seealso::

         ``.netrc`` documentation: https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html

      .. versionadded:: 2.3

      .. versionchanged:: 3.0

         Added support for ``~/.netrc`` file.

      .. versionchanged:: 3.9

         Added support for reading HTTP Basic Auth credentials from :file:`~/.netrc` file.

   :param bool requote_redirect_url: Apply *URL requoting* for redirection URLs if
                                     automatic redirection is enabled (``True`` by
                                     default).

      .. versionadded:: 3.5

   :param trace_configs: A list of :class:`TraceConfig` instances used for client
                         tracing.  ``None`` (default) is used for request tracing
                         disabling.  See :ref:`aiohttp-client-tracing-reference` for
                         more information.

   :param middlewares: A sequence of middleware instances to apply to all session requests.
                      Each middleware must match the :type:`ClientMiddlewareType` signature.
                      ``()`` (empty tuple, default) is used when no middleware is needed.
                      See :ref:`aiohttp-client-middleware` for more information.

      .. versionadded:: 3.12

   :param int read_bufsize: Size of the read buffer (:attr:`ClientResponse.content`).
                            64 KiB by default.

      .. versionadded:: 3.7

   :param int max_line_size: Maximum allowed size of lines in responses.

   :param int max_field_size: Maximum allowed size of header fields in responses.

   :param Callable[[ClientResponse,bytes],str] fallback_charset_resolver:
      A :term:`callable` that accepts a :class:`ClientResponse` and the
      :class:`bytes` contents, and returns a :class:`str` which will be used as
      the encoding parameter to :meth:`bytes.decode()`.

      This function will be called when the charset is not known (e.g. not specified in the
      Content-Type header). The default function simply defaults to ``utf-8``.

      .. versionadded:: 3.8.6

   :param float ssl_shutdown_timeout: **(DEPRECATED)** This parameter is deprecated
      and will be removed in aiohttp 4.0. Grace period for SSL shutdown handshake on
      TLS connections when the connector is closed (``0`` seconds by default).
      By default (``0``), SSL connections are aborted immediately when the
      connector is closed, without performing the shutdown handshake. During
      normal operation, SSL connections use Python's default SSL shutdown
      behavior. Setting this to a positive value (e.g., ``0.1``) will perform
      a graceful shutdown when closing the connector, notifying the remote
      peer which can help prevent "connection reset" errors at the cost of
      additional cleanup time. This timeout is passed to the underlying
      :class:`TCPConnector` when one is created automatically.
      Note: On Python versions prior to 3.11, only a value of ``0`` is supported;
      other values will trigger a warning.

      .. versionadded:: 3.12.5

      .. versionchanged:: 3.12.11
         Changed default from ``0.1`` to ``0`` to abort SSL connections
         immediately when the connector is closed. Added support for
         ``ssl_shutdown_timeout=0`` on all Python versions. A :exc:`RuntimeWarning`
         is issued when non-zero values are passed on Python < 3.11.

      .. deprecated:: 3.12.11
         This parameter is deprecated and will be removed in aiohttp 4.0.

   .. attribute:: closed

      ``True`` if the session has been closed, ``False`` otherwise.

      A read-only property.

   .. attribute:: connector

      :class:`aiohttp.BaseConnector` derived instance used
      for the session.

      A read-only property.

   .. attribute:: cookie_jar

      The session cookies, :class:`~aiohttp.abc.AbstractCookieJar` instance.

      Gives access to cookie jar's content and modifiers.

      A read-only property.

   .. attribute:: requote_redirect_url

      aiohttp re quote's redirect urls by default, but some servers
      require exact url from location header. To disable *re-quote* system
      set :attr:`requote_redirect_url` attribute to ``False``.

      .. versionadded:: 2.1

      .. note:: This parameter affects all subsequent requests.

      .. deprecated:: 3.5

         The attribute modification is deprecated.

   .. attribute:: loop

      A loop instance used for session creation.

      A read-only property.

      .. deprecated:: 3.5

   .. attribute:: timeout

      Default client timeouts, :class:`ClientTimeout` instance.  The value can
      be tuned by passing *timeout* parameter to :class:`ClientSession`
      constructor.

      .. versionadded:: 3.7

   .. attribute:: headers

      HTTP Headers that sent with every request

      May be either *iterable of key-value pairs* or
      :class:`~collections.abc.Mapping`
      (e.g. :class:`dict`,
      :class:`~multidict.CIMultiDict`).

      .. versionadded:: 3.7

   .. attribute:: skip_auto_headers

      Set of headers for which autogeneration skipped.

      :class:`frozenset` of :class:`str` or :class:`~multidict.istr` (optional)

      .. versionadded:: 3.7

   .. attribute:: auth

      An object that represents HTTP Basic Authorization.

      :class:`~aiohttp.BasicAuth` (optional)

      .. versionadded:: 3.7

   .. attribute:: json_serialize

      Json serializer callable.

      By default :func:`json.dumps` function.

      .. versionadded:: 3.7

   .. attribute:: connector_owner

      Should connector be closed on session closing

      :class:`bool` (optional)

      .. versionadded:: 3.7

   .. attribute:: raise_for_status

      Should :meth:`ClientResponse.raise_for_status` be called for each response

      Either :class:`bool` or :class:`collections.abc.Callable`

      .. versionadded:: 3.7

   .. attribute:: auto_decompress

      Should the body response be automatically decompressed

      :class:`bool` default is ``True``

      .. versionadded:: 3.7

   .. attribute:: trust_env

      Trust environment settings for proxy configuration
      or ~/.netrc file if present. See :ref:`aiohttp-client-proxy-support` for
      more information.

      :class:`bool` default is ``False``

      .. versionadded:: 3.7

   .. attribute:: trace_configs

      A list of :class:`TraceConfig` instances used for client
      tracing.  ``None`` (default) is used for request tracing
      disabling.  See :ref:`aiohttp-client-tracing-reference` for more information.

      .. versionadded:: 3.7

   .. method:: request(method, url, *, params=None, data=None, json=None,\
                         cookies=None, headers=None, skip_auto_headers=None, \
                         auth=None, allow_redirects=True,\
                         max_redirects=10,\
                         compress=None, chunked=None, expect100=False, raise_for_status=None,\
                         read_until_eof=True, \
                         proxy=None, proxy_auth=None,\
                         timeout=sentinel, ssl=True, \
                         server_hostname=None, \
                         proxy_headers=None, \
                         trace_request_ctx=None, \
                         middlewares=None, \
                         read_bufsize=None, \
                         auto_decompress=None, \
                         max_line_size=None, \
                         max_field_size=None)
      :async:
      :noindexentry:

      Performs an asynchronous HTTP request. Returns a response object that
      should be used as an async context manager.

      :param str method: HTTP method

      :param url: Request URL, :class:`~yarl.URL` or :class:`str` that will
                  be encoded with :class:`~yarl.URL` (see :class:`~yarl.URL`
                  to skip encoding).

      :param params: Mapping, iterable of tuple of *key*/*value* pairs or
                     string to be sent as parameters in the query
                     string of the new request. Ignored for subsequent
                     redirected requests (optional)

                     Allowed values are:

                     - :class:`collections.abc.Mapping` e.g. :class:`dict`,
                       :class:`multidict.MultiDict` or
                       :class:`multidict.MultiDictProxy`
                     - :class:`collections.abc.Iterable` e.g. :class:`tuple` or
                       :class:`list`
                     - :class:`str` with preferably url-encoded content
                       (**Warning:** content will not be encoded by *aiohttp*)

      :param data: The data to send in the body of the request. This can be a
                   :class:`FormData` object or anything that can be passed into
                   :class:`FormData`, e.g. a dictionary, bytes, or file-like object.
                   (optional)

      :param json: Any json compatible python object
                   (optional). *json* and *data* parameters could not
                   be used at the same time.

      :param dict cookies: HTTP Cookies to send with
                           the request (optional)

         Global session cookies and the explicitly set cookies will be merged
         when sending the request.

         .. versionadded:: 3.5

      :param dict headers: HTTP Headers to send with
                           the request (optional)

      :param skip_auto_headers: set of headers for which autogeneration
         should be skipped.

         *aiohttp* autogenerates headers like ``User-Agent`` or
         ``Content-Type`` if these headers are not explicitly
         passed. Using ``skip_auto_headers`` parameter allows to skip
         that generation.

         Iterable of :class:`str` or :class:`~multidict.istr`
         (optional)

      :param aiohttp.BasicAuth auth: an object that represents HTTP
                                     Basic Authorization (optional)

      :param bool allow_redirects: Whether to process redirects or not.
         When ``True``, redirects are followed (up to ``max_redirects`` times)
         and logged into :attr:`ClientResponse.history` and ``trace_configs``.
         When ``False``, the original response is returned.
         ``True`` by default (optional).

      :param int max_redirects: Maximum number of redirects to follow.
         :exc:`TooManyRedirects` is raised if the number is exceeded.
         Ignored when ``allow_redirects=False``.
         ``10`` by default.

      :param bool compress: Set to ``True`` if request has to be compressed
         with deflate encoding. If `compress` can not be combined
         with a *Content-Encoding* and *Content-Length* headers.
         ``None`` by default (optional).

      :param int chunked: Enable chunked transfer encoding.
         It is up to the developer
         to decide how to chunk data streams. If chunking is enabled, aiohttp
         encodes the provided chunks in the "Transfer-encoding: chunked" format.
         If *chunked* is set, then the *Transfer-encoding* and *content-length*
         headers are disallowed. ``None`` by default (optional).

      :param bool expect100: Expect 100-continue response from server.
                             ``False`` by default (optional).

      :param bool raise_for_status: Automatically call :meth:`ClientResponse.raise_for_status` for
                                    response if set to ``True``.
                                    If set to ``None`` value from ``ClientSession`` will be used.
                                    ``None`` by default (optional).

          .. versionadded:: 3.4

      :param bool read_until_eof: Read response until EOF if response
                                  does not have Content-Length header.
                                  ``True`` by default (optional).

      :param proxy: Proxy URL, :class:`str` or :class:`~yarl.URL` (optional)

      :param aiohttp.BasicAuth proxy_auth: an object that represents proxy HTTP
                                           Basic Authorization (optional)

      :param int timeout: override the session's timeout.

         .. versionchanged:: 3.3

            The parameter is :class:`ClientTimeout` instance,
            :class:`float` is still supported for sake of backward
            compatibility.

            If :class:`float` is passed it is a *total* timeout (in seconds).

      :param ssl: SSL validation mode. ``True`` for default SSL check
                  (:func:`ssl.create_default_context` is used),
                  ``False`` for skip SSL certificate validation,
                  :class:`aiohttp.Fingerprint` for fingerprint
                  validation, :class:`ssl.SSLContext` for custom SSL
                  certificate validation.

                  Supersedes *verify_ssl*, *ssl_context* and
                  *fingerprint* parameters.

         .. versionadded:: 3.0

      :param str server_hostname: Sets or overrides the host name that the
         target server's certificate will be matched against.

         See :py:meth:`asyncio.loop.create_connection` for more information.

         .. versionadded:: 3.9

      :param collections.abc.Mapping proxy_headers: HTTP headers to send to the proxy if the
         parameter proxy has been provided.

         .. versionadded:: 2.3

      :param trace_request_ctx: Object used to give as a kw param for each new
        :class:`TraceConfig` object instantiated,
        used to give information to the
        tracers that is only available at request time.

         .. versionadded:: 3.0

      :param middlewares: A sequence of middleware instances to apply to this request only.
                         Each middleware must match the :type:`ClientMiddlewareType` signature.
                         ``None`` by default which uses session middlewares.
                         See :ref:`aiohttp-client-middleware` for more information.

         .. versionadded:: 3.12

      :param int read_bufsize: Size of the read buffer (:attr:`ClientResponse.content`).
                              ``None`` by default,
                              it means that the session global value is used.

          .. versionadded:: 3.7

      :param bool auto_decompress: Automatically decompress response body.
         Overrides :attr:`ClientSession.auto_decompress`.
         May be used to enable/disable auto decompression on a per-request basis.

      :param int max_line_size: Maximum allowed size of lines in responses.

      :param int max_field_size: Maximum allowed size of header fields in responses.

      :return ClientResponse: a :class:`client response <ClientResponse>`
         object.

   .. method:: get(url, *, allow_redirects=True, **kwargs)
      :async:

      Perform a ``GET`` request. Returns an async context manager.

      In order to modify inner
      :meth:`request<aiohttp.ClientSession.request>`
      parameters, provide `kwargs`.

      :param url: Request URL, :class:`str` or :class:`~yarl.URL`

      :param bool allow_redirects: Whether to process redirects or not.
         When ``True``, redirects are followed and logged into
         :attr:`ClientResponse.history`.
         When ``False``, the original response is returned.
         ``True`` by default (optional).

      :return ClientResponse: a :class:`client response
                              <ClientResponse>` object.

   .. method:: post(url, *, data=None, **kwargs)
      :async:

      Perform a ``POST`` request. Returns an async context manager.

      In order to modify inner
      :meth:`request<aiohttp.ClientSession.request>`
      parameters, provide `kwargs`.


      :param url: Request URL, :class:`str` or :class:`~yarl.URL`

      :param data: Data to send in the body of the request; see
                   :meth:`request<aiohttp.ClientSession.request>`
                   for details (optional)

      :return ClientResponse: a :class:`client response
                              <ClientResponse>` object.

   .. method:: put(url, *, data=None, **kwargs)
      :async:

      Perform a ``PUT`` request. Returns an async context manager.

      In order to modify inner
      :meth:`request<aiohttp.ClientSession.request>`
      parameters, provide `kwargs`.


      :param url: Request URL, :class:`str` or :class:`~yarl.URL`

      :param data: Data to send in the body of the request; see
                   :meth:`request<aiohttp.ClientSession.request>`
                   for details (optional)

      :return ClientResponse: a :class:`client response
                              <ClientResponse>` object.

   .. method:: delete(url, **kwargs)
      :async:

      Perform a ``DELETE`` request. Returns an async context manager.

      In order to modify inner
      :meth:`request<aiohttp.ClientSession.request>`
      parameters, provide `kwargs`.

      :param url: Request URL, :class:`str` or :class:`~yarl.URL`

      :return ClientResponse: a :class:`client response
                              <ClientResponse>` object.

   .. method:: head(url, *, allow_redirects=False, **kwargs)
      :async:

      Perform a ``HEAD`` request. Returns an async context manager.

      In order to modify inner
      :meth:`request<aiohttp.ClientSession.request>`
      parameters, provide `kwargs`.

      :param url: Request URL, :class:`str` or :class:`~yarl.URL`

      :param bool allow_redirects: Whether to process redirects or not.
         When ``True``, redirects are followed and logged into
         :attr:`ClientResponse.history`.
         When ``False``, the original response is returned.
         ``False`` by default (optional).

      :return ClientResponse: a :class:`client response
                              <ClientResponse>` object.

   .. method:: options(url, *, allow_redirects=True, **kwargs)
      :async:

      Perform an ``OPTIONS`` request. Returns an async context manager.

      In order to modify inner
      :meth:`request<aiohttp.ClientSession.request>`
      parameters, provide `kwargs`.


      :param url: Request URL, :class:`str` or :class:`~yarl.URL`

      :param bool allow_redirects: Whether to process redirects or not.
         When ``True``, redirects are followed and logged into
         :attr:`ClientResponse.history`.
         When ``False``, the original response is returned.
         ``True`` by default (optional).

      :return ClientResponse: a :class:`client response
                              <ClientResponse>` object.

   .. method:: patch(url, *, data=None, **kwargs)
      :async:

      Perform a ``PATCH`` request. Returns an async context manager.

      In order to modify inner
      :meth:`request<aiohttp.ClientSession.request>`
      parameters, provide `kwargs`.

      :param url: Request URL, :class:`str` or :class:`~yarl.URL`

      :param data: Data to send in the body of the request; see
                   :meth:`request<aiohttp.ClientSession.request>`
                   for details (optional)

      :return ClientResponse: a :class:`client response
                              <ClientResponse>` object.

   .. method:: ws_connect(url, *, method='GET', \
                            protocols=(), \
                            timeout=sentinel,\
                            auth=None,\
                            autoclose=True,\
                            autoping=True,\
                            heartbeat=None,\
                            origin=None, \
                            params=None, \
                            headers=None, \
                            proxy=None, proxy_auth=None, ssl=True, \
                            verify_ssl=None, fingerprint=None, \
                            ssl_context=None, proxy_headers=None, \
                            compress=0, max_msg_size=4194304)
      :async:

      Create a websocket connection. Returns a
      :class:`ClientWebSocketResponse` async context manager object.

      :param url: Websocket server url, :class:`~yarl.URL` or :class:`str` that
                  will be encoded with :class:`~yarl.URL` (see :class:`~yarl.URL`
                  to skip encoding).

      :param tuple protocols: Websocket protocols

      :param timeout: a :class:`ClientWSTimeout` timeout for websocket.
                      By default, the value
                      `ClientWSTimeout(ws_receive=None, ws_close=10.0)` is used
                      (``10.0`` seconds for the websocket to close).
                      ``None`` means no timeout will be used.

      :param aiohttp.BasicAuth auth: an object that represents HTTP
                                     Basic Authorization (optional)

      :param bool autoclose: Automatically close websocket connection on close
                             message from server. If *autoclose* is False
                             then close procedure has to be handled manually.
                             ``True`` by default

      :param bool autoping: automatically send *pong* on *ping*
                            message from server. ``True`` by default

      :param float heartbeat: Send *ping* message every *heartbeat*
                              seconds and wait *pong* response, if
                              *pong* response is not received then
                              close connection. The timer is reset on any data
                              reception.(optional)

      :param str origin: Origin header to send to server(optional)

      :param params: Mapping, iterable of tuple of *key*/*value* pairs or
                     string to be sent as parameters in the query
                     string of the new request. Ignored for subsequent
                     redirected requests (optional)

                     Allowed values are:

                     - :class:`collections.abc.Mapping` e.g. :class:`dict`,
                       :class:`multidict.MultiDict` or
                       :class:`multidict.MultiDictProxy`
                     - :class:`collections.abc.Iterable` e.g. :class:`tuple` or
                       :class:`list`
                     - :class:`str` with preferably url-encoded content
                       (**Warning:** content will not be encoded by *aiohttp*)

      :param dict headers: HTTP Headers to send with
                           the request (optional)

      :param str proxy: Proxy URL, :class:`str` or :class:`~yarl.URL` (optional)

      :param aiohttp.BasicAuth proxy_auth: an object that represents proxy HTTP
                                           Basic Authorization (optional)

      :param ssl: SSL validation mode. ``True`` for default SSL check
                  (:func:`ssl.create_default_context` is used),
                  ``False`` for skip SSL certificate validation,
                  :class:`aiohttp.Fingerprint` for fingerprint
                  validation, :class:`ssl.SSLContext` for custom SSL
                  certificate validation.

                  Supersedes *verify_ssl*, *ssl_context* and
                  *fingerprint* parameters.

         .. versionadded:: 3.0

      :param bool verify_ssl: Perform SSL certificate validation for
         *HTTPS* requests (enabled by default). May be disabled to
         skip validation for sites with invalid certificates.

         .. versionadded:: 2.3

         .. deprecated:: 3.0

            Use ``ssl=False``

      :param bytes fingerprint: Pass the SHA256 digest of the expected
         certificate in DER format to verify that the certificate the
         server presents matches. Useful for `certificate pinning
         <https://en.wikipedia.org/wiki/HTTP_Public_Key_Pinning>`_.

         Note: use of MD5 or SHA1 digests is insecure and deprecated.

         .. versionadded:: 2.3

         .. deprecated:: 3.0

            Use ``ssl=aiohttp.Fingerprint(digest)``

      :param ssl.SSLContext ssl_context: ssl context used for processing
         *HTTPS* requests (optional).

         *ssl_context* may be used for configuring certification
         authority channel, supported SSL options etc.

         .. versionadded:: 2.3

         .. deprecated:: 3.0

            Use ``ssl=ssl_context``

      :param dict proxy_headers: HTTP headers to send to the proxy if the
         parameter proxy has been provided.

         .. versionadded:: 2.3

      :param int compress: Enable Per-Message Compress Extension support.
                           0 for disable, 9 to 15 for window bit support.
                           Default value is 0.

         .. versionadded:: 2.3

      :param int max_msg_size: maximum size of read websocket message,
                               4 MB by default. To disable the size
                               limit use ``0``.

         .. versionadded:: 3.3

      :param str method: HTTP method to establish WebSocket connection,
                         ``'GET'`` by default.

         .. versionadded:: 3.5


   .. method:: close()
      :async:

      Close underlying connector.

      Release all acquired resources.

   .. method:: detach()

      Detach connector from session without closing the former.

      Session is switched to closed state anyway.



Basic API
---------

While we encourage :class:`ClientSession` usage we also provide simple
coroutines for making HTTP requests.

Basic API is good for performing simple HTTP requests without
keepaliving, cookies and complex connection stuff like properly configured SSL
certification chaining.


.. function:: request(method, url, *, params=None, data=None, \
                        json=None,\
                        cookies=None, headers=None, skip_auto_headers=None, auth=None, \
                        allow_redirects=True, max_redirects=10, \
                        compress=False, chunked=None, expect100=False, raise_for_status=None, \
                        read_until_eof=True, \
                        proxy=None, proxy_auth=None, \
                        timeout=sentinel, ssl=True, \
                        server_hostname=None, \
                        proxy_headers=None, \
                        trace_request_ctx=None, \
                        read_bufsize=None, \
                        auto_decompress=None, \
                        max_line_size=None, \
                        max_field_size=None, \
                        version=aiohttp.HttpVersion11, \
                        connector=None)
   :async:

   Asynchronous context manager for performing an asynchronous HTTP
   request. Returns a :class:`ClientResponse` response object. Use as
   an async context manager.

   :param str method: HTTP method

   :param url: Request URL, :class:`~yarl.URL` or :class:`str` that will
               be encoded with :class:`~yarl.URL` (see :class:`~yarl.URL`
               to skip encoding).

   :param params: Mapping, iterable of tuple of *key*/*value* pairs or
                  string to be sent as parameters in the query
                  string of the new request. Ignored for subsequent
                  redirected requests (optional)

                  Allowed values are:

                  - :class:`collections.abc.Mapping` e.g. :class:`dict`,
                     :class:`multidict.MultiDict` or
                     :class:`multidict.MultiDictProxy`
                  - :class:`collections.abc.Iterable` e.g. :class:`tuple` or
                     :class:`list`
                  - :class:`str` with preferably url-encoded content
                     (**Warning:** content will not be encoded by *aiohttp*)

   :param data: The data to send in the body of the request. This can be a
                :class:`FormData` object or anything that can be passed into
                :class:`FormData`, e.g. a dictionary, bytes, or file-like object.
                (optional)

   :param json: Any json compatible python object (optional). *json* and *data*
                parameters could not be used at the same time.

   :param dict cookies: HTTP Cookies to send with the request (optional)

   :param dict headers: HTTP Headers to send with the request (optional)

   :param skip_auto_headers: set of headers for which autogeneration
      should be skipped.

      *aiohttp* autogenerates headers like ``User-Agent`` or
      ``Content-Type`` if these headers are not explicitly
      passed. Using ``skip_auto_headers`` parameter allows to skip
      that generation.

      Iterable of :class:`str` or :class:`~multidict.istr`
      (optional)

   :param aiohttp.BasicAuth auth: an object that represents HTTP Basic
                                  Authorization (optional)

   :param bool allow_redirects: Whether to process redirects or not.
      When ``True``, redirects are followed (up to ``max_redirects`` times)
      and logged into :attr:`ClientResponse.history` and ``trace_configs``.
      When ``False``, the original response is returned.
      ``True`` by default (optional).

   :param int max_redirects: Maximum number of redirects to follow.
      :exc:`TooManyRedirects` is raised if the number is exceeded.
      Ignored when ``allow_redirects=False``.
      ``10`` by default.

   :param bool compress: Set to ``True`` if request has to be compressed
                         with deflate encoding. If `compress` can not be combined
                         with a *Content-Encoding* and *Content-Length* headers.
                         ``None`` by default (optional).

   :param int chunked: Enables chunked transfer encoding.
      It is up to the developer
      to decide how to chunk data streams. If chunking is enabled, aiohttp
      encodes the provided chunks in the "Transfer-encoding: chunked" format.
      If *chunked* is set, then the *Transfer-encoding* and *content-length*
      headers are disallowed. ``None`` by default (optional).

   :param bool expect100: Expect 100-continue response from server.
                          ``False`` by default (optional).

   :param bool raise_for_status: Automatically call
                                 :meth:`ClientResponse.raise_for_status`
                                 for response if set to ``True``.  If
                                 set to ``None`` value from
                                 ``ClientSession`` will be used.
                                 ``None`` by default (optional).

      .. versionadded:: 3.4

   :param bool read_until_eof: Read response until EOF if response
                               does not have Content-Length header.
                               ``True`` by default (optional).

   :param proxy: Proxy URL, :class:`str` or :class:`~yarl.URL` (optional)

   :param aiohttp.BasicAuth proxy_auth: an object that represents proxy HTTP
                                        Basic Authorization (optional)

   :param timeout: a :class:`ClientTimeout` settings structure, 300 seconds (5min)
        total timeout, 30 seconds socket connect timeout by default.

   :param ssl: SSL validation mode. ``True`` for default SSL check
               (:func:`ssl.create_default_context` is used),
               ``False`` for skip SSL certificate validation,
               :class:`aiohttp.Fingerprint` for fingerprint
               validation, :class:`ssl.SSLContext` for custom SSL
               certificate validation.

               Supersedes *verify_ssl*, *ssl_context* and
               *fingerprint* parameters.

   :param str server_hostname: Sets or overrides the host name that the
      target server's certificate will be matched against.

      See :py:meth:`asyncio.loop.create_connection`
      for more information.

   :param collections.abc.Mapping proxy_headers: HTTP headers to send to the proxy
      if the parameter proxy has been provided.

   :param trace_request_ctx: Object used to give as a kw param for each new
      :class:`TraceConfig` object instantiated,
      used to give information to the
      tracers that is only available at request time.

   :param int read_bufsize: Size of the read buffer (:attr:`ClientResponse.content`).
                            ``None`` by default,
                            it means that the session global value is used.

      .. versionadded:: 3.7

   :param bool auto_decompress: Automatically decompress response body.
      May be used to enable/disable auto decompression on a per-request basis.

   :param int max_line_size: Maximum allowed size of lines in responses.

   :param int max_field_size: Maximum allowed size of header fields in responses.

   :param aiohttp.protocol.HttpVersion version: Request HTTP version,
      ``HTTP 1.1`` by default. (optional)

   :param aiohttp.BaseConnector connector: BaseConnector sub-class
      instance to support connection pooling. (optional)

   :return ClientResponse: a :class:`client response <ClientResponse>` object.

   Usage::

      import aiohttp

      async def fetch():
          async with aiohttp.request('GET',
                  'http://python.org/') as resp:
              assert resp.status == 200
              print(await resp.text())


.. _aiohttp-client-reference-connectors:

Connectors
----------

Connectors are transports for aiohttp client API.

There are standard connectors:

1. :class:`TCPConnector` for regular *TCP sockets* (both *HTTP* and
   *HTTPS* schemes supported).
2. :class:`UnixConnector` for connecting via UNIX socket (it's used mostly for
   testing purposes).

All connector classes should be derived from :class:`BaseConnector`.

By default all *connectors* support *keep-alive connections* (behavior
is controlled by *force_close* constructor's parameter).


.. class:: BaseConnector(*, keepalive_timeout=15, \
                         force_close=False, limit=100, limit_per_host=0, \
                         enable_cleanup_closed=False, loop=None)

   Base class for all connectors.

   :param float keepalive_timeout: timeout for connection reusing
                                   after releasing (optional). Values
                                   ``0``. For disabling *keep-alive*
                                   feature use ``force_close=True``
                                   flag.

   :param int limit: total number simultaneous connections. If *limit* is
                     ``0`` the connector has no limit (default: 100).

   :param int limit_per_host: limit simultaneous connections to the same
      endpoint.  Endpoints are the same if they are
      have equal ``(host, port, is_ssl)`` triple.
      If *limit* is ``0`` the connector has no limit (default: 0).

   :param bool force_close: close underlying sockets after
                            connection releasing (optional).

   :param bool enable_cleanup_closed: some SSL servers do not properly complete
      SSL shutdown process, in that case asyncio leaks SSL connections.
      If this parameter is set to True, aiohttp additionally aborts underlining
      transport after 2 seconds. It is off by default.

      For Python version 3.12.7+, or 3.13.1 and later,
      this parameter is ignored because the asyncio SSL connection
      leak is fixed in these versions of Python.


   :param loop: :ref:`event loop<asyncio-event-loop>`
      used for handling connections.
      If param is ``None``, :func:`asyncio.get_event_loop`
      is used for getting default event loop.

      .. deprecated:: 2.0

   .. attribute:: closed

      Read-only property, ``True`` if connector is closed.

   .. attribute:: force_close

      Read-only property, ``True`` if connector should ultimately
      close connections on releasing.

   .. attribute:: limit

      The total number for simultaneous connections.
      If limit is 0 the connector has no limit. The default limit size is 100.

   .. attribute:: limit_per_host

      The limit for simultaneous connections to the same
      endpoint.

      Endpoints are the same if they are have equal ``(host, port,
      is_ssl)`` triple.

      If *limit_per_host* is ``0`` the connector has no limit per host.

      Read-only property.

   .. method:: close()
      :async:

      Close all opened connections.

   .. method:: connect(request)
      :async:

      Get a free connection from pool or create new one if connection
      is absent in the pool.

      The call may be paused if :attr:`limit` is exhausted until used
      connections returns to pool.

      :param aiohttp.ClientRequest request: request object
                                                   which is connection
                                                   initiator.

      :return: :class:`Connection` object.

   .. method:: _create_connection(req)
      :async:

      Abstract method for actual connection establishing, should be
      overridden in subclasses.


.. py:class:: AddrInfoType

   Refer to :py:data:`aiohappyeyeballs.AddrInfoType` for more info.

.. warning::

   Be sure to use ``aiohttp.AddrInfoType`` rather than
   ``aiohappyeyeballs.AddrInfoType`` to avoid import breakage, as
   it is likely to be removed from :mod:`aiohappyeyeballs` in the
   future.


.. py:class:: SocketFactoryType

   Refer to :py:data:`aiohappyeyeballs.SocketFactoryType` for more info.

.. warning::

   Be sure to use ``aiohttp.SocketFactoryType`` rather than
   ``aiohappyeyeballs.SocketFactoryType`` to avoid import breakage,
   as it is likely to be removed from :mod:`aiohappyeyeballs` in the
   future.


.. class:: TCPConnector(*, ssl=True, verify_ssl=True, fingerprint=None, \
                 use_dns_cache=True, ttl_dns_cache=10, \
                 family=0, ssl_context=None, local_addr=None, \
                 resolver=None, keepalive_timeout=sentinel, \
                 force_close=False, limit=100, limit_per_host=0, \
                 enable_cleanup_closed=False, timeout_ceil_threshold=5, \
                 happy_eyeballs_delay=0.25, interleave=None, loop=None, \
                 socket_factory=None, ssl_shutdown_timeout=0)

   Connector for working with *HTTP* and *HTTPS* via *TCP* sockets.

   The most common transport. When you don't know what connector type
   to use, use a :class:`TCPConnector` instance.

   :class:`TCPConnector` inherits from :class:`BaseConnector`.

   Constructor accepts all parameters suitable for
   :class:`BaseConnector` plus several TCP-specific ones:

      :param ssl: SSL validation mode. ``True`` for default SSL check
                  (:func:`ssl.create_default_context` is used),
                  ``False`` for skip SSL certificate validation,
                  :class:`aiohttp.Fingerprint` for fingerprint
                  validation, :class:`ssl.SSLContext` for custom SSL
                  certificate validation.

                  Supersedes *verify_ssl*, *ssl_context* and
                  *fingerprint* parameters.

         .. versionadded:: 3.0

   :param bool verify_ssl: perform SSL certificate validation for
      *HTTPS* requests (enabled by default). May be disabled to
      skip validation for sites with invalid certificates.

      .. deprecated:: 2.3

         Pass *verify_ssl* to ``ClientSession.get()`` etc.

   :param bytes fingerprint: pass the SHA256 digest of the expected
      certificate in DER format to verify that the certificate the
      server presents matches. Useful for `certificate pinning
      <https://en.wikipedia.org/wiki/HTTP_Public_Key_Pinning>`_.

      Note: use of MD5 or SHA1 digests is insecure and deprecated.

      .. deprecated:: 2.3

         Pass *verify_ssl* to ``ClientSession.get()`` etc.

   :param bool use_dns_cache: use internal cache for DNS lookups, ``True``
      by default.

      Enabling an option *may* speedup connection
      establishing a bit but may introduce some
      *side effects* also.

   :param int ttl_dns_cache: expire after some seconds the DNS entries, ``None``
      means cached forever. By default 10 seconds (optional).

      In some environments the IP addresses related to a specific HOST can
      change after a specific time. Use this option to keep the DNS cache
      updated refreshing each entry after N seconds.

   :param int limit: total number simultaneous connections. If *limit* is
                     ``0`` the connector has no limit (default: 100).

   :param int limit_per_host: limit simultaneous connections to the same
      endpoint.  Endpoints are the same if they are
      have equal ``(host, port, is_ssl)`` triple.
      If *limit* is ``0`` the connector has no limit (default: 0).

   :param aiohttp.abc.AbstractResolver resolver: custom resolver
      instance to use.  ``aiohttp.DefaultResolver`` by
      default (asynchronous if ``aiodns>=1.1`` is installed).

      Custom resolvers allow to resolve hostnames differently than the
      way the host is configured.

      The resolver is ``aiohttp.ThreadedResolver`` by default,
      asynchronous version is pretty robust but might fail in
      very rare cases.

   :param int family: TCP socket family, both IPv4 and IPv6 by default.
                      For *IPv4* only use :data:`socket.AF_INET`,
                      for  *IPv6* only -- :data:`socket.AF_INET6`.

                      *family* is ``0`` by default, that means both
                      IPv4 and IPv6 are accepted. To specify only
                      concrete version please pass
                      :data:`socket.AF_INET` or
                      :data:`socket.AF_INET6` explicitly.

   :param ssl.SSLContext ssl_context: SSL context used for processing
      *HTTPS* requests (optional).

      *ssl_context* may be used for configuring certification
      authority channel, supported SSL options etc.

   :param tuple local_addr: tuple of ``(local_host, local_port)`` used to bind
      socket locally if specified.

   :param bool force_close: close underlying sockets after
                            connection releasing (optional).

   :param bool enable_cleanup_closed: Some ssl servers do not properly complete
      SSL shutdown process, in that case asyncio leaks SSL connections.
      If this parameter is set to True, aiohttp additionally aborts underlining
      transport after 2 seconds. It is off by default.

   :param float happy_eyeballs_delay: The amount of time in seconds to wait for a
      connection attempt to complete, before starting the next attempt in parallel.
      This is the “Connection Attempt Delay” as defined in RFC 8305. To disable
      Happy Eyeballs, set this to ``None``. The default value recommended by the
      RFC is 0.25 (250 milliseconds).

        .. versionadded:: 3.10

   :param int interleave: controls address reordering when a host name resolves
      to multiple IP addresses. If ``0`` or unspecified, no reordering is done, and
      addresses are tried in the order returned by the resolver. If a positive
      integer is specified, the addresses are interleaved by address family, and
      the given integer is interpreted as “First Address Family Count” as defined
      in RFC 8305. The default is ``0`` if happy_eyeballs_delay is not specified, and
      ``1`` if it is.

        .. versionadded:: 3.10

   :param SocketFactoryType socket_factory: This function takes an
      :py:data:`AddrInfoType` and is used in lieu of
      :py:func:`socket.socket` when creating TCP connections.

        .. versionadded:: 3.12

   :param float ssl_shutdown_timeout: **(DEPRECATED)** This parameter is deprecated
      and will be removed in aiohttp 4.0. Grace period for SSL shutdown on TLS
      connections when the connector is closed (``0`` seconds by default).
      By default (``0``), SSL connections are aborted immediately when the
      connector is closed, without performing the shutdown handshake. During
      normal operation, SSL connections use Python's default SSL shutdown
      behavior. Setting this to a positive value (e.g., ``0.1``) will perform
      a graceful shutdown when closing the connector, notifying the remote
      server which can help prevent "connection reset" errors at the cost of
      additional cleanup time. Note: On Python versions prior to 3.11, only
      a value of ``0`` is supported; other values will trigger a warning.

        .. versionadded:: 3.12.5

        .. versionchanged:: 3.12.11
           Changed default from ``0.1`` to ``0`` to abort SSL connections
           immediately when the connector is closed. Added support for
           ``ssl_shutdown_timeout=0`` on all Python versions. A :exc:`RuntimeWarning`
           is issued when non-zero values are passed on Python < 3.11.

        .. deprecated:: 3.12.11
           This parameter is deprecated and will be removed in aiohttp 4.0.

   .. attribute:: family

      *TCP* socket family e.g. :data:`socket.AF_INET` or
      :data:`socket.AF_INET6`

      Read-only property.

   .. attribute:: dns_cache

      Use quick lookup in internal *DNS* cache for host names if ``True``.

      Read-only :class:`bool` property.

   .. attribute:: cached_hosts

      The cache of resolved hosts if :attr:`dns_cache` is enabled.

      Read-only :class:`types.MappingProxyType` property.

   .. method:: clear_dns_cache(self, host=None, port=None)

      Clear internal *DNS* cache.

      Remove specific entry if both *host* and *port* are specified,
      clear all cache otherwise.


.. class:: UnixConnector(path, *, conn_timeout=None, \
                         keepalive_timeout=30, limit=100, \
                         force_close=False, loop=None)

   Unix socket connector.

   Use :class:`UnixConnector` for sending *HTTP/HTTPS* requests
   through *UNIX Sockets* as underlying transport.

   UNIX sockets are handy for writing tests and making very fast
   connections between processes on the same host.

   :class:`UnixConnector` is inherited from :class:`BaseConnector`.

    Usage::

       conn = UnixConnector(path='/path/to/socket')
       session = ClientSession(connector=conn)
       async with session.get('http://python.org') as resp:
           ...

   Constructor accepts all parameters suitable for
   :class:`BaseConnector` plus UNIX-specific one:

   :param str path: Unix socket path


   .. attribute:: path

      Path to *UNIX socket*, read-only :class:`str` property.


.. class:: Connection

   Encapsulates single connection in connector object.

   End user should never create :class:`Connection` instances manually
   but get it by :meth:`BaseConnector.connect` coroutine.

   .. attribute:: closed

      :class:`bool` read-only property, ``True`` if connection was
      closed, released or detached.

   .. attribute:: loop

      Event loop used for connection

      .. deprecated:: 3.5

   .. attribute:: transport

      Connection transport

   .. method:: close()

      Close connection with forcibly closing underlying socket.

   .. method:: release()

      Release connection back to connector.

      Underlying socket is not closed, the connection may be reused
      later if timeout (30 seconds by default) for connection was not
      expired.


Response object
---------------

.. class:: ClientResponse

   Client response returned by :meth:`aiohttp.ClientSession.request` and family.

   User never creates the instance of ClientResponse class but gets it
   from API calls.

   :class:`ClientResponse` supports async context manager protocol, e.g.::

       resp = await client_session.get(url)
       async with resp:
           assert resp.status == 200

   After exiting from ``async with`` block response object will be
   *released* (see :meth:`release` method).

   .. attribute:: version

      Response's version, :class:`~aiohttp.protocol.HttpVersion` instance.

   .. attribute:: status

      HTTP status code of response (:class:`int`), e.g. ``200``.

   .. attribute:: reason

      HTTP status reason of response (:class:`str`), e.g. ``"OK"``.

   .. attribute:: ok

      Boolean representation of HTTP status code (:class:`bool`).
      ``True`` if ``status`` is less than ``400``; otherwise, ``False``.

   .. attribute:: method

      Request's method (:class:`str`).

   .. attribute:: url

      URL of request (:class:`~yarl.URL`).

   .. attribute:: real_url

      Unmodified URL of request with URL fragment unstripped (:class:`~yarl.URL`).

      .. versionadded:: 3.2

   .. attribute:: connection

      :class:`Connection` used for handling response.

   .. attribute:: content

      Payload stream, which contains response's BODY (:class:`StreamReader`).
      It supports various reading methods depending on the expected format.
      When chunked transfer encoding is used by the server, allows retrieving
      the actual http chunks.

      Reading from the stream may raise
      :exc:`aiohttp.ClientPayloadError` if the response object is
      closed before response receives all data or in case if any
      transfer encoding related errors like malformed chunked
      encoding of broken compression data.

   .. attribute:: cookies

      HTTP cookies of response (*Set-Cookie* HTTP header,
      :class:`~http.cookies.SimpleCookie`).

      .. note::

         Since :class:`~http.cookies.SimpleCookie` uses cookie name as the
         key, cookies with the same name but different domains or paths will
         be overwritten. Only the last cookie with a given name will be
         accessible via this attribute.

         To access all cookies, including duplicates with the same name,
         use :meth:`response.headers.getall('Set-Cookie') <multidict.MultiDictProxy.getall>`.

         The session's cookie jar will correctly store all cookies, even if
         they are not accessible via this attribute.

   .. attribute:: headers

      A case-insensitive multidict proxy with HTTP headers of
      response, :class:`~multidict.CIMultiDictProxy`.

   .. attribute:: raw_headers

      Unmodified HTTP headers of response as unconverted bytes, a sequence of
      ``(key, value)`` pairs.

   .. attribute:: links

      Link HTTP header parsed into a :class:`~multidict.MultiDictProxy`.

      For each link, key is link param `rel` when it exists, or link url as
      :class:`str` otherwise, and value is :class:`~multidict.MultiDictProxy`
      of link params and url at key `url` as :class:`~yarl.URL` instance.

      .. versionadded:: 3.2

   .. attribute:: content_type

      Read-only property with *content* part of *Content-Type* header.

      .. note::

         Returns value is ``'application/octet-stream'`` if no
         Content-Type header present in HTTP headers according to
         :rfc:`9110`. If the *Content-Type* header is invalid (e.g., ``jpg``
         instead of ``image/jpeg``), the value is ``text/plain`` by default
         according to :rfc:`2045`. To see the original header check
         ``resp.headers['CONTENT-TYPE']``.

         To make sure Content-Type header is not present in
         the server reply, use :attr:`headers` or :attr:`raw_headers`, e.g.
         ``'CONTENT-TYPE' not in resp.headers``.

   .. attribute:: charset

      Read-only property that specifies the *encoding* for the request's BODY.

      The value is parsed from the *Content-Type* HTTP header.

      Returns :class:`str` like ``'utf-8'`` or ``None`` if no *Content-Type*
      header present in HTTP headers or it has no charset information.

   .. attribute:: content_disposition

      Read-only property that specified the *Content-Disposition* HTTP header.

      Instance of :class:`ContentDisposition` or ``None`` if no *Content-Disposition*
      header present in HTTP headers.

   .. attribute:: history

      A :class:`~collections.abc.Sequence` of :class:`ClientResponse`
      objects of preceding requests (earliest request first) if there were
      redirects, an empty sequence otherwise.

   .. method:: close()

      Close response and underlying connection.

      For :term:`keep-alive` support see :meth:`release`.

   .. method:: read()
      :async:

      Read the whole response's body as :class:`bytes`.

      Close underlying connection if data reading gets an error,
      release connection otherwise.

      Raise an :exc:`aiohttp.ClientResponseError` if the data can't
      be read.

      :return bytes: read *BODY*.

      .. seealso:: :meth:`close`, :meth:`release`.

   .. method:: release()

      It is not required to call `release` on the response
      object. When the client fully receives the payload, the
      underlying connection automatically returns back to pool. If the
      payload is not fully read, the connection is closed

   .. method:: raise_for_status()

      Raise an :exc:`aiohttp.ClientResponseError` if the response
      status is 400 or higher.

      Do nothing for success responses (less than 400).

   .. method:: text(encoding=None)
      :async:

      Read response's body and return decoded :class:`str` using
      specified *encoding* parameter.

      If *encoding* is ``None`` content encoding is determined from the
      Content-Type header, or using the ``fallback_charset_resolver`` function.

      Close underlying connection if data reading gets an error,
      release connection otherwise.

      :param str encoding: text encoding used for *BODY* decoding, or
                           ``None`` for encoding autodetection
                           (default).


      :raises: :exc:`UnicodeDecodeError` if decoding fails. See also
               :meth:`get_encoding`.

      :return str: decoded *BODY*

   .. method:: json(*, encoding=None, loads=json.loads, \
                      content_type='application/json')
      :async:

      Read response's body as *JSON*, return :class:`dict` using
      specified *encoding* and *loader*. If data is not still available
      a ``read`` call will be done.

      If response's `content-type` does not match `content_type` parameter
      :exc:`aiohttp.ContentTypeError` get raised.
      To disable content type check pass ``None`` value.

      :param str encoding: text encoding used for *BODY* decoding, or
                           ``None`` for encoding autodetection
                           (default).

                           By the standard JSON encoding should be
                           ``UTF-8`` but practice beats purity: some
                           servers return non-UTF
                           responses. Autodetection works pretty fine
                           anyway.

      :param collections.abc.Callable loads: :term:`callable` used for loading *JSON*
                             data, :func:`json.loads` by default.

      :param str content_type: specify response's content-type, if content type
         does not match raise :exc:`aiohttp.ClientResponseError`.
         To disable `content-type` check, pass ``None`` as value.
         (default: `application/json`).

      :return: *BODY* as *JSON* data parsed by *loads* parameter or
               ``None`` if *BODY* is empty or contains white-spaces only.

   .. attribute:: request_info

       A :class:`typing.NamedTuple` with request URL and headers from :class:`~aiohttp.ClientRequest`
       object, :class:`aiohttp.RequestInfo` instance.

   .. method:: get_encoding()

      Retrieve content encoding using ``charset`` info in ``Content-Type`` HTTP header.
      If no charset is present or the charset is not understood by Python, the
      ``fallback_charset_resolver`` function associated with the ``ClientSession`` is called.

      .. versionadded:: 3.0


ClientWebSocketResponse
-----------------------

To connect to a websocket server :func:`aiohttp.ws_connect` or
:meth:`aiohttp.ClientSession.ws_connect` coroutines should be used, do
not create an instance of class :class:`ClientWebSocketResponse`
manually.

.. class:: ClientWebSocketResponse()

   Class for handling client-side websockets.

   .. attribute:: closed

      Read-only property, ``True`` if :meth:`close` has been called or
      :const:`~aiohttp.WSMsgType.CLOSE` message has been received from peer.

   .. attribute:: protocol

      Websocket *subprotocol* chosen after :meth:`start` call.

      May be ``None`` if server and client protocols are
      not overlapping.

   .. method:: get_extra_info(name, default=None)

      Reads optional extra information from the connection's transport.
      If no value associated with ``name`` is found, ``default`` is returned.

      See :meth:`asyncio.BaseTransport.get_extra_info`

      :param str name: The key to look up in the transport extra information.

      :param default: Default value to be used when no value for ``name`` is
                      found (default is ``None``).

   .. method:: exception()

      Returns exception if any occurs or returns None.

   .. method:: ping(message=b'')
      :async:

      Send :const:`~aiohttp.WSMsgType.PING` to peer.

      :param message: optional payload of *ping* message,
                      :class:`str` (converted to *UTF-8* encoded bytes)
                      or :class:`bytes`.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`

   .. method:: pong(message=b'')
      :async:

      Send :const:`~aiohttp.WSMsgType.PONG` to peer.

      :param message: optional payload of *pong* message,
                      :class:`str` (converted to *UTF-8* encoded bytes)
                      or :class:`bytes`.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`

   .. method:: send_str(data, compress=None)
      :async:

      Send *data* to peer as :const:`~aiohttp.WSMsgType.TEXT` message.

      :param str data: data to send.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      :raise TypeError: if data is not :class:`str`

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`,
         *compress* parameter added.

   .. method:: send_bytes(data, compress=None)
      :async:

      Send *data* to peer as :const:`~aiohttp.WSMsgType.BINARY` message.

      :param data: data to send.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      :raise TypeError: if data is not :class:`bytes`,
                        :class:`bytearray` or :class:`memoryview`.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`,
         *compress* parameter added.

   .. method:: send_json(data, compress=None, *, dumps=json.dumps)
      :async:

      Send *data* to peer as JSON string.

      :param data: data to send.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      :param collections.abc.Callable dumps: any :term:`callable` that accepts an object and
                             returns a JSON string
                             (:func:`json.dumps` by default).

      :raise RuntimeError: if connection is not started or closing

      :raise ValueError: if data is not serializable object

      :raise TypeError: if value returned by ``dumps(data)`` is not
                        :class:`str`

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`,
         *compress* parameter added.

   .. method:: send_frame(message, opcode, compress=None)
      :async:

      Send a :const:`~aiohttp.WSMsgType` message *message* to peer.

      This method is low-level and should be used with caution as it
      only accepts bytes which must conform to the correct message type
      for *message*.

      It is recommended to use the :meth:`send_str`, :meth:`send_bytes`
      or :meth:`send_json` methods instead of this method.

      The primary use case for this method is to send bytes that are
      have already been encoded without having to decode and
      re-encode them.

      :param bytes message: message to send.

      :param ~aiohttp.WSMsgType opcode: opcode of the message.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      .. versionadded:: 3.11

   .. method:: close(*, code=WSCloseCode.OK, message=b'')
      :async:

      A :ref:`coroutine<coroutine>` that initiates closing handshake by sending
      :const:`~aiohttp.WSMsgType.CLOSE` message. It waits for
      close response from server. To add a timeout to `close()` call
      just wrap the call with `asyncio.wait()` or `asyncio.wait_for()`.

      :param int code: closing code. See also :class:`~aiohttp.WSCloseCode`.

      :param message: optional payload of *close* message,
         :class:`str` (converted to *UTF-8* encoded bytes) or :class:`bytes`.

   .. method:: receive()
      :async:

      A :ref:`coroutine<coroutine>` that waits upcoming *data*
      message from peer and returns it.

      The coroutine implicitly handles
      :const:`~aiohttp.WSMsgType.PING`,
      :const:`~aiohttp.WSMsgType.PONG` and
      :const:`~aiohttp.WSMsgType.CLOSE` without returning the
      message.

      It process *ping-pong game* and performs *closing handshake* internally.

      :return: :class:`~aiohttp.WSMessage`

   .. method:: receive_str()
      :async:

      A :ref:`coroutine<coroutine>` that calls :meth:`receive` but
      also asserts the message type is
      :const:`~aiohttp.WSMsgType.TEXT`.

      :return str: peer's message content.

      :raise aiohttp.WSMessageTypeError: if message is not :const:`~aiohttp.WSMsgType.TEXT`.

   .. method:: receive_bytes()
      :async:

      A :ref:`coroutine<coroutine>` that calls :meth:`receive` but
      also asserts the message type is
      :const:`~aiohttp.WSMsgType.BINARY`.

      :return bytes: peer's message content.

      :raise aiohttp.WSMessageTypeError: if message is not :const:`~aiohttp.WSMsgType.BINARY`.

   .. method:: receive_json(*, loads=json.loads)
      :async:

      A :ref:`coroutine<coroutine>` that calls :meth:`receive_str` and loads
      the JSON string to a Python dict.

      :param collections.abc.Callable loads: any :term:`callable` that accepts
                              :class:`str` and returns :class:`dict`
                              with parsed JSON (:func:`json.loads` by
                              default).

      :return dict: loaded JSON content

      :raise TypeError: if message is :const:`~aiohttp.WSMsgType.BINARY`.
      :raise ValueError: if message is not valid JSON.

ClientRequest
-------------

.. class:: ClientRequest

   Represents an HTTP request to be sent by the client.

   This object encapsulates all the details of an HTTP request before it is sent.
   It is primarily used within client middleware to inspect or modify requests.

   .. note::

      You typically don't create ``ClientRequest`` instances directly. They are
      created internally by :class:`ClientSession` methods and passed to middleware.

   For more information about using middleware, see :ref:`aiohttp-client-middleware`.

   .. attribute:: body
      :type: Payload | Literal[b""]

      The request body payload (defaults to ``b""`` if no body passed).

      .. danger::

         **DO NOT set this attribute directly!** Direct assignment will cause resource
         leaks. Always use :meth:`update_body` instead:

         .. code-block:: python

            # WRONG - This will leak resources!
            request.body = b"new data"

            # CORRECT - Use update_body
            await request.update_body(b"new data")

         Setting body directly bypasses cleanup of the previous payload, which can
         leave file handles open, streams unclosed, and buffers unreleased.

         Additionally, setting body directly must be done from within an event loop
         and is not thread-safe. Setting body outside of an event loop may raise
         RuntimeError when closing file-based payloads.

   .. attribute:: chunked
      :type: bool | None

      Whether to use chunked transfer encoding:

      - ``True``: Use chunked encoding
      - ``False``: Don't use chunked encoding
      - ``None``: Automatically determine based on body

   .. attribute:: compress
      :type: str | None

      The compression encoding for the request body. Common values include
      ``'gzip'`` and ``'deflate'``, but any string value is technically allowed.
      ``None`` means no compression.

   .. attribute:: headers
      :type: multidict.CIMultiDict

      The HTTP headers that will be sent with the request. This is a case-insensitive
      multidict that can be modified by middleware.

      .. code-block:: python

         # Add or modify headers
         request.headers['X-Custom-Header'] = 'value'
         request.headers['User-Agent'] = 'MyApp/1.0'

   .. attribute:: is_ssl
      :type: bool

      ``True`` if the request uses a secure scheme (e.g., HTTPS, WSS), ``False`` otherwise.

   .. attribute:: method
      :type: str

      The HTTP method of the request (e.g., ``'GET'``, ``'POST'``, ``'PUT'``, etc.).

   .. attribute:: original_url
      :type: yarl.URL

      The original URL passed to the request method, including any fragment.
      This preserves the exact URL as provided by the user.

   .. attribute:: proxy
      :type: yarl.URL | None

      The proxy URL if the request will be sent through a proxy, ``None`` otherwise.

   .. attribute:: proxy_headers
      :type: multidict.CIMultiDict | None

      Headers to be sent to the proxy server (e.g., ``Proxy-Authorization``).
      Only set when :attr:`proxy` is not ``None``.

   .. attribute:: response_class
      :type: type[ClientResponse]

      The class to use for creating the response object. Defaults to
      :class:`ClientResponse` but can be customized for special handling.

   .. attribute:: server_hostname
      :type: str | None

      Override the hostname for SSL certificate verification. Useful when
      connecting through proxies or to IP addresses.

   .. attribute:: session
      :type: ClientSession

      The client session that created this request. Useful for accessing
      session-level configuration or making additional requests within middleware.

      .. warning::
         Be careful when making requests with the same session inside middleware
         to avoid infinite recursion. Use ``middlewares=()`` parameter when needed.

   .. attribute:: ssl
      :type: ssl.SSLContext | bool | Fingerprint

      SSL validation configuration for this request:

      - ``True``: Use default SSL verification
      - ``False``: Skip SSL verification
      - :class:`ssl.SSLContext`: Custom SSL context
      - :class:`Fingerprint`: Verify specific certificate fingerprint

   .. attribute:: url
      :type: yarl.URL

      The target URL of the request with the fragment (``#...``) part stripped.
      This is the actual URL that will be used for the connection.

      .. note::
         To access the original URL with fragment, use :attr:`original_url`.

   .. attribute:: version
      :type: HttpVersion

      The HTTP version to use for the request (e.g., ``HttpVersion(1, 1)`` for HTTP/1.1).

   .. method:: update_body(body)

      Update the request body and close any existing payload to prevent resource leaks.

      **This is the ONLY correct way to modify a request body.** Never set the
      :attr:`body` attribute directly.

      This method is particularly useful in middleware when you need to modify the
      request body after the request has been created but before it's sent.

      :param body: The new body content. Can be:

                   - ``bytes``/``bytearray``: Raw binary data
                   - ``str``: Text data (encoded using charset from Content-Type)
                   - :class:`FormData`: Form data encoded as multipart/form-data
                   - :class:`Payload`: A pre-configured payload object
                   - ``AsyncIterable[bytes]``: Async iterable of bytes chunks
                   - File-like object: Will be read and sent as binary data
                   - ``None``: Clears the body

      .. code-block:: python

         async def middleware(request, handler):
             # Modify request body in middleware
             if request.method == 'POST':
                 # CORRECT: Always use update_body
                 await request.update_body(b'{"modified": true}')

                 # WRONG: Never set body directly!
                 # request.body = b'{"modified": true}'  # This leaks resources!

             # Or add authentication data to form
             if isinstance(request.body, FormData):
                 form = FormData()
                 # Copy existing fields and add auth token
                 form.add_field('auth_token', 'secret123')
                 await request.update_body(form)

             return await handler(request)

      .. note::

         This method is async because it may need to close file handles or
         other resources associated with the previous payload. Always await
         this method to ensure proper cleanup.

      .. danger::

         **Never set :attr:`ClientRequest.body` directly!** Direct assignment will cause resource
         leaks. Always use this method instead. Setting the body attribute directly:

         - Bypasses cleanup of the previous payload
         - Leaves file handles and streams open
         - Can cause memory leaks
         - May result in unexpected behavior with async iterables

      .. warning::

         When updating the body, ensure that the Content-Type header is
         appropriate for the new body content. The Content-Length header
         will be updated automatically. When using :class:`FormData` or
         :class:`Payload` objects, headers are updated automatically,
         but you may need to set Content-Type manually for raw bytes or text.

         It is not recommended to change the payload type in middleware. If the
         body was already set (e.g., as bytes), it's best to keep the same type
         rather than converting it (e.g., to str) as this may result in unexpected
         behavior.

      .. versionadded:: 3.12



Utilities
---------


.. class:: ClientTimeout(*, total=None, connect=None, \
                         sock_connect=None, sock_read=None)

   A data class for client timeout settings.

   See :ref:`aiohttp-client-timeouts` for usage examples.

   .. attribute:: total

      Total number of seconds for the whole request.

      :class:`float`, ``None`` by default.

   .. attribute:: connect

      Maximal number of seconds for acquiring a connection from pool.  The time
      consists connection establishment for a new connection or
      waiting for a free connection from a pool if pool connection
      limits are exceeded.

      For pure socket connection establishment time use
      :attr:`sock_connect`.

      :class:`float`, ``None`` by default.

   .. attribute:: sock_connect

      Maximal number of seconds for connecting to a peer for a new connection, not
      given from a pool.  See also :attr:`connect`.

      :class:`float`, ``None`` by default.

   .. attribute:: sock_read

      Maximal number of seconds for reading a portion of data from a peer.

      :class:`float`, ``None`` by default.


.. class:: ClientWSTimeout(*, ws_receive=None, ws_close=None)

   A data class for websocket client timeout settings.

   .. attribute:: ws_receive

      A timeout for websocket to receive a complete message.

      :class:`float`, ``None`` by default.

   .. attribute:: ws_close

      A timeout for the websocket to close.

      :class:`float`, ``10.0`` by default.


   .. note::

      Timeouts of 5 seconds or more are rounded for scheduling on the next
      second boundary (an absolute time where microseconds part is zero) for the
      sake of performance.

      E.g., assume a timeout is ``10``, absolute time when timeout should expire
      is ``loop.time() + 5``, and it points to ``12345.67 + 10`` which is equal
      to ``12355.67``.

      The absolute time for the timeout cancellation is ``12356``.

      It leads to grouping all close scheduled timeout expirations to exactly
      the same time to reduce amount of loop wakeups.

      .. versionchanged:: 3.7

         Rounding to the next seconds boundary is disabled for timeouts smaller
         than 5 seconds for the sake of easy debugging.

         In turn, tiny timeouts can lead to significant performance degradation
         on production environment.


.. class:: ETag(name, is_weak=False)

   Represents `ETag` identifier.

   .. attribute:: value

      Value of corresponding etag without quotes.

   .. attribute:: is_weak

      Flag indicates that etag is weak (has `W/` prefix).

   .. versionadded:: 3.8


.. class:: ContentDisposition

    A data class to represent the Content-Disposition header,
    available as :attr:`ClientResponse.content_disposition` attribute.

    .. attribute:: type

    A :class:`str` instance. Value of Content-Disposition header
    itself, e.g. ``attachment``.

    .. attribute:: filename

    A :class:`str` instance. Content filename extracted from
    parameters. May be ``None``.

    .. attribute:: parameters

    Read-only mapping contains all parameters.


.. class:: RequestInfo()

   A :class:`typing.NamedTuple` with request URL and headers from :class:`~aiohttp.ClientRequest`
   object, available as :attr:`ClientResponse.request_info` attribute.

   .. attribute:: url

      Requested *url*, :class:`yarl.URL` instance.

   .. attribute:: method

      Request HTTP method like ``'GET'`` or ``'POST'``, :class:`str`.

   .. attribute:: headers

      HTTP headers for request, :class:`multidict.CIMultiDict` instance.

   .. attribute:: real_url

      Requested *url* with URL fragment unstripped, :class:`yarl.URL` instance.

      .. versionadded:: 3.2



.. class:: BasicAuth(login, password='', encoding='latin1')

   HTTP basic authentication helper.

   :param str login: login
   :param str password: password
   :param str encoding: encoding (``'latin1'`` by default)


   Should be used for specifying authorization data in client API,
   e.g. *auth* parameter for :meth:`ClientSession.request() <aiohttp.ClientSession.request>`.


   .. classmethod:: decode(auth_header, encoding='latin1')

      Decode HTTP basic authentication credentials.

      :param str auth_header:  The ``Authorization`` header to decode.
      :param str encoding: (optional) encoding ('latin1' by default)

      :return:  decoded authentication data, :class:`BasicAuth`.

   .. classmethod:: from_url(url)

      Constructed credentials info from url's *user* and *password*
      parts.

      :return: credentials data, :class:`BasicAuth` or ``None`` is
                credentials are not provided.

      .. versionadded:: 2.3

   .. method:: encode()

      Encode credentials into string suitable for ``Authorization``
      header etc.

      :return: encoded authentication data, :class:`str`.


.. class:: DigestAuthMiddleware(login, password, *, preemptive=True)

   HTTP digest authentication client middleware.

   :param str login: login
   :param str password: password
   :param bool preemptive: Enable preemptive authentication (default: ``True``)

   This middleware supports HTTP digest authentication with both `auth` and
   `auth-int` quality of protection (qop) modes, and a variety of hashing algorithms.

   It automatically handles the digest authentication handshake by:

   - Parsing 401 Unauthorized responses with `WWW-Authenticate: Digest` headers
   - Generating appropriate `Authorization: Digest` headers on retry
   - Maintaining nonce counts and challenge data per request
   - When ``preemptive=True``, reusing authentication credentials for subsequent
     requests to the same protection space (following RFC 7616 Section 3.6)

   **Preemptive Authentication**

   By default (``preemptive=True``), the middleware remembers successful authentication
   challenges and automatically includes the Authorization header in subsequent requests
   to the same protection space. This behavior:

   - Improves server efficiency by avoiding extra round trips
   - Matches how modern web browsers handle digest authentication
   - Follows the recommendation in RFC 7616 Section 3.6

   The server may still respond with a 401 status and ``stale=true`` if the nonce
   has expired, in which case the middleware will automatically retry with the new nonce.

   To disable preemptive authentication and require a 401 challenge for every request,
   set ``preemptive=False``::

       # Default behavior - preemptive auth enabled
       digest_auth_middleware = DigestAuthMiddleware(login="user", password="pass")

       # Disable preemptive auth - always wait for 401 challenge
       digest_auth_middleware = DigestAuthMiddleware(login="user", password="pass",
                                                      preemptive=False)

   Usage::

       digest_auth_middleware = DigestAuthMiddleware(login="user", password="pass")
       async with ClientSession(middlewares=(digest_auth_middleware,)) as session:
           async with session.get("http://protected.example.com") as resp:
               # The middleware automatically handles the digest auth handshake
               assert resp.status == 200

           # Subsequent requests include auth header preemptively
           async with session.get("http://protected.example.com/other") as resp:
               assert resp.status == 200  # No 401 round trip needed

   .. versionadded:: 3.12
   .. versionchanged:: 3.12.8
      Added ``preemptive`` parameter to enable/disable preemptive authentication.


.. class:: CookieJar(*, unsafe=False, quote_cookie=True, treat_as_secure_origin = [])

   The cookie jar instance is available as :attr:`ClientSession.cookie_jar`.

   The jar contains :class:`~http.cookies.Morsel` items for storing
   internal cookie data.

   API provides a count of saved cookies::

       len(session.cookie_jar)

   These cookies may be iterated over::

       for cookie in session.cookie_jar:
           print(cookie.key)
           print(cookie["domain"])

   The class implements :class:`collections.abc.Iterable`,
   :class:`collections.abc.Sized` and
   :class:`aiohttp.abc.AbstractCookieJar` interfaces.

   Implements cookie storage adhering to RFC 6265.

   :param bool unsafe: (optional) Whether to accept cookies from IPs.

   :param bool quote_cookie: (optional) Whether to quote cookies according to
                             :rfc:`2109`.  Some backend systems
                             (not compatible with RFC mentioned above)
                             does not support quoted cookies.

      .. versionadded:: 3.7

   :param treat_as_secure_origin: (optional) Mark origins as secure
                                  for cookies marked as Secured. Possible types are

                                  Possible types are:

                                  - :class:`tuple` or :class:`list` of
                                    :class:`str` or :class:`yarl.URL`
                                  - :class:`str`
                                  - :class:`yarl.URL`

      .. versionadded:: 3.8

   .. method:: update_cookies(cookies, response_url=None)

      Update cookies returned by server in ``Set-Cookie`` header.

      :param cookies: a :class:`collections.abc.Mapping`
         (e.g. :class:`dict`, :class:`~http.cookies.SimpleCookie`) or
         *iterable* of *pairs* with cookies returned by server's
         response.

      :param ~yarl.URL response_url: URL of response, ``None`` for *shared
         cookies*.  Regular cookies are coupled with server's URL and
         are sent only to this server, shared ones are sent in every
         client request.

   .. method:: filter_cookies(request_url)

      Return jar's cookies acceptable for URL and available in
      ``Cookie`` header for sending client requests for given URL.

      :param ~yarl.URL response_url: request's URL for which cookies are asked.

      :return: :class:`http.cookies.SimpleCookie` with filtered
         cookies for given URL.

   .. method:: save(file_path)

      Write a pickled representation of cookies into the file
      at provided path.

      :param file_path: Path to file where cookies will be serialized,
          :class:`str` or :class:`pathlib.Path` instance.

   .. method:: load(file_path)

      Load a pickled representation of cookies from the file
      at provided path.

      :param file_path: Path to file from where cookies will be
           imported, :class:`str` or :class:`pathlib.Path` instance.

   .. method:: clear(predicate=None)

      Removes all cookies from the jar if the predicate is ``None``. Otherwise remove only those :class:`~http.cookies.Morsel` that ``predicate(morsel)`` returns ``True``.

      :param predicate: callable that gets :class:`~http.cookies.Morsel` as a parameter and returns ``True`` if this :class:`~http.cookies.Morsel` must be deleted from the jar.

          .. versionadded:: 4.0

   .. method:: clear_domain(domain)

      Remove all cookies from the jar that belongs to the specified domain or its subdomains.

      :param str domain: domain for which cookies must be deleted from the jar.

      .. versionadded:: 4.0


.. class:: DummyCookieJar(*, loop=None)

   Dummy cookie jar which does not store cookies but ignores them.

   Could be useful e.g. for web crawlers to iterate over Internet
   without blowing up with saved cookies information.

   To install dummy cookie jar pass it into session instance::

      jar = aiohttp.DummyCookieJar()
      session = aiohttp.ClientSession(cookie_jar=DummyCookieJar())


.. class:: Fingerprint(digest)

   Fingerprint helper for checking SSL certificates by *SHA256* digest.

   :param bytes digest: *SHA256* digest for certificate in DER-encoded
                        binary form (see
                        :meth:`ssl.SSLSocket.getpeercert`).

   To check fingerprint pass the object into :meth:`ClientSession.get`
   call, e.g.::

      import hashlib

      with open(path_to_cert, 'rb') as f:
          digest = hashlib.sha256(f.read()).digest()

      await session.get(url, ssl=aiohttp.Fingerprint(digest))

   .. versionadded:: 3.0

.. function:: set_zlib_backend(lib)

   Sets the compression backend for zlib-based operations.

   This function allows you to override the default zlib backend
   used internally by passing a module that implements the standard
   compression interface.

   The module should implement at minimum the exact interface offered by the
   latest version of zlib.

   :param types.ModuleType lib: A module that implements the zlib-compatible compression API.

   Example usage::

      import zlib_ng.zlib_ng as zng
      import aiohttp

      aiohttp.set_zlib_backend(zng)

   .. note:: aiohttp has been tested internally with :mod:`zlib`, :mod:`zlib_ng.zlib_ng`, and :mod:`isal.isal_zlib`.

   .. versionadded:: 3.12

FormData
^^^^^^^^

A :class:`FormData` object contains the form data and also handles
encoding it into a body that is either ``multipart/form-data`` or
``application/x-www-form-urlencoded``. ``multipart/form-data`` is
used if at least one field is an :class:`io.IOBase` object or was
added with at least one optional argument to :meth:`add_field<aiohttp.FormData.add_field>`
(``content_type``, ``filename``, or ``content_transfer_encoding``).
Otherwise, ``application/x-www-form-urlencoded`` is used.

:class:`FormData` instances are callable and return a :class:`aiohttp.payload.Payload`
on being called.

.. class:: FormData(fields, quote_fields=True, charset=None)

   Helper class for multipart/form-data and application/x-www-form-urlencoded body generation.

   :param fields: A container for the key/value pairs of this form.

                  Possible types are:

                  - :class:`dict`
                  - :class:`tuple` or :class:`list`
                  - :class:`io.IOBase`, e.g. a file-like object
                  - :class:`multidict.MultiDict` or :class:`multidict.MultiDictProxy`

                  If it is a :class:`tuple` or :class:`list`, it must be a valid argument
                  for :meth:`add_fields<aiohttp.FormData.add_fields>`.

                  For :class:`dict`, :class:`multidict.MultiDict`, and :class:`multidict.MultiDictProxy`,
                  the keys and values must be valid `name` and `value` arguments to
                  :meth:`add_field<aiohttp.FormData.add_field>`, respectively.

   .. method:: add_field(name, value, content_type=None, filename=None,\
                         content_transfer_encoding=None)

      Add a field to the form.

      :param str name: Name of the field

      :param value: Value of the field

                    Possible types are:

                    - :class:`str`
                    - :class:`bytes`, :class:`bytearray`, or :class:`memoryview`
                    - :class:`io.IOBase`, e.g. a file-like object

      :param str content_type: The field's content-type header (optional)

      :param str filename: The field's filename (optional)

                           If this is not set and ``value`` is a :class:`bytes`, :class:`bytearray`,
                           or :class:`memoryview` object, the `name` argument is used as the filename
                           unless ``content_transfer_encoding`` is specified.

                           If ``filename`` is not set and ``value`` is an :class:`io.IOBase`
                           object, the filename is extracted from the object if possible.

      :param str content_transfer_encoding: The field's content-transfer-encoding
                                            header (optional)

   .. method:: add_fields(fields)

      Add one or more fields to the form.

      :param fields: An iterable containing:

                     - :class:`io.IOBase`, e.g. a file-like object
                     - :class:`multidict.MultiDict` or :class:`multidict.MultiDictProxy`
                     - :class:`tuple` or :class:`list` of length two, containing a name-value pair

Client exceptions
-----------------

Exception hierarchy has been significantly modified in version
2.0. aiohttp defines only exceptions that covers connection handling
and server response misbehaviors.  For developer specific mistakes,
aiohttp uses python standard exceptions like :exc:`ValueError` or
:exc:`TypeError`.

Reading a response content may raise a :exc:`ClientPayloadError`
exception. This exception indicates errors specific to the payload
encoding. Such as invalid compressed data, malformed chunked-encoded
chunks or not enough data that satisfy the content-length header.

All exceptions are available as members of *aiohttp* module.

.. exception:: ClientError

   Base class for all client specific exceptions.

   Derived from :exc:`Exception`


.. class:: ClientPayloadError

   This exception can only be raised while reading the response
   payload if one of these errors occurs:

   1. invalid compression
   2. malformed chunked encoding
   3. not enough data that satisfy ``Content-Length`` HTTP header.

   Derived from :exc:`ClientError`

.. exception:: InvalidURL

   URL used for fetching is malformed, e.g. it does not contain host
   part.

   Derived from :exc:`ClientError` and :exc:`ValueError`

   .. attribute:: url

      Invalid URL, :class:`yarl.URL` instance.

    .. attribute:: description

      Invalid URL description, :class:`str` instance or :data:`None`.

.. exception:: InvalidUrlClientError

   Base class for all errors related to client url.

   Derived from :exc:`InvalidURL`

.. exception:: RedirectClientError

   Base class for all errors related to client redirects.

   Derived from :exc:`ClientError`

.. exception:: NonHttpUrlClientError

   Base class for all errors related to non http client urls.

   Derived from :exc:`ClientError`

.. exception:: InvalidUrlRedirectClientError

   Redirect URL is malformed, e.g. it does not contain host part.

   Derived from :exc:`InvalidUrlClientError` and :exc:`RedirectClientError`

.. exception:: NonHttpUrlRedirectClientError

   Redirect URL does not contain http schema.

   Derived from :exc:`RedirectClientError` and :exc:`NonHttpUrlClientError`

Response errors
^^^^^^^^^^^^^^^

.. exception:: ClientResponseError

   These exceptions could happen after we get response from server.

   Derived from :exc:`ClientError`

   .. attribute:: request_info

      Instance of :class:`RequestInfo` object, contains information
      about request.

   .. attribute:: status

      HTTP status code of response (:class:`int`), e.g. ``400``.

   .. attribute:: message

      Message of response (:class:`str`), e.g. ``"OK"``.

   .. attribute:: headers

      Headers in response, a list of pairs.

   .. attribute:: history

      History from failed response, if available, else empty tuple.

      A :class:`tuple` of :class:`ClientResponse` objects used for
      handle redirection responses.

   .. attribute:: code

      HTTP status code of response (:class:`int`), e.g. ``400``.

      .. deprecated:: 3.1


.. class:: ContentTypeError

   Invalid content type.

   Derived from :exc:`ClientResponseError`

   .. versionadded:: 2.3


.. class:: TooManyRedirects

   Client was redirected too many times.

   Maximum number of redirects can be configured by using
   parameter ``max_redirects`` in :meth:`request<aiohttp.ClientSession.request>`.

   Derived from :exc:`ClientResponseError`

   .. versionadded:: 3.2


.. class:: WSServerHandshakeError

   Web socket server response error.

   Derived from :exc:`ClientResponseError`

.. exception:: WSMessageTypeError

   Received WebSocket message of unexpected type

   Derived from :exc:`TypeError`

Connection errors
^^^^^^^^^^^^^^^^^

.. class:: ClientConnectionError

   These exceptions related to low-level connection problems.

   Derived from :exc:`ClientError`

.. class:: ClientConnectionResetError

   Derived from :exc:`ClientConnectionError` and :exc:`ConnectionResetError`

.. class:: ClientOSError

   Subset of connection errors that are initiated by an :exc:`OSError`
   exception.

   Derived from :exc:`ClientConnectionError` and :exc:`OSError`

.. class:: ClientConnectorError

   Connector related exceptions.

   Derived from :exc:`ClientOSError`

.. class:: ClientConnectorDNSError

   DNS resolution error.

   Derived from :exc:`ClientConnectorError`

.. class:: ClientProxyConnectionError

   Derived from :exc:`ClientConnectorError`

.. class:: ClientSSLError

   Derived from :exc:`ClientConnectorError`

.. class:: ClientConnectorSSLError

   Response ssl error.

   Derived from :exc:`ClientSSLError` and :exc:`ssl.SSLError`

.. class:: ClientConnectorCertificateError

   Response certificate error.

   Derived from :exc:`ClientSSLError` and :exc:`ssl.CertificateError`

.. class:: UnixClientConnectorError

   Derived from :exc:`ClientConnectorError`

.. class:: ServerConnectionError

   Derived from :exc:`ClientConnectionError`

.. class:: ServerDisconnectedError

   Server disconnected.

   Derived from :exc:`~aiohttp.ServerConnectionError`

   .. attribute:: message

      Partially parsed HTTP message (optional).


.. class:: ServerFingerprintMismatch

   Server fingerprint mismatch.

   Derived from :exc:`ServerConnectionError`

.. class:: ServerTimeoutError

   Server operation timeout: read timeout, etc.

   To catch all timeouts, including the ``total`` timeout, use
   :exc:`asyncio.TimeoutError`.

   Derived from :exc:`ServerConnectionError` and :exc:`asyncio.TimeoutError`

.. class:: ConnectionTimeoutError

   Connection timeout on ``connect`` and ``sock_connect`` timeouts.

   Derived from :exc:`ServerTimeoutError`

.. class:: SocketTimeoutError

   Reading from socket timeout on ``sock_read`` timeout.

   Derived from :exc:`ServerTimeoutError`

Hierarchy of exceptions
^^^^^^^^^^^^^^^^^^^^^^^

* :exc:`ClientError`

  * :exc:`ClientConnectionError`

    * :exc:`ClientConnectionResetError`

    * :exc:`ClientOSError`

      * :exc:`ClientConnectorError`

        * :exc:`ClientProxyConnectionError`

        * :exc:`ClientConnectorDNSError`

        * :exc:`ClientSSLError`

          * :exc:`ClientConnectorCertificateError`

          * :exc:`ClientConnectorSSLError`

        * :exc:`UnixClientConnectorError`

    * :exc:`ServerConnectionError`

      * :exc:`ServerDisconnectedError`

      * :exc:`ServerFingerprintMismatch`

      * :exc:`ServerTimeoutError`

        * :exc:`ConnectionTimeoutError`

        * :exc:`SocketTimeoutError`

  * :exc:`ClientPayloadError`

  * :exc:`ClientResponseError`

    * :exc:`~aiohttp.ClientHttpProxyError`

    * :exc:`ContentTypeError`

    * :exc:`TooManyRedirects`

    * :exc:`WSServerHandshakeError`

  * :exc:`InvalidURL`

    * :exc:`InvalidUrlClientError`

      * :exc:`InvalidUrlRedirectClientError`

  * :exc:`NonHttpUrlClientError`

    * :exc:`NonHttpUrlRedirectClientError`

  * :exc:`RedirectClientError`

    * :exc:`InvalidUrlRedirectClientError`

    * :exc:`NonHttpUrlRedirectClientError`


Client Types
------------

.. type:: ClientMiddlewareType

   Type alias for client middleware functions. Middleware functions must have this signature::

      Callable[
          [ClientRequest, ClientHandlerType],
          Awaitable[ClientResponse]
      ]

.. type:: ClientHandlerType

   Type alias for client request handler functions::

      Callable[[ClientRequest], Awaitable[ClientResponse]]
````

## File: docs/client.rst
````
.. _aiohttp-client:

Client
======

.. currentmodule:: aiohttp

The page contains all information about aiohttp Client API:


.. toctree::
   :name: client
   :maxdepth: 3

   Quickstart <client_quickstart>
   Advanced Usage <client_advanced>
   Client Middleware Cookbook <client_middleware_cookbook>
   Reference <client_reference>
   Tracing Reference <tracing_reference>
   The aiohttp Request Lifecycle <http_request_lifecycle>
````

## File: docs/contributing-admins.rst
````
:orphan:

Instructions for aiohttp admins
===============================

This page is intended to document certain processes for admins of the aiohttp repository.
For regular contributors, return to :doc:`contributing`.

.. contents::
   :local:

Creating a new release
----------------------

.. note:: The example commands assume that ``origin`` refers to the ``aio-libs`` repository.

To create a new release:

#. Start on the branch for the release you are planning (e.g. ``3.8`` for v3.8.6): ``git checkout 3.8 && git pull``
#. Update the version number in ``__init__.py``.
#. Run ``towncrier``.
#. Check and cleanup the changes in ``CHANGES.rst``.
#. Checkout a new branch: e.g. ``git checkout -b release/v3.8.6``
#. Commit and create a PR. Verify the changelog and release notes look good on Read the Docs. Once PR is merged, continue.
#. Go back to the release branch: e.g. ``git checkout 3.8 && git pull``
#. Add a tag: e.g. ``git tag -a v3.8.6 -m 'Release 3.8.6' -s``
#. Push the tag: e.g. ``git push origin v3.8.6``
#. Monitor CI to ensure release process completes without errors.

Once released, we need to complete some cleanup steps (no further steps are needed for
non-stable releases though). If doing a patch release, we need to do the below steps twice,
first merge into the newer release branch (e.g. 3.8 into 3.9) and then to master
(e.g. 3.9 into master). If a new minor release, then just merge to master.

#. Switch to target branch: e.g. ``git checkout 3.9 && git pull``
#. Start a merge: e.g. ``git merge 3.8 --no-commit --no-ff --gpg-sign``
#. Carefully review the changes and revert anything that should not be included (most
   things outside the changelog).
#. To ensure change fragments are cleaned up properly, run: ``python tools/cleanup_changes.py``
#. Commit the merge (must be a normal merge commit, not squashed).
#. Push the branch directly to Github (because a PR would get squashed). When pushing,
   you may get a rejected message. Follow these steps to resolve:

  #. Checkout to a new branch and push: e.g. ``git checkout -b do-not-merge && git push``
  #. Open a *draft* PR with a title of 'DO NOT MERGE'.
  #. Once the CI has completed on that branch, you should be able to switch back and push
     the target branch (as tests have passed on the merge commit now).
  #. This should automatically consider the PR merged and delete the temporary branch.

Back on the original release branch, bump the version number and append ``.dev0`` in ``__init__.py``.

Post the release announcement to social media:
 - BlueSky: https://bsky.app/profile/aiohttp.org and re-post to https://bsky.app/profile/aio-libs.org
 - Mastodon: https://fosstodon.org/@aiohttp and re-post to https://fosstodon.org/@aio_libs

If doing a minor release:

#. Create a new release branch for future features to go to: e.g. ``git checkout -b 3.10 3.9 && git push``
#. Update both ``target-branch`` backports for Dependabot to reference the new branch name in ``.github/dependabot.yml``.
#. Delete the older backport label (e.g. backport-3.8): https://github.com/aio-libs/aiohttp/labels
#. Add a new backport label (e.g. backport-3.10).
````

## File: docs/contributing.rst
````
.. _aiohttp-contributing:

Contributing
============

(:doc:`contributing-admins`)

Instructions for contributors
-----------------------------

In order to make a clone of the GitHub_ repo: open the link and press the "Fork" button on the upper-right menu of the web page.

I hope everybody knows how to work with git and github nowadays :)

Workflow is pretty straightforward:

  0. Make sure you are reading the latest version of this document.
     It can be found in the GitHub_ repo in the ``docs`` subdirectory.

  1. Clone the GitHub_ repo using the ``--recurse-submodules`` argument

  2. Setup your machine with the required development environment

  3. Make a change

  4. Make sure all tests passed

  5. Add a file into the ``CHANGES`` folder (see `Changelog update`_ for how).

  6. Commit changes to your own aiohttp clone

  7. Make a pull request from the github page of your clone against the master branch

  8. Optionally make backport Pull Request(s) for landing a bug fix into released aiohttp versions.

.. note::

   The project uses *Squash-and-Merge* strategy for *GitHub Merge* button.

   Basically it means that there is **no need to rebase** a Pull Request against
   *master* branch. Just ``git merge`` *master* into your working copy (a fork) if
   needed. The Pull Request is automatically squashed into the single commit
   once the PR is accepted.

.. note::

   GitHub issue and pull request threads are automatically locked when there has
   not been any recent activity for one year.  Please open a `new issue
   <https://github.com/aio-libs/aiohttp/issues/new>`_ for related bugs.

   If you feel like there are important points in the locked discussions,
   please include those excerpts into that new issue.


Preconditions for running aiohttp test suite
--------------------------------------------

We expect you to use a python virtual environment to run our tests.

There are several ways to make a virtual environment.

If you like to use *virtualenv* please run:

.. code-block:: shell

   $ cd aiohttp
   $ virtualenv --python=`which python3` venv
   $ . venv/bin/activate

For standard python *venv*:

.. code-block:: shell

   $ cd aiohttp
   $ python3 -m venv venv
   $ . venv/bin/activate

For *virtualenvwrapper*:

.. code-block:: shell

   $ cd aiohttp
   $ mkvirtualenv --python=`which python3` aiohttp

There are other tools like *pyvenv* but you know the rule of thumb now: create a python3 virtual environment and activate it.

After that please install libraries required for development:

.. code-block:: shell

   $ make install-dev

.. note::

  For now, the development tooling depends on ``make`` and assumes an Unix OS If you wish to contribute to aiohttp from a Windows machine, the easiest way is probably to `configure the WSL <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_ so you can use the same instructions. If it's not possible for you or if it doesn't work, please contact us so we can find a solution together.

Install pre-commit hooks:

.. code-block:: shell

   $ pre-commit install

.. warning::

  If you plan to use temporary ``print()``, ``pdb`` or ``ipdb`` within the test suite, execute it with ``-s``:

  .. code-block:: shell

     $ pytest tests -s

  in order to run the tests without output capturing.

Congratulations, you are ready to run the test suite!

.. include:: ../vendor/README.rst


Run autoformatter
-----------------

The project uses black_ + isort_ formatters to keep the source code style.
Please run `make fmt` after every change before starting tests.

  .. code-block:: shell

     $ make fmt


Run aiohttp test suite
----------------------

After all the preconditions are met you can run tests typing the next
command:

.. code-block:: shell

   $ make test

The command at first will run the *linters* (sorry, we don't accept
pull requests with pyflakes, black, isort, or mypy errors).

On *lint* success the tests will be run.

Please take a look on the produced output.

Any extra texts (print statements and so on) should be removed.

.. note::

   If you see that CI build is failing on a specific Python version and
   you don't have this version on your computer, you can use the helper to
   run it (only if you have docker)::

     make test-<python-version>[-no-extensions]

   For example, if you want to run tests for python3.10
   without extensions, you can run this command::

     make test-3.10-no-extensions

Code coverage
-------------

We use *codecov.io* as an indispensable tool for analyzing our coverage
results. Visit https://codecov.io/gh/aio-libs/aiohttp to see coverage
reports for the master branch, history, pull requests etc.

We'll use an example from a real PR to demonstrate how we use this.
Once the tests run in a PR, you'll see a comment posted by *codecov*.
The most important thing to check here is whether there are any new
missed or partial lines in the report:

.. image:: _static/img/contributing-cov-comment.svg

Here, the PR has introduced 1 miss and 2 partials. Now we
click the link in the comment header to open the full report:

.. image:: _static/img/contributing-cov-header.svg
   :alt: Codecov report

Now, if we look through the diff under 'Files changed' we find one of
our partials:

.. image:: _static/img/contributing-cov-partial.svg
   :alt: A while loop with partial coverage.

In this case, the while loop is never skipped in our tests. This is
probably not worth writing a test for (and may be a situation that is
impossible to trigger anyway), so we leave this alone.

We're still missing a partial and a miss, so we switch to the
'Indirect changes' tab and take a look through the diff there. This
time we find the remaining 2 lines:

.. image:: _static/img/contributing-cov-miss.svg
   :alt: An if statement that isn't covered anymore.

After reviewing the PR, we find that this code is no longer needed as
the changes mean that this method will never be called under those
conditions. Thanks to this report, we were able to remove some
redundant code from a performance-critical part of our codebase (this
check would have been run, probably multiple times, for every single
incoming request).

.. tip::
   Sometimes the diff on *codecov.io* doesn't make sense. This is usually
   caused by the branch being out of sync with master. Try merging
   master into the branch and it will likely fix the issue. Failing
   that, try checking coverage locally as described in the next section.

Other tools
-----------

The browser extension https://docs.codecov.io/docs/browser-extension
is also a useful tool for analyzing the coverage directly from *Files
Changed* tab on the *GitHub Pull Request* review page.


You can also produce coverage reports locally with ``make cov-dev``
or just adding ``--cov-report=html`` to ``pytest``.

This will run the test suite and collect coverage information. Once
finished, coverage results can be view by opening:
```console
$ python -m webbrowser -n file://"$(pwd)"/htmlcov/index.html
```

Documentation
-------------

We encourage documentation improvements.

Please before making a Pull Request about documentation changes run:

.. code-block:: shell

   $ make doc

Once it finishes it will output the index html page
``open file:///.../aiohttp/docs/_build/html/index.html``.

Go to the link and make sure your doc changes looks good.

Spell checking
--------------

We use ``pyenchant`` and ``sphinxcontrib-spelling`` for running spell
checker for documentation:

.. code-block:: shell

   $ make doc-spelling

Unfortunately there are problems with running spell checker on MacOS X.

To run spell checker on Linux box you should install it first:

.. code-block:: shell

   $ sudo apt-get install enchant
   $ pip install sphinxcontrib-spelling


Preparing a pull request
------------------------

When making a pull request, please include a short summary of the changes
and a reference to any issue tickets that the PR is intended to solve.
All PRs with code changes should include tests. All changes should
include a changelog entry.


Changelog update
----------------

.. include:: ../CHANGES/README.rst


Making a pull request
---------------------

After finishing all steps make a GitHub_ Pull Request with *master* base branch.


Backporting
-----------

All Pull Requests are created against *master* git branch.

If the Pull Request is not a new functionality but bug fixing
*backport* to maintenance branch would be desirable.

*aiohttp* project committer may ask for making a *backport* of the PR
into maintained branch(es), in this case he or she adds a github label
like *needs backport to 3.1*.

*Backporting* is performed *after* main PR merging into master.
 Please do the following steps:

1. Find *Pull Request's commit* for cherry-picking.

   *aiohttp* does *squashing* PRs on merging, so open your PR page on
   github and scroll down to message like ``asvetlov merged commit
   f7b8921 into master 9 days ago``.  ``f7b8921`` is the required commit number.

2. Run `cherry_picker
   <https://github.com/python/core-workflow/tree/master/cherry_picker>`_
   tool for making backport PR (the tool is already pre-installed from
   ``./requirements/dev.txt``), e.g. ``cherry_picker f7b8921 3.1``.

3. In case of conflicts fix them and continue cherry-picking by
   ``cherry_picker --continue``.

   ``cherry_picker --abort`` stops the process.

   ``cherry_picker --status`` shows current cherry-picking status
   (like ``git status``)

4. After all conflicts are done the tool opens a New Pull Request page
   in a browser with pre-filed information.  Create a backport Pull
   Request and wait for review/merging.

5. *aiohttp* *committer* should remove *backport Git label* after
   merging the backport.

How to become an aiohttp committer
----------------------------------

Contribute!

The easiest way is providing Pull Requests for issues in our bug
tracker.  But if you have a great idea for the library improvement
-- please make an issue and Pull Request.



The rules for committers are simple:

1. No wild commits! Everything should go through PRs.
2. Take a part in reviews. It's very important part of maintainer's activity.
3. Pickup issues created by others, especially if they are simple.
4. Keep test suite comprehensive. In practice it means leveling up
   coverage. 97% is not bad but we wish to have 100% someday. Well, 99%
   is good target too.
5. Don't hesitate to improve our docs. Documentation is a very important
   thing, it's the key for project success. The documentation should
   not only cover our public API but help newbies to start using the
   project and shed a light on non-obvious gotchas.



After positive answer aiohttp committer creates an issue on github
with the proposal for nomination.  If the proposal will collect only
positive votes and no strong objection -- you'll be a new member in
our team.


.. _GitHub: https://github.com/aio-libs/aiohttp

.. _ipdb: https://pypi.python.org/pypi/ipdb

.. _black: https://pypi.python.org/pypi/black

.. _isort: https://pypi.python.org/pypi/isort
````

## File: docs/deployment.rst
````
.. _aiohttp-deployment:

=================
Server Deployment
=================

There are several options for aiohttp server deployment:

* Standalone server

* Running a pool of backend servers behind of :term:`nginx`, HAProxy
  or other *reverse proxy server*

* Using :term:`gunicorn` behind of *reverse proxy*

Every method has own benefits and disadvantages.


.. _aiohttp-deployment-standalone:

Standalone
==========

Just call :func:`aiohttp.web.run_app` function passing
:class:`aiohttp.web.Application` instance.


The method is very simple and could be the best solution in some
trivial cases. But it does not utilize all CPU cores.

For running multiple aiohttp server instances use *reverse proxies*.

.. _aiohttp-deployment-nginx-supervisord:

Nginx+supervisord
=================

Running aiohttp servers behind :term:`nginx` makes several advantages.

First, nginx is the perfect frontend server. It may prevent many
attacks based on malformed http protocol etc.

Second, running several aiohttp instances behind nginx allows to
utilize all CPU cores.

Third, nginx serves static files much faster than built-in aiohttp
static file support.

But this way requires more complex configuration.

Nginx configuration
--------------------

Here is short example of an Nginx configuration file.
It does not cover all available Nginx options.

For full details, read `Nginx tutorial
<https://www.nginx.com/resources/admin-guide/>`_ and `official Nginx
documentation
<http://nginx.org/en/docs/http/ngx_http_proxy_module.html>`_.

First configure HTTP server itself:

.. code-block:: nginx

   http {
     server {
       listen 80;
       client_max_body_size 4G;

       server_name example.com;

       location / {
         proxy_set_header Host $http_host;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_redirect off;
         proxy_buffering off;
         proxy_pass http://aiohttp;
       }

       location /static {
         # path for static files
         root /path/to/app/static;
       }

     }
   }

This config listens on port ``80`` for a server named ``example.com``
and redirects everything to the ``aiohttp`` backend group.

Also it serves static files from ``/path/to/app/static`` path as
``example.com/static``.

Next we need to configure *aiohttp upstream group*:

.. code-block:: nginx

   http {
     upstream aiohttp {
       # fail_timeout=0 means we always retry an upstream even if it failed
       # to return a good HTTP response

       # Unix domain servers
       server unix:/tmp/example_1.sock fail_timeout=0;
       server unix:/tmp/example_2.sock fail_timeout=0;
       server unix:/tmp/example_3.sock fail_timeout=0;
       server unix:/tmp/example_4.sock fail_timeout=0;

       # Unix domain sockets are used in this example due to their high performance,
       # but TCP/IP sockets could be used instead:
       # server 127.0.0.1:8081 fail_timeout=0;
       # server 127.0.0.1:8082 fail_timeout=0;
       # server 127.0.0.1:8083 fail_timeout=0;
       # server 127.0.0.1:8084 fail_timeout=0;
     }
   }

All HTTP requests for ``http://example.com`` except ones for
``http://example.com/static`` will be redirected to ``example1.sock``,
``example2.sock``, ``example3.sock`` or ``example4.sock``
backend servers. By default, Nginx uses round-robin algorithm for backend
selection.

.. note::

   Nginx is not the only existing *reverse proxy server*, but it's the most
   popular one.  Alternatives like HAProxy may be used as well.

Supervisord
-----------

After configuring Nginx we need to start our aiohttp backends. It's best
to use some tool for starting them automatically after a system reboot
or backend crash.

There are many ways to do it: Supervisord, Upstart, Systemd,
Gaffer, Circus, Runit etc.

Here we'll use `Supervisord <http://supervisord.org/>`_ as an example:

.. code-block:: cfg

   [program:aiohttp]
   numprocs = 4
   numprocs_start = 1
   process_name = example_%(process_num)s

   ; Unix socket paths are specified by command line.
   command=/path/to/aiohttp_example.py --path=/tmp/example_%(process_num)s.sock

   ; We can just as easily pass TCP port numbers:
   ; command=/path/to/aiohttp_example.py --port=808%(process_num)s

   user=nobody
   autostart=true
   autorestart=true

aiohttp server
--------------

The last step is preparing the aiohttp server to work with supervisord.

Assuming we have properly configured :class:`aiohttp.web.Application`
and port is specified by command line, the task is trivial:

.. code-block:: python3

   # aiohttp_example.py
   import argparse
   from aiohttp import web

   parser = argparse.ArgumentParser(description="aiohttp server example")
   parser.add_argument('--path')
   parser.add_argument('--port')


   if __name__ == '__main__':
       app = web.Application()
       # configure app

       args = parser.parse_args()
       web.run_app(app, path=args.path, port=args.port)

For real use cases we perhaps need to configure other things like
logging etc., but it's out of scope of the topic.


.. _aiohttp-deployment-gunicorn:

Nginx+Gunicorn
==============

aiohttp can be deployed using `Gunicorn
<http://docs.gunicorn.org/en/latest/index.html>`_, which is based on a
pre-fork worker model.  Gunicorn launches your app as worker processes
for handling incoming requests.

As opposed to deployment with :ref:`bare Nginx
<aiohttp-deployment-nginx-supervisord>`, this solution does not need to
manually run several aiohttp processes and use a tool like supervisord
to monitor them. But nothing is free: running aiohttp
application under gunicorn is slightly slower.


Prepare environment
-------------------

You first need to setup your deployment environment. This example is
based on `Ubuntu <https://www.ubuntu.com/>`_ 16.04.

Create a directory for your application::

  >> mkdir myapp
  >> cd myapp

Create a Python virtual environment::

  >> python3 -m venv venv
  >> source venv/bin/activate

Now that the virtual environment is ready, we'll proceed to install
aiohttp and gunicorn::

  >> pip install gunicorn
  >> pip install aiohttp


Application
-----------

Lets write a simple application, which we will save to file. We'll
name this file *my_app_module.py*::

   from aiohttp import web

   async def index(request):
       return web.Response(text="Welcome home!")


   my_web_app = web.Application()
   my_web_app.router.add_get('/', index)


Application factory
-------------------

As an option an entry point could be a coroutine that accepts no
parameters and returns an application instance::

   from aiohttp import web

   async def index(request):
       return web.Response(text="Welcome home!")


   async def my_web_app():
       app = web.Application()
       app.router.add_get('/', index)
       return app


Start Gunicorn
--------------

When `Running Gunicorn
<http://docs.gunicorn.org/en/latest/run.html>`_, you provide the name
of the module, i.e. *my_app_module*, and the name of the app or
application factory, i.e. *my_web_app*, along with other `Gunicorn
Settings <http://docs.gunicorn.org/en/latest/settings.html>`_ provided
as command line flags or in your config file.

In this case, we will use:

* the ``--bind`` flag to set the server's socket address;
* the ``--worker-class`` flag to tell Gunicorn that we want to use a
  custom worker subclass instead of one of the Gunicorn default worker
  types;
* you may also want to use the ``--workers`` flag to tell Gunicorn how
  many worker processes to use for handling requests. (See the
  documentation for recommendations on `How Many Workers?
  <http://docs.gunicorn.org/en/latest/design.html#how-many-workers>`_)
* you may also want to use the ``--accesslog`` flag to enable the access
  log to be populated. (See :ref:`logging <gunicorn-accesslog>` for more information.)

The custom worker subclass is defined in ``aiohttp.GunicornWebWorker``::

  >> gunicorn my_app_module:my_web_app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker
  [2017-03-11 18:27:21 +0000] [1249] [INFO] Starting gunicorn 19.7.1
  [2017-03-11 18:27:21 +0000] [1249] [INFO] Listening at: http://127.0.0.1:8080 (1249)
  [2017-03-11 18:27:21 +0000] [1249] [INFO] Using worker: aiohttp.worker.GunicornWebWorker
  [2015-03-11 18:27:21 +0000] [1253] [INFO] Booting worker with pid: 1253

Gunicorn is now running and ready to serve requests to your app's
worker processes.

.. note::

   If you want to use an alternative asyncio event loop
   `uvloop <https://github.com/MagicStack/uvloop>`_, you can use the
   ``aiohttp.GunicornUVLoopWebWorker`` worker class.

Proxy through NGINX
----------------------

We can proxy our gunicorn workers through NGINX with a configuration like this:

.. code-block:: nginx

    worker_processes 1;
    user nobody nogroup;
    events {
        worker_connections 1024;
    }
    http {
        ## Main Server Block
        server {
            ## Open by default.
            listen                80 default_server;
            server_name           main;
            client_max_body_size  200M;

            ## Main site location.
            location / {
                proxy_pass                          http://127.0.0.1:8080;
                proxy_set_header                    Host $host;
                proxy_set_header X-Forwarded-Host   $server_name;
                proxy_set_header X-Real-IP          $remote_addr;
            }
        }
    }

Since gunicorn listens for requests at our localhost address on port 8080, we can
use the `proxy_pass <https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass>`_
directive to send web traffic to our workers. If everything is configured correctly,
we should reach our application at the ip address of our web server.

Proxy through NGINX + SSL
----------------------------

Here is an example NGINX configuration setup to accept SSL connections:

.. code-block:: nginx

    worker_processes 1;
    user nobody nogroup;
    events {
        worker_connections 1024;
    }
    http {
        ## SSL Redirect
        server {
            listen 80       default;
            return 301      https://$host$request_uri;
        }

        ## Main Server Block
        server {
            # Open by default.
            listen                443 ssl default_server;
            listen                [::]:443 ssl default_server;
            server_name           main;
            client_max_body_size  200M;

            ssl_certificate       /etc/secrets/cert.pem;
            ssl_certificate_key   /etc/secrets/key.pem;

            ## Main site location.
            location / {
                proxy_pass                          http://127.0.0.1:8080;
                proxy_set_header                    Host $host;
                proxy_set_header X-Forwarded-Host   $server_name;
                proxy_set_header X-Real-IP          $remote_addr;
            }
        }
    }


The first server block accepts regular http connections on port 80 and redirects
them to our secure SSL connection. The second block matches our previous example
except we need to change our open port to https and specify where our SSL
certificates are being stored with the ``ssl_certificate`` and ``ssl_certificate_key``
directives.

During development, you may want to `create your own self-signed certificates for testing purposes <https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04>`_
and use another service like `Let's Encrypt <https://letsencrypt.org/>`_ when you
are ready to move to production.

More information
----------------

See the `official documentation
<http://docs.gunicorn.org/en/latest/deploy.html>`_ for more
information about suggested nginx configuration. You can also find out more about
`configuring for secure https connections as well. <https://nginx.org/en/docs/http/configuring_https_servers.html>`_

Logging configuration
---------------------

``aiohttp`` and ``gunicorn`` use different format for specifying access log.

By default aiohttp uses own defaults::

   '%a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"'

For more information please read :ref:`Format Specification for Access
Log <aiohttp-logging-access-log-format-spec>`.


Proxy through Apache at your own risk
-------------------------------------
Issues have been reported using Apache2 in front of aiohttp server:
`#2687 Intermittent 502 proxy errors when running behind Apache <https://github.com/aio-libs/aiohttp/issues/2687>`.
````

## File: docs/essays.rst
````
Essays
======


.. toctree::

   new_router
   whats_new_1_1
   migration_to_2xx
   whats_new_3_0
````

## File: docs/external.rst
````
Who uses aiohttp?
=================

The list of *aiohttp* users: both libraries, big projects and web sites.

Please don't hesitate to add your awesome project to the list by
making a Pull Request on GitHub_.

If you like the project -- please go to GitHub_ and press *Star* button!


.. toctree::

   third_party
   built_with
   powered_by

.. _GitHub: https://github.com/aio-libs/aiohttp
````

## File: docs/faq.rst
````
FAQ
===

.. contents::
   :local:

Are there plans for an @app.route decorator like in Flask?
----------------------------------------------------------

As of aiohttp 2.3, :class:`~aiohttp.web.RouteTableDef` provides an API
similar to Flask's ``@app.route``. See
:ref:`aiohttp-web-alternative-routes-definition`.

Unlike Flask's ``@app.route``, :class:`~aiohttp.web.RouteTableDef`
does not require an ``app`` in the module namespace (which often leads
to circular imports).

Instead, a :class:`~aiohttp.web.RouteTableDef` is decoupled from an application instance::

   routes = web.RouteTableDef()

   @routes.get('/get')
   async def handle_get(request):
       ...


   @routes.post('/post')
   async def handle_post(request):
       ...

   app.router.add_routes(routes)


Does aiohttp have a concept like Flask's "blueprint" or Django's "app"?
-----------------------------------------------------------------------

If you're writing a large application, you may want to consider
using :ref:`nested applications <aiohttp-web-nested-applications>`, which
are similar to Flask's "blueprints" or Django's "apps".

See: :ref:`aiohttp-web-nested-applications`.


How do I create a route that matches urls with a given prefix?
--------------------------------------------------------------

You can do something like the following: ::

    app.router.add_route('*', '/path/to/{tail:.+}', sink_handler)

The first argument, ``*``,  matches any HTTP method
(*GET, POST, OPTIONS*, etc). The second argument matches URLS with the desired prefix.
The third argument is the handler function.


Where do I put my database connection so handlers can access it?
----------------------------------------------------------------

:class:`aiohttp.web.Application` object supports the :class:`dict`
interface and provides a place to store your database connections or any
other resource you want to share between handlers.
::

    db_key = web.AppKey("db_key", DB)

    async def go(request):
        db = request.app[db_key]
        cursor = await db.cursor()
        await cursor.execute('SELECT 42')
        # ...
        return web.Response(status=200, text='ok')


    async def init_app():
        app = Application()
        db = await create_connection(user='user', password='123')
        app[db_key] = db
        app.router.add_get('/', go)
        return app


How can middleware store data for web handlers to use?
------------------------------------------------------

Both :class:`aiohttp.web.Request`  and :class:`aiohttp.web.Application`
support the :class:`dict` interface.

Therefore, data may be stored inside a request object. ::

   async def handler(request):
       request['unique_key'] = data

See https://github.com/aio-libs/aiohttp_session code for an example.
The ``aiohttp_session.get_session(request)`` method uses ``SESSION_KEY``
for saving request-specific session information.

As of aiohttp 3.0, all response objects are dict-like structures as
well.


.. _aiohttp_faq_parallel_event_sources:

Can a handler receive incoming events from different sources in parallel?
-------------------------------------------------------------------------

Yes.

As an example, we may have two event sources:

   1. WebSocket for events from an end user

   2. Redis PubSub for events from other parts of the application

The most native way to handle this is to create a separate task for
PubSub handling.

Parallel :meth:`aiohttp.web.WebSocketResponse.receive` calls are forbidden;
a single task should perform WebSocket reading.
However, other tasks may use the same WebSocket object for sending data to
peers. ::

    async def handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        task = asyncio.create_task(
            read_subscription(ws, request.app[redis_key]))
        try:
            async for msg in ws:
                # handle incoming messages
                # use ws.send_str() to send data back
                ...

        finally:
            task.cancel()

    async def read_subscription(ws, redis):
        channel, = await redis.subscribe('channel:1')

        try:
            async for msg in channel.iter():
                answer = process_the_message(msg)  # your function here
                await ws.send_str(answer)
        finally:
            await redis.unsubscribe('channel:1')


.. _aiohttp_faq_terminating_websockets:

How do I programmatically close a WebSocket server-side?
--------------------------------------------------------

Let's say we have an application with two endpoints:


   1. ``/echo`` a WebSocket echo server that authenticates the user
   2. ``/logout_user`` that, when invoked, closes all open
      WebSockets for that user.

One simple solution is to keep a shared registry of WebSocket
responses for a user in the :class:`aiohttp.web.Application` instance
and call :meth:`aiohttp.web.WebSocketResponse.close` on all of them in
``/logout_user`` handler::

    async def echo_handler(request):

        ws = web.WebSocketResponse()
        user_id = authenticate_user(request)
        await ws.prepare(request)
        request.app[websockets_key][user_id].add(ws)
        try:
            async for msg in ws:
                ws.send_str(msg.data)
        finally:
            request.app[websockets_key][user_id].remove(ws)

        return ws


    async def logout_handler(request):

        user_id = authenticate_user(request)

        ws_closers = [ws.close()
                      for ws in request.app[websockets_key][user_id]
                      if not ws.closed]

        # Watch out, this will keep us from returning the response
        # until all are closed
        ws_closers and await asyncio.gather(*ws_closers)

        return web.Response(text='OK')


    def main():
        loop = asyncio.get_event_loop()
        app = web.Application()
        app.router.add_route('GET', '/echo', echo_handler)
        app.router.add_route('POST', '/logout', logout_handler)
        app[websockets_key] = defaultdict(set)
        web.run_app(app, host='localhost', port=8080)


How do I make a request from a specific IP address?
---------------------------------------------------

If your system has several IP interfaces, you may choose one which will
be used used to bind a socket locally::

    conn = aiohttp.TCPConnector(local_addr=('127.0.0.1', 0))
    async with aiohttp.ClientSession(connector=conn) as session:
        ...

.. seealso:: :class:`aiohttp.TCPConnector` and ``local_addr`` parameter.


What is the API stability and deprecation policy?
-------------------------------------------------

*aiohttp* follows strong `Semantic Versioning <https://semver.org>`_ (SemVer).

Obsolete attributes and methods are marked as *deprecated* in the
documentation and raise :class:`DeprecationWarning` upon usage.

Assume aiohttp ``X.Y.Z`` where ``X`` is major version,
``Y`` is minor version and ``Z`` is bugfix number.

For example, if the latest released version is ``aiohttp==3.0.6``:

``3.0.7`` fixes some bugs but have no new features.

``3.1.0`` introduces new features and can deprecate some API but never
remove it, also all bug fixes from previous release are merged.

``4.0.0`` removes all deprecations collected from ``3.Y`` versions
**except** deprecations from the **last** ``3.Y`` release. These
deprecations will be removed by ``5.0.0``.

Unfortunately we may have to break these rules when a **security
vulnerability** is found.
If a security problem cannot be fixed without breaking backward
compatibility, a bugfix release may break compatibility. This is unlikely, but
possible.

All backward incompatible changes are explicitly marked in
:ref:`the changelog <aiohttp_changes>`.


How do I enable gzip compression globally for my entire application?
--------------------------------------------------------------------

It's impossible. Choosing what to compress and what not to compress
is a tricky matter.

If you need global compression, write a custom middleware. Or
enable compression in NGINX (you are deploying aiohttp behind reverse
proxy, right?).


How do I manage a ClientSession within a web server?
----------------------------------------------------

:class:`aiohttp.ClientSession` should be created once for the lifetime
of the server in order to benefit from connection pooling.

Sessions save cookies internally. If you don't need cookie processing,
use :class:`aiohttp.DummyCookieJar`. If you need separate cookies
for different http calls but process them in logical chains, use a single
:class:`aiohttp.TCPConnector` with separate
client sessions and ``connector_owner=False``.


How do I access database connections from a subapplication?
-----------------------------------------------------------

Restricting access from subapplication to main (or outer) app is a
deliberate choice.

A subapplication is an isolated unit by design. If you need to share a
database object, do it explicitly::

   subapp[db_key] = mainapp[db_key]
   mainapp.add_subapp("/prefix", subapp)

This can also be done from a :ref:`cleanup context<aiohttp-web-cleanup-ctx>`::

   async def db_context(app: web.Application) -> AsyncIterator[None]:
      async with create_db() as db:
         mainapp[db_key] = mainapp[subapp_key][db_key] = db
         yield

   mainapp[subapp_key] = subapp
   mainapp.add_subapp("/prefix", subapp)
   mainapp.cleanup_ctx.append(db_context)


How do I perform operations in a request handler after sending the response?
----------------------------------------------------------------------------

Middlewares can be written to handle post-response operations, but
they run after every request. You can explicitly send the response by
calling :meth:`aiohttp.web.Response.write_eof`, which starts sending
before the handler returns, giving you a chance to execute follow-up
operations::

    def ping_handler(request):
        """Send PONG and increase DB counter."""

        # explicitly send the response
        resp = web.json_response({'message': 'PONG'})
        await resp.prepare(request)
        await resp.write_eof()

        # increase the pong count
        request.app[db_key].inc_pong()

        return resp

A :class:`aiohttp.web.Response` object must be returned. This is
required by aiohttp web contracts, even though the response has
already been sent.


How do I make sure my custom middleware response will behave correctly?
------------------------------------------------------------------------

Sometimes your middleware handlers might need to send a custom response.
This is just fine as long as you always create a new
:class:`aiohttp.web.Response` object when required.

The response object is a Finite State Machine. Once it has been dispatched
by the server, it will reach its final state and cannot be used again.

The following middleware will make the server hang, once it serves the second
response::

    from aiohttp import web

    def misbehaved_middleware():
        # don't do this!
        cached = web.Response(status=200, text='Hi, I am cached!')

        async def middleware(request, handler):
            # ignoring response for the sake of this example
            _res = handler(request)
            return cached

        return middleware

The rule of thumb is *one request, one response*.


Why is creating a ClientSession outside of an event loop dangerous?
-------------------------------------------------------------------

Short answer is: life-cycle of all asyncio objects should be shorter
than life-cycle of event loop.

Full explanation is longer.  All asyncio object should be correctly
finished/disconnected/closed before event loop shutdown.  Otherwise
user can get unexpected behavior. In the best case it is a warning
about unclosed resource, in the worst case the program just hangs,
awaiting for coroutine is never resumed etc.

Consider the following code from ``mod.py``::

    import aiohttp

    session = aiohttp.ClientSession()

    async def fetch(url):
        async with session.get(url) as resp:
            return await resp.text()

The session grabs current event loop instance and stores it in a
private variable.

The main module imports the module and installs ``uvloop`` (an
alternative fast event loop implementation).

``main.py``::

    import asyncio
    import uvloop
    import mod

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())

The code is broken: ``session`` is bound to default ``asyncio`` loop
on import time but the loop is changed **after the import** by
``set_event_loop()``.  As result ``fetch()`` call hangs.


To avoid import dependency hell *aiohttp* encourages creation of
``ClientSession`` from async function.  The same policy works for
``web.Application`` too.

Another use case is unit test writing.  Very many test libraries
(*aiohttp test tools* first) creates a new loop instance for every
test function execution.  It's done for sake of tests isolation.
Otherwise pending activity (timers, network packets etc.) from
previous test may interfere with current one producing very cryptic
and unstable test failure.

Note: *class variables* are hidden globals actually. The following
code has the same problem as ``mod.py`` example, ``session`` variable
is the hidden global object::

    class A:
        session = aiohttp.ClientSession()

        async def fetch(self, url):
            async with session.get(url) as resp:
                return await resp.text()
````

## File: docs/glossary.rst
````
.. _aiohttp-glossary:


==========
 Glossary
==========

.. if you add new entries, keep the alphabetical sorting!

.. glossary::
   :sorted:

   aiodns

      DNS resolver for asyncio.

      https://pypi.python.org/pypi/aiodns

   asyncio

      The library for writing single-threaded concurrent code using
      coroutines, multiplexing I/O access over sockets and other
      resources, running network clients and servers, and other
      related primitives.

      Reference implementation of :pep:`3156`

      https://pypi.python.org/pypi/asyncio/

   Brotli

      Brotli is a generic-purpose lossless compression algorithm that
      compresses data using a combination of a modern variant
      of the LZ77 algorithm, Huffman coding and second order context modeling,
      with a compression ratio comparable to the best currently available
      general-purpose compression methods. It is similar in speed with deflate
      but offers more dense compression.

      The specification of the Brotli Compressed Data Format is defined :rfc:`7932`

      https://pypi.org/project/Brotli/

   brotlicffi

      An alternative implementation of :term:`Brotli` built using the CFFI
      library. This implementation supports PyPy correctly.

      https://pypi.org/project/brotlicffi/

   callable

      Any object that can be called. Use :func:`callable` to check
      that.

   gunicorn

       Gunicorn 'Green Unicorn' is a Python WSGI HTTP Server for
       UNIX.

       http://gunicorn.org/

   IDNA

       An Internationalized Domain Name in Applications (IDNA) is an
       industry standard for encoding Internet Domain Names that contain in
       whole or in part, in a language-specific script or alphabet,
       such as Arabic, Chinese, Cyrillic, Tamil, Hebrew or the Latin
       alphabet-based characters with diacritics or ligatures, such as
       French. These writing systems are encoded by computers in
       multi-byte Unicode. Internationalized domain names are stored
       in the Domain Name System as ASCII strings using Punycode
       transcription.

   keep-alive

       A technique for communicating between HTTP client and server
       when connection is not closed after sending response but kept
       open for sending next request through the same socket.

       It makes communication faster by getting rid of connection
       establishment for every request.



   nginx

      Nginx [engine x] is an HTTP and reverse proxy server, a mail
      proxy server, and a generic TCP/UDP proxy server.

      https://nginx.org/en/

   percent-encoding

      A mechanism for encoding information in a Uniform Resource
      Locator (URL) if URL parts don't fit in safe characters space.

   requests

      Currently the most popular synchronous library to make
      HTTP requests in Python.

      https://requests.readthedocs.io

   requoting

      Applying :term:`percent-encoding` to non-safe symbols and decode
      percent encoded safe symbols back.

      According to :rfc:`3986` allowed path symbols are::

         allowed       = unreserved / pct-encoded / sub-delims
                         / ":" / "@" / "/"

         pct-encoded   = "%" HEXDIG HEXDIG

         unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"

         sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
                         / "*" / "+" / "," / ";" / "="

   resource

      A concept reflects the HTTP **path**, every resource corresponds
      to *URI*.

      May have a unique name.

      Contains :term:`route`\'s for different HTTP methods.

   route

       A part of :term:`resource`, resource's *path* coupled with HTTP method.

   web-handler

       An endpoint that returns HTTP response.

   websocket

       A protocol providing full-duplex communication channels over a
       single TCP connection. The WebSocket protocol was standardized
       by the IETF as :rfc:`6455`

   yarl

      A library for operating with URL objects.

      https://pypi.python.org/pypi/yarl


Environment Variables
=====================

.. envvar:: AIOHTTP_NO_EXTENSIONS

   If set to a non-empty value while building from source, aiohttp will be built without speedups
   written as C extensions. This option is primarily useful for debugging.

.. envvar:: AIOHTTP_USE_SYSTEM_DEPS

   If set to a non-empty value while building from source, aiohttp will be built against
   the system installation of llhttp rather than the vendored library. This option is primarily
   meant to be used by downstream redistributors.

.. envvar:: NETRC

   If set, HTTP Basic Auth will be read from the file pointed to by this environment variable,
   rather than from :file:`~/.netrc`.

   .. seealso::

      ``.netrc`` documentation: https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html
````

## File: docs/http_request_lifecycle.rst
````
.. _aiohttp-request-lifecycle:


The aiohttp Request Lifecycle
=============================


Why is aiohttp client API that way?
--------------------------------------


The first time you use aiohttp, you'll notice that a simple HTTP request is performed not with one, but with up to three steps:


.. code-block:: python


    async with aiohttp.ClientSession() as session:
        async with session.get('http://python.org') as response:
            print(await response.text())


It's especially unexpected when coming from other libraries such as the very popular :term:`requests`, where the "hello world" looks like this:


.. code-block:: python


    response = requests.get('http://python.org')
    print(response.text)


So why is the aiohttp snippet so verbose?


Because aiohttp is asynchronous, its API is designed to make the most out of non-blocking network operations. In code like this, requests will block three times, and does it transparently, while aiohttp gives the event loop three opportunities to switch context:


- When doing the ``.get()``, both libraries send a GET request to the remote server. For aiohttp, this means asynchronous I/O, which is marked here with an ``async with`` that gives you the guarantee that not only it doesn't block, but that it's cleanly finalized.
- When doing ``response.text`` in requests, you just read an attribute. The call to ``.get()`` already preloaded and decoded the entire response payload, in a blocking manner. aiohttp loads only the headers when ``.get()`` is executed, letting you decide to pay the cost of loading the body afterward, in a second asynchronous operation. Hence the ``await response.text()``.
- ``async with aiohttp.ClientSession()`` does not perform I/O when entering the block, but at the end of it, it will ensure all remaining resources are closed correctly. Again, this is done asynchronously and must be marked as such. The session is also a performance tool, as it manages a pool of connections for you, allowing you to reuse them instead of opening and closing a new one at each request. You can even `manage the pool size by passing a connector object <client_advanced.html#limiting-connection-pool-size>`_.

Using a session as a best practice
-----------------------------------

The requests library does in fact also provides a session system. Indeed, it lets you do:

.. code-block:: python

    with requests.Session() as session:
        response = session.get('http://python.org')
        print(response.text)

It's just not the default behavior, nor is it advertised early in the documentation. Because of this, most users take a hit in performance, but can quickly start hacking. And for requests, it's an understandable trade-off, since its goal is to be "HTTP for humans" and simplicity has always been more important than performance in this context.

However, if one uses aiohttp, one chooses asynchronous programming, a paradigm that makes the opposite trade-off: more verbosity for better performance. And so the library default behavior reflects this, encouraging you to use performant best practices from the start.

How to use the ClientSession ?
-------------------------------

By default the :class:`aiohttp.ClientSession` object will hold a connector with a maximum of 100 connections, putting the rest in a queue. This is quite a big number, this means you must be connected to a hundred different servers (not pages!) concurrently before even having to consider if your task needs resource adjustment.

In fact, you can picture the session object as a user starting and closing a browser: it wouldn't make sense to do that every time you want to load a new tab.

So you are expected to reuse a session object and make many requests from it. For most scripts and average-sized software, this means you can create a single session, and reuse it for the entire execution of the program. You can even pass the session around as a parameter in functions. For example, the typical "hello world":

.. code-block:: python

    import aiohttp
    import asyncio

    async def main():
        async with aiohttp.ClientSession() as session:
            async with session.get('http://python.org') as response:
                html = await response.text()
                print(html)

    asyncio.run(main())


Can become this:


.. code-block:: python

    import aiohttp
    import asyncio

    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async def main():
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, 'http://python.org')
            print(html)

    asyncio.run(main())

On more complex code bases, you can even create a central registry to hold the session object from anywhere in the code, or a higher level ``Client`` class that holds a reference to it.

When to create more than one session object then? It arises when you want more granularity with your resources management:

- you want to group connections by a common configuration. e.g: sessions can set cookies, headers, timeout values, etc. that are shared for all connections they hold.
- you need several threads and want to avoid sharing a mutable object between them.
- you want several connection pools to benefit from different queues and assign priorities. e.g: one session never uses the queue and is for high priority requests, the other one has a small concurrency limit and a very long queue, for non important requests.
````

## File: docs/index.rst
````
.. aiohttp documentation master file, created by
   sphinx-quickstart on Wed Mar  5 12:35:35 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================
Welcome to AIOHTTP
==================

Asynchronous HTTP Client/Server for :term:`asyncio` and Python.

Current version is |release|.

.. _GitHub: https://github.com/aio-libs/aiohttp


Key Features
============

- Supports both :ref:`aiohttp-client` and :ref:`HTTP Server <aiohttp-web>`.
- Supports both :ref:`Server WebSockets <aiohttp-web-websockets>` and
  :ref:`Client WebSockets <aiohttp-client-websockets>` out-of-the-box
  without the Callback Hell.
- Web-server has :ref:`aiohttp-web-middlewares`,
  :ref:`aiohttp-web-signals` and pluggable routing.
- Client supports :ref:`middleware <aiohttp-client-middleware>` for
  customizing request/response processing.

.. _aiohttp-installation:

Library Installation
====================

.. code-block:: bash

   $ pip install aiohttp

For speeding up DNS resolving by client API you may install
:term:`aiodns` as well.
This option is highly recommended:

.. code-block:: bash

   $ pip install aiodns

Installing all speedups in one command
--------------------------------------

The following will get you ``aiohttp`` along with :term:`aiodns` and ``Brotli`` in one
bundle.
No need to type separate commands anymore!

.. code-block:: bash

   $ pip install aiohttp[speedups]

Getting Started
===============

Client example
--------------

.. code-block:: python

  import aiohttp
  import asyncio

  async def main():

      async with aiohttp.ClientSession() as session:
          async with session.get('http://python.org') as response:

              print("Status:", response.status)
              print("Content-type:", response.headers['content-type'])

              html = await response.text()
              print("Body:", html[:15], "...")

  asyncio.run(main())

This prints:

.. code-block:: text

    Status: 200
    Content-type: text/html; charset=utf-8
    Body: <!doctype html> ...

Coming from :term:`requests` ? Read :ref:`why we need so many lines <aiohttp-request-lifecycle>`.

Server example:
----------------

.. code-block:: python

    from aiohttp import web

    async def handle(request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name
        return web.Response(text=text)

    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.get('/{name}', handle)])

    if __name__ == '__main__':
        web.run_app(app)


For more information please visit :ref:`aiohttp-client` and
:ref:`aiohttp-web` pages.

Development mode
================

When writing your code, we recommend enabling Python's
`development mode <https://docs.python.org/3/library/devmode.html>`_
(``python -X dev``). In addition to the extra features enabled for asyncio, aiohttp
will:

- Use a strict parser in the client code (which can help detect malformed responses
  from a server).
- Enable some additional checks (resulting in warnings in certain situations).

What's new in aiohttp 3?
========================

Go to :ref:`aiohttp_whats_new_3_0` page for aiohttp 3.0 major release
changes.


Tutorial
========

:ref:`Polls tutorial <aiohttpdemos:aiohttp-demos-polls-beginning>`


Source code
===========

The project is hosted on GitHub_

Please feel free to file an issue on the `bug tracker
<https://github.com/aio-libs/aiohttp/issues>`_ if you have found a bug
or have some suggestion in order to improve the library.


Dependencies
============

- *multidict*
- *yarl*

- *Optional* :term:`aiodns` for fast DNS resolving. The
  library is highly recommended.

  .. code-block:: bash

     $ pip install aiodns

- *Optional* :term:`Brotli` or :term:`brotlicffi` for brotli (:rfc:`7932`)
  client compression support.

  .. code-block:: bash

     $ pip install Brotli


Communication channels
======================

*aio-libs Discussions*: https://github.com/aio-libs/aiohttp/discussions

Feel free to post your questions and ideas here.

*Matrix*: `#aio-libs:matrix.org <https://matrix.to/#/#aio-libs:matrix.org>`_

We support `Stack Overflow
<https://stackoverflow.com/questions/tagged/aiohttp>`_.
Please add *aiohttp* tag to your question there.

Contributing
============

Please read the :ref:`instructions for contributors<aiohttp-contributing>`
before making a Pull Request.


Authors and License
===================

The ``aiohttp`` package is written mostly by Nikolay Kim and Andrew Svetlov.

It's *Apache 2* licensed and freely available.

Feel free to improve this package and send a pull request to GitHub_.


.. _aiohttp-backward-compatibility-policy:

Policy for Backward Incompatible Changes
========================================

*aiohttp* keeps backward compatibility.

When a new release is published that deprecates a *Public API* (method, class,
function argument, etc.), the library will guarantee its usage for at least
a year and half from the date of release.

Deprecated APIs are reflected in their documentation, and their use will raise
:exc:`DeprecationWarning`.

However, if there is a strong reason, we may be forced to break this guarantee.
The most likely reason would be a critical bug, such as a security issue, which
cannot be solved without a major API change. We are working hard to keep these
breaking changes as rare as possible.


Table Of Contents
=================

.. toctree::
   :name: mastertoc
   :maxdepth: 2

   client
   web
   utilities
   faq
   misc
   external
   contributing
````

## File: docs/logging.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-logging:

Logging
=======

*aiohttp* uses standard :mod:`logging` for tracking the
library activity.

We have the following loggers enumerated by names:

- ``'aiohttp.access'``
- ``'aiohttp.client'``
- ``'aiohttp.internal'``
- ``'aiohttp.server'``
- ``'aiohttp.web'``
- ``'aiohttp.websocket'``

You may subscribe to these loggers for getting logging messages.  The
page does not provide instructions for logging subscribing while the
most friendly method is :func:`logging.config.dictConfig` for
configuring whole loggers in your application.

Logging does not work out of the box. It requires at least minimal ``'logging'``
configuration.
Example of minimal working logger setup::

  import logging
  from aiohttp import web

  app = web.Application()
  logging.basicConfig(level=logging.DEBUG)
  web.run_app(app, port=5000)

.. versionadded:: 4.0.0

Access logs
-----------

Access logs are enabled by default. If the `debug` flag is set, and the default
logger ``'aiohttp.access'`` is used, access logs will be output to
:obj:`~sys.stderr` if no handlers are attached.
Furthermore, if the default logger has no log level set, the log level will be
set to :obj:`logging.DEBUG`.

This logging may be controlled by :meth:`aiohttp.web.AppRunner` and
:func:`aiohttp.web.run_app`.

To override the default logger, pass an instance of :class:`logging.Logger` to
override the default logger.

.. note::

   Use ``web.run_app(app, access_log=None)`` to disable access logs.


In addition, *access_log_format* may be used to specify the log format.

.. _aiohttp-logging-access-log-format-spec:

Format specification
^^^^^^^^^^^^^^^^^^^^

The library provides custom micro-language to specifying info about
request and response:

+--------------+---------------------------------------------------------+
| Option       | Meaning                                                 |
+==============+=========================================================+
| ``%%``       | The percent sign                                        |
+--------------+---------------------------------------------------------+
| ``%a``       | Remote IP-address                                       |
|              | (IP-address of proxy if using reverse proxy)            |
+--------------+---------------------------------------------------------+
| ``%t``       | Time when the request was started to process            |
+--------------+---------------------------------------------------------+
| ``%P``       | The process ID of the child that serviced the request   |
+--------------+---------------------------------------------------------+
| ``%r``       | First line of request                                   |
+--------------+---------------------------------------------------------+
| ``%s``       | Response status code                                    |
+--------------+---------------------------------------------------------+
| ``%b``       | Size of response in bytes, including HTTP headers       |
+--------------+---------------------------------------------------------+
| ``%T``       | The time taken to serve the request, in seconds         |
+--------------+---------------------------------------------------------+
| ``%Tf``      | The time taken to serve the request, in seconds         |
|              | with fraction in %.06f format                           |
+--------------+---------------------------------------------------------+
| ``%D``       | The time taken to serve the request, in microseconds    |
+--------------+---------------------------------------------------------+
| ``%{FOO}i``  | ``request.headers['FOO']``                              |
+--------------+---------------------------------------------------------+
| ``%{FOO}o``  | ``response.headers['FOO']``                             |
+--------------+---------------------------------------------------------+

The default access log format is::

   '%a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"'

.. versionadded:: 2.3.0

*access_log_class* introduced.

Example of a drop-in replacement for the default access logger::

  from aiohttp.abc import AbstractAccessLogger

  class AccessLogger(AbstractAccessLogger):

      def log(self, request, response, time):
          self.logger.info(f'{request.remote} '
                           f'"{request.method} {request.path} '
                           f'done in {time}s: {response.status}')

      @property
      def enabled(self):
          """Return True if logger is enabled.

          Override this property if logging is disabled to avoid the
          overhead of calculating details to feed the logger.

          This property may be omitted if logging is always enabled.
          """
          return self.logger.isEnabledFor(logging.INFO)

.. versionadded:: 4.0.0


``AccessLogger.log()`` can now access any exception raised while processing
the request with ``sys.exc_info()``.


.. versionadded:: 4.0.0


If your logging needs to perform IO you can instead inherit from
:class:`aiohttp.abc.AbstractAsyncAccessLogger`::


  from aiohttp.abc import AbstractAsyncAccessLogger

  class AccessLogger(AbstractAsyncAccessLogger):

      async def log(self, request, response, time):
          logging_service = request.app['logging_service']
          await logging_service.log(f'{request.remote} '
                                    f'"{request.method} {request.path} '
                                    f'done in {time}s: {response.status}')

      @property
      def enabled(self) -> bool:
          """Return True if logger is enabled.

          Override this property if logging is disabled to avoid the
          overhead of calculating details to feed the logger.
          """
          return self.logger.isEnabledFor(logging.INFO)


This also allows access to the results of coroutines on the ``request`` and
``response``, e.g. ``request.text()``.

.. _gunicorn-accesslog:

Gunicorn access logs
^^^^^^^^^^^^^^^^^^^^
When `Gunicorn <http://docs.gunicorn.org/en/latest/index.html>`_ is used for
:ref:`deployment <aiohttp-deployment-gunicorn>`, its default access log format
will be automatically replaced with the default aiohttp's access log format.

If Gunicorn's option access_logformat_ is
specified explicitly, it should use aiohttp's format specification.

Gunicorn's access log works only if accesslog_ is specified explicitly in your
config or as a command line option.
This configuration can be either a path or ``'-'``. If the application uses
a custom logging setup intercepting the ``'gunicorn.access'`` logger,
accesslog_ should be set to ``'-'`` to prevent Gunicorn to create an empty
access log file upon every startup.

Error logs
----------

:mod:`aiohttp.web` uses a logger named ``'aiohttp.server'`` to store errors
given on web requests handling.

This log is enabled by default.

To use a different logger name, pass *logger* (:class:`logging.Logger`
instance) to the :meth:`aiohttp.web.AppRunner` constructor.


.. _access_logformat:
    http://docs.gunicorn.org/en/stable/settings.html#access-log-format

.. _accesslog:
    http://docs.gunicorn.org/en/stable/settings.html#accesslog
````

## File: docs/migration_to_2xx.rst
````
.. _aiohttp-migration:

Migration to 2.x
================

Client
------

chunking
^^^^^^^^

aiohttp does not support custom chunking sizes. It is up to the developer
to decide how to chunk data streams. If chunking is enabled, aiohttp
encodes the provided chunks in the "Transfer-encoding: chunked" format.

aiohttp does not enable chunked encoding automatically even if a
*transfer-encoding* header is supplied: *chunked* has to be set
explicitly. If *chunked* is set, then the *Transfer-encoding* and
*content-length* headers are disallowed.

compression
^^^^^^^^^^^

Compression has to be enabled explicitly with the *compress* parameter.
If compression is enabled, adding a *content-encoding* header is not allowed.
Compression also enables the *chunked* transfer-encoding.
Compression can not be combined with a *Content-Length* header.


Client Connector
^^^^^^^^^^^^^^^^

1. By default a connector object manages a total number of concurrent
   connections.  This limit was a per host rule in version 1.x. In
   2.x, the `limit` parameter defines how many concurrent connection
   connector can open and a new `limit_per_host` parameter defines the
   limit per host. By default there is no per-host limit.
2. BaseConnector.close is now a normal function as opposed to
   coroutine in version 1.x
3. BaseConnector.conn_timeout was moved to ClientSession


ClientResponse.release
^^^^^^^^^^^^^^^^^^^^^^

Internal implementation was significantly redesigned. It is not
required to call `release` on the response object. When the client
fully receives the payload, the underlying connection automatically
returns back to pool. If the payload is not fully read, the connection
is closed


Client exceptions
^^^^^^^^^^^^^^^^^

Exception hierarchy has been significantly modified. aiohttp now defines only
exceptions that covers connection handling and server response misbehaviors.
For developer specific mistakes, aiohttp uses python standard exceptions
like ValueError or TypeError.

Reading a response content may raise a ClientPayloadError
exception. This exception indicates errors specific to the payload
encoding. Such as invalid compressed data, malformed chunked-encoded
chunks or not enough data that satisfy the content-length header.

All exceptions are moved from `aiohttp.errors` module to top level
`aiohttp` module.

New hierarchy of exceptions:

* `ClientError` - Base class for all client specific exceptions

  - `ClientResponseError` - exceptions that could happen after we get
    response from server

    * `WSServerHandshakeError` - web socket server response error

      - `ClientHttpProxyError` - proxy response

  - `ClientConnectionError` - exceptions related to low-level
    connection problems

    * `ClientOSError` - subset of connection errors that are initiated
      by an OSError exception

      - `ClientConnectorError` - connector related exceptions

        * `ClientProxyConnectionError` - proxy connection initialization error

          - `ServerConnectionError` - server connection related errors

        * `ServerDisconnectedError` - server disconnected

        * `ServerTimeoutError` - server operation timeout, (read timeout, etc)

        * `ServerFingerprintMismatch` - server fingerprint mismatch

  - `ClientPayloadError` - This exception can only be raised while
    reading the response payload if one of these errors occurs:
    invalid compression, malformed chunked encoding or not enough data
    that satisfy content-length header.


Client payload (form-data)
^^^^^^^^^^^^^^^^^^^^^^^^^^

To unify form-data/payload handling a new `Payload` system was
introduced. It handles customized handling of existing types and
provide implementation for user-defined types.

1. FormData.__call__ does not take an encoding arg anymore
   and its return value changes from an iterator or bytes to a Payload instance.
   aiohttp provides payload adapters for some standard types like `str`, `byte`,
   `io.IOBase`, `StreamReader` or `DataQueue`.

2. a generator is not supported as data provider anymore, `streamer`
   can be used instead.  For example, to upload data from file::

     @aiohttp.streamer
     def file_sender(writer, file_name=None):
           with open(file_name, 'rb') as f:
               chunk = f.read(2**16)
               while chunk:
                   yield from writer.write(chunk)
                   chunk = f.read(2**16)

     # Then you can use `file_sender` like this:

     async with session.post('http://httpbin.org/post',
                             data=file_sender(file_name='huge_file')) as resp:
            print(await resp.text())


Various
^^^^^^^

1. the `encoding` parameter is deprecated in `ClientSession.request()`.
   Payload encoding is controlled at the payload level.
   It is possible to specify an encoding for each payload instance.

2. the `version` parameter is removed in `ClientSession.request()`
   client version can be specified in the `ClientSession` constructor.

3. `aiohttp.MsgType` dropped, use `aiohttp.WSMsgType` instead.

4. `ClientResponse.url` is an instance of `yarl.URL` class (`url_obj`
   is deprecated)

5. `ClientResponse.raise_for_status()` raises
   :exc:`aiohttp.ClientResponseError` exception

6. `ClientResponse.json()` is strict about response's content type. if
   content type does not match, it raises
   :exc:`aiohttp.ClientResponseError` exception.  To disable content
   type check you can pass ``None`` as `content_type` parameter.




Server
------

ServerHttpProtocol and low-level details
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Internal implementation was significantly redesigned to provide
better performance and support HTTP pipelining.
ServerHttpProtocol is dropped, implementation is merged with RequestHandler
a lot of low-level api's are dropped.


Application
^^^^^^^^^^^

1. Constructor parameter `loop` is deprecated. Loop is get configured by application runner,
   `run_app` function for any of gunicorn workers.

2. `Application.router.add_subapp` is dropped, use `Application.add_subapp` instead

3. `Application.finished` is dropped, use `Application.cleanup` instead


WebRequest and WebResponse
^^^^^^^^^^^^^^^^^^^^^^^^^^

1. the `GET` and `POST` attributes no longer exist. Use the `query` attribute instead of `GET`

2. Custom chunking size is not support `WebResponse.chunked` - developer is
   responsible for actual chunking.

3. Payloads are supported as body. So it is possible to use client response's content
   object as body parameter for `WebResponse`

4. `FileSender` api is dropped, it is replaced with more general `FileResponse` class::

     async def handle(request):
         return web.FileResponse('path-to-file.txt')

5. `WebSocketResponse.protocol` is renamed to `WebSocketResponse.ws_protocol`.
   `WebSocketResponse.protocol` is instance of `RequestHandler` class.



RequestPayloadError
^^^^^^^^^^^^^^^^^^^

Reading request's payload may raise a `RequestPayloadError` exception. The behavior is similar
to `ClientPayloadError`.


WSGI
^^^^

*WSGI* support has been dropped, as well as gunicorn wsgi support. We still provide default and uvloop gunicorn workers for `web.Application`
````

## File: docs/misc.rst
````
.. _aiohttp-misc:

Miscellaneous
=============

Helpful pages.

.. toctree::
   :name: misc

   essays
   glossary

.. toctree::
   :titlesonly:

   changes

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
````

## File: docs/multipart_reference.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-multipart-reference:

Multipart reference
===================

.. class:: MultipartResponseWrapper(resp, stream)

   Wrapper around the :class:`MultipartReader` to take care about
   underlying connection and close it when it needs in.


   .. method:: at_eof()

      Returns ``True`` when all response data had been read.

      :rtype: bool

   .. method:: next()
      :async:

      Emits next multipart reader object.

   .. method:: release()
      :async:

      Releases the connection gracefully, reading all the content
      to the void.


.. class:: BodyPartReader(boundary, headers, content)

   Multipart reader for single body part.

   .. method:: read(*, decode=False)
      :async:

      Reads body part data.

      :param bool decode: Decodes data following by encoding method
                          from ``Content-Encoding`` header. If it
                          missed data remains untouched

      :rtype: bytearray

   .. method:: read_chunk(size=chunk_size)
      :async:

      Reads body part content chunk of the specified size.

      :param int size: chunk size

      :rtype: bytearray

   .. method:: readline()
      :async:

      Reads body part by line by line.

      :rtype: bytearray

   .. method:: release()
      :async:

      Like :meth:`read`, but reads all the data to the void.

      :rtype: None

   .. method:: text(*, encoding=None)
      :async:

      Like :meth:`read`, but assumes that body part contains text data.

      :param str encoding: Custom text encoding. Overrides specified
                           in charset param of ``Content-Type`` header

      :rtype: str

   .. method:: json(*, encoding=None)
      :async:

      Like :meth:`read`, but assumes that body parts contains JSON data.

      :param str encoding: Custom JSON encoding. Overrides specified
                           in charset param of ``Content-Type`` header

   .. method:: form(*, encoding=None)
      :async:

      Like :meth:`read`, but assumes that body parts contains form
      urlencoded data.

      :param str encoding: Custom form encoding. Overrides specified
                           in charset param of ``Content-Type`` header

   .. method:: at_eof()

      Returns ``True`` if the boundary was reached or ``False`` otherwise.

      :rtype: bool

   .. method:: decode(data)

      Decodes data according the specified ``Content-Encoding``
      or ``Content-Transfer-Encoding`` headers value.

      Supports ``gzip``, ``deflate`` and ``identity`` encodings for
      ``Content-Encoding`` header.

      Supports ``base64``, ``quoted-printable``, ``binary`` encodings for
      ``Content-Transfer-Encoding`` header.

      :param bytearray data: Data to decode.

      :raises: :exc:`RuntimeError` - if encoding is unknown.

      :rtype: bytes

   .. method:: get_charset(default=None)

      Returns charset parameter from ``Content-Type`` header or default.

   .. attribute:: name

      A field *name* specified in ``Content-Disposition`` header or ``None``
      if missed or header is malformed.

      Readonly :class:`str` property.

   .. attribute:: filename

      A field *filename* specified in ``Content-Disposition`` header or ``None``
      if missed or header is malformed.

      Readonly :class:`str` property.


.. class:: MultipartReader(headers, content)

   Multipart body reader.

   .. classmethod:: from_response(cls, response)

      Constructs reader instance from HTTP response.

      :param response: :class:`~aiohttp.ClientResponse` instance

   .. method:: at_eof()

      Returns ``True`` if the final boundary was reached or
      ``False`` otherwise.

      :rtype: bool

   .. method:: next()
      :async:

      Emits the next multipart body part.

   .. method:: release()
      :async:

      Reads all the body parts to the void till the final boundary.

   .. method:: fetch_next_part()
      :async:

      Returns the next body part reader.


.. class:: MultipartWriter(subtype='mixed', boundary=None, close_boundary=True)

   Multipart body writer.

   ``boundary`` may be an ASCII-only string.

   .. attribute:: boundary

      The string (:class:`str`) representation of the boundary.

      .. versionchanged:: 3.0

         Property type was changed from :class:`bytes` to :class:`str`.

   .. method:: append(obj, headers=None)

      Append an object to writer.

   .. method:: append_payload(payload)

      Adds a new body part to multipart writer.

   .. method:: append_json(obj, headers=None)

      Helper to append JSON part.

   .. method:: append_form(obj, headers=None)

      Helper to append form urlencoded part.

   .. attribute:: size

      Size of the payload.

   .. method:: write(writer, close_boundary=True)
      :async:

      Write body.

      :param bool close_boundary: The (:class:`bool`) that will emit
                                  boundary closing. You may want to disable
                                  when streaming (``multipart/x-mixed-replace``)

      .. versionadded:: 3.4

         Support ``close_boundary`` argument.
````

## File: docs/multipart.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-multipart:

Working with Multipart
======================

``aiohttp`` supports a full featured multipart reader and writer. Both
are designed with streaming processing in mind to avoid unwanted
footprint which may be significant if you're dealing with large
payloads, but this also means that most I/O operation are only
possible to be executed a single time.

Reading Multipart Responses
---------------------------

Assume you made a request, as usual, and want to process the response multipart
data::

    async with aiohttp.request(...) as resp:
        pass

First, you need to wrap the response with a
:meth:`MultipartReader.from_response`. This needs to keep the implementation of
:class:`MultipartReader` separated from the response and the connection routines
which makes it more portable::

    reader = aiohttp.MultipartReader.from_response(resp)

Let's assume with this response you'd received some JSON document and multiple
files for it, but you don't need all of them, just a specific one.

So first you need to enter into a loop where the multipart body will
be processed::

    metadata = None
    filedata = None
    while True:
        part = await reader.next()

The returned type depends on what the next part is: if it's a simple body part
then you'll get :class:`BodyPartReader` instance here, otherwise, it will
be another :class:`MultipartReader` instance for the nested multipart. Remember,
that multipart format is recursive and supports multiple levels of nested body
parts. When there are no more parts left to fetch, ``None`` value will be
returned - that's the signal to break the loop::

    if part is None:
        break

Both :class:`BodyPartReader` and :class:`MultipartReader` provides access to
body part headers: this allows you to filter parts by their attributes::

    if part.headers[aiohttp.hdrs.CONTENT_TYPE] == 'application/json':
        metadata = await part.json()
        continue

Neither :class:`BodyPartReader` nor :class:`MultipartReader` instances
read the whole body part data without explicitly asking for.
:class:`BodyPartReader` provides a set of helpers methods
to fetch popular content types in friendly way:

- :meth:`BodyPartReader.text` for plain text data;
- :meth:`BodyPartReader.json` for JSON;
- :meth:`BodyPartReader.form` for `application/www-urlform-encode`

Each of these methods automatically recognizes if content is compressed by
using `gzip` and `deflate` encoding (while it respects `identity` one), or if
transfer encoding is base64 or `quoted-printable` - in each case the result
will get automatically decoded. But in case you need to access to raw binary
data as it is, there are :meth:`BodyPartReader.read` and
:meth:`BodyPartReader.read_chunk` coroutine methods as well to read raw binary
data as it is all-in-single-shot or by chunks respectively.

When you have to deal with multipart files, the :attr:`BodyPartReader.filename`
property comes to help. It's a very smart helper which handles
`Content-Disposition` handler right and extracts the right filename attribute
from it::

    if part.filename != 'secret.txt':
        continue

If current body part does not matches your expectation and you want to skip it
- just continue a loop to start a next iteration of it. Here is where magic
happens. Before fetching the next body part ``await reader.next()`` it
ensures that the previous one was read completely. If it was not, all its content
sends to the void in term to fetch the next part. So you don't have to care
about cleanup routines while you're within a loop.

Once you'd found a part for the file you'd searched for, just read it. Let's
handle it as it is without applying any decoding magic::

    filedata = await part.read(decode=False)

Later you may decide to decode the data. It's still simple and possible
to do::

    filedata = part.decode(filedata)

Once you are done with multipart processing, just break a loop::

    break


Sending Multipart Requests
--------------------------

:class:`MultipartWriter` provides an interface to build multipart payload from
the Python data and serialize it into chunked binary stream. Since multipart
format is recursive and supports deeply nesting, you can use ``with`` statement
to design your multipart data closer to how it will be::

    with aiohttp.MultipartWriter('mixed') as mpwriter:
        ...
        with aiohttp.MultipartWriter('related') as subwriter:
            ...
        mpwriter.append(subwriter)

        with aiohttp.MultipartWriter('related') as subwriter:
            ...
            with aiohttp.MultipartWriter('related') as subsubwriter:
                ...
            subwriter.append(subsubwriter)
        mpwriter.append(subwriter)

        with aiohttp.MultipartWriter('related') as subwriter:
            ...
        mpwriter.append(subwriter)

The :meth:`MultipartWriter.append` is used to join new body parts into a
single stream. It accepts various inputs and determines what default headers
should be used for.

For text data default `Content-Type` is :mimetype:`text/plain; charset=utf-8`::

    mpwriter.append('hello')

For binary data :mimetype:`application/octet-stream` is used::

    mpwriter.append(b'aiohttp')

You can always override these default by passing your own headers with
the second argument::

    mpwriter.append(io.BytesIO(b'GIF89a...'),
                    {'CONTENT-TYPE': 'image/gif'})

For file objects `Content-Type` will be determined by using Python's
mod:`mimetypes` module and additionally `Content-Disposition` header
will include the file's basename::

    part = root.append(open(__file__, 'rb'))

If you want to send a file with a different name, just handle the
:class:`~aiohttp.payload.Payload` instance which :meth:`MultipartWriter.append` will
always return and set `Content-Disposition` explicitly by using
the :meth:`Payload.set_content_disposition() <aiohttp.payload.Payload.set_content_disposition>` helper::

    part.set_content_disposition('attachment', filename='secret.txt')

Additionally, you may want to set other headers here::

    part.headers[aiohttp.hdrs.CONTENT_ID] = 'X-12345'

If you'd set `Content-Encoding`, it will be automatically applied to the
data on serialization (see below)::

    part.headers[aiohttp.hdrs.CONTENT_ENCODING] = 'gzip'

There are also :meth:`MultipartWriter.append_json` and
:meth:`MultipartWriter.append_form` helpers which are useful to work with JSON
and form urlencoded data, so you don't have to encode it every time manually::

    mpwriter.append_json({'test': 'passed'})
    mpwriter.append_form([('key', 'value')])

When it's done, to make a request just pass a root :class:`MultipartWriter`
instance as :meth:`aiohttp.ClientSession.request` ``data`` argument::

    await session.post('http://example.com', data=mpwriter)

Behind the scenes :meth:`MultipartWriter.write` will yield chunks of every
part and if body part has `Content-Encoding` or `Content-Transfer-Encoding`
they will be applied on streaming content.

Please note, that on :meth:`MultipartWriter.write` all the file objects
will be read until the end and there is no way to repeat a request without
rewinding their pointers to the start.

Example MJPEG Streaming ``multipart/x-mixed-replace``. By default
:meth:`MultipartWriter.write` appends closing ``--boundary--`` and breaks your
content. Providing `close_boundary = False` prevents this.::

    my_boundary = 'some-boundary'
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'multipart/x-mixed-replace;boundary={}'.format(my_boundary)
        }
    )
    while True:
        frame = get_jpeg_frame()
        with MultipartWriter('image/jpeg', boundary=my_boundary) as mpwriter:
            mpwriter.append(frame, {
                'Content-Type': 'image/jpeg'
            })
            await mpwriter.write(response, close_boundary=False)
        await response.drain()

Hacking Multipart
-----------------

The Internet is full of terror and sometimes you may find a server which
implements multipart support in strange ways when an oblivious solution
does not work.

For instance, is server used :class:`cgi.FieldStorage` then you have
to ensure that no body part contains a `Content-Length` header::

    for part in mpwriter:
        part.headers.pop(aiohttp.hdrs.CONTENT_LENGTH, None)

On the other hand, some server may require to specify `Content-Length` for the
whole multipart request. `aiohttp` does not do that since it sends multipart
using chunked transfer encoding by default. To overcome this issue, you have
to serialize a :class:`MultipartWriter` by our own in the way to calculate its
size::

    class Writer:
        def __init__(self):
            self.buffer = bytearray()

        async def write(self, data):
            self.buffer.extend(data)

    writer = Writer()
    await mpwriter.write(writer)
    await aiohttp.post('http://example.com',
                       data=writer.buffer, headers=mpwriter.headers)

Sometimes the server response may not be well formed: it may or may not
contains nested parts. For instance, we request a resource which returns
JSON documents with the files attached to it. If the document has any
attachments, they are returned as a nested multipart.
If it has not it responds as plain body parts:

.. code-block:: none

    CONTENT-TYPE: multipart/mixed; boundary=--:

    --:
    CONTENT-TYPE: application/json

    {"_id": "foo"}
    --:
    CONTENT-TYPE: multipart/related; boundary=----:

    ----:
    CONTENT-TYPE: application/json

    {"_id": "bar"}
    ----:
    CONTENT-TYPE: text/plain
    CONTENT-DISPOSITION: attachment; filename=bar.txt

    bar! bar! bar!
    ----:--
    --:
    CONTENT-TYPE: application/json

    {"_id": "boo"}
    --:
    CONTENT-TYPE: multipart/related; boundary=----:

    ----:
    CONTENT-TYPE: application/json

    {"_id": "baz"}
    ----:
    CONTENT-TYPE: text/plain
    CONTENT-DISPOSITION: attachment; filename=baz.txt

    baz! baz! baz!
    ----:--
    --:--

Reading such kind of data in single stream is possible, but is not clean at
all::

    result = []
    while True:
        part = await reader.next()

        if part is None:
            break

        if isinstance(part, aiohttp.MultipartReader):
            # Fetching files
            while True:
                filepart = await part.next()
                if filepart is None:
                    break
                result[-1].append((await filepart.read()))

        else:
            # Fetching document
            result.append([(await part.json())])

Let's hack a reader in the way to return pairs of document and reader of the
related files on each iteration::

    class PairsMultipartReader(aiohttp.MultipartReader):

        # keep reference on the original reader
        multipart_reader_cls = aiohttp.MultipartReader

        async def next(self):
            """Emits a tuple of document object (:class:`dict`) and multipart
            reader of the followed attachments (if any).

            :rtype: tuple
            """
            reader = await super().next()

            if self._at_eof:
                return None, None

            if isinstance(reader, self.multipart_reader_cls):
                part = await reader.next()
                doc = await part.json()
            else:
                doc = await reader.json()

            return doc, reader

And this gives us a more cleaner solution::

    reader = PairsMultipartReader.from_response(resp)
    result = []
    while True:
        doc, files_reader = await reader.next()

        if doc is None:
            break

        files = []
        while True:
            filepart = await files_reader.next()
            if file.part is None:
                break
            files.append((await filepart.read()))

        result.append((doc, files))

.. seealso:: :ref:`aiohttp-multipart-reference`
````

## File: docs/new_router.rst
````
.. _aiohttp-router-refactoring-021:

Router refactoring in 0.21
==========================

Rationale
---------

First generation (v1) of router has mapped ``(method, path)`` pair to
:term:`web-handler`.  Mapping is named **route**. Routes used to have
unique names if any.

The main mistake with the design is coupling the **route** to
``(method, path)`` pair while really URL construction operates with
**resources** (**location** is a synonym). HTTP method is not part of URI
but applied on sending HTTP request only.

Having different **route names** for the same path is confusing. Moreover
**named routes** constructed for the same path should have unique
non overlapping names which is cumbersome is certain situations.

From other side sometimes it's desirable to bind several HTTP methods
to the same web handler. For *v1* router it can be solved by passing '*'
as HTTP method. Class based views require '*' method also usually.


Implementation
--------------

The change introduces **resource** as first class citizen::

   resource = router.add_resource('/path/{to}', name='name')

*Resource* has a **path** (dynamic or constant) and optional **name**.

The name is **unique** in router context.

*Resource* has **routes**.

*Route* corresponds to *HTTP method* and :term:`web-handler` for the method::

   route = resource.add_route('GET', handler)

User still may use wildcard for accepting all HTTP methods (maybe we
will add something like ``resource.add_wildcard(handler)`` later).

Since **names** belongs to **resources** now ``app.router['name']``
returns a **resource** instance instead of :class:`aiohttp.web.AbstractRoute`.

**resource** has ``.url()`` method, so
``app.router['name'].url(parts={'a': 'b'}, query={'arg': 'param'})``
still works as usual.


The change allows to rewrite static file handling and implement nested
applications as well.

Decoupling of *HTTP location* and *HTTP method* makes life easier.

Backward compatibility
----------------------

The refactoring is 99% compatible with previous implementation.

99% means all example and the most of current code works without
modifications but we have subtle API backward incompatibles.

``app.router['name']`` returns a :class:`aiohttp.web.AbstractResource`
instance instead of :class:`aiohttp.web.AbstractRoute` but resource has the
same ``resource.url(...)`` most useful method, so end user should feel no
difference.

``route.match(...)`` is **not** supported anymore, use
:meth:`aiohttp.web.AbstractResource.resolve` instead.

``app.router.add_route(method, path, handler, name='name')`` now is just
shortcut for::

    resource = app.router.add_resource(path, name=name)
    route = resource.add_route(method, handler)
    return route

``app.router.register_route(...)`` is still supported, it creates
``aiohttp.web.ResourceAdapter`` for every call (but it's deprecated now).
````

## File: docs/powered_by.rst
````
.. _aiohttp-powered-by:

Powered by aiohttp
==================

Web sites powered by aiohttp.

Feel free to fork documentation on github, add a link to your site and
make a Pull Request!

* `Farmer Business Network <https://www.farmersbusinessnetwork.com>`_
* `Home Assistant <https://home-assistant.io>`_
* `KeepSafe <https://www.getkeepsafe.com/>`_
* `Skyscanner Hotels <https://www.skyscanner.net/hotels>`_
* `Ocean S.A. <https://ocean.io/>`_
* `GNS3 <http://gns3.com>`_
* `TutorCruncher socket
  <https://tutorcruncher.com/features/tutorcruncher-socket/>`_
* `Eyepea - Custom telephony solutions <http://www.eyepea.eu>`_
* `ALLOcloud - Telephony in the cloud <https://www.allocloud.com>`_
* `helpmanual - comprehensive help and man page database
  <https://helpmanual.io/>`_
* `bedevere <https://github.com/python/bedevere>`_ - CPython's GitHub
  bot, helps maintain and identify issues with a CPython pull request.
* `miss-islington <https://github.com/python/miss-islington>`_ -
  CPython's GitHub bot, backports and merge CPython's pull requests
* `noa technologies - Bike-sharing management platform
  <https://noa.one/>`_ - SSE endpoint, pushes real time updates of
  bikes location.
* `Wargaming: World of Tanks <https://worldoftanks.ru/>`_
* `Yandex <https://yandex.ru>`_
* `Rambler <https://rambler.ru>`_
* `Escargot <https://escargot.log1p.xyz>`_ - Chat server
* `Prom.ua <https://prom.ua/>`_ - Online trading platform
* `globo.com <https://www.globo.com/>`_ - (some parts) Brazilian largest media portal
* `Glose <https://www.glose.com/>`_ - Social reader for E-Books
* `Emoji Generator <https://emoji-gen.ninja>`_ - Text icon generator
* `SerpsBot Google Search API <https://serpsbot.com>`_ - SerpsBot Google Search API
* `PyChess <https://www.pychess.org>`_ - Chess variant server
````

## File: docs/spelling_wordlist.txt
````
abc
addons
aiodns
aioes
aiohttp
aiohttpdemo
aiohttp’s
aiopg
alives
api
api’s
app
app’s
apps
arg
args
armv
Arsenic
async
asyncio
asyncpg
asynctest
attrs
auth
autocalculated
autodetection
autoformatter
autoformatters
autogenerates
autogeneration
awaitable
backoff
backend
backends
backport
Backport
Backporting
backports
BaseEventLoop
basename
BasicAuth
behaviour
BodyPartReader
boolean
botocore
brotli
Brotli
brotlicffi
brotlipy
bugfix
bugfixes
Bugfixes
builtin
BytesIO
callables
cancelled
canonicalization
canonicalize
cchardet
cChardet
ceil
changelog
Changelog
chardet
Chardet
charset
charsetdetect
chunked
chunking
CIMultiDict
ClientSession
cls
cmd
codebase
codec
Codings
committer
committers
config
Config
configs
conjunction
contextmanager
CookieJar
coroutine
Coroutine
coroutines
cpu
CPython
css
ctor
Ctrl
cython
Cython
Cythonize
cythonized
de
deduplicate
defs
Dependabot
deprecations
DER
dev
Dev
dict
Dict
Discord
django
Django
dns
DNSResolver
docstring
docstrings
DoS
downstreams
Dup
elasticsearch
encodings
env
environ
eof
epoll
etag
ETag
expirations
Facebook
facto
fallback
fallbacks
filename
finalizers
formatter
formatters
frontend
getall
gethostbyname
github
google
gunicorn
gunicorn’s
gzipped
hackish
highlevel
hostnames
HTTPException
HttpProcessingError
httpretty
https
hostname
impl
incapsulates
Indices
infos
initializer
inline
intaking
io
IoT
ip
IP
ipdb
ipv
IPv
ish
isort
iterable
iterables
javascript
Jinja
json
keepalive
keepalived
keepalives
keepaliving
kib
KiB
kwarg
kwargs
latin
lifecycle
linux
llhttp
localhost
Locator
login
lookup
lookups
lossless
lowercased
Mako
manylinux
metadata
microservice
middleware
middlewares
miltidict
misbehaviors
Mixcloud
Mongo
msg
MsgType
multi
multidict
multidict’s
multidicts
Multidicts
multipart
Multipart
musllinux
mypy
Nagle
Nagle’s
namedtuple
nameservers
namespace
netrc
nginx
Nginx
Nikolay
noop
normalizer
nowait
OAuth
Online
optimizations
os
outcoming
Overridable
Paolini
param
params
parsers
pathlib
peername
performant
pickleable
ping
pipelining
pluggable
plugin
poller
pong
Postgres
pre
preloaded
proactor
programmatically
proxied
PRs
pubsub
Punycode
py
pydantic
pyenv
pyflakes
pyright
pytest
Pytest
qop
Quickstart
quote’s
rc
readline
readonly
readpayload
rebase
redirections
Redis
refactor
refactored
refactoring
referenceable
regex
regexps
regexs
reloader
renderer
renderers
repo
repr
repr’s
RequestContextManager
request’s
Request’s
requote
requoting
resolvehost
resolvers
reusage
reuseconn
Runit
runtime
runtimes
sa
Satisfiable
schemas
sendfile
serializable
serializer
shourtcuts
skipuntil
Skyscanner
SocketSocketTransport
ssl
SSLContext
startup
subapplication
subclassed
subclasses
subdirectory
submodules
subpackage
subprotocol
subprotocols
subtype
supervisord
Supervisord
Svetlov
symlink
symlinks
syscall
syscalls
Systemd
tarball
TCP
teardown
Teardown
TestClient
Testsuite
Tf
timestamps
TLS
tmp
tmpdir
toolbar
toplevel
towncrier
tp
tuples
UI
un
unawaited
undercounting
unclosed
unhandled
unicode
unittest
Unittest
unix
unsets
unstripped
untyped
uppercased
upstr
url
urldispatcher
urlencoded
url’s
urls
utf
utils
uvloop
uWSGI
vcvarsall
vendored
vendoring
waituntil
wakeup
wakeups
webapp
websocket
websocket’s
websockets
Websockets
wildcard
Winloop
Workflow
ws
wsgi
wss
www
xxx
yarl
zlib
zstandard
zstd
````

## File: docs/streams.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-streams:

Streaming API
=============


``aiohttp`` uses streams for retrieving *BODIES*:
:attr:`aiohttp.web.BaseRequest.content` and
:attr:`aiohttp.ClientResponse.content` are properties with stream API.


.. class:: StreamReader

   The reader from incoming stream.

   User should never instantiate streams manually but use existing
   :attr:`aiohttp.web.BaseRequest.content` and
   :attr:`aiohttp.ClientResponse.content` properties for accessing raw
   BODY data.

Reading Methods
---------------

.. method:: StreamReader.read(n=-1)
      :async:

   Read up to a maximum of *n* bytes. If *n* is not provided, or set to ``-1``,
   read until EOF and return all read bytes.

   When *n* is provided, data will be returned as soon as it is available.
   Therefore it will return less than *n* bytes if there are less than *n*
   bytes in the buffer.

   If the EOF was received and the internal buffer is empty, return an
   empty bytes object.

   :param int n: maximum number of bytes to read, ``-1`` for the whole stream.

   :return bytes: the given data

.. method:: StreamReader.readany()
      :async:

   Read next data portion for the stream.

   Returns immediately if internal buffer has a data.

   :return bytes: the given data

.. method:: StreamReader.readexactly(n)
      :async:

   Read exactly *n* bytes.

   Raise an :exc:`asyncio.IncompleteReadError` if the end of the
   stream is reached before *n* can be read, the
   :attr:`asyncio.IncompleteReadError.partial` attribute of the
   exception contains the partial read bytes.

   :param int n: how many bytes to read.

   :return bytes: the given data


.. method:: StreamReader.readline()
      :async:

   Read one line, where “line” is a sequence of bytes ending
   with ``\n``.

   If EOF is received, and ``\n`` was not found, the method will
   return the partial read bytes.

   If the EOF was received and the internal buffer is empty, return an
   empty bytes object.

   :return bytes: the given line

.. method:: StreamReader.readuntil(separator="\n")
      :async:

   Read until separator, where `separator` is a sequence of bytes.

   If EOF is received, and `separator` was not found, the method will
   return the partial read bytes.

   If the EOF was received and the internal buffer is empty, return an
   empty bytes object.

   .. versionadded:: 3.8

   :return bytes: the given data

.. method:: StreamReader.readchunk()
      :async:

   Read a chunk of data as it was received by the server.

   Returns a tuple of (data, end_of_HTTP_chunk).

   When chunked transfer encoding is used, end_of_HTTP_chunk is a :class:`bool`
   indicating if the end of the data corresponds to the end of a HTTP chunk,
   otherwise it is always ``False``.

   :return tuple[bytes, bool]: a chunk of data and a :class:`bool` that is ``True``
                               when the end of the returned chunk corresponds
                               to the end of a HTTP chunk.


Asynchronous Iteration Support
------------------------------


Stream reader supports asynchronous iteration over BODY.

By default it iterates over lines::

   async for line in response.content:
       print(line)

Also there are methods for iterating over data chunks with maximum
size limit and over any available data.

.. method:: StreamReader.iter_chunked(n)
   :async:

   Iterates over data chunks with maximum size limit::

      async for data in response.content.iter_chunked(1024):
          print(data)

   To get chunks that are exactly *n* bytes, you could use the
   `asyncstdlib.itertools <https://asyncstdlib.readthedocs.io/en/stable/source/api/itertools.html>`_
   module::

      chunks = batched(chain.from_iterable(response.content.iter_chunked(n)), n)
      async for data in chunks:
          print(data)

.. method:: StreamReader.iter_any()
   :async:

   Iterates over data chunks in order of intaking them into the stream::

      async for data in response.content.iter_any():
          print(data)

.. method:: StreamReader.iter_chunks()
   :async:

   Iterates over data chunks as received from the server::

      async for data, _ in response.content.iter_chunks():
          print(data)

   If chunked transfer encoding is used, the original http chunks formatting
   can be retrieved by reading the second element of returned tuples::

      buffer = b""

      async for data, end_of_http_chunk in response.content.iter_chunks():
          buffer += data
          if end_of_http_chunk:
              print(buffer)
              buffer = b""


Helpers
-------

.. method:: StreamReader.exception()

   Get the exception occurred on data reading.

.. method:: is_eof()

   Return ``True`` if EOF was reached.

   Internal buffer may be not empty at the moment.

   .. seealso::

      :meth:`StreamReader.at_eof`

.. method:: StreamReader.at_eof()

   Return ``True`` if the buffer is empty and EOF was reached.

.. method:: StreamReader.read_nowait(n=None)

   Returns data from internal buffer if any, empty bytes object otherwise.

   Raises :exc:`RuntimeError` if other coroutine is waiting for stream.


   :param int n: how many bytes to read, ``-1`` for the whole internal
                 buffer.

   :return bytes: the given data

.. method:: StreamReader.unread_data(data)

   Rollback reading some data from stream, inserting it to buffer head.

   :param bytes data: data to push back into the stream.

   .. warning:: The method does not wake up waiters.

      E.g. :meth:`~StreamReader.read` will not be resumed.


.. method:: wait_eof()
      :async:

   Wait for EOF. The given data may be accessible by upcoming read calls.
````

## File: docs/structures.rst
````
.. currentmodule:: aiohttp


.. _aiohttp-structures:


Common data structures
======================

Common data structures used by *aiohttp* internally.


FrozenList
----------

A list-like structure which implements
:class:`collections.abc.MutableSequence`.

The list is *mutable* unless :meth:`FrozenList.freeze` is called,
after that the list modification raises :exc:`RuntimeError`.


.. class:: FrozenList(items)

   Construct a new *non-frozen* list from *items* iterable.

   The list implements all :class:`collections.abc.MutableSequence`
   methods plus two additional APIs.

   .. attribute:: frozen

      A read-only property, ``True`` is the list is *frozen*
      (modifications are forbidden).

   .. method:: freeze()

      Freeze the list. There is no way to *thaw* it back.


ChainMapProxy
-------------

An *immutable* version of :class:`collections.ChainMap`.  Internally
the proxy is a list of mappings (dictionaries), if the requested key
is not present in the first mapping the second is looked up and so on.

The class supports :class:`collections.abc.Mapping` interface.

.. class:: ChainMapProxy(maps)

   Create a new chained mapping proxy from a list of mappings (*maps*).

   .. versionadded:: 3.2
````

## File: docs/testing.rst
````
.. module:: aiohttp.test_utils

.. _aiohttp-testing:

Testing
=======

Testing aiohttp web servers
---------------------------

aiohttp provides plugin for *pytest* making writing web server tests
extremely easy, it also provides :ref:`test framework agnostic
utilities <aiohttp-testing-framework-agnostic-utilities>` for testing
with other frameworks such as :ref:`unittest
<aiohttp-testing-unittest-example>`.

Before starting to write your tests, you may also be interested on
reading :ref:`how to write testable
services<aiohttp-testing-writing-testable-services>` that interact
with the loop.


For using pytest plugin please install pytest-aiohttp_ library:

.. code-block:: shell

   $ pip install pytest-aiohttp

If you don't want to install *pytest-aiohttp* for some reason you may
insert ``pytest_plugins = 'aiohttp.pytest_plugin'`` line into
``conftest.py`` instead for the same functionality.



The Test Client and Servers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*aiohttp* test utils provides a scaffolding for testing aiohttp-based
web servers.

They consist of two parts: running test server and making HTTP
requests to this server.

:class:`~aiohttp.test_utils.TestServer` runs :class:`aiohttp.web.Application`
based server, :class:`~aiohttp.test_utils.RawTestServer` starts
:class:`aiohttp.web.Server` low level server.

For performing HTTP requests to these servers you have to create a
test client: :class:`~aiohttp.test_utils.TestClient` instance.

The client incapsulates :class:`aiohttp.ClientSession` by providing
proxy methods to the client for common operations such as
*ws_connect*, *get*, *post*, etc.



Pytest
~~~~~~

.. currentmodule:: pytest_aiohttp

The :data:`aiohttp_client` fixture available from pytest-aiohttp_ plugin
allows you to create a client to make requests to test your app.

To run these examples, you need to use `--asyncio-mode=auto` or add to your
pytest config file::

    asyncio_mode = auto

A simple test would be::

    from aiohttp import web

    async def hello(request):
        return web.Response(text='Hello, world')

    async def test_hello(aiohttp_client):
        app = web.Application()
        app.router.add_get('/', hello)
        client = await aiohttp_client(app)
        resp = await client.get('/')
        assert resp.status == 200
        text = await resp.text()
        assert 'Hello, world' in text


It also provides access to the app instance allowing tests to check the state
of the app. Tests can be made even more succinct with a fixture to create an
app test client::

    import pytest
    from aiohttp import web

    value = web.AppKey("value", str)


    async def previous(request):
        if request.method == 'POST':
            request.app[value] = (await request.post())['value']
            return web.Response(body=b'thanks for the data')
        return web.Response(
            body='value: {}'.format(request.app[value]).encode('utf-8'))

    @pytest.fixture
    async def cli(aiohttp_client):
        app = web.Application()
        app.router.add_get('/', previous)
        app.router.add_post('/', previous)
        return await aiohttp_client(app)

    async def test_set_value(cli):
        resp = await cli.post('/', data={'value': 'foo'})
        assert resp.status == 200
        assert await resp.text() == 'thanks for the data'
        assert cli.server.app[value] == 'foo'

    async def test_get_value(cli):
        cli.server.app[value] = 'bar'
        resp = await cli.get('/')
        assert resp.status == 200
        assert await resp.text() == 'value: bar'


Pytest tooling has the following fixtures:

.. data:: aiohttp_server(app, *, port=None, **kwargs)

   A fixture factory that creates
   :class:`~aiohttp.test_utils.TestServer`::

      async def test_f(aiohttp_server):
          app = web.Application()
          # fill route table

          server = await aiohttp_server(app)

   The server will be destroyed on exit from test function.

   *app* is the :class:`aiohttp.web.Application` used
                           to start server.

   *port* optional, port the server is run at, if
   not provided a random unused port is used.

   .. versionadded:: 3.0

   *kwargs* are parameters passed to
                  :meth:`aiohttp.web.AppRunner`

   .. versionchanged:: 3.0
   .. deprecated:: 3.2

      The fixture was renamed from ``test_server`` to ``aiohttp_server``.


.. data:: aiohttp_client(app, server_kwargs=None, **kwargs)
          aiohttp_client(server, **kwargs)
          aiohttp_client(raw_server, **kwargs)

   A fixture factory that creates
   :class:`~aiohttp.test_utils.TestClient` for access to tested server::

      async def test_f(aiohttp_client):
          app = web.Application()
          # fill route table

          client = await aiohttp_client(app)
          resp = await client.get('/')

   *client* and responses are cleaned up after test function finishing.

   The fixture accepts :class:`aiohttp.web.Application`,
   :class:`aiohttp.test_utils.TestServer` or
   :class:`aiohttp.test_utils.RawTestServer` instance.

   *server_kwargs* are parameters passed to the test server if an app
   is passed, else ignored.

   *kwargs* are parameters passed to
   :class:`aiohttp.test_utils.TestClient` constructor.

   .. versionchanged:: 3.0

      The fixture was renamed from ``test_client`` to ``aiohttp_client``.

.. data:: aiohttp_raw_server(handler, *, port=None, **kwargs)

   A fixture factory that creates
   :class:`~aiohttp.test_utils.RawTestServer` instance from given web
   handler.::

      async def test_f(aiohttp_raw_server, aiohttp_client):

          async def handler(request):
              return web.Response(text="OK")

          raw_server = await aiohttp_raw_server(handler)
          client = await aiohttp_client(raw_server)
          resp = await client.get('/')

   *handler* should be a coroutine which accepts a request and returns
   response, e.g.

   *port* optional, port the server is run at, if
   not provided a random unused port is used.

   .. versionadded:: 3.0

.. data:: aiohttp_unused_port()

   Function to return an unused port number for IPv4 TCP protocol::

      async def test_f(aiohttp_client, aiohttp_unused_port):
          port = aiohttp_unused_port()
          app = web.Application()
          # fill route table

          client = await aiohttp_client(app, server_kwargs={'port': port})
          ...

   .. versionchanged:: 3.0

      The fixture was renamed from ``unused_port`` to ``aiohttp_unused_port``.

.. data:: aiohttp_client_cls

   A fixture for passing custom :class:`~aiohttp.test_utils.TestClient` implementations::

      class MyClient(TestClient):
          async def login(self, *, user, pw):
              payload = {"username": user, "password": pw}
              return await self.post("/login", json=payload)

      @pytest.fixture
      def aiohttp_client_cls():
          return MyClient

      def test_login(aiohttp_client):
          app = web.Application()
          client = await aiohttp_client(app)
          await client.login(user="admin", pw="s3cr3t")

   If you want to switch between different clients in tests, you can use
   the usual ``pytest`` machinery. Example with using test markers::

      class RESTfulClient(TestClient):
          ...

      class GraphQLClient(TestClient):
          ...

      @pytest.fixture
      def aiohttp_client_cls(request):
          if request.node.get_closest_marker('rest') is not None:
              return RESTfulClient
          if request.node.get_closest_marker('graphql') is not None:
              return GraphQLClient
          return TestClient


      @pytest.mark.rest
      async def test_rest(aiohttp_client) -> None:
          client: RESTfulClient = await aiohttp_client(Application())
          ...


      @pytest.mark.graphql
      async def test_graphql(aiohttp_client) -> None:
          client: GraphQLClient = await aiohttp_client(Application())
          ...


.. _aiohttp-testing-unittest-example:

.. _aiohttp-testing-unittest-style:

Unittest
~~~~~~~~

.. currentmodule:: aiohttp.test_utils


To test applications with the standard library's unittest or unittest-based
functionality, the AioHTTPTestCase is provided::

    from aiohttp.test_utils import AioHTTPTestCase
    from aiohttp import web

    class MyAppTestCase(AioHTTPTestCase):

        async def get_application(self):
            """
            Override the get_app method to return your application.
            """
            async def hello(request):
                return web.Response(text='Hello, world')

            app = web.Application()
            app.router.add_get('/', hello)
            return app

        async def test_example(self):
            async with self.client.request("GET", "/") as resp:
                self.assertEqual(resp.status, 200)
                text = await resp.text()
            self.assertIn("Hello, world", text)

.. class:: AioHTTPTestCase

    A base class to allow for unittest web applications using aiohttp.

    Derived from :class:`unittest.IsolatedAsyncioTestCase`

    See :class:`unittest.TestCase` and :class:`unittest.IsolatedAsyncioTestCase`
    for inherited methods and behavior.

    This class additionally provides the following:

    .. attribute:: client

       an aiohttp test client, :class:`TestClient` instance.

    .. attribute:: server

       an aiohttp test server, :class:`TestServer` instance.

       .. versionadded:: 2.3

    .. attribute:: app

       The application returned by :meth:`~aiohttp.test_utils.AioHTTPTestCase.get_application`
       (:class:`aiohttp.web.Application` instance).

    .. method:: get_client()
      :async:

       This async method can be overridden to return the :class:`TestClient`
       object used in the test.

       :return: :class:`TestClient` instance.

       .. versionadded:: 2.3

    .. method:: get_server()
      :async:

       This async method can be overridden to return the :class:`TestServer`
       object used in the test.

       :return: :class:`TestServer` instance.

       .. versionadded:: 2.3

    .. method:: get_application()
      :async:

       This async method should be overridden
       to return the :class:`aiohttp.web.Application`
       object to test.

       :return: :class:`aiohttp.web.Application` instance.

    .. method:: asyncSetUp()
      :async:

       This async method can be overridden to execute asynchronous code during
       the ``setUp`` stage of the ``TestCase``::

           async def asyncSetUp(self):
               await super().asyncSetUp()
               await foo()

       .. versionadded:: 2.3

       .. versionchanged:: 3.8

          ``await super().asyncSetUp()`` call is required.

    .. method:: asyncTearDown()
      :async:

       This async method can be overridden to execute asynchronous code during
       the ``tearDown`` stage of the ``TestCase``::

           async def asyncTearDown(self):
               await super().asyncTearDown()
               await foo()

       .. versionadded:: 2.3

       .. versionchanged:: 3.8

          ``await super().asyncTearDown()`` call is required.

Faking request object
^^^^^^^^^^^^^^^^^^^^^

aiohttp provides test utility for creating fake
:class:`aiohttp.web.Request` objects:
:func:`aiohttp.test_utils.make_mocked_request`, it could be useful in
case of simple unit tests, like handler tests, or simulate error
conditions that hard to reproduce on real server::

    from aiohttp import web
    from aiohttp.test_utils import make_mocked_request

    def handler(request):
        assert request.headers.get('token') == 'x'
        return web.Response(body=b'data')

    def test_handler():
        req = make_mocked_request('GET', '/', headers={'token': 'x'})
        resp = handler(req)
        assert resp.body == b'data'

.. warning::

   We don't recommend to apply
   :func:`~aiohttp.test_utils.make_mocked_request` everywhere for
   testing web-handler's business object -- please use test client and
   real networking via 'localhost' as shown in examples before.

   :func:`~aiohttp.test_utils.make_mocked_request` exists only for
   testing complex cases (e.g. emulating network errors) which
   are extremely hard or even impossible to test by conventional
   way.


.. function:: make_mocked_request(method, path, headers=None, *, \
                                  version=HttpVersion(1, 1), \
                                  closing=False, \
                                  app=None, \
                                  match_info=sentinel, \
                                  reader=sentinel, \
                                  writer=sentinel, \
                                  transport=sentinel, \
                                  payload=sentinel, \
                                  sslcontext=None, \
                                  loop=...)

   Creates mocked web.Request testing purposes.

   Useful in unit tests, when spinning full web server is overkill or
   specific conditions and errors are hard to trigger.

   :param method: str, that represents HTTP method, like; GET, POST.
   :type method: str

   :param path: str, The URL including *PATH INFO* without the host or scheme
   :type path: str

   :param headers: mapping containing the headers. Can be anything accepted
       by the multidict.CIMultiDict constructor.
   :type headers: dict, multidict.CIMultiDict, list of tuple(str, str)

   :param match_info: mapping containing the info to match with url parameters.
   :type match_info: dict

   :param version: namedtuple with encoded HTTP version
   :type version: aiohttp.protocol.HttpVersion

   :param closing: flag indicates that connection should be closed after
       response.
   :type closing: bool

   :param app: the aiohttp.web application attached for fake request
   :type app: aiohttp.web.Application

   :param writer: object for managing outcoming data
   :type writer: aiohttp.StreamWriter

   :param transport: asyncio transport instance
   :type transport: asyncio.Transport

   :param payload: raw payload reader object
   :type  payload: aiohttp.StreamReader

   :param sslcontext: ssl.SSLContext object, for HTTPS connection
   :type sslcontext: ssl.SSLContext

   :param loop: An event loop instance, mocked loop by default.
   :type loop: :class:`asyncio.AbstractEventLoop`

   :return: :class:`aiohttp.web.Request` object.

   .. versionadded:: 2.3
      *match_info* parameter.

.. _aiohttp-testing-writing-testable-services:

.. _aiohttp-testing-framework-agnostic-utilities:


Framework Agnostic Utilities
----------------------------

High level test creation::

    from aiohttp.test_utils import TestClient, TestServer
    from aiohttp import request

    async def test():
        app = _create_example_app()
        async with TestClient(TestServer(app)) as client:

            async def test_get_route():
                nonlocal client
                resp = await client.get("/")
                assert resp.status == 200
                text = await resp.text()
                assert "Hello, world" in text

            await test_get_route()


If it's preferred to handle the creation / teardown on a more granular
basis, the TestClient object can be used directly::

    from aiohttp.test_utils import TestClient, TestServer

    async def test():
        app = _create_example_app()
        client = TestClient(TestServer(app))
        await client.start_server()
        root = "http://127.0.0.1:{}".format(port)

        async def test_get_route():
            resp = await client.get("/")
            assert resp.status == 200
            text = await resp.text()
            assert "Hello, world" in text

        await test_get_route()
        await client.close()


A full list of the utilities provided can be found at the
:data:`api reference <aiohttp.test_utils>`


Testing API Reference
---------------------

Test server
~~~~~~~~~~~

Runs given :class:`aiohttp.web.Application` instance on random TCP port.

After creation the server is not started yet, use
:meth:`~aiohttp.test_utils.BaseTestServer.start_server` for actual server
starting and :meth:`~aiohttp.test_utils.BaseTestServer.close` for
stopping/cleanup.

Test server usually works in conjunction with
:class:`aiohttp.test_utils.TestClient` which provides handy client methods
for accessing to the server.

.. class:: BaseTestServer(*, scheme='http', host='127.0.0.1', port=None, socket_factory=get_port_socket)

   Base class for test servers.

   :param str scheme: HTTP scheme, non-protected ``"http"`` by default.

   :param str host: a host for TCP socket, IPv4 *local host*
      (``'127.0.0.1'``) by default.

   :param int port: optional port for TCP socket, if not provided a
      random unused port is used.

      .. versionadded:: 3.0

   :param collections.abc.Callable[[str,int,socket.AddressFamily],socket.socket] socket_factory: optional
                          Factory to create a socket for the server.
                          By default creates a TCP socket and binds it
                          to ``host`` and ``port``.

      .. versionadded:: 3.8

   .. attribute:: scheme

      A *scheme* for tested application, ``'http'`` for non-protected
      run and ``'https'`` for TLS encrypted server.

   .. attribute:: host

      *host* used to start a test server.

   .. attribute:: port

      *port* used to start the test server.

   .. attribute:: handler

      :class:`aiohttp.web.Server` used for HTTP requests serving.

   .. attribute:: server

      :class:`asyncio.AbstractServer` used for managing accepted connections.

   .. attribute:: socket_factory

      *socket_factory* used to create and bind a server socket.

      .. versionadded:: 3.8

   .. method:: start_server(**kwargs)
      :async:

      Start a test server.

   .. method:: close()
      :async:

      Stop and finish executed test server.

   .. method:: make_url(path)

      Return an *absolute* :class:`~yarl.URL` for given *path*.


.. class:: RawTestServer(handler, *, scheme="http", host='127.0.0.1')

   Low-level test server (derived from :class:`BaseTestServer`).

   :param handler: a coroutine for handling web requests. The
                   handler should accept
                   :class:`aiohttp.web.BaseRequest` and return a
                   response instance,
                   e.g. :class:`~aiohttp.web.StreamResponse` or
                   :class:`~aiohttp.web.Response`.

                   The handler could raise
                   :class:`~aiohttp.web.HTTPException` as a signal for
                   non-200 HTTP response.

   :param str scheme: HTTP scheme, non-protected ``"http"`` by default.

   :param str host: a host for TCP socket, IPv4 *local host*
      (``'127.0.0.1'``) by default.

   :param int port: optional port for TCP socket, if not provided a
      random unused port is used.

      .. versionadded:: 3.0


.. class:: TestServer(app, *, scheme="http", host='127.0.0.1')

   Test server (derived from :class:`BaseTestServer`) for starting
   :class:`~aiohttp.web.Application`.

   :param app: :class:`aiohttp.web.Application` instance to run.

   :param str scheme: HTTP scheme, non-protected ``"http"`` by default.

   :param str host: a host for TCP socket, IPv4 *local host*
      (``'127.0.0.1'``) by default.

   :param int port: optional port for TCP socket, if not provided a
      random unused port is used.

      .. versionadded:: 3.0

   .. attribute:: app

      :class:`aiohttp.web.Application` instance to run.


Test Client
~~~~~~~~~~~

.. class:: TestClient(app_or_server, *, \
                      scheme='http', host='127.0.0.1', \
                      cookie_jar=None, **kwargs)

   A test client used for making calls to tested server.

   :param app_or_server: :class:`BaseTestServer` instance for making
                         client requests to it.

                         In order to pass an :class:`aiohttp.web.Application`
                         you need to convert it first to :class:`TestServer`
                         first with ``TestServer(app)``.

   :param cookie_jar: an optional :class:`aiohttp.CookieJar` instance,
                      may be useful with
                      ``CookieJar(unsafe=True, treat_as_secure_origin="http://127.0.0.1")``
                      option.

   :param str scheme: HTTP scheme, non-protected ``"http"`` by default.

   :param str host: a host for TCP socket, IPv4 *local host*
      (``'127.0.0.1'``) by default.

   .. attribute:: scheme

      A *scheme* for tested application, ``'http'`` for non-protected
      run and ``'https'`` for TLS encrypted server.

   .. attribute:: host

      *host* used to start a test server.

   .. attribute:: port

      *port* used to start the server

   .. attribute:: server

      :class:`BaseTestServer` test server instance used in conjunction
      with client.

   .. attribute:: app

      An alias for ``self.server.app``. return ``None`` if
      ``self.server`` is not :class:`TestServer`
      instance(e.g. :class:`RawTestServer` instance for test low-level server).

   .. attribute:: session

      An internal :class:`aiohttp.ClientSession`.

      Unlike the methods on the :class:`TestClient`, client session
      requests do not automatically include the host in the url
      queried, and will require an absolute path to the resource.

   .. method:: start_server(**kwargs)
      :async:

      Start a test server.

   .. method:: close()
      :async:

      Stop and finish executed test server.

   .. method:: make_url(path)

      Return an *absolute* :class:`~yarl.URL` for given *path*.

   .. method:: request(method, path, *args, **kwargs)
      :async:

      Routes a request to tested http server.

      The interface is identical to
      :meth:`aiohttp.ClientSession.request`, except the loop kwarg is
      overridden by the instance used by the test server.

   .. method:: get(path, *args, **kwargs)
      :async:

      Perform an HTTP GET request.

   .. method:: post(path, *args, **kwargs)
      :async:

      Perform an HTTP POST request.

   .. method:: options(path, *args, **kwargs)
      :async:

      Perform an HTTP OPTIONS request.

   .. method:: head(path, *args, **kwargs)
      :async:

      Perform an HTTP HEAD request.

   .. method:: put(path, *args, **kwargs)
      :async:

      Perform an HTTP PUT request.

   .. method:: patch(path, *args, **kwargs)
      :async:

      Perform an HTTP PATCH request.

   .. method:: delete(path, *args, **kwargs)
      :async:

      Perform an HTTP DELETE request.

   .. method:: ws_connect(path, *args, **kwargs)
      :async:

      Initiate websocket connection.

      The api corresponds to :meth:`aiohttp.ClientSession.ws_connect`.


Utilities
~~~~~~~~~

.. function:: unused_port()

   Return an unused port number for IPv4 TCP protocol.

   :return int: ephemeral port number which could be reused by test server.

.. function:: loop_context(loop_factory=<function asyncio.new_event_loop>)

   A contextmanager that creates an event_loop, for test purposes.

   Handles the creation and cleanup of a test loop.

.. function:: setup_test_loop(loop_factory=<function asyncio.new_event_loop>)

   Create and return an :class:`asyncio.AbstractEventLoop` instance.

   The caller should also call teardown_test_loop, once they are done
   with the loop.

   .. note::

      As side effect the function changes asyncio *default loop* by
      :func:`asyncio.set_event_loop` call.

      Previous default loop is not restored.

      It should not be a problem for test suite: every test expects a
      new test loop instance anyway.

   .. versionchanged:: 3.1

      The function installs a created event loop as *default*.

.. function:: teardown_test_loop(loop)

   Teardown and cleanup an event_loop created by setup_test_loop.

   :param loop: the loop to teardown
   :type loop: asyncio.AbstractEventLoop



.. _pytest: http://pytest.org/latest/
.. _pytest-aiohttp: https://pypi.python.org/pypi/pytest-aiohttp
````

## File: docs/third_party.rst
````
.. _aiohttp-3rd-party:

Third-Party libraries
=====================


aiohttp is not just a library for making HTTP requests and creating web
servers.

It is the foundation for libraries built *on top* of aiohttp.

This page is a list of these tools.

Please feel free to add your open source library if it's not listed
yet by making a pull request to https://github.com/aio-libs/aiohttp/

* Why would you want to include your awesome library in this list?

* Because the list increases your library visibility. People
  will have an easy way to find it.


Officially supported
--------------------

This list contains libraries which are supported by the *aio-libs* team
and located on https://github.com/aio-libs


aiohttp extensions
^^^^^^^^^^^^^^^^^^

- `aiohttp-apischema <https://github.com/aio-libs/aiohttp-apischema>`_
  provides automatic API schema generation and validation of user input
  for :mod:`aiohttp.web`.

- `aiohttp-session <https://github.com/aio-libs/aiohttp-session>`_
  provides sessions for :mod:`aiohttp.web`.

- `aiohttp-debugtoolbar <https://github.com/aio-libs/aiohttp-debugtoolbar>`_
  is a library for *debug toolbar* support for :mod:`aiohttp.web`.

- `aiohttp-security <https://github.com/aio-libs/aiohttp-security>`_
  auth and permissions for :mod:`aiohttp.web`.

- `aiohttp-devtools <https://github.com/aio-libs/aiohttp-devtools>`_
  provides development tools for :mod:`aiohttp.web` applications.

- `aiohttp-cors <https://github.com/aio-libs/aiohttp-cors>`_ CORS
  support for aiohttp.

- `aiohttp-sse <https://github.com/aio-libs/aiohttp-sse>`_ Server-sent
  events support for aiohttp.

- `pytest-aiohttp <https://github.com/aio-libs/pytest-aiohttp>`_
  pytest plugin for aiohttp support.

- `aiohttp-mako <https://github.com/aio-libs/aiohttp-mako>`_ Mako
  template renderer for aiohttp.web.

- `aiohttp-jinja2 <https://github.com/aio-libs/aiohttp-jinja2>`_ Jinja2
  template renderer for aiohttp.web.

- `aiozipkin <https://github.com/aio-libs/aiozipkin>`_ distributed
  tracing instrumentation for `aiohttp` client and server.

Database drivers
^^^^^^^^^^^^^^^^

- `aiopg <https://github.com/aio-libs/aiopg>`_ PostgreSQL async driver.

- `aiomysql <https://github.com/aio-libs/aiomysql>`_ MySQL async driver.

- `aioredis <https://github.com/aio-libs/aioredis>`_ Redis async driver.

Other tools
^^^^^^^^^^^

- `aiodocker <https://github.com/aio-libs/aiodocker>`_ Python Docker
  API client based on asyncio and aiohttp.

- `aiobotocore <https://github.com/aio-libs/aiobotocore>`_ asyncio
  support for botocore library using aiohttp.


Approved third-party libraries
------------------------------

These libraries are not part of ``aio-libs`` but they have proven to be very
well written and highly recommended for usage.

- `uvloop <https://github.com/MagicStack/uvloop>`_ Ultra fast
  implementation of asyncio event loop on top of ``libuv``.

  We highly recommend to use this instead of standard ``asyncio``.

Database drivers
^^^^^^^^^^^^^^^^

- `asyncpg <https://github.com/MagicStack/asyncpg>`_ Another
  PostgreSQL async driver. It's much faster than ``aiopg`` but is
  not a drop-in replacement -- the API is different. But, please take
  a look at it -- the driver is incredibly fast.

OpenAPI / Swagger extensions
----------------------------

Extensions bringing `OpenAPI <https://swagger.io/docs/specification/about>`_
support to aiohttp web servers.

- `aiohttp-apispec <https://github.com/maximdanilchenko/aiohttp-apispec>`_
  Build and document REST APIs with ``aiohttp`` and ``apispec``.

- `aiohttp_apiset <https://github.com/aamalev/aiohttp_apiset>`_
  Package to build routes using swagger specification.

- `aiohttp-pydantic <https://github.com/Maillol/aiohttp-pydantic>`_
  An ``aiohttp.View`` to validate the HTTP request's body, query-string, and
  headers regarding function annotations and generate OpenAPI doc.

- `aiohttp-swagger <https://github.com/cr0hn/aiohttp-swagger>`_
  Swagger API Documentation builder for aiohttp server.

- `aiohttp-swagger3 <https://github.com/hh-h/aiohttp-swagger3>`_
  Library for Swagger documentation builder and validating aiohttp requests
  using swagger specification 3.0.

- `aiohttp-swaggerify <https://github.com/dchaplinsky/aiohttp_swaggerify>`_
  Library to automatically generate swagger2.0 definition for aiohttp endpoints.

- `aio-openapi <https://github.com/quantmind/aio-openapi>`_
  Asynchronous web middleware for aiohttp and serving Rest APIs with OpenAPI v3
  specification and with optional PostgreSQL database bindings.

- `rororo <https://github.com/playpauseandstop/rororo>`_
  Implement ``aiohttp.web`` OpenAPI 3 server applications with schema first
  approach.

Others
------

Here is a list of other known libraries that do not belong in the former categories.

We cannot vouch for the quality of these libraries, use them at your own risk.

Please add your library reference here first and after some time
ask to raise the status.

- `pytest-aiohttp-client <https://github.com/sivakov512/pytest-aiohttp-client>`_
  Pytest fixture with simpler api, payload decoding and status code assertions.

- `octomachinery <https://octomachinery.dev>`_ A framework for developing
  GitHub Apps and GitHub Actions.

- `aiomixcloud <https://github.com/amikrop/aiomixcloud>`_
  Mixcloud API wrapper for Python and Async IO.

- `aiohttp-cache <https://github.com/cr0hn/aiohttp-cache>`_ A cache
  system for aiohttp server.

- `aiocache <https://github.com/argaen/aiocache>`_ Caching for asyncio
  with multiple backends (framework agnostic)

- `gain <https://github.com/gaojiuli/gain>`_ Web crawling framework
  based on asyncio for everyone.

- `aiohttp-validate <https://github.com/dchaplinsky/aiohttp_validate>`_
  Simple library that helps you validate your API endpoints requests/responses with json schema.

- `raven-aiohttp <https://github.com/getsentry/raven-aiohttp>`_ An
  aiohttp transport for raven-python (Sentry client).

- `webargs <https://github.com/sloria/webargs>`_ A friendly library
  for parsing HTTP request arguments, with built-in support for
  popular web frameworks, including Flask, Django, Bottle, Tornado,
  Pyramid, webapp2, Falcon, and aiohttp.

- `aiohttpretty
  <https://github.com/CenterForOpenScience/aiohttpretty>`_ A simple
  asyncio compatible httpretty mock using aiohttp.

- `aioresponses <https://github.com/pnuckowski/aioresponses>`_ a
  helper for mock/fake web requests in python aiohttp package.

- `aiohttp-transmute
  <https://github.com/toumorokoshi/aiohttp-transmute>`_ A transmute
  implementation for aiohttp.

- `aiohttp-login <https://github.com/imbolc/aiohttp-login>`_
  Registration and authorization (including social) for aiohttp
  applications.

- `aiohttp_utils <https://github.com/sloria/aiohttp_utils>`_ Handy
  utilities for building aiohttp.web applications.

- `aiohttpproxy <https://github.com/jmehnle/aiohttpproxy>`_ Simple
  aiohttp HTTP proxy.

- `aiohttp_traversal <https://github.com/zzzsochi/aiohttp_traversal>`_
  Traversal based router for aiohttp.web.

- `aiohttp_autoreload
  <https://github.com/anti1869/aiohttp_autoreload>`_ Makes aiohttp
  server auto-reload on source code change.

- `gidgethub <https://github.com/brettcannon/gidgethub>`_ An async
  GitHub API library for Python.

- `aiohttp-rpc <https://github.com/expert-m/aiohttp-rpc>`_ A simple
  JSON-RPC for aiohttp.

- `aiohttp_jrpc <https://github.com/zloidemon/aiohttp_jrpc>`_ aiohttp
  JSON-RPC service.

- `fbemissary <https://github.com/cdunklau/fbemissary>`_ A bot
  framework for the Facebook Messenger platform, built on asyncio and
  aiohttp.

- `aioslacker <https://github.com/wikibusiness/aioslacker>`_ slacker
  wrapper for asyncio.

- `aioreloader <https://github.com/and800/aioreloader>`_ Port of
  tornado reloader to asyncio.

- `aiohttp_babel <https://github.com/jie/aiohttp_babel>`_ Babel
  localization support for aiohttp.

- `python-mocket <https://github.com/mindflayer/python-mocket>`_ a
  socket mock framework - for all kinds of socket animals, web-clients
  included.

- `aioraft <https://github.com/lisael/aioraft>`_ asyncio RAFT
  algorithm based on aiohttp.

- `home-assistant <https://github.com/home-assistant/home-assistant>`_
  Open-source home automation platform running on Python 3.

- `discord.py <https://github.com/Rapptz/discord.py>`_ Discord client library.

- `aiogram <https://github.com/aiogram/aiogram>`_
  A fully asynchronous library for Telegram Bot API written with asyncio and aiohttp.

- `aiohttp-graphql <https://github.com/graphql-python/aiohttp-graphql>`_
  GraphQL and GraphIQL interface for aiohttp.

- `aiohttp-sentry <https://github.com/underyx/aiohttp-sentry>`_
  An aiohttp middleware for reporting errors to Sentry.

- `aiohttp-datadog <https://github.com/underyx/aiohttp-datadog>`_
  An aiohttp middleware for reporting metrics to DataDog.

- `async-v20 <https://github.com/jamespeterschinner/async_v20>`_
  Asynchronous FOREX client for OANDA's v20 API.

- `aiohttp-jwt <https://github.com/hzlmn/aiohttp-jwt>`_
  An aiohttp middleware for JWT(JSON Web Token) support.

- `AWS Xray Python SDK <https://github.com/aws/aws-xray-sdk-python>`_
  Native tracing support for Aiohttp applications.

- `GINO <https://github.com/fantix/gino>`_
  An asyncio ORM on top of SQLAlchemy core, delivered with an aiohttp extension.

- `New Relic <https://github.com/newrelic/newrelic-quickstarts/tree/main/quickstarts/python/aiohttp>`_ An aiohttp middleware for reporting your `Python application performance <https://newrelic.com/instant-observability/aiohttp>`_ metrics to New Relic.

- `eider-py <https://github.com/eider-rpc/eider-py>`_ Python implementation of
  the `Eider RPC protocol <http://eider.readthedocs.io/>`_.

- `asynapplicationinsights
  <https://github.com/RobertoPrevato/asynapplicationinsights>`_ A client for
  `Azure Application Insights
  <https://azure.microsoft.com/en-us/services/application-insights/>`_
  implemented using ``aiohttp`` client, including a middleware for ``aiohttp``
  servers to collect web apps telemetry.

- `aiogmaps <https://github.com/hzlmn/aiogmaps>`_
  Asynchronous client for Google Maps API Web Services.

- `DBGR <https://github.com/JakubTesarek/dbgr>`_
  Terminal based tool to test and debug HTTP APIs with ``aiohttp``.

- `aiohttp-middlewares <https://github.com/playpauseandstop/aiohttp-middlewares>`_
  Collection of useful middlewares for ``aiohttp.web`` applications.

- `aiohttp-tus <https://github.com/pylotcode/aiohttp-tus>`_
  `tus.io <https://tus.io>`_ protocol implementation for ``aiohttp.web``
  applications.

- `aiohttp-sse-client <https://github.com/rtfol/aiohttp-sse-client>`_
  A Server-Sent Event python client base on aiohttp.

- `aiohttp-retry <https://github.com/inyutin/aiohttp_retry>`_
  Wrapper for aiohttp client for retrying requests.

- `aiohttp-socks <https://github.com/romis2012/aiohttp-socks>`_
  SOCKS proxy connector for aiohttp.

- `aiohttp-catcher <https://github.com/yuvalherziger/aiohttp-catcher>`_
  An aiohttp middleware library for centralized error handling in aiohttp servers.

- `rsocket <https://github.com/rsocket/rsocket-py>`_
  Python implementation of `RSocket protocol <https://rsocket.io>`_.

- `nacl_middleware <https://github.com/CosmicDNA/nacl_middleware>`_
  An aiohttp middleware library for asymmetric encryption of data transmitted via http and/or websocket connections.

- `aiohttp-asgi-connector <https://github.com/thearchitector/aiohttp-asgi-connector>`_
  An aiohttp connector for using a ``ClientSession`` to interface directly with separate ASGI applications.

- `aiohttp-openmetrics <https://github.com/jelmer/aiohttp-openmetrics>`_
  An aiohttp middleware for exposing Prometheus metrics.

- `wireup <https://github.com/maldoinc/wireup>`_
  Performant, concise, and easy-to-use dependency injection container.
````

## File: docs/tracing_reference.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-client-tracing-reference:

Tracing Reference
=================

.. versionadded:: 3.0

A reference for client tracing API.

.. seealso:: :ref:`aiohttp-client-tracing` for tracing usage instructions.


Request life cycle
------------------

A request goes through the following stages and corresponding fallbacks.


Overview
^^^^^^^^

.. graphviz::

   digraph {

     start[shape=point, xlabel="start", width="0.1"];
     redirect[shape=box];
     end[shape=point, xlabel="end  ", width="0.1"];
     exception[shape=oval];

     acquire_connection[shape=box];
     headers_received[shape=box];
     headers_sent[shape=box];
     chunk_sent[shape=box];
     chunk_received[shape=box];

     start -> acquire_connection;
     acquire_connection -> headers_sent;
     headers_sent -> headers_received;
     headers_sent -> chunk_sent;
     chunk_sent -> chunk_sent;
     chunk_sent -> headers_received;
     headers_received -> chunk_received;
     chunk_received -> chunk_received;
     chunk_received -> end;
     headers_received -> redirect;
     headers_received -> end;
     redirect -> headers_sent;
     chunk_received -> exception;
     chunk_sent -> exception;
     headers_sent -> exception;

   }

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - start
     - on_request_start
   * - redirect
     - on_request_redirect
   * - acquire_connection
     - Connection acquiring
   * - headers_received
     -
   * - exception
     - on_request_exception
   * - end
     - on_request_end
   * - headers_sent
     - on_request_headers_sent
   * - chunk_sent
     - on_request_chunk_sent
   * - chunk_received
     - on_response_chunk_received

Connection acquiring
^^^^^^^^^^^^^^^^^^^^

.. graphviz::

   digraph {

     begin[shape=point, xlabel="begin", width="0.1"];
     end[shape=point, xlabel="end ", width="0.1"];
     exception[shape=oval];

     queued_start[shape=box];
     queued_end[shape=box];
     create_start[shape=box];
     create_end[shape=box];
     reuseconn[shape=box];
     resolve_dns[shape=box];
     sock_connect[shape=box];

     begin -> reuseconn;
     begin -> create_start;
     create_start -> resolve_dns;
     resolve_dns -> exception;
     resolve_dns -> sock_connect;
     sock_connect -> exception;
     sock_connect -> create_end -> end;
     begin -> queued_start;
     queued_start -> queued_end;
     queued_end -> reuseconn;
     queued_end -> create_start;
     reuseconn -> end;

   }

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - begin
     -
   * - end
     -
   * - queued_start
     - on_connection_queued_start
   * - create_start
     - on_connection_create_start
   * - reuseconn
     - on_connection_reuseconn
   * - queued_end
     - on_connection_queued_end
   * - create_end
     - on_connection_create_end
   * - exception
     - Exception raised
   * - resolve_dns
     - DNS resolving
   * - sock_connect
     - Connection establishment

DNS resolving
^^^^^^^^^^^^^

.. graphviz::

   digraph {

     begin[shape=point, xlabel="begin", width="0.1"];
     end[shape=point, xlabel="end", width="0.1"];
     exception[shape=oval];

     resolve_start[shape=box];
     resolve_end[shape=box];
     cache_hit[shape=box];
     cache_miss[shape=box];

     begin -> cache_hit -> end;
     begin -> cache_miss -> resolve_start;
     resolve_start -> resolve_end -> end;
     resolve_start -> exception;

   }

.. list-table::
   :header-rows: 1

   * - Name
     - Description
   * - begin
     -
   * - end
     -
   * - exception
     - Exception raised
   * - resolve_end
     - on_dns_resolvehost_end
   * - resolve_start
     - on_dns_resolvehost_start
   * - cache_hit
     - on_dns_cache_hit
   * - cache_miss
     - on_dns_cache_miss

Classes
-------

.. class:: TraceConfig(trace_config_ctx_factory=SimpleNamespace)

   Trace config is the configuration object used to trace requests
   launched by a :class:`ClientSession` object using different events
   related to different parts of the request flow.

   :param trace_config_ctx_factory: factory used to create trace contexts,
      default class used :class:`types.SimpleNamespace`

   .. method:: trace_config_ctx(trace_request_ctx=None)

      :param trace_request_ctx: Will be used to pass as a kw for the
        ``trace_config_ctx_factory``.

      Build a new trace context from the config.

   Every signal handler should have the following signature::

      async def on_signal(session, context, params): ...

   where ``session`` is :class:`ClientSession` instance, ``context`` is an
   object returned by :meth:`trace_config_ctx` call and ``params`` is a
   data class with signal parameters. The type of ``params`` depends on
   subscribed signal and described below.

   .. attribute:: on_request_start

      Property that gives access to the signals that will be executed
      when a request starts.

      ``params`` is :class:`aiohttp.TraceRequestStartParams` instance.

   .. attribute:: on_request_chunk_sent


      Property that gives access to the signals that will be executed
      when a chunk of request body is sent.

      ``params`` is :class:`aiohttp.TraceRequestChunkSentParams` instance.

      .. versionadded:: 3.1

   .. attribute:: on_response_chunk_received


      Property that gives access to the signals that will be executed
      when a chunk of response body is received.

      ``params`` is :class:`aiohttp.TraceResponseChunkReceivedParams` instance.

      .. versionadded:: 3.1

   .. attribute:: on_request_redirect

      Property that gives access to the signals that will be executed when a
      redirect happens during a request flow.

      ``params`` is :class:`aiohttp.TraceRequestRedirectParams` instance.

   .. attribute:: on_request_end

      Property that gives access to the signals that will be executed when a
      request ends.

      ``params`` is :class:`aiohttp.TraceRequestEndParams` instance.

   .. attribute:: on_request_exception

      Property that gives access to the signals that will be executed when a
      request finishes with an exception.

      ``params`` is :class:`aiohttp.TraceRequestExceptionParams` instance.

   .. attribute:: on_connection_queued_start

      Property that gives access to the signals that will be executed when a
      request has been queued waiting for an available connection.

      ``params`` is :class:`aiohttp.TraceConnectionQueuedStartParams`
      instance.

   .. attribute:: on_connection_queued_end

      Property that gives access to the signals that will be executed when a
      request that was queued already has an available connection.

      ``params`` is :class:`aiohttp.TraceConnectionQueuedEndParams`
      instance.

   .. attribute:: on_connection_create_start

      Property that gives access to the signals that will be executed when a
      request creates a new connection.

      ``params`` is :class:`aiohttp.TraceConnectionCreateStartParams`
      instance.

   .. attribute:: on_connection_create_end

      Property that gives access to the signals that will be executed when a
      request that created a new connection finishes its creation.

      ``params`` is :class:`aiohttp.TraceConnectionCreateEndParams`
      instance.

   .. attribute:: on_connection_reuseconn

      Property that gives access to the signals that will be executed when a
      request reuses a connection.

      ``params`` is :class:`aiohttp.TraceConnectionReuseconnParams`
      instance.

   .. attribute:: on_dns_resolvehost_start

      Property that gives access to the signals that will be executed when a
      request starts to resolve the domain related with the request.

      ``params`` is :class:`aiohttp.TraceDnsResolveHostStartParams`
      instance.

   .. attribute:: on_dns_resolvehost_end

      Property that gives access to the signals that will be executed when a
      request finishes to resolve the domain related with the request.

      ``params`` is :class:`aiohttp.TraceDnsResolveHostEndParams` instance.

   .. attribute:: on_dns_cache_hit

      Property that gives access to the signals that will be executed when a
      request was able to use a cached DNS resolution for the domain related
      with the request.

      ``params`` is :class:`aiohttp.TraceDnsCacheHitParams` instance.

   .. attribute:: on_dns_cache_miss

      Property that gives access to the signals that will be executed when a
      request was not able to use a cached DNS resolution for the domain related
      with the request.

      ``params`` is :class:`aiohttp.TraceDnsCacheMissParams` instance.

   .. attribute:: on_request_headers_sent

      Property that gives access to the signals that will be executed
      when request headers are sent.

      ``params`` is :class:`aiohttp.TraceRequestHeadersSentParams` instance.

      .. versionadded:: 3.8


.. class:: TraceRequestStartParams

   See :attr:`TraceConfig.on_request_start` for details.

   .. attribute:: method

       Method that will be used  to make the request.

   .. attribute:: url

       URL that will be used  for the request.

   .. attribute:: headers

       Headers that will be used for the request, can be mutated.


.. class:: TraceRequestChunkSentParams

   .. versionadded:: 3.1

   See :attr:`TraceConfig.on_request_chunk_sent` for details.

   .. attribute:: method

       Method that will be used  to make the request.

   .. attribute:: url

       URL that will be used  for the request.

   .. attribute:: chunk

       Bytes of chunk sent


.. class:: TraceResponseChunkReceivedParams

   .. versionadded:: 3.1

   See :attr:`TraceConfig.on_response_chunk_received` for details.

   .. attribute:: method

       Method that will be used  to make the request.

   .. attribute:: url

       URL that will be used  for the request.

   .. attribute:: chunk

       Bytes of chunk received


.. class:: TraceRequestEndParams

   See :attr:`TraceConfig.on_request_end` for details.

   .. attribute:: method

       Method used to make the request.

   .. attribute:: url

       URL used for the request.

   .. attribute:: headers

       Headers used for the request.

   .. attribute:: response

       Response :class:`ClientResponse`.


.. class:: TraceRequestExceptionParams

   See :attr:`TraceConfig.on_request_exception` for details.

   .. attribute:: method

       Method used to make the request.

   .. attribute:: url

       URL used for the request.

   .. attribute:: headers

       Headers used for the request.

   .. attribute:: exception

       Exception raised during the request.


.. class:: TraceRequestRedirectParams

   See :attr:`TraceConfig.on_request_redirect` for details.

   .. attribute:: method

       Method used to get this redirect request.

   .. attribute:: url

       URL used for this redirect request.

   .. attribute:: headers

       Headers used for this redirect.

   .. attribute:: response

       Response :class:`ClientResponse` got from the redirect.


.. class:: TraceConnectionQueuedStartParams

   See :attr:`TraceConfig.on_connection_queued_start` for details.

   There are no attributes right now.


.. class:: TraceConnectionQueuedEndParams

   See :attr:`TraceConfig.on_connection_queued_end` for details.

   There are no attributes right now.


.. class:: TraceConnectionCreateStartParams

   See :attr:`TraceConfig.on_connection_create_start` for details.

   There are no attributes right now.


.. class:: TraceConnectionCreateEndParams

   See :attr:`TraceConfig.on_connection_create_end` for details.

   There are no attributes right now.


.. class:: TraceConnectionReuseconnParams

   See :attr:`TraceConfig.on_connection_reuseconn` for details.

   There are no attributes right now.


.. class:: TraceDnsResolveHostStartParams

   See :attr:`TraceConfig.on_dns_resolvehost_start` for details.

   .. attribute:: host

       Host that will be resolved.


.. class:: TraceDnsResolveHostEndParams

   See :attr:`TraceConfig.on_dns_resolvehost_end` for details.

   .. attribute:: host

       Host that has been resolved.


.. class:: TraceDnsCacheHitParams

   See :attr:`TraceConfig.on_dns_cache_hit` for details.

   .. attribute:: host

       Host found in the cache.


.. class:: TraceDnsCacheMissParams

   See :attr:`TraceConfig.on_dns_cache_miss` for details.

   .. attribute:: host

       Host didn't find the cache.


.. class:: TraceRequestHeadersSentParams

   See :attr:`TraceConfig.on_request_headers_sent` for details.

   .. versionadded:: 3.8

   .. attribute:: method

       Method that will be used to make the request.

   .. attribute:: url

       URL that will be used for the request.

   .. attribute:: headers

       Headers that will be used for the request.
````

## File: docs/utilities.rst
````
.. currentmodule:: aiohttp

.. _aiohttp-utilities:

Utilities
=========

Miscellaneous API Shared between Client And Server.

.. toctree::
   :name: utilities
   :maxdepth: 2

   abc
   multipart
   multipart_reference
   streams
   structures
   websocket_utilities
````

## File: docs/web_advanced.rst
````
.. currentmodule:: aiohttp.web

.. _aiohttp-web-advanced:

Web Server Advanced
===================

Unicode support
---------------

*aiohttp* does :term:`requoting` of incoming request path.

Unicode (non-ASCII) symbols are processed transparently on both *route
adding* and *resolving* (internally everything is converted to
:term:`percent-encoding` form by :term:`yarl` library).

But in case of custom regular expressions for
:ref:`aiohttp-web-variable-handler` please take care that URL is
*percent encoded*: if you pass Unicode patterns they don't match to
*requoted* path.

.. _aiohttp-web-peer-disconnection:

Peer disconnection
------------------

*aiohttp* has 2 approaches to handling client disconnections.
If you are familiar with asyncio, or scalability is a concern for
your application, we recommend using the handler cancellation method.

Raise on read/write (default)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a client peer is gone, a subsequent reading or writing raises :exc:`OSError`
or a more specific exception like :exc:`ConnectionResetError`.

This behavior is similar to classic WSGI frameworks like Flask and Django.

The reason for disconnection varies; it can be a network issue or explicit
socket closing on the peer side without reading the full server response.

*aiohttp* handles disconnection properly but you can handle it explicitly, e.g.::

   async def handler(request):
       try:
           text = await request.text()
       except OSError:
           # disconnected

.. _web-handler-cancellation:

Web handler cancellation
^^^^^^^^^^^^^^^^^^^^^^^^

This method can be enabled using the ``handler_cancellation`` parameter
to :func:`run_app`.

When a client disconnects, the web handler task will be cancelled. This
is recommended as it can reduce the load on your server when there is no
client to receive a response. It can also help make your application
more resilient to DoS attacks (by requiring an attacker to keep a
connection open in order to waste server resources).

This behavior is very different from classic WSGI frameworks like
Flask and Django. It requires a reasonable level of asyncio knowledge to
use correctly without causing issues in your code. We provide some
examples here to help understand the complexity and methods
needed to deal with them.

.. warning::

   :term:`web-handler` execution could be canceled on every ``await`` or
   ``async with`` if client drops connection without reading entire response's BODY.

Sometimes it is a desirable behavior: on processing ``GET`` request the
code might fetch data from a database or other web resource, the
fetching is potentially slow.

Canceling this fetch is a good idea: the client dropped the connection
already, so there is no reason to waste time and resources (memory etc)
by getting data from a DB without any chance to send it back to the client.

But sometimes the cancellation is bad: on ``POST`` requests very often
it is needed to save data to a DB regardless of connection closing.

Cancellation prevention could be implemented in several ways:

* Applying :func:`aiojobs.aiohttp.shield` to a coroutine that saves data.
* Using aiojobs_ or another third party library to run a task in the background.

:func:`aiojobs.aiohttp.shield` can work well. The only disadvantage is you
need to split the web handler into two async functions: one for the handler
itself and another for protected code.

.. warning::

   We don't recommend using :func:`asyncio.shield` for this because the shielded
   task cannot be tracked by the application and therefore there is a risk that
   the task will get cancelled during application shutdown. The function provided
   by aiojobs_ operates in the same way except the inner task will be tracked
   by the Scheduler and will get waited on during the cleanup phase.

For example the following snippet is not safe::

   from aiojobs.aiohttp import shield

   async def handler(request):
       await shield(request, write_to_redis(request))
       await shield(request, write_to_postgres(request))
       return web.Response(text="OK")

Cancellation might occur while saving data in REDIS, so the
``write_to_postgres`` function will not be called, potentially
leaving your data in an inconsistent state.

Instead, you would need to write something like::

   async def write_data(request):
       await write_to_redis(request)
       await write_to_postgres(request)

   async def handler(request):
       await shield(request, write_data(request))
       return web.Response(text="OK")

Alternatively, if you want to spawn a task without waiting for
its completion, you can use aiojobs_ which provides an API for
spawning new background jobs. It stores all scheduled activity in
internal data structures and can terminate them gracefully::

   from aiojobs.aiohttp import setup, spawn

   async def handler(request):
       await spawn(request, write_data())
       return web.Response()

   app = web.Application()
   setup(app)
   app.router.add_get("/", handler)

.. warning::

   Don't use :func:`asyncio.create_task` for this. All tasks
   should be awaited at some point in your code (``aiojobs`` handles
   this for you), otherwise you will hide legitimate exceptions
   and result in warnings being emitted.

   A good case for using :func:`asyncio.create_task` is when
   you want to run something while you are processing other data,
   but still want to ensure the task is complete before returning::

       async def handler(request):
           t = asyncio.create_task(get_some_data())
           ...  # Do some other things, while data is being fetched.
           data = await t
           return web.Response(text=data)

One more approach would be to use :func:`aiojobs.aiohttp.atomic`
decorator to execute the entire handler as a new job. Essentially
restoring the default disconnection behavior only for specific handlers::

   from aiojobs.aiohttp import atomic

   @atomic
   async def handler(request):
       await write_to_db()
       return web.Response()

   app = web.Application()
   setup(app)
   app.router.add_post("/", handler)

It prevents all of the ``handler`` async function from cancellation,
so ``write_to_db`` will never be interrupted.

.. _aiojobs: http://aiojobs.readthedocs.io/en/latest/

Passing a coroutine into run_app and Gunicorn
---------------------------------------------

:func:`run_app` accepts either application instance or a coroutine for
making an application. The coroutine based approach allows to perform
async IO before making an app::

   async def app_factory():
       await pre_init()
       app = web.Application()
       app.router.add_get(...)
       return app

   web.run_app(app_factory())

Gunicorn worker supports a factory as well. For Gunicorn the factory
should accept zero parameters::

   async def my_web_app():
       app = web.Application()
       app.router.add_get(...)
       return app

Start gunicorn:

.. code-block:: shell

   $ gunicorn my_app_module:my_web_app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker

.. versionadded:: 3.1

Custom Routing Criteria
-----------------------

Sometimes you need to register :ref:`handlers <aiohttp-web-handler>` on
more complex criteria than simply a *HTTP method* and *path* pair.

Although :class:`UrlDispatcher` does not support any extra criteria, routing
based on custom conditions can be accomplished by implementing a second layer
of routing in your application.

The following example shows custom routing based on the *HTTP Accept* header::

   class AcceptChooser:

       def __init__(self):
           self._accepts = {}

       async def do_route(self, request):
           for accept in request.headers.getall('ACCEPT', []):
               acceptor = self._accepts.get(accept)
               if acceptor is not None:
                   return (await acceptor(request))
           raise HTTPNotAcceptable()

       def reg_acceptor(self, accept, handler):
           self._accepts[accept] = handler


   async def handle_json(request):
       # do json handling

   async def handle_xml(request):
       # do xml handling

   chooser = AcceptChooser()
   app.add_routes([web.get('/', chooser.do_route)])

   chooser.reg_acceptor('application/json', handle_json)
   chooser.reg_acceptor('application/xml', handle_xml)

.. _aiohttp-web-static-file-handling:

Static file handling
--------------------

The best way to handle static files (images, JavaScripts, CSS files
etc.) is using `Reverse Proxy`_ like `nginx`_ or `CDN`_ services.

.. _Reverse Proxy: https://en.wikipedia.org/wiki/Reverse_proxy
.. _nginx: https://nginx.org/
.. _CDN: https://en.wikipedia.org/wiki/Content_delivery_network

But for development it's very convenient to handle static files by
aiohttp server itself.

To do it just register a new static route by
:meth:`RouteTableDef.static` or :func:`static` calls::

   app.add_routes([web.static('/prefix', path_to_static_folder)])

   routes.static('/prefix', path_to_static_folder)

When a directory is accessed within a static route then the server responses
to client with ``HTTP/403 Forbidden`` by default. Displaying folder index
instead could be enabled with ``show_index`` parameter set to ``True``::

   web.static('/prefix', path_to_static_folder, show_index=True)

When a symlink that leads outside the static directory is accessed, the server
responds to the client with ``HTTP/404 Not Found`` by default. To allow the server to
follow symlinks that lead outside the static root, the parameter ``follow_symlinks``
should be set to ``True``::

   web.static('/prefix', path_to_static_folder, follow_symlinks=True)

.. caution::

   Enabling ``follow_symlinks`` can be a security risk, and may lead to
   a directory transversal attack. You do NOT need this option to follow symlinks
   which point to somewhere else within the static directory, this option is only
   used to break out of the security sandbox. Enabling this option is highly
   discouraged, and only expected to be used for edge cases in a local
   development setting where remote users do not have access to the server.

When you want to enable cache busting,
parameter ``append_version`` can be set to ``True``

Cache busting is the process of appending some form of file version hash
to the filename of resources like JavaScript and CSS files.
The performance advantage of doing this is that we can tell the browser
to cache these files indefinitely without worrying about the client not getting
the latest version when the file changes::

   web.static('/prefix', path_to_static_folder, append_version=True)

Template Rendering
------------------

:mod:`aiohttp.web` does not support template rendering out-of-the-box.

However, there is a third-party library, :mod:`aiohttp_jinja2`, which is
supported by the *aiohttp* authors.

Using it is rather simple. First, setup a *jinja2 environment* with a call
to :func:`aiohttp_jinja2.setup`::

    app = web.Application()
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader('/path/to/templates/folder'))

After that you may use the template engine in your
:ref:`handlers <aiohttp-web-handler>`. The most convenient way is to simply
wrap your handlers with the  :func:`aiohttp_jinja2.template` decorator::

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def handler(request):
        return {'name': 'Andrew', 'surname': 'Svetlov'}

If you prefer the `Mako`_ template engine, please take a look at the
`aiohttp_mako`_ library.

.. warning::

   :func:`aiohttp_jinja2.template` should be applied **before**
   :meth:`RouteTableDef.get` decorator and family, e.g. it must be
   the *first* (most *down* decorator in the chain)::


      @routes.get('/path')
      @aiohttp_jinja2.template('tmpl.jinja2')
      async def handler(request):
          return {'name': 'Andrew', 'surname': 'Svetlov'}


.. _Mako: http://www.makotemplates.org/

.. _aiohttp_mako: https://github.com/aio-libs/aiohttp_mako


.. _aiohttp-web-websocket-read-same-task:

Reading from the same task in WebSockets
----------------------------------------

Reading from the *WebSocket* (``await ws.receive()``) **must only** be
done inside the request handler *task*; however, writing
(``ws.send_str(...)``) to the *WebSocket*, closing (``await
ws.close()``) and canceling the handler task may be delegated to other
tasks. See also :ref:`FAQ section
<aiohttp_faq_terminating_websockets>`.

:mod:`aiohttp.web` creates an implicit :class:`asyncio.Task` for
handling every incoming request.

.. note::

   While :mod:`aiohttp.web` itself only supports *WebSockets* without
   downgrading to *LONG-POLLING*, etc., our team supports SockJS_, an
   aiohttp-based library for implementing SockJS-compatible server
   code.

.. _SockJS: https://github.com/aio-libs/sockjs


.. warning::

   Parallel reads from websocket are forbidden, there is no
   possibility to call :meth:`WebSocketResponse.receive`
   from two tasks.

   See :ref:`FAQ section <aiohttp_faq_parallel_event_sources>` for
   instructions how to solve the problem.


.. _aiohttp-web-data-sharing:

Data Sharing aka No Singletons Please
-------------------------------------

:mod:`aiohttp.web` discourages the use of *global variables*, aka *singletons*.
Every variable should have its own context that is *not global*.

Global variables are generally considered bad practice due to the complexity
they add in keeping track of state changes to variables.

*aiohttp* does not use globals by design, which will reduce the number of bugs
and/or unexpected behaviors for its users. For example, an i18n translated string
being written for one request and then being served to another.

So, :class:`Application` and :class:`Request`
support a :class:`collections.abc.MutableMapping` interface (i.e. they are
dict-like objects), allowing them to be used as data stores.


.. _aiohttp-web-data-sharing-app-config:

Application's config
^^^^^^^^^^^^^^^^^^^^

For storing *global-like* variables, feel free to save them in an
:class:`Application` instance::

    app['my_private_key'] = data

and get it back in the :term:`web-handler`::

    async def handler(request):
        data = request.app['my_private_key']

Rather than using :class:`str` keys, we recommend using :class:`AppKey`.
This is required for type safety (e.g. when checking with mypy)::

    my_private_key = web.AppKey("my_private_key", str)
    app[my_private_key] = data

    async def handler(request: web.Request):
        data = request.app[my_private_key]
        # reveal_type(data) -> str

In case of :ref:`nested applications
<aiohttp-web-nested-applications>` the desired lookup strategy could
be the following:

1. Search the key in the current nested application.
2. If the key is not found continue searching in the parent application(s).

For this please use :attr:`Request.config_dict` read-only property::

    async def handler(request):
        data = request.config_dict[my_private_key]

The app object can be used in this way to reuse a database connection or anything
else needed throughout the application.

See this reference section for more detail: :ref:`aiohttp-web-app-and-router`.

Request's storage
^^^^^^^^^^^^^^^^^

Variables that are only needed for the lifetime of a :class:`Request`, can be
stored in a :class:`Request`::

    async def handler(request):
      request['my_private_key'] = "data"
      ...

This is mostly useful for :ref:`aiohttp-web-middlewares` and
:ref:`aiohttp-web-signals` handlers to store data for further processing by the
next handlers in the chain.

Response's storage
^^^^^^^^^^^^^^^^^^

:class:`StreamResponse` and :class:`Response` objects
also support :class:`collections.abc.MutableMapping` interface. This is useful
when you want to share data with signals and middlewares once all the work in
the handler is done::

    async def handler(request):
      [ do all the work ]
      response['my_metric'] = 123
      return response


Naming hint
^^^^^^^^^^^

To avoid clashing with other *aiohttp* users and third-party libraries, please
choose a unique key name for storing data.

If your code is published on PyPI, then the project name is most likely unique
and safe to use as the key.
Otherwise, something based on your company name/url would be satisfactory (i.e.
``org.company.app``).


.. _aiohttp-web-contextvars:


ContextVars support
-------------------

Asyncio has :mod:`Context Variables <contextvars>` as a context-local storage
(a generalization of thread-local concept that works with asyncio tasks also).


*aiohttp* server supports it in the following way:

* A server inherits the current task's context used when creating it.
  :func:`aiohttp.web.run_app()` runs a task for handling all underlying jobs running
  the app, but alternatively :ref:`aiohttp-web-app-runners` can be used.

* Application initialization / finalization events (:attr:`Application.cleanup_ctx`,
  :attr:`Application.on_startup` and :attr:`Application.on_shutdown`,
  :attr:`Application.on_cleanup`) are executed inside the same context.

  E.g. all context modifications made on application startup are visible on teardown.

* On every request handling *aiohttp* creates a context copy. :term:`web-handler` has
  all variables installed on initialization stage. But the context modification made by
  a handler or middleware is invisible to another HTTP request handling call.

An example of context vars usage::

    from contextvars import ContextVar

    from aiohttp import web

    VAR = ContextVar('VAR', default='default')


    async def coro():
        return VAR.get()


    async def handler(request):
        var = VAR.get()
        VAR.set('handler')
        ret = await coro()
        return web.Response(text='\n'.join([var,
                                            ret]))


    async def on_startup(app):
        print('on_startup', VAR.get())
        VAR.set('on_startup')


    async def on_cleanup(app):
        print('on_cleanup', VAR.get())
        VAR.set('on_cleanup')


    async def init():
        print('init', VAR.get())
        VAR.set('init')
        app = web.Application()
        app.router.add_get('/', handler)

        app.on_startup.append(on_startup)
        app.on_cleanup.append(on_cleanup)
        return app


    web.run_app(init())
    print('done', VAR.get())

.. versionadded:: 3.5


.. _aiohttp-web-middlewares:

Middlewares
-----------

:mod:`aiohttp.web` provides a powerful mechanism for customizing
:ref:`request handlers<aiohttp-web-handler>` via *middlewares*.

A *middleware* is a coroutine that can modify either the request or
response. For example, here's a simple *middleware* which appends
``' wink'`` to the response::

    from aiohttp import web
    from typing import Callable, Awaitable

    async def middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]]
    ) -> web.StreamResponse:
        resp = await handler(request)
        resp.text = resp.text + ' wink'
        return resp

.. warning::

   As of version ``4.0.0`` "new-style" middleware is default and the
   ``@middleware`` decorator is not required (and is deprecated), you can
   simply remove the decorator. "Old-style" middleware (a coroutine which
   returned a coroutine) is no longer supported.

.. note::

   The example won't work with streamed responses or websockets

Every *middleware* should accept two parameters, a :class:`request
<Request>` instance and a *handler*, and return the response or raise
an exception. If the exception is not an instance of
:exc:`HTTPException` it is converted to ``500``
:exc:`HTTPInternalServerError` after processing the
middlewares chain.

.. warning::

   Second argument should be named *handler* exactly.

When creating an :class:`Application`, these *middlewares* are passed to
the keyword-only ``middlewares`` parameter::

   app = web.Application(middlewares=[middleware_1,
                                      middleware_2])

Internally, a single :ref:`request handler <aiohttp-web-handler>` is constructed
by applying the middleware chain to the original handler in reverse order,
and is called by the :class:`~aiohttp.web.RequestHandler` as a regular *handler*.

Since *middlewares* are themselves coroutines, they may perform extra
``await`` calls when creating a new handler, e.g. call database etc.

*Middlewares* usually call the handler, but they may choose to ignore it,
e.g. displaying *403 Forbidden page* or raising :exc:`HTTPForbidden` exception
if the user does not have permissions to access the underlying resource.
They may also render errors raised by the handler, perform some pre- or
post-processing like handling *CORS* and so on.

The following code demonstrates middlewares execution order::

   from aiohttp import web
   from typing import Callable, Awaitable

   async def test(request: web.Request) -> web.Response:
       print('Handler function called')
       return web.Response(text="Hello")

   async def middleware1(
       request: web.Request,
       handler: Callable[[web.Request], Awaitable[web.StreamResponse]]
   ) -> web.StreamResponse:
       print('Middleware 1 called')
       response = await handler(request)
       print('Middleware 1 finished')
       return response

   async def middleware2(
       request: web.Request,
       handler: Callable[[web.Request], Awaitable[web.StreamResponse]]
   ) -> web.StreamResponse:
       print('Middleware 2 called')
       response = await handler(request)
       print('Middleware 2 finished')
       return response


   app = web.Application(middlewares=[middleware1, middleware2])
   app.router.add_get('/', test)
   web.run_app(app)

Produced output::

   Middleware 1 called
   Middleware 2 called
   Handler function called
   Middleware 2 finished
   Middleware 1 finished

Request Body Stream Consumption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

   When middleware reads the request body (using :meth:`~aiohttp.web.BaseRequest.read`,
   :meth:`~aiohttp.web.BaseRequest.text`, :meth:`~aiohttp.web.BaseRequest.json`, or
   :meth:`~aiohttp.web.BaseRequest.post`), the body stream is consumed. However, these
   high-level methods cache their result, so subsequent calls from the handler or other
   middleware will return the same cached value.

   The important distinction is:

   - High-level methods (:meth:`~aiohttp.web.BaseRequest.read`, :meth:`~aiohttp.web.BaseRequest.text`,
     :meth:`~aiohttp.web.BaseRequest.json`, :meth:`~aiohttp.web.BaseRequest.post`) cache their
     results internally, so they can be called multiple times and will return the same value.
   - Direct stream access via :attr:`~aiohttp.web.BaseRequest.content` does NOT have this
     caching behavior. Once you read from ``request.content`` directly (e.g., using
     ``await request.content.read()``), subsequent reads will return empty bytes.

Consider this middleware that logs request bodies::

    from aiohttp import web
    from typing import Callable, Awaitable

    async def logging_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]]
    ) -> web.StreamResponse:
        # This consumes the request body stream
        body = await request.text()
        print(f"Request body: {body}")
        return await handler(request)

    async def handler(request: web.Request) -> web.Response:
        # This will return the same value that was read in the middleware
        # (i.e., the cached result, not an empty string)
        body = await request.text()
        return web.Response(text=f"Received: {body}")

In contrast, when accessing the stream directly (not recommended in middleware)::

    async def stream_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]]
    ) -> web.StreamResponse:
        # Reading directly from the stream - this consumes it!
        data = await request.content.read()
        print(f"Stream data: {data}")
        return await handler(request)

    async def handler(request: web.Request) -> web.Response:
        # This will return empty bytes because the stream was already consumed
        data = await request.content.read()
        # data will be b'' (empty bytes)

        # However, high-level methods would still work if called for the first time:
        # body = await request.text()  # This would read from internal cache if available
        return web.Response(text=f"Received: {data}")

When working with raw stream data that needs to be shared between middleware and handlers::

    async def stream_parsing_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]]
    ) -> web.StreamResponse:
        # Read stream once and store the data
        raw_data = await request.content.read()
        request['raw_body'] = raw_data
        return await handler(request)

    async def handler(request: web.Request) -> web.Response:
        # Access the stored data instead of reading the stream again
        raw_data = request.get('raw_body', b'')
        return web.Response(body=raw_data)

Example
^^^^^^^

A common use of middlewares is to implement custom error pages.  The following
example will render 404 errors using a JSON response, as might be appropriate
a JSON REST service::

    from aiohttp import web

    async def error_middleware(request, handler):
        try:
            response = await handler(request)
            if response.status != 404:
                return response
            message = response.message
        except web.HTTPException as ex:
            if ex.status != 404:
                raise
            message = ex.reason
        return web.json_response({'error': message})

    app = web.Application(middlewares=[error_middleware])


Middleware Factory
^^^^^^^^^^^^^^^^^^

A *middleware factory* is a function that creates a middleware with passed
arguments. For example, here's a trivial *middleware factory*::

    def middleware_factory(text):
        async def sample_middleware(request, handler):
            resp = await handler(request)
            resp.text = resp.text + text
            return resp
        return sample_middleware

Note that in contrast to regular middlewares, a middleware factory should
return the function, not the value. So when passing a middleware factory
to the app you actually need to call it::

    app = web.Application(middlewares=[middleware_factory(' wink')])

.. _aiohttp-web-signals:

Signals
-------

Although :ref:`middlewares <aiohttp-web-middlewares>` can customize
:ref:`request handlers<aiohttp-web-handler>` before or after a :class:`Response`
has been prepared, they can't customize a :class:`Response` **while** it's
being prepared. For this :mod:`aiohttp.web` provides *signals*.

For example, a middleware can only change HTTP headers for *unprepared*
responses (see :meth:`StreamResponse.prepare`), but sometimes we
need a hook for changing HTTP headers for streamed responses and WebSockets.
This can be accomplished by subscribing to the
:attr:`Application.on_response_prepare` signal, which is called after default
headers have been computed and directly before headers are sent::

    async def on_prepare(request, response):
        response.headers['My-Header'] = 'value'

    app.on_response_prepare.append(on_prepare)


Additionally, the :attr:`Application.on_startup` and
:attr:`Application.on_cleanup` signals can be subscribed to for
application component setup and tear down accordingly.

The following example will properly initialize and dispose an asyncpg connection
engine::

    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

    pg_engine = web.AppKey("pg_engine", AsyncEngine)

    async def create_pg(app):
        app[pg_engine] = await create_async_engine(
            "postgresql+asyncpg://postgre:@localhost:5432/postgre"
        )

    async def dispose_pg(app):
        await app[pg_engine].dispose()

    app.on_startup.append(create_pg)
    app.on_cleanup.append(dispose_pg)


Signal handlers should not return a value but may modify incoming mutable
parameters.

Signal handlers will be run sequentially, in order they were
added. All handlers must be asynchronous since *aiohttp* 3.0.

.. _aiohttp-web-cleanup-ctx:

Cleanup Context
---------------

Bare :attr:`Application.on_startup` / :attr:`Application.on_cleanup`
pair still has a pitfall: signals handlers are independent on each other.

E.g. we have ``[create_pg, create_redis]`` in *startup* signal and
``[dispose_pg, dispose_redis]`` in *cleanup*.

If, for example, ``create_pg(app)`` call fails ``create_redis(app)``
is not called. But on application cleanup both ``dispose_pg(app)`` and
``dispose_redis(app)`` are still called: *cleanup signal* has no
knowledge about startup/cleanup pairs and their execution state.


The solution is :attr:`Application.cleanup_ctx` usage::

    async def pg_engine(app: web.Application):
        app[pg_engine] = await create_async_engine(
            "postgresql+asyncpg://postgre:@localhost:5432/postgre"
        )
        yield
        await app[pg_engine].dispose()

    app.cleanup_ctx.append(pg_engine)

The attribute is a list of *asynchronous generators*, a code *before*
``yield`` is an initialization stage (called on *startup*), a code
*after* ``yield`` is executed on *cleanup*. The generator must have only
one ``yield``.

*aiohttp* guarantees that *cleanup code* is called if and only if
*startup code* was successfully finished.

.. versionadded:: 3.1

.. _aiohttp-web-nested-applications:

Nested applications
-------------------

Sub applications are designed for solving the problem of the big
monolithic code base.
Let's assume we have a project with own business logic and tools like
administration panel and debug toolbar.

Administration panel is a separate application by its own nature but all
toolbar URLs are served by prefix like ``/admin``.

Thus we'll create a totally separate application named ``admin`` and
connect it to main app with prefix by
:meth:`Application.add_subapp`::

   admin = web.Application()
   # setup admin routes, signals and middlewares

   app.add_subapp('/admin/', admin)

Middlewares and signals from ``app`` and ``admin`` are chained.

It means that if URL is ``'/admin/something'`` middlewares from
``app`` are applied first and ``admin.middlewares`` are the next in
the call chain.

The same is going for
:attr:`Application.on_response_prepare` signal -- the
signal is delivered to both top level ``app`` and ``admin`` if
processing URL is routed to ``admin`` sub-application.

Common signals like :attr:`Application.on_startup`,
:attr:`Application.on_shutdown` and
:attr:`Application.on_cleanup` are delivered to all
registered sub-applications. The passed parameter is sub-application
instance, not top-level application.


Third level sub-applications can be nested into second level ones --
there are no limitation for nesting level.

Url reversing for sub-applications should generate urls with proper prefix.

But for getting URL sub-application's router should be used::

   admin = web.Application()
   admin.add_routes([web.get('/resource', handler, name='name')])

   app.add_subapp('/admin/', admin)

   url = admin.router['name'].url_for()

The generated ``url`` from example will have a value
``URL('/admin/resource')``.

If main application should do URL reversing for sub-application it could
use the following explicit technique::

   admin = web.Application()
   admin_key = web.AppKey('admin_key', web.Application)
   admin.add_routes([web.get('/resource', handler, name='name')])

   app.add_subapp('/admin/', admin)
   app[admin_key] = admin

   async def handler(request: web.Request):  # main application's handler
       admin = request.app[admin_key]
       url = admin.router['name'].url_for()

.. _aiohttp-web-expect-header:

*Expect* Header
---------------

:mod:`aiohttp.web` supports *Expect* header. By default it sends
``HTTP/1.1 100 Continue`` line to client, or raises
:exc:`HTTPExpectationFailed` if header value is not equal to
"100-continue". It is possible to specify custom *Expect* header
handler on per route basis. This handler gets called if *Expect*
header exist in request after receiving all headers and before
processing application's :ref:`aiohttp-web-middlewares` and
route handler. Handler can return *None*, in that case the request
processing continues as usual. If handler returns an instance of class
:class:`StreamResponse`, *request handler* uses it as response. Also
handler can raise a subclass of :exc:`HTTPException`. In this case all
further processing will not happen and client will receive appropriate
http response.

.. note::
    A server that does not understand or is unable to comply with any of the
    expectation values in the Expect field of a request MUST respond with
    appropriate error status. The server MUST respond with a 417
    (Expectation Failed) status if any of the expectations cannot be met or,
    if there are other problems with the request, some other 4xx status.

    http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.20

If all checks pass, the custom handler *must* write a *HTTP/1.1 100 Continue*
status code before returning.

The following example shows how to setup a custom handler for the *Expect*
header::

   async def check_auth(request):
       if request.version != aiohttp.HttpVersion11:
           return

       if request.headers.get('EXPECT') != '100-continue':
           raise HTTPExpectationFailed(text="Unknown Expect: %s" % expect)

       if request.headers.get('AUTHORIZATION') is None:
           raise HTTPForbidden()

       request.transport.write(b"HTTP/1.1 100 Continue\r\n\r\n")

   async def hello(request):
       return web.Response(body=b"Hello, world")

   app = web.Application()
   app.add_routes([web.add_get('/', hello, expect_handler=check_auth)])

.. _aiohttp-web-custom-resource:

Custom resource implementation
------------------------------

To register custom resource use :meth:`~aiohttp.web.UrlDispatcher.register_resource`.
Resource instance must implement `AbstractResource` interface.

.. _aiohttp-web-app-runners:

Application runners
-------------------

:func:`run_app` provides a simple *blocking* API for running an
:class:`Application`.

For starting the application *asynchronously* or serving on multiple
HOST/PORT :class:`AppRunner` exists.

The simple startup code for serving HTTP site on ``'localhost'``, port
``8080`` looks like::

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    while True:
        await asyncio.sleep(3600)  # sleep forever

To stop serving call :meth:`AppRunner.cleanup`::

    await runner.cleanup()

.. versionadded:: 3.0

.. _aiohttp-web-graceful-shutdown:

Graceful shutdown
------------------

Stopping *aiohttp web server* by just closing all connections is not
always satisfactory.

When aiohttp is run with :func:`run_app`, it will attempt a graceful shutdown
by following these steps (if using a :ref:`runner <aiohttp-web-app-runners>`,
then calling :meth:`AppRunner.cleanup` will perform these steps, excluding
step 7).

1. Stop each site listening on sockets, so new connections will be rejected.
2. Close idle keep-alive connections (and set active ones to close upon completion).
3. Call the :attr:`Application.on_shutdown` signal. This should be used to shutdown
   long-lived connections, such as websockets (see below).
4. Wait a short time for running handlers to complete. This allows any pending handlers
   to complete successfully. The timeout can be adjusted with ``shutdown_timeout``
   in :func:`run_app`.
5. Close any remaining connections and cancel their handlers. It will wait on the
   canceling handlers for a short time, again adjustable with ``shutdown_timeout``.
6. Call the :attr:`Application.on_cleanup` signal. This should be used to cleanup any
   resources (such as DB connections). This includes completing the
   :ref:`cleanup contexts<aiohttp-web-cleanup-ctx>` which may be used to ensure
   background tasks are completed successfully (see
   :ref:`handler cancellation<web-handler-cancellation>` or aiojobs_ for examples).
7. Cancel any remaining tasks and wait on them to complete.

Websocket shutdown
^^^^^^^^^^^^^^^^^^

One problem is if the application supports :term:`websockets <websocket>` or
*data streaming* it most likely has open connections at server shutdown time.

The *library* has no knowledge how to close them gracefully but a developer can
help by registering an :attr:`Application.on_shutdown` signal handler.

A developer should keep a list of opened connections
(:class:`Application` is a good candidate).

The following :term:`websocket` snippet shows an example of a websocket handler::

    from aiohttp import web
    import weakref

    app = web.Application()
    websockets = web.AppKey("websockets", weakref.WeakSet)
    app[websockets] = weakref.WeakSet()

    async def websocket_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        request.app[websockets].add(ws)
        try:
            async for msg in ws:
                ...
        finally:
            request.app[websockets].discard(ws)

        return ws

Then the signal handler may look like::

    from aiohttp import WSCloseCode

    async def on_shutdown(app):
        for ws in set(app[websockets]):
            await ws.close(code=WSCloseCode.GOING_AWAY, message="Server shutdown")

    app.on_shutdown.append(on_shutdown)

.. _aiohttp-web-ceil-absolute-timeout:

Ceil of absolute timeout value
------------------------------

*aiohttp* **ceils** internal timeout values if the value is equal or
greater than 5 seconds. The timeout expires at the next integer second
greater than ``current_time + timeout``.

More details about ceiling absolute timeout values is available here
:ref:`aiohttp-client-timeouts`.

The default threshold can be configured at :class:`aiohttp.web.Application`
level using the ``handler_args`` parameter.

.. code-block:: python3

    app = web.Application(handler_args={"timeout_ceil_threshold": 1})

.. _aiohttp-web-background-tasks:

Background tasks
-----------------

Sometimes there's a need to perform some asynchronous operations just
after application start-up.

Even more, in some sophisticated systems there could be a need to run some
background tasks in the event loop along with the application's request
handler. Such as listening to message queue or other network message/event
sources (e.g. ZeroMQ, Redis Pub/Sub, AMQP, etc.) to react to received messages
within the application.

For example the background task could listen to ZeroMQ on
``zmq.SUB`` socket, process and forward retrieved messages to
clients connected via WebSocket that are stored somewhere in the
application (e.g. in the ``application['websockets']`` list).

To run such short and long running background tasks aiohttp provides an
ability to register :attr:`Application.on_startup` signal handler(s) that
will run along with the application's request handler.

For example there's a need to run one quick task and two long running
tasks that will live till the application is alive. The appropriate
background tasks could be registered as an :attr:`Application.on_startup`
signal handler or :attr:`Application.cleanup_ctx` as shown in the example
below::

  async def listen_to_redis(app: web.Application):
      client = redis.from_url("redis://localhost:6379")
      channel = "news"
      async with client.pubsub() as pubsub:
          await pubsub.subscribe(channel)
          while True:
              msg = await pubsub.get_message(ignore_subscribe_messages=True)
              if msg is not None:
                  for ws in app["websockets"]:
                      await ws.send_str("{}: {}".format(channel, msg))


  async def background_tasks(app):
      app[redis_listener] = asyncio.create_task(listen_to_redis(app))

      yield

      app[redis_listener].cancel()
      with contextlib.suppress(asyncio.CancelledError):
          await app[redis_listener]


  app = web.Application()
  redis_listener = web.AppKey("redis_listener", asyncio.Task[None])
  app.cleanup_ctx.append(background_tasks)
  web.run_app(app)


The task ``listen_to_redis`` will run forever.
To shut it down correctly :attr:`Application.on_cleanup` signal handler
may be used to send a cancellation to it.

.. _aiohttp-web-complex-applications:

Complex Applications
^^^^^^^^^^^^^^^^^^^^

Sometimes aiohttp is not the sole part of an application and additional
tasks/processes may need to be run alongside the aiohttp :class:`Application`.

Generally, the best way to achieve this is to use :func:`aiohttp.web.run_app`
as the entry point for the program. Other tasks can then be run via
:attr:`Application.startup` and :attr:`Application.on_cleanup`. By having the
:class:`Application` control the lifecycle of the entire program, the code
will be more robust and ensure that the tasks are started and stopped along
with the application.

For example, running a long-lived task alongside the :class:`Application`
can be done with a :ref:`aiohttp-web-cleanup-ctx` function like::


  async def run_other_task(_app):
      task = asyncio.create_task(other_long_task())

      yield

      task.cancel()
      with suppress(asyncio.CancelledError):
          await task  # Ensure any exceptions etc. are raised.

  app.cleanup_ctx.append(run_other_task)


Or a separate process can be run with something like::


  async def run_process(_app):
      proc = await asyncio.create_subprocess_exec(path)

      yield

      if proc.returncode is None:
          proc.terminate()
      await proc.wait()

  app.cleanup_ctx.append(run_process)


Handling error pages
--------------------

Pages like *404 Not Found* and *500 Internal Error* could be handled
by custom middleware, see :ref:`polls demo <aiohttpdemos:aiohttp-demos-polls-middlewares>`
for example.

.. _aiohttp-web-forwarded-support:

Deploying behind a Proxy
------------------------

As discussed in :ref:`aiohttp-deployment` the preferable way is
deploying *aiohttp* web server behind a *Reverse Proxy Server* like
:term:`nginx` for production usage.

In this way properties like :attr:`BaseRequest.scheme`
:attr:`BaseRequest.host` and :attr:`BaseRequest.remote` are
incorrect.

Real values should be given from proxy server, usually either
``Forwarded`` or old-fashion ``X-Forwarded-For``,
``X-Forwarded-Host``, ``X-Forwarded-Proto`` HTTP headers are used.

*aiohttp* does not take *forwarded* headers into account by default
because it produces *security issue*: HTTP client might add these
headers too, pushing non-trusted data values.

That's why *aiohttp server* should setup *forwarded* headers in custom
middleware in tight conjunction with *reverse proxy configuration*.

For changing :attr:`BaseRequest.scheme` :attr:`BaseRequest.host`
:attr:`BaseRequest.remote` and :attr:`BaseRequest.client_max_size`
the middleware might use :meth:`BaseRequest.clone`.

.. seealso::

   https://github.com/aio-libs/aiohttp-remotes provides secure helpers
   for modifying *scheme*, *host* and *remote* attributes according
   to ``Forwarded`` and ``X-Forwarded-*`` HTTP headers.

CORS support
------------

:mod:`aiohttp.web` itself does not support `Cross-Origin Resource
Sharing <https://en.wikipedia.org/wiki/Cross-origin_resource_sharing>`_, but
there is an aiohttp plugin for it:
`aiohttp-cors <https://github.com/aio-libs/aiohttp-cors>`_.


Debug Toolbar
-------------

`aiohttp-debugtoolbar`_ is a very useful library that provides a
debugging toolbar while you're developing an :mod:`aiohttp.web`
application.

Install it with ``pip``:

.. code-block:: shell

    $ pip install aiohttp_debugtoolbar


Just call :func:`aiohttp_debugtoolbar.setup`::

    import aiohttp_debugtoolbar
    from aiohttp_debugtoolbar import toolbar_middleware_factory

    app = web.Application()
    aiohttp_debugtoolbar.setup(app)

The toolbar is ready to use. Enjoy!!!

.. _aiohttp-debugtoolbar: https://github.com/aio-libs/aiohttp_debugtoolbar


Dev Tools
---------

`aiohttp-devtools`_ provides a couple of tools to simplify development of
:mod:`aiohttp.web` applications.


Install with ``pip``:

.. code-block:: shell

    $ pip install aiohttp-devtools

``adev runserver`` provides a development server with auto-reload,
live-reload, static file serving.

Documentation and a complete tutorial of creating and running an app
locally are available at `aiohttp-devtools`_.

.. _aiohttp-devtools: https://github.com/aio-libs/aiohttp-devtools
````

## File: docs/web_exceptions.rst
````
.. currentmodule:: aiohttp.web

.. _aiohttp-web-exceptions:

Web Server Exceptions
=====================

Overview
--------

:mod:`aiohttp.web` defines a set of exceptions for every *HTTP status code*.

Each exception is a subclass of :exc:`HTTPException` and relates to a single
HTTP status code::

    async def handler(request):
        raise aiohttp.web.HTTPFound('/redirect')

Each exception class has a status code according to :rfc:`2068`:
codes with 100-300 are not really errors; 400s are client errors,
and 500s are server errors.

HTTP Exception hierarchy chart::

   Exception
     HTTPException
       HTTPSuccessful
         * 200 - HTTPOk
         * 201 - HTTPCreated
         * 202 - HTTPAccepted
         * 203 - HTTPNonAuthoritativeInformation
         * 204 - HTTPNoContent
         * 205 - HTTPResetContent
         * 206 - HTTPPartialContent
       HTTPRedirection
         * 304 - HTTPNotModified
         HTTPMove
           * 300 - HTTPMultipleChoices
           * 301 - HTTPMovedPermanently
           * 302 - HTTPFound
           * 303 - HTTPSeeOther
           * 305 - HTTPUseProxy
           * 307 - HTTPTemporaryRedirect
           * 308 - HTTPPermanentRedirect
       HTTPError
         HTTPClientError
           * 400 - HTTPBadRequest
           * 401 - HTTPUnauthorized
           * 402 - HTTPPaymentRequired
           * 403 - HTTPForbidden
           * 404 - HTTPNotFound
           * 405 - HTTPMethodNotAllowed
           * 406 - HTTPNotAcceptable
           * 407 - HTTPProxyAuthenticationRequired
           * 408 - HTTPRequestTimeout
           * 409 - HTTPConflict
           * 410 - HTTPGone
           * 411 - HTTPLengthRequired
           * 412 - HTTPPreconditionFailed
           * 413 - HTTPRequestEntityTooLarge
           * 414 - HTTPRequestURITooLong
           * 415 - HTTPUnsupportedMediaType
           * 416 - HTTPRequestRangeNotSatisfiable
           * 417 - HTTPExpectationFailed
           * 421 - HTTPMisdirectedRequest
           * 422 - HTTPUnprocessableEntity
           * 424 - HTTPFailedDependency
           * 426 - HTTPUpgradeRequired
           * 428 - HTTPPreconditionRequired
           * 429 - HTTPTooManyRequests
           * 431 - HTTPRequestHeaderFieldsTooLarge
           * 451 - HTTPUnavailableForLegalReasons
         HTTPServerError
           * 500 - HTTPInternalServerError
           * 501 - HTTPNotImplemented
           * 502 - HTTPBadGateway
           * 503 - HTTPServiceUnavailable
           * 504 - HTTPGatewayTimeout
           * 505 - HTTPVersionNotSupported
           * 506 - HTTPVariantAlsoNegotiates
           * 507 - HTTPInsufficientStorage
           * 510 - HTTPNotExtended
           * 511 - HTTPNetworkAuthenticationRequired

All HTTP exceptions have the same constructor signature::

    HTTPNotFound(*, headers=None, reason=None,
                 text=None, content_type=None)

If not directly specified, *headers* will be added to the *default
response headers*.

Classes :exc:`HTTPMultipleChoices`, :exc:`HTTPMovedPermanently`,
:exc:`HTTPFound`, :exc:`HTTPSeeOther`, :exc:`HTTPUseProxy`,
:exc:`HTTPTemporaryRedirect` have the following constructor signature::

    HTTPFound(location, *,headers=None, reason=None,
              text=None, content_type=None)

where *location* is value for *Location HTTP header*.

:exc:`HTTPMethodNotAllowed` is constructed by providing the incoming
unsupported method and list of allowed methods::

    HTTPMethodNotAllowed(method, allowed_methods, *,
                         headers=None, reason=None,
                         text=None, content_type=None)

:exc:`HTTPUnavailableForLegalReasons` should be constructed with a ``link``
to yourself (as the entity implementing the blockage), and an explanation for
the block included in ``text``.::

    HTTPUnavailableForLegalReasons(link, *,
                                   headers=None, reason=None,
                                   text=None, content_type=None)

Base HTTP Exception
-------------------

.. exception:: HTTPException(*, headers=None, reason=None, text=None, \
                             content_type=None)

   The base class for HTTP server exceptions. Inherited from :exc:`Exception`.

   :param headers: HTTP headers (:class:`~collections.abc.Mapping`)

   :param str reason: an optional custom HTTP reason. aiohttp uses *default reason
                      string* if not specified.

   :param str text: an optional text used in response body. If not specified *default
                    text* is constructed from status code and reason, e.g. `"404: Not
                    Found"`.

   :param str content_type: an optional Content-Type, `"text/plain"` by default.

   .. attribute:: status

      HTTP status code for the exception, :class:`int`

   .. attribute:: reason

      HTTP status reason for the exception, :class:`str`

   .. attribute:: text

      HTTP status reason for the exception, :class:`str` or ``None``
      for HTTP exceptions without body, e.g. "204 No Content"

   .. attribute:: headers

      HTTP headers for the exception, :class:`multidict.CIMultiDict`

   .. attribute:: cookies

      An instance of :class:`http.cookies.SimpleCookie` for *outgoing* cookies.

      .. versionadded:: 4.0

   .. method:: set_cookie(name, value, *, path='/', expires=None, \
                          domain=None, max_age=None, \
                          secure=None, httponly=None, version=None, \
                          samesite=None)

      Convenient way for setting :attr:`cookies`, allows to specify
      some additional properties like *max_age* in a single call.

      .. versionadded:: 4.0

      :param str name: cookie name

      :param str value: cookie value (will be converted to
                        :class:`str` if value has another type).

      :param expires: expiration date (optional)

      :param str domain: cookie domain (optional)

      :param int max_age: defines the lifetime of the cookie, in
                          seconds.  The delta-seconds value is a
                          decimal non- negative integer.  After
                          delta-seconds seconds elapse, the client
                          should discard the cookie.  A value of zero
                          means the cookie should be discarded
                          immediately.  (optional)

      :param str path: specifies the subset of URLs to
                       which this cookie applies. (optional, ``'/'`` by default)

      :param bool secure: attribute (with no value) directs
                          the user agent to use only (unspecified)
                          secure means to contact the origin server
                          whenever it sends back this cookie.
                          The user agent (possibly under the user's
                          control) may determine what level of
                          security it considers appropriate for
                          "secure" cookies.  The *secure* should be
                          considered security advice from the server
                          to the user agent, indicating that it is in
                          the session's interest to protect the cookie
                          contents. (optional)

      :param bool httponly: ``True`` if the cookie HTTP only (optional)

      :param int version: a decimal integer, identifies to which
                          version of the state management
                          specification the cookie
                          conforms. (Optional, *version=1* by default)

      :param str samesite: Asserts that a cookie must not be sent with
         cross-origin requests, providing some protection
         against cross-site request forgery attacks.
         Generally the value should be one of: ``None``,
         ``Lax`` or ``Strict``. (optional)

      .. warning::

         In HTTP version 1.1, ``expires`` was deprecated and replaced with
         the easier-to-use ``max-age``, but Internet Explorer (IE6, IE7,
         and IE8) **does not** support ``max-age``.

   .. method:: del_cookie(name, *, path='/', domain=None)

      Deletes cookie.

      .. versionadded:: 4.0

      :param str name: cookie name

      :param str domain: optional cookie domain

      :param str path: optional cookie path, ``'/'`` by default


Successful Exceptions
---------------------

HTTP exceptions for status code in range 200-299. They are not *errors* but special
classes reflected in exceptions hierarchy. E.g. ``raise web.HTTPNoContent`` may look
strange a little but the construction is absolutely legal.

.. exception:: HTTPSuccessful

   A base class for the category, a subclass of :exc:`HTTPException`.

.. exception:: HTTPOk

   An exception for *200 OK*, a subclass of :exc:`HTTPSuccessful`.

.. exception:: HTTPCreated

   An exception for *201 Created*, a subclass of :exc:`HTTPSuccessful`.

.. exception:: HTTPAccepted

   An exception for *202 Accepted*, a subclass of :exc:`HTTPSuccessful`.

.. exception:: HTTPNonAuthoritativeInformation

   An exception for *203 Non-Authoritative Information*, a subclass of
   :exc:`HTTPSuccessful`.

.. exception:: HTTPNoContent

   An exception for *204 No Content*, a subclass of :exc:`HTTPSuccessful`.

   Has no HTTP body.

.. exception:: HTTPResetContent

   An exception for *205 Reset Content*, a subclass of :exc:`HTTPSuccessful`.

   Has no HTTP body.

.. exception:: HTTPPartialContent

   An exception for *206 Partial Content*, a subclass of :exc:`HTTPSuccessful`.

Redirections
------------

HTTP exceptions for status code in range 300-399, e.g. ``raise
web.HTTPMovedPermanently(location='/new/path')``.

.. exception:: HTTPRedirection

   A base class for the category, a subclass of :exc:`HTTPException`.

.. exception:: HTTPMove(location, *, headers=None, reason=None, text=None, \
                        content_type=None)

   A base class for redirections with implied *Location* header,
   all redirections except :exc:`HTTPNotModified`.

   :param location: a :class:`yarl.URL` or :class:`str` used for *Location* HTTP
                    header.

   For other arguments see :exc:`HTTPException` constructor.

   .. attribute:: location

      A *Location* HTTP header value, :class:`yarl.URL`.

.. exception:: HTTPMultipleChoices

   An exception for *300 Multiple Choices*, a subclass of :exc:`HTTPMove`.

.. exception:: HTTPMovedPermanently

   An exception for *301 Moved Permanently*, a subclass of :exc:`HTTPMove`.

.. exception:: HTTPFound

   An exception for *302 Found*, a subclass of :exc:`HTTPMove`.

.. exception:: HTTPSeeOther

   An exception for *303 See Other*, a subclass of :exc:`HTTPMove`.

.. exception:: HTTPNotModified

   An exception for *304 Not Modified*, a subclass of :exc:`HTTPRedirection`.

   Has no HTTP body.

.. exception:: HTTPUseProxy

   An exception for *305 Use Proxy*, a subclass of :exc:`HTTPMove`.

.. exception:: HTTPTemporaryRedirect

   An exception for *307 Temporary Redirect*, a subclass of :exc:`HTTPMove`.

.. exception:: HTTPPermanentRedirect

   An exception for *308 Permanent Redirect*, a subclass of :exc:`HTTPMove`.


Client Errors
-------------

HTTP exceptions for status code in range 400-499, e.g. ``raise web.HTTPNotFound()``.

.. exception:: HTTPClientError

   A base class for the category, a subclass of :exc:`HTTPException`.

.. exception:: HTTPBadRequest

   An exception for *400 Bad Request*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPUnauthorized

   An exception for *401 Unauthorized*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPPaymentRequired

   An exception for *402 Payment Required*, a subclass of
   :exc:`HTTPClientError`.

.. exception:: HTTPForbidden

   An exception for *403 Forbidden*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPNotFound

   An exception for *404 Not Found*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPMethodNotAllowed(method, allowed_methods, *, \
                                    headers=None, reason=None, text=None, \
                                    content_type=None)

   An exception for *405 Method Not Allowed*, a subclass of
   :exc:`HTTPClientError`.

   :param str method: requested but not allowed HTTP method.

   :param allowed_methods: an iterable of allowed HTTP methods (:class:`str`),
                           *Allow* HTTP header is constructed from
                           the sequence separated by comma.

   For other arguments see :exc:`HTTPException` constructor.

   .. attribute:: allowed_methods

      A set of allowed HTTP methods.

   .. attribute:: method

      Requested but not allowed HTTP method.

.. exception:: HTTPNotAcceptable

   An exception for *406 Not Acceptable*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPProxyAuthenticationRequired

   An exception for *407 Proxy Authentication Required*, a subclass of
   :exc:`HTTPClientError`.

.. exception:: HTTPRequestTimeout

   An exception for *408 Request Timeout*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPConflict

   An exception for *409 Conflict*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPGone

   An exception for *410 Gone*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPLengthRequired

   An exception for *411 Length Required*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPPreconditionFailed

   An exception for *412 Precondition Failed*, a subclass of
   :exc:`HTTPClientError`.

.. exception:: HTTPRequestEntityTooLarge(max_size, actual_size, **kwargs)

   An exception for *413 Entity Too Large*, a subclass of :exc:`HTTPClientError`.

   :param int max_size: Maximum allowed request body size

   :param int actual_size: Actual received size

   For other acceptable parameters see :exc:`HTTPException` constructor.

.. exception:: HTTPRequestURITooLong

   An exception for *414 URI is too long*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPUnsupportedMediaType

   An exception for *415 Entity body in unsupported format*, a subclass of
   :exc:`HTTPClientError`.

.. exception:: HTTPRequestRangeNotSatisfiable

   An exception for *416 Cannot satisfy request range*, a subclass of
   :exc:`HTTPClientError`.

.. exception:: HTTPExpectationFailed

   An exception for *417 Expect condition could not be satisfied*, a subclass of
   :exc:`HTTPClientError`.

.. exception:: HTTPMisdirectedRequest

   An exception for *421 Misdirected Request*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPUnprocessableEntity

   An exception for *422 Unprocessable Entity*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPFailedDependency

   An exception for *424 Failed Dependency*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPUpgradeRequired

   An exception for *426 Upgrade Required*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPPreconditionRequired

   An exception for *428 Precondition Required*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPTooManyRequests

   An exception for *429 Too Many Requests*, a subclass of :exc:`HTTPClientError`.

.. exception:: HTTPRequestHeaderFieldsTooLarge

   An exception for *431 Requests Header Fields Too Large*, a subclass of
   :exc:`HTTPClientError`.

.. exception:: HTTPUnavailableForLegalReasons(link, *, \
                                              headers=None, \
                                              reason=None, \
                                              text=None, \
                                              content_type=None)


   An exception for *451 Unavailable For Legal Reasons*, a subclass of
   :exc:`HTTPClientError`.

   :param link: A link to yourself (as the entity implementing the blockage),
                :class:`str`, :class:`~yarl.URL` or ``None``.

   For other parameters see :exc:`HTTPException` constructor.
   A reason for the block should be included in ``text``.

   .. attribute:: link

      A :class:`~yarl.URL` link to the entity implementing the blockage or ``None``,
      read-only property.


Server Errors
-------------

HTTP exceptions for status code in range 500-599, e.g. ``raise web.HTTPBadGateway()``.


.. exception:: HTTPServerError

   A base class for the category, a subclass of :exc:`HTTPException`.

.. exception:: HTTPInternalServerError

   An exception for *500 Server got itself in trouble*, a subclass of
   :exc:`HTTPServerError`.

.. exception:: HTTPNotImplemented

   An exception for *501 Server does not support this operation*, a subclass of
   :exc:`HTTPServerError`.

.. exception:: HTTPBadGateway

   An exception for *502 Invalid responses from another server/proxy*, a
   subclass of :exc:`HTTPServerError`.

.. exception:: HTTPServiceUnavailable

   An exception for *503 The server cannot process the request due to a high
   load*, a subclass of :exc:`HTTPServerError`.

.. exception:: HTTPGatewayTimeout

   An exception for *504 The gateway server did not receive a timely response*,
   a subclass of :exc:`HTTPServerError`.

.. exception:: HTTPVersionNotSupported

   An exception for *505 Cannot fulfill request*, a subclass of :exc:`HTTPServerError`.

.. exception:: HTTPVariantAlsoNegotiates

   An exception for *506 Variant Also Negotiates*, a subclass of :exc:`HTTPServerError`.

.. exception:: HTTPInsufficientStorage

   An exception for *507 Insufficient Storage*, a subclass of :exc:`HTTPServerError`.

.. exception:: HTTPNotExtended

   An exception for *510 Not Extended*, a subclass of :exc:`HTTPServerError`.

.. exception:: HTTPNetworkAuthenticationRequired

   An exception for *511 Network Authentication Required*, a subclass of
   :exc:`HTTPServerError`.
````

## File: docs/web_lowlevel.rst
````
.. currentmodule:: aiohttp.web

.. _aiohttp-web-lowlevel:

Low Level Server
================


This topic describes :mod:`aiohttp.web` based *low level* API.

Abstract
--------

Sometimes users don't need high-level concepts introduced in
:ref:`aiohttp-web`: applications, routers, middlewares and signals.

All that may be needed is supporting an asynchronous callable which accepts a
request and returns a response object.

This is done by introducing :class:`aiohttp.web.Server` class which
serves a *protocol factory* role for
:meth:`asyncio.loop.create_server` and bridges data
stream to *web handler* and sends result back.


Low level *web handler* should accept the single :class:`BaseRequest`
parameter and performs one of the following actions:

  1. Return a :class:`Response` with the whole HTTP body stored in memory.

  2. Create a :class:`StreamResponse`, send headers by
     :meth:`StreamResponse.prepare` call, send data chunks by
     :meth:`StreamResponse.write` and return finished response.

  3. Raise :class:`HTTPException` derived exception (see
     :ref:`aiohttp-web-exceptions` section).

     All other exceptions not derived from :class:`HTTPException`
     leads to *500 Internal Server Error* response.

  4. Initiate and process Web-Socket connection by
     :class:`WebSocketResponse` using (see :ref:`aiohttp-web-websockets`).


Run a Basic Low-Level Server
----------------------------

The following code demonstrates very trivial usage example::

   import asyncio
   from aiohttp import web


   async def handler(request):
       return web.Response(text="OK")


   async def main():
       server = web.Server(handler)
       runner = web.ServerRunner(server)
       await runner.setup()
       site = web.TCPSite(runner, 'localhost', 8080)
       await site.start()

       print("======= Serving on http://127.0.0.1:8080/ ======")

       # pause here for very long time by serving HTTP requests and
       # waiting for keyboard interruption
       await asyncio.sleep(100*3600)


   asyncio.run(main())


In the snippet we have ``handler`` which returns a regular
:class:`Response` with ``"OK"`` in BODY.

This *handler* is processed by ``server`` (:class:`Server` which acts
as *protocol factory*).  Network communication is created by
:ref:`runners API <aiohttp-web-app-runners-reference>` to serve
``http://127.0.0.1:8080/``.

The handler should process every request for every *path*, e.g.
``GET``, ``POST``, Web-Socket.

The example is very basic: it always return ``200 OK`` response, real
life code is much more complex usually.
````

## File: docs/web_quickstart.rst
````
.. currentmodule:: aiohttp.web

.. _aiohttp-web-quickstart:

Web Server Quickstart
=====================

Run a Simple Web Server
-----------------------

In order to implement a web server, first create a
:ref:`request handler <aiohttp-web-handler>`.

A request handler must be a :ref:`coroutine <coroutine>` that
accepts a :class:`Request` instance as its only parameter and returns a
:class:`Response` instance::

   from aiohttp import web

   async def hello(request):
       return web.Response(text="Hello, world")

Next, create an :class:`Application` instance and register the
request handler on a particular *HTTP method* and *path*::

   app = web.Application()
   app.add_routes([web.get('/', hello)])

After that, run the application by :func:`run_app` call::

   web.run_app(app)

That's it. Now, head over to ``http://localhost:8080/`` to see the results.

Alternatively if you prefer *route decorators* create a *route table*
and register a :term:`web-handler`::

   routes = web.RouteTableDef()

   @routes.get('/')
   async def hello(request):
       return web.Response(text="Hello, world")

   app = web.Application()
   app.add_routes(routes)
   web.run_app(app)

Both ways essentially do the same work, the difference is only in your
taste: do you prefer *Django style* with famous ``urls.py`` or *Flask*
with shiny route decorators.

*aiohttp* server documentation uses both ways in code snippets to
emphasize their equality, switching from one style to another is very
trivial.

.. note::
   You can get a powerful aiohttp template by running one command.
   To do this, simply use our `boilerplate for quick start with aiohttp
   <https://create-aio-app.readthedocs.io/pages/aiohttp_quick_start.html>`_.


.. seealso::

   :ref:`aiohttp-web-graceful-shutdown` section explains what :func:`run_app`
   does and how to implement complex server initialization/finalization
   from scratch.

   :ref:`aiohttp-web-app-runners` for more handling more complex cases
   like *asynchronous* web application serving and multiple hosts
   support.

.. _aiohttp-web-cli:

Command Line Interface (CLI)
----------------------------
:mod:`aiohttp.web` implements a basic CLI for quickly serving an
:class:`Application` in *development* over TCP/IP:

.. code-block:: shell

    $ python -m aiohttp.web -H localhost -P 8080 package.module:init_func

``package.module:init_func`` should be an importable :term:`callable` that
accepts a list of any non-parsed command-line arguments and returns an
:class:`Application` instance after setting it up::

    def init_func(argv):
        app = web.Application()
        app.router.add_get("/", index_handler)
        return app


.. note::
   For local development we typically recommend using
   `aiohttp-devtools <https://github.com/aio-libs/aiohttp-devtools>`_.

.. _aiohttp-web-handler:

Handler
-------

A request handler must be a :ref:`coroutine<coroutine>` that accepts a
:class:`Request` instance as its only argument and returns a
:class:`StreamResponse` derived (e.g. :class:`Response`) instance::

   async def handler(request):
       return web.Response()

Handlers are setup to handle requests by registering them with the
:meth:`Application.add_routes` on a particular route (*HTTP method* and
*path* pair) using helpers like :func:`get` and
:func:`post`::

   app.add_routes([web.get('/', handler),
                   web.post('/post', post_handler),
                   web.put('/put', put_handler)])

Or use *route decorators*::

    routes = web.RouteTableDef()

    @routes.get('/')
    async def get_handler(request):
        ...

    @routes.post('/post')
    async def post_handler(request):
        ...

    @routes.put('/put')
    async def put_handler(request):
        ...

    app.add_routes(routes)


Wildcard *HTTP method* is also supported by :func:`route` or
:meth:`RouteTableDef.route`, allowing a handler to serve incoming
requests on a *path* having **any** *HTTP method*::

  app.add_routes([web.route('*', '/path', all_handler)])

The *HTTP method* can be queried later in the request handler using the
:attr:`aiohttp.web.BaseRequest.method` property.

By default endpoints added with ``GET`` method will accept
``HEAD`` requests and return the same response headers as they would
for a ``GET`` request. You can also deny ``HEAD`` requests on a route::

   web.get('/', handler, allow_head=False)

Here ``handler`` won't be called on ``HEAD`` request and the server
will respond with ``405: Method Not Allowed``.

.. seealso::

   :ref:`aiohttp-web-peer-disconnection` section explains how handlers
   behave when a client connection drops and ways to optimize handling
   of this.

.. _aiohttp-web-resource-and-route:

Resources and Routes
--------------------

Internally routes are served by :attr:`Application.router`
(:class:`UrlDispatcher` instance).

The *router* is a list of *resources*.

Resource is an entry in *route table* which corresponds to requested URL.

Resource in turn has at least one *route*.

Route corresponds to handling *HTTP method* by calling *web handler*.

Thus when you add a *route* the *resource* object is created under the hood.

The library implementation **merges** all subsequent route additions
for the same path adding the only resource for all HTTP methods.

Consider two examples::

   app.add_routes([web.get('/path1', get_1),
                   web.post('/path1', post_1),
                   web.get('/path2', get_2),
                   web.post('/path2', post_2)]

and::

   app.add_routes([web.get('/path1', get_1),
                   web.get('/path2', get_2),
                   web.post('/path2', post_2),
                   web.post('/path1', post_1)]

First one is *optimized*. You have got the idea.

.. _aiohttp-web-variable-handler:

Variable Resources
^^^^^^^^^^^^^^^^^^

Resource may have *variable path* also. For instance, a resource with
the path ``'/a/{name}/c'`` would match all incoming requests with
paths such as ``'/a/b/c'``, ``'/a/1/c'``, and ``'/a/etc/c'``.

A variable *part* is specified in the form ``{identifier}``, where the
``identifier`` can be used later in a
:ref:`request handler <aiohttp-web-handler>` to access the matched value for
that *part*. This is done by looking up the ``identifier`` in the
:attr:`Request.match_info` mapping::

   @routes.get('/{name}')
   async def variable_handler(request):
       return web.Response(
           text="Hello, {}".format(request.match_info['name']))

By default, each *part* matches the regular expression ``[^{}/]+``.

You can also specify a custom regex in the form ``{identifier:regex}``::

   web.get(r'/{name:\d+}', handler)


.. _aiohttp-web-named-routes:

Reverse URL Constructing using Named Resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Routes can also be given a *name*::

   @routes.get('/root', name='root')
   async def handler(request):
       ...

Which can then be used to access and build a *URL* for that resource later (e.g.
in a :ref:`request handler <aiohttp-web-handler>`)::

   url = request.app.router['root'].url_for().with_query({"a": "b", "c": "d"})
   assert url == URL('/root?a=b&c=d')

A more interesting example is building *URLs* for :ref:`variable
resources <aiohttp-web-variable-handler>`::

   app.router.add_resource(r'/{user}/info', name='user-info')


In this case you can also pass in the *parts* of the route::

   url = request.app.router['user-info'].url_for(user='john_doe')
   url_with_qs = url.with_query("a=b")
   assert url_with_qs == '/john_doe/info?a=b'


Organizing Handlers in Classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As discussed above, :ref:`handlers <aiohttp-web-handler>` can be first-class
coroutines::

   async def hello(request):
       return web.Response(text="Hello, world")

   app.router.add_get('/', hello)

But sometimes it's convenient to group logically similar handlers into a Python
*class*.

Since :mod:`aiohttp.web` does not dictate any implementation details,
application developers can organize handlers in classes if they so wish::

   class Handler:

       def __init__(self):
           pass

       async def handle_intro(self, request):
           return web.Response(text="Hello, world")

       async def handle_greeting(self, request):
           name = request.match_info.get('name', "Anonymous")
           txt = "Hello, {}".format(name)
           return web.Response(text=txt)

   handler = Handler()
   app.add_routes([web.get('/intro', handler.handle_intro),
                   web.get('/greet/{name}', handler.handle_greeting)])


.. _aiohttp-web-class-based-views:

Class Based Views
^^^^^^^^^^^^^^^^^

:mod:`aiohttp.web` has support for *class based views*.

You can derive from :class:`View` and define methods for handling http
requests::

   class MyView(web.View):
       async def get(self):
           return await get_resp(self.request)

       async def post(self):
           return await post_resp(self.request)

Handlers should be coroutines accepting *self* only and returning
response object as regular :term:`web-handler`. Request object can be
retrieved by :attr:`View.request` property.

After implementing the view (``MyView`` from example above) should be
registered in application's router::

   app.add_routes([web.view('/path/to', MyView)])

or::

   @routes.view('/path/to')
   class MyView(web.View):
       ...

or::

   app.router.add_route('*', '/path/to', MyView)

Example will process GET and POST requests for */path/to* but raise
*405 Method not allowed* exception for unimplemented HTTP methods.

Resource Views
^^^^^^^^^^^^^^

*All* registered resources in a router can be viewed using the
:meth:`UrlDispatcher.resources` method::

   for resource in app.router.resources():
       print(resource)

A *subset* of the resources that were registered with a *name* can be
viewed using the :meth:`UrlDispatcher.named_resources` method::

   for name, resource in app.router.named_resources().items():
       print(name, resource)


.. _aiohttp-web-alternative-routes-definition:

Alternative ways for registering routes
---------------------------------------

Code examples shown above use *imperative* style for adding new
routes: they call ``app.router.add_get(...)`` etc.

There are two alternatives: route tables and route decorators.

Route tables look like Django way::

   async def handle_get(request):
       ...


   async def handle_post(request):
       ...

   app.router.add_routes([web.get('/get', handle_get),
                          web.post('/post', handle_post),


The snippet calls :meth:`~aiohttp.web.UrlDispatcher.add_routes` to
register a list of *route definitions* (:class:`aiohttp.web.RouteDef`
instances) created by :func:`aiohttp.web.get` or
:func:`aiohttp.web.post` functions.

.. seealso:: :ref:`aiohttp-web-route-def` reference.

Route decorators are closer to Flask approach::

   routes = web.RouteTableDef()

   @routes.get('/get')
   async def handle_get(request):
       ...


   @routes.post('/post')
   async def handle_post(request):
       ...

   app.router.add_routes(routes)

It is also possible to use decorators with class-based views::

   routes = web.RouteTableDef()

   @routes.view("/view")
   class MyView(web.View):
       async def get(self):
           ...

       async def post(self):
           ...

   app.router.add_routes(routes)

The example creates a :class:`aiohttp.web.RouteTableDef` container first.

The container is a list-like object with additional decorators
:meth:`aiohttp.web.RouteTableDef.get`,
:meth:`aiohttp.web.RouteTableDef.post` etc. for registering new
routes.

After filling the container
:meth:`~aiohttp.web.UrlDispatcher.add_routes` is used for adding
registered *route definitions* into application's router.

.. seealso:: :ref:`aiohttp-web-route-table-def` reference.

All tree ways (imperative calls, route tables and decorators) are
equivalent, you could use what do you prefer or even mix them on your
own.

.. versionadded:: 2.3


JSON Response
-------------

It is a common case to return JSON data in response, :mod:`aiohttp.web`
provides a shortcut for returning JSON -- :func:`aiohttp.web.json_response`::

   async def handler(request):
       data = {'some': 'data'}
       return web.json_response(data)

The shortcut method returns :class:`aiohttp.web.Response` instance
so you can for example set cookies before returning it from handler.


User Sessions
-------------

Often you need a container for storing user data across requests. The concept
is usually called a *session*.

:mod:`aiohttp.web` has no built-in concept of a *session*, however, there is a
third-party library, :mod:`aiohttp_session`, that adds *session* support::

    import asyncio
    import time
    import base64
    from cryptography import fernet
    from aiohttp import web
    from aiohttp_session import setup, get_session, session_middleware
    from aiohttp_session.cookie_storage import EncryptedCookieStorage

    async def handler(request):
        session = await get_session(request)

        last_visit = session.get("last_visit")
        session["last_visit"] = time.time()
        text = "Last visited: {}".format(last_visit)

        return web.Response(text=text)

    async def make_app():
        app = web.Application()
        # secret_key must be 32 url-safe base64-encoded bytes
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(app, EncryptedCookieStorage(secret_key))
        app.add_routes([web.get('/', handler)])
        return app

    web.run_app(make_app())


.. _aiohttp-web-forms:

HTTP Forms
----------

HTTP Forms are supported out of the box.

If form's method is ``"GET"`` (``<form method="get">``) use
:attr:`aiohttp.web.BaseRequest.query` for getting form data.

To access form data with ``"POST"`` method use
:meth:`aiohttp.web.BaseRequest.post` or :meth:`aiohttp.web.BaseRequest.multipart`.

:meth:`aiohttp.web.BaseRequest.post` accepts both
``'application/x-www-form-urlencoded'`` and ``'multipart/form-data'``
form's data encoding (e.g. ``<form enctype="multipart/form-data">``).
It stores files data in temporary directory. If `client_max_size` is
specified `post` raises `ValueError` exception.
For efficiency use :meth:`aiohttp.web.BaseRequest.multipart`, It is especially effective
for uploading large files (:ref:`aiohttp-web-file-upload`).

Values submitted by the following form:

.. code-block:: html

   <form action="/login" method="post" accept-charset="utf-8"
         enctype="application/x-www-form-urlencoded">

       <label for="login">Login</label>
       <input id="login" name="login" type="text" value="" autofocus/>
       <label for="password">Password</label>
       <input id="password" name="password" type="password" value=""/>

       <input type="submit" value="login"/>
   </form>

could be accessed as::

    async def do_login(request):
        data = await request.post()
        login = data['login']
        password = data['password']


.. _aiohttp-web-file-upload:

File Uploads
------------

:mod:`aiohttp.web` has built-in support for handling files uploaded from the
browser.

First, make sure that the HTML ``<form>`` element has its *enctype* attribute
set to ``enctype="multipart/form-data"``. As an example, here is a form that
accepts an MP3 file:

.. code-block:: html

   <form action="/store/mp3" method="post" accept-charset="utf-8"
         enctype="multipart/form-data">

       <label for="mp3">Mp3</label>
       <input id="mp3" name="mp3" type="file" value=""/>

       <input type="submit" value="submit"/>
   </form>

Then, in the :ref:`request handler <aiohttp-web-handler>` you can access the
file input field as a :class:`FileField` instance. :class:`FileField` is simply
a container for the file as well as some of its metadata::

    async def store_mp3_handler(request):

        # WARNING: don't do that if you plan to receive large files!
        data = await request.post()

        mp3 = data['mp3']

        # .filename contains the name of the file in string format.
        filename = mp3.filename

        # .file contains the actual file data that needs to be stored somewhere.
        mp3_file = data['mp3'].file

        content = mp3_file.read()

        return web.Response(body=content,
                            headers=MultiDict(
                                {'CONTENT-DISPOSITION': mp3_file}))


You might have noticed a big warning in the example above. The general issue is
that :meth:`aiohttp.web.BaseRequest.post` reads the whole payload in memory,
resulting in possible
:abbr:`OOM (Out Of Memory)` errors. To avoid this, for multipart uploads, you
should use :meth:`aiohttp.web.BaseRequest.multipart` which returns a :ref:`multipart reader
<aiohttp-multipart>`::

    async def store_mp3_handler(request):

        reader = await request.multipart()

        # /!\ Don't forget to validate your inputs /!\

        # reader.next() will `yield` the fields of your form

        field = await reader.next()
        assert field.name == 'name'
        name = await field.read(decode=True)

        field = await reader.next()
        assert field.name == 'mp3'
        filename = field.filename
        # You cannot rely on Content-Length if transfer is chunked.
        size = 0
        with open(os.path.join('/spool/yarrr-media/mp3/', filename), 'wb') as f:
            while True:
                chunk = await field.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        return web.Response(text='{} sized of {} successfully stored'
                                 ''.format(filename, size))

.. _aiohttp-web-websockets:

WebSockets
----------

:mod:`aiohttp.web` supports *WebSockets* out-of-the-box.

To setup a *WebSocket*, create a :class:`WebSocketResponse` in a
:ref:`request handler <aiohttp-web-handler>` and then use it to communicate
with the peer::

    async def websocket_handler(request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            # ws.__next__() automatically terminates the loop
            # after ws.close() or ws.exception() is called
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

The handler should be registered as HTTP GET processor::

    app.add_routes([web.get('/ws', websocket_handler)])

.. _aiohttp-web-redirects:

Redirects
---------

To redirect user to another endpoint - raise :class:`HTTPFound` with
an absolute URL, relative URL or view name (the argument from router)::

    raise web.HTTPFound('/redirect')

The following example shows redirect to view named 'login' in routes::

    async def handler(request):
        location = request.app.router['login'].url_for()
        raise web.HTTPFound(location=location)

    router.add_get('/handler', handler)
    router.add_get('/login', login_handler, name='login')

Example with login validation::

    @aiohttp_jinja2.template('login.html')
    async def login(request):

        if request.method == 'POST':
            form = await request.post()
            error = validate_login(form)
            if error:
                return {'error': error}
            else:
                # login form is valid
                location = request.app.router['index'].url_for()
                raise web.HTTPFound(location=location)

        return {}

    app.router.add_get('/', index, name='index')
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
````

## File: docs/web_reference.rst
````
.. currentmodule:: aiohttp.web

.. _aiohttp-web-reference:

Server Reference
================

.. _aiohttp-web-request:


Request and Base Request
------------------------

The Request object contains all the information about an incoming HTTP request.

:class:`BaseRequest` is used for :ref:`Low-Level
Servers<aiohttp-web-lowlevel>` (which have no applications, routers,
signals and middlewares). :class:`Request` has an :attr:`Request.app`
and :attr:`Request.match_info` attributes.

A :class:`BaseRequest` / :class:`Request` are :obj:`dict` like objects,
allowing them to be used for :ref:`sharing
data<aiohttp-web-data-sharing>` among :ref:`aiohttp-web-middlewares`
and :ref:`aiohttp-web-signals` handlers.

.. class:: BaseRequest

   .. attribute:: version

      *HTTP version* of request, Read-only property.

      Returns :class:`aiohttp.protocol.HttpVersion` instance.

   .. attribute:: method

      *HTTP method*, read-only property.

      The value is upper-cased :class:`str` like ``"GET"``,
      ``"POST"``, ``"PUT"`` etc.

   .. attribute:: url

      A :class:`~yarl.URL` instance with absolute URL to resource
      (*scheme*, *host* and *port* are included).

      .. note::

         In case of malformed request (e.g. without ``"HOST"`` HTTP
         header) the absolute url may be unavailable.

   .. attribute:: rel_url

      A :class:`~yarl.URL` instance with relative URL to resource
      (contains *path*, *query* and *fragment* parts only, *scheme*,
      *host* and *port* are excluded).

      The property is equal to ``.url.relative()`` but is always present.

      .. seealso::

         A note from :attr:`url`.

   .. attribute:: scheme

      A string representing the scheme of the request.

      The scheme is ``'https'`` if transport for request handling is
      *SSL*, ``'http'`` otherwise.

      The value could be overridden by :meth:`~BaseRequest.clone`.

      Read-only :class:`str` property.

      .. versionchanged:: 2.3

         *Forwarded* and *X-Forwarded-Proto* are not used anymore.

         Call ``.clone(scheme=new_scheme)`` for setting up the value
         explicitly.

      .. seealso:: :ref:`aiohttp-web-forwarded-support`

   .. attribute:: secure

      Shorthand for ``request.url.scheme == 'https'``

      Read-only :class:`bool` property.

      .. seealso:: :attr:`scheme`

   .. attribute:: forwarded

      A tuple containing all parsed Forwarded header(s).

      Makes an effort to parse Forwarded headers as specified by :rfc:`7239`:

      - It adds one (immutable) dictionary per Forwarded ``field-value``, i.e.
        per proxy. The element corresponds to the data in the Forwarded
        ``field-value`` added by the first proxy encountered by the client.
        Each subsequent item corresponds to those added by later proxies.
      - It checks that every value has valid syntax in general as specified
        in :rfc:`7239#section-4`: either a ``token`` or a ``quoted-string``.
      - It un-escapes ``quoted-pairs``.
      - It does NOT validate 'by' and 'for' contents as specified in
        :rfc:`7239#section-6`.
      - It does NOT validate ``host`` contents (Host ABNF).
      - It does NOT validate ``proto`` contents for valid URI scheme names.

      Returns a tuple containing one or more ``MappingProxy`` objects

      .. seealso:: :attr:`scheme`

      .. seealso:: :attr:`host`

   .. attribute:: host

      Host name of the request, resolved in this order:

      - Overridden value by :meth:`~BaseRequest.clone` call.
      - *Host* HTTP header
      - :func:`socket.getfqdn`

      Read-only :class:`str` property.

      .. versionchanged:: 2.3

         *Forwarded* and *X-Forwarded-Host* are not used anymore.

         Call ``.clone(host=new_host)`` for setting up the value
         explicitly.

      .. seealso:: :ref:`aiohttp-web-forwarded-support`

   .. attribute:: remote

      Originating IP address of a client initiated HTTP request.

      The IP is resolved through the following headers, in this order:

      - Overridden value by :meth:`~BaseRequest.clone` call.
      - Peer name of opened socket.

      Read-only :class:`str` property.

      Call ``.clone(remote=new_remote)`` for setting up the value
      explicitly.

      .. versionadded:: 2.3

      .. seealso:: :ref:`aiohttp-web-forwarded-support`

   .. attribute:: client_max_size

      The maximum size of the request body.

      The value could be overridden by :meth:`~BaseRequest.clone`.

      Read-only :class:`int` property.

   .. attribute:: path_qs

      The URL including PATH_INFO and the query string. e.g.,
      ``/app/blog?id=10``

      Read-only :class:`str` property.

   .. attribute:: path

      The URL including *PATH INFO* without the host or scheme. e.g.,
      ``/app/blog``. The path is URL-decoded. For raw path info see
      :attr:`raw_path`.

      Read-only :class:`str` property.

   .. attribute:: raw_path

      The URL including raw *PATH INFO* without the host or scheme.
      Warning, the path may be URL-encoded and may contain invalid URL
      characters, e.g.
      ``/my%2Fpath%7Cwith%21some%25strange%24characters``.

      For URL-decoded version please take a look on :attr:`path`.

      Read-only :class:`str` property.

   .. attribute:: query

      A multidict with all the variables in the query string.

      Read-only :class:`~multidict.MultiDictProxy` lazy property.

   .. attribute:: query_string

      The query string in the URL, e.g., ``id=10``

      Read-only :class:`str` property.

   .. attribute:: headers

      A case-insensitive multidict proxy with all headers.

      Read-only :class:`~multidict.CIMultiDictProxy` property.

   .. attribute:: raw_headers

      HTTP headers of response as unconverted bytes, a sequence of
      ``(key, value)`` pairs.

   .. attribute:: keep_alive

      ``True`` if keep-alive connection enabled by HTTP client and
      protocol version supports it, otherwise ``False``.

      Read-only :class:`bool` property.

   .. attribute:: transport

      A :ref:`transport<asyncio-transport>` used to process request.
      Read-only property.

      The property can be used, for example, for getting IP address of
      client's peer::

         peername = request.transport.get_extra_info('peername')
         if peername is not None:
             host, port = peername

   .. attribute:: cookies

      A read-only dictionary-like object containing the request's cookies.

      Read-only :class:`~types.MappingProxyType` property.

   .. attribute:: content

      A :class:`~aiohttp.StreamReader` instance,
      input stream for reading request's *BODY*.

      Read-only property.

   .. attribute:: body_exists

      Return ``True`` if request has *HTTP BODY*, ``False`` otherwise.

      Read-only :class:`bool` property.

      .. versionadded:: 2.3

   .. attribute:: can_read_body

      Return ``True`` if request's *HTTP BODY* can be read, ``False`` otherwise.

      Read-only :class:`bool` property.

      .. versionadded:: 2.3

   .. attribute:: content_type

      Read-only property with *content* part of *Content-Type* header.

      Returns :class:`str` like ``'text/html'``

      .. note::

         Returns value is ``'application/octet-stream'`` if no
         Content-Type header present in HTTP headers according to
         :rfc:`2616`

   .. attribute:: charset

      Read-only property that specifies the *encoding* for the request's BODY.

      The value is parsed from the *Content-Type* HTTP header.

      Returns :class:`str` like ``'utf-8'`` or ``None`` if
      *Content-Type* has no charset information.

   .. attribute:: content_length

      Read-only property that returns length of the request's BODY.

      The value is parsed from the *Content-Length* HTTP header.

      Returns :class:`int` or ``None`` if *Content-Length* is absent.

   .. attribute:: http_range

      Read-only property that returns information about *Range* HTTP header.

      Returns a :class:`slice` where ``.start`` is *left inclusive
      bound*, ``.stop`` is *right exclusive bound* and ``.step`` is
      ``1``.

      The property might be used in two manners:

      1. Attribute-access style (example assumes that both left and
         right borders are set, the real logic for case of open bounds
         is more complex)::

            rng = request.http_range
            with open(filename, 'rb') as f:
                f.seek(rng.start)
                return f.read(rng.stop-rng.start)

      2. Slice-style::

            return buffer[request.http_range]

   .. attribute:: if_modified_since

      Read-only property that returns the date specified in the
      *If-Modified-Since* header.

      Returns :class:`datetime.datetime` or ``None`` if
      *If-Modified-Since* header is absent or is not a valid
      HTTP date.

   .. attribute:: if_unmodified_since

      Read-only property that returns the date specified in the
      *If-Unmodified-Since* header.

      Returns :class:`datetime.datetime` or ``None`` if
      *If-Unmodified-Since* header is absent or is not a valid
      HTTP date.

      .. versionadded:: 3.1

   .. attribute:: if_match

      Read-only property that returns :class:`~aiohttp.ETag` objects specified
      in the *If-Match* header.

      Returns :class:`tuple` of :class:`~aiohttp.ETag` or ``None`` if
      *If-Match* header is absent.

      .. versionadded:: 3.8

   .. attribute:: if_none_match

      Read-only property that returns :class:`~aiohttp.ETag` objects specified
      *If-None-Match* header.

      Returns :class:`tuple` of :class:`~aiohttp.ETag` or ``None`` if
      *If-None-Match* header is absent.

      .. versionadded:: 3.8

   .. attribute:: if_range

      Read-only property that returns the date specified in the
      *If-Range* header.

      Returns :class:`datetime.datetime` or ``None`` if
      *If-Range* header is absent or is not a valid
      HTTP date.

      .. versionadded:: 3.1

   .. method:: clone(*, method=..., rel_url=..., headers=...)

      Clone itself with replacement some attributes.

      Creates and returns a new instance of Request object. If no parameters
      are given, an exact copy is returned. If a parameter is not passed, it
      will reuse the one from the current request object.

      :param str method: http method

      :param rel_url: url to use, :class:`str` or :class:`~yarl.URL`

      :param headers: :class:`~multidict.CIMultiDict` or compatible
                      headers container.

      :return: a cloned :class:`Request` instance.

   .. method:: get_extra_info(name, default=None)

      Reads extra information from the protocol's transport.
      If no value associated with ``name`` is found, ``default`` is returned.

      See :meth:`asyncio.BaseTransport.get_extra_info`

      :param str name: The key to look up in the transport extra information.

      :param default: Default value to be used when no value for ``name`` is
                      found (default is ``None``).

      .. versionadded:: 3.7

   .. method:: read()
      :async:

      Read request body, returns :class:`bytes` object with body content.

      .. note::

         The method **does** store read data internally, subsequent
         :meth:`~aiohttp.web.BaseRequest.read` call will return the same value.

   .. method:: text()
      :async:

      Read request body, decode it using :attr:`charset` encoding or
      ``UTF-8`` if no encoding was specified in *MIME-type*.

      Returns :class:`str` with body content.

      .. note::

         The method **does** store read data internally, subsequent
         :meth:`~aiohttp.web.BaseRequest.text` call will return the same value.

   .. method:: json(*, loads=json.loads, \
                    content_type='application/json')
      :async:

      Read request body decoded as *json*. If request's content-type does not
      match `content_type` parameter, :exc:`aiohttp.web.HTTPBadRequest` get raised.
      To disable content type check pass ``None`` value.

      :param collections.abc.Callable loads: any :term:`callable` that accepts
                              :class:`str` and returns :class:`dict`
                              with parsed JSON (:func:`json.loads` by
                              default).
      :param str content_type: expected value of Content-Type header or ``None``
                              ('application/json' by default)

      .. note::

         The method **does** store read data internally, subsequent
         :meth:`~aiohttp.web.BaseRequest.json` call will return the same value.


   .. method:: multipart()
      :async:

      Returns :class:`aiohttp.MultipartReader` which processes
      incoming *multipart* request.

      The method is just a boilerplate :ref:`coroutine <coroutine>`
      implemented as::

         async def multipart(self, *, reader=aiohttp.multipart.MultipartReader):
             return reader(self.headers, self._payload)

      This method is a coroutine for consistency with the else reader methods.

      .. warning::

         The method **does not** store read data internally. That means once
         you exhausts multipart reader, you cannot get the request payload one
         more time.

      .. seealso:: :ref:`aiohttp-multipart`

      .. versionchanged:: 3.4

         Dropped *reader* parameter.

   .. method:: post()
      :async:

      A :ref:`coroutine <coroutine>` that reads POST parameters from
      request body.

      Returns :class:`~multidict.MultiDictProxy` instance filled
      with parsed data.

      If :attr:`method` is not *POST*, *PUT*, *PATCH*, *TRACE* or *DELETE* or
      :attr:`content_type` is not empty or
      *application/x-www-form-urlencoded* or *multipart/form-data*
      returns empty multidict.

      .. note::

         The method **does** store read data internally, subsequent
         :meth:`~aiohttp.web.BaseRequest.post` call will return the same value.

   .. method:: release()
      :async:

      Release request.

      Eat unread part of HTTP BODY if present.

      .. note::

          User code may never call :meth:`~aiohttp.web.BaseRequest.release`, all
          required work will be processed by :mod:`aiohttp.web`
          internal machinery.

.. class:: Request

   A request used for receiving request's information by *web handler*.

   Every :ref:`handler<aiohttp-web-handler>` accepts a request
   instance as the first positional parameter.

   The class in derived from :class:`BaseRequest`, shares all parent's
   attributes and methods but has a couple of additional properties:

   .. attribute:: match_info

      Read-only property with :class:`~aiohttp.abc.AbstractMatchInfo`
      instance for result of route resolving.

      .. note::

         Exact type of property depends on used router.  If
         ``app.router`` is :class:`UrlDispatcher` the property contains
         :class:`UrlMappingMatchInfo` instance.

   .. attribute:: app

      An :class:`Application` instance used to call :ref:`request handler
      <aiohttp-web-handler>`, Read-only property.

   .. attribute:: config_dict

      A :class:`aiohttp.ChainMapProxy` instance for mapping all properties
      from the current application returned by :attr:`app` property
      and all its parents.

      .. seealso:: :ref:`aiohttp-web-data-sharing-app-config`

      .. versionadded:: 3.2

   .. note::

      You should never create the :class:`Request` instance manually
      -- :mod:`aiohttp.web` does it for you. But
      :meth:`~BaseRequest.clone` may be used for cloning *modified*
      request copy with changed *path*, *method* etc.




.. _aiohttp-web-response:


Response classes
----------------

For now, :mod:`aiohttp.web` has three classes for the *HTTP response*:
:class:`StreamResponse`, :class:`Response` and :class:`FileResponse`.

Usually you need to use the second one. :class:`StreamResponse` is
intended for streaming data, while :class:`Response` contains *HTTP
BODY* as an attribute and sends own content as single piece with the
correct *Content-Length HTTP header*.

For sake of design decisions :class:`Response` is derived from
:class:`StreamResponse` parent class.

The response supports *keep-alive* handling out-of-the-box if
*request* supports it.

You can disable *keep-alive* by :meth:`~StreamResponse.force_close` though.

The common case for sending an answer from
:ref:`web-handler<aiohttp-web-handler>` is returning a
:class:`Response` instance::

   async def handler(request):
       return Response(text="All right!")

Response classes are :obj:`dict` like objects,
allowing them to be used for :ref:`sharing
data<aiohttp-web-data-sharing>` among :ref:`aiohttp-web-middlewares`
and :ref:`aiohttp-web-signals` handlers::

   resp['key'] = value

.. versionadded:: 3.0

   Dict-like interface support.


.. class:: StreamResponse(*, status=200, reason=None)

   The base class for the *HTTP response* handling.

   Contains methods for setting *HTTP response headers*, *cookies*,
   *response status code*, writing *HTTP response BODY* and so on.

   The most important thing you should know about *response* --- it
   is *Finite State Machine*.

   That means you can do any manipulations with *headers*, *cookies*
   and *status code* only before :meth:`prepare` coroutine is called.

   Once you call :meth:`prepare` any change of
   the *HTTP header* part will raise :exc:`RuntimeError` exception.

   Any :meth:`write` call after :meth:`write_eof` is also forbidden.

   :param int status: HTTP status code, ``200`` by default.

   :param str reason: HTTP reason. If param is ``None`` reason will be
                      calculated basing on *status*
                      parameter. Otherwise pass :class:`str` with
                      arbitrary *status* explanation..

   .. attribute:: prepared

      Read-only :class:`bool` property, ``True`` if :meth:`prepare` has
      been called, ``False`` otherwise.

   .. attribute:: task

      A task that serves HTTP request handling.

      May be useful for graceful shutdown of long-running requests
      (streaming, long polling or web-socket).

   .. attribute:: status

      Read-only property for *HTTP response status code*, :class:`int`.

      ``200`` (OK) by default.

   .. attribute:: reason

      Read-only property for *HTTP response reason*, :class:`str`.

   .. method:: set_status(status, reason=None)

      Set :attr:`status` and :attr:`reason`.

      *reason* value is auto calculated if not specified (``None``).

   .. attribute:: keep_alive

      Read-only property, copy of :attr:`aiohttp.web.BaseRequest.keep_alive` by default.

      Can be switched to ``False`` by :meth:`force_close` call.

   .. method:: force_close

      Disable :attr:`keep_alive` for connection. There are no ways to
      enable it back.

   .. attribute:: compression

      Read-only :class:`bool` property, ``True`` if compression is enabled.

      ``False`` by default.

      .. seealso:: :meth:`enable_compression`

   .. method:: enable_compression(force=None, strategy=None)

      Enable compression.

      When *force* is unset compression encoding is selected based on
      the request's *Accept-Encoding* header.

      *Accept-Encoding* is not checked if *force* is set to a
      :class:`ContentCoding`.

      *strategy* accepts a :mod:`zlib` compression strategy.
      See :func:`zlib.compressobj` for possible values, or refer to the
      docs for the zlib of your using, should you use :func:`aiohttp.set_zlib_backend`
      to change zlib backend. If ``None``, the default value adopted by
      your zlib backend will be used where applicable.

      .. seealso:: :attr:`compression`

   .. attribute:: chunked

      Read-only property, indicates if chunked encoding is on.

      Can be enabled by :meth:`enable_chunked_encoding` call.

      .. seealso:: :attr:`enable_chunked_encoding`

   .. method:: enable_chunked_encoding()

      Enables :attr:`chunked` encoding for response. There are no ways to
      disable it back. With enabled :attr:`chunked` encoding each :meth:`write`
      operation encoded in separate chunk.

      .. warning:: chunked encoding can be enabled for ``HTTP/1.1`` only.

                   Setting up both :attr:`content_length` and chunked
                   encoding is mutually exclusive.

      .. seealso:: :attr:`chunked`

   .. attribute:: headers

      :class:`~multidict.CIMultiDict` instance
      for *outgoing* *HTTP headers*.

   .. attribute:: cookies

      An instance of :class:`http.cookies.SimpleCookie` for *outgoing* cookies.

      .. warning::

         Direct setting up *Set-Cookie* header may be overwritten by
         explicit calls to cookie manipulation.

         We are encourage using of :attr:`cookies` and
         :meth:`set_cookie`, :meth:`del_cookie` for cookie
         manipulations.

   .. method:: set_cookie(name, value, *, path='/', expires=None, \
                          domain=None, max_age=None, \
                          secure=None, httponly=None, samesite=None, \
                          partitioned=None)

      Convenient way for setting :attr:`cookies`, allows to specify
      some additional properties like *max_age* in a single call.

      :param str name: cookie name

      :param str value: cookie value (will be converted to
                        :class:`str` if value has another type).

      :param expires: expiration date (optional)

      :param str domain: cookie domain (optional)

      :param int max_age: defines the lifetime of the cookie, in
                          seconds.  The delta-seconds value is a
                          decimal non- negative integer.  After
                          delta-seconds seconds elapse, the client
                          should discard the cookie.  A value of zero
                          means the cookie should be discarded
                          immediately.  (optional)

      :param str path: specifies the subset of URLs to
                       which this cookie applies. (optional, ``'/'`` by default)

      :param bool secure: attribute (with no value) directs
                          the user agent to use only (unspecified)
                          secure means to contact the origin server
                          whenever it sends back this cookie.
                          The user agent (possibly under the user's
                          control) may determine what level of
                          security it considers appropriate for
                          "secure" cookies.  The *secure* should be
                          considered security advice from the server
                          to the user agent, indicating that it is in
                          the session's interest to protect the cookie
                          contents. (optional)

      :param bool httponly: ``True`` if the cookie HTTP only (optional)

      :param str samesite: Asserts that a cookie must not be sent with
         cross-origin requests, providing some protection
         against cross-site request forgery attacks.
         Generally the value should be one of: ``None``,
         ``Lax`` or ``Strict``. (optional)

            .. versionadded:: 3.7

      :param bool partitioned: ``True`` to set a partitioned cookie.
         Available in Python 3.14+. (optional)

            .. versionadded:: 3.12

   .. method:: del_cookie(name, *, path='/', domain=None)

      Deletes cookie.

      :param str name: cookie name

      :param str domain: optional cookie domain

      :param str path: optional cookie path, ``'/'`` by default

   .. attribute:: content_length

      *Content-Length* for outgoing response.

   .. attribute:: content_type

      *Content* part of *Content-Type* for outgoing response.

   .. attribute:: charset

      *Charset* aka *encoding* part of *Content-Type* for outgoing response.

      The value converted to lower-case on attribute assigning.

   .. attribute:: last_modified

      *Last-Modified* header for outgoing response.

      This property accepts raw :class:`str` values,
      :class:`datetime.datetime` objects, Unix timestamps specified
      as an :class:`int` or a :class:`float` object, and the
      value ``None`` to unset the header.

   .. attribute:: etag

      *ETag* header for outgoing response.

      This property accepts raw :class:`str` values, :class:`~aiohttp.ETag`
      objects and the value ``None`` to unset the header.

      In case of :class:`str` input, etag is considered as strong by default.

      **Do not** use double quotes ``"`` in the etag value,
      they will be added automatically.

      .. versionadded:: 3.8

   .. method:: prepare(request)
      :async:

      :param aiohttp.web.Request request: HTTP request object, that the
                                          response answers.

      Send *HTTP header*. You should not change any header data after
      calling this method.

      The coroutine calls :attr:`~aiohttp.web.Application.on_response_prepare`
      signal handlers after default headers have been computed and directly
      before headers are sent.

   .. method:: write(data)
      :async:

      Send byte-ish data as the part of *response BODY*::

          await resp.write(data)

      :meth:`prepare` must be invoked before the call.

      Raises :exc:`TypeError` if data is not :class:`bytes`,
      :class:`bytearray` or :class:`memoryview` instance.

      Raises :exc:`RuntimeError` if :meth:`prepare` has not been called.

      Raises :exc:`RuntimeError` if :meth:`write_eof` has been called.

   .. method:: write_eof()
      :async:

      A :ref:`coroutine<coroutine>` *may* be called as a mark of the
      *HTTP response* processing finish.

      *Internal machinery* will call this method at the end of
      the request processing if needed.

      After :meth:`write_eof` call any manipulations with the *response*
      object are forbidden.


.. class:: Response(*, body=None, status=200, reason=None, text=None, \
                    headers=None, content_type=None, charset=None, \
                    zlib_executor_size=sentinel, zlib_executor=None)

   The most usable response class, inherited from :class:`StreamResponse`.

   Accepts *body* argument for setting the *HTTP response BODY*.

   The actual :attr:`body` sending happens in overridden
   :meth:`~StreamResponse.write_eof`.

   :param bytes body: response's BODY

   :param int status: HTTP status code, 200 OK by default.

   :param collections.abc.Mapping headers: HTTP headers that should be added to
                           response's ones.

   :param str text: response's BODY

   :param str content_type: response's content type. ``'text/plain'``
                       if *text* is passed also,
                       ``'application/octet-stream'`` otherwise.

   :param str charset: response's charset. ``'utf-8'`` if *text* is
                       passed also, ``None`` otherwise.

   :param int zlib_executor_size: length in bytes which will trigger zlib compression
                            of body to happen in an executor

      .. versionadded:: 3.5

   :param int zlib_executor: executor to use for zlib compression

      .. versionadded:: 3.5


   .. attribute:: body

      Read-write attribute for storing response's content aka BODY,
      :class:`bytes`.

      Assigning :class:`str` to :attr:`body` will make the :attr:`body`
      type of :class:`aiohttp.payload.StringPayload`, which tries to encode
      the given data based on *Content-Type* HTTP header, while defaulting
      to ``UTF-8``.

   .. attribute:: text

      Read-write attribute for storing response's
      :attr:`~aiohttp.StreamResponse.body`, represented as :class:`str`.


.. class:: FileResponse(*, path, chunk_size=256*1024, status=200, reason=None, headers=None)

   The response class used to send files, inherited from :class:`StreamResponse`.

   Supports the ``Content-Range`` and ``If-Range`` HTTP Headers in requests.

   The actual :attr:`body` sending happens in overridden :meth:`~StreamResponse.prepare`.

   :param path: Path to file. Accepts both :class:`str` and :class:`pathlib.Path`.
   :param int chunk_size: Chunk size in bytes which will be passed into
                          :meth:`io.RawIOBase.read` in the event that the
                          ``sendfile`` system call is not supported.

   :param int status: HTTP status code, ``200`` by default.

   :param str reason: HTTP reason. If param is ``None`` reason will be
                      calculated basing on *status*
                      parameter. Otherwise pass :class:`str` with
                      arbitrary *status* explanation..

   :param collections.abc.Mapping headers: HTTP headers that should be added to
                           response's ones. The ``Content-Type`` response header
                           will be overridden if provided.


.. class:: WebSocketResponse(*, timeout=10.0, receive_timeout=None, \
                             autoclose=True, autoping=True, heartbeat=None, \
                             protocols=(), compress=True, max_msg_size=4194304, \
                             writer_limit=65536)

   Class for handling server-side websockets, inherited from
   :class:`StreamResponse`.

   After starting (by :meth:`prepare` call) the response you
   cannot use :meth:`~StreamResponse.write` method but should to
   communicate with websocket client by :meth:`send_str`,
   :meth:`receive` and others.

   To enable back-pressure from slow websocket clients treat methods
   :meth:`ping`, :meth:`pong`, :meth:`send_str`,
   :meth:`send_bytes`, :meth:`send_json`, :meth:`send_frame` as coroutines.
   By default write buffer size is set to 64k.

   :param bool autoping: Automatically send
                         :const:`~aiohttp.WSMsgType.PONG` on
                         :const:`~aiohttp.WSMsgType.PING`
                         message from client, and handle
                         :const:`~aiohttp.WSMsgType.PONG`
                         responses from client.
                         Note that server does not send
                         :const:`~aiohttp.WSMsgType.PING`
                         requests, you need to do this explicitly
                         using :meth:`ping` method.

   :param float heartbeat: Send `ping` message every `heartbeat`
                           seconds and wait `pong` response, close
                           connection if `pong` response is not
                           received. The timer is reset on any data reception.

   :param float timeout: Timeout value for the ``close``
                         operation. After sending the close websocket message,
                         ``close`` waits for ``timeout`` seconds for a response.
                         Default value is ``10.0`` (10 seconds for ``close``
                         operation)

   :param float receive_timeout: Timeout value for `receive`
                                 operations.  Default value is :data:`None`
                                 (no timeout for receive operation)

   :param bool compress: Enable per-message deflate extension support.
                          :data:`False` for disabled, default value is :data:`True`.

   :param int max_msg_size: maximum size of read websocket message, 4
                            MB by default. To disable the size limit use ``0``.

      .. versionadded:: 3.3

   :param bool autoclose: Close connection when the client sends
                           a :const:`~aiohttp.WSMsgType.CLOSE` message,
                           ``True`` by default. If set to ``False``,
                           the connection is not closed and the
                           caller is responsible for calling
                           ``request.transport.close()`` to avoid
                           leaking resources.

   :param int writer_limit: maximum size of write buffer, 64 KB by default.
                            Once the buffer is full, the websocket will pause
                            to drain the buffer.

      .. versionadded:: 3.11

   The class supports ``async for`` statement for iterating over
   incoming messages::

      ws = web.WebSocketResponse()
      await ws.prepare(request)

          async for msg in ws:
              print(msg.data)


   .. method:: prepare(request)
      :async:

      Starts websocket. After the call you can use websocket methods.

      :param aiohttp.web.Request request: HTTP request object, that the
                                          response answers.


      :raises HTTPException: if websocket handshake has failed.

   .. method:: can_prepare(request)

      Performs checks for *request* data to figure out if websocket
      can be started on the request.

      If :meth:`can_prepare` call is success then :meth:`prepare` will
      success too.

      :param aiohttp.web.Request request: HTTP request object, that the
                                          response answers.

      :return: :class:`WebSocketReady` instance.

               :attr:`WebSocketReady.ok` is
               ``True`` on success, :attr:`WebSocketReady.protocol` is
               websocket subprotocol which is passed by client and
               accepted by server (one of *protocols* sequence from
               :class:`WebSocketResponse` ctor).
               :attr:`WebSocketReady.protocol` may be ``None`` if
               client and server subprotocols are not overlapping.

      .. note:: The method never raises exception.

   .. attribute:: closed

      Read-only property, ``True`` if connection has been closed or in process
      of closing.
      :const:`~aiohttp.WSMsgType.CLOSE` message has been received from peer.

   .. attribute:: prepared

      Read-only :class:`bool` property, ``True`` if :meth:`prepare` has
      been called, ``False`` otherwise.

   .. attribute:: close_code

      Read-only property, close code from peer. It is set to ``None`` on
      opened connection.

   .. attribute:: ws_protocol

      Websocket *subprotocol* chosen after :meth:`start` call.

      May be ``None`` if server and client protocols are
      not overlapping.

   .. method:: get_extra_info(name, default=None)

      Reads optional extra information from the writer's transport.
      If no value associated with ``name`` is found, ``default`` is returned.

      See :meth:`asyncio.BaseTransport.get_extra_info`

      :param str name: The key to look up in the transport extra information.

      :param default: Default value to be used when no value for ``name`` is
                      found (default is ``None``).

   .. method:: exception()

      Returns last occurred exception or None.

   .. method:: ping(message=b'')
      :async:

      Send :const:`~aiohttp.WSMsgType.PING` to peer.

      :param message: optional payload of *ping* message,
                      :class:`str` (converted to *UTF-8* encoded bytes)
                      or :class:`bytes`.

      :raise RuntimeError: if the connections is not started.

      :raise aiohttp.ClientConnectionResetError: if the connection is closing.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`

   .. method:: pong(message=b'')
      :async:

      Send *unsolicited* :const:`~aiohttp.WSMsgType.PONG` to peer.

      :param message: optional payload of *pong* message,
                      :class:`str` (converted to *UTF-8* encoded bytes)
                      or :class:`bytes`.

      :raise RuntimeError: if the connections is not started.

      :raise aiohttp.ClientConnectionResetError: if the connection is closing.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`

   .. method:: send_str(data, compress=None)
      :async:

      Send *data* to peer as :const:`~aiohttp.WSMsgType.TEXT` message.

      :param str data: data to send.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      :raise RuntimeError: if the connection is not started.

      :raise TypeError: if data is not :class:`str`

      :raise aiohttp.ClientConnectionResetError: if the connection is closing.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`,
         *compress* parameter added.

   .. method:: send_bytes(data, compress=None)
      :async:

      Send *data* to peer as :const:`~aiohttp.WSMsgType.BINARY` message.

      :param data: data to send.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      :raise RuntimeError: if the connection is not started.

      :raise TypeError: if data is not :class:`bytes`,
                        :class:`bytearray` or :class:`memoryview`.

      :raise aiohttp.ClientConnectionResetError: if the connection is closing.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`,
         *compress* parameter added.

   .. method:: send_json(data, compress=None, *, dumps=json.dumps)
      :async:

      Send *data* to peer as JSON string.

      :param data: data to send.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      :param collections.abc.Callable dumps: any :term:`callable` that accepts an object and
                             returns a JSON string
                             (:func:`json.dumps` by default).

      :raise RuntimeError: if the connection is not started.

      :raise ValueError: if data is not serializable object

      :raise TypeError: if value returned by ``dumps`` param is not :class:`str`

      :raise aiohttp.ClientConnectionResetError: if the connection is closing.

      .. versionchanged:: 3.0

         The method is converted into :term:`coroutine`,
         *compress* parameter added.

   .. method:: send_frame(message, opcode, compress=None)
      :async:

      Send a :const:`~aiohttp.WSMsgType` message *message* to peer.

      This method is low-level and should be used with caution as it
      only accepts bytes which must conform to the correct message type
      for *message*.

      It is recommended to use the :meth:`send_str`, :meth:`send_bytes`
      or :meth:`send_json` methods instead of this method.

      The primary use case for this method is to send bytes that are
      have already been encoded without having to decode and
      re-encode them.

      :param bytes message: message to send.

      :param ~aiohttp.WSMsgType opcode: opcode of the message.

      :param int compress: sets specific level of compression for
                           single message,
                           ``None`` for not overriding per-socket setting.

      :raise RuntimeError: if the connection is not started.

      :raise aiohttp.ClientConnectionResetError: if the connection is closing.

      .. versionadded:: 3.11

   .. method:: close(*, code=WSCloseCode.OK, message=b'', drain=True)
      :async:

      A :ref:`coroutine<coroutine>` that initiates closing
      handshake by sending :const:`~aiohttp.WSMsgType.CLOSE` message.

      It is safe to call `close()` from different task.

      :param int code: closing code. See also :class:`~aiohttp.WSCloseCode`.

      :param message: optional payload of *close* message,
                      :class:`str` (converted to *UTF-8* encoded bytes)
                      or :class:`bytes`.

      :param bool drain: drain outgoing buffer before closing connection.

      :raise RuntimeError: if connection is not started

   .. method:: receive(timeout=None)
      :async:

      A :ref:`coroutine<coroutine>` that waits upcoming *data*
      message from peer and returns it.

      The coroutine implicitly handles
      :const:`~aiohttp.WSMsgType.PING`,
      :const:`~aiohttp.WSMsgType.PONG` and
      :const:`~aiohttp.WSMsgType.CLOSE` without returning the
      message.

      It process *ping-pong game* and performs *closing handshake* internally.

      .. note::

         Can only be called by the request handling task.

      :param timeout: timeout for `receive` operation.

         timeout value overrides response`s receive_timeout attribute.

      :return: :class:`~aiohttp.WSMessage`

      :raise RuntimeError: if connection is not started

   .. method:: receive_str(*, timeout=None)
      :async:

      A :ref:`coroutine<coroutine>` that calls :meth:`receive` but
      also asserts the message type is :const:`~aiohttp.WSMsgType.TEXT`.

      .. note::

         Can only be called by the request handling task.

      :param timeout: timeout for `receive` operation.

         timeout value overrides response`s receive_timeout attribute.

      :return str: peer's message content.

      :raise aiohttp.WSMessageTypeError: if message is not :const:`~aiohttp.WSMsgType.TEXT`.

   .. method:: receive_bytes(*, timeout=None)
      :async:

      A :ref:`coroutine<coroutine>` that calls :meth:`receive` but
      also asserts the message type is
      :const:`~aiohttp.WSMsgType.BINARY`.

      .. note::

         Can only be called by the request handling task.

      :param timeout: timeout for `receive` operation.

         timeout value overrides response`s receive_timeout attribute.

      :return bytes: peer's message content.

      :raise aiohttp.WSMessageTypeError: if message is not :const:`~aiohttp.WSMsgType.BINARY`.

   .. method:: receive_json(*, loads=json.loads, timeout=None)
      :async:

      A :ref:`coroutine<coroutine>` that calls :meth:`receive_str` and loads the
      JSON string to a Python dict.

      .. note::

         Can only be called by the request handling task.

      :param collections.abc.Callable loads: any :term:`callable` that accepts
                              :class:`str` and returns :class:`dict`
                              with parsed JSON (:func:`json.loads` by
                              default).

      :param timeout: timeout for `receive` operation.

         timeout value overrides response`s receive_timeout attribute.

      :return dict: loaded JSON content

      :raise TypeError: if message is :const:`~aiohttp.WSMsgType.BINARY`.
      :raise ValueError: if message is not valid JSON.


.. seealso:: :ref:`WebSockets handling<aiohttp-web-websockets>`


.. class:: WebSocketReady

   A named tuple for returning result from
   :meth:`WebSocketResponse.can_prepare`.

   Has :class:`bool` check implemented, e.g.::

       if not await ws.can_prepare(...):
           cannot_start_websocket()

   .. attribute:: ok

      ``True`` if websocket connection can be established, ``False``
      otherwise.


   .. attribute:: protocol

      :class:`str` represented selected websocket sub-protocol.

   .. seealso:: :meth:`WebSocketResponse.can_prepare`


.. function:: json_response([data], *, text=None, body=None, \
                            status=200, reason=None, headers=None, \
                            content_type='application/json', \
                            dumps=json.dumps)

Return :class:`Response` with predefined ``'application/json'``
content type and *data* encoded by ``dumps`` parameter
(:func:`json.dumps` by default).


.. _aiohttp-web-app-and-router:

Application and Router
----------------------


.. class:: Application(*, logger=<default>, middlewares=(), \
                       handler_args=None, client_max_size=1024**2, \
                       debug=...)

   Application is a synonym for web-server.

   To get a fully working example, you have to make an *application*, register
   supported urls in the *router* and pass it to :func:`aiohttp.web.run_app`
   or :class:`aiohttp.web.AppRunner`.

   *Application* contains a *router* instance and a list of callbacks that
   will be called during application finishing.

   This class is a :obj:`dict`-like object, so you can use it for
   :ref:`sharing data<aiohttp-web-data-sharing>` globally by storing arbitrary
   properties for later access from a :ref:`handler<aiohttp-web-handler>` via the
   :attr:`Request.app` property::

       app = Application()
       database = AppKey("database", AsyncEngine)
       app[database] = await create_async_engine(db_url)

       async def handler(request):
           async with request.app[database].begin() as conn:
               await conn.execute("DELETE * FROM table")

   Although it` is a :obj:`dict`-like object, it can't be duplicated like one
   using :meth:`~aiohttp.web.Application.copy`.

   The class inherits :class:`dict`.

   :param logger: :class:`logging.Logger` instance for storing application logs.

                  By default the value is ``logging.getLogger("aiohttp.web")``

   :param middlewares: :class:`list` of middleware factories, see
                       :ref:`aiohttp-web-middlewares` for details.

   :param handler_args: dict-like object that overrides keyword arguments of
                        :class:`AppRunner` constructor.

   :param client_max_size: client's maximum size in a request, in
                           bytes.  If a POST request exceeds this
                           value, it raises an
                           `HTTPRequestEntityTooLarge` exception.

   :param debug: Switches debug mode.

      .. deprecated:: 3.5

         The argument does nothing starting from 4.0,
         use asyncio :ref:`asyncio-debug-mode` instead.


   .. attribute:: router

      Read-only property that returns *router instance*.

   .. attribute:: logger

      :class:`logging.Logger` instance for storing application logs.

   .. attribute:: debug

      Boolean value indicating whether the debug mode is turned on or off.

      .. deprecated:: 3.5

         Use asyncio :ref:`asyncio-debug-mode` instead.

   .. attribute:: on_response_prepare

      A :class:`~aiosignal.Signal` that is fired near the end
      of :meth:`StreamResponse.prepare` with parameters *request* and
      *response*. It can be used, for example, to add custom headers to each
      response, or to modify the default headers computed by the application,
      directly before sending the headers to the client.

      Signal handlers should have the following signature::

          async def on_prepare(request, response):
              pass

      .. note::

         The headers are written immediately after these callbacks are run.
         Therefore, if you modify the content of the response, you may need to
         adjust the `Content-Length` header or similar to match. Aiohttp will
         not make any updates to the headers from this point.

   .. attribute:: on_startup

      A :class:`~aiosignal.Signal` that is fired on application start-up.

      Subscribers may use the signal to run background tasks in the event
      loop along with the application's request handler just after the
      application start-up.

      Signal handlers should have the following signature::

          async def on_startup(app):
              pass

      .. seealso:: :ref:`aiohttp-web-signals` and :ref:`aiohttp-web-cleanup-ctx`.

   .. attribute:: on_shutdown

      A :class:`~aiosignal.Signal` that is fired on application shutdown.

      Subscribers may use the signal for gracefully closing long running
      connections, e.g. websockets and data streaming.

      Signal handlers should have the following signature::

          async def on_shutdown(app):
              pass

      It's up to end user to figure out which :term:`web-handler`\s
      are still alive and how to finish them properly.

      We suggest keeping a list of long running handlers in
      :class:`Application` dictionary.

      .. seealso:: :ref:`aiohttp-web-graceful-shutdown` and :attr:`on_cleanup`.

   .. attribute:: on_cleanup

      A :class:`~aiosignal.Signal` that is fired on application cleanup.

      Subscribers may use the signal for gracefully closing
      connections to database server etc.

      Signal handlers should have the following signature::

          async def on_cleanup(app):
              pass

      .. seealso:: :ref:`aiohttp-web-signals` and :attr:`on_shutdown`.

   .. attribute:: cleanup_ctx

      A list of *context generators* for *startup*/*cleanup* handling.

      Signal handlers should have the following signature::

          async def context(app):
              # do startup stuff
              yield
              # do cleanup

      .. versionadded:: 3.1

      .. seealso:: :ref:`aiohttp-web-cleanup-ctx`.

   .. method:: add_subapp(prefix, subapp)

      Register nested sub-application under given path *prefix*.

      In resolving process if request's path starts with *prefix* then
      further resolving is passed to *subapp*.

      :param str prefix: path's prefix for the resource.

      :param Application subapp: nested application attached under *prefix*.

      :returns: a :class:`PrefixedSubAppResource` instance.

   .. method:: add_domain(domain, subapp)

      Register nested sub-application that serves
      the domain name or domain name mask.

      In resolving process if request.headers['host']
      matches the pattern *domain* then
      further resolving is passed to *subapp*.

      :param str domain: domain or mask of domain for the resource.

      :param Application subapp: nested application.

      :returns: a :class:`~aiohttp.web.MatchedSubAppResource` instance.

   .. method:: add_routes(routes_table)

      Register route definitions from *routes_table*.

      The table is a :class:`list` of :class:`RouteDef` items or
      :class:`RouteTableDef`.

      :returns: :class:`list` of registered :class:`AbstractRoute` instances.

      The method is a shortcut for
      ``app.router.add_routes(routes_table)``, see also
      :meth:`UrlDispatcher.add_routes`.

      .. versionadded:: 3.1

      .. versionchanged:: 3.7

         Return value updated from ``None`` to :class:`list` of
         :class:`AbstractRoute` instances.

   .. method:: startup()
      :async:

      A :ref:`coroutine<coroutine>` that will be called along with the
      application's request handler.

      The purpose of the method is calling :attr:`on_startup` signal
      handlers.

   .. method:: shutdown()
      :async:

      A :ref:`coroutine<coroutine>` that should be called on
      server stopping but before :meth:`cleanup`.

      The purpose of the method is calling :attr:`on_shutdown` signal
      handlers.

   .. method:: cleanup()
      :async:

      A :ref:`coroutine<coroutine>` that should be called on
      server stopping but after :meth:`shutdown`.

      The purpose of the method is calling :attr:`on_cleanup` signal
      handlers.

   .. note::

      Application object has :attr:`router` attribute but has no
      ``add_route()`` method. The reason is: we want to support
      different router implementations (even maybe not url-matching
      based but traversal ones).

      For sake of that fact we have very trivial ABC for
      :class:`~aiohttp.abc.AbstractRouter`: it should have only
      :meth:`aiohttp.abc.AbstractRouter.resolve` coroutine.

      No methods for adding routes or route reversing (getting URL by
      route name). All those are router implementation details (but,
      sure, you need to deal with that methods after choosing the
      router for your application).


.. class:: AppKey(name, t)

   This class should be used for the keys in :class:`Application`. They
   provide a type-safe alternative to `str` keys when checking your code
   with a type checker (e.g. mypy). They also avoid name clashes with keys
   from different libraries etc.

   :param name: A name to help with debugging. This should be the same as
                the variable name (much like how :class:`typing.TypeVar`
                is used).

   :param t: The type that should be used for the value in the dict (e.g.
             `str`, `Iterator[int]` etc.)

.. class:: Server

   A protocol factory compatible with
   :meth:`~asyncio.AbstractEventLoop.create_server`.

   The class is responsible for creating HTTP protocol
   objects that can handle HTTP connections.

   .. attribute:: connections

      List of all currently opened connections.

   .. attribute:: requests_count

      Amount of processed requests.

   .. method:: Server.shutdown(timeout)
      :async:

      A :ref:`coroutine<coroutine>` that should be called to close all opened
      connections.


.. class:: UrlDispatcher()

   For dispatching URLs to :ref:`handlers<aiohttp-web-handler>`
   :mod:`aiohttp.web` uses *routers*, which is any object that implements
   :class:`~aiohttp.abc.AbstractRouter` interface.

   This class is a straightforward url-matching router, implementing
   :class:`collections.abc.Mapping` for access to *named routes*.

   :class:`Application` uses this class as
   :meth:`~aiohttp.web.Application.router` by default.

   Before running an :class:`Application` you should fill *route
   table* first by calling :meth:`add_route` and :meth:`add_static`.

   :ref:`Handler<aiohttp-web-handler>` lookup is performed by iterating on
   added *routes* in FIFO order. The first matching *route* will be used
   to call the corresponding *handler*.

   If during route creation you specify *name* parameter the result is a
   *named route*.

   A *named route* can be retrieved by a ``app.router[name]`` call, checking for
   existence can be done with ``name in app.router`` etc.

   .. seealso:: :ref:`Route classes <aiohttp-web-route>`

   .. method:: add_resource(path, *, name=None)

      Append a :term:`resource` to the end of route table.

      *path* may be either *constant* string like ``'/a/b/c'`` or
      *variable rule* like ``'/a/{var}'`` (see
      :ref:`handling variable paths <aiohttp-web-variable-handler>`)

      :param str path: resource path spec.

      :param str name: optional resource name.

      :return: created resource instance (:class:`PlainResource` or
               :class:`DynamicResource`).

   .. method:: add_route(method, path, handler, *, \
                         name=None, expect_handler=None)

      Append :ref:`handler<aiohttp-web-handler>` to the end of route table.

      *path* may be either *constant* string like ``'/a/b/c'`` or
       *variable rule* like ``'/a/{var}'`` (see
       :ref:`handling variable paths <aiohttp-web-variable-handler>`)

      Pay attention please: *handler* must be a coroutine.

      :param str method: HTTP method for route. Should be one of
                         ``'GET'``, ``'POST'``, ``'PUT'``,
                         ``'DELETE'``, ``'PATCH'``, ``'HEAD'``,
                         ``'OPTIONS'`` or ``'*'`` for any method.

                         The parameter is case-insensitive, e.g. you
                         can push ``'get'`` as well as ``'GET'``.

      :param str path: route path. Should be started with slash (``'/'``).

      :param collections.abc.Callable handler: route handler.

      :param str name: optional route name.

      :param collections.abc.Coroutine expect_handler: optional *expect* header handler.

      :returns: new :class:`AbstractRoute` instance.

   .. method:: add_routes(routes_table)

      Register route definitions from *routes_table*.

      The table is a :class:`list` of :class:`RouteDef` items or
      :class:`RouteTableDef`.

      :returns: :class:`list` of registered :class:`AbstractRoute` instances.

      .. versionadded:: 2.3

      .. versionchanged:: 3.7

         Return value updated from ``None`` to :class:`list` of
         :class:`AbstractRoute` instances.

   .. method:: add_get(path, handler, *, name=None, allow_head=True, **kwargs)

      Shortcut for adding a GET handler. Calls the :meth:`add_route` with \
      ``method`` equals to ``'GET'``.

      If *allow_head* is ``True`` (default) the route for method HEAD
      is added with the same handler as for GET.

      If *name* is provided the name for HEAD route is suffixed with
      ``'-head'``. For example ``router.add_get(path, handler,
      name='route')`` call adds two routes: first for GET with name
      ``'route'`` and second for HEAD with name ``'route-head'``.

   .. method:: add_post(path, handler, **kwargs)

      Shortcut for adding a POST handler. Calls the :meth:`add_route` with \


      ``method`` equals to ``'POST'``.

   .. method:: add_head(path, handler, **kwargs)

      Shortcut for adding a HEAD handler. Calls the :meth:`add_route` with \
      ``method`` equals to ``'HEAD'``.

   .. method:: add_put(path, handler, **kwargs)

      Shortcut for adding a PUT handler. Calls the :meth:`add_route` with \
      ``method`` equals to ``'PUT'``.

   .. method:: add_patch(path, handler, **kwargs)

      Shortcut for adding a PATCH handler. Calls the :meth:`add_route` with \
      ``method`` equals to ``'PATCH'``.

   .. method:: add_delete(path, handler, **kwargs)

      Shortcut for adding a DELETE handler. Calls the :meth:`add_route` with \
      ``method`` equals to ``'DELETE'``.

   .. method:: add_view(path, handler, **kwargs)

      Shortcut for adding a class-based view handler. Calls the \
      :meth:`add_route` with ``method`` equals to ``'*'``.

      .. versionadded:: 3.0

   .. method:: add_static(prefix, path, *, name=None, expect_handler=None, \
                          chunk_size=256*1024, \
                          response_factory=StreamResponse, \
                          show_index=False, \
                          follow_symlinks=False, \
                          append_version=False)

      Adds a router and a handler for returning static files.

      Useful for serving static content like images, javascript and css files.

      On platforms that support it, the handler will transfer files more
      efficiently using the ``sendfile`` system call.

      In some situations it might be necessary to avoid using the ``sendfile``
      system call even if the platform supports it. This can be accomplished by
      by setting environment variable ``AIOHTTP_NOSENDFILE=1``.

      If a Brotli or gzip compressed version of the static content exists at
      the requested path with the ``.br`` or ``.gz`` extension, it will be used
      for the response. Brotli will be preferred over gzip if both files exist.

      .. warning::

         Use :meth:`add_static` for development only. In production,
         static content should be processed by web servers like *nginx*
         or *apache*. Such web servers will be able to provide significantly
         better performance and security for static assets. Several past security
         vulnerabilities in aiohttp only affected applications using
         :meth:`add_static`.

      :param str prefix: URL path prefix for handled static files

      :param path: path to the folder in file system that contains
                   handled static files, :class:`str` or :class:`pathlib.Path`.

      :param str name: optional route name.

      :param collections.abc.Coroutine expect_handler: optional *expect* header handler.

      :param int chunk_size: size of single chunk for file
                             downloading, 256Kb by default.

                             Increasing *chunk_size* parameter to,
                             say, 1Mb may increase file downloading
                             speed but consumes more memory.

      :param bool show_index: flag for allowing to show indexes of a directory,
                              by default it's not allowed and HTTP/403 will
                              be returned on directory access.

      :param bool follow_symlinks: flag for allowing to follow symlinks that lead
                              outside the static root directory, by default it's not allowed and
                              HTTP/404 will be returned on access.  Enabling ``follow_symlinks``
                              can be a security risk, and may lead to a directory transversal attack.
                              You do NOT need this option to follow symlinks which point to somewhere
                              else within the static directory, this option is only used to break out
                              of the security sandbox. Enabling this option is highly discouraged,
                              and only expected to be used for edge cases in a local development
                              setting where remote users do not have access to the server.

      :param bool append_version: flag for adding file version (hash)
                              to the url query string, this value will
                              be used as default when you call to
                              :meth:`~aiohttp.web.AbstractRoute.url` and
                              :meth:`~aiohttp.web.AbstractRoute.url_for` methods.


      :returns: new :class:`~aiohttp.web.AbstractRoute` instance.

   .. method:: resolve(request)
      :async:

      A :ref:`coroutine<coroutine>` that returns
      :class:`~aiohttp.abc.AbstractMatchInfo` for *request*.

      The method never raises exception, but returns
      :class:`~aiohttp.abc.AbstractMatchInfo` instance with:

      1. :attr:`~aiohttp.abc.AbstractMatchInfo.http_exception` assigned to
         :exc:`HTTPException` instance.
      2. :meth:`~aiohttp.abc.AbstractMatchInfo.handler` which raises
         :exc:`HTTPNotFound` or :exc:`HTTPMethodNotAllowed` on handler's
         execution if there is no registered route for *request*.

         *Middlewares* can process that exceptions to render
         pretty-looking error page for example.

      Used by internal machinery, end user unlikely need to call the method.

      .. note:: The method uses :attr:`aiohttp.web.BaseRequest.raw_path` for pattern
         matching against registered routes.

   .. method:: resources()

      The method returns a *view* for *all* registered resources.

      The view is an object that allows to:

      1. Get size of the router table::

           len(app.router.resources())

      2. Iterate over registered resources::

           for resource in app.router.resources():
               print(resource)

      3. Make a check if the resources is registered in the router table::

           route in app.router.resources()

   .. method:: routes()

      The method returns a *view* for *all* registered routes.

   .. method:: named_resources()

      Returns a :obj:`dict`-like :class:`types.MappingProxyType` *view* over
      *all* named **resources**.

      The view maps every named resource's **name** to the
      :class:`AbstractResource` instance. It supports the usual
      :obj:`dict`-like operations, except for any mutable operations
      (i.e. it's **read-only**)::

          len(app.router.named_resources())

          for name, resource in app.router.named_resources().items():
              print(name, resource)

          "name" in app.router.named_resources()

          app.router.named_resources()["name"]


.. _aiohttp-web-resource:

Resource
^^^^^^^^

Default router :class:`UrlDispatcher` operates with :term:`resource`\s.

Resource is an item in *routing table* which has a *path*, an optional
unique *name* and at least one :term:`route`.

:term:`web-handler` lookup is performed in the following way:

1. The router splits the URL and checks the index from longest to shortest.
   For example, '/one/two/three' will first check the index for
   '/one/two/three', then '/one/two' and finally '/'.
2. If the URL part is found in the index, the list of routes for
   that URL part is iterated over. If a route matches to requested HTTP
   method (or ``'*'`` wildcard) the route's handler is used as the chosen
   :term:`web-handler`. The lookup is finished.
3. If the route is not found in the index, the router tries to find
   the route in the list of :class:`~aiohttp.web.MatchedSubAppResource`,
   (current only created from :meth:`~aiohttp.web.Application.add_domain`),
   and will iterate over the list of
   :class:`~aiohttp.web.MatchedSubAppResource` in a linear fashion
   until a match is found.
4. If no *resource* / *route* pair was found, the *router*
   returns the special :class:`~aiohttp.abc.AbstractMatchInfo`
   instance with :attr:`aiohttp.abc.AbstractMatchInfo.http_exception` is not ``None``
   but :exc:`HTTPException` with  either *HTTP 404 Not Found* or
   *HTTP 405 Method Not Allowed* status code.
   Registered :meth:`~aiohttp.abc.AbstractMatchInfo.handler` raises this exception on call.

Fixed paths are preferred over variable paths. For example,
if you have two routes ``/a/b`` and ``/a/{name}``, then the first
route will always be preferred over the second one.

If there are multiple dynamic paths with the same fixed prefix,
they will be resolved in order of registration.

For example, if you have two dynamic routes that are prefixed
with the fixed ``/users`` path such as ``/users/{x}/{y}/z`` and
``/users/{x}/y/z``, the first one will be preferred over the
second one.

User should never instantiate resource classes but give it by
:meth:`UrlDispatcher.add_resource` call.

After that he may add a :term:`route` by calling :meth:`Resource.add_route`.

:meth:`UrlDispatcher.add_route` is just shortcut for::

   router.add_resource(path).add_route(method, handler)

Resource with a *name* is called *named resource*.
The main purpose of *named resource* is constructing URL by route name for
passing it into *template engine* for example::

   url = app.router['resource_name'].url_for().with_query({'a': 1, 'b': 2})

Resource classes hierarchy::

   AbstractResource
     Resource
       PlainResource
       DynamicResource
     PrefixResource
       StaticResource
       PrefixedSubAppResource
          MatchedSubAppResource


.. class:: AbstractResource

   A base class for all resources.

   Inherited from :class:`collections.abc.Sized` and
   :class:`collections.abc.Iterable`.

   ``len(resource)`` returns amount of :term:`route`\s belongs to the resource,
   ``for route in resource`` allows to iterate over these routes.

   .. attribute:: name

      Read-only *name* of resource or ``None``.

   .. attribute:: canonical

      Read-only *canonical path* associate with the resource. For example
      ``/path/to`` or ``/path/{to}``

      .. versionadded:: 3.3

   .. method:: resolve(request)
      :async:

      Resolve resource by finding appropriate :term:`web-handler` for
      ``(method, path)`` combination.

      :return: (*match_info*, *allowed_methods*) pair.

               *allowed_methods* is a :class:`set` or HTTP methods accepted by
               resource.

               *match_info* is either :class:`UrlMappingMatchInfo` if
               request is resolved or ``None`` if no :term:`route` is
               found.

   .. method:: get_info()

      A resource description, e.g. ``{'path': '/path/to'}`` or
      ``{'formatter': '/path/{to}', 'pattern':
      re.compile(r'^/path/(?P<to>[a-zA-Z][_a-zA-Z0-9]+)$``

   .. method:: url_for(*args, **kwargs)

      Construct an URL for route with additional params.

      *args* and **kwargs** depend on a parameters list accepted by
      inherited resource class.

      :return: :class:`~yarl.URL` -- resulting URL instance.


.. class:: Resource

   A base class for new-style resources, inherits :class:`AbstractResource`.


   .. method:: add_route(method, handler, *, expect_handler=None)

      Add a :term:`web-handler` to resource.

      :param str method: HTTP method for route. Should be one of
                         ``'GET'``, ``'POST'``, ``'PUT'``,
                         ``'DELETE'``, ``'PATCH'``, ``'HEAD'``,
                         ``'OPTIONS'`` or ``'*'`` for any method.

                         The parameter is case-insensitive, e.g. you
                         can push ``'get'`` as well as ``'GET'``.

                         The method should be unique for resource.

      :param collections.abc.Callable handler: route handler.

      :param collections.abc.Coroutine expect_handler: optional *expect* header handler.

      :returns: new :class:`ResourceRoute` instance.


.. class:: PlainResource

   A resource, inherited from :class:`Resource`.

   The class corresponds to resources with plain-text matching,
   ``'/path/to'`` for example.

   .. attribute:: canonical

      Read-only *canonical path* associate with the resource. Returns the path
      used to create the PlainResource. For example ``/path/to``

      .. versionadded:: 3.3

   .. method:: url_for()

      Returns a :class:`~yarl.URL` for the resource.


.. class:: DynamicResource

   A resource, inherited from :class:`Resource`.

   The class corresponds to resources with
   :ref:`variable <aiohttp-web-variable-handler>` matching,
   e.g. ``'/path/{to}/{param}'`` etc.

   .. attribute:: canonical

      Read-only *canonical path* associate with the resource. Returns the
      formatter obtained from the path used to create the DynamicResource.
      For example, from a path ``/get/{num:^\d+}``, it returns ``/get/{num}``

      .. versionadded:: 3.3

   .. method:: url_for(**params)

      Returns a :class:`~yarl.URL` for the resource.

      :param params: -- a variable substitutions for dynamic resource.

         E.g. for ``'/path/{to}/{param}'`` pattern the method should
         be called as ``resource.url_for(to='val1', param='val2')``


.. class:: StaticResource

   A resource, inherited from :class:`Resource`.

   The class corresponds to resources for :ref:`static file serving
   <aiohttp-web-static-file-handling>`.

   .. attribute:: canonical

      Read-only *canonical path* associate with the resource. Returns the prefix
      used to create the StaticResource. For example ``/prefix``

      .. versionadded:: 3.3

   .. method:: url_for(filename, append_version=None)

      Returns a :class:`~yarl.URL` for file path under resource prefix.

      :param filename: -- a file name substitution for static file handler.

         Accepts both :class:`str` and :class:`pathlib.Path`.

         E.g. an URL for ``'/prefix/dir/file.txt'`` should
         be generated as ``resource.url_for(filename='dir/file.txt')``

      :param bool append_version: -- a flag for adding file version
                                  (hash) to the url query string for
                                  cache boosting

         By default has value from a constructor (``False`` by default)
         When set to ``True`` - ``v=FILE_HASH`` query string param will be added
         When set to ``False`` has no impact

         if file not found has no impact


.. class:: PrefixedSubAppResource

   A resource for serving nested applications. The class instance is
   returned by :class:`~aiohttp.web.Application.add_subapp` call.

   .. attribute:: canonical

      Read-only *canonical path* associate with the resource. Returns the
      prefix used to create the PrefixedSubAppResource.
      For example ``/prefix``

      .. versionadded:: 3.3

   .. method:: url_for(**kwargs)

      The call is not allowed, it raises :exc:`RuntimeError`.


.. _aiohttp-web-route:

Route
^^^^^

Route has *HTTP method* (wildcard ``'*'`` is an option),
:term:`web-handler` and optional *expect handler*.

Every route belong to some resource.

Route classes hierarchy::

   AbstractRoute
     ResourceRoute
     SystemRoute

:class:`ResourceRoute` is the route used for resources,
:class:`SystemRoute` serves URL resolving errors like *404 Not Found*
and *405 Method Not Allowed*.

.. class:: AbstractRoute

   Base class for routes served by :class:`UrlDispatcher`.

   .. attribute:: method

      HTTP method handled by the route, e.g. *GET*, *POST* etc.

   .. attribute:: handler

      :ref:`handler<aiohttp-web-handler>` that processes the route.

   .. attribute:: name

      Name of the route, always equals to name of resource which owns the route.

   .. attribute:: resource

      Resource instance which holds the route, ``None`` for
      :class:`SystemRoute`.

   .. method:: url_for(*args, **kwargs)

      Abstract method for constructing url handled by the route.

      Actually it's a shortcut for ``route.resource.url_for(...)``.

   .. method:: handle_expect_header(request)
      :async:

      ``100-continue`` handler.

.. class:: ResourceRoute

   The route class for handling different HTTP methods for :class:`Resource`.


.. class:: SystemRoute

   The route class for handling URL resolution errors like like *404 Not Found*
   and *405 Method Not Allowed*.

   .. attribute:: status

      HTTP status code

   .. attribute:: reason

      HTTP status reason


.. _aiohttp-web-route-def:


RouteDef and StaticDef
^^^^^^^^^^^^^^^^^^^^^^

Route definition, a description for not registered yet route.

Could be used for filing route table by providing a list of route
definitions (Django style).

The definition is created by functions like :func:`get` or
:func:`post`, list of definitions could be added to router by
:meth:`UrlDispatcher.add_routes` call::

   from aiohttp import web

   async def handle_get(request):
       ...


   async def handle_post(request):
       ...

   app.router.add_routes([web.get('/get', handle_get),
                          web.post('/post', handle_post),

.. class:: AbstractRouteDef

   A base class for route definitions.

   Inherited from :class:`abc.ABC`.

   .. versionadded:: 3.1

   .. method:: register(router)

      Register itself into :class:`UrlDispatcher`.

      Abstract method, should be overridden by subclasses.

      :returns: :class:`list` of registered :class:`AbstractRoute` objects.

      .. versionchanged:: 3.7

         Return value updated from ``None`` to :class:`list` of
         :class:`AbstractRoute` instances.


.. class:: RouteDef

   A definition of not registered yet route.

   Implements :class:`AbstractRouteDef`.

   .. versionadded:: 2.3

   .. versionchanged:: 3.1

      The class implements :class:`AbstractRouteDef` interface.

   .. attribute:: method

      HTTP method (``GET``, ``POST`` etc.)  (:class:`str`).

   .. attribute:: path

      Path to resource, e.g. ``/path/to``. Could contain ``{}``
      brackets for :ref:`variable resources
      <aiohttp-web-variable-handler>` (:class:`str`).

   .. attribute:: handler

      An async function to handle HTTP request.

   .. attribute:: kwargs

      A :class:`dict` of additional arguments.


.. class:: StaticDef

   A definition of static file resource.

   Implements :class:`AbstractRouteDef`.

   .. versionadded:: 3.1

   .. attribute:: prefix

      A prefix used for static file handling, e.g. ``/static``.

   .. attribute:: path

      File system directory to serve, :class:`str` or
      :class:`pathlib.Path`
      (e.g. ``'/home/web-service/path/to/static'``.

   .. attribute:: kwargs

      A :class:`dict` of additional arguments, see
      :meth:`UrlDispatcher.add_static` for a list of supported
      options.


.. function:: get(path, handler, *, name=None, allow_head=True, \
              expect_handler=None)

   Return :class:`RouteDef` for processing ``GET`` requests. See
   :meth:`UrlDispatcher.add_get` for information about parameters.

   .. versionadded:: 2.3

.. function:: post(path, handler, *, name=None, expect_handler=None)

   Return :class:`RouteDef` for processing ``POST`` requests. See
   :meth:`UrlDispatcher.add_post` for information about parameters.

   .. versionadded:: 2.3

.. function:: head(path, handler, *, name=None, expect_handler=None)

   Return :class:`RouteDef` for processing ``HEAD`` requests. See
   :meth:`UrlDispatcher.add_head` for information about parameters.

   .. versionadded:: 2.3

.. function:: put(path, handler, *, name=None, expect_handler=None)

   Return :class:`RouteDef` for processing ``PUT`` requests. See
   :meth:`UrlDispatcher.add_put` for information about parameters.

   .. versionadded:: 2.3

.. function:: patch(path, handler, *, name=None, expect_handler=None)

   Return :class:`RouteDef` for processing ``PATCH`` requests. See
   :meth:`UrlDispatcher.add_patch` for information about parameters.

   .. versionadded:: 2.3

.. function:: delete(path, handler, *, name=None, expect_handler=None)

   Return :class:`RouteDef` for processing ``DELETE`` requests. See
   :meth:`UrlDispatcher.add_delete` for information about parameters.

   .. versionadded:: 2.3

.. function:: view(path, handler, *, name=None, expect_handler=None)

   Return :class:`RouteDef` for processing ``ANY`` requests. See
   :meth:`UrlDispatcher.add_view` for information about parameters.

   .. versionadded:: 3.0

.. function:: static(prefix, path, *, name=None, expect_handler=None, \
                     chunk_size=256*1024, \
                     show_index=False, follow_symlinks=False, \
                     append_version=False)

   Return :class:`StaticDef` for processing static files.

   See :meth:`UrlDispatcher.add_static` for information
   about supported parameters.

   .. versionadded:: 3.1

.. function:: route(method, path, handler, *, name=None, expect_handler=None)

   Return :class:`RouteDef` for processing requests that decided by
   ``method``. See :meth:`UrlDispatcher.add_route` for information
   about parameters.

   .. versionadded:: 2.3


.. _aiohttp-web-route-table-def:

RouteTableDef
^^^^^^^^^^^^^

A routes table definition used for describing routes by decorators
(Flask style)::

   from aiohttp import web

   routes = web.RouteTableDef()

   @routes.get('/get')
   async def handle_get(request):
       ...


   @routes.post('/post')
   async def handle_post(request):
       ...

   app.router.add_routes(routes)


   @routes.view("/view")
   class MyView(web.View):
       async def get(self):
           ...

       async def post(self):
           ...

.. class:: RouteTableDef()

   A sequence of :class:`RouteDef` instances (implements
   :class:`collections.abc.Sequence` protocol).

   In addition to all standard :class:`list` methods the class
   provides also methods like ``get()`` and ``post()`` for adding new
   route definition.

   .. versionadded:: 2.3

   .. decoratormethod:: get(path, *, allow_head=True, \
                            name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering ``GET`` web-handler.

      See :meth:`UrlDispatcher.add_get` for information about parameters.

   .. decoratormethod:: post(path, *, name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering ``POST`` web-handler.

      See :meth:`UrlDispatcher.add_post` for information about parameters.

   .. decoratormethod:: head(path, *, name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering ``HEAD`` web-handler.

      See :meth:`UrlDispatcher.add_head` for information about parameters.

   .. decoratormethod:: put(path, *, name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering ``PUT`` web-handler.

      See :meth:`UrlDispatcher.add_put` for information about parameters.

   .. decoratormethod:: patch(path, *, name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering ``PATCH`` web-handler.

      See :meth:`UrlDispatcher.add_patch` for information about parameters.

   .. decoratormethod:: delete(path, *, name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering ``DELETE`` web-handler.

      See :meth:`UrlDispatcher.add_delete` for information about parameters.

   .. decoratormethod:: view(path, *, name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering ``ANY`` methods
      against a class-based view.

      See :meth:`UrlDispatcher.add_view` for information about parameters.

      .. versionadded:: 3.0

   .. method:: static(prefix, path, *, name=None, expect_handler=None, \
                      chunk_size=256*1024, \
                      show_index=False, follow_symlinks=False, \
                      append_version=False)


      Add a new :class:`StaticDef` item for registering static files processor.

      See :meth:`UrlDispatcher.add_static` for information about
      supported parameters.

      .. versionadded:: 3.1

   .. decoratormethod:: route(method, path, *, name=None, expect_handler=None)

      Add a new :class:`RouteDef` item for registering a web-handler
      for arbitrary HTTP method.

      See :meth:`UrlDispatcher.add_route` for information about parameters.


MatchInfo
^^^^^^^^^

After route matching web application calls found handler if any.

Matching result can be accessible from handler as
:attr:`Request.match_info` attribute.

In general the result may be any object derived from
:class:`~aiohttp.abc.AbstractMatchInfo` (:class:`UrlMappingMatchInfo` for default
:class:`UrlDispatcher` router).

.. class:: UrlMappingMatchInfo

   Inherited from :class:`dict` and :class:`~aiohttp.abc.AbstractMatchInfo`. Dict
   items are filled by matching info and is :term:`resource`\-specific.

   .. attribute:: expect_handler

      A coroutine for handling ``100-continue``.

   .. attribute:: handler

      A coroutine for handling request.

   .. attribute:: route

      :class:`AbstractRoute` instance for url matching.


View
^^^^

.. class:: View(request)

   Inherited from :class:`~aiohttp.abc.AbstractView`.

   Base class for class based views. Implementations should derive from
   :class:`View` and override methods for handling HTTP verbs like
   ``get()`` or ``post()``::

       class MyView(View):

           async def get(self):
               resp = await get_response(self.request)
               return resp

           async def post(self):
               resp = await post_response(self.request)
               return resp

       app.router.add_view('/view', MyView)

   The view raises *405 Method Not allowed*
   (:class:`HTTPMethodNotAllowed`) if requested web verb is not
   supported.

   :param request: instance of :class:`Request` that has initiated a view
                   processing.


   .. attribute:: request

      Request sent to view's constructor, read-only property.


   Overridable coroutine methods: ``connect()``, ``delete()``,
   ``get()``, ``head()``, ``options()``, ``patch()``, ``post()``,
   ``put()``, ``trace()``.

.. seealso:: :ref:`aiohttp-web-class-based-views`


.. _aiohttp-web-app-runners-reference:

Running Applications
--------------------

To start web application there is ``AppRunner`` and site classes.

Runner is a storage for running application, sites are for running
application on specific TCP or Unix socket, e.g.::

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    # wait for finish signal
    await runner.cleanup()


.. versionadded:: 3.0

   :class:`AppRunner` / :class:`ServerRunner` and :class:`TCPSite` /
   :class:`UnixSite` / :class:`SockSite` are added in aiohttp 3.0


.. class:: BaseRunner

   A base class for runners. Use :class:`AppRunner` for serving
   :class:`Application`, :class:`ServerRunner` for low-level
   :class:`Server`.

   .. attribute:: server

      Low-level web :class:`Server` for handling HTTP requests,
      read-only attribute.

   .. attribute:: addresses

      A  :class:`list` of served sockets addresses.

      See :meth:`socket.getsockname() <socket.socket.getsockname>` for items type.

      .. versionadded:: 3.3

   .. attribute:: sites

      A read-only :class:`set` of served sites (:class:`TCPSite` /
      :class:`UnixSite` / :class:`NamedPipeSite` / :class:`SockSite` instances).

   .. method:: setup()
      :async:

      Initialize the server. Should be called before adding sites.

   .. method:: cleanup()
      :async:

      Stop handling all registered sites and cleanup used resources.


.. class:: AppRunner(app, *, handle_signals=False, **kwargs)

   A runner for :class:`Application`. Used with conjunction with sites
   to serve on specific port.

   Inherited from :class:`BaseRunner`.

   :param Application app: web application instance to serve.

   :param bool handle_signals: add signal handlers for
                               :data:`signal.SIGINT` and
                               :data:`signal.SIGTERM` (``False`` by
                               default). These handlers will raise
                               :exc:`GracefulExit`.

   :param kwargs: named parameters to pass into
                  web protocol.

   Supported *kwargs*:

   :param bool tcp_keepalive: Enable TCP Keep-Alive. Default: ``True``.
   :param int keepalive_timeout: Number of seconds before closing Keep-Alive
        connection. Default: ``3630`` seconds (when deployed behind a reverse proxy
        it's important for this value to be higher than the proxy's timeout. To avoid
        race conditions we always want the proxy to close the connection).
   :param logger: Custom logger object. Default:
        :data:`aiohttp.log.server_logger`.
   :param access_log: Custom logging object. Default:
        :data:`aiohttp.log.access_logger`.
   :param access_log_class: Class for `access_logger`. Default:
        :data:`aiohttp.helpers.AccessLogger`.
        Must to be a subclass of :class:`aiohttp.abc.AbstractAccessLogger`.
   :param str access_log_format: Access log format string. Default:
        :attr:`helpers.AccessLogger.LOG_FORMAT`.
   :param int max_line_size: Optional maximum header line size. Default:
        ``8190``.
   :param int max_field_size: Optional maximum header field size. Default:
        ``8190``.

   :param float lingering_time: Maximum time during which the server
        reads and ignores additional data coming from the client when
        lingering close is on.  Use ``0`` to disable lingering on
        server channel closing.
   :param int read_bufsize: Size of the read buffer (:attr:`BaseRequest.content`).
                            ``None`` by default,
                            it means that the session global value is used.

      .. versionadded:: 3.7
   :param bool auto_decompress: Automatically decompress request body,
      ``True`` by default.

      .. versionadded:: 3.8



   .. attribute:: app

      Read-only attribute for accessing to :class:`Application` served
      instance.

   .. method:: setup()
      :async:

      Initialize application. Should be called before adding sites.

      The method calls :attr:`Application.on_startup` registered signals.

   .. method:: cleanup()
      :async:

      Stop handling all registered sites and cleanup used resources.

      :attr:`Application.on_shutdown` and
      :attr:`Application.on_cleanup` signals are called internally.


.. class:: ServerRunner(web_server, *, handle_signals=False, **kwargs)

   A runner for low-level :class:`Server`. Used with conjunction with sites
   to serve on specific port.

   Inherited from :class:`BaseRunner`.

   :param Server web_server: low-level web server instance to serve.

   :param bool handle_signals: add signal handlers for
                               :data:`signal.SIGINT` and
                               :data:`signal.SIGTERM` (``False`` by
                               default). These handlers will raise
                               :exc:`GracefulExit`.

   :param kwargs: named parameters to pass into
                  web protocol.

   .. seealso::

      :ref:`aiohttp-web-lowlevel` demonstrates low-level server usage

.. class:: BaseSite

   An abstract class for handled sites.

   .. attribute:: name

      An identifier for site, read-only :class:`str` property. Could
      be a handled URL or UNIX socket path.

   .. method:: start()
      :async:

      Start handling a site.

   .. method:: stop()
      :async:

      Stop handling a site.


.. class:: TCPSite(runner, host=None, port=None, *, \
                   shutdown_timeout=60.0, ssl_context=None, \
                   backlog=128, reuse_address=None, \
                   reuse_port=None)

   Serve a runner on TCP socket.

   :param runner: a runner to serve.

   :param str host: HOST to listen on, all interfaces if ``None`` (default).

   :param int port: PORT to listed on, ``8080`` if ``None`` (default).

   :param float shutdown_timeout: a timeout used for both waiting on pending
                                  tasks before application shutdown and for
                                  closing opened connections on
                                  :meth:`BaseSite.stop` call.

   :param ssl_context: a :class:`ssl.SSLContext` instance for serving
                       SSL/TLS secure server, ``None`` for plain HTTP
                       server (default).

   :param int backlog: a number of unaccepted connections that the
                       system will allow before refusing new
                       connections, see :meth:`socket.socket.listen` for details.

                       ``128`` by default.

   :param bool reuse_address: tells the kernel to reuse a local socket in
                              TIME_WAIT state, without waiting for its
                              natural timeout to expire. If not specified
                              will automatically be set to True on UNIX.

   :param bool reuse_port: tells the kernel to allow this endpoint to be
                           bound to the same port as other existing
                           endpoints are bound to, so long as they all set
                           this flag when being created. This option is not
                           supported on Windows.

.. class:: UnixSite(runner, path, *, \
                   shutdown_timeout=60.0, ssl_context=None, \
                   backlog=128)

   Serve a runner on UNIX socket.

   :param runner: a runner to serve.

   :param str path: PATH to UNIX socket to listen.

   :param float shutdown_timeout: a timeout used for both waiting on pending
                                  tasks before application shutdown and for
                                  closing opened connections on
                                  :meth:`BaseSite.stop` call.

   :param ssl_context: a :class:`ssl.SSLContext` instance for serving
                       SSL/TLS secure server, ``None`` for plain HTTP
                       server (default).

   :param int backlog: a number of unaccepted connections that the
                       system will allow before refusing new
                       connections, see :meth:`socket.socket.listen` for details.

                       ``128`` by default.

.. class:: NamedPipeSite(runner, path, *, shutdown_timeout=60.0)

   Serve a runner on Named Pipe in Windows.

   :param runner: a runner to serve.

   :param str path: PATH of named pipe to listen.

   :param float shutdown_timeout: a timeout used for both waiting on pending
                                  tasks before application shutdown and for
                                  closing opened connections on
                                  :meth:`BaseSite.stop` call.

.. class:: SockSite(runner, sock, *, \
                   shutdown_timeout=60.0, ssl_context=None, \
                   backlog=128)

   Serve a runner on UNIX socket.

   :param runner: a runner to serve.

   :param sock: A :ref:`socket instance <socket-objects>` to listen to.

   :param float shutdown_timeout: a timeout used for both waiting on pending
                                  tasks before application shutdown and for
                                  closing opened connections on
                                  :meth:`BaseSite.stop` call.

   :param ssl_context: a :class:`ssl.SSLContext` instance for serving
                       SSL/TLS secure server, ``None`` for plain HTTP
                       server (default).

   :param int backlog: a number of unaccepted connections that the
                       system will allow before refusing new
                       connections, see :meth:`socket.socket.listen` for details.

                       ``128`` by default.

.. exception:: GracefulExit

   Raised by signal handlers for :data:`signal.SIGINT` and :data:`signal.SIGTERM`
   defined in :class:`AppRunner` and :class:`ServerRunner`
   when ``handle_signals`` is set to ``True``.

   Inherited from :exc:`SystemExit`,
   which exits with error code ``1`` if not handled.


Utilities
---------

.. class:: FileField

   A :mod:`dataclass <dataclasses>` instance that is returned as
   multidict value by :meth:`aiohttp.web.BaseRequest.post` if field is uploaded file.

   .. attribute:: name

      Field name

   .. attribute:: filename

      File name as specified by uploading (client) side.

   .. attribute:: file

      An :class:`io.IOBase` instance with content of uploaded file.

   .. attribute:: content_type

      *MIME type* of uploaded file, ``'text/plain'`` by default.

   .. seealso:: :ref:`aiohttp-web-file-upload`


.. function:: run_app(app, *, debug=False, host=None, port=None, \
                      path=None, sock=None, shutdown_timeout=60.0, \
                      keepalive_timeout=3630, ssl_context=None, \
                      print=print, backlog=128, \
                      access_log_class=aiohttp.helpers.AccessLogger, \
                      access_log_format=aiohttp.helpers.AccessLogger.LOG_FORMAT, \
                      access_log=aiohttp.log.access_logger, \
                      handle_signals=True, \
                      reuse_address=None, \
                      reuse_port=None, \
                      handler_cancellation=False)

   A high-level function for running an application, serving it until
   keyboard interrupt and performing a
   :ref:`aiohttp-web-graceful-shutdown`.

   This is a high-level function very similar to :func:`asyncio.run` and
   should be used as the main entry point for an application. The
   :class:`Application` object essentially becomes our `main()` function.
   If additional tasks need to be run in parallel, see
   :ref:`aiohttp-web-complex-applications`.

   The server will listen on any host or Unix domain socket path you supply.
   If no hosts or paths are supplied, or only a port is supplied, a TCP server
   listening on 0.0.0.0 (all hosts) will be launched.

   Distributing HTTP traffic to multiple hosts or paths on the same
   application process provides no performance benefit as the requests are
   handled on the same event loop. See :doc:`deployment` for ways of
   distributing work for increased performance.

   :param app: :class:`Application` instance to run or a *coroutine*
               that returns an application.

   :param bool debug: enable :ref:`asyncio debug mode <asyncio-debug-mode>` if ``True``.

   :param str host: TCP/IP host or a sequence of hosts for HTTP server.
                    Default is ``'0.0.0.0'`` if *port* has been specified
                    or if *path* is not supplied.

   :param int port: TCP/IP port for HTTP server. Default is ``8080`` for plain
                    text HTTP and ``8443`` for HTTP via SSL (when
                    *ssl_context* parameter is specified).

   :param path: file system path for HTTP server Unix domain socket.
                    A sequence of file system paths can be used to bind
                    multiple domain sockets. Listening on Unix domain
                    sockets is not supported by all operating systems,
                    :class:`str`, :class:`pathlib.Path` or an iterable of these.

   :param socket.socket sock: a preexisting socket object to accept connections on.
                       A sequence of socket objects can be passed.

   :param int shutdown_timeout: a delay to wait for graceful server
                                shutdown before disconnecting all
                                open client sockets hard way.

                                This is used as a delay to wait for
                                pending tasks to complete and then
                                again to close any pending connections.

                                A system with properly
                                :ref:`aiohttp-web-graceful-shutdown`
                                implemented never waits for the second
                                timeout but closes a server in a few
                                milliseconds.

   :param float keepalive_timeout: a delay before a TCP connection is
                                   closed after a HTTP request. The delay
                                   allows for reuse of a TCP connection.

                                   When deployed behind a reverse proxy
                                   it's important for this value to be
                                   higher than the proxy's timeout. To avoid
                                   race conditions, we always want the proxy
                                   to handle connection closing.

      .. versionadded:: 3.8

   :param ssl_context: :class:`ssl.SSLContext` for HTTPS server,
                       ``None`` for HTTP connection.

   :param print: a callable compatible with :func:`print`. May be used
                 to override STDOUT output or suppress it. Passing `None`
                 disables output.

   :param int backlog: the number of unaccepted connections that the
                       system will allow before refusing new
                       connections (``128`` by default).

   :param access_log_class: class for `access_logger`. Default:
                            :data:`aiohttp.helpers.AccessLogger`.
                            Must to be a subclass of :class:`aiohttp.abc.AbstractAccessLogger`.

   :param access_log: :class:`logging.Logger` instance used for saving
                      access logs. Use ``None`` for disabling logs for
                      sake of speedup.

   :param access_log_format: access log format, see
                             :ref:`aiohttp-logging-access-log-format-spec`
                             for details.

   :param bool handle_signals: override signal TERM handling to gracefully
                               exit the application.

   :param bool reuse_address: tells the kernel to reuse a local socket in
                              TIME_WAIT state, without waiting for its
                              natural timeout to expire. If not specified
                              will automatically be set to True on UNIX.

   :param bool reuse_port: tells the kernel to allow this endpoint to be
                           bound to the same port as other existing
                           endpoints are bound to, so long as they all set
                           this flag when being created. This option is not
                           supported on Windows.

   :param bool handler_cancellation: cancels the web handler task if the client
                                     drops the connection. This is recommended
                                     if familiar with asyncio behavior or
                                     scalability is a concern.
                                     :ref:`aiohttp-web-peer-disconnection`

   .. versionadded:: 3.0

      Support *access_log_class* parameter.

      Support *reuse_address*, *reuse_port* parameter.

   .. versionadded:: 3.1

      Accept a coroutine as *app* parameter.

   .. versionadded:: 3.9

      Support handler_cancellation parameter (this was the default behavior
      in aiohttp <3.7).

Constants
---------

.. class:: ContentCoding

   An :class:`enum.Enum` class of available Content Codings.

   .. attribute:: deflate

      *DEFLATE compression*

   .. attribute:: gzip

      *GZIP compression*

   .. attribute:: identity

      *no compression*


Middlewares
-----------

.. function:: normalize_path_middleware(*, \
                                        append_slash=True, \
                                        remove_slash=False, \
                                        merge_slashes=True, \
                                        redirect_class=HTTPPermanentRedirect)

   Middleware factory which produces a middleware that normalizes
   the path of a request. By normalizing it means:

     - Add or remove a trailing slash to the path.
     - Double slashes are replaced by one.

   The middleware returns as soon as it finds a path that resolves
   correctly. The order if both merge and append/remove are enabled is:

     1. *merge_slashes*
     2. *append_slash* or *remove_slash*
     3. both *merge_slashes* and *append_slash* or *remove_slash*

   If the path resolves with at least one of those conditions, it will
   redirect to the new path.

   Only one of *append_slash* and *remove_slash* can be enabled. If both are
   ``True`` the factory will raise an ``AssertionError``

   If *append_slash* is ``True`` the middleware will append a slash when
   needed. If a resource is defined with trailing slash and the request
   comes without it, it will append it automatically.

   If *remove_slash* is ``True``, *append_slash* must be ``False``. When enabled
   the middleware will remove trailing slashes and redirect if the resource is
   defined.

   If *merge_slashes* is ``True``, merge multiple consecutive slashes in the
   path into one.

   .. versionadded:: 3.4

      Support for *remove_slash*
````

## File: docs/web.rst
````
.. _aiohttp-web:

Server
======

.. module:: aiohttp.web

The page contains all information about aiohttp Server API:


.. toctree::
   :name: server
   :maxdepth: 3

   Tutorial <https://demos.aiohttp.org>
   Quickstart <web_quickstart>
   Advanced Usage <web_advanced>
   Low Level <web_lowlevel>
   Reference <web_reference>
   Web Exceptions <web_exceptions>
   Logging <logging>
   Testing <testing>
   Deployment <deployment>
````

## File: docs/websocket_utilities.rst
````
.. currentmodule:: aiohttp


WebSocket utilities
===================

.. class:: WSCloseCode

    An :class:`~enum.IntEnum` for keeping close message code.

    .. attribute:: OK

       A normal closure, meaning that the purpose for
       which the connection was established has been fulfilled.

    .. attribute:: GOING_AWAY

       An endpoint is "going away", such as a server
       going down or a browser having navigated away from a page.

    .. attribute:: PROTOCOL_ERROR

       An endpoint is terminating the connection due
       to a protocol error.

    .. attribute:: UNSUPPORTED_DATA

       An endpoint is terminating the connection
       because it has received a type of data it cannot accept (e.g., an
       endpoint that understands only text data MAY send this if it
       receives a binary message).

    .. attribute:: INVALID_TEXT

       An endpoint is terminating the connection
       because it has received data within a message that was not
       consistent with the type of the message (e.g., non-UTF-8 :rfc:`3629`
       data within a text message).

    .. attribute:: POLICY_VIOLATION

       An endpoint is terminating the connection because it has
       received a message that violates its policy.  This is a generic
       status code that can be returned when there is no other more
       suitable status code (e.g.,
       :attr:`~aiohttp.WSCloseCode.UNSUPPORTED_DATA` or
       :attr:`~aiohttp.WSCloseCode.MESSAGE_TOO_BIG`) or if there is a need to
       hide specific details about the policy.

    .. attribute:: MESSAGE_TOO_BIG

       An endpoint is terminating the connection
       because it has received a message that is too big for it to
       process.

    .. attribute:: MANDATORY_EXTENSION

       An endpoint (client) is terminating the
       connection because it has expected the server to negotiate one or
       more extension, but the server did not return them in the response
       message of the WebSocket handshake.  The list of extensions that
       are needed should appear in the /reason/ part of the Close frame.
       Note that this status code is not used by the server, because it
       can fail the WebSocket handshake instead.

    .. attribute:: INTERNAL_ERROR

       A server is terminating the connection because
       it encountered an unexpected condition that prevented it from
       fulfilling the request.

    .. attribute:: SERVICE_RESTART

       The service is restarted. a client may reconnect, and if it
       chooses to do, should reconnect using a randomized delay of 5-30s.

    .. attribute:: TRY_AGAIN_LATER

       The service is experiencing overload. A client should only
       connect to a different IP (when there are multiple for the
       target) or reconnect to the same IP upon user action.

    .. attribute:: ABNORMAL_CLOSURE

       Used to indicate that a connection was closed abnormally
       (that is, with no close frame being sent) when a status code
       is expected.

    .. attribute:: BAD_GATEWAY

       The server was acting as a gateway or proxy and received
       an invalid response from the upstream server.
       This is similar to 502 HTTP Status Code.


.. class:: WSMsgType

   An :class:`~enum.IntEnum` for describing :class:`WSMessage` type.

   .. attribute:: CONTINUATION

      A mark for continuation frame, user will never get the message
      with this type.

   .. attribute:: TEXT

      Text message, the value has :class:`str` type.

   .. attribute:: BINARY

      Binary message, the value has :class:`bytes` type.

   .. attribute:: PING

      Ping frame (sent by client peer).

   .. attribute:: PONG

      Pong frame, answer on ping. Sent by server peer.

   .. attribute:: CLOSE

      Close frame.

   .. attribute:: CLOSED FRAME

      Actually not frame but a flag indicating that websocket was
      closed.

   .. attribute:: ERROR

      Actually not frame but a flag indicating that websocket was
      received an error.


.. class:: WSMessage

   Websocket message, returned by ``.receive()`` calls. This is actually defined as a
   :class:`typing.Union` of different message types. All messages are a
   :func:`collections.namedtuple` with the below attributes.

   .. attribute:: data

      Message payload.

      1. :class:`str` for :attr:`WSMsgType.TEXT` messages.

      2. :class:`bytes` for :attr:`WSMsgType.BINARY` messages.

      3. :class:`int` (see :class:`WSCloseCode` for common codes)
         for :attr:`WSMsgType.CLOSE` messages.

      4. :class:`bytes` for :attr:`WSMsgType.PING` messages.

      5. :class:`bytes` for :attr:`WSMsgType.PONG` messages.

      6. :class:`Exception` for :attr:`WSMsgType.ERROR` messages.

   .. attribute:: extra

      Additional info, :class:`str` if provided, otherwise defaults to ``None``.

      Makes sense only for :attr:`WSMsgType.CLOSE` messages, contains
      optional message description.

   .. attribute:: type

      Message type, :class:`WSMsgType` instance.

   .. method:: json(*, loads=json.loads)

      Returns parsed JSON data (the method is only present on :attr:`WSMsgType.TEXT`
      and :attr:`WSMsgType.BINARY` messages).

      :param loads: optional JSON decoder function.
````

## File: docs/whats_new_1_1.rst
````
=========================
What's new in aiohttp 1.1
=========================


YARL and URL encoding
======================

Since aiohttp 1.1 the library uses :term:`yarl` for URL processing.

New API
-------

:class:`yarl.URL` gives handy methods for URL operations etc.

Client API still accepts :class:`str` everywhere *url* is used,
e.g. ``session.get('http://example.com')`` works as well as
``session.get(yarl.URL('http://example.com'))``.

Internal API has been switched to :class:`yarl.URL`.
:class:`aiohttp.CookieJar` accepts :class:`~yarl.URL` instances only.

On server side has added :attr:`aiohttp.web.BaseRequest.url` and
:attr:`aiohttp.web.BaseRequest.rel_url` properties for representing relative and
absolute request's URL.

URL using is the recommended way, already existed properties for
retrieving URL parts are deprecated and will be eventually removed.

Redirection web exceptions accepts :class:`yarl.URL` as *location*
parameter. :class:`str` is still supported and will be supported forever.

Reverse URL processing for *router* has been changed.

The main API is ``aiohttp.web.Request.url_for``
which returns a :class:`yarl.URL` instance for named resource. It
does not support *query args* but adding *args* is trivial:
``request.url_for('named_resource', param='a').with_query(arg='val')``.

The method returns a *relative* URL, absolute URL may be constructed by
``request.url.join(request.url_for(...)`` call.


URL encoding
------------

YARL encodes all non-ASCII symbols on :class:`yarl.URL` creation.

Thus ``URL('https://www.python.org/путь')`` becomes
``'https://www.python.org/%D0%BF%D1%83%D1%82%D1%8C'``.

On filling route table it's possible to use both non-ASCII and percent
encoded paths::

   app.router.add_get('/путь', handler)

and::

   app.router.add_get('/%D0%BF%D1%83%D1%82%D1%8C', handler)

are the same. Internally ``'/путь'`` is converted into
percent-encoding representation.

Route matching also accepts both URL forms: raw and encoded by
converting the route pattern to *canonical* (encoded) form on route
registration.


Sub-Applications
================

Sub applications are designed for solving the problem of the big
monolithic code base.
Let's assume we have a project with own business logic and tools like
administration panel and debug toolbar.

Administration panel is a separate application by its own nature but all
toolbar URLs are served by prefix like ``/admin``.

Thus we'll create a totally separate application named ``admin`` and
connect it to main app with prefix::

   admin = web.Application()
   # setup admin routes, signals and middlewares

   app.add_subapp('/admin/', admin)

Middlewares and signals from ``app`` and ``admin`` are chained.

It means that if URL is ``'/admin/something'`` middlewares from
``app`` are applied first and ``admin.middlewares`` are the next in
the call chain.

The same is going for
:attr:`~aiohttp.web.Application.on_response_prepare` signal -- the
signal is delivered to both top level ``app`` and ``admin`` if
processing URL is routed to ``admin`` sub-application.

Common signals like :attr:`~aiohttp.web.Application.on_startup`,
:attr:`~aiohttp.web.Application.on_shutdown` and
:attr:`~aiohttp.web.Application.on_cleanup` are delivered to all
registered sub-applications. The passed parameter is sub-application
instance, not top-level application.


Third level sub-applications can be nested into second level ones --
there are no limitation for nesting level.


Url reversing
-------------

Url reversing for sub-applications should generate urls with proper prefix.

But for getting URL sub-application's router should be used::

   admin = web.Application()
   admin.add_get('/resource', handler, name='name')

   app.add_subapp('/admin/', admin)

   url = admin.router['name'].url_for()

The generated ``url`` from example will have a value
``URL('/admin/resource')``.

Application freezing
====================

Application can be used either as main app (``app.make_handler()``) or as
sub-application -- not both cases at the same time.

After connecting application by ``.add_subapp()`` call or starting
serving web-server as toplevel application the application is
**frozen**.

It means that registering new routes, signals and middlewares is
forbidden.  Changing state (``app['name'] = 'value'``) of frozen application is
deprecated and will be eventually removed.
````

## File: docs/whats_new_3_0.rst
````
.. _aiohttp_whats_new_3_0:

=========================
What's new in aiohttp 3.0
=========================

async/await everywhere
======================

The main change is dropping ``yield from`` support and using
``async``/``await`` everywhere. Farewell, Python 3.4.

The minimal supported Python version is **3.5.3** now.

Why not *3.5.0*?  Because *3.5.3* has a crucial change:
:func:`asyncio.get_event_loop()` returns the running loop instead of
*default*, which may be different, e.g.::

    loop = asyncio.new_event_loop()
    loop.run_until_complete(f())

Note, :func:`asyncio.set_event_loop` was not called and default loop
is not equal to actually executed one.

Application Runners
===================

People constantly asked about ability to run aiohttp servers together
with other asyncio code, but :func:`aiohttp.web.run_app` is blocking
synchronous call.

aiohttp had support for starting the application without ``run_app`` but the API
was very low-level and cumbersome.

Now application runners solve the task in a few lines of code, see
:ref:`aiohttp-web-app-runners` for details.

Client Tracing
==============

Other long awaited feature is tracing client request life cycle to
figure out when and why client request spends a time waiting for
connection establishment, getting server response headers etc.

Now it is possible by registering special signal handlers on every
request processing stage.  :ref:`aiohttp-client-tracing` provides more
info about the feature.

HTTPS support
=============

Unfortunately asyncio has a bug with checking SSL certificates for
non-ASCII site DNS names, e.g. `https://историк.рф <https://историк.рф>`_ or
`https://雜草工作室.香港 <https://雜草工作室.香港>`_.

The bug has been fixed in upcoming Python 3.7 only (the change
requires breaking backward compatibility in :mod:`ssl` API).

aiohttp installs a fix for older Python versions (3.5 and 3.6).


Dropped obsolete API
====================

A switch to new major version is a great chance for dropping already
deprecated features.

The release dropped a lot, see :ref:`aiohttp_changes` for details.

All removals was already marked as deprecated or related to very low
level implementation details.

If user code did not raise :exc:`DeprecationWarning` it is compatible
with aiohttp 3.0 most likely.


Summary
=======

Enjoy aiohttp 3.0 release!

The full change log is here: :ref:`aiohttp_changes`.
````
