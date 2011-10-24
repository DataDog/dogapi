:mod:`dogapi` - "Simple" client for easy, high-level API access
===============================================================

.. py:module:: dogapi

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

   .. automethod:: all_tags
   .. automethod:: host_tags
   .. automethod:: add_tags
   .. automethod:: change_tags
   .. automethod:: detatch_tags

   .. automethod:: dashboard
   .. automethod:: create_dashboard
   .. automethod:: update_dashboard
   .. automethod:: delete_dashboard

   .. automethod:: search
