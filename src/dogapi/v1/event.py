"""
Full client-side comment client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

# Extra kwargs supported by POST
SUPPORTED_POST_ARGS = ["event_type", "event_object", "alert_type", "source_type", "source_type_name"]

class EventService(APIService):
    """
    Post to and read from the stream.

    :param api_key: your org's API key
    :type api_key: string

    :param application_key: your application key
    :type application_key: string

    :param timeout: seconds before timing out a request
    :type timeout: integer

    :param timeout_counter: shared timeout counter
    :type timeout_counter: :class:`dogapi.common.SharedCounter`
    """

    def query(self, start, end, priority=None, sources=None, tags=None):
        """
        Get a filtered event stream.

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
            'api_key':         self.api_key,
            'application_key': self.application_key,
            'start':           start,
            'end':             end,
        }

        if priority is not None:
            params['priority'] = priority

        if sources is not None:
            params['sources'] = ','.join(sources)

        if tags is not None:
            params['tags'] = ','.join(tags)

        return self.request('GET', '/api/' + API_VERSION + '/events', params, None)

    def get(self, id):
        """
        Get details for an individual event.

        :param id: numeric event id
        :type id: integer

        :return: event details (see https://github.com/DataDog/dogapi/wiki/Event for structure)
        :rtype: decoded JSON
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/events/' + str(id), params, None)

    def post(self, title, text, date_happened=None, handle=None, priority=None, related_event_id=None, tags=None, host=None, device_name=None, **kwargs):
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

        :return: posted event
        :rtype: decoded JSON
        """


        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

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

        for kwarg in kwargs:
            if kwarg in SUPPORTED_POST_ARGS:
                body[kwarg] = kwargs[kwarg]
            else:
                logging.warning("Argument %s is not supported" % kwarg)

        return self.request('POST', '/api/' + API_VERSION + '/events', params, body, send_json=True)
