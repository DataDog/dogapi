import os
import time
from datetime import datetime as dt
from datetime import timedelta as delta
import math
import dogapi
from dogapi.event import Event

dog = dogapi.init(api_key=os.environ.get("DATADOG_KEY"), host="test-api.datadoghq.com")
# Emit points one by one
dog.emit_point('test.api.test_metric', 4.0)
time.sleep(1)
dog.emit_point('test.api.test_metric', 5.0)

# Emit a list of points in one go
now = dt.now()
points = []
for i in range(60, 1, -1):
    t = now - delta(minutes=i)
    points.append((t, math.cos(i)))
dog.emit_points('test.api.test_metric', points)

# Send an event too
dog.emit_event(Event("Testing done, FTW"))
