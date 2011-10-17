Getting started with :mod:`dogapi`
======================================

Dogapi has two layers. For many uses, the simple client is sufficient.
For more robust use cases, you can dig a bit deeper and instantiate the
full blown client services. 

First, let's take a look at how you would post a comment to the stream
with the simple client.


    >>> from dogapi import dog
    >>> dog.api_key = 'your_orgs_api_key'
    >>> dog.application_key = 'your_application_key'
    >>> dog.comment('matt', 'hello dogapi')
    1234


The simple client is available as an already instantiated, ready-to-go client
called :class:`~dogapi.dog` in :mod:`dogapi`, and has methods for all the basic
API actions.

.. note::

    Be careful, :class:`~dogapi.dog` is not inherently threadsafe. If you're
    using the API in a multi-threaded environment, you're probbaly safer
    creating your own :class:`~dogapi.SimpleClient` instances and managing them
    yourself.

After importing the :class:`~dogapi.dog`, we quickly configure it with
our account's API key and an appropriate application key, and
we're ready to roll. (Some API commands only require reporting
permissions. That means they only need an API key. For them, you can
just omit the application key.)

Last, we post a comment from user "matt" with the message "hello dogapi". If
the commnet is posted successfully, the result is the unique ID of the comment,
which can be used to modify or delete the comment later.

Defensive by design
===================

The simple client is designed defensively, to be safe by default. The simple
client is built with aggressive default timeouts, and is designed to suppress
exceptions rather than letting them escape from the library and potentially
interfere with surrounding code. This tradeoff comes at a cost. With default
settings, the simple client can fail silently, and will assume Datadog is down
(and stop sending requests) if too many timeouts occur. This allows you to
experiment with the client with confidence, but may ultimately be less than ideal.

When you're ready to get your hands dirty, you can disable the defensive defaults
and start handling exceptions and timeouts programmatically. See full
documentation for the :class:`~dogapi.SimpleClient` for details.
