"""
Reporter classes.
"""


from dogapi import DogHttpApi


class Reporter(object):

    def flush(self, metrics):
        raise NotImplementedError()


class HttpReporter(Reporter):

    def __init__(self, api_key=None, api_host=None):
        self.dog = DogHttpApi(api_key=api_key, api_host=api_host)

    def flush(self, metrics):
        self.dog.metrics(metrics)

class GraphiteReporter(Reporter):

    def flush(self, metrics):
        pass
