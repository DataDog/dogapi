:mod:`dogapi.v1` - full clients for lower-level API access
==========================================================

.. py:module:: dogapi.v1

The full clients are a thin wrapper on top of the HTTP API documented at:

https://github.com/DataDog/dogapi/wiki

They return the Python object that results from deserializing the HTTP API's
JSON response. In the case of a blank body, they return an empty dict.

.. autoclass:: ClusterService
   :members:
.. autoclass:: CommentService
   :members:
.. autoclass:: DashService
   :members:
.. autoclass:: EventService
   :members:
.. autoclass:: MetricService
   :members:
.. autoclass:: SearchService
   :members:
