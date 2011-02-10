# python
import random, math
import datetime
import unittest

# nose
from nose.plugins.skip import SkipTest

# dogclient
from dogclient.event import EventService, Scope, Event


class TestEventClient(unittest.TestCase):

    def setUp(self):
        self.api_key = "apikey_3"
            
    def test_submit_event(self, scope=None, source_type=None):
        # create and submit a new event
        event_service = EventService("localhost:5000")
        tok = '#%s' % random.randint(1,10000)
        test_message='event_test_%s'% tok
        event = Event(test_message, event_type='test-event-type')
        res = event_service.submit(self.api_key, event, scope=scope, source_type=source_type)
        assert res['id'] is not None

    def test_submit_scoped_event(self): 
        self.test_submit_event(Scope("scoped-testhost", "testdevice"))

    def test_typed_event(self):
        self.test_submit_event(Scope("typed-testhost", "testdevice"), source_type="Nagios")
        self.test_submit_event(Scope("typed-testhost", "testdevice"), source_type="GitHub")

if __name__ == '__main__':
    unittest.main()
        
