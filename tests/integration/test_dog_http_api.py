# python
import datetime
import os
import time
import unittest

# nose
from nose.plugins.attrib import attr

# dogapi
import dogapi
from dogapi.exceptions import *
from snapshot_test_utils import (
    assert_not_blank, assert_has_no_events
)


TEST_USER = os.environ.get('DATADOG_TEST_USER')
API_KEY = os.environ.get('DATADOG_API_KEY')
APP_KEY = os.environ.get('DATADOG_APP_KEY')

# Our
dog = None

class TestDatadog(unittest.TestCase):

    def setUp(self):
        global dog
        dog = dogapi.DogHttpApi()
        dog.api_key = API_KEY
        dog.application_key = APP_KEY
        dog.swallow = False

    def test_tags(self):
        # post a metric to make sure the test host context exists
        hostname = 'test.tag.host'
        dog.metric('test.tag.metric', 1, host=hostname)

        dog.all_tags()

        dog.detach_tags(hostname)
        assert len(dog.host_tags(hostname)) == 0

        dog.add_tags(hostname, ['test.tag.1', 'test.tag.2'], source='datadog')
        new_tags = dog.host_tags(hostname)
        assert len(new_tags) == 2
        assert 'test.tag.1' in new_tags
        assert 'test.tag.2' in new_tags

        dog.add_tags(hostname, ['test.tag.3'], source='datadog')
        new_tags = dog.host_tags(hostname)
        assert len(new_tags) == 3
        assert 'test.tag.1' in new_tags
        assert 'test.tag.2' in new_tags
        assert 'test.tag.3' in new_tags

        dog.change_tags(hostname, ['test.tag.4'], source='datadog')
        new_tags = dog.host_tags(hostname)
        assert len(new_tags) == 1
        assert 'test.tag.4' in new_tags

        dog.detach_tags(hostname, source='datadog')
        assert len(dog.host_tags(hostname)) == 0

    def test_events(self):
        now = datetime.datetime.now()

        now_ts = int(time.mktime(now.timetuple()))
        now_title = 'end test title ' + str(now_ts)
        now_message = 'test message ' + str(now_ts)

        before_ts = int(time.mktime((now - datetime.timedelta(minutes=5)).timetuple()))
        before_title = 'start test title ' + str(before_ts)
        before_message = 'test message ' + str(before_ts)

        now_event_id = dog.event_with_response(now_title, now_message, now_ts)
        before_event_id = dog.event_with_response(before_title, before_message, before_ts)
        time.sleep(2)

        now_event = dog.get_event(now_event_id)
        before_event = dog.get_event(before_event_id)

        self.assertEquals(now_event['text'], now_message)
        self.assertEquals(before_event['text'], before_message)

        event_id = dog.event_with_response('test host and device', 'test host and device', host='test.host', device_name='test.device')
        time.sleep(2)
        event = dog.get_event(event_id)

        self.assertEquals(event['host'], 'test.host')
        self.assertEquals(event['device_name'], 'test.device')

        event_id = dog.event_with_response('test event tags', 'test event tags', tags=['test-tag-1','test-tag-2'])
        time.sleep(2)
        event = dog.get_event(event_id)

        assert 'test-tag-1' in event['tags']
        assert 'test-tag-2' in event['tags']

    def test_aggregate_events(self):
        now_ts = int(time.time())
        agg_key = 'aggregate_me ' + str(now_ts)
        msg_1 = 'aggregate 1'
        msg_2 = 'aggregate 2'

        # send two events that should aggregate
        event1_id = dog.event_with_response(msg_1, msg_1, aggregation_key=agg_key)
        event2_id = dog.event_with_response(msg_2, msg_2, aggregation_key=agg_key)
        time.sleep(3)

        event1 = dog.get_event(event1_id)
        event2 = dog.get_event(event2_id)

        self.assertEquals(msg_1, event1['text'])
        self.assertEquals(msg_2, event2['text'])

        # FIXME: Need the aggregation_id to check if they are attached to the
        # same aggregate

    def test_git_commits(self):
        """Pretend to send git commits"""
        event_id = dog.event_with_response("Testing git commits", """$$$
eac54655 *   Merge pull request #2 from DataDog/alq-add-arg-validation (alq@datadoghq.com)
         |\
760735ef | * origin/alq-add-arg-validation Simple typechecking between metric and metrics (matt@datadoghq.com)
         |/
f7a5a23d * missed version number in docs (matt@datadoghq.com)
$$$""", event_type="commit", source_type_name="git", event_object="0xdeadbeef")

        time.sleep(1)
        event = dog.get_event(event_id)

        self.assertEquals(event.get("title", ""), "Testing git commits")

    def test_comments(self):
        now = datetime.datetime.now()
        now_ts = int(time.mktime(now.timetuple()))
        before_ts = int(time.mktime((now - datetime.timedelta(minutes=5)).timetuple()))
        message = 'test message ' + str(now_ts)

        comment_id = dog.comment(TEST_USER, message)
        event = dog.get_event(comment_id)
        assert event['text'] == message

        dog.update_comment(TEST_USER, message + ' updated', comment_id)
        event = dog.get_event(comment_id)
        assert event['text'] == message + ' updated'

        reply_id = dog.comment(TEST_USER, message + ' reply', related_event_id=comment_id)

        # Add a bit of latency for the comment to appear
        time.sleep(1)
        stream = dog.stream(before_ts, now_ts + 10)

        assert reply_id in [x['id'] for x in stream[0]['comments']], "Should find {0} in {1}".format(reply_id, [x['id'] for x in stream[0]['comments']])

        # Delete the reply
        dog.delete_comment(reply_id)
        # Then the post itself
        dog.delete_comment(comment_id)
        try:
            dog.get_event(comment_id)
        except:
            pass
        else:
            assert False


    @attr('dashboards')
    def test_dash(self):

        graph = {
                "title": "test metric graph",
                "definition":
                    {
                        "requests": [{"q": "testing.metric.1{host:blah.host.1}"}],
                        "viz": "timeseries",
                    }
                }
        dash_id = dog.create_dashboard('api dash', 'my api dash', [graph])

        remote_dash = dog.dashboard(dash_id)

        assert 'api dash' == remote_dash['title']
        assert graph['definition']['requests'] == remote_dash['graphs'][0]['definition']['requests']

        graph = {
                "title": "updated test metric graph",
                "definition":
                    {
                        "requests": [{"q": "testing.metric.1{host:blah.host.1}"}],
                        "viz": "timeseries",
                    }
                }

        dash_id = dog.update_dashboard(dash_id, 'updated api dash', 'my api dash', [graph],
                                       template_variables=['foo', 'bar'])

        # Query and ensure all is well.
        remote_dash = dog.dashboard(dash_id)

        assert 'updated api dash' == remote_dash['title']
        self.assertEqual([
            {'default': None, 'name': 'foo', 'prefix': None},
            {'default': None, 'name': 'bar', 'prefix': None},
        ], remote_dash['template_variables'])

        p = graph['definition']['requests']
        assert graph['definition']['requests'] == remote_dash['graphs'][0]['definition']['requests']

        # Query all dashboards and make sure it's in there.

        dashes = dog.dashboards()
        ids = [dash["id"] for dash in dashes]
        assert dash_id in ids or str(dash_id) in ids

        dog.delete_dashboard(dash_id)

        try:
            d = dog.dashboard(dash_id)
        except:
            pass
        else:
            # the previous get *should* throw and exception
            assert False

    def test_search(self):
        results = dog.search('e')
        assert len(results['hosts']) > 0
        assert len(results['metrics']) > 0

    def test_metrics(self):
        now = datetime.datetime.now()
        now_ts = int(time.mktime(now.timetuple()))

        dog.metric('test.metric.' + str(now_ts), 1, host="test.host." + str(now_ts))
        time.sleep(4)

        results = dog.search('metrics:test.metric.' + str(now_ts))
        # FIXME mattp: cache issue. move this test to server side.
        #assert len(results['metrics']) == 1, results

        matt_series = [
                (int(time.mktime((now - datetime.timedelta(minutes=25)).timetuple())), 5),
                (int(time.mktime((now - datetime.timedelta(minutes=25)).timetuple())) + 1, 15),
                (int(time.mktime((now - datetime.timedelta(minutes=24)).timetuple())), 10),
                (int(time.mktime((now - datetime.timedelta(minutes=23)).timetuple())), 15),
                (int(time.mktime((now - datetime.timedelta(minutes=23)).timetuple())) + 1, 5),
                (int(time.mktime((now - datetime.timedelta(minutes=22)).timetuple())), 5),
                (int(time.mktime((now - datetime.timedelta(minutes=20)).timetuple())), 15),
                (int(time.mktime((now - datetime.timedelta(minutes=18)).timetuple())), 5),
                (int(time.mktime((now - datetime.timedelta(minutes=17)).timetuple())), 5),
                (int(time.mktime((now - datetime.timedelta(minutes=17)).timetuple())) + 1, 15),
                (int(time.mktime((now - datetime.timedelta(minutes=15)).timetuple())), 15),
                (int(time.mktime((now - datetime.timedelta(minutes=15)).timetuple())) + 1, 5),
                (int(time.mktime((now - datetime.timedelta(minutes=14)).timetuple())), 5),
                (int(time.mktime((now - datetime.timedelta(minutes=14)).timetuple())) + 1, 15),
                (int(time.mktime((now - datetime.timedelta(minutes=12)).timetuple())), 15),
                (int(time.mktime((now - datetime.timedelta(minutes=12)).timetuple())) + 1, 5),
                (int(time.mktime((now - datetime.timedelta(minutes=11)).timetuple())), 5),
                ]

        dog.metric('matt.metric', matt_series, host="matt.metric.host")

        dog.metrics({
                'test.metric1': [(1000000000, 1), (1000000000, 2)],
                'test.metric2': [(1000000000, 2), (1000000000, 4)],
        })

    def test_type_check(self):
        dog.metric("test.metric", [(time.time() - 3600, 1.0)])
        dog.metric("test.metric", 1.0)
        dog.metric("test.metric", (time.time(), 1.0))

    def test_alerts(self):
        query = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 100"

        alert_id = dog.alert(query)
        alert = dog.get_alert(alert_id)
        assert alert['query'] == query, alert['query']
        assert alert['silenced'] == False, alert['silenced']
        assert alert['notify_no_data'] == False, alert['notify_no_data']

        dog.update_alert(alert_id, query, silenced=True)
        alert = dog.get_alert(alert_id)
        assert alert['query'] == query, alert['query']
        assert alert['silenced'] == True, alert['silenced']

        dog.update_alert(alert_id, query, silenced=True, notify_no_data=True, timeout_h=1)
        alert = dog.get_alert(alert_id)
        assert alert['query'] == query, alert['query']
        assert alert['silenced'] == True, alert['silenced']
        assert alert['notify_no_data'] == True, alert['notify_no_data']
        assert alert['timeout_h'] == 1, alert['timeout_h']

        dog.delete_alert(alert_id)
        try:
            dog.get_alert(alert_id)
        except:
            pass
        else:
            assert False, 'alert not deleted'

        query1 = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 100"
        query2 = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 200"

        alert_id1 = dog.alert(query1)
        alert_id2 = dog.alert(query2)
        alerts = dog.get_all_alerts()
        alert1 = [a for a in alerts if a['id'] == alert_id1][0]
        alert2 = [a for a in alerts if a['id'] == alert_id2][0]
        assert alert1['query'] == query1, alert1
        assert alert2['query'] == query2, alert2

    def test_user_error(self):
        query = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 100"

        dog.swallow = True
        dog.json_responses = True

        alert = dog.alert(query)
        assert 'id' in alert, alert
        result = dog.update_alert(alert['id'], 'aaa', silenced=True)
        assert 'errors' in result, result

        dog.swallow = True
        dog.json_responses = False

        alert_id = dog.alert(query)
        assert alert_id == int(alert_id), alert_id
        result = dog.update_alert(alert_id, 'aaa', silenced=True)
        assert 'errors' in result, result

        dog.swallow = False
        dog.json_responses = False

        alert_id = dog.alert(query)
        assert alert_id == int(alert_id), alert_id
        try:
            result = dog.update_alert(alert_id, 'aaa', silenced=True)
        except ApiError, e:
            pass
        else:
            raise False, "Should have raised an exception"

    @attr('snapshot')
    def test_graph_snapshot(self):
        metric_query = "system.load.1{*}"
        event_query = "*"
        end = int(time.time())
        start = end - 60 * 60 # go back 1 hour

        # Test without an event query
        snap = dog.graph_snapshot(metric_query, start, end)
        time.sleep(3)  # Give API enough time to create the snapshot
        assert 'snapshot_url' in snap, snap
        assert 'metric_query' in snap, snap
        assert 'event_query' not in snap, snap
        assert snap['metric_query'] == metric_query
        snapshot_url = snap['snapshot_url']
        assert_not_blank(snapshot_url)
        assert_has_no_events(snapshot_url)

        # Test with an event query
        snap = dog.graph_snapshot(metric_query, start, end,
                                  event_query=event_query)
        time.sleep(3)  # Give API enough time to create the snapshot
        assert 'snapshot_url' in snap, snap
        assert 'metric_query' in snap, snap
        assert 'event_query' in snap, snap
        assert snap['metric_query'] == metric_query
        assert snap['event_query'] == event_query
        assert_not_blank(snap['snapshot_url'])

    @attr('screenboard')
    def test_screenboard(self):
        def _compare_screenboard(board1, board2):
            compare_keys = ['board_title', 'height', 'width', 'widgets']
            for key in compare_keys:
                assert board1[key] == board2[key], key

        board = {
            "width": 1024,
            "height": 768,
            "board_title": "dogapi test",
            "widgets": [
                {
                    "type": "event_stream",
                    "title": False,
                    "height": 57,
                    "width": 59,
                    "y": 18,
                    "x": 84,
                    "query": "tags:release",
                    "timeframe": "1w"
                },
                {
                  "type": "image",
                  "height": 20,
                  "width": 32,
                  "y": 7,
                  "x": 32,
                  "url": "http://path/to/image.jpg"
                }
            ]
        }

        updated_board = {
            "width": 1024,
            "height": 768,
            "board_title": "dogapi test",
            "widgets": [
                {
                  "type": "image",
                  "height": 20,
                  "width": 32,
                  "y": 7,
                  "x": 32,
                  "url": "http://path/to/image.jpg"
                }
            ]
        }

        create_res = dog.create_screenboard(board)
        _compare_screenboard(board, create_res)

        get_res = dog.get_screenboard(create_res['id'])
        _compare_screenboard(get_res, create_res)
        assert get_res['id'] == create_res['id']

        update_res = dog.update_screenboard(get_res['id'], updated_board)
        _compare_screenboard(update_res, updated_board)
        assert get_res['id'] == update_res['id']

        share_res = dog.share_screenboard(get_res['id'])
        assert share_res['board_id'] == get_res['id']

        delete_res = dog.delete_screenboard(update_res['id'])
        assert delete_res['id'] == update_res['id']


if __name__ == '__main__':
    unittest.main()
