
from random import random
from dogapi import dog_stats_api

dog_stats_api.start(statsd=True,
                    statsd_host='localhost',
                    statsd_port=9966)

while True:
    dog_stats_api.gauge('test.udp.gauge', 1000)
    dog_stats_api.increment('test.udp.counter')
    dog_stats_api.histogram('test.udp.histogram', random() * 1000)
