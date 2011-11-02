"""
Full client-side tag client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class TagService(APIService):
    """
    Tag and untag hosts

    :param api_key: your org's API key
    :type api_key: string

    :param application_key: your application key
    :type application_key: string

    :param timeout: seconds before timing out a request
    :type timeout: integer

    :param timeout_counter: shared timeout counter
    :type timeout_counter: :class:`dogapi.common.SharedCounter`
    """

    def get_all(self):
        """
        Get a list of tags for your org and their member hosts.

        :return: tag list
        :rtype: decoded JSON
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/tags/hosts', params)

    def get(self, host_id):
        """
        Get a list of tags for the specified host by name or id.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :return: tags the host belongs to
        :rtype: decoded JSON
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/tags/hosts/' + str(host_id), params)

    def add(self, host_id, tags):
        """
        Add one or more tags to a host.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tags: tag names
        :type tags: list
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'tags': tags,
        }

        return self.request('POST', '/api/' + API_VERSION + '/tags/hosts/' + str(host_id), params, body, send_json=True)

    def update(self, host_id, tags):
        """
        Replace all of a hosts tags with a new set.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tags: tags names
        :type tags: list
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'tags': tags,
        }

        return self.request('PUT', '/api/' + API_VERSION + '/tags/hosts/' + str(host_id), params, body, send_json=True)

    def detach(self, host_id):
        """
        Remove all tags from a host.

        :param host_id: id or name of the host
        :type host_id: integer or string
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('DELETE', '/api/' + API_VERSION + '/tags/hosts/' + str(host_id), params)
