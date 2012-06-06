__all__ = [
    'EventApi',
]

class EventApi(object):
    def stream(self, start, end, priority=None, sources=None, tags=None):
        """
        Get the events that occurred between the *start* and *end* POSIX timestamps,
        optional filtered by *priority* ("low" or "normal"), *sources* and
        *tags*.

        See the `event API documentation <http://api.datadoghq.com/events>`_ for the
        event data format.

        >>> dog_http_api.stream(1313769783, 131378000, sources=["nagios"])
        { "events": [
            {
              "id": "event-1",
              "title": "my first event",
              "priority": "normal",
              "handle": "alq@datadoghq.com",
              "date_happened": 1313769783,
              "source": "nagios",
              "alert_type": "ok",
              "is_aggregate": true,
              "children": [
                {
                  "id": "event-100",
                  "date_happened": 123459833,
                  "alert_type": "error"
                }, ...
              ]
            }, ...
          ]
        }
        """
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

        response = self.http_request('GET', '/events', **params)
        if self.json_responses:
            return response
        else:
            return response['events']

    def get_event(self, id):
        """
        Get details for an individual event with the given *id*.

        See the `event API documentation <http://api.datadoghq.com/events>`_ for the
        event data format.

        >>> dog_http_api.get_event("event-1")
        {
          "id": "event-1",
          "title": "my first event",
          "priority": "normal",
          "handle": "alq@datadoghq.com",
          "date_happened": 1313769783,
          "source": "nagios",
          "alert_type": "ok",
          "is_aggregate": true,
          "children": [
            {
              "id": "event-100",
              "date_happened": 123459833,
              "alert_type": "error"
            }, ...
          ]
        }
        """
        response = self.http_request('GET', '/events/' + str(id))
        if self.json_responses:
            return response
        else:
            return response['event']

    def _event(self, title, text, date_happened=None, handle=None, priority=None, related_event_id=None, tags=None, host=None, device_name=None, **kwargs):
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

        response = self.http_request('POST', '/events', body)
        if self.json_responses:
            return response
        else:
            return response['event']['id']

    def event(self, *args, **kwargs):
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
        self._event(*args, **kwargs)

    def event_with_response(self, *args, **kwargs):
        return self._event(*args, **kwargs)

    def comment(self, handle, message, comment_id=None, related_event_id=None):
        """
        Post a comment *message* as the user with *handle*. Edit a comment by including it's *comment_id*.
        Reply to a related event by setting the *related_event_id*.

        >>> dog_http_api.comment("matt", "Hey! Something strange is going on.")
        """
        body = {
            'handle':  handle,
            'message': message,
        }
        if related_event_id is not None:
            body['related_event_id'] = int(related_event_id)
        response = self.http_request('POST', '/comments', body)

        if self.json_responses:
            return response
        else:
            return response['comment']['id']

    def update_comment(self, handle, message, comment_id):
        body = {
            'handle':  handle,
            'message': message,
        }
        response = self.http_request('PUT', '/comments/%s' % comment_id, body)
        if self.json_responses:
            return response
        else:
            return response['comment']['id']


    def delete_comment(self, comment_id):
        """
        Delete a comment with the given *comment_id*.

        >>> dog_http_api.delete_comment('1234')
        """
        response = self.http_request('DELETE', '/comments/' + str(comment_id))
        if self.json_responses:
            return response
        else:
            return None
