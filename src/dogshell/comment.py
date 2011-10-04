from dogapi.v1 import CommentService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class CommentClient(CommandLineClient):

    def __init__(self, apikey, appkey):
        self.apikey = apikey
        self.appkey = appkey

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('comment', help='post comments')
        parser.add_argument('handle', help='handle to post as')
        parser.add_argument('comment', help='comment to post')
        parser.set_defaults(func=self.comment)

    def comment(self, args):
        svc = CommentService(self.apikey, self.appkey)
        res = svc.post(args.handle, args.comment)
        report_warnings(res)
        if report_errors(res):
            return
