import sys

import simplejson

from dogapi.v1 import CommentService, EventService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class CommentClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('comment', help='Post, update, and delete comments.')
        verb_parsers = parser.add_subparsers(title='Verbs')

        post_parser = verb_parsers.add_parser('post', help='Post comments.')
        post_parser.add_argument('--handle', help='handle to post as. if unset, posts as the owner of the application key used to authenticate')
        post_parser.add_argument('comment', help='comment message to post. if unset, reads from stdin.', nargs="?")
        post_parser.set_defaults(func=self._post)

        update_parser = verb_parsers.add_parser('update', help='Update existing comments.')
        update_parser.add_argument('comment_id', help='comment to update (by id)')
        update_parser.add_argument('--handle', help='handle to post as. if unset, posts as the owner of the application key used to authenticate')
        update_parser.add_argument('comment', help='comment message to post. if unset, reads from stdin.', nargs="?")
        update_parser.set_defaults(func=self._update)

        reply_parser = verb_parsers.add_parser('reply', help='Reply to existing comments.')
        reply_parser.add_argument('comment_id', help='comment to reply to (by id)')
        reply_parser.add_argument('--handle', help='handle to post as. if unset, posts as the owner of the application key used to authenticate')
        reply_parser.add_argument('comment', help='comment message to post. if unset, reads from stdin.', nargs="?")
        reply_parser.set_defaults(func=self._reply)

        show_parser = verb_parsers.add_parser('show', help='Show comment details.')
        show_parser.add_argument('comment_id', help='comment to show')
        show_parser.set_defaults(func=self._show)

        delete_parser = verb_parsers.add_parser('delete', help='Delete comments.')
        delete_parser.add_argument('comment_id', help='comment to delete (by id)')
        delete_parser.set_defaults(func=self._delete)

    def _post(self, args):
        handle = args.handle
        comment = args.comment
        format = args.format
        if comment is None:
            comment = sys.stdin.read()
        svc = CommentService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.post(handle, comment)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['comment']['message']
            lines = message.split('\n')
            message = '\n'.join(['    ' + line for line in lines])
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\n' + message
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\t\t' + res['comment']['message'].__repr__()

    def _update(self, args):
        handle = args.handle
        comment = args.comment
        id = args.comment_id
        format = args.format
        if comment is None:
            comment = sys.stdin.read()
        svc = CommentService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.edit(id, handle, comment)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['comment']['message']
            lines = message.split('\n')
            message = '\n'.join(['    ' + line for line in lines])
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\n' + message
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\t\t' + res['comment']['message'].__repr__()

    def _reply(self, args):
        handle = args.handle
        comment = args.comment
        id = args.comment_id
        format = args.format
        if comment is None:
            comment = sys.stdin.read()
        svc = CommentService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.post(handle, comment, related_event_id=id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['comment']['message']
            lines = message.split('\n')
            message = '\n'.join(['    ' + line for line in lines])
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\n' + message
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\t\t' + res['comment']['message'].__repr__()

    def _show(self, args):
        id = args.comment_id
        format = args.format
        svc = EventService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.get(id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['event']['text']
            lines = message.split('\n')
            message = '\n'.join(['    ' + line for line in lines])
            print 'id\t\t' + str(res['event']['id'])
            print 'url\t\t' + res['event']['url']
            print 'resource\t' + res['event']['resource']
            #print 'handle\t\t' + res['event']['handle']
            print 'message\n' + message
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            print 'id\t\t' + str(res['event']['id'])
            print 'url\t\t' + res['event']['url']
            print 'resource\t' + res['event']['resource']
            #print 'handle\t\t' + res['event']['handle']
            print 'message\t\t' + res['event']['text'].__repr__()

    def _delete(self, args):
        id = args.comment_id
        format = args.format
        svc = CommentService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.delete(id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print 'event %s deleted' % id
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            pass
