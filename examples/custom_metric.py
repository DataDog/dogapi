# standard imports for this example
import os
import time
from datetime import datetime as dt
from datetime import timedelta as delta
import math

# imports needed to emit metrics and events
import dogapi
from dogapi.event import Event

# Create a client
# host is optional here, it's a shortcut to tie event and metrics to a given host
# you typically want to do:
# dogapi.init(api_key=actual_api_key_as_a_string, ...)
# We are using os.environ to let you experiment via an environment variable.
dog = dogapi.init(api_key=os.environ.get("DATADOG_KEY"), host="test-api.datadoghq.com")

# Emit points one by one, timestamp is omitted and is the time this call is made.
dog.emit_point('test.api.test_metric', 4.0)

time.sleep(1)

dog.emit_point('test.api.test_metric', 5.0, host="another_host")

# Emit a list of points in one go as a list of (timestamp, value)
# here we pretend to send a point a minute for the past hour
now = dt.now()
points = []

# create the list here (a list comprehension would do too)
for i in range(60, 1, -1):
    t = now - delta(minutes=i)
    points.append((t, math.cos(i) + 1.0))

# And emit the data in one call
dog.emit_points('test.api.test_metric', points)

# Send an event too, automatically tied to the same host
dog.emit_event(Event("Testing done, FTW"))

# To record an event with duration
with dog.start_event(Event("My event with a duration")):
    # do your work here...
    time.sleep(1)
# stop_event will be send automatically
