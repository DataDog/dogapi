"""
Full client-side comment client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class EventService(APIService):

    def query(self, start, end, priority=None, sources=None, tags=None):

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

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/events/' + str(id), params, None)

    def post(self, title, text, date_happened=None, handle=None, priority=None, related_event_id=None, tags=None):

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

        return self.request('POST', '/api/' + API_VERSION + '/events', params, body, send_json=True)
