import time, datetime
import socket

import simplejson

from dogapi.v1 import MetricService
from dogapi.common import find_localhost

from dogshell.common import report_errors, report_warnings, CommandLineClient

class MetricClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('metric', help='Post metrics.')
        verb_parsers = parser.add_subparsers(title='Verbs')

        post_parser = verb_parsers.add_parser('post', help='Post metrics')
        post_parser.add_argument('name', help='metric name')
        post_parser.add_argument('value', help='metric value (integer or decimal value)', type=float)
        post_parser.add_argument('--host', help='scopes your metric to a specific host', default=None)
        post_parser.add_argument('--device', help='scopes your metric to a specific device', default=None)
        post_parser.add_argument('--localhostname', help='same as --host=`hostname` (overrides --host)', action='store_true')
        parser.set_defaults(func=self._post)

    def _post(self, args):
        svc = MetricService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        now = datetime.datetime.now()
        now = time.mktime(now.timetuple())
        if args.localhostname:
            host = find_localhost()
        else:
            host = args.host
        res = svc.post(args.name, [(now, args.value)], host=host, device=args.device)
        report_warnings(res)
        report_errors(res)
