__all__ = [
    'SnapshotApi',
]

class SnapshotApi(object):

    def graph_snapshot(self, metric_query, start, end, event_query=None):
        """
        Take a snapshot of a graph, returning the full url to the snapshot.
        Values for `start` and `end` are given in seconds since the epoch.

        >>> end = int(time.time())
        >>> start = end - 60 * 60
        >>> dog_http_api.snapshot("system.load.1{*}", start, end)
        """
        query_params = {
            'metric_query': metric_query,
            'start': start,
            'end': end,
            'event_query': event_query
        }

        return self.http_request('GET', '/graph/snapshot', **query_params)
