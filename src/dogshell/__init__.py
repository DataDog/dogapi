import argparse
import os
import sys

from dogapi.search import SearchService

from dogshell.common import DogshellConfig

from dogshell.comment import CommentClient
from dogshell.search import SearchClient
from dogshell.metric import MetricClient

def main():

    parser = argparse.ArgumentParser(description='Interact with the Datadog API',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', help='location of your dogrc file (default ~/.dogrc)',
            default=os.path.expanduser("~/.dogrc"))

    config = DogshellConfig()

    # Set up subparsers for each service

    subparsers = parser.add_subparsers(title='Modes')

    cc = CommentClient(config)
    cc.setup_parser(subparsers)

    sc = SearchClient(config)
    sc.setup_parser(subparsers)

    mc = MetricClient(config)
    mc.setup_parser(subparsers)

    args = parser.parse_args()
    config.load(args.config)
    args.func(args)

if __name__=='__main__':
    main()
