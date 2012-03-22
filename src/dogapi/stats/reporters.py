"""
Reporter classes.
"""


from dogapi import DogHttpApi


class Reporter(object):

    def flush(self, metrics):
        raise NotImplementedError()


class HTTPReporter(Reporter):

    def __init__(self, api_key=None,
                       application_key=None,
                       api_host=None,

    def flush(self, metrics):
        pass


class GraphiteReporter(Reporter):

    def flush(self, metrics):
        pass
