import sys

from dogapi.v1 import CommentService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class CommentClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('comment', help='post comments')
        parser.add_argument('--handle', help='handle to post as. if unset, posts as the owner of the application key used to authenticate')
        parser.add_argument('comment', help='comment to post. if unset, reads from stdin.', nargs="?")
        parser.set_defaults(r_func=self.r_comment)
        parser.set_defaults(p_func=self.p_comment)
        parser.set_defaults(l_func=self.l_comment)

    def _comment(self, handle, comment):
        if comment is None:
            comment = sys.stdin.read()
        svc = CommentService(self.config['apikey'], self.config['appkey'])
        return svc.post(handle, comment)

    def r_comment(self, args):
        res = self._comment(args.handle, args.comment)
        report_warnings(res)
        report_errors(res)
        print res

    def p_comment(self, args):
        res = self._comment(args.handle, args.comment)
        report_warnings(res)
        report_errors(res)
        message = res['comment']['message']
        lines = message.split('\n')
        message = '\n'.join(['    ' + line for line in lines])
        print 'id\t\t' + str(res['comment']['id'])
        print 'url\t\t' + res['comment']['url']
        print 'resource\t' + res['comment']['resource']
        print 'handle\t\t' + res['comment']['handle']
        print 'message\n' + message

    def l_comment(self, args):
        res = self._comment(args.handle, args.comment)
        report_warnings(res)
        report_errors(res)
        print 'id\t\t' + str(res['comment']['id'])
        print 'url\t\t' + res['comment']['url']
        print 'resource\t' + res['comment']['resource']
        print 'handle\t\t' + res['comment']['handle']
        print 'message\t\t' + res['comment']['message'].__repr__()
