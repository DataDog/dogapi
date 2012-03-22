"""
Tests for metric aggregation/
"""

import nose.tools as nt

from metrics import Counter, Histogram, Gauge

def test_counter():
    counter = Counter('my.counter', 10)

    # Increment the counter in two finished intervals and one incomplete.
    counter.add_point(1000.0, 1)
    counter.add_point(1000.5, 1)
    counter.add_point(1009.9, 3)

    counter.add_point(1010.0, 1)
    counter.add_point(1015.1, 2)

    counter.add_point(1022.1, 2)

    # Flush and make sure they roll-up correctly.
    metrics = counter.flush(1020.0)
    nt.assert_equals(2, len(metrics))
    (first, second) = metrics
    nt.assert_equals(first[0], 1000.0)
    nt.assert_equals(first[1], 5)
    nt.assert_equals(first[2], 'my.counter')

    nt.assert_equals(second[0], 1010.0)
    nt.assert_equals(second[1], 3)
    nt.assert_equals(second[2], 'my.counter')

    # Flush again and make sure their gone.
    metrics = counter.flush(1021.0)
    assert not metrics

    # And flush the last interval.
    metrics = counter.flush(1031.0)
    nt.assert_equal(1, len(metrics))

def test_histogram():
    histogram = Histogram('query.time', 10)
    histogram.add_point(1000.0, 10)
    histogram.add_point(1001.0, 15)
    histogram.add_point(1002.0, 20)

    # Assert histograms roll-up correctly.
    metrics = histogram.flush(1020)
    nt.assert_equals(2, len(metrics))
    (avg, count) = metrics

    nt.assert_equals(avg[0], 1000.0)
    nt.assert_equals(avg[1], 15)
    nt.assert_equals(avg[2], 'query.time.avg')

    nt.assert_equals(count[0], 1000.0)
    nt.assert_equals(count[1], 3)
    nt.assert_equals(count[2], 'query.time.count')

def test_gauge():
    gauge = Gauge('room.temperature', 10)
    gauge.add_point(10.0, 25)
    gauge.add_point(12.0, 27)
    gauge.add_point(21.0, 10)

    # Assert gauges only store one value per flush interval.
    metrics = gauge.flush(1020)
    nt.assert_equals(2, len(metrics))
    (first, second) = metrics

    nt.assert_equals(first[0], 10.0)
    nt.assert_equals(first[1], 27)
    nt.assert_equals(first[2], 'room.temperature')

    nt.assert_equals(second[0], 20.0)
    nt.assert_equals(second[1], 10)
