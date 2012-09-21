__all__ = [
    'DashApi',
]

try:
    import simplejson as json
except ImportError:
    import json

class DashApi(object):
    def dashboard(self, dash_id):
        """
        Return the dashboard with the given id.

        See the `dashboard API documentation <http://docs.datadoghq.com/dashboards>`_ for the
        dashboard data format.
        """
        response = self.http_request('GET', '/dash/' + str(dash_id))
        if self.json_responses:
            return response
        else:
            return response['dash']

    def dashboards(self):
        """
        Return all of your dashboards.

        See the `dashboard API documentation <http://docs.datadoghq.com/dashboards>`_ for the
        dashboard data format.
        """
        response = self.http_request('GET', '/dash')
        if self.json_responses:
            return response
        else:
            return response['dashes']


    def create_dashboard(self, title, description, graphs):
        """
        Create a new dashboard with the given *title*, *description* and *graphs*.

        See the `dashboard API documentation <http://docs.datadoghq.com/dashboards>`_ for the
        dashboard data format.
        """
        if isinstance(graphs, str):
            graphs = json.loads(graphs)
        body = {
            'title': title,
            'description': description,
            'graphs': graphs
        }
        response = self.http_request('POST', '/dash', body)
        if self.json_responses:
            return response
        else:
            return response['dash']['id']

    def update_dashboard(self, dash_id, title, description, graphs):
        """
        Update the dashboard whose id is  *dash_id*, replacing it's *title*, *description* and *graphs*.
        Return the dashboard with the given id.

        See the `dashboard API documentation <http://docs.datadoghq.com/dashboards>`_ for the
        dashboard data format.
        """
        if isinstance(graphs, str):
            graphs = json.loads(graphs)
        body = {
            'title': title,
            'description': description,
            'graphs': graphs
        }
        response = self.http_request('PUT', '/dash/' + str(dash_id), body)
        if self.json_responses:
            return response
        else:
            return response['dash']['id']

    def delete_dashboard(self, dash_id):
        """
        Delete the dashboard with the given *dash_id*.

        >>> dog_http_api.delete_dashboard(dash_id)
        """
        response = self.http_request('DELETE', '/dash/' + str(dash_id))
        if self.json_responses:
            return response
        else:
            return None

