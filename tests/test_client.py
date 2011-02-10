# python
import os
import unittest
import time
from datetime import datetime as dt

# dogclient
from dogclient.common import find_datadog_host, find_api_key
from dogclient.event import Event
import dogclient

class TestClient(unittest.TestCase):

    def config_client_test_env(self):
        self.api_key = find_api_key()
        if not self.api_key:
            self.api_key = 'apikey_3'
            os.environ['DATADOG_KEY'] = self.api_key
        
        self.host = find_datadog_host()
        if not self.host:
            self.host = 'localhost:5000'
            os.environ['DATADOG_HOST'] = self.host
            
    def setUp(self):
        self.config_client_test_env()
        
    def test_simple_client(self):
        # no  checking of submitted data yet. Just making sure it goes through
        dog = dogclient.init().default_to_localhost()
        
        # single point, default context
        dog.emit_point('test.dogclient.emit_point', 999, host='test.dogclient.fake')
        
        # multiple points, overriden context
        dog.emit_points(
            'test.dogclient.emit_points', 
            [(dt(2010,1,1), 10), (dt(2010,1,2), 20), (dt(2010,1,3), 40), (dt(2010,1,4), 80)], 
            host='test.dogclient.fake',
            device='eth0'
        )

        my_event = Event("Testing Event API")
        dog.emit_event(my_event, "test.dogclient.fake", "eth0")

        my_event = Event("Testing Event API with a duration")
        with dog.start_event(my_event, "test.dogclient.fake", "eth1"):
            time.sleep(1)
            # Done
        
if __name__ == "__main__":
    unittest.main()            
