__all__ = [
    'DowntimeApi',
    'MonitorApi',
    'MonitorType',
]

from dogapi.constants import MonitorType
from dogapi.exceptions import ApiError

class MonitorApi(object):

    def monitor(self, mtype, query, name=None, message=None, options=None):
        """
        Create a new monitor of type *mtype* with the given *name* and *query*.
        The *message* will accompany any notifications sent for the alert and
        can contain the same '@' notation as events to alert individual users.
        The *options* argument is a dictionary of settings for the monitor.
        See the Datadog API documentation for a break down of available options.

        >>> dog_http_api.monitor("metric alert", "sum(last_1d):sum:system.net.bytes_rcvd{host:host0} > 100")
        """
        mtype = mtype.lower()
        if mtype not in MonitorType.ALL:
            raise ApiError('Invalid monitor type, expected one of %s' \
                    % ', '.join(MonitorType.ALL))

        body = {
            'type': mtype,
            'name': name,
            'query': query,
        }

        if name:
            body['name'] = name
        if message:
            body['message'] = message
        if options:
            if not isinstance(options, dict):
                raise ApiError('Invalid type for `options`, expected `dict`.')
            body['options'] = options

        return self.http_request('POST', '/monitor', body,
            response_formatter=lambda x: x['id'],
        )

    def update_monitor(self, monitor_id, query, name=None, message=None,
        options=None):
        """
        Update the monitor identified by *monitor_id* with the given *query*.
        The *message* will accompany any notifications sent for the alert and
        can contain the same '@' notation as events to alert individual users.
        The *options* argument is a dictionary of settings for the monitor.
        See the Datadog API documentation for a break down of available options.

        >>> dog_http_api.update_monitor(1234, "sum(last_1d):sum:system.net.bytes_rcvd{host:host0} > 200")
        """
        body = {
            'query': query
        }
        if name:
            body['name'] = name
        if message:
            body['message'] = message
        if options:
            body['options'] = options

        return self.http_request('PUT', '/monitor/%s' % monitor_id, body,
            response_formatter=lambda x: x['id'],
        )

    def get_monitor(self, monitor_id):
        """
        Get the details for the monitor identified by *monitor_id*.

        >>> dog_http_api.get_monitor(1234)
        """

        return self.http_request('GET', '/monitor/%s' % monitor_id)

    def delete_monitor(self, monitor_id):
        """
        Delete the monitor identified by *monitor_id*.

        >>> dog_http_api.delete_monitor(1234)
        """

        return self.http_request('DELETE', '/monitor/%s' % monitor_id)

    def get_all_monitors(self, include_state=False):
        """
        Get the details for all monitors. If *include_state* is set to True then
        the response will include the state of each active group in the alert.

        >>> dog_http_api.get_all_monitors()
        """

        return self.http_request('GET', '/monitor')

    def mute_monitors(self):
        """
        Mute all monitors.

        >>> dog_http_api.mute_monitors()
        """

        return self.http_request('POST', '/monitor/mute_all')

    def unmute_monitors(self):
        """
        Unmute all monitors.

        >>> dog_http_api.unmute_monitors()
        """

        return self.http_request('POST', '/monitor/unmute_all')

    def mute_monitor(self, monitor_id, scope=None, end=None):
        """
        Mute the monitor identified by *monitor_id*. If a *scope* is given your
        mute will just apply to that scope. You can give an *end* argument that
        is a POSIX timestamp of when the mute should stop.

        >>> dog_http_api.mute_monitor(1234, scope='env:staging')
        """
        body = {}
        if scope:
            body['scope'] = scope
        if end:
            body['end'] = end
        return self.http_request('POST', '/monitor/%s/mute' % monitor_id, body)

    def unmute_monitor(self, monitor_id, scope=None):
        """
        Unmute the monitor identified by *monitor_id*. If a *scope* is given
        your unmute will just apply to that scope.

        >>> dog_http_api.unmute_monitors(1234, scope='env:staging')
        """
        body = {}
        if scope:
            body['scope'] = scope
        return self.http_request('POST', '/monitor/%s/unmute' % monitor_id, body)


class DowntimeApi(object):

    def schedule_downtime(self, scope, start, end=None):
        """
        Schedule downtime over *scope* from *start* to *end*, where *start* and
        *end* are POSIX timestamps. If *end* is omitted then the downtime will
        continue until cancelled.
        """
        body = {
            'scope': scope,
            'start': start,
            'end': end
        }
        return self.http_request('POST', '/downtime', body,
            response_formatter=lambda x: x['id'],
        )

    def get_downtime(self, downtime_id):
        """
        Get the downtime identified by *downtime_id*
        """
        return self.http_request('GET', '/downtime/%s' % downtime_id)

    def cancel_downtime(self, downtime_id):
        """
        Cancel the downtime identified by *downtime_id*
        """
        return self.http_request('DELETE', '/downtime/%s' % downtime_id)

    def list_downtime(self):
        """
        List all scheduled downtimes.
        """
        return self.http_request('GET', '/downtime')
