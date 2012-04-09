import logging
from dogapi import dog_stats_api



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
logger.addHandler(ch)


dog_stats_api.start(api_key="6233a8363aa294e0cee787f46d98496b",
                    api_host="http://localhost:9000")

while True:
    for i in range(100):
        dog_stats_api.gauge('test.tag.metric.%s' % i, 10)
    import time
    time.sleep(0.5)


