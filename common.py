import httplib
import json
import time
import socket
import os
from contextlib import contextmanager
from urllib import urlencode
from pprint import pformat

def dt2epoch(d):
    return time.mktime(d.timetuple())
    
def find_datadog_host():
    "Used for internal testing. Chances are, you're not running your own development instance of datadog"
    return os.environ.get('DATADOG_HOST', "app.datadoghq.com")
    
def find_api_key():
    "You can pass the api key in the environment, using the DATADOG_KEY variable"
    return os.environ.get('DATADOG_KEY', None)

def find_localhost():
    return socket.gethostname()
    
class Scope(object):
    def __init__(self, host=None, device=None):
        self.host = host or find_localhost()
        self.device = device

class Service(object):
    def __init__(self, api_host=find_datadog_host()):
        self.host = api_host
    
    @contextmanager
    def connect(self, host=None, api_key=None):
        ''' Context manager to make it easier to make http requests.
            Optionally takes in a host to connect to, defaulting to self.host.
            Returns an httplib.HTTPConnection object that gets automagically 
            closed when leaving the context, whether by normal execution 
            or raised exception.
        
            Example usage:
            
            with self.connect() as conn:
                conn.request('GET', /my/service)
                response = conn.getresponse()
                data = response.read()
            
            return data
        '''
        
        host = host or self.host
        self.api_key = api_key
        
        conn = httplib.HTTPSConnection(host)
        try:
            yield conn
        finally:
            conn.close()
    
    def request(self, method, url, params):
        '''handles a request to the datadog service.
        '''
        # process params
        if not params.has_key('api_key'):
            params['api_key'] = self.api_key
        
        # handle request/response
        with self.connect() as conn:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            conn.request(method, url, urlencode(params), headers)
            response = conn.getresponse()
            response_str = response.read()

            try:
                response_obj = json.loads(response_str)
            except ValueError:
                raise ValueError('Invalid JSON response: {0}'.format(response_str))

            if 'error' in response_obj:
                pretty_params = '\n'.join(['>> ' + line for line in pformat(params).split('\n')])
                request_str = '>> {0} {1} \n{2}'.format(method, url, pretty_params)
                error_message = '\n'.join(['<< ' + line for line in response_obj['error'].split('\n')])
                raise Exception('Failed request \n{0}\n\n{1}'.format(request_str, error_message))

        return response_obj
