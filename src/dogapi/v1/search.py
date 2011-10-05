"""
Full client-side search client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class SearchService(APIService):

    def query(self, query):

        params = {
            'api_key':  self.api_key,
            'application_key': self.application_key,
            'q':     query,
        }

        return self.request('GET', '/api/' + API_VERSION + '/search', params, None)
