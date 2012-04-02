"""
Tests for the DogStatsAPI class.
"""

import os
import random
import time

import nose.tools as nt

from dogapi import DogStatsApi


#
# Test fixtures.
#

class MemoryReporter(object):
    """ A reporting class that reports to memory for testing. """

    def __init__(self):
        self.metrics = []

    def flush(self, metrics):
        self.metrics += metrics


#
# Unit tests.
#

class TestUnitDogStatsAPI(object):
    """ Unit tests for the dog stats api. """

    def sort_metrics(self, metrics):
        """ Sort metrics by timestamp of first point and then name """
        sort = lambda metric: (metric['points'][0][0], metric['metric'])
        return sorted(metrics, key=sort)

    def test_timed_decorator(self):
        dog = DogStatsApi()
        dog.start(roll_up_interval=1, flush_in_thread=False)
        reporter = dog.reporter = MemoryReporter()

        @dog.timed('timed.test')
        def func(a, b, c=1, d=1):
            return (a, b, c, d)

        result = func(1, 2, d=3)
        # Assert it handles args and kwargs correctly.
        nt.assert_equal(result, (1, 2, 1, 3))
        time.sleep(1) # Argh. I hate this.
        dog.flush()
        metrics = self.sort_metrics(reporter.metrics)
        nt.assert_equal(len(metrics), 8)
        (_, _, _, _, avg, count, max_, min_) = metrics
        nt.assert_equal(avg['metric'], 'timed.test.avg')
        nt.assert_equal(count['metric'], 'timed.test.count')
        nt.assert_equal(max_['metric'], 'timed.test.max')
        nt.assert_equal(min_['metric'], 'timed.test.min')

    def test_histogram(self):
        dog = DogStatsApi()
        dog.start(roll_up_interval=10, flush_in_thread=False)
        reporter = dog.reporter = MemoryReporter()

        # Add some histogram metrics.
        dog.histogram('histogram.1', 20, 100.0)
        dog.histogram('histogram.1', 30, 105.0)
        dog.histogram('histogram.1', 40, 106.0)
        dog.histogram('histogram.1', 50, 106.0)

        dog.histogram('histogram.1', 30, 110.0)
        dog.histogram('histogram.1', 50, 115.0)
        dog.histogram('histogram.1', 40, 116.0)

        dog.histogram('histogram.2', 40, 100.0)

        dog.histogram('histogram.3', 50, 134.0)

        # Flush and ensure they roll up properly.
        dog.flush(120.0)
        metrics = self.sort_metrics(reporter.metrics)
        nt.assert_equal(len(metrics), 24)

        # Test histograms elsewhere.
        (h1751, h1851, h1951, h1991, h1avg1, h1cnt1, h1max1, h1min1,
         _, _, _, _, h2avg1, h2cnt1, h2max1, h2min1,
         h1752, _, _, h1992, h1avg2, h1cnt2, h1max2, h1min2) = metrics

        nt.assert_equal(h1avg1['metric'], 'histogram.1.avg')
        nt.assert_equal(h1avg1['points'][0][0], 100.0)
        nt.assert_equal(h1avg1['points'][0][1], 35)
        nt.assert_equal(h1cnt1['metric'], 'histogram.1.count')
        nt.assert_equal(h1cnt1['points'][0][0], 100.0)
        nt.assert_equal(h1cnt1['points'][0][1], 4)
        nt.assert_equal(h1min1['metric'], 'histogram.1.min')
        nt.assert_equal(h1min1['points'][0][1], 20)
        nt.assert_equal(h1max1['metric'], 'histogram.1.max')
        nt.assert_equal(h1max1['points'][0][1], 50)
        nt.assert_equal(h1751['metric'], 'histogram.1.75percentile')
        nt.assert_equal(h1751['points'][0][1], 40)
        nt.assert_equal(h1991['metric'], 'histogram.1.99percentile')
        nt.assert_equal(h1991['points'][0][1], 50)


        nt.assert_equal(h1avg2['metric'], 'histogram.1.avg')
        nt.assert_equal(h1avg2['points'][0][0], 110.0)
        nt.assert_equal(h1avg2['points'][0][1], 40)
        nt.assert_equal(h1cnt2['metric'], 'histogram.1.count')
        nt.assert_equal(h1cnt2['points'][0][0], 110.0)
        nt.assert_equal(h1cnt2['points'][0][1], 3)
        nt.assert_equal(h1752['metric'], 'histogram.1.75percentile')
        nt.assert_equal(h1752['points'][0][0], 110.0)
        nt.assert_equal(h1752['points'][0][1], 40.0)
        nt.assert_equal(h1992['metric'], 'histogram.1.99percentile')
        nt.assert_equal(h1992['points'][0][0], 110.0)
        nt.assert_equal(h1992['points'][0][1], 50.0)


        nt.assert_equal(h2avg1['metric'], 'histogram.2.avg')
        nt.assert_equal(h2avg1['points'][0][0], 100.0)
        nt.assert_equal(h2avg1['points'][0][1], 40)
        nt.assert_equal(h2cnt1['metric'], 'histogram.2.count')
        nt.assert_equal(h2cnt1['points'][0][0], 100.0)
        nt.assert_equal(h2cnt1['points'][0][1], 1)

        # Flush again ensure they're gone.
        dog.reporter.metrics = []
        dog.flush(140.0)
        nt.assert_equal(len(dog.reporter.metrics), 8)
        dog.reporter.metrics = []
        dog.flush(200.0)
        nt.assert_equal(len(dog.reporter.metrics), 0)

    def test_histogram_percentiles(self):
        dog = DogStatsApi()
        dog.start(roll_up_interval=10, flush_in_thread=False)
        reporter = dog.reporter = MemoryReporter()
        # Sample all numbers between 1-100 many times. This
        # means our percentiles should be relatively close to themselves.
        percentiles = range(100)
        random.shuffle(percentiles) # in place
        for i in percentiles:
            for j in xrange(20):
                dog.histogram('percentiles', i, 1000.0)
        dog.flush(2000.0)
        metrics = reporter.metrics
        def assert_almost_equal(i, j, e=1):
            # Floating point math?
            assert abs(i - j) <= e, "%s %s %s" % (i, j, e)
        nt.assert_equal(len(metrics), 8)
        p75, p85, p95, p99, _, _, _, _ = self.sort_metrics(metrics)
        nt.assert_equal(p75['metric'], 'percentiles.75percentile')
        nt.assert_equal(p75['points'][0][0], 1000.0)
        assert_almost_equal(p75['points'][0][1], 75, 5)
        assert_almost_equal(p85['points'][0][1], 85, 5)
        assert_almost_equal(p95['points'][0][1], 95, 5)
        assert_almost_equal(p99['points'][0][1], 99, 5)

    def test_gauge(self):
        # Create some fake metrics.
        dog = DogStatsApi()
        dog.start(roll_up_interval=10, flush_in_thread=False)
        reporter = dog.reporter = MemoryReporter()

        dog.gauge('test.gauge.1', 20, 100.0)
        dog.gauge('test.gauge.1', 22, 105.0)
        dog.gauge('test.gauge.2', 30, 115.0)
        dog.gauge('test.gauge.3', 30, 125.0)
        dog.flush(120.0)

        # Assert they've been properly flushed.
        metrics = reporter.metrics
        nt.assert_equal(len(metrics), 2)

        (first, second) = metrics
        nt.assert_equal(first['metric'], 'test.gauge.1')
        nt.assert_equal(first['points'][0][0], 100.0)
        nt.assert_equal(first['points'][0][1], 22)
        nt.assert_equal(second['metric'], 'test.gauge.2')

        # Flush again and make sure we're progressing.
        reporter.metrics = []
        dog.flush(130.0)
        nt.assert_equal(len(reporter.metrics), 1)

        # Finally, make sure we've flushed all metrics.
        reporter.metrics = []
        dog.flush(150.0)
        nt.assert_equal(len(reporter.metrics), 0)

    def test_counter(self):
        # Create some fake metrics.
        dog = DogStatsApi()
        dog.start(roll_up_interval=10, flush_in_thread=False)
        reporter = dog.reporter = MemoryReporter()

        dog.increment('test.counter.1', timestamp=1000.0)
        dog.increment('test.counter.1', value=2, timestamp=1005.0)
        dog.increment('test.counter.2', timestamp=1015.0)
        dog.increment('test.counter.3', timestamp=1025.0)
        dog.flush(1021.0)

        # Assert they've been properly flushed.
        metrics = self.sort_metrics(reporter.metrics)
        nt.assert_equal(len(metrics), 2)
        (first, second) = metrics
        nt.assert_equal(first['metric'], 'test.counter.1')
        nt.assert_equal(first['points'][0][0], 1000.0)
        nt.assert_equal(first['points'][0][1], 3)
        nt.assert_equal(second['metric'], 'test.counter.2')

        # Flush again and make sure we're progressing.
        reporter.metrics = []
        dog.flush(1030.0)
        nt.assert_equal(len(reporter.metrics), 1)

        # Finally, make sure we've flushed all metrics.
        reporter.metrics = []
        dog.flush(1050.0)
        nt.assert_equal(len(reporter.metrics), 0)

    def test_default_host_and_device(self):
        dog = DogStatsApi()
        dog.start(roll_up_interval=1, flush_in_thread=False)
        reporter = dog.reporter = MemoryReporter()
        dog.gauge('my.gauge', 1, 100.0)
        dog.flush(1000)
        metric = reporter.metrics[0]
        assert not metric['device']
        assert metric['host']

    def test_custom_host_and_device(self):
        dog = DogStatsApi()
        dog.start(roll_up_interval=1, flush_in_thread=False, host='host', device='dev')
        reporter = dog.reporter = MemoryReporter()
        dog.gauge('my.gauge', 1, 100.0)
        dog.flush(1000)
        metric = reporter.metrics[0]
        nt.assert_equal(metric['device'], 'dev')
        nt.assert_equal(metric['host'], 'host')

#
# Integration tests.
#

API_KEY = os.environ.get('DATADOG_API_KEY')
APP_KEY = os.environ.get('DATADOG_APP_KEY')

class TestIntegrationDogStatsAPI(object):

    def test_flushing_in_thread(self):
        dog = DogStatsApi()
        dog.start(roll_up_interval=1,
                  flush_interval=1,
                  api_key=API_KEY)

        now = time.time()
        dog.gauge('test.dogapi.thread.gauge.%s' % now , 3)
        dog.increment('test.dogapi.thread.counter.%s' % now)
        dog.increment('test.dogapi.thread.counter.%s' % now)
        dog.histogram('test.dogapi.thread.histogram.%s' % now, 20)
        dog.histogram('test.dogapi.thread.histogram.%s' % now, 30)
        time.sleep(3)
        assert 1 <= dog.flush_count <= 5

