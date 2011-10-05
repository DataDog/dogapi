from dogapi.v1 import CommentService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class CommentClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('comment', help='post comments')
        parser.add_argument('handle', help='handle to post as')
        parser.add_argument('comment', help='comment to post')
        parser.set_defaults(r_func=self.r_comment)
        parser.set_defaults(p_func=self.p_comment)
        parser.set_defaults(l_func=self.p_comment)

    def _comment(self, handle, comment):
        svc = CommentService(self.config['apikey'], self.config['appkey'])
        return svc.post(handle, comment)

    def r_comment(self, args):
        res = self._comment(args.handle, args.comment)
        report_warnings(res)
        if report_errors(res):
            return
        print res

    def p_comment(self, args):
        res = self._comment(args.handle, args.comment)
        report_warnings(res)
        if report_errors(res):
            return
        print 'id\t\t' + str(res['comment']['id'])
        print 'url\t\t' + res['comment']['url']
        print 'resource\t' + res['comment']['resource']
        print 'handle\t\t' + res['comment']['handle']
        print 'message\t\t' + res['comment']['message']
