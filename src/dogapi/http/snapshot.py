__all__ = [
    'SnapshotApi',
]


class SnapshotApi(object):

    def graph_snapshot(self, metric_query, start, end,
                       event_query=None, graph_def=None):
        """
        Take a snapshot of a graph, returning the full url to the snapshot.
        Values for `start` and `end` are given in seconds since the epoch.

        >>> end = int(time.time())
        >>> start = end - 60 * 60
        >>> dog_http_api.snapshot("system.load.1{*}", start, end)

        Optional:
            event_query:    an event query to overlay on the graph
            graph_def:      a graph definition to snapshot custom graphs
                            if present, it overrides metric_query, useful
                            to obtaining snapshots of non-trivial charts
        """
        query_params = {
            'metric_query': metric_query,
            'start': start,
            'end': end
        }

        if event_query:
            query_params['event_query'] = event_query

        if graph_def:
            query_params['graph_def'] = graph_def

        return self.http_request('GET', '/graph/snapshot', **query_params)
