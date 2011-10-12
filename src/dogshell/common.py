import ConfigParser
import sys
from UserDict import IterableUserDict

def report_errors(res):
    if 'errors' in res:
        for e in res['errors']:
            print >> sys.stderr, 'ERROR: ' + e
        sys.exit(1)
    return False

def report_warnings(res):
    if 'warnings' in res:
        for e in res['warnings']:
            print >> sys.stderr, 'WARNING: ' + e
        return True
    return False

class CommandLineClient(object):
    pass

class DogshellConfig(IterableUserDict):

    def load(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self['apikey'] = config.get('Connection', 'apikey')
        self['appkey'] = config.get('Connection', 'appkey')
