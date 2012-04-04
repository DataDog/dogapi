"""
Performance tests for the stats api.
"""

import hotshot
import hotshot.stats
import os
import tempfile

from dogapi import DogStatsApi


class NullReporter(object):

    def flush(self, metrics):
        pass


def measure_thousands_of_metrics():
    dog = DogStatsApi(flush_in_thread=False, roll_up_interval=5)
    dog.reporter = NullReporter()
    for i in xrange(10):
        for i in xrange(10000):
            name = i % 100
            dog.gauge('gauge.%s' % name, i)
            dog.increment('gauge.%s' % name, i)
            dog.histogram('histogram.%s' % name, i)
        (dog.flush() for i in xrange(100))


if __name__ == '__main__':
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


