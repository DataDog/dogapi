import logging
import socket
import time
from functools import wraps

import dogapi
from collections import defaultdict # python >= 2.5

log = logging.getLogger('dogapi.metrics')

class MetricFamily(object):
    def __init__(self, name, dog=None):
        self.name = name
        self.dog = dog or dogapi.dog
        self.metrics = {}
    
    def get(self, name):
        if name not in self.metrics:
            self.metrics[name] = Metric('.'.join([self.name, name]))
        return self.metrics[name]
    
    def record(self, metric_name, value):
        self.get(metric_name).record(value)
    
    def increment(self, metric_name, value=1):
        self.get(metric_name).increment(value)
    
    def sample(self, metric_name, value):
        self.get(metric_name).sample(value)
    
    def count_calls(self, metric_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                finally:
                    self.increment(metric_name)
            return wrapper
        return decorator

    def submit(self):
        to_submit = {}
        for metric in self.metrics.values():
            to_submit[metric.name] = metric.to_series()
            aggr_val = metric.aggregated()
            log.info('{0:40} {1}'.format(metric.name, round(aggr_val, 4) if isinstance(aggr_val, float) else aggr_val))

        if to_submit:
            log.info("Submitting {0} metrics".format(self.name))
            
            # Submit metrics.
            self.dog.batch_metrics(to_submit, host=socket.gethostname())
            self.metrics = {}

class Metric(object):
    def __init__(self, name, aggregator=None):
        self.name = name
        self.values = defaultdict(lambda: 0)
        self.samples = None
        self.aggregator = aggregator or sum
    
    def get_timestamp(self):
        return int(time.time())
    
    def record(self, value):
        self.values[self.get_timestamp()] = value
    
    def increment(self, value=1):
        self.values[self.get_timestamp()] += value
    
    def sample(self, value):
        if self.samples is None:
            self.samples = defaultdict(list)
            self.aggregator = max
        
        self.samples[self.get_timestamp()].append(value)
    
    def aggregated(self):
        if self.samples is not None:
            output = []
            for vals in self.samples.values():
                output.append(self.aggregator(vals))
            return self.aggregator(output)
        else:
            return self.aggregator(self.values.values())
    
    def to_series(self):
        if self.samples is not None:
            output = []
            for key, vals in self.samples.items():
                output.append((key, self.aggregator(vals)))
            return sorted(output)
        else:
            return sorted(dict(self.values).items())
