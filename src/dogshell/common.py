from __future__ import print_function
from dogapi.common import is_p3k, find_localhost


get_input = input

if is_p3k():
    import configparser
else:
    get_input = raw_input
    import ConfigParser as configparser
import os
import sys
try:
    from UserDict import IterableUserDict
except ImportError:
    from collections import UserDict as IterableUserDict

from dogapi import DogHttpApi

def print_err(msg):
    if is_p3k():
        print('ERROR: ' + msg + '\n', file=sys.stderr)
    else:
        sys.stderr.write(msg + '\n')


def report_errors(res):
    if 'errors' in res:
        for e in res['errors']:
            print_err('ERROR: ' + e)
        sys.exit(1)
    return False

def report_warnings(res):
    if 'warnings' in res:
        for e in res['warnings']:
            print_err('WARNING: ' + e)
        return True
    return False

class CommandLineClient(object):
    def __init__(self, config):
        self.config = config
        self._dog = None

    @property
    def dog(self):
        if not self._dog:
            self._dog = DogHttpApi(self.config['apikey'], self.config['appkey'], swallow=True, json_responses=True)
        return self._dog


class DogshellConfig(IterableUserDict):

    def load(self, config_file, apikey, appkey):
        config = configparser.ConfigParser()

        if apikey is not None and appkey is not None:
            self['apikey'] = apikey
            self['appkey'] = appkey
        else:
            if os.access(config_file, os.F_OK):
                config.read(config_file)
                if not config.has_section('Connection'):
                    report_errors({'errors': ['%s has no [Connection] section' % config_file]})
            else:
                try:
                    response = ''
                    while response.strip().lower() not in ['y', 'n']:
                        response = get_input('%s does not exist. Would you like to create it? [Y/n] ' % config_file)
                        if response.strip().lower() in ['', 'y', 'yes']:
                            # Read the api and app keys from stdin
                            apikey = get_input('What is your api key? (Get it here: https://app.datadoghq.com/account/settings#api) ')
                            appkey = get_input('What is your application key? (Generate one here: https://app.datadoghq.com/account/settings#api) ')

                            # Write the config file
                            config.add_section('Connection')
                            config.set('Connection', 'apikey', apikey)
                            config.set('Connection', 'appkey', appkey)

                            f = open(config_file, 'w')
                            config.write(f)
                            f.close()
                            print('Wrote %s' % config_file)
                        elif response.strip().lower() == 'n':
                            # Abort
                            print_err('Exiting\n')
                            sys.exit(1)
                except KeyboardInterrupt:
                    # Abort
                    print_err('\nExiting')
                    sys.exit(1)


            self['apikey'] = config.get('Connection', 'apikey')
            self['appkey'] = config.get('Connection', 'appkey')
        assert self['apikey'] is not None and self['appkey'] is not None
        
