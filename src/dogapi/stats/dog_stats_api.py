"""
DogStatsApi is a tool for collecting application metrics without hindering
performance. It collects metrics in the application thread with very little overhead
and allows flushing metrics in process, in a thread or in a greenlet, depending
on your application's needs.
"""

import logging
import socket
from functools import wraps
from contextlib import contextmanager
from time import time

from dogapi.common import get_ec2_instance_id
from dogapi.constants import MetricType
from dogapi.stats.metrics import MetricsAggregator, Counter, Gauge, Histogram
from dogapi.stats.statsd  import StatsdAggregator
from dogapi.stats.reporters import HttpReporter


# Loggers
log = logging.getLogger('dd.dogapi')


class DogStatsApi(object):

    def __init__(self):
        """ Initialize a dogstats object. """
        # Don't collect until start is called.
        self._disabled = True

    def start(self, api_key=None,
                    flush_interval=10,
                    roll_up_interval=10,
                    host=None,
                    device=None,
                    api_host=None,
                    use_ec2_instance_ids=False,
                    flush_in_thread=True,
                    flush_in_greenlet=False,
                    disabled=False,
                    statsd=False,
                    statsd_host='localhost',
                    statsd_port=8125):
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

        self._is_auto_flushing = False
        if statsd:
            # If we're configured to send to a statsd instance, use an aggregator
            # which forwards packets over UDP.
            log.info("Initializing dog api to use statsd: %s, %s" % (statsd_host, statsd_port))
            self._needs_flush = False
            self._aggregator = StatsdAggregator(statsd_host, statsd_port)
        else:
            # Otherwise create an aggreagtor that while aggregator metrics
            # in process.
            self._needs_flush = True
            self._aggregator = MetricsAggregator(self.roll_up_interval)

            # The reporter is responsible for sending metrics off to their final destination.
            # It's abstracted to support easy unit testing and in the near future, forwarding
            # to the datadog agent.
            self.reporter = HttpReporter(api_key=api_key, api_host=api_host)

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


    def gauge(self, metric_name, value, timestamp=None, tags=None, sample_rate=1):
        """
        Record the instantaneous *value* of a metric. They most recent value in
        a given flush interval will be recorded. Optionally, specify a set of
        tags to associate with the metric.

        >>> dog_stats_api.gauge('process.uptime', time.time() - process_start_time)
        >>> dog_stats_api.gauge('cache.bytes.free', cache.get_free_bytes(), tags=['version:1.0'])
        """
        if not self._disabled:
            self._aggregator.add_point(metric_name, tags, timestamp or time(), value, Gauge, sample_rate)

    def increment(self, metric_name, value=1, timestamp=None, tags=None, sample_rate=1):
        """
        Increment the counter by the given *value*. Optionally, specify a list of
        *tags* to associate with the metric.

        >>> dog_stats_api.increment('home.page.hits')
        >>> dog_stats_api.increment('bytes.processed', file.size())
        """
        if not self._disabled:
            self._aggregator.add_point(metric_name, tags, timestamp or time(), value, Counter, sample_rate)

    def histogram(self, metric_name, value, timestamp=None, tags=None, sample_rate=1):
        """
        Sample a histogram value. Histograms will produce metrics that
        describe the distribution of the recorded values, namely the minimum,
        maximum, average, count and the 75th, 85th, 95th and 99th percentiles.
        Optionally, specify a list of *tags* to associate with the metric.

        >>> dog_stats_api.histogram('uploaded_file.size', uploaded_file.size())
        """
        if not self._disabled:
            self._aggregator.add_point(metric_name, tags, timestamp or time(), value, Histogram, sample_rate)

    @contextmanager
    def timer(self, metric_name, sample_rate=1, tags=None):
        """
        A context manager that will track the distribution of the contained code's run time.
        Optionally specify a list of tags to associate with the metric.
        ::

            def get_user(user_id):
                with dog_stats_api.timer('user.query.time'):
                    # Do what you need to ...
                    pass

            # Is equivalent to ...
            def get_user(user_id):
                start = time.time()
                try:
                    # Do what you need to ...
                    pass
                finally:
                    dog_stats_api.histogram('user.query.time', time.time() - start)
        """
        start = time()
        try:
            yield
        finally:
            end = time()
            self.histogram(metric_name, end - start, end, tags=tags, sample_rate=sample_rate)

    def timed(self, metric_name, sample_rate=1, tags=None):
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
            @wraps(func)
            def wrapped(*args, **kwargs):
                with self.timer(metric_name, sample_rate, tags):
                    result = func(*args, **kwargs)
                    return result
            return wrapped
        return wrapper

    def flush(self, timestamp=None):
        """
        Flush and post all metrics to the server. Note that this is a blocking
        call, so it is likely not suitable for user facing processes. In those
        cases, it's probably best to flush in a thread or greenlet.
        """
        try:
            if not self._needs_flush:
                return False
            if self._is_flush_in_progress:
                log.debug("A flush is already in progress. Skipping this one.")
                return False
            elif self._disabled:
                log.info("Not flushing because we're disabled.")
                return False

            self._is_flush_in_progress = True
            metrics = self._get_aggregate_metrics(timestamp or time())
            count = len(metrics)
            if count:
                self.flush_count += 1
                log.info("Flush #%s sending %s metrics" % (self.flush_count, count))
                self.reporter.flush(metrics)
            else:
                log.debug("No metrics to flush. Continuing.")
        except:
            try:
                log.exception("Error flushing metrics")
            except:
                pass
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


