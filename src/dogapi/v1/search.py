"""
Full client-side search client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class SearchService(APIService):

    def __init__(self, api_key, application_key, api_host):
        self.api_key = api_key
        self.application_key = application_key
        self.api_host = api_host

    def query_host(self, name):

        params = {
            'api_key':  self.api_key,
            'application_key': self.application_key,
            'name':     name,
        }

        return self.request('GET', '/api/' + API_VERSION + '/search/host', params, None)

    def query_metric(self, name):

        params = {
            'api_key':  self.api_key,
            'application_key': self.application_key,
            'name':     name,
        }

        return self.request('GET', '/api/' + API_VERSION + '/search/metric', params, None)
