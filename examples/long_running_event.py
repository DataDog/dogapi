'''
An example of how to submit long-running events.
'''

import os
import random
import sys
import time
from optparse import OptionParser

from event import EventService, Scope, Event

if 'DATADOG_KEY' not in os.environ:
    print >> sys.stdout, 'DATADOG_KEY environment variable not set'
    sys.exit(1)

parser = OptionParser()
parser.add_option("-t", "--target", action="store", dest="host", help="host to post events to", default="app.datadoghq.com")
options, args = parser.parse_args()

api_key = os.environ['DATADOG_KEY']
host = options.host

event_service = EventService(host)
scope = Scope()

cost = random.randint(12,16)
sleep_time = random.randint(10, 60)
event = Event('Doing %s units of work then sleeping for %s seconds' % (cost, sleep_time))
print event.msg_text

with event_service.start(api_key, event, scope):
    time.sleep(sleep_time)
    
    if random.randint(1, 3) == 1:
        # Leaving the context with an exception will tell the event api to 
        # mark the event as unsuccessful
        raise Exception('Job failed') 
