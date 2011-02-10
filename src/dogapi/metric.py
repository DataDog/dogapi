"""
Full client-side metrics client
See facade.py for a simpler wrapper
"""
import logging
import json

from common import Service, Scope, dt2epoch

API_VERSION="1.0.0"

class MetricService(Service):
    def submit(self, api_key, scope, metric, points):
        
        series = [{
            'host':             scope.host,
            'device':           scope.device,
            'metric':           metric,
            'points':           [(dt2epoch(p[0]), p[1]) for p in points]
        }]
        
        params = {
            'api_key':          api_key,
            'api_version':      API_VERSION,
            'series':           json.dumps(series)
        }
        
        return self.request('POST', '/series/submit', params)
        
