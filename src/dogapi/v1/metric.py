"""
Full client-side comment client
See facade.py for a simpler wrapper
"""
import logging
import simplejson

from dogapi.common import APIService

API_VERSION="v1"

class MetricService(APIService):

    def __init__(self, api_key, application_key, api_host):
        self.api_key = api_key
        self.application_key = application_key
        self.api_host = api_host

    def post(self, metric_name, points, mtype="gauge", host=None, device=None):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = { "series": [
            {
            'metric': metric_name,
            'points': [[int(x[0]), int(x[1])] for x in points],
            'type': mtype,
            'host': host,
            'device': device,
            }
            ]
        }

        return self.request('POST', '/api/' + API_VERSION + '/series', params, body, send_json=True)
