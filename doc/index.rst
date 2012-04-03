%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
:mod:`dogapi` --- DataDog's Python API
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

.. module:: dogapi


The :mod:`dogapi` module provides :class:`DogHttpApi` - a simple wrapper around
DataDog's HTTP API - and :class:`~dogapi.stats.DogStatsApi` - a tool for collecting metrics
in high performance applications.

DogStatsApi
===========

DogStatsApi is a tool for collecting application metrics without hindering
performance. It collects metrics in the application thread with very little overhead
(it just writes them to a `Queue <http://docs.python.org/library/queue.html>`_
with an aggressive timeout). The aggregation and network access is performed in another
thread to ensure the instrumentation doesn't block your application's real work.


.. class:: dogapi.stats.DogStatsApi

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

    .. method:: gauge(metric_name, value, timestamp=None)

        Record the instantaneous *value* of a metric. They most recent value in
        a given flush interval will be recorded.

        >>> dog_stats_api.gauge('process.uptime', time.time() - process_start_time)
        >>> dog_stats_api.gauge('cache.bytes.free', cache.get_free_bytes())

    .. method:: increment(metric_name, value=1, timestamp=None)

        Increment the counter value of the given metric.

        >>> dog_stats_api.increment('home.page.hits')
        >>> dog_stats_api.increment('bytes.processed', file.size())

    .. method:: histogram(metric_name, value, timestamp=None)

        Sample a histogram value. Histograms will produce metrics that
        describe the distribution of the recorded values, namely the minimum,
        maximum, average, count and the 75th, 85th, 95th and 99th percentiles.

        >>> dog_stats_api.histogram('uploaded_file.size', uploaded_file.size())

    .. method:: timed (metric_name)

        A decorator that will track the distribution of a function's run time.
        ::

            @dog_stats_api.timed('user.query.time')
            def get_user(user_id):
                # Do what you need to ...
                pass

            # Is equivalent to ...
            start = time.time()
            try:
                get_user(user_id)
            finally:
                dog_stats_api.histogram('user.query.time', time.time() - start)

.. data:: dog_stats_api

    A global :class:`~dogapi.stats.DogStatsApi` instance that is easily shared
    across an application's modules. Initialize this once in your application's
    set-up code and then other modules can import and use it without further
    configuration.

    >>> from dogapi import dog_stats_api
    >>> dog_stats_api.start(api_key='my_api_key')


Here's an example that put's it all together. ::

    # Import the dog stats instance.
    from dogapi import dog_stats_api

    # Begin flushing asynchronously with the given api key. After this is done
    # once in your application, other modules can import and use dog_stats_api
    # without any further configuration.
    dog_stats_api.start(api_key='my_api_key')


    @dog_stats_api.timed('home_page.render.time')
    def render_home_page(user_id):
        """ Render the home page for the given user. """

        # Fetch the user from the cache or the database
        # and record metrics on our cache hits and misses.
        user = user_cache.get(user_id)
        if user:
            dog_stats_api.increment('user_cache.hit')
        else:
            dog_stats_api.increment('user_cache.miss')
            user = user_database.get(user_id)

        return render('home.html', user_id)

Contact
=======

If you have any questions or suggestions, get in touch at datadoghq.com.
