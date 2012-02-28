__all__ = [
    'EventApi',
]

class EventApi(object):
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
        Get details for an individual event.

        :param id: numeric event id
        :type id: integer

        :return: event details (see https://github.com/DataDog/dogapi/wiki/Event for structure)
        :rtype: decoded JSON
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
        ''' No response, async interface by default
        '''
        self._event(*args, **kwargs)

    def event_with_response(self, *args, **kwargs):
        return self._event(*args, **kwargs)

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
        Delete a comment.

        :param comment_id: comment to delete
        :type comment_id: integer

        :raises: Exception on error
        """
        response = self.http_request('DELETE', '/comments/' + str(comment_id))
        if self.json_responses:
            return response
        else:
            return None




