"""
Metric roll-up classes.
"""


from collections import defaultdict
import random
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

    def _pop_past_intervals(self, timestamp):
        """ Return all intervals that are before the given timestamp. """
        ts_interval = self._get_interval(timestamp)
        past_timestamps = sorted([i for i in self._intervals if i < ts_interval])
        return [(ts, self._intervals.pop(ts)) for ts in past_timestamps]


class Gauge(Metric):
    """ A gauge metric. """

    def __init__(self, name, roll_up_interval):
        super(Gauge, self).__init__(name, roll_up_interval)
        self._intervals = defaultdict(lambda: None)

    def add_point(self, timestamp, value):
        interval = self._get_interval(timestamp)
        self._intervals[interval] = value

    def flush(self, timestamp):
        past_intervals = self._pop_past_intervals(timestamp)
        return [(ts, gauge, self._name) for ts, gauge in past_intervals]


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
        past_intervals = self._pop_past_intervals(timestamp)
        return [(ts, count, self._name) for ts, count in past_intervals]


class Histogram(Metric):
    """ A histogram metric. """

    def __init__(self, name, roll_up_interval, sample_size=1000):
        super(Histogram, self).__init__(name, roll_up_interval)
        # Each interval stores a dictionary of running stats of the
        # histogram, like max, min, samples and so on.
        self._intervals = defaultdict(lambda: {})
        self._sample_size = sample_size
        self._percentiles = [0.75, 0.85, 0.95, 0.99]

        # The names of the metrics the histogram produces.
        self._min_name = self._name + '.min'
        self._max_name = self._name + '.max'
        self._avg_name = self._name + '.avg'
        self._count_name = self._name + '.count'
        self._percentile_names = {}
        for p in self._percentiles:
            pint = int(p * 100)
            self._percentile_names[p] = "%s.%spercentile" % (self._name, pint)

    def add_point(self, timestamp, value):
        interval = self._get_interval(timestamp)
        bucket = self._intervals[interval]

        # Update the min, max and so on.
        bucket['max'] = max(bucket.get('max', float("-inf")), value)
        bucket['min'] = min(bucket.get('min', float("inf")), value)
        bucket['count'] = bucket.get('count', 0) + 1
        bucket['sum'] = bucket.get('sum', 0) + value

        # And sample a value for percentiles.
        samples = bucket.get('samples', [])
        if len(samples) < self._sample_size:
            samples.append(value)
        else:
            index = random.randint(0, self._sample_size - 1)
            samples[index] = value
        bucket['samples'] = samples

        # And put our bucket back.
        self._intervals[interval] = bucket

    def _get_percentiles(self, samples):
        samples.sort()
        length = len(samples)
        output = {}
        if not length:
            return output
        for percentile in self._percentiles:
            index = int(round(percentile * length - 1))
            output[percentile] = samples[index]
        return output

    def flush(self, timestamp):
        metrics = []
        for i, bucket in self._pop_past_intervals(timestamp):
            count = bucket['count']
            if count <= 0:
                raise Exception("no metrics: %s %s" % (self._name, i))
            min_ = bucket['min']
            max_ = bucket['max']
            avg = float(bucket['sum']) / count

            metrics.append((i, avg,   self._avg_name))
            metrics.append((i, count, self._count_name))
            metrics.append((i, min_,  self._min_name))
            metrics.append((i, max_,  self._max_name))
            percentiles = self._get_percentiles(bucket['samples'])
            for p, value in percentiles.items():
                name = self._percentile_names[p]
                metrics.append((i, value, name))
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

