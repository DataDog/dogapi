import argparse
import ConfigParser
import os
import sys

from dogapi.search import SearchService

from dogshell.comment import CommentClient
from dogshell.search import SearchClient
from dogshell.metric import MetricClient

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

    sc = SearchClient(apikey, appkey)
    sc.setup_parser(subparsers)

    mc = MetricClient(apikey, appkey)
    mc.setup_parser(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__=='__main__':
    main()
