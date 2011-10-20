"""
Full client-side comment client
See facade.py for a simpler wrapper
"""
import logging
import simplejson

from dogapi.common import APIService

API_VERSION="v1"

class DashService(APIService):
    """
    Create, modify, and delete dashboards.

    :param api_key: your org's API key
    :type api_key: string

    :param application_key: your application key
    :type application_key: string

    :param timeout: seconds before timing out a request
    :type timeout: integer

    :param timeout_counter: shared timeout counter
    :type timeout_counter: :class:`dogapi.common.SharedCounter`
    """

    def get(self, dash_id):
        """
        Get a dashboard definition.

        :param dash_id: id of the dash to get
        :type dash_id: integer

        :return: dashboard definition
        :rtype: decoded JSON
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/dash/' + str(dash_id), params, None)

    def get_all(self):
        """
        Get a summary (id, title, resource, description) of all dashboards for an Org.

        :return: list of dashboard titles and resource URLs
        :rtype: decoded JSON (list of dicts)
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/dash', params, None)


    def create(self, title, description, graphs):
        """
        Create a new dashboard.

        :param title: tile for the new dashboard
        :type title: string

        :param description: description of the new dashboard
        :type description: string

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.SimpleClient.dashboard`)
        :type graphs: decoded JSON

        :return: new dashboard
        :rtype: decoded JSON
        """

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
        """
        Update an existing dashboard.

        :param dash_id: dash to update
        :type dash_id: integer

        :param title: new tile for the dashboard
        :type title: string

        :param description: new description for the dashboard
        :type description: string

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.SimpleClient.dashboard`). replaces existing graphs.
        :type graphs: decoded JSON

        :return: dashboard
        :rtype: decoded JSON
        """

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
        """
        Delete a dashboard.

        :param dash_id: dash to delete
        :type dash_id: integer
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('DELETE', '/api/' + API_VERSION + '/dash/' + str(dash_id), params, None)
