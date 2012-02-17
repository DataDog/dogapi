import httplib
import logging
import time
import re
import socket
import ssl
import os
from contextlib import contextmanager
from urllib import urlencode
from pprint import pformat

try:
    import simplejson as json
except ImportError:
    import json

log = logging.getLogger('dogapi.http')

def dt2epoch(d):
    return time.mktime(d.timetuple())

class ClientError(Exception): pass
class HttpTimeout(Exception): pass
class HttpBackoff(Exception): pass
timeout_exceptions = (socket.timeout, ssl.SSLError)

class HttpClient(object):
    def __init__(self, backoff_period, max_timeouts):
        self.backoff_period = backoff_period
        self.max_timeouts = max_timeouts
        self.backoff_timestamp = None
        self.timeout_counter = 0

    def request(self, method, path, body=None, **params):
        if not self.should_submit():
            raise HttpBackoff("Too many timeouts. Won't try again for {1} seconds.".format(*self.backoff_status()))
        
        match = re.match('^(https?)://(.*)', self.api_host)
        http_conn_cls = httplib.HTTPSConnection

        if match:
            host = match.group(2)
            if match.group(1) == 'http':
                http_conn_cls = httplib.HTTPConnection

        conn = http_conn_cls(host)
        url = "/%s?%s" % (path.lstrip('/'), urlencode(params))
        
        headers = {}
        if isinstance(body, dict):
            body = json.dumps(body)
            headers['Content-Type'] = 'application/json'
                
        try:
            start_time = time.time()
            try:
                conn.request(method, url, body, headers)
            except timeout_exceptions:
                self.report_timeout()
                raise HttpTimeout('%s %s timed out after %d seconds.' % (method, url, self.timeout))
            
            response = conn.getresponse()
            duration = round((time.time() - start_time) * 1000., 4) 
            log.info("%s %s %s (%sms)" % (response.status, method, url, duration))
            response_str = response.read()
            if response_str:
                try:
                    response_obj = json.loads(response_str)
                except ValueError:
                    raise ValueError('Invalid JSON response: {0}'.format(response_str))
                
                if response_obj and 'errors' in response_obj:
                    raise ClientError(response_obj['errors'])
            else:
                response_obj = {}
            return response_obj
        finally:
            conn.close()     

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


