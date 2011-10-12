from dogapi.v1 import SearchService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class SearchClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser_search = subparsers.add_parser('search', help='search datadog')
        parser_search.add_argument('query', help='string to search for. accepts faceted or un-faceted queries. see https://github.com/DataDog/dogapi/wiki/Search for the latest on the query language.')
        parser_search.set_defaults(r_func=self.r_search)
        parser_search.set_defaults(p_func=self.p_search)
        parser_search.set_defaults(l_func=self.l_search)

    def _search(self, query):
        svc = SearchService(self.config['apikey'], self.config['appkey'])
        res = svc.query(query)
        return res

    def r_search(self, args):
        res = self._search(args.query)
        report_warnings(res)
        report_errors(res)
        print res

    def p_search(self, args):
        res = self._search(args.query)
        report_warnings(res)
        report_errors(res)
        for facet, results in res['results'].items():
            for idx, result in enumerate(results):
                if idx == 0:
                    print '\n'
                    print "%s\t%s" % (facet, result)
                else:
                    print "%s\t%s" % (' '*len(facet), result)

    def l_search(self, args):
        res = self._search(args.query)
        report_warnings(res)
        report_errors(res)
        for facet, results in res['results'].items():
            for result in results:
                print "%s\t%s" % (facet, result)

