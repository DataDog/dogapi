from dogapi.http.base import *
from dogapi.http.metrics import *
from dogapi.http.events import *
from dogapi.http.dashes import *
from dogapi.http.infrastructure import *


class DogHttpApi(BaseDatadog, HttpMetricApi, EventApi, DashApi, InfrastructureApi):
    """
    A high-level client for interacting with the Datadog API.

    By default, service calls to the simple client silently swallow any exceptions
    before they escape from the library. To disable this behavior, simply set the
    `swallow` attribute of your :class:`~dogapi.Datadog` instance to `False`.

    The default timeout is 2 seconds, but that can be changed by setting the
    client's `timeout` attribute.
    """

