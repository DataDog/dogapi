"""
Full client-side events client
See facade.py for a simpler wrapper
"""
import logging
import socket
import time

from collections import namedtuple
from contextlib import contextmanager

from common import Service, Scope

class Event(object):
    def __init__(self, msg_text, metric='', date_detected='', date_happened='', alert_type='', event_type='', event_object='', msg_title='', json_payload=''):
        """ Encapsulates json parameters that define an event
        """
        self.msg_text = msg_text
        self.metric = metric
        self.date_detected = date_detected or time.time()
        self.date_happened = date_happened or time.time()
        self.alert_type = alert_type
        self.event_type = event_type
        self.event_object = event_object
        self.msg_title = msg_title
        self.json_payload = json_payload

class EventService(Service):
    def submit(self, api_key, event, scope=None, source_type=None):
        scope = scope or Scope()
        params = {
            'api_key':          api_key,
             
            # Scope params
            'host':             getattr(scope, "host", None),
            'device':           getattr(scope, "device", None),

            # Event params
            'metric':           event.metric,
            'date_detected':    event.date_detected,
            'date_happened':    event.date_happened,
            'alert_type':       event.alert_type,
            'event_type':       event.event_type,
            'event_object':     event.event_object,
            'msg_title':        event.msg_title,
            'msg_text':         event.msg_text,
            'json_payload':     event.json_payload,           
        }

        # Source_type is optional
        if source_type is not None:
            params['source_type'] = source_type
        
        return self.request('POST', '/event/submit', params)
    
    @contextmanager
    def start(self, api_key, event, scope, source_type=None):
        result = self.submit(api_key, event, scope, source_type=source_type)
        success = None
        
        try:
            yield result
        except:
            success = False
            raise
        else:
            success = True
        finally:
            self.end(api_key, result['id'], successful=success)
    
    def end(self, api_key, event_id, date_ended=None, successful=None):
        params = {
            'api_key': api_key,
            'event_id': event_id
        }

        return self.request('POST', '/event/ended', params)          
            
class MockEventService(Service):
    def submit(self, api_key, event, scope, source_type=None):
        ''' No op
        '''
        with self.connect() as conn:
            return {'id': 1}


if __name__ == '__main__':
    import os
    import sys
    from optparse import OptionParser
    
    if 'DATADOG_KEY' not in os.environ:
        print >> sys.stdout, 'DATADOG_KEY environment variable not set'
        sys.exit(1)
    
    api_key = os.environ['DATADOG_KEY']
    
    parser = OptionParser()
    parser.add_option("-t", "--target", action="store", dest="host", help="host to post events to")
    options, args = parser.parse_args()
    
    if len(args) == 0:
        message = sys.stdin.read()
    else:
        message = args[0]
    
    event_service = EventService(options.host)
    scope = Scope()
    event = Event(message)
    
    result = event_service.submit(api_key, event, scope)
