%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
:mod:`dogapi` --- DataDog's Python API
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

.. module:: dogapi


The :mod:`dogapi` module provides :class:`DogHttpApi` - a simple wrapper around
DataDog's HTTP API - and :class:`~dogapi.stats.DogStatsApi` - a tool for collecting metrics
in high performance applications.


DogHttpApi
==========

DogHttpApi is a Python client library for DataDog's `HTTP API <http://api.datadoqhq.com>`_.


.. autoclass:: dogapi.http.DogHttpApi
    :members:
    :inherited-members:
    :exclude-members: __init__

DogStatsApi
===========

.. automodule:: dogapi.stats.dog_stats_api

.. autoclass::  dogapi.stats.DogStatsApi

    .. method:: start(api_key=api_key, flush_interval=10, flush_in_thread=True, flush_in_greenlet=False)

        Begin flushing metrics with your account's *api_key* every
        *flush_interval* seconds. By default, metrics will be flushed in
        a seperate thread. ::

        >>> dog_stats_api.start(api_key='my_api_key')

        If you're running a gevent server and want to flush metrics in a
        greenlet, set *flush_in_greenlet* to True. Be sure to import and monkey
        patch gevent before starting dog_stats_api. ::

        >>> from gevent import monkey; monkey.patch_all()
        >>> dog_stats_api.start(api_key='my_api_key', flush_in_greelet=True)

    .. automethod:: gauge

    .. automethod:: increment

    .. automethod:: histogram

    .. automethod:: timed


.. module:: dogapi
.. data:: dog_stats_api

    A global :class:`~dogapi.stats.DogStatsApi` instance that is easily shared
    across an application's modules. Initialize this once in your application's
    set-up code and then other modules can import and use it without further
    configuration.

    >>> from dogapi import dog_stats_api
    >>> dog_stats_api.start(api_key='my_api_key')


Here's an example that put's it all together. ::

    # Import the dog stats instance.
    from dogapi import dog_stats_api as dog

    # Begin flushing asynchronously with the given api key. After this is done
    # once in your application, other modules can import and use dog_stats_api
    # without any further configuration.
    dog.start(api_key='my_api_key')


    @dog.timed('home_page.render.time')
    def render_home_page(user_id):
        """ Render the home page for the given user. """

        # Fetch the user from the cache or the database
        # and record metrics on our cache hits and misses.
        user = user_cache.get(user_id)
        if user:
            dog.increment('user_cache.hit')
        else:
            dog.increment('user_cache.miss')
            user = user_database.get(user_id)

        return render('home.html', user_id)

Contact
=======

If you have any questions or suggestions, get in touch at datadoghq.com.
