"""
DataDog Stat's API
"""


import logging
import socket
import time
import Queue

from dogapi.constants import MetricType
from dogapi.stats.periodic_timer import PeriodicTimer
from dogapi.stats.metrics import MetricsAggregator


log = logging.getLogger('dogapi')


class DogStatsApi(object):

    def __init__(self, flush_interval=10,
                       roll_up_interval=10,
                       api_host='https://app.datadoghq.com',
                       application_key=None,
                       api_key=None,
                       max_queue_size=0,
                       max_flush_size=1000,
                       flush_in_thread=True,
                       flush_in_greenlet=False):
        """
        Create a DogStatsApi instance.
        """

        self.reporter = None

        self.flush_interval = flush_interval
        self.roll_up_interval = roll_up_interval
        self.max_queue_size = max_queue_size
        self.max_flush_size = max_flush_size

        # FIXME mattp: share with http api?
        self._host_name = socket.gethostname()

        # We buffer metrics in a thread safe queue, so that there is no conflict
        # if we are flushing metrics in another thread.
        self._metrics_queue = Queue.Queue(self.max_queue_size)

        # Initialize the metrics aggregator.
        self._metrics_aggregator = MetricsAggregator(self.roll_up_interval)

        self._flushing = False # True if a flush mechanism has been started.

        # Start the appropriate flushing mechanism.
        if flush_in_thread:
            self._start_flush_thread()
        elif flush_in_greenlet:
            self._start_flush_greenlet()

    def gauge(self, metric_name, value, timestamp=None):
        """
        Record a value for the given gauge.
        """
        self._queue_metric(metric_name, value, MetricType.Gauge, timestamp)

    def increment(self, metric_name, value=1, timestamp=None):
        self._queue_metric(metric_name, value, MetricType.Counter, timestamp)

    def histogram(self, metric_name, value, timestamp=None):
        self._queue_metric(metric_name, value, MetricType.Histogram, timestamp)

    def timed(self, metric_name):
        def wrapper(func):
            def wrapped(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                self.histogram(metric_name, time.time() - start)
                return result
            return wrapped
        return wrapper

    def flush(self, timestamp=None):
        """ Aggregate metrics and pass along to the reporter. """
        raw_metrics = self._dequeue_metrics()
        metrics = self._aggregate_metrics(raw_metrics, timestamp)
        self.reporter.flush(metrics)

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
                'host':    self._host_name,
                'device':  None
            }
            metrics.append(metric)
        return metrics

    def _start_flush_thread(self):
        """ Start a thread to flush metrics. """
        if self._flushing:
            log.info("Already running.")
            return

        self._flushing = True

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
        if self._flushing:
            log.info("Already flushing.")
            return
        self._flushing = True

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
            'type':     metric_type,
            'host':     self._host_name,
            'device':   None
        }
        # If the metrics queue is full, don't block.
        try:
            self._metrics_queue.put_nowait(metric)
        except Queue.Full:
            log.error("Metrics queue is full with size %s" % self.max_queue_size)

    def _dequeue_metrics(self):
        """ Pop all metrics off of the queue. """
        metrics = []
        while True:
            # FIXME mattp: is this performant enough? If we're flushing
            # manually or in a greenlet, we could skip this step and queue
            # directly onto the aggregator.
            try:
                metrics.append(self._metrics_queue.get_nowait())
            except Queue.Empty:
                break
            # Ensure that we aren't popping metrics for a dangerously
            # long time.
            if len(metrics) >= self.max_flush_size:
                log.info("Maximum flush size hit %s" % self.max_flush_size)
                break
        return metrics

