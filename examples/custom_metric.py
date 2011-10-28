# standard imports for this example
import os
import time
from datetime import datetime as dt
from datetime import timedelta as delta
import math

# import the simple dog client
from dogapi import dog

# give dog your credentials (we're using os.environ to let you experiment via environment variables)
# in this example we're only reporting data, so we only need an API key
# see: https://github.com/DataDog/dogapi/wiki/Authentication for more on API authentication
dog.api_key = os.environ.get("DATADOG_API_KEY")

# emit points one by one. timestamp is determined at call time.
dog.metric('test.api.test_metric', 4.0, host="some_host")

time.sleep(1)

dog.metric('test.api.test_metric', 5.0, host="another_host")

# emit a list of points in one go as a list of (timestamp, value)
# here we pretend to send a point a minute for the past hour
now = dt.now()
points = []

# create the list here (a list comprehension would do too)
for i in range(60, 1, -1):
    t = time.mktime((now - delta(minutes=i)).timetuple())
    points.append((t, math.cos(i) + 1.0))

# and emit the data in one call
dog.metrics('test.api.test_metric', points, host="some_other_host")

# send an event too
dog.event("API Testing", "Testing done, FTW")
