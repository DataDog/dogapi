__all__ = [
    'HttpMetricApi',
]

import logging
import time


from dogapi.constants import MetricType


logger = logging.getLogger('dd.dogapi')


class HttpMetricApi(object):
    default_metric_type = MetricType.Gauge


    def metric(self, name, points, host=None, device=None, tags=None, metric_type=MetricType.Gauge):
        """
        Submit a point or series of *points* to the metric API, optionally specifying a *host*
        or *device*. Points can either be a value,
        a tuple of POSIX timestamps and a value, or a list of timestamp value pairs.

        >>> dog_http_api.metric('my.value', 123.4, host="my.custom.host")
        >>> dog_http_api.metric('my.pair', (1317652676, 15), device="eth0")
        >>> dog_http_api.metric('my.series', [(1317652676, 15), (1317652800, 16))
        """
        if host is None:
            host = self._default_host

        now = time.time()
        if isinstance(points, (float, int)):
            points = [(now, points)]
        elif isinstance(points, tuple):
            points = [points]

        return self.metrics([{
            'metric':   name,
            'points':   [[ts, val] for ts, val in points],
            'type':     metric_type,
            'host':     host,
            'device':   device,
            'tags' : tags
        }])

    def metrics(self, metrics):
        """
        Submit a list of *metrics* with 1 or more data points to the metric API. Each metric is a dictionary
        that includes the fields metric_name, points and optionally, host and device to scope the metric.

        >>> dog_http_api.metrics([{'metric':'my.metric', 'points':[(1317652676, 15)]}])
        """
        logger.debug("Submitting metrics to the api")
        return self._submit_metrics(metrics)

    def _submit_metrics(self, metrics):
        logger.debug("flushing metrics over http.")
        request = { "series": metrics }
        self.http_request('POST', '/series', request)
        if self.json_responses:
            return {}
        else:
            return None

