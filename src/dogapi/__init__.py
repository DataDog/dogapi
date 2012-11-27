from dogapi.http import DogHttpApi
from dogapi.stats import DogStatsApi

# make sure there's at least some basic logging configured
import logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

#FIXME matt: remove the 'dog' variable.
dog = dog_stats_api = DogStatsApi()
dog_http_api = DogHttpApi()
