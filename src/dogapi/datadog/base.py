import os
import logging
import socket
import re
import sys
import time, datetime
import types
import httplib
import urllib2
from urllib import urlencode
from decorator import decorator

from dogapi.http import HttpClient, HttpTimeout, HttpBackoff, json
log = logging.getLogger('dogapi')

class BaseDatadog(HttpClient):
    def __init__(self, api_key=None, application_key=None, api_version='v1', api_host=None, timeout=2, max_timeouts=3, backoff_period=300, swallow=True, use_ec2_instance_id=False):
        self.api_host = api_host or os.environ.get('DATADOG_HOST', 'https://app.datadoghq.com')
        super(BaseDatadog, self).__init__(backoff_period, max_timeouts)
        self.api_key = api_key
        self.api_version = api_version
        self.application_key = application_key
        self.timeout = timeout
        self.swallow = swallow
        self._default_host = socket.gethostname()
        self._use_ec2_instance_id = None
        self.use_ec2_instance_id = use_ec2_instance_id
    
    def request(self, method, path, body=None, **params):
        if self.api_key:
            params['api_key'] = self.api_key
        if self.application_key:
            params['application_key'] = self.application_key
        path = "/api/%s/%s" % (self.api_version, path.lstrip('/'))
        try:
            return super(BaseDatadog, self).request(method, path, body, **params)
        except (HttpTimeout, HttpBackoff), e:
            if self.swallow:
                log.error(str(e))
            else:
                raise            

    def use_ec2_instance_id():
        def fget(self):
            return self._use_ec2_instance_id
        
        def fset(self, value):
            self._use_ec2_instance_id = value

            if value:
                try:
                    # Remember the previous default timeout
                    old_timeout = socket.getdefaulttimeout()

                    # Try to query the EC2 internal metadata service, but fail fast
                    socket.setdefaulttimeout(0.25)

                    try:
                        host = urllib2.urlopen(urllib2.Request('http://169.254.169.254/latest/meta-data/instance-id')).read()
                    finally:
                        # Reset the previous default timeout
                        socket.setdefaulttimeout(old_timeout)
                except Exception:
                    host = socket.gethostname()

                self._default_host = host
            else:
                self._default_host = socket.gethostname()
        
        def fdel(self):
            del self._use_ec2_instance_id
        
        return locals()
    use_ec2_instance_id = property(**use_ec2_instance_id())

