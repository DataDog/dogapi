# python
import random, math
import datetime
import unittest

# nose
from nose.plugins.skip import SkipTest

# dogapi
from dogapi.event import EventService, Scope, Event


class TestEventClient(unittest.TestCase):

    def setUp(self):
        self.api_key = "apikey_3"
            
    def test_submit_event(self, scope=None, source_type=None):
        # create and submit a new event
        event_service = EventService("http://localhost:5000")
        tok = '#%s' % random.randint(1,10000)
        test_message='event_test_%s'% tok
        event = Event(test_message, event_type='test-event-type')
        res = event_service.submit(self.api_key, event, scope=scope, source_type=source_type)
        assert res['id'] is not None

    def test_submit_scoped_event(self): 
        self.test_submit_event(Scope("scoped-testhost", "testdevice"))

if __name__ == '__main__':
    unittest.main()
        
