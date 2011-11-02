import sys

import simplejson

from dogapi.v1 import TagService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class TagClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('tag', help='View and modify host tags.')
        verb_parsers = parser.add_subparsers(title='Verbs')

        add_parser = verb_parsers.add_parser('add', help='Add a host to one or more tags.', description='Hosts can be specified by name or id.')
        add_parser.add_argument('host', help='host to add')
        add_parser.add_argument('tag', help='tag to add host to (one or more, space separated)', nargs='+')
        add_parser.set_defaults(func=self._add)

        replace_parser = verb_parsers.add_parser('replace', help='Replace all tags with one or more new tags.', description='Hosts can be specified by name or id.')
        replace_parser.add_argument('host', help='host to modify')
        replace_parser.add_argument('tag', help='tag to add host to (one or more, space separated)', nargs='+')
        replace_parser.set_defaults(func=self._replace)

        show_parser = verb_parsers.add_parser('show', help='Show host tags.', description='Hosts can be specified by name or id.')
        show_parser.add_argument('host', help='host to show (or "all" to show all tags)')
        show_parser.set_defaults(func=self._show)

        detach_parser = verb_parsers.add_parser('detach', help='Remove a host from all tags.', description='Hosts can be specified by name or id.')
        detach_parser.add_argument('host', help='host to detach')
        detach_parser.set_defaults(func=self._detach)

    def _add(self, args):
        format = args.format
        svc = TagService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.add(args.host, args.tag)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print "Tags for '%s':" % res['host']
            for c in res['tags']:
                print '  ' + c
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            for c in res['tags']:
                print c

    def _replace(self, args):
        format = args.format
        svc = TagService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.update(args.host, args.tag)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print "Tags for '%s':" % res['host']
            for c in res['tags']:
                print '  ' + c
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            for c in res['tags']:
                print c

    def _show(self, args):
        format = args.format
        svc = TagService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        if args.host == 'all':
            res = svc.get_all()
        else:
            res = svc.get(args.host)
        report_warnings(res)
        report_errors(res)
        if args.host == 'all':
            if format == 'pretty':
                for tag, hosts in res['tags'].items():
                    for host in hosts:
                        print tag
                        print '  ' + host
                    print
            elif format == 'raw':
                print simplejson.dumps(res)
            else:
                for tag, hosts in res['tags'].items():
                    for host in hosts:
                        print tag + '\t' + host
        else:
            if format == 'pretty':
                for tag in res['tags']:
                    print tag
            elif format == 'raw':
                print simplejson.dumps(res)
            else:
                for tag in res['tags']:
                    print tag

    def _detach(self, args):
        format = args.format
        svc = TagService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.detach(args.host)
        report_warnings(res)
        report_errors(res)
        if format == 'raw':
            print simplejson.dumps(res)
