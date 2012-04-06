"""
Performance tests for the stats api.
"""

import hotshot
import hotshot.stats
import yappi
import os
import tempfile
import time

from dogapi import DogStatsApi


class NullReporter(object):

    def flush(self, metrics):
        pass


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
        time.sleep(0.5)

def hs():
    _, logfile = tempfile.mkstemp()
    try:
        profiler = hotshot.Profile(logfile)
        profiler.runcall(measure_thousands_of_metrics)
        profiler.close()
        stats = hotshot.stats.load(logfile)
        stats.strip_dirs()
        stats.sort_stats('cumulative', 'time', 'calls')
        stats.print_stats()
    finally:
        if os.path.exists(logfile):
            os.remove(logfile)


def y():
    yappi.start()
    measure_thousands_of_metrics()
    yappi.print_stats()



if __name__ == '__main__':
    y()

