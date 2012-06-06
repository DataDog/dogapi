'''
A simple script that will do a git pull on a local repo and submit an event
if there were new changes pulled down. Useful for setups that use git as
their deployment mechanism, so you know when new code has been released.
'''

import os
import subprocess
import sys
from optparse import OptionParser

from dogapi import dog_http_api as dog

if 'DATADOG_API_KEY' not in os.environ:
    print >> sys.stderr, 'DATADOG_API_KEY environment variable not set'
    sys.exit(1)
else:
    dog.api_key = os.environ['DATADOG_API_KEY']

parser = OptionParser(usage="usage: %prog [options] /path/to/local_git_dir")
parser.add_option("-r", "--remote", action="store", dest="remote", help="Git remote to pull from", default="origin")
parser.add_option("-b", "--branch", action="store", dest="branch", help="Git branch to pull from", default="master")
options, args = parser.parse_args()

if len(args) < 1:
    parser.print_help()
    sys.exit(1)
else:
    local_repo_dir = args[0]

# Execute the git pull command
git_cmd = ['git', 'pull', options.remote, options.branch]
proc = subprocess.Popen(git_cmd, cwd=local_repo_dir, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
git_message, _ = proc.communicate()

if 'Already up-to-date.' not in git_message:
    # Only submit events if there were changes
    print git_message
    dog.event("Git Changes", git_message)
