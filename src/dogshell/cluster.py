import sys

from dogapi.v1 import ClusterService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class ClusterClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('cluster', help='View and modify host clusters.')
        verb_parsers = parser.add_subparsers(title='Verbs')

        add_parser = verb_parsers.add_parser('add', help='Add a host to one or more clusters.', description='Hosts can be specified by name or id.')
        add_parser.add_argument('host', help='host to add')
        add_parser.add_argument('cluster', help='cluster to add host to (one or more, space separated)', nargs='+')
        add_parser.set_defaults(func=self._add)

        replace_parser = verb_parsers.add_parser('replace', help='Replace all clusters with one or more new clusters.', description='Hosts can be specified by name or id.')
        replace_parser.add_argument('host', help='host to modify')
        replace_parser.add_argument('cluster', help='cluster to add host to (one or more, space separated)', nargs='+')
        replace_parser.set_defaults(func=self._replace)

        show_parser = verb_parsers.add_parser('show', help='Show host clusters.', description='Hosts can be specified by name or id.')
        show_parser.add_argument('host', help='host to show (or "all" to show all clusters)')
        show_parser.set_defaults(func=self._show)

        detatch_parser = verb_parsers.add_parser('detatch', help='Remove a host from all clusters.', description='Hosts can be specified by name or id.')
        detatch_parser.add_argument('host', help='host to detatch')
        detatch_parser.set_defaults(func=self._detatch)

    def _add(self, args):
        format = args.format
        svc = ClusterService(self.config['apikey'], self.config['appkey'])
        res = svc.add(args.host, args.cluster)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print "Clusters for '%s':" % res['host']
            for c in res['clusters']:
                print '  ' + c
        elif format == 'raw':
            print res
        else:
            for c in res['clusters']:
                print c

    def _replace(self, args):
        format = args.format
        svc = ClusterService(self.config['apikey'], self.config['appkey'])
        res = svc.update(args.host, args.cluster)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print "Clusters for '%s':" % res['host']
            for c in res['clusters']:
                print '  ' + c
        elif format == 'raw':
            print res
        else:
            for c in res['clusters']:
                print c

    def _show(self, args):
        format = args.format
        svc = ClusterService(self.config['apikey'], self.config['appkey'])
        if args.host == 'all':
            res = svc.get_all()
        else:
            res = svc.get(args.host)
        report_warnings(res)
        report_errors(res)
        if args.host == 'all':
            if format == 'pretty':
                for cluster, hosts in res['clusters'].items():
                    for host in hosts:
                        print cluster
                        print '  ' + host
                    print
            elif format == 'raw':
                print res
            else:
                for cluster, hosts in res['clusters'].items():
                    for host in hosts:
                        print cluster + '\t' + host
        else:
            if format == 'pretty':
                for cluster in res['clusters']:
                    print cluster
            elif format == 'raw':
                print res
            else:
                for cluster in res['clusters']:
                    print cluster

    def _detatch(self, args):
        format = args.format
        svc = ClusterService(self.config['apikey'], self.config['appkey'])
        res = svc.detatch(args.host)
        report_warnings(res)
        report_errors(res)
        if format == 'raw':
            print res
