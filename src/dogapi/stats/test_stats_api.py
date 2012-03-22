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

dog = None
reporter = None

class TestDogStatsAPI(object):

    def setUp(self):
        global dog
        global reporter
        dog = DogStatsApi(roll_up_interval=1, flush_interval=1)
        # Hack the reporting class so that it flushes to memory.
        reporter = Reporter()
        dog.reporter = reporter

    def test_gauge(self):
        # Add a gauge value and ensure 
        dog.gauge('test.dogapi.gauge', 123.4)
        time.sleep(3) # Sleep for the roll-up interval.

        metrics = reporter.metrics
        nt.assert_equal(len(metrics), 1)

