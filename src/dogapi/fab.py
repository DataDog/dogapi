from functools import wraps
import logging
import time

from fabric.tasks import WrappedCallableTask
from dogapi import dog_http_api

logger = logging.getLogger("fabric")

def setup(api_key):
    global dog_http_api
    dog_http_api.api_key = api_key

def human_duration(d):
    def pluralize(quantity, noun):
        if quantity >= 2:
            return "{0} {1}s".format(quantity, noun)
        else:
            return "{0} {1}".format(quantity, noun)
    
    if d < 1:
        return "less than 1 second"
    elif d < 60:
        return "{0}".format(pluralize(int(d), "second"))
    elif d >= 61 and d < 3600:
        return "{0}".format(pluralize(d/60, "minute"))
    else:
        return "{0} {1}".format(pluralize(d/3600, "hour"), pluralize(d % 3600, "minute"))

def notify(t):
    """Decorates a fabric task"""
    @wraps(t)
    def wrapper(*args, **kwargs):
        notify_datadog = True

        if type(t) != WrappedCallableTask:
            logger.warn("@notify decorator only works on a new-style Fabric Task")
            notify_datadog = False
        
        start = time.time()
        
        try:
            r = t(*args, **kwargs)
            end = time.time()
            duration = end - start
            if notify_datadog:
                try:
                    dog_http_api.event("{0}".format(t.wrapped.func_name),
                                       "{0} ran for {1}.".format(t.wrapped.func_name, human_duration(duration)),
                                       source_type_name="fabric",
                                       alert_type="success",
                                       priority="normal",
                                       aggregation_key=t.wrapped.func_name)
                except:
                    logger.warn("Datadog notification failed but task {0} completed".format(t.wrapped.func_name))
            return r
        except Exception, e:
            # If notification is on, create an error event
            end = time.time()
            duration = end - start
            if notify_datadog:
                try:
                    dog_http_api.event("{0}".format(t.wrapped.func_name),
                                       "{0} failed after {1} because of {2}.".format(t.wrapped.func_name, human_duration(duration), e),
                                       source_type_name="fabric",
                                       alert_type="error",
                                       priority="normal",
                                       aggregation_key=t.wrapped.func_name)
                except:
                    logger.exception("Datadog notification failed")
            # Reraise
            raise

    return WrappedCallableTask(wrapper)

    
