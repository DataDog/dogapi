"""
DogStatsAPI collects metrics and asynchronously flushes them to DataDog's
HTTP API.
"""

import logging
import socket
import time
import Queue

from dogapi.common import get_ec2_instance_id
from dogapi.constants import MetricType
from dogapi.stats.metrics import MetricsAggregator
from dogapi.stats.reporters import HttpReporter


log = logging.getLogger('dd.dogapi')
stat_log = logging.getLogger('dd.dogapi.stats')


class DogStatsApi(object):

    def __init__(self):
        """ Initialize a dogstats object. """
        self.max_queue_size = 200000
        self.metric_timeout = 0.01

        # We buffer metrics in a thread safe queue, so that there is no conflict
        # if we are flushing metrics in another thread.
        self._metrics_queue = Queue.Queue(self.max_queue_size)

    def start(self, api_key=None,
                    flush_interval=10,
                    roll_up_interval=10,
                    host=None,
                    device=None,
                    api_host=None,
                    metric_timeout=0.01,
                    use_ec2_instance_ids=False,
                    flush_in_thread=True,
                    flush_in_greenlet=False):
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
        self.metric_timeout = metric_timeout

        self.host = host or socket.gethostname()
        if use_ec2_instance_ids:
            self.host = get_ec2_instance_id()

        # Initialize the metrics aggregator.
        self._metrics_aggregator = MetricsAggregator(self.roll_up_interval)

        # The reporter is responsible for sending metrics off to their final destination.
        # It's abstracted to support easy unit testing and in the near future, forwarding
        # to the datadog agent.
        self.reporter = HttpReporter(api_key=api_key, api_host=api_host)

        self._is_auto_flushing = False
        self._is_flush_in_progress = False
        self.flush_count = 0
        if flush_in_greenlet:
            self._start_flush_greenlet()
        elif flush_in_thread:
            self._start_flush_thread()

    def gauge(self, metric_name, value, timestamp=None):
        """
        Record the instantaneous value of the given gauge.

        :param metric_name: The name of the gauge (e.g. 'my.app.users.online')
        :param value: The integer or floating point value of the gauge.
        :param timestamp: The time the value was recorded. Defaults to now.
        """
        self._queue_metric(metric_name, value, MetricType.Gauge, timestamp)

    def increment(self, metric_name, value=1, timestamp=None):
        """
        Increment the given counter.

        :param metric_name: The name of the counter (e.g. 'home.page.request.count')
        :param value: The value to increment to by. Defaults to one.
        :param timestamp: The time the counter was incremented. Defaults to now.
        """
        self._queue_metric(metric_name, value, MetricType.Counter, timestamp)

    def histogram(self, metric_name, value, timestamp=None):
        """
        Sample a value of the given histogram

        :param metric_name: The name of the histogram (e.g. 'home.page.query.time')
        :param value: The integer or floating value to sample.
        :param timestamp: The time the value was sampled. Defaults to now.
        """
        self._queue_metric(metric_name, value, MetricType.Histogram, timestamp)

    def timed(self, metric_name):
        """
        A decorator that will sample the run time of a function in a histogram.

        :param metric_name: The name of the histogram metric.
        """
        def wrapper(func):
            def wrapped(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                self.histogram(metric_name, time.time() - start)
                return result
            return wrapped
        return wrapper

    def flush(self, timestamp=None):
        """
        Flush all metrics to their final destination.
        """
        if self._is_flush_in_progress:
            log.debug("A flush is already in progress. Skipping this one.")
            return
        try:
            self._is_flush_in_progress = True
            raw_metrics = self._dequeue_metrics()
            metrics = self._aggregate_metrics(raw_metrics, timestamp)
            count = len(metrics)
            if count:
                self.flush_count += 1
                log.info("Flush #%s sending %s metrics" % (self.flush_count, count))
                self.reporter.flush(metrics)
            else:
                log.info("No metrics to flush. Continuing.")
        finally:
            self._is_flush_in_progress = False

    def _aggregate_metrics(self, raw_metrics, flush_time=None):
        flush_time = flush_time or time.time()
        for raw_metric in raw_metrics:
            name = raw_metric['metric']
            type_ = raw_metric['type']
            aggregator = self._metrics_aggregator.get_aggregator_function(type_)
            # Aggregate them.
            for timestamp, value in raw_metric['points']:
                aggregator(name, timestamp, value)

        # Get rolled up metrics
        rolled_up_metrics = self._metrics_aggregator.flush(flush_time)

        metrics = []
        for timestamp, value, name in rolled_up_metrics:
            metric = {
                'metric' : name,
                'points' : [[timestamp, value]],
                'type':    MetricType.Gauge,
                'host':    self.host,
                'device':  self.device
            }
            metrics.append(metric)
            stat_log.info("Metric (%s, %s, %s)" % (name, value, timestamp))
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

    def _queue_metric(self, metric_name, value, metric_type, timestamp=None):
        """ Queue the given metric for aggregation. """
        metric = {
            'metric':   metric_name,
            'points':   [[timestamp or time.time(), value]],
            'type':     metric_type
        }
        # If the metrics queue is full, don't block.
        try:
            self._metrics_queue.put(metric, True, self.metric_timeout)
        except Queue.Full:
            # This check has a race condition, but if we're in the
            # ballpark of the max queue size, it's true enough.
            if self._metrics_queue.full():
                log.error("Metrics queue is full with size %s" % self.max_queue_size)
            else:
                log.error("Hit metric timeout of %s. Dropping point." % self.metric_timeout)

    def _dequeue_metrics(self):
        """ Pop all metrics off of the queue. """
        metrics = []
        loops = 0
        log.debug("Dequeuing metrics. Size: %s" % self._metrics_queue.qsize())
        while True:
            loops += 1
            # FIXME mattp: is this performant enough? If we're flushing
            # manually or in a greenlet, we could skip this step and queue
            # directly onto the aggregator.
            try:
                metrics.append(self._metrics_queue.get(False, self.metric_timeout * 2))
            except Queue.Empty:
                # Only break if the queue is actually close to empty. Let the
                if self._metrics_queue.empty():
                    break
            # Ensure that we aren't popping metrics for a dangerously long time.
            if loops >= self.max_queue_size:
                log.info("Maximum flush size hit %s" % self.max_queue_size)
                break
        log.debug("Finished dequeueing metrics. Size: %s" %
                                        self._metrics_queue.qsize())
        return metrics

