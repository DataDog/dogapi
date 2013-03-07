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
        return self.http_request('GET', '/search', q=query,
            response_formatter=lambda x: x['results'],
        )

    def all_tags(self, source=None):
        """
        Get a list of tags for your org and their member hosts.

        >>> dog_http_api.all_tags()
        [ { 'tag1': [ 'host1', 'host2', ... ] }, ... ]
        """
        params = {}
        if source:
            params['source'] = source
        return self.http_request('GET', '/tags/hosts',
            response_formatter=lambda x: x['tags'],
            **params
        )

    def host_tags(self, host_id, source=None, by_source=False):
        """
        Get a list of tags for the specified host by name or id.

        >>> dog_http_api.host_tags('web.example.com')
        ['web', 'env:production']
        >>> dog_http_api.host_tags(1234)
        ['database', 'env:test']
        """
        params = {}
        if source:
            params['source'] = source
        if by_source:
            params['by_source'] = 'true'
        return self.http_request('GET', '/tags/hosts/' + str(host_id),
            response_formatter=lambda x: x['tags'],
            **params
        )

    def add_tags(self, host_id, tags, source=None):
        """add_tags(host_id, [tag1, tag2, ...])
        Add one or more tags to a host.

        >>> dog_http_api.add_tags(host_id, ['env:test'])
        >>> dog_http_api.add_tags(host_id, ['env:test', 'database'])
        """
        if isinstance(tags, basestring):
            tags = [tags]
        body = {
            'tags': tags,
        }
        params = {}
        if source:
            params['source'] = source
        return self.http_request('POST', '/tags/hosts/' + str(host_id), body,
            response_formatter=lambda x: x['tags'],
            **params
        )

    def change_tags(self, host_id, tags, source=None):
        """change_tags(host_id, [tag1, tag2, ...])
        Replace a host's tags with one or more new tags.

        >>> dog_http_api.change_tags(host_id, ['env:test'])
        >>> dog_http_api.change_tags(host_id, ['env:test', 'database'])
        """
        if isinstance(tags, basestring):
            tags = [tags]
        body = {
            'tags': tags
        }
        params = {}
        if source:
            params['source'] = source
        return self.http_request('PUT', '/tags/hosts/' + str(host_id), body,
            response_formatter=lambda x: x['tags'],
            **params
        )

    def detach_tags(self, host_id, source=None):
        """
        Remove all tags from a host.

        >>> dog_http_api.detach_tags(123)
        """
        params = {}
        if source:
            params['source'] = source
        return self.http_request('DELETE', '/tags/hosts/' + str(host_id),
            **params
        )
