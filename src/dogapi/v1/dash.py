"""
Full client-side comment client
See facade.py for a simpler wrapper
"""
import logging
import simplejson

from dogapi.common import APIService

API_VERSION="v1"

class DashService(APIService):

    def __init__(self, api_key, application_key, api_host):
        self.api_key = api_key
        self.application_key = application_key
        self.api_host = api_host

    def get_all(self):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/dashboards', params, None)

    def get(self, dash_id):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/dash/' + str(dash_id), params, None)

    def create(self, title, description, graphs):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        if type(graphs) == basestring:
            graphs = simplejson.loads(graphs)

        body = {
            'title':  title,
            'description': description,
            'graphs': graphs,
        }

        return self.request('POST', '/api/' + API_VERSION + '/dash', params, body, send_json=True)

    def update(self, dash_id, title, description, graphs):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        if type(graphs) == basestring:
            graphs = simplejson.loads(graphs)

        body = {
            'title':  title,
            'description': description,
            'graphs': graphs,
        }

        return self.request('PUT', '/api/' + API_VERSION + '/dash/' + str(dash_id), params, body, send_json=True)

    def delete(self, dash_id):

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('DELETE', '/api/' + API_VERSION + '/dash/' + str(dash_id), params, None)
