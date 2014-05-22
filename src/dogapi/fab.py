from functools import wraps
import logging
import time

from fabric.tasks import WrappedCallableTask
from dogapi import dog_http_api

logger = logging.getLogger("fabric")

MAX_ARGS_LEN = 256

def setup(api_key, application_key=None):
    global dog_http_api
    dog_http_api.api_key = api_key
    if application_key is not None:
        dog_http_api.application_key = application_key

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
    return "%s.%s" % (t.__module__, t.__name__)

def _format_args(args, kwargs):
    serialized_args = u", ".join(map(unicode, args)+[u"{0}={1}".format(k, kwargs[k]) for k in kwargs])
    if len(serialized_args) > MAX_ARGS_LEN:
        return serialized_args[:MAX_ARGS_LEN] + u"..."
    else:
        return serialized_args

def _text(t, args, kwargs, duration, error):
    if error:
        return "{0}({1}) failed after {2} because of {3}.".format(_task_details(t), _format_args(args, kwargs), _human_duration(duration), error)
    else:
        return "{0}({1}) ran for {2}.".format(_task_details(t), _format_args(args, kwargs), _human_duration(duration))

def _title(t, args, kwargs, error):
    return "{0}".format(_task_details(t))

def _aggregation_key(t, args, kwargs, error):
    return _task_details(t)

def _tags(t, args, kwargs, error):
    return []

def notify(t):
    """Decorates a fabric task"""
    @wraps(t)
    def wrapper(*args, **kwargs):
        start = time.time()
        error = None
        try:
            r = t(*args, **kwargs)
        except Exception, e:
            error = e

        end = time.time()
        duration = end - start
        try:
            dog_http_api.event(_title(t, args, kwargs, error),
                               _text(t, args, kwargs, duration, error),
                               source_type_name="fabric",
                               alert_type="error" if error else "success",
                               priority="normal",
                               aggregation_key=_aggregation_key(t, args, kwargs, error),
                               tags=_tags(t, args, kwargs, error))
        except Exception, e:
            logger.warn("Datadog notification on task {0} failed with {1}".format(t.__name__, e))

        if error:
            raise error
        else:
            return r

    return WrappedCallableTask(wrapper)
