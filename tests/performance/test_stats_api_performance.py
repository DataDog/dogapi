"""
Performance tests for the stats api.
"""

import os
import random
import tempfile
import time

import yappi

from dogapi import DogStatsApi


class NullReporter(object):
    """
    A DogAPI to nowhere.
    """

    def flush(self, metrics):
        print 'flushing metrics'


class NullDogStatsApi(DogStatsApi):
    """
    A DogStats API that does nothing, for comparing the effects
    of including DogApi in your program.
    """

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def gauge(self, *args, **kwargs):
        pass

    def increment(self, *args, **kwargs):
        pass

    def histogram(self, *args, **kwargs):
        pass


class CPUBoundProgram(object):

    def __init__(self, dog_stats_api):
        self.dog_stats_api = dog_stats_api

    def run(self):
        for i in range(100000):
            self.dog_stats_api.gauge('current.number', i)
            self.dog_stats_api.increment('numbers.checked')
            j = 0
            start = time.time()
            while j < i:
                j += 1
            self.dog_stats_api.histogram('number.check.time', time.time() - start)


def profile_cpu_bound_program():
    real_dog = DogStatsApi()
    real_dog.reporter = NullReporter()
    fake_dog = NullDogStatsApi()
    for type_, dog in [('real', real_dog), ('fake', fake_dog)]:
        print '\n\n\nTESTING %s\n\n' % type_
        dog.start()
        program = CPUBoundProgram(dog)
        yappi.start()
        program.run()
        yappi.print_stats(sort_type=yappi.SORTTYPE_TSUB, sort_order=yappi.SORTORDER_DESC)
        yappi.stop()
        yappi.clear_stats()



def measure_thousands_of_metrics():
    dog = DogStatsApi()
    dog.start(api_key='apikey_3', api_host="https://app.datad0g.com")
    for i in range(100):
        for j in xrange(1000):
            name = j % 100
            dog.gauge('gauge.%s' % name, j)
            dog.increment('gauge.%s' % name, j)
            dog.histogram('histogram.%s' % name, j)
        print 'run %s' % i

def profile_yappi():
    profile_cpu_bound_program()



if __name__ == '__main__':
    profile_yappi()

