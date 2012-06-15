from functools import wraps
import logging

from fabric.tasks import WrappedCallableTask
from dogapi import dog_http_api

logger = logging.getLogger("fabric")

def setup(api_key, application_key):
    global dog_http_api
    dog_http_api.api_key = api_key
    dog_http_api.application_key = application_key

def notify(t):
    """Decorates a fabric task"""
    @wraps(t)
    def wrapper(*args, **kwargs):
        notify_datadog = True
        if type(t) != WrappedCallableTask:
            logger.warn("@notify decorator only works on a new-style Fabric Task")
            notify_datadog = False
        
        try:
            r = t(*args, **kwargs)
            if notify_datadog:
                try:
                    dog_http_api.event("%s" % t.wrapped.func_name,
                                       "",
                                       source_type="fabric",
                                       alert_type="success",
                                       priority="normal",
                                       aggregation_key=t.wrapped.func_name)
                except:
                    logger.warn("Datadog notification failed but task {0} completed".format(t.wrapped.func_name))
            return r
        except Exception, e:
            # If notification is on, create an error event
            if notify_datadog:
                try:
                    dog_http_api.event("%s" % t.wrapped.func_name,
                                       "",
                                       source_type="fabric",
                                       alert_type="error",
                                       priority="normal",
                                       aggregation_key=t.wrapped.func_name)
                except:
                    logger.exception("Datadog notification failed")
            # Reraise
            raise e

    return wrapper
    
