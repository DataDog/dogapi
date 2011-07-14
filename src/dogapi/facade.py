"""
Simple client-side wrapper for Datadog API clients
Provides one-line, object-less events and metrics submission
See event.py and metric.py for the underlying, thicker clients.

Usage examples: 

import dogapi
from datetime import datetime as dt

dog = dogapi.init('replace_this_with_your_api_key', 'my_host', 'my_device')
dog.emit_point('x.myorg.mymetric', 4.0)
dog.emit_point('x.myorg.mymetric', 5.0, dt(2010,12,31), host='another_host')

or 

dog = dogapi.init('replace_this_with_your_api_key')
dog.emit_points('x.myorg.mymetric', [(dt(2010,12,30), 99.0), (dt(2010,12,31), 99.9)])

"""
from contextlib import contextmanager

from datetime import datetime as dt
from dogapi.common import find_datadog_host, find_api_key, Scope
from dogapi.metric import MetricService
from dogapi.event import EventService, Event

class Client(object):
    """Thin, flat client to Datadog APIs"""

    def __init__(self, api_key=None, host=None, device=None, 
                 datadog_host=None):
        """ Client c'tor - automatically detects API_Key and Datadog Server
            Use dogapi.init() instead
        """
        # determine which api_key to use
        self.api_key = api_key

        # which datadog service host to connect to
        self.datadog_host = datadog_host or find_datadog_host()

        # store optional default host / device context
        self.host = host
        self.device = device
        
        # and get the underlying services to communicate with the server
        self.metric_svc = MetricService(self.datadog_host)
        self.event_svc = EventService(self.datadog_host)

    def _override_scope(self, host, device):
        if host:    h = host 
        else:       h = self.host
        if device:  d = device
        else:       d = self.device
        return Scope(h, d)
    
    def emit_point(self, metric, value, timestamp=None, host=None, device=None):
        """ Emits one metric point to Datadog
            - metric:       name of the metric issued e.g. "x.datadog.perf.series_count"
            - value:        data point to be issued, as a float
            - timestamp:    time coordinate, as a datetime. Optional. Defaults to now()
            - host:         name of the host to use as metric context. Optional.
            - device:       name of the device to use as metric context. Optional.
        """
        if not self.api_key:
            return
            
        timestamp = timestamp or dt.now()
        return self.emit_points(metric, [(timestamp, value)], host, device)
    
    def emit_points(self, metric, points, host=None, device=None):
        """ Emits a list of metric points to Datadog
            - metric:       see emit_point()
            - points:       data points as [(datetime, val), ...]
            - host:         see emit_point()
            - device:       see emit_point()
        """
        if not self.api_key:
            return
        
        # override context defaults if needed
        scope = self._override_scope(host, device)

        # Quick type check:
        for p in points:
            assert type(p[0]) == dt
            float(p[1])

        # submit!
        res = self.metric_svc.submit(self.api_key, scope, metric, points)
        assert res['status'] == 'ok'

        # ok
        return self
        
    def emit_event(self, event, host=None, device=None, source_type=None):
        """ Emits an event to Datadog
            - event:        a dogapi.event.Event object
            - host:         the name of the host to use as event context. Optional.
            - device:       the name of the device to use as event context. Optional.
            - source_type:  the name of the type of event. Not needed to submit custom events.
                            this parameter is case-sensitive

            >>> client.emit_event(e, "myhost", "mydevice")
        """
        if not self.api_key:
            return
        
        # override context defaults if needed
        scope = self._override_scope(host, device)

        res = self.event_svc.submit(self.api_key, event, scope, source_type)
        assert int(res.get("id", None)), str(res)
        assert res.get("status", None) == "ok", str(res)
        return self

    @contextmanager
    def start_event(self, event, host=None, device=None, source_type=None):
        """ Emits an event to Datadog and records its duration
            - event:        a dogapi.event.Event object
            - host:         name of the host to use as event context. Optional.
            - device:       name of the device to use as event context. Optional.
            - source_type:  the name of the type of event. Not needed to submit custom events.

            >>> with client.start_event(e, "myhost", "mydevice"):
            ...     # do some work
            ...     # when done, datadog will record the duration automatically
        """
        if not self.api_key:
            yield self
        else:
            # override context defaults if needed
            scope = self._override_scope(host, device)

            with self.event_svc.start(self.api_key, event, scope):
                yield self

    def set_api_key(self, api_key):
        self.api_key = api_key
    
    def set_host(self, host):
        self.host = host
    
    def set_device(self, device):
        self.device = device
    
    def set_datadog_host(self, datadog_host):
        self.datadog_host = datadog_host
        self.metric_svc = MetricService(self.datadog_host)
        self.event_svc = EventService(self.datadog_host)

def init(api_key=None, host=None, device=None, datadog_host=None):
    """ Initializes and returns a thin, flat client to Datadog APIs
        - api_key:      api_key string to use.
        - host:         name of the host to use as a default metric context. Optional
        - device:       name of the device to use as a default metric context. Optional
        
        Note
         - api_key will default to the one specified by the DATADOG_KEY env variable
    """
    return Client(api_key, host, device, datadog_host)

