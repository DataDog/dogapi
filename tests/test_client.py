# python
import os
import unittest
import time
from datetime import datetime as dt

from nose.plugins.skip import SkipTest

# dogapi
from dogapi.common import find_datadog_host, find_api_key
from dogapi.event import Event
import dogapi

class TestClient(unittest.TestCase):

    def config_client_test_env(self):
        self.api_key = 'apikey_3'
        self.datadog_host = 'http://localhost:5000'
            
    def setUp(self):
        self.config_client_test_env()

    @SkipTest
    def test_simple_client(self):
        # no  checking of submitted data yet. Just making sure it goes through
        dog = dogapi.init(self.api_key, datadog_host=self.datadog_host)
        
        # single point, default context
        dog.emit_point('test.dogapi.emit_point', 999, host='test.dogapi.fake')
        
        # multiple points, overriden context
        dog.emit_points(
            'test.dogapi.emit_points', 
            [(dt(2010,1,1), 10), (dt(2010,1,2), 20), (dt(2010,1,3), 40), (dt(2010,1,4), 80)], 
            host='test.dogapi.fake',
            device='eth0'
        )

        my_event = Event("Testing Event API")
        dog.emit_event(my_event, "test.dogapi.fake", "eth0")

        my_event = Event("Testing Event API with a duration")
        with dog.start_event(my_event, "test.dogapi.fake", "eth1"):
            time.sleep(1)
            # Done
        
if __name__ == "__main__":
    unittest.main()            
