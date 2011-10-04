import time, datetime
import socket

from dogapi.v1 import MetricService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class MetricClient(CommandLineClient):

    def __init__(self, apikey, appkey):
        self.apikey = apikey
        self.appkey = appkey

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('metric', help='post metric series data point')
        parser.add_argument('name', help='metric name')
        parser.add_argument('value', help='metric value (integer or decimal value)', type=float)
        parser.add_argument('--host', help='scopes your metric to a specific host', default=None)
        parser.add_argument('--device', help='scopes your metric to a specific device', default=None)
        parser.add_argument('--localhostname', help='same as --host=`hostname` (overrides --host)', action='store_true')
        parser.set_defaults(func=self.post_metric)

    def post_metric(self, args):
        svc = MetricService(self.apikey, self.appkey)
        now = datetime.datetime.now()
        now = time.mktime(now.timetuple())
        if args.localhostname:
            host = socket.gethostname()
        else:
            host = args.host
        res = svc.post(args.name, [(now, args.value)], host=host, device=args.device)
        report_warnings(res)
        if report_errors(res):
            return
