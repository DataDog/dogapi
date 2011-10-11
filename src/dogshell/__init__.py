import argparse
import os
import sys

from dogshell.common import DogshellConfig

from dogshell.comment import CommentClient
from dogshell.search import SearchClient
from dogshell.metric import MetricClient

def main():

    parser = argparse.ArgumentParser(description='Interact with the Datadog API',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', help='location of your dogrc file (default ~/.dogrc)',
            default=os.path.expanduser("~/.dogrc"))
    parser.add_argument('--pretty', help='pretty-print output (suitable for human consumption, less useful for scripting)',
            dest='format', action='store_const', const='pretty')
    parser.add_argument('--raw', help='raw JSON as returned by the HTTP service',
            dest='format', action='store_const', const='raw')

    config = DogshellConfig()

    # Set up subparsers for each service

    subparsers = parser.add_subparsers(title='Modes')

    CommentClient(config).setup_parser(subparsers)
    SearchClient(config).setup_parser(subparsers)
    MetricClient(config).setup_parser(subparsers)

    args = parser.parse_args()
    config.load(args.config)

    if args.format == 'raw':
        args.r_func(args)
    elif args.format == 'pretty':
        args.p_func(args)
    else:
        args.l_func(args)

if __name__=='__main__':
    main()
