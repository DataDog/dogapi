import simplejson
import sys

from dogapi.v1 import DashService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class DashClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('dashboard', help='Create, edit, and delete dashboards.')
        verb_parsers = parser.add_subparsers(title='Verbs')

        post_parser = verb_parsers.add_parser('post', help='Create dashboards.')
        post_parser.add_argument('title', help='title for the new dashboard')
        post_parser.add_argument('description', help='short description of the dashboard')
        post_parser.add_argument('graphs', help='graph definitions as a JSON string. if unset, reads from stdin.', nargs="?")
        post_parser.set_defaults(func=self._post)

        update_parser = verb_parsers.add_parser('update', help='Update existing dashboards.')
        update_parser.add_argument('dashboard_id', help='dashboard to replace with the new definition')
        update_parser.add_argument('title', help='new title for the dashboard')
        update_parser.add_argument('description', help='short description of the dashboard')
        update_parser.add_argument('graphs', help='graph definitions as a JSON string. if unset, reads from stdin.', nargs="?")
        update_parser.set_defaults(func=self._update)

        show_parser = verb_parsers.add_parser('show', help='Show a dashboard definition.')
        show_parser.add_argument('dashboard_id', help='dashboard to show')
        show_parser.set_defaults(func=self._show)

        show_all_parser = verb_parsers.add_parser('show_all', help='Show a list of dashboards.')
        show_all_parser.set_defaults(func=self._show_all)

        delete_parser = verb_parsers.add_parser('delete', help='Delete dashboards.')
        delete_parser.add_argument('dashboard_id', help='dashboard to delete')
        delete_parser.set_defaults(func=self._delete)


    def _post(self, args):
        format = args.format
        if args.graphs is None:
            graphs = sys.stdin.read()
        try:
            graphs = simplejson.loads(graphs)
        except:
            raise Exception('bad json parameter')
        svc = DashService(self.config['apikey'], self.config['appkey'])
        res = svc.create(args.title, args.description, graphs)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print res
        elif format == 'raw':
            print res
        else:
            print res

    def _update(self, args):
        format = args.format
        if args.graphs is None:
            graphs = sys.stdin.read()
        try:
            graphs = simplejson.loads(graphs)
        except:
            raise Exception('bad json parameter')
        svc = DashService(self.config['apikey'], self.config['appkey'])
        res = svc.update(args.dashboard_id, args.title, args.description, graphs)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print res
        elif format == 'raw':
            print res
        else:
            print res

    def _show(self, args):
        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'])
        res = svc.get(args.dashboard_id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print simplejson.dumps(res, sort_keys=True, indent=2)
        elif format == 'raw':
            print res
        else:
            print res

    def _show_all(self, args):
        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'])
        res = svc.get_all()
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print simplejson.dumps(res, sort_keys=True, indent=2)
        elif format == 'raw':
            print res
        else:
            print res

    def _delete(self, args):
        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'])
        res = svc.delete(args.dashboard_id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print res
        elif format == 'raw':
            print res
        else:
            print res
