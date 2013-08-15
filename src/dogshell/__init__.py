import argparse
import os
import sys

import logging
logging.getLogger('dd.dogapi').setLevel(logging.CRITICAL)

from dogshell.common import DogshellConfig

from dogshell.comment import CommentClient
from dogshell.search import SearchClient
from dogshell.metric import MetricClient
from dogshell.tag import TagClient
from dogshell.event import EventClient
from dogshell.dashboard import DashClient

def main():

    parser = argparse.ArgumentParser(description='Interact with the Datadog API',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', help='location of your dogrc file (default ~/.dogrc)',
            default=os.path.expanduser("~/.dogrc"))
    parser.add_argument('--api-key', help='your API key, from https://app.datadoghq.com/account/settings#api',
            dest="api_key", default=None)
    parser.add_argument('--application-key', help='your Application key, from https://app.datadoghq.com/account/settings#api',
            dest="app_key", default=None)
    parser.add_argument('--pretty', help='pretty-print output (suitable for human consumption, less useful for scripting)',
            dest='format', action='store_const', const='pretty')
    parser.add_argument('--raw', help='raw JSON as returned by the HTTP service',
            dest='format', action='store_const', const='raw')
    parser.add_argument('--timeout', help='time to wait in seconds before timing out an API call (default 10)',
            default=10, type=int)

    config = DogshellConfig()

    # Set up subparsers for each service

    subparsers = parser.add_subparsers(title='Modes')

    CommentClient(config).setup_parser(subparsers)
    SearchClient(config).setup_parser(subparsers)
    MetricClient(config).setup_parser(subparsers)
    TagClient(config).setup_parser(subparsers)
    EventClient(config).setup_parser(subparsers)
    DashClient(config).setup_parser(subparsers)

    args = parser.parse_args()
    config.load(args.config, args.api_key, args.app_key)

    args.func(args)

if __name__ == '__main__':
    main()
