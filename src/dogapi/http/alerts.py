__all__ = [
    'AlertApi',
]

class AlertApi(object):

    def alert(self, query, name=None, message=None, silenced=False,
            notify_no_data=None, timeout_h=None):
        """
        Create a new metric alert for the given *query*. If *name* is unset,
        the alert will be given a name based on the query. The *message* will
        accompany any notifications sent for the alert and can contain the same
        '@' notation as events to alert individual users. The *silenced* flag
        controls whether or not notifications are sent for alert state changes.

        >>> dog_http_api.alert("sum(last_1d):sum:system.net.bytes_rcvd{host:host0} > 100")
        """
        body = {
            'query':  query,
            'silenced': silenced,
        }
        if name:
            body['name'] = name
        if message:
            body['message'] = message
        if notify_no_data:
            body['notify_no_data'] = notify_no_data
        if timeout_h:
            body['timeout_h'] = timeout_h

        return self.http_request('POST', '/alert', body,
            response_formatter=lambda x: x['id'],
        )

    def update_alert(self, alert_id, query, name=None, message=None, silenced=False,
            notify_no_data=None, timeout_h=None):
        """
        Update the metric alert identified by *alert_id* with the given
        *query*. If *name* is unset, the alert will be given a name based on
        the query. The *message* will accompany any notifications sent for the
        alert and can contain the same '@' notation as events to alert
        individual users. The *silenced* flag controls whether or not
        notifications are sent for alert state changes.

        >>> dog_http_api.update_alert(1234, "sum(last_1d):sum:system.net.bytes_rcvd{host:host0} > 100")
        """
        body = {
            'query':  query,
            'silenced': silenced,
        }
        if name:
            body['name'] = name
        if message:
            body['message'] = message
        if notify_no_data:
            body['notify_no_data'] = notify_no_data
        if timeout_h:
            body['timeout_h'] = timeout_h

        return self.http_request('PUT', '/alert/%s' % alert_id, body,
            response_formatter=lambda x: x['id'],
        )

    def get_alert(self, alert_id):
        """
        Get the details for the metric alert identified by *alert_id*.

        >>> dog_http_api.get_alert(1234)
        """

        return self.http_request('GET', '/alert/%s' % alert_id)

    def delete_alert(self, alert_id):
        """
        Delete the metric alert identified by *alert_id*.

        >>> dog_http_api.delete_alert(1234)
        """

        return self.http_request('DELETE', '/alert/%s' % alert_id)

    def get_all_alerts(self):
        """
        Get the details for all metric alerts.

        >>> dog_http_api.get_all_alert()
        """

        return self.http_request('GET', '/alert',
            response_formatter=lambda x: x['alerts'],
        )

    def mute_alerts(self):
        """
        Mute all alerts.

        >>> dog_http_api.mute_alerts()
        """

        return self.http_request('POST', '/mute_alerts')

    def unmute_alerts(self):
        """
        Unmute all alerts.

        >>> dog_http_api.unmute_alerts()
        """

        return self.http_request('POST', '/unmute_alerts')
