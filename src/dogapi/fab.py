from functools import wraps
import logging
import time

from fabric.tasks import WrappedCallableTask
from dogapi import dog_http_api

logger = logging.getLogger("fabric")

MAX_ARGS_LEN = 256

def setup(api_key):
    global dog_http_api
    dog_http_api.api_key = api_key

def _human_duration(d):
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

def _task_details(t):
    return "%s.%s" % (t.__module__, t.wrapped.func_name)

def _format_args(args, kwargs):
    serialized_args = u", ".join(map(unicode, args)+[u"{0}={1}".format(k, kwargs[k]) for k in kwargs])
    if len(serialized_args) > MAX_ARGS_LEN:
        return serialized_args[:MAX_ARGS_LEN] + u"..."]
    else:
        return serialized_args

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
                    dog_http_api.event("{0}".format(_task_details(t)),
                                       "{0}({1}) ran for {2}.".format(_task_details(t), _format_args(args, kwargs), _human_duration(duration)),
                                       source_type_name="fabric",
                                       alert_type="success",
                                       priority="normal",
                                       aggregation_key=_task_details(t))
                except Exception:
                    logger.warn("Datadog notification failed but task {0} completed".format(t.wrapped.func_name))
            return r
        except Exception, e:
            # If notification is on, create an error event
            end = time.time()
            duration = end - start
            if notify_datadog:
                try:
                    dog_http_api.event("{0}".format(_task_details(t)),
                                       "{0}({1}) failed after {2} because of {3}.".format(_task_details(t), _format_args(args, kwargs), _human_duration(duration), e),
                                       source_type_name="fabric",
                                       alert_type="error",
                                       priority="normal",
                                       aggregation_key=_task_details(t))
                except Exception:
                    logger.exception("Datadog notification failed")
            # Reraise
            raise

    return WrappedCallableTask(wrapper)

    
