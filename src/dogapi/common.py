import httplib
import json
import logging
import time
import re
import socket
import os
import simplejson
from contextlib import contextmanager
from urllib import urlencode
from pprint import pformat

log = logging.getLogger('dogapi')

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

        match = re.match('^(https?)://(.*)', host)
        http_conn_cls = httplib.HTTPSConnection

        if match:
            host = match.group(2)
            if match.group(1) == 'http':
                http_conn_cls = httplib.HTTPConnection

        conn = http_conn_cls(host)

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

            if method == 'GET':
                if len(params) > 0:
                    qs_params = [k + '=' + v for k,v in params.iteritems()]
                    qs = '?' + '&'.join(qs_params)
                    conn.request(method, url + qs, None, headers)
                else:
                    conn.request(method, url, None, headers)
            else:
                conn.request(method, url, urlencode(params), headers)
            response = conn.getresponse()
            response_str = response.read()

            try:
                response_obj = json.loads(response_str)
            except ValueError:
                raise ValueError('Invalid JSON response: {0}'.format(response_str))

            if response.status == 200:
                if 'error' in response_obj:
                    pretty_params = '\n'.join(['>> ' + line for line in pformat(params).split('\n')])
                    request_str = '>> {0} {1} \n{2}'.format(method, url, pretty_params)
                    error_message = '\n'.join(['<< ' + line for line in response_obj['error'].split('\n')])
                    raise Exception('Failed request \n{0}\n\n{1}'.format(request_str, error_message))

        return response_obj

class SharedCounter(object):
    # This thing is deprecated. Left around for backwards compatability.
    # FIXME: remove the code in templeton that messes with me
    def __init__(self):
        self.counter = 0

class TimeoutManager(object):
    # FIXME: maybe? officially this should be threadsafe, but probably it's
    # safe enough. there might be some race-y conditions, but I think the worst
    # that can happen is a few timeouts don't get counted. worth a second look.

    def __init__(self, backoff_period=300, max_timeouts=3):
        self.backoff_period = backoff_period
        self.max_timeouts = max_timeouts
        self.backoff_timestamp = None
        self.timeout_counter = 0

    def should_submit(self):
        """ Returns True if we're in a state where we should make a request
        (backoff expired, no backoff in effect), false otherwise.
        """
        now = time.time()
        should_submit = False

        # If we're not backing off, but the timeout counter exceeds the max
        # number of timeouts, then enter the backoff state, recording the time
        # we started backing off
        if not self.backoff_timestamp and self.timeout_counter >= self.max_timeouts:
            log.info("Max number of dogapi timeouts exceeded, backing off for {0} seconds".format(self.backoff_period))
            self.backoff_timestamp = now
            should_submit = False

        # If we are backing off but the we've waiting sufficiently long enough
        # (backoff_retry_age), exit the backoff state and reset the timeout
        # counter so that we try submitting metrics again
        elif self.backoff_timestamp:
            backed_off_time, backoff_time_left = self.backoff_status()
            if backoff_time_left < 0:
                log.info("Exiting backoff state after {0} seconds, will try to submit metrics again".format(backed_off_time))
                self.backoff_timestamp = None
                self.timeout_counter = 0
                should_submit = True
            else:
                log.info("In backoff state, won't submit metrics for another {0} seconds".format(backoff_time_left))
                should_submit = False
        else:
            should_submit = True

        return should_submit

    def report_timeout(self):
        """ Report to the manager that a timeout has occurred.
        """
        self.timeout_counter += 1

    def backoff_status(self):
        now = time.time()
        backed_off_time = now - self.backoff_timestamp
        backoff_time_left = self.backoff_period - backed_off_time
        return round(backed_off_time, 2), round(backoff_time_left, 2)

class APIService(object):

    def __init__(self, api_key, application_key, timeout=2, timeout_counter=None):
        self.api_key = api_key
        self.application_key = application_key
        self.api_host = os.environ.get("DATADOG_HOST", "https://app.datadoghq.com")
        self.timeout = timeout
        self.timeout_counter = timeout_counter or SharedCounter()

    @contextmanager
    def connect(self):

        http_conn_cls = httplib.HTTPSConnection
        match = re.match('^(https?)://(.*)', self.api_host)
        if match:
            host = match.group(2)
            if match.group(1) == 'http':
                http_conn_cls = httplib.HTTPConnection
        conn = http_conn_cls(host, timeout=self.timeout)

        try:
            yield conn
        finally:
            conn.close()

    def request(self, method, url, params=None, body=None, send_json=False):
        '''handles a request to the datadog service.
        '''
        # handle request/response
        with self.connect() as conn:
            if send_json:
                headers = {
                        'Content-Type': 'application/json'
                        }
                body = simplejson.dumps(body)
            else:
                headers = {}

            qs = ''
            if params and len(params) > 0:
                qs_params = [k + '=' + str(v) for k,v in params.iteritems()]
                qs = '?' + '&'.join(qs_params)
                conn.request(method, url + qs, body, headers)
            else:
                conn.request(method, url, body, headers)

            start_time = time.time()
            response = conn.getresponse()
            response_str = response.read()
            response_time = time.time() - start_time
            log.debug("%s %s %s %sms" % (response.status, method, url + qs, round(response_time * 1000., 4)))

            if response.status != 204 and response_str != '' and response_str != 'null':
                try:
                    response_obj = json.loads(response_str)
                except ValueError:
                    raise ValueError('Invalid JSON response: {0}'.format(response_str))

                return response_obj or {}
            else:
                return {}
