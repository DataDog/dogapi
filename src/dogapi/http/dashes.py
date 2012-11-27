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
        return self.http_request('GET', '/dash/' + str(dash_id),
            response_formatter=lambda x: x['dash'],
        )

    def dashboards(self):
        """
        Return all of your dashboards.

        See the `dashboard API documentation <http://docs.datadoghq.com/dashboards>`_ for the
        dashboard data format.
        """
        return self.http_request('GET', '/dash',
            response_formatter=lambda x: x['dashes'],
        )


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
        return self.http_request('POST', '/dash', body,
            response_formatter=lambda x: x['dash']['id'],
        )

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
        return self.http_request('PUT', '/dash/' + str(dash_id), body,
            response_formatter=lambda x: x['dash']['id'],
        )

    def delete_dashboard(self, dash_id):
        """
        Delete the dashboard with the given *dash_id*.

        >>> dog_http_api.delete_dashboard(dash_id)
        """
        return self.http_request('DELETE', '/dash/' + str(dash_id))
