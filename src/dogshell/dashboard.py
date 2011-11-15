import os.path
import platform
import sys
import webbrowser
from datetime import datetime

import argparse
import simplejson

from dogapi.v1 import DashService

from dogshell.common import report_errors, report_warnings, CommandLineClient

class DashClient(CommandLineClient):

    def __init__(self, config):
        self.config = config

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser('dashboard', help='Create, edit, and delete dashboards.')
        parser.add_argument('--string_ids', action='store_true', dest='string_ids', 
                            help='Represent Dashboard IDs as strings instead of ints in JSON')

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

        show_all_parser = verb_parsers.add_parser('show_all', help='Show a list of all dashboards.')
        show_all_parser.set_defaults(func=self._show_all)

        pull_parser = verb_parsers.add_parser('pull', help='Pull a dashboard on the server into a local file')
        pull_parser.add_argument('dashboard_id', help='ID of dashboard to pull')
        pull_parser.add_argument('filename', help='file to pull dashboard into') # , type=argparse.FileType('wb'))
        pull_parser.set_defaults(func=self._pull)

        pull_all_parser = verb_parsers.add_parser('pull_all', help='Pull all dashboards into files in a directory')
        pull_all_parser.add_argument('pull_dir', help='directory to pull dashboards into')
        pull_all_parser.set_defaults(func=self._pull_all)

        push_parser = verb_parsers.add_parser('push', help='Push updates to dashboards from local files to the server')
        push_parser.add_argument('--append_auto_text', action='store_true', dest='append_auto_text',
                                 help='When pushing to the server, appends filename and timestamp to the end of the dashboard description')
        push_parser.add_argument('file', help='dashboard files to push to the server', nargs='+', type=argparse.FileType('r'))
        push_parser.set_defaults(func=self._push)

        new_file_parser = verb_parsers.add_parser('new_file', help='Create a new dashboard and put its contents in a file')
        new_file_parser.add_argument('filename', help='name of file to create with empty dashboard')
        new_file_parser.set_defaults(func=self._new_file)

        web_view_parser = verb_parsers.add_parser('web_view', help='View the dashboard in a web browser')
        web_view_parser.add_argument('file', help='dashboard file', type=argparse.FileType('r'))
        web_view_parser.set_defaults(func=self._web_view)

        delete_parser = verb_parsers.add_parser('delete', help='Delete dashboards.')
        delete_parser.add_argument('dashboard_id', help='dashboard to delete')
        delete_parser.set_defaults(func=self._delete)



    def _pull(self, args):
        self._write_dash_to_file(args.dashboard_id, args.filename, args.timeout, args.format, args.string_ids)

    def _pull_all(self, args):
        
        def _title_to_filename(title):
            # Get a lowercased version with most punctuation stripped out...
            no_punct = filter(lambda c: c.isalnum() or c in [" ", "_", "-"],
                              title.lower())
            # Now replace all -'s, _'s and spaces with "_", and strip trailing _
            return no_punct.replace(" ", "_").replace("-", "_").strip("_")

        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.get_all()
        report_warnings(res)
        report_errors(res)
        
        if not os.path.exists(args.pull_dir):
            os.mkdir(args.pull_dir, 0755)
        
        used_filenames = set()
        for dash_summary in res['dashes']:
            filename = _title_to_filename(dash_summary['title'])
            if filename in used_filenames:
                filename = filename + "-" + dash_summary['id']
            used_filenames.add(filename)

            self._write_dash_to_file(dash_summary['id'], 
                                     os.path.join(args.pull_dir, filename + ".json"),
                                     args.timeout,
                                     format,
                                     args.string_ids)
        if format == 'pretty':
            print("\n### Total: {0} dashboards to {1} ###"
                  .format(len(used_filenames), os.path.realpath(args.pull_dir)))

    def _new_file(self, args):
        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.create(args.filename, 
                         "Description for {0}".format(args.filename), [])
        report_warnings(res)
        report_errors(res)
        
        self._write_dash_to_file(res['dash']['id'], args.filename, args.timeout, format, args.string_ids)

        if format == 'pretty':
            print self._pretty_json(res)
        else:
            print simplejson.dumps(res)

    def _write_dash_to_file(self, dash_id, filename, timeout, format='raw', string_ids=False):
        with open(filename, "wb") as f:
            svc = DashService(self.config['apikey'], self.config['appkey'], timeout=timeout)
            res = svc.get(dash_id)
            report_warnings(res)
            report_errors(res)

            dash_obj = res["dash"]
            if "resource" in dash_obj:
                del dash_obj["resource"]
            if "url" in dash_obj:
                del dash_obj["url"]

            if string_ids:
                dash_obj["id"] = str(dash_obj["id"])

            simplejson.dump(dash_obj, f, indent=2)

            if format == 'pretty':
                print "Downloaded dashboard {0} to file {1}".format(dash_id, filename)
            else:
                print "{0} {1}".format(dash_id, filename)

    def _push(self, args):
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        for f in args.file:
            try:
                dash_obj = simplejson.load(f)
            except Exception as err:
            # except simplejson.decoder.JSONDecodeError as err: # only works in simplejson 2.2.x
                raise Exception("Could not parse {0}: {1}".format(f.name, err))
            
            # Always convert to int, in case it was originally a string.
            dash_obj["id"] = int(dash_obj["id"])

            if args.append_auto_text:
                datetime_str = datetime.now().strftime('%x %X')
                auto_text = ("<br/>\nUpdated at {0} from {1} ({2}) on {3}"
                             .format(datetime_str, f.name, dash_obj["id"], platform.node()))
                dash_obj["description"] += auto_text

            res = svc.update(dash_obj["id"], dash_obj["title"], 
                             dash_obj["description"], dash_obj["graphs"])

            if 'errors' in res:
                print >> sys.stderr, 'Upload of dashboard {0} from file {1} failed.'.format(dash_obj["id"], f.name)

            report_warnings(res)
            report_errors(res)

            if args.format == 'pretty':
                print "Uploaded file {0} (dashboard {1})".format(f.name, dash_obj["id"])
        
    def _post(self, args):
        format = args.format
        if args.graphs is None:
            graphs = sys.stdin.read()
        try:
            graphs = simplejson.loads(graphs)
        except:
            raise Exception('bad json parameter')
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.create(args.title, args.description, graphs)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print self._pretty_json(res)
        else:
            print simplejson.dumps(res)

    def _update(self, args):
        format = args.format
        if args.graphs is None:
            graphs = sys.stdin.read()
        try:
            graphs = simplejson.loads(graphs)
        except:
            raise Exception('bad json parameter')
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.update(args.dashboard_id, args.title, args.description, graphs)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print self._pretty_json(res)
        else:
            print simplejson.dumps(res)

    def _show(self, args):
        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.get(args.dashboard_id)
        report_warnings(res)
        report_errors(res)

        if args.string_ids:
            res["dash"]["id"] = str(res["dash"]["id"])

        if format == 'pretty':
            print self._pretty_json(res)
        else:
            print simplejson.dumps(res)

    def _show_all(self, args):
        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.get_all()
        report_warnings(res)
        report_errors(res)

        if args.string_ids:
            for d in res["dashes"]:
                d["id"] = str(d["id"])

        if format == 'pretty':
            print self._pretty_json(res)
        elif format == 'raw':
            print simplejson.dumps(res)
        else:
            for d in res["dashes"]:
                print "\t".join([(d["id"]), 
                                 (d["resource"]),
                                 (d["title"]),
                                 self._escape(d["description"])])

    def _delete(self, args):
        format = args.format
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        res = svc.delete(args.dashboard_id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            print self._pretty_json(res)
        else:
            print simplejson.dumps(res)

    def _web_view(self, args):
        svc = DashService(self.config['apikey'], self.config['appkey'], timeout=args.timeout)
        dash_id = simplejson.load(args.file)['id']
        url = svc.api_host + "/dash/dash/{0}".format(dash_id)
        webbrowser.open(url)

    def _escape(self, s):
        return s.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")

    def _pretty_json(self, obj):
        return simplejson.dumps(obj, sort_keys=True, indent=2)

