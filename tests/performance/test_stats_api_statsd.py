from dogapi import dog_stats_api as d


d.start(statsd=True, statsd_port=9999)


for i in xrange(10000):
    d.gauge('my.gauge', 1, sample_rate=0.5)
    d.increment('my.counter', sample_rate=0.01)
