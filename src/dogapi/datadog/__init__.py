from dogapi.datadog.base import *
from dogapi.datadog.metrics import *
from dogapi.datadog.events import *
from dogapi.datadog.dashes import *
from dogapi.datadog.infrastructure import *
from dogapi.datadog.submitter import *



class Datadog(BaseDatadog, HttpMetricApi, EventApi, DashApi, InfrastructureApi,
                SynchronousSubmitter):
    """
    A high-level client for interacting with the Datadog API.

    By default, service calls to the simple client silently swallow any exceptions
    before they escape from the library. To disable this behavior, simply set the
    `swallow` attribute of your :class:`~dogapi.Datadog` instance to `False`.

    The default timeout is 2 seconds, but that can be changed by setting the
    client's `timeout` attribute.
    """


class StatsdDatadog(BaseDatadog, StatsdMetricApi, EventApi, DashApi,
                                InfrastructureApi, SynchronousSubmitter):
    """ Same as the Datadog client, except sends metrics to a statsd
        instance which will aggregate multiple requests and send to
        Datadog instead of directly to Datadog.
    """

