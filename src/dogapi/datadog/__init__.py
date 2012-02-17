from dogapi.datadog.base import BaseDatadog
from dogapi.datadog.metrics import MetricApi
from dogapi.datadog.events import EventApi
from dogapi.datadog.dashes import DashApi
from dogapi.datadog.infrastructure import InfrastructureApi



class Datadog(BaseDatadog, MetricApi, EventApi, DashApi, InfrastructureApi):
    """
    A high-level client for interacting with the Datadog API.

    By default, service calls to the simple client silently swallow any exceptions
    before they escape from the library. To disable this behavior, simply set the
    `swallow` attribute of your :class:`~dogapi.Datadog` instance to `False`.

    The default timeout is 2 seconds, but that can be changed by setting the
    client's `timeout` attribute.
    """



