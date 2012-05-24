__all__ = [
    'InfrastructureApi',
]

class InfrastructureApi(object):
    def search(self, query):
        """
        Search datadog for hosts and metrics by name. The search *query* can be
        faceted to limit the results (e.g. ``"host:foo"``, or ``"metric:bar"``)
        or un-faceted, which will return results of all types (e.g. ``"baz"``).
        Return a dictionary mapping each queried facet to a list of name
        strings.

        >>> dog_http_api.search("cassandra")
        { "results": {
            "hosts": ["cassandraHostA", "cassandraHostB", ...],
            "metrics": ["cassandra.load", "cassandra.requests", ...]
          }
        }
        """
        response = self.http_request('GET', '/search', q=query)
        if self.json_responses:
            return response
        else:
            return response['results']

    def all_tags(self):
        """
        Get a list of tags for your org and their member hosts.

        >>> dog_http_api.all_tags()
        [ { 'tag1': [ 'host1', 'host2', ... ] }, ... ]
        """
        response = self.http_request('GET', '/tags/hosts')
        if self.json_responses:
            return response
        else:
            return response['tags']

    def host_tags(self, host_id):
        """
        Get a list of tags for the specified host by name or id.

        >>> dog_http_api.host_tags('web.example.com')
        ['web', 'env:production']
        >>> dog_http_api.host_tags(1234)
        ['database', 'env:test']
        """
        response = self.http_request('GET', '/tags/hosts/' + str(host_id))
        if self.json_responses:
            return response
        else:
            return response['tags']

    def add_tags(self, host_id, *tags):
        """add_tags(host_id, tag1, [tag2, [...]])
        Add one or more tags to a host.

        >>> dog_http_api.add_tags(host_id, 'env:test')
        >>> dog_http_api.add_tags(host_id, 'env:test', 'database')
        """
        body = {
            'tags': tags,
        }
        response = self.http_request('POST', '/tags/hosts/' + str(host_id), body)
        if self.json_responses:
            return response
        else:
            return response['tags']

    def change_tags(self, host_id, *tags):
        """change_tags(host_id, tag1, [tag2, [...]])
        Replace a host's tags with one or more new tags.

        >>> dog_http_api.change_tags(host_id, 'env:test')
        >>> dog_http_api.change_tags(host_id, 'env:test', 'database')
        """
        body = {
            'tags': tags
        }
        response = self.http_request('PUT', '/tags/hosts/' + str(host_id), body)
        if self.json_responses:
            return response
        else:
            return response['tags']

    def detach_tags(self, host_id):
        """
        Remove all tags from a host.

        >>> dog_http_api.detach_tags(123)
        """
        response = self.http_request('DELETE', '/tags/hosts/' + str(host_id))
        if self.json_responses:
            return response
        else:
            return None


