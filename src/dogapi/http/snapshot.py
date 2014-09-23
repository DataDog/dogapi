__all__ = [
    'SnapshotApi',
]


class SnapshotApi(object):

    def graph_snapshot(self, metric_query, start, end, event_query=None):
        """
        Take a snapshot of a graph, returning the full url to the snapshot.
        Values for `start` and `end` are given in seconds since the epoch.
        An optional event query can be provided to overlay events on the graph.

        >>> end = int(time.time())
        >>> start = end - 60 * 60
        >>> dog_http_api.snapshot("system.load.1{*}", start, end)
        """
        query_params = {
            'metric_query': metric_query,
            'start': start,
            'end': end
        }

        if event_query:
            query_params['event_query'] = event_query

        return self.http_request('GET', '/graph/snapshot', **query_params)

    def graph_snapshot_from_def(self, graph_def, start, end):
        """
        Take a snapshot of a graph from a graph definition, returning the
        full url to the snapshot. Values for `start` and `end` are given in
        seconds since the epoch.

        >>> end = int(time.time())
        >>> start = end - 60 * 60
        >>> graph_def = json.dumps({
            "requests": [{
                "q": "system.load.1{*}"
            }, {
                "q": "system.load.5{*}"
            }],
            "viz": "timeseries",
            "events": [{
                "q": "*"
            }]
        })
        >>> dog_http_api.snapshot(graph_def, start, end)
        """
        query_params = {
            'graph_def': graph_def,
            'start': start,
            'end': end
        }

        return self.http_request('GET', '/graph/snapshot', **query_params)
