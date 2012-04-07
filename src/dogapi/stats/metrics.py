"""
Metric roll-up classes.
"""


from collections import defaultdict
import random
import time
import threading


class Metric(object):
    """
    A base metric class that accepts points, slices them into time intervals
    and performs roll-ups within those intervals.
    """

    def add_point(self, value):
        """ Add a point to the given metric. """
        raise NotImplementedError()

    def flush(self, timestamp):
        """ Flush all metrics up to the given timestamp. """
        raise NotImplementedError()


class Gauge(Metric):
    """ A gauge metric. """

    def __init__(self, name):
        self.name = name
        self.value = None

    def add_point(self, value):
        self.value = value

    def flush(self, timestamp):
        return [(timestamp, self.value, self.name)]

class Counter(Metric):
    """ A counter metric. """

    def __init__(self, name):
        self.name = name
        self.count = 0
        self.interval = None
        self.lock = threading.RLock()

    def add_point(self, value):
        with self.lock:
            self.count += value

    def flush(self, timestamp):
        return [(timestamp, self.count, self.name)]


class Histogram(Metric):
    """ A histogram metric. """

    def __init__(self, name, sample_size=1000):
        self.name = name
        self.max = float("-inf")
        self.min = float("inf")
        self.sum = 0
        self.count = 0
        self.sample_size = sample_size
        self.samples = [None] * self.sample_size
        self.percentiles = [0.75, 0.85, 0.95, 0.99]
        self.lock = threading.RLock()

    def add_point(self, value):
        self.max = self.max if self.max > value else value
        self.min = self.min if self.min < value else value
        with self.lock:
            self.sum += value
            if self.count < self.sample_size:
                self.samples[self.count] = value
            else:
                self.samples[random.randrange(0, self.sample_size)] = value
            self.count += 1

    def flush(self, timestamp):
        if not self.count:
            return []
        metrics = [
            (timestamp, self.min,   '%s.min' % self.name),
            (timestamp, self.max,   '%s.max' % self.name),
            (timestamp, self.count, '%s.count' % self.name),
            (timestamp, float(self.sum) / self.count, '%s.avg' % self.name)
        ]
        samples = sorted(self.samples[:self.count])
        for p in self.percentiles:
            val = samples[int(round(p * len(samples) - 1))]
            name = '%s.%spercentile' % (self.name, int(p * 100))
            metrics.append((timestamp, val, name))
        return metrics

class MetricsAggregator(object):
    """
    A small class to handle the roll-ups of multiple metrics at once.
    """

    def __init__(self, roll_up_interval=10):
        self._metrics = {}
        self._roll_up_interval = roll_up_interval

    def increment(self, metric, timestamp, value=1):
        """ Increment the given counter. """
        self._add_point(metric, timestamp, value, Counter)

    def gauge(self, metric, timestamp, value):
        """ Record a gauge metric. """
        self._add_point(metric, timestamp, value, Gauge)

    def histogram(self, metric, timestamp, value):
        """ Sample a histogram point. """
        self._add_point(metric, timestamp, value, Histogram)

    def _add_point(self, metric, timestamp, value, metric_class):
        interval = timestamp - timestamp % self._roll_up_interval
        if interval not in self._metrics:
            self._metrics[interval] = {}
        if metric not in self._metrics[interval]:
            self._metrics[interval][metric] = metric_class(metric)
        self._metrics[interval][metric].add_point(value)

    def flush(self, timestamp):
        """ Flush all metrics up to the given timestamp. """
        interval = timestamp - timestamp % self._roll_up_interval
        past_intervals = sorted((i for i in self._metrics if i < interval))
        metrics = []
        for i in past_intervals:
            for m in self._metrics.pop(i).values():
                metrics += m.flush(i)
        return metrics

