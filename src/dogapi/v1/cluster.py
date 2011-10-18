"""
Full client-side cluster client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class ClusterService(APIService):
    """
    Add and remove hosts from clusters.

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
        Get a list of clusters for your org and their member hosts.

        :return: cluster list
        :rtype: decoded JSON
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/clusters/hosts', params)

    def get(self, host_id):
        """
        Get a list of clusters for the specified host by name or id.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :return: clusters the host belongs to
        :rtype: decoded JSON
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('GET', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params)

    def add(self, host_id, clusters):
        """
        Add a host to one or more clusters.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param clusters: cluster names
        :type clusters: list
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'clusters': clusters,
        }

        return self.request('POST', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params, body, send_json=True)

    def update(self, host_id, clusters):
        """
        Remove a host from all existing clusters and add it to one or more new clusters.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param clusters: cluster names
        :type clusters: list
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = {
            'clusters': clusters,
        }

        return self.request('PUT', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params, body, send_json=True)

    def detatch(self, host_id):
        """
        Remove a host from all clusters.

        :param host_id: id or name of the host
        :type host_id: integer or string
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        return self.request('DELETE', '/api/' + API_VERSION + '/clusters/hosts/' + str(host_id), params)
