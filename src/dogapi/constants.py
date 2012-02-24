class DeliveryTiming(object):
    Immediate = 'immediate'
    Never = 'never'

class DeliveryMethod(object):
    Http = 'http'
    Statsd = 'statsd'

class MetricType(object):
    Gauge = "gauge"
    Counter = "counter"
    Timer = "timer"
    Sampler = "sampler"
