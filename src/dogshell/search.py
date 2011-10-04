from dogapi.v1 import SearchService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class SearchClient(CommandLineClient):

    def __init__(self, apikey, appkey):
        self.apikey = apikey
        self.appkey = appkey

    def setup_parser(self, subparsers):
        parser_search = subparsers.add_parser('search', help='search datadog')
        subparsers_search = parser_search.add_subparsers(title='Search domains', help='sub-command help')

        parser_search_hosts = subparsers_search.add_parser('host', help='search datadog for hosts')
        parser_search_hosts.add_argument('name', help='hostname or hostname fragment to match. implicit wildcards (e.g. *name*).')
        parser_search_hosts.set_defaults(func=self.search_hosts)

        parser_search_metrics = subparsers_search.add_parser('metric', help='search datadog for metrics')
        parser_search_metrics.add_argument('name', help='metric name or metric name fragment to match. implicit wildcards (e.g. *name*).')
        parser_search_metrics.set_defaults(func=self.search_metrics)

    def search_hosts(self, args):
        svc = SearchService(hosturl)
        res = svc.query_host(self.apikey, args.name)
        report_warnings(res)
        if report_errors(res):
            return
        for host in res['hosts']:
            print host['name']

    def search_metrics(self, args):
        svc = SearchService(hosturl)
        res = svc.query_metric(self.apikey, args.name)
        report_warnings(res)
        if report_errors(res):
            return
        for metric in res['metrics']:
            print metric['name']
