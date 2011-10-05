from dogapi.v1 import SearchService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class SearchClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser_search = subparsers.add_parser('search', help='search datadog')
        parser_search.add_argument('query', help='string to search for. accepts faceted or un-faceted queries. see https://github.com/DataDog/dogapi/wiki/Search for the latest on the query language.')
        parser_search.set_defaults(func=self.search)

    def search(self, args):
        svc = SearchService(self.config['apikey'], self.config['appkey'])
        res = svc.query(args.query)
        report_warnings(res)
        if report_errors(res):
            return
        for facet, results in res['results'].items():
            for result in results:
                print "%s\t%s" % (facet, result)

