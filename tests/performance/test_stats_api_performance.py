"""
Performance tests for the stats api.
"""

import hotshot
import hotshot.stats
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
    for i in range(10):
        for j in xrange(1000):
            name = j % 100
            dog.gauge('gauge.%s' % name, j)
            dog.increment('gauge.%s' % name, j)
            dog.histogram('histogram.%s' % name, j)
        print 'run %s' % i

def profile_hotshot():
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

def profile_yappi():
    import yappi
    yappi.start()
    measure_thousands_of_metrics()
    yappi.print_stats(sort_type=yappi.SORTTYPE_TSUB, sort_order=yappi.SORTORDER_DESC)



if __name__ == '__main__':
    profile_yappi()

