# python
import random, math
from datetime import datetime as dt
from datetime import timedelta as delta
import unittest

# nose
from nose.plugins.skip import SkipTest

# dogapi
from dogapi.metric import MetricService, Scope
from dogapi.search import SearchService

class TestSearchClient(unittest.TestCase):

    def setUp(self):
        self.api_key = "apikey_2"
        self.host = "http://localhost:5000"

        # create and submit a new event
        metric_service = MetricService(self.host)
        scope = Scope("test.dogapi.searchtest", "eth0")
        metric = 'test.dogapi.metric.search_metric'
        points = [
            (dt.now()-delta(seconds=90), 1.0),
            (dt.now()-delta(seconds=60), 2.0),
            (dt.now()-delta(seconds=30), 4.0),
            (dt.now(),                   8.0)
        ]
        res = metric_service.submit(self.api_key, scope, metric, points)
        assert res['status'] == 'ok'

    def test_search_metric(self):
        search_service = SearchService(self.host)
        res = search_service.query_metric(self.api_key, 'load')
        assert res['status'] == 'ok'
        assert len(res['metrics']) == 3
        for m in res['metrics']:
            assert 'load' in m['name']

    def test_search_host(self):
        search_service = SearchService(self.host)
        res = search_service.query_host(self.api_key, 'saffron')
        assert res['status'] == 'ok'
        assert len(res['hosts']) >= 1
        for m in res['hosts']:
            assert 'saffron' in m['name']

if __name__ == '__main__':
    unittest.main()
