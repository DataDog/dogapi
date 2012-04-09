"""
DogStatsApi is a tool for collecting application metrics without hindering
performance. It collects metrics in the application thread with very little overhead
(it just writes them to a `Queue <http://docs.python.org/library/queue.html>`_
with an aggressive timeout). The aggregation and network access is performed in another
thread to ensure the instrumentation doesn't block your application's real work.
"""

import logging
import socket
import time
import Queue

from dogapi.common import get_ec2_instance_id
from dogapi.constants import MetricType
from dogapi.stats.metrics import MetricsAggregator
from dogapi.stats.reporters import HttpReporter


# Loggers
log = logging.getLogger('dd.dogapi')


class DogStatsApi(object):

    def __init__(self):
        """ Initialize a dogstats object. """
        pass

    def start(self, api_key=None,
                    flush_interval=10,
                    roll_up_interval=10,
                    host=None,
                    device=None,
                    api_host=None,
                    use_ec2_instance_ids=False,
                    flush_in_thread=True,
                    flush_in_greenlet=False,
                    disabled=False):
        """
        Configure the DogStatsApi instance and optionally, begin auto-flusing metrics.

        :param api_key: Your DataDog API key.
        :param flush_interval: The number of seconds to wait between flushes.
        :param flush_in_thread: True if you'd like to spawn a thread to flush metrics. It will run every `flush_interval` seconds.
        :param flush_in_greenlet: Set to true if you'd like to flush in a gevent greenlet.
        """
        self.flush_interval = flush_interval
        self.roll_up_interval = roll_up_interval
        self.device = device
        self._disabled = disabled

        self.host = host or socket.gethostname()
        if use_ec2_instance_ids:
            self.host = get_ec2_instance_id()

        # Initialize the metrics aggregator.
        self._aggregator = MetricsAggregator(self.roll_up_interval)

        # The reporter is responsible for sending metrics off to their final destination.
        # It's abstracted to support easy unit testing and in the near future, forwarding
        # to the datadog agent.
        self.reporter = HttpReporter(api_key=api_key, api_host=api_host)

        self._is_auto_flushing = False
        self._is_flush_in_progress = False
        self.flush_count = 0
        if self._disabled:
            log.info("dogapi is disabled. No metrics will flush.")
        else:
            if flush_in_greenlet:
                self._start_flush_greenlet()
            elif flush_in_thread:
                self._start_flush_thread()

    def stop(self):
        if not self._is_auto_flushing:
            return True
        if self._flush_thread:
            self._flush_thread.end()
            self._is_auto_flushing = False
            return True


    def gauge(self, metric_name, value, timestamp=None, tags=None):
        """
        Record the instantaneous *value* of a metric. They most recent value in
        a given flush interval will be recorded. Optionally, specify a set of
        tags to associate with the metric.

        >>> dog_stats_api.gauge('process.uptime', time.time() - process_start_time)
        >>> dog_stats_api.gauge('cache.bytes.free', cache.get_free_bytes(), tags=['version:1.0'])
        """
        self._aggregator.gauge(metric_name, tags, timestamp or time.time(), value)

    def increment(self, metric_name, value=1, timestamp=None, tags=None):
        """
        Increment the counter by the given *value*. Optionally, specify a list of
        *tags* to associate with the metric.

        >>> dog_stats_api.increment('home.page.hits')
        >>> dog_stats_api.increment('bytes.processed', file.size())
        """
        self._aggregator.increment(metric_name, tags, timestamp or time.time(), value)

    def histogram(self, metric_name, value, timestamp=None, tags=None):
        """
        Sample a histogram value. Histograms will produce metrics that
        describe the distribution of the recorded values, namely the minimum,
        maximum, average, count and the 75th, 85th, 95th and 99th percentiles.
        Optionally, specify a list of *tags* to associate with the metric.

        >>> dog_stats_api.histogram('uploaded_file.size', uploaded_file.size())
        >>> dog_stats_api.histogram('uploaded_file.size', uploaded_file.size())
        """
        self._aggregator.histogram(metric_name, tags, timestamp or time.time(), value)

    def timed(self, metric_name, tags=None):
        """
        A decorator that will track the distribution of a function's run time.
        Optionally specify a list of tags to associate with the metric.
        ::

            @dog_stats_api.timed('user.query.time')
            def get_user(user_id):
                # Do what you need to ...
                pass

            # Is equivalent to ...
            start = time.time()
            try:
                get_user(user_id)
            finally:
                dog_stats_api.histogram('user.query.time', time.time() - start)
        """
        def wrapper(func):
            def wrapped(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                self.histogram(metric_name, time.time() - start, tags=tags)
                return result
            return wrapped
        return wrapper

    def flush(self, timestamp=None):
        """
        Flush all metrics to their final destination.
        """
        if self._is_flush_in_progress:
            log.debug("A flush is already in progress. Skipping this one.")
            return False
        elif self._disabled:
            log.info("Not flushing because we're disabled.")
            return False

        try:
            self._is_flush_in_progress = True
            metrics = self._get_aggregate_metrics(timestamp or time.time())
            count = len(metrics)
            if count:
                self.flush_count += 1
                log.info("Flush #%s sending %s metrics" % (self.flush_count, count))
                self.reporter.flush(metrics)
            else:
                log.info("No metrics to flush. Continuing.")
        finally:
            self._is_flush_in_progress = False

    def _get_aggregate_metrics(self, flush_time=None):
        # Get rolled up metrics
        rolled_up_metrics = self._aggregator.flush(flush_time)

        # FIXME: emit a dictionary from the aggregator
        metrics = []
        for timestamp, value, name, tags in rolled_up_metrics:
            metric = {
                'metric' : name,
                'points' : [[timestamp, value]],
                'type':    MetricType.Gauge,
                'host':    self.host,
                'device':  self.device,
                'tags'  :  tags
            }
            metrics.append(metric)
        return metrics

    def _start_flush_thread(self):
        """ Start a thread to flush metrics. """
        from dogapi.stats.periodic_timer import PeriodicTimer
        if self._is_auto_flushing:
            log.info("Autoflushing already started.")
            return
        self._is_auto_flushing = True

        # A small helper for logging and flushing.
        def flush():
            try:
                log.debug("Flushing metrics in thread")
                self.flush()
            except:
                try:
                    log.exception("Error flushing in thread")
                except:
                    pass

        log.info("Starting flush thread with interval %s." % self.flush_interval)
        self._flush_thread = PeriodicTimer(self.flush_interval, flush)
        self._flush_thread.daemon = True    # Die when parent thread dies.
        self._flush_thread.start()

    def _start_flush_greenlet(self):
        if self._is_auto_flushing:
            log.info("Autoflushing already started.")
            return
        self._is_auto_flushing = True

        import gevent
        # A small helper for flushing.
        def flush():
            while True:
                try:
                    log.debug("Flushing metrics in greenlet")
                    self.flush()
                    gevent.sleep(self.flush_interval)
                except:
                    try:
                        log.exception("Error flushing in greenlet")
                    except:
                        pass

        log.info("Starting flush greenlet with interval %s." % self.flush_interval)
        gevent.spawn(flush)


