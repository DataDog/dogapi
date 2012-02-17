import os
import logging
import socket
import re
import sys
import time, datetime
import types
import httplib
import urllib2
from urllib import urlencode
from decorator import decorator
try:
    import simplejson as json
except ImportError:
    import json

from dogapi.common import TimeoutManager

log = logging.getLogger('dogapi')

import ssl
timeout_exceptions = (socket.timeout, ssl.SSLError)

class Datadog(object):
    """
    A high-level client for interacting with the Datadog API.

    By default, service calls to the simple client silently swallow any exceptions
    before they escape from the library. To disable this behavior, simply set the
    `swallow` attribute of your :class:`~dogapi.Datadog` instance to `False`.

    The default timeout is 2 seconds, but that can be changed by setting the
    client's `timeout` attribute.
    """

    def __init__(self, api_key=None, application_key=None, api_version='v1', api_host=None, timeout=2, max_timeouts=3, backoff_period=300, swallow=True, use_ec2_instance_id=False):
        self.api_host = api_host or os.environ.get('DATADOG_HOST', 'https://app.datadoghq.com')
        self.api_key = api_key
        self.api_version = api_version
        self.application_key = application_key
        self.timeout = timeout
        self.timeout_manager = TimeoutManager(backoff_period, max_timeouts)
        self.swallow = swallow
        self._default_host = socket.gethostname()
        self._use_ec2_instance_id = None
        self.use_ec2_instance_id = use_ec2_instance_id
    
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

    def request(self, method, path, body=None, **params):
        if not self.timeout_manager.should_submit():
            self._report_error("Too many timeouts. Won't try again for {1} seconds.".format(*self.timeout_manager.backoff_status()))
            return None
        
        match = re.match('^(https?)://(.*)', self.api_host)
        http_conn_cls = httplib.HTTPSConnection

        if match:
            host = match.group(2)
            if match.group(1) == 'http':
                http_conn_cls = httplib.HTTPConnection

        conn = http_conn_cls(host)
        url_params = {}
        if self.api_key:
            url_params['api_key'] = self.api_key
        if self.application_key:
            url_params['application_key'] = self.application_key
        url_params.update(params)
        url = "/api/%s/%s?%s" % (self.api_version, path.lstrip('/'), urlencode(url_params))
        
        headers = {}
        if isinstance(body, dict):
            body = json.dumps(body)
            headers['Content-Type'] = 'application/json'
                
        try:
            try:
                conn.request(method, url, body, headers)
            except timeout_exceptions:
                self.timeout_manager.report_timeout()
                self._report_error('%s %s timed out after %d seconds.' % (method, url, self.timeout))
                return None
            
            response = conn.getresponse()
            response_str = response.read()
            if response_str:
                try:
                    response_obj = json.loads(response_str)
                except ValueError:
                    raise ValueError('Invalid JSON response: {0}'.format(response_str))
                
                if response_obj and 'errors' in response_obj:
                    self._report_error(response_obj['errors'])
            else:
                response_obj = {}
            return response_obj
        finally:
            conn.close()        

    @_swallow_exceptions
    def metric(self, name, points, host=None, device=None):
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
        if self.api_key is None:
            self._report_error("Metric API requires an api key")
            return
                
        if host is None:
            host = self._default_host
        
        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        now = time.mktime(datetime.datetime.now().timetuple())
        if isinstance(points, (float, int)):
            points = [(now, points)]
        elif isinstance(points, tuple):
            points = [points]
        
        body = { "series": [
            {
            'metric': name,
            'points': [[x[0], x[1]] for x in points],
            'type': "gauge",
            'host': host,
            'device': device,
            }
            ]
        }
        
        return self.request('POST', '/series', body)

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
        if self.api_key is None:
            self._report_error("Metric API requires an api key")
            return
        
        body = { "series": [
            {
            'metric': name,
            'points': [[x[0], x[1]] for x in points],
            'type': mtype,
            'host': host,
            'device': device,
            } for name, points in values.items()
            ]
        }
        
        return self.request('POST', '/series', body)
        

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
        if self.api_key is None or self.application_key is None:
            self._report_error("Comment API requires api and application keys")
            return
        
        body = {
            'handle':  handle,
            'message': message,
        }
        url = '/comments'
        method = 'POST'
        if related_event_id is not None:
            body['related_event_id'] = int(related_event_id)
        response = self.request(method, url, body)
        return response['comment']['id']

    @_swallow_exceptions
    def update_comment(self, handle, message, comment_id):
        if self.api_key is None or self.application_key is None:
            self._report_error("Comment API requires api and application keys")
            return
        
        body = {
            'handle':  handle,
            'message': message,
        }
        method = 'PUT'
        response = self.request('PUT', '/comments/%s' % comment_id, body)
        return response['comment']['id']


    @_swallow_exceptions
    def delete_comment(self, comment_id):
        """
        Delete a comment.

        :param comment_id: comment to delete
        :type comment_id: integer

        :raises: Exception on error
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Comment API requires api and application keys")
            return
        return self.request('DELETE', '/comments/' + str(comment_id))

    #
    # Tag API

    @_swallow_exceptions
    def all_tags(self):
        """
        Get a list of tags for your org and their member hosts.

        :return: [ { 'tag1': [ 'host1', 'host2', ... ] }, ... ]
        :rtype: list
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        
        response = self.request('GET', '/tags/hosts')
        return response['tags']

    @_swallow_exceptions
    def host_tags(self, host_id):
        """
        Get a list of tags for the specified host by name or id.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :return: tags for the host
        :rtype: list
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        
        response = self.request('GET', '/tags/hosts/' + str(host_id))
        return response['tags']

    @_swallow_exceptions
    def add_tags(self, host_id, *tags):
        """add_tags(host_id, tag1, [tag2, [...]])
        Add one or more tags to a host.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tagN: tag name
        :type tagN: string
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        body = {
            'tags': tags,
        }
        response = self.request('POST', '/tags/hosts/' + str(host_id), body)

    @_swallow_exceptions
    def change_tags(self, host_id, *tags):
        """change_tags(host_id, tag1, [tag2, [...]])
        Replace a host's tags with one or more new tags.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tagN: tag name
        :type tagN: string
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        body = {
            'tags': tags
        }
        return self.request('PUT', '/tags/hosts/' + str(host_id), body)

    @_swallow_exceptions
    def detach_tags(self, host_id):
        """
        Remove all tags from a host.

        :param host_id: id or name of the host
        :type host_id: integer or string
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        
        return self.request('DELETE', '/tags/hosts/' + str(host_id))

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
        if self.api_key is None or self.application_key is None:
            self._report_error("Event API requires api and application keys")
            return

        params = {
            'start': start,
            'end': end,
        }        
        if priority:
            params['priority'] = priority
        if sources:
            params['sources'] = ','.join(sources)
        if tags:
            params['tags'] = ','.join(tags)

        response = self.request('GET', '/events', **params)
        return response['events']

    @_swallow_exceptions
    def get_event(self, id):
        """
        Get details for an individual event.

        :param id: numeric event id
        :type id: integer

        :return: event details (see https://github.com/DataDog/dogapi/wiki/Event for structure)
        :rtype: decoded JSON
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Event API requires api and application keys")
            return
        
        response = self.request('GET', '/events/' + str(id))
        return response['event']

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
        if self.api_key is None:
            self._report_error("Event API requires api key")
            return
        
        body = {
            'title': title,
            'text': text,
        }

        if date_happened is not None:
            body['date_happened'] = date_happened

        if handle is not None:
            body['handle'] = handle

        if priority is not None:
            body['priority'] = priority

        if related_event_id is not None:
            body['related_event_id'] = related_event_id

        if tags is not None:
            body['tags'] = ','.join(tags)

        if host is not None:
            body['host'] = host

        if device_name is not None:
            body['device_name'] = device_name
        
        body.update(kwargs)

        response = self.request('POST', '/events', body)
        return response['event']['id']

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
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        response = self.request('GET', '/dash/' + str(dash_id))
        return response['dash']

    @_swallow_exceptions
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
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        
        if isinstance(graphs, (str, unicode)):
            graphs = json.loads(graphs)
        body = {
            'title': title,
            'description': description,
            'graphs': graphs
        }
        response = self.request('POST', '/dash', body)
        return response['dash']['id']

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

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.Datadog.dashboard`). replaces existing graphs.
        :type graphs: decoded JSON

        :return: dashboard's id
        :rtype: integer
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        
        if isinstance(graphs, (str, unicode)):
            graphs = json.loads(graphs)
        body = {
            'title': title,
            'description': description,
            'graphs': graphs
        }
        response = self.request('PUT', '/dash/' + str(dash_id), body)
        return response['dash']['id']

    @_swallow_exceptions
    def delete_dashboard(self, dash_id):
        """
        Delete a dashboard.

        :param dash_id: dash to delete
        :type dash_id: integer
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
            return
        self.request('DELETE', '/dash/' + str(dash_id))

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
        response = self.request('GET', '/search', q=query)
        return response['results']
