import argparse
from dogapi.search import SearchService

def main():
    parser = argparse.ArgumentParser(description='Interact with the Datadog API',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(title='Modes')

    parser_search = subparsers.add_parser('search', help='search datadog')
    subparsers_search = parser_search.add_subparsers(title='Search domains', help='sub-command help')

    parser_search_hosts = subparsers_search.add_parser('host', help='search datadog for hosts')
    parser_search_hosts.add_argument('name', help='hostname or hostname fragment to match. implicit wildcards (e.g. *name*).')
    parser_search_hosts.set_defaults(func=search_hosts)

    parser_search_metrics = subparsers_search.add_parser('metric', help='search datadog for metrics')
    parser_search_metrics.add_argument('name', help='metric name or metric name fragment to match. implicit wildcards (e.g. *name*).')
    parser_search_metrics.set_defaults(func=search_metrics)

    args = parser.parse_args()
    args.func(args)

apikey = 'apikey_2'
hosturl = 'http://localhost:5000'

def search_hosts(args):
    svc = SearchService(hosturl)
    res = svc.query_host(apikey, args.name)
    for host in res['hosts']:
        print host['name']

def search_metrics(args):
    svc = SearchService(hosturl)
    res = svc.query_metric(apikey, args.name)
    for metric in res['metrics']:
        print metric['name']

if __name__=='__main__':
    main()
