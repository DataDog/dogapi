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
    >>> resp = dog.comment('matt', 'hello dogapi')
    >>> print resp
    {u'comment': {u'message': u'hello dogapi', u'handle': u'matt', u'id': 1395}}


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

Last, we post a comment from user "matt" with the message "hello dogapi". We
capture the response, which is simply the decoded JSON of the underlying HTTP
response. Here, with a successful action, it's mostly just the information we
submitted reflected back at us, but with the addition of a unique id that we can
use to reference the comment in the future (for example, to edit or delete it).
