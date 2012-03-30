:class:`~dogapi.dogstats.DogStatsApi` - High performance application instrumentation
===============================================================

.. py:module:: dogapi

DogStatsApi collects application metrics and asynchronously flushes them to
DataDog's HTTP API, so it can be used without adversely affecting your
application's performance.

.. autoclass:: dogapi.stats.DogStatsApi

   .. automethod:: start
   .. automethod:: gauge
   .. automethod:: increment
   .. automethod:: histogram
   .. automethod:: timed
