# python
import random, math
from datetime import datetime as dt
from datetime import timedelta as delta
import unittest

# nose
from nose.plugins.skip import SkipTest

# dogapi
from dogapi.metric import MetricService, Scope

class TestMetricClient(unittest.TestCase):

    def setUp(self):
        self.api_key = "apikey_3"
        self.host = "http://localhost:5000"
            
    # deprecated - matt
    @SkipTest
    def test_submit_metric(self):
        # create and submit a new event
        metric_service = MetricService(self.host)
        scope = Scope("test.dogapi.fake", "eth0")
        metric = 'test.dogapi.metric.submit_metric'
        points = [
            (dt.now()-delta(seconds=90), 1.0), 
            (dt.now()-delta(seconds=60), 2.0), 
            (dt.now()-delta(seconds=30), 4.0),             
            (dt.now(),                   8.0)
        ]
        res = metric_service.submit(self.api_key, scope, metric, points)
        assert res['status'] == 'ok'
        assert len(res['results']) == 1, 'res=%s' % res
        r = res['results'][0]
        assert r['host'] == scope.host, 'res=%s' % res
        if scope.device:    assert r['device'] == scope.device, 'res=%s' % res
        assert r['metric'] == metric, 'res=%s' % res
        assert r['length'] == len(points), 'res=%s' % res
            
if __name__ == '__main__':
    unittest.main()
