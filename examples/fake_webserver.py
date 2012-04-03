
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

dog = dogapi.dog_stats_api

dog.start(
#dog.api_key = '9863dbd9474b5589d36bca341d9f0703'
#dog.application_key = '89336306d9899fb127123ad7d4daba2389033778'
    api_key='apikey_3',
    api_host = 'https://app.datad0g.com',
    flush_interval = 5,
    flush_in_thread=True)

time.sleep(3)
dog._start_flush_thread()
dog._start_flush_thread()
dog._start_flush_thread()
users_online = 0
page_hits = 0

def render_template(a, b, c=1, d=2):
    assert c == 1

class Controller(object):

    x = 'a'

    @dog.timed('perpick.test.render.template.time')
    def render(self, a):
        assert self.x == 'a'

def track():
    for i in xrange(500):
        dog.histogram('perpick.test.page_load_time', random.randint(10, 100))
        dog.increment('perpick.test.page_hits.%s' % i)
        dog.increment('perpick.test.cache_hits', random.randint(0, 20))
        dog.gauge('perpick.test.users_online', users_online)

        c = Controller()
        c.render('a')
        render_template('a', 'b', d=4)

while True:
    track()
    print 'posted metrics'

    time.sleep(0.1)
    if int(time.time()) % 10 == 0:
        dog.gauge('perpick.test.gauge', 10)

