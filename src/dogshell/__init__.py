import argparse
import ConfigParser
import os
import sys

from dogapi.search import SearchService

from dogshell.comment import CommentClient
from dogshell.search import SearchClient

def main():

    parser = argparse.ArgumentParser(description='Interact with the Datadog API',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser("~/.dogrc"))
    apikey = config.get('Connection', 'apikey')
    appkey = config.get('Connection', 'appkey')

    # Set up subparsers for each service

    subparsers = parser.add_subparsers(title='Modes')

    cc = CommentClient(apikey, appkey)
    cc.setup_parser(subparsers)

    cc = SearchClient(apikey, appkey)
    cc.setup_parser(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__=='__main__':
    main()
