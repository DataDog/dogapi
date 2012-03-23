"""
Tests for the DogStatsAPI class.
"""


import time

import nose.tools as nt

from dogapi import DogStatsApi


#
# Test fixtures.
#

class TestReporter(object):
    """ A reporting class that reports to memory for testing. """

    def __init__(self):
        self.metrics = []

    def flush(self, metrics):
        self.metrics += metrics


#
# Test code.
#

class TestDogStatsAPI(object):

    def test_gauge(self):

        # Create some fake metrics.
        dog = DogStatsApi(roll_up_interval=10, flush_in_thread=False)
        reporter = dog.reporter = TestReporter()

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
        dog = DogStatsApi(roll_up_interval=10, flush_in_thread=False)
        reporter = dog.reporter = TestReporter()

        dog.increment('test.counter.1', timestamp=1000.0)
        dog.increment('test.counter.1', value=2, timestamp=1005.0)
        dog.increment('test.counter.2', timestamp=1015.0)
        dog.increment('test.counter.3', timestamp=1025.0)
        dog.flush(1021.0)

        # Assert they've been properly flushed.
        metrics = reporter.metrics
        nt.assert_equal(len(metrics), 2)

        (first, second) = metrics

        # order isn't guarantted. cheeezy.
        if first['metric'] == 'test.counter.2':
            (second, first) = (first, second)
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

    def test_max_queue_size(self):
        dog = DogStatsApi(flush_interval=1, max_queue_size=5, roll_up_interval=1, flush_in_thread=False)
        reporter = dog.reporter = TestReporter()
        for i in range(10):
            dog.gauge('my.gauge.%s' % i,  1, 1000.0)
        dog.flush(2000.0)
        nt.assert_equal(len(reporter.metrics), 5)

