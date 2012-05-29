try:
    import simplejson as json
except ImportError:
    import json

from dogshell.common import report_errors, report_warnings, CommandLineClient

class SearchClient(CommandLineClient):

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('search', help='search datadog')
        verb_parsers = parser.add_subparsers(title='Verbs')

        query_parser = verb_parsers.add_parser('query', help='Search datadog.')
        query_parser.add_argument('query', help='optionally faceted search query')
        query_parser.set_defaults(func=self._query)

    def _query(self, args):
        self.dog.timeout = args.timeout
        res = self.dog.search(args.query)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            for facet, results in list(res['results'].items()):
                for idx, result in enumerate(results):
                    if idx == 0:
                        print('\n')
                        print("%s\t%s" % (facet, result))
                    else:
                        print("%s\t%s" % (' '*len(facet), result))
        elif format == 'raw':
            print(json.dumps(res))
        else:
            for facet, results in list(res['results'].items()):
                for result in results:
                    print("%s\t%s" % (facet, result))
