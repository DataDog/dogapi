"""
DataDog Stat's API
"""


import logging
import socket
import time
import Queue

from dogapi.stats.periodic_timer import PeriodicTimer
from dogapi.stats.metrics import MetricsAggregator


log = logging.getLogger('dogapi')


GAUGE = 'gauge'
COUNTER = 'counter'
HISTOGRAM = 'histogram'


class DogStatsApi(object):

    def __init__(self, flush_interval=10,
                       roll_up_interval=10,
                       max_queue_size=0,
                       api_host='https://app.datadoghq.com',
                       application_key=None,
                       api_key=None):
        """
        Create a DogStatsApi instance.
        """
        self.reporter = None
        self.flush_interval = flush_interval
        self.roll_up_interval = roll_up_interval
        self.max_queue_size = max_queue_size

        # FIXME mattp: share with http api?
        self._host_name = socket.gethostname()

        # We buffer metrics in a thread safe queue, so that there is no conflict
        # if we are flushing metrics in another thread.
        self._metrics_queue = Queue.Queue(self.max_queue_size)

        # Initialize the metrics aggregator.  
        self._metrics_aggregator = MetricsAggregator(self.roll_up_interval)

        self._flushing = False # True if a flush mechanism has been started.
        self._start_flush_thread()

    def gauge(self, metric_name, value):
        """
        Record a value for the given gauge.
        """
        self._queue_metric(metric_name, value, GAUGE)

    def increment(self):
        pass

    def histogram(self):
        pass

    def timed(self):
        pass

    def _flush(self):
        """ Aggregate metrics and pass along to the reporter. """
        raw_metrics = self._dequeue_metrics()
        metrics = self._aggregate_metrics(raw_metrics)
        self.reporter.flush(metrics)

    def _aggregate_metrics(self, raw_metrics):
        flush_time = time.time()
        for raw_metric in raw_metrics:
            print raw_metric
            name = raw_metric['metric']
            type_ = raw_metric['type']
            # Figure out the type of metric.

            aggregator = None
            if type_ == COUNTER:
                aggregator = self._metrics_aggregator.increment
            elif type_  == GAUGE:
                aggregator = self._metrics_aggregator.gauge
            elif type_ == HISTOGRAM:
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
                'points' : [[timestamp, value]],
                'type':    GAUGE,
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
                self._flush()
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
                    self._flush()
                    gevent.sleep(self.flush_interval)
                except:
                    try:
                        log.exception("Error flushing in greenlet")
                    except:
                        pass

        log.info("Starting flush greenlet with interval %s." % self.flush_interval)
        gevent.spawn(flush)

    def _queue_metric(self, metric_name, value, metric_type):
        """ Queue the given metric for aggregation. """
        metric = {
            'metric':   metric_name,
            'points':   [[time.time(), value]],
            'type':     metric_type,
            'host':     self._host_name,
            'device':   None
        }
        # If the metrics queue is full, don't block.
        self._metrics_queue.put_nowait(metric)

    def _dequeue_metrics(self):
        """ Pop all metrics off of the queue. """
        MAX_POPS = 1000
        pops = 0
        metrics = []
        while True:
            # FIXME mattp: is this performant enough?
            try:
                metrics.append(self._metrics_queue.get_nowait())
            except Queue.Empty:
                break
            # Ensure that we aren't popping metrics for a dangerously
            # long time.
            pops += 1
            if pops > MAX_POPS:
                break
        return metrics

class Reporter(object):
    
    def flush(self, metrics):
        pass

class HttpReporter(Reporter):

    def flush(self, metrics):
        pass

