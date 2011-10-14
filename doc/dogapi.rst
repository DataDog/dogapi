:mod:`dogapi` - "Simple" client for easy, high-level API access
===============================================================

.. py:module:: dogapi

Contents:

.. data:: dog

    An instantiated, ready-to-use :class:`~dogapi.SimpleClient`.

.. autoclass:: SimpleClient

   .. automethod:: metric
   .. automethod:: metrics

   .. automethod:: comment
   .. automethod:: delete_comment

   .. automethod:: stream
   .. automethod:: get_event
   .. automethod:: event

   .. automethod:: all_clusters
   .. automethod:: host_clusters
   .. automethod:: add_clusters
   .. automethod:: change_clusters
   .. automethod:: detatch_clusters

   .. automethod:: dashboard
   .. automethod:: create_dashboard
   .. automethod:: update_dashboard
   .. automethod:: delete_dashboard

   .. automethod:: search
