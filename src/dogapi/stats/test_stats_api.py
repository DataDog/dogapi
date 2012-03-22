"""
Tests for the DogStatsAPI class.
"""


import time

import nose.tools as nt

from dogapi import DogStatsApi


#
# Test fixtures.
#

class Reporter(object):
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
        dog = DogStatsApi(roll_up_interval=1, flush_interval=1)
        # Hack the reporting class so that it flushes to memory.
        reporter = Reporter()
        dog.reporter = reporter

        # Add a gauge value and ensure 
        dog.gauge('test.dogapi.gauge', 123.4)
        time.sleep(2) # Sleep for the roll-up interval.

        metrics = reporter.metrics
        nt.assert_equal(len(metrics), 1)

    def test_max_queue_size(self):
        max_dog = DogStatsApi(max_queue_size=1, flush_interval=1, roll_up_interval=1)
        max_dog.reporter = Reporter()
        max_dog.gauge('my.gauge', 1)
        max_dog.increment('my.counter')
        time.sleep(2)
        max_dog.flush()
        nt.assert_equal(len(max_dog.reporter.metrics), 1)


