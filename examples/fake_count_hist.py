
import logging
import os
import random
import time


import dogapi

# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

# create logger
dog = dogapi.dog_stats_api

dog.start(
    api_key='apikey_3',
    api_host = 'https://app.datad0g.com',
    flush_interval = 15,
    flush_in_thread = True)

j = 0

while True:
    j += random.random() * 2 - 0.1
    for i in xrange(100):
        dog.increment('perpick.test.counter')
        dog.histogram('perpick.test.histogram', j)
    for i in xrange(10):
        dog.gauge('perpick.test.gauge.%s' % i, i)
    time.sleep(0.05)
    print 'doing it'
