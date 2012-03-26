"""
Tests for flushing with greenlets. Can't be run in the same process
as other tests because of the gevent monkey patch.
"""


from gevent import monkey
monkey.patch_all()

import os
import time
import unittest

from dogapi import DogStatsApi


API_KEY = os.environ.get('DATADOG_API_KEY')


class TestGreenletIntegrationDogStatsApi(unittest.TestCase):

    def test_flushing_in_thread(self):
        dog = DogStatsApi()
        dog.start(roll_up_interval=1,
                  flush_interval=1,
                  flush_in_greenlet=True,
                  api_key=API_KEY)

        now = time.time()
        dog.gauge('test.dogapi.greenlet.gauge.%s' % now , 3)
        dog.increment('test.dogapi.greenlet.counter.%s' % now)
        dog.increment('test.dogapi.greenlet.counter.%s' % now)
        dog.histogram('test.dogapi.greenlet.histogram.%s' % now, 20)
        dog.histogram('test.dogapi.greenlet.histogram.%s' % now, 30)
        time.sleep(3)
        assert 1 <= dog.flush_count <= 5

if __name__ == '__main__':
    unittest.main()

