__all__ = [
    'HttpMetricApi',
]

import logging
import time


from dogapi.constants import MetricType


logger = logging.getLogger('dogapi')


class HttpMetricApi(object):
    default_metric_type = MetricType.Gauge


    def metric(self, name, points, host=None, device=None, metric_type=MetricType.Gauge):
        """
        Submit a series of data points to the metric API.

        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param values: data series. list of (POSIX timestamp, intever value) tuples.
                (e.g. ``[(1317652676, 15), (1317652706, 18), ...]``)
        :type values: list

        :param host: optional host to scope the metric (e.g.
        ``"hostA.example.com"``). defaults to local hostname. to submit without
        a host, explicitly set host=None.
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
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
        }])

    def metrics(self, metrics):
        """
        Submit a series of metrics with 1 or more data points to the metric
        API.

        :param values A dictionary of names to a list values, in the form of {name: [(POSIX timestamp, integer value), ...], name2: [(POSIX timestamp, integer value), ...]}
        :type values: dict

        :param host: optional host to scope the metric (e.g.
        ``"hostA.example.com"``). to submit without a host, explicitly set
        host=None.
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
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

