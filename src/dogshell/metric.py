import time, datetime
import socket

from dogapi.v1 import MetricService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class MetricClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('metric', help='post metric series data point')
        parser.add_argument('name', help='metric name')
        parser.add_argument('value', help='metric value (integer or decimal value)', type=float)
        parser.add_argument('--host', help='scopes your metric to a specific host', default=None)
        parser.add_argument('--device', help='scopes your metric to a specific device', default=None)
        parser.add_argument('--localhostname', help='same as --host=`hostname` (overrides --host)', action='store_true')
        parser.set_defaults(r_func=self.r_post_metric)
        parser.set_defaults(p_func=self.r_post_metric)
        parser.set_defaults(l_func=self.r_post_metric)

    def _post_metric(self, args):
        svc = MetricService(self.config['apikey'], self.config['appkey'])
        now = datetime.datetime.now()
        now = time.mktime(now.timetuple())
        if args.localhostname:
            host = socket.gethostname()
        else:
            host = args.host
        return svc.post(args.name, [(now, args.value)], host=host, device=args.device)

    def r_post_metric(self, args):
        res = self._post_metric(args)
        report_warnings(res)
        report_errors(res)
