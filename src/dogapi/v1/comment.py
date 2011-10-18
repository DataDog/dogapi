"""
Full client-side comment client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class CommentService(APIService):
    """
    Post, edit, and delete comments.

    :param api_key: your org's API key
    :type api_key: string

    :param application_key: your application key
    :type application_key: string

    :param timeout: seconds before timing out a request
    :type timeout: integer

    :param timeout_counter: shared timeout counter
    :type timeout_counter: :class:`dogapi.common.SharedCounter`
    """

    def post(self, handle, message, related_event_id=None):
        """
        Post a comment.

        :param handle: user handle to post the comment as
        :type handle: string

        :param message: comment message
        :type message: string

        :param related_event_id: if set, comment will be posted as a reply to the specified comment or event
        :type related_event_id: integer

        :return: the newly created comment
        :rtype: decoded JSON
        """
        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'handle':  handle,
            'message': message,
        }
        if related_event_id is not None:
            body['related_event_id'] = int(related_event_id)

        return self.request('POST', '/api/' + API_VERSION + '/comments', params, body, send_json=True)

    def edit(self, comment_id, handle, message, related_event_id=None):
        """
        Update an existing comment.

        :param comment_id: comment to update
        :type comment_id: integer

        :param handle: user handle to post the comment as
        :type handle: string

        :param message: comment message
        :type message: string

        :param related_event_id: if set, comment will be posted as a reply to the specified comment or event
        :type related_event_id: integer

        :return: the updated comment
        :rtype: decoded JSON
        """
        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'handle':  handle,
            'message': message,
        }
        if related_event_id is not None:
            body['related_event_id'] = int(related_event_id)
        else:
            body['related_event_id'] = None

        return self.request('PUT', '/api/' + API_VERSION + '/comments/' + str(comment_id), params, body, send_json=True)

    def delete(self, comment_id):
        """
        Delete a comment.

        :param comment_id: comment to delete
        :type comment_id: integer
        """
        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('DELETE', '/api/' + API_VERSION + '/comments/' + str(comment_id), params)
