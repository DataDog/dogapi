class DashApi(object):
    def dashboard(self, dash_id):
        """
        Get a dashboard definition.

        :param dash_id: id of the dash to get
        :type dash_id: integer

        :return: dashboard definition (see https://github.com/DataDog/dogapi/wiki/Dashboard for details)
        :rtype: decoded JSON
        """
        response = self.request('GET', '/dash/' + str(dash_id))
        return response['dash']

    def create_dashboard(self, title, description, graphs):
        """
        Create a new dashboard.

        :param title: tile for the new dashboard
        :type title: string

        :param description: description of the new dashboard
        :type description: string

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.Datadog.dashboard`)
        :type graphs: decoded JSON

        :return: new dashboard's id
        :rtype: integer
        """        
        if isinstance(graphs, (str, unicode)):
            graphs = json.loads(graphs)
        body = {
            'title': title,
            'description': description,
            'graphs': graphs
        }
        response = self.request('POST', '/dash', body)
        return response['dash']['id']

    def update_dashboard(self, dash_id, title, description, graphs):
        """
        Update an existing dashboard.

        :param dash_id: dash to update
        :type dash_id: integer

        :param title: new tile for the dashboard
        :type title: string

        :param description: new description for the dashboard
        :type description: string

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.Datadog.dashboard`). replaces existing graphs.
        :type graphs: decoded JSON

        :return: dashboard's id
        :rtype: integer
        """
        if isinstance(graphs, (str, unicode)):
            graphs = json.loads(graphs)
        body = {
            'title': title,
            'description': description,
            'graphs': graphs
        }
        response = self.request('PUT', '/dash/' + str(dash_id), body)
        return response['dash']['id']

    def delete_dashboard(self, dash_id):
        """
        Delete a dashboard.

        :param dash_id: dash to delete
        :type dash_id: integer
        """
        self.request('DELETE', '/dash/' + str(dash_id))