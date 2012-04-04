#
# Integration tests.
#
import os
import time

import dogapi

API_KEY = os.environ.get('DATADOG_API_KEY')
APP_KEY = os.environ.get('DATADOG_APP_KEY')

class TestIntegrationDogStatsAPI(object):

    def test_flushing_in_thread(self):
        dog = dogapi.DogStatsApi()
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

