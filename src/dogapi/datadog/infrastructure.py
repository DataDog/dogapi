
class InfrastructureApi(object):
    def search(self, query):
        """
        Search datadog for hosts and metrics by name.

        :param query: search query can either be faceted to limit the results (e.g. ``"host:foo"``, or ``"metric:bar"``) or un-faceted, which will return results of all types (e.g. ``"baz"``)
        :type query: string

        :return: a dictionary maping each queried facet to a list of name strings
        :rtype: dictionary
        """
        response = self.request('GET', '/search', q=query)
        return response['results']

    def all_tags(self):
        """
        Get a list of tags for your org and their member hosts.

        :return: [ { 'tag1': [ 'host1', 'host2', ... ] }, ... ]
        :rtype: list
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        
        response = self.request('GET', '/tags/hosts')
        return response['tags']

    def host_tags(self, host_id):
        """
        Get a list of tags for the specified host by name or id.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :return: tags for the host
        :rtype: list
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        
        response = self.request('GET', '/tags/hosts/' + str(host_id))
        return response['tags']

    def add_tags(self, host_id, *tags):
        """add_tags(host_id, tag1, [tag2, [...]])
        Add one or more tags to a host.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tagN: tag name
        :type tagN: string
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        body = {
            'tags': tags,
        }
        response = self.request('POST', '/tags/hosts/' + str(host_id), body)

    def change_tags(self, host_id, *tags):
        """change_tags(host_id, tag1, [tag2, [...]])
        Replace a host's tags with one or more new tags.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param tagN: tag name
        :type tagN: string
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        body = {
            'tags': tags
        }
        return self.request('PUT', '/tags/hosts/' + str(host_id), body)

    def detach_tags(self, host_id):
        """
        Remove all tags from a host.

        :param host_id: id or name of the host
        :type host_id: integer or string
        """
        if self.api_key is None or self.application_key is None:
            self._report_error("Tag API requires api and application keys")
            return
        
        return self.request('DELETE', '/tags/hosts/' + str(host_id))
