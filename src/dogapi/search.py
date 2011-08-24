"""
Full client-side search client
See facade.py for a simpler wrapper
"""
import logging

from common import Service

API_VERSION="v1"

class SearchService(Service):

    def query_host(self, api_key, name):

        params = {
            'api_key':  api_key,
            'name':     name,
        }

        return self.request('GET', '/api/' + API_VERSION + '/search/host', params)

    def query_metric(self, api_key, name):

        params = {
            'api_key':  api_key,
            'name':     name,
        }

        return self.request('GET', '/api/' + API_VERSION + '/search/metric', params)
