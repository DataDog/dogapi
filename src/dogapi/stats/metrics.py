"""
Metric roll-up classes.
"""


from collections import defaultdict
import time

from dogapi.constants import MetricType

class Metric(object):
    """
    A base metric class that accepts points, slices them into time intervals
    and performs roll-ups within those intervals.
    """

    def __init__(self, name, roll_up_interval):
        """ Create a metric. """
        self._name = name
        self._roll_up_interval = roll_up_interval

    def add_point(self, timestamp, value):
        """ Add a point to the given metric. """
        raise NotImplementedError()

    def flush(self, timestamp):
        """ Flush all metrics up to the given timestamp. """
        raise NotImplementedError()

    def _get_interval(self, timestamp):
        """ Return the interval into which the given timestamp fits. """
        return timestamp - timestamp % self._roll_up_interval

    def _get_past_intervals(self, timestamp):
        """ Return all intervals that are before the given timestamp. """
        ts_interval = self._get_interval(timestamp)
        return sorted([i for i in self._intervals if i < ts_interval])


class Gauge(Metric):
    """ A gauge metric. """

    def __init__(self, name, roll_up_interval):
        super(Gauge, self).__init__(name, roll_up_interval)
        self._intervals = defaultdict(lambda: None)

    def add_point(self, timestamp, value):
        interval = self._get_interval(timestamp)
        self._intervals[interval] = value

    def flush(self, timestamp):
        past_intervals = self._get_past_intervals(timestamp)
        return [(i, self._intervals.pop(i), self._name) for i in past_intervals]


class Counter(Metric):
    """ A counter metric. """

    def __init__(self, name, roll_up_interval):
        super(Counter, self).__init__(name, roll_up_interval)
        self._intervals = {}

    def add_point(self, timestamp, value):
        interval = self._get_interval(timestamp)
        count = self._intervals.get(interval, 0)
        self._intervals[interval] = count + value

    def flush(self, timestamp):
        past_intervals = self._get_past_intervals(timestamp)
        return [(i, self._intervals.pop(i), self._name) for i in past_intervals]


class Histogram(Metric):
    """ A histogram metric. """

    def __init__(self, name, roll_up_interval):
       super(Histogram, self).__init__(name, roll_up_interval)
       self._intervals = defaultdict(lambda: [])

    def add_point(self, timestamp, value):
        interval = self._get_interval(timestamp)
        self._intervals[interval].append(value)

    def flush(self, timestamp):
        metrics = []
        for i in self._get_past_intervals(timestamp):
            #FIXME: make this real.
            values = self._intervals.pop(i)
            count = len(values)
            avg = sum(values) / count
            metrics.append((i, avg, self._name + '.avg'))
            metrics.append((i, count, self._name + '.count'))
            metrics.append((i, min(values), self._name + '.min'))
            metrics.append((i, max(values), self._name + '.max'))
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
        # FIXME mattp: overwrite metric if we add a different type?
        if metric not in self._metrics:
            self._metrics[metric] = metric_class(metric, self._roll_up_interval)
        self._metrics[metric].add_point(timestamp, value)

    def flush(self, timestamp):
        """ Flush all metrics up to the given timestamp. """
        # remove empty metrics on flush?
        metrics = []
        for metric in self._metrics.values():
            metrics += metric.flush(timestamp)
        return metrics

    def get_aggregator_function(self, metric_type):
        if metric_type == MetricType.Gauge:
            return self.gauge
        elif metric_type == MetricType.Counter:
            return self.increment
        elif metric_type == MetricType.Histogram:
            return self.histogram
        else:
            raise Exception('unknown metric type: %s' % metric_type)

