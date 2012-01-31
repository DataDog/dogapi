import logging
import socket
import sys
import time, datetime
import types
import urllib2
from decorator import decorator

from dogapi.common import SharedCounter, TimeoutManager
from v1 import *

log = logging.getLogger('dogapi')

class SimpleClient(object):
    """
    A high-level client for interacting with the Datadog API.

    By default, service calls to the simple client silently swallow any exceptions
    before they escape from the library. To disable this behavior, simply set the
    `swallow` attribute of your :class:`~dogapi.SimpleClient` instance to `False`.

    The default timeout is 2 seconds, but that can be changed by setting the
    client's `timeout` attribute.
    """

    def __init__(self):
        self.api_key = None
        self.application_key = None
        self.timeout = 2
        self.swallow = True
        self.timeout_manager = TimeoutManager()
        # FIXME: preserved for backwards compatability. remove when no longer
        # accessed in templeton
        self.max_timeouts = 3
        self.timeout_counter = SharedCounter()
        self._use_ec2_instance_id = False
        self._default_host = socket.gethostname()
    
    def use_ec2_instance_id():
        def fget(self):
            return self._use_ec2_instance_id
        
        def fset(self, value):
            self._use_ec2_instance_id = value

            if value:
                try:
                    # Remember the previous default timeout
                    old_timeout = socket.getdefaulttimeout()

                    # Try to query the EC2 internal metadata service, but fail fast
                    socket.setdefaulttimeout(0.25)

                    try:
                        host = urllib2.urlopen(urllib2.Request('http://169.254.169.254/latest/meta-data/instance-id')).read()
                    finally:
                        # Reset the previous default timeout
                        socket.setdefaulttimeout(old_timeout)
                except Exception:
                    host = socket.gethostname()

                self._default_host = host
            else:
                self._default_host = socket.gethostname()
        
        def fdel(self):
            del self._use_ec2_instance_id
        
        return locals()
    use_ec2_instance_id = property(**use_ec2_instance_id())

    @decorator
    def _swallow_exceptions(f, self, *args, **kwargs):
        if self.swallow is True:
            try:
                return f(self, *args, **kwargs)
            except Exception, e:
                self._report_error(str(e))
        else:
            return f(self, *args, **kwargs)

    def _report_error(self, message):
        if self.swallow:
            log.error(message)
        else:
            raise Exception(message)

    #
    # Metric API

    @_swallow_exceptions
    def metric(self, name, value, host=None, device=None):
        """
        Submit a single data point to the metric API.

        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param value: data point value
        :type value: numeric

        :param host: optional host to scope the metric (e.g.
        ``"hostA.example.com"``). defaults to local hostname. to submit without
        a host, explicitly set host=None.
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None:
            self._report_error("Metric API requires an api key")
            return

        # FIXME import typecheck more elegant than this
        # Check type of value since .metric and .metrics can easily by confused
        if type(value) not in (types.FloatType, types.IntType):
            self._report_error(".metric takes a scalar value not a %s. You might want to use .metrics instead" % type(value))
            return
        
        if host is None:
            host = self._default_host
        s = MetricService(self.api_key, self.application_key, timeout=self.timeout)
        now = time.mktime(datetime.datetime.now().timetuple())
        try:
            r = s.post(name, [[now, value]], host=host, device=device)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])

    @_swallow_exceptions
    def metrics(self, name, values, host=None, device=None):
        """
        Submit a series of data points to the metric API.

        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param values: data series. list of (POSIX timestamp, intever value) tuples. (e.g. ``[(1317652676, 15), (1317652706, 18), ...]``)
        :type values: list

        :param host: optional host to scope the metric (e.g.
        ``"hostA.example.com"``). defaults to local hostname. to submit without
        a host, explicitly set host=None.
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None:
            self._report_error("Metric API requires an api key")
            return

        # FIXME import typecheck more elegant than this
        if type(values) not in (types.ListType, types.TupleType):
            self._report_error(".metrics takes a list of pairs not a %s. You might want to use .metric instead to send a scalar value" % type(values))
            return

        if host is None:
            host = self._default_host
        s = MetricService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            if device:
                r = s.post(name, values, host=host, device=device)
            else:
                r = s.post(name, values, host=host)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])

    @_swallow_exceptions
    def batch_metrics(self, values, host=None, device=None):
        """
        Submit a series of metrics with 1 or more data points to the metric API

        :param values A dictionary of names to a list values, in the form of {name: [(POSIX timestamp, integer value), ...], name2: [(POSIX timestamp, integer value), ...]}
        :type values: dict

        :param host: optional host to scope the metric (e.g.
        ``"hostA.example.com"``). to submit without a host, explicitly set
        host=None.
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None:
            self._report_error("Metric API requires an api key")
            return

        if host is None:
            host = self._default_host
        s = MetricService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            if device:
                r = s.post_batch(values, host=host, device=device)
            else:
                r = s.post_batch(values, host=host)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return

    #
    # Comment API

    @_swallow_exceptions
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
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Comment API requires api and application keys")
            return
        s = CommentService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            if comment_id is None:
                r = s.post(handle, message, related_event_id)
            else:
                r = s.edit(comment_id, handle, message, related_event_id)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['comment']['id']

    @_swallow_exceptions
    def delete_comment(self, comment_id):
        """
        Delete a comment.

        :param comment_id: comment to delete
        :type comment_id: integer

        :raises: Exception on error
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Comment API requires api and application keys")
            return
        s = CommentService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.delete(comment_id)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])

    #
    # Tag API

    @_swallow_exceptions
    def all_tags(self):
        """
        Get a list of tags for your org and their member hosts.

        :return: [ { 'tag1': [ 'host1', 'host2', ... ] }, ... ]
        :rtype: list
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        s = TagService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.get_all()
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['tags']

    @_swallow_exceptions
    def host_tags(self, host_id):
        """
        Get a list of tags for the specified host by name or id.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :return: tags for the host
        :rtype: list
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        s = TagService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.get(host_id)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['tags']

    @_swallow_exceptions
    def add_tags(self, host_id, *args):
        """add_tags(host_id, tag1, [tag2, [...]])
        Add one or more tags to a host.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tagN: tag name
        :type tagN: string
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        s = TagService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.add(host_id, args)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])

    @_swallow_exceptions
    def change_tags(self, host_id, *args):
        """change_tags(host_id, tag1, [tag2, [...]])
        Replace a host's tags with one or more new tags.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tagN: tag name
        :type tagN: string
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        s = TagService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.update(host_id, args)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])

    @_swallow_exceptions
    def detach_tags(self, host_id):
        """
        Remove all tags from a host.

        :param host_id: id or name of the host
        :type host_id: integer or string
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        s = TagService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.detach(host_id)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])

    #
    # Stream API

    @_swallow_exceptions
    def stream(self, start, end, priority=None, sources=None, tags=None):
        """
        Get an event stream, optionally filtered.

        :param start: start date for the stream query (POSIX timestamp)
        :type start: integer

        :param end: end date for the stream query (POSIX timestamp)
        :type end: integer

        :param priority: show only events of the given priority ("low" or "normal")
        :type priority: string

        :param sources: show only events for the give sources (see
                        https://github.com/DataDog/dogapi/wiki/Event
                        for an up-to-date list of available sources)
        :type sources: list of strings

        :param tags: show only events for the given tags
        :type tags: list of strings

        :return: list of events (see https://github.com/DataDog/dogapi/wiki/Event for structure)
        :rtype: decoded JSON
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Event API requires api and application keys")
            return
        s = EventService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.query(start, end, priority, sources, tags)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['events']

    @_swallow_exceptions
    def get_event(self, id):
        """
        Get details for an individual event.

        :param id: numeric event id
        :type id: integer

        :return: event details (see https://github.com/DataDog/dogapi/wiki/Event for structure)
        :rtype: decoded JSON
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Event API requires api and application keys")
            return
        s = EventService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.get(id)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['event']

    @_swallow_exceptions
    def event(self, title, text, date_happened=None, handle=None, priority=None, related_event_id=None, tags=None, host=None, device_name=None, **kwargs):
        """
        Post an event.

        :param title: title for the new event
        :type title: string

        :param text: event message
        :type text: string

        :param date_happened: when the event occurred. if unset defaults to the current time. (POSIX timestamp)
        :type date_happened: integer

        :param handle: user to post the event as. defaults to owner of the application key used to submit.
        :type handle: string

        :param priority: priority to post the event as. ("normal" or "low", defaults to "normal")
        :type priority: string

        :param related_event_id: post event as a child of the given event
        :type related_event_id: id

        :param tags: tags to post the event with
        :type tags: list of strings

        :param host: host to post the event with
        :type host: list of strings

        :param device_name: device_name to post the event with
        :type device_name: list of strings

        :return: new event id
        :rtype: integer
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None:
            self._report_error("Event API requires api key")
            return
        s = EventService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.post(title, text, date_happened, handle, priority, related_event_id, tags, host, device_name, **kwargs)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['event']['id']

    #
    # Dash API

    @_swallow_exceptions
    def dashboard(self, dash_id):
        """
        Get a dashboard definition.

        :param dash_id: id of the dash to get
        :type dash_id: integer

        :return: dashboard definition (see https://github.com/DataDog/dogapi/wiki/Dashboard for details)
        :rtype: decoded JSON
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        s = DashService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.get(dash_id)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['dash']

    @_swallow_exceptions
    def create_dashboard(self, title, description, graphs):
        """
        Create a new dashboard.

        :param title: tile for the new dashboard
        :type title: string

        :param description: description of the new dashboard
        :type description: string

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.SimpleClient.dashboard`)
        :type graphs: decoded JSON

        :return: new dashboard's id
        :rtype: integer
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        s = DashService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.create(title, description, graphs)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['dash']['id']

    @_swallow_exceptions
    def update_dashboard(self, dash_id, title, description, graphs):
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

        :return: dashboard's id
        :rtype: integer
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        s = DashService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.update(dash_id, title, description, graphs)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['dash']['id']

    @_swallow_exceptions
    def delete_dashboard(self, dash_id):
        """
        Delete a dashboard.

        :param dash_id: dash to delete
        :type dash_id: integer
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        s = DashService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.delete(dash_id)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])

    #
    # Search API

    @_swallow_exceptions
    def search(self, query):
        """
        Search datadog for hosts and metrics by name.

        :param query: search query can either be faceted to limit the results (e.g. ``"host:foo"``, or ``"metric:bar"``) or un-faceted, which will return results of all types (e.g. ``"baz"``)
        :type query: string

        :return: a dictionary maping each queried facet to a list of name strings
        :rtype: dictionary
        """
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return
        if self.api_key is None or self.application_key is None:
            self._report_error("Search API requires api and application keys")
            return
        s = SearchService(self.api_key, self.application_key, timeout=self.timeout)
        try:
            r = s.query(query)
        except socket.timeout:
            self.timeout_manager.report_timeout()
            self._report_error('Client timed out after %d seconds.' % self.timeout)
            return
        if r.has_key('errors'):
            self._report_error(r['errors'])
            return
        return r['results']
