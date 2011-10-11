import time, datetime
from socket import timeout

from dogapi.common import SharedCounter

from v1 import *

class SimpleClient(object):
    """
    A high-level client for interacting with the Datadog API.
    """

    def __init__(self):
        self.api_key = None
        self.application_key = None
        self.datadog_host = 'https://app.datadoghq.com'
        self.max_timeouts = 3
        self.timeout_counter = SharedCounter()



    #
    # Metric API

    def metric(self, name, value, host=None, device=None):
        """
        Submit a single data point to the metric API.
        
        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param value: data point value
        :type value: numeric

        :param host: optional host to scope the metric (e.g. ``"hostA.example.com"``)
        :type host: string
        
        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Metric API requires api and application keys")
        s = MetricService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        now = time.mktime(datetime.datetime.now().timetuple())
        r = s.post(name, [[now, value]], host=host, device=device)
        if r.has_key('errors'):
            raise Exception(r['errors'])

    def metrics(self, name, values, host=None, device=None):
        """
        Submit a series of data points to the metric API.
        
        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param values: data series. list of (POSIX timestamp, intever value) tuples. (e.g. ``[(1317652676, 15), (1317652706, 18), ...]``)
        :type values: list

        :param host: optional host to scope the metric (e.g. ``"hostA.example.com"``)
        :type host: string
        
        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Metric API requires api and application keys")
        s = MetricService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        if device:
            r = s.post(name, values, host=host, device=device)
        else:
            r = s.post(name, values, host=host)
        if r.has_key('errors'):
            raise Exception(r['errors'])

    #
    # Comment API

    def comment(self, handle, message, comment_id=None, related_event_id=None):
        """
        Post or edit a comment.

        :param handle: user handle to post the comment as
        :type handle: string

        :param message: comment message
        :type message: string

        :param comment_id: if set, comment will be updated instead of creating a new comment
        :type comment_id: integer

        :param related_event_id: if set, comment will be posted as a reply to the specified comment or event
        :type related_event_id: integer

        :return: comment id
        :rtype: integer

        :raises:  Exception on failure
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Comment API requires api and application keys")
        s = CommentService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        if comment_id is None:
            r = s.post(handle, message, related_event_id)
        else:
            r = s.edit(comment_id, handle, message, related_event_id)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['comment']['id']

    def delete_comment(self, comment_id):
        """
        Delete a comment.


        :param comment_id: comment to delete
        :type comment_id: integer

        :raises: Exception on error
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Comment API requires api and application keys")
        s = CommentService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.delete(comment_id)
        if r.has_key('errors'):
            raise Exception(r['errors'])

    #
    # Cluster API

    def all_clusters(self):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get_all()
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['clusters']

    def host_clusters(self, host_id):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get(host_id)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['clusters']

    def add_clusters(self, host_id, *args):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.add(host_id, args)
        if r.has_key('errors'):
            raise Exception(r['errors'])

    def change_clusters(self, host_id, *args):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.update(host_id, args)
        if r.has_key('errors'):
            raise Exception(r['errors'])

    def detatch_clusters(self, host_id):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.detatch(host_id)
        if r.has_key('errors'):
            raise Exception(r['errors'])

    #
    # Stream API

    def stream(self, start, end, priority=None, sources=None, tags=None):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Event API requires api and application keys")
        s = EventService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.query(start, end, priority, sources, tags)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['events']

    def get_event(self, id):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Event API requires api and application keys")
        s = EventService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get(id)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['event']

    def event(self, title, text, date_happened=None, handle=None, priority=None, related_event_id=None, tags=None):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Event API requires api and application keys")
        s = EventService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.post(title, text, date_happened, handle, priority, related_event_id, tags)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['event']['id']

    #
    # Dash API

    def dashboard(self, dash_id):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get(dash_id)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['dash']

    def create_dashboard(self, title, description, graphs):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.create(title, description, graphs)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['dash']['id']

    def update_dashboard(self, dash_id, title, description, graphs):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.update(dash_id, title, description, graphs)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['dash']['id']

    def delete_dashboard(self, dash_id):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.delete(dash_id)
        if r.has_key('errors'):
            raise Exception(r['errors'])

    #
    # Search API

    def search(self, query):
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            raise Exception("Search API requires api and application keys")
        s = SearchService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.query(query)
        if r.has_key('errors'):
            raise Exception(r['errors'])
        return r['results']
