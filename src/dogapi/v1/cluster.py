"""
Full client-side cluster client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class ClusterService(APIService):

    def get_all(self):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/clusters/hosts', params)

    def get(self, host_id):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params)

    def add(self, host_id, clusters):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'clusters': clusters,
        }

        return self.request('POST', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params, body, send_json=True)

    def update(self, host_id, clusters):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'clusters': clusters,
        }

        return self.request('PUT', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params, body, send_json=True)

    def detatch(self, host_id):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('DELETE', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params)
