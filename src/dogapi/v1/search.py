"""
Full client-side search client
See facade.py for a simpler wrapper
"""
import logging

from dogapi.common import APIService

API_VERSION="v1"

class SearchService(APIService):
    """
    Search for hosts and metrics.

    :param api_key: your org's API key
    :type api_key: string

    :param application_key: your application key
    :type application_key: string

    :param timeout: seconds before timing out a request
    :type timeout: integer

    :param timeout_counter: shared timeout counter
    :type timeout_counter: :class:`dogapi.common.SharedCounter`
    """

    def query(self, query):
        """
        Search datadog for hosts and metrics by name.

        :param query: search query can either be faceted to limit the results (e.g. ``"host:foo"``, or ``"metric:bar"``) or un-faceted, which will return results of all types (e.g. ``"baz"``)
        :type query: string

        :return: matched entities by type
        :rtype: decoded JSON
        """

        params = {
            'api_key':  self.api_key,
            'application_key': self.application_key,
            'q':     query,
        }

        return self.request('GET', '/api/' + API_VERSION + '/search', params, None)
