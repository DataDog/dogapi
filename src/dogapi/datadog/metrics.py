__all__ = [
    'HttpMetricApi',
    'StatsdMetricApi',
]

import logging
import time
import Queue

from dogapi.common import *


logger = logging.getLogger('dogapi')


class MetricApi(object):
    default_metric_type = MetricType.Gauge

    def increment(self, name, value=1):
        self.metric(name, value, metric_type="counter")

    def gauge(self, name, value):
        self.metric(name, value, metric_type="gauge")

    def histogram(self, name, value):
        """ Histogram. """
        self.metric(name, value, metric_type="histogram")

    def metric(self, name, points, host=None, device=None, metric_type=None):
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
        # Queue the metrics for flushing.
        logger.debug("queueing metrics to be flushed")
        self._metrics_queue.put(metrics)

        # If we're flushing in the main thread and we're ready for it,
        # submit the metrics.
        if not self._flush_thread and (time.time() - self._last_flush_time) > self.flush_interval:
            self._flush_metrics()

    def _flush_metrics(self):
        logger.info("flushing metrics")
        try:
            metrics = self._get_aggregated_metrics()
            return self._submit_metrics(metrics)
        finally:
            logger.debug("finished flush.")
            self._last_flush_time = time.time()

    def _get_aggregated_metrics(self):
        flush_time = time.time()
        raw_metrics = self._get_metrics_from_queue()
        for raw_metric in raw_metrics:
            name = raw_metric['metric']
            type_ = raw_metric['type']
            # Figure out the type of metric.
            aggregator = None
            if type_ == 'counter':
                aggregator = self._metrics_aggregator.increment
            elif type_  == 'gauge':
                aggregator = self._metrics_aggregator.gauge
            elif type_ == 'histogram':
                aggregator = self._metrics_aggregator.histogram
            else:
                raise Exception('unknown metric type %s' % type_)

            # Aggregate them.
            for timestamp, value in raw_metric['points']:
                aggregator(name, timestamp, value)

        # Get rolled up metrics
        rolled_up_metrics = self._metrics_aggregator.flush(flush_time)

        metrics = []
        for timestamp, value, name in rolled_up_metrics:
            metric = {
                'metric' : name,
                'points' : [timestamp, value],
                'type':     'gauge',
                'host':     self._default_host,
                'device':   None
            }
            metrics.append(metric)
        return metrics

    def _get_metrics_from_queue(self):
        # FIXME mattp: it's possible the thread can't completely
        # exhaust the queue. maybe default to some sane amount of
        # metrics to flush at once?
        #
        # also, is this performant enough?
        metrics = []
        while True:
            try:
                metrics += self._metrics_queue.get_nowait()
            except Queue.Empty:
                break
        return metrics

    def _submit_metrics(self, metrics):
        raise NotImplementedError()


class HttpMetricApi(MetricApi):

    def _submit_metrics(self, metrics):
        logger.debug("submitting %s metrics via http" % len(metrics))
        request = { "series": metrics }
        self.http_request('POST', '/series', request)
        if self.json_responses:
            return {}
        else:
            return None


class StatsdMetricApi(MetricApi):

    def _submit_metrics(self, metrics):
        logger.debug("submitting %s metrics via statsd" % len(metrics))
        requests = []
        for metric_series in metrics:
            metric_name = metric_series.get('metric', None)
            metric_points = metric_series.get('points', [])
            metric_type = metric_series.get('type', self.default_metric_type)

            # Don't send incomplete requests
            if not (metric_name or metric_points):
                continue

            if metric_type == MetricType.Gauge:
                # Note: not all StatsD implementations support gauges
                statsd_type_abbrev = "g"

            elif metric_type == MetricType.Counter:
                sampling_rate = metric_series.get('sampling_rate', None)
                try:
                    sampling_rate = float(sampling_rate)
                except:
                    sampling_rate = None

                if sampling_rate:
                    statsd_type_abbrev = "c|@{0}".format(sampling_rate)
                else:
                    statsd_type_abbrev = "c"

            elif metric_type == MetricType.Timer:
                statsd_type_abbrev = metric_series.get('unit', 'ms')

            else:
                log.warn("Stats doesn't support the {0} metric type".format(metric_type))
                continue

            for _ts, value in metric_points:
                requests.append("{0}:{1}|{2}".format(metric_name, value, statsd_type_abbrev))

        self.statsd_request(requests)
        if self.json_responses:
            return {}
        else:
            return None




