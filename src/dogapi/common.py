import logging
import socket
import sys

from dogapi.exceptions import *
from dogapi.constants import *

log = logging.getLogger('dd.dogapi')

def is_p3k(): return sys.version_info[0] == 3

if is_p3k():
    import urllib.request, urllib.error, urllib.parse
else:
    import urllib2

def get_ec2_instance_id():
    try:
        # Remember the previous default timeout
        old_timeout = socket.getdefaulttimeout()

        # Try to query the EC2 internal metadata service, but fail fast
        socket.setdefaulttimeout(0.25)

        try:
            if is_p3k():
                return urllib.request.urlopen(urllib.request.Request('http://169.254.169.254/latest/meta-data/instance-id')).read()
            else:
                return urllib2.urlopen(urllib2.Request('http://169.254.169.254/latest/meta-data/instance-id')).read()
        finally:
            # Reset the previous default timeout
            socket.setdefaulttimeout(old_timeout)
    except:
        return socket.gethostname()


