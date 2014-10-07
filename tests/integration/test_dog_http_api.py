# python
import datetime
import os
import time
import unittest

# 3p
from nose.plugins.attrib import attr
import nose.tools as nt
from nose.tools import assert_equal as eq
from nose.tools import assert_true as ok
import simplejson as json

# dogapi
import dogapi
from dogapi.exceptions import *
from tests.util.snapshot_test_utils import (
    assert_snap_not_blank, assert_snap_has_no_events
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
        wait_time = 10  # seconds
        now = datetime.datetime.now()

        now_ts = int(time.mktime(now.timetuple()))
        now_title = 'end test title ' + str(now_ts)
        now_message = 'test message ' + str(now_ts)

        before_ts = int(time.mktime((now - datetime.timedelta(minutes=5)).timetuple()))
        before_title = 'start test title ' + str(before_ts)
        before_message = 'test message ' + str(before_ts)

        now_event_id = dog.event_with_response(now_title, now_message, now_ts)
        before_event_id = dog.event_with_response(before_title, before_message, before_ts)
        time.sleep(wait_time)

        now_event = dog.get_event(now_event_id)
        before_event = dog.get_event(before_event_id)

        self.assertEquals(now_event['text'], now_message)
        self.assertEquals(before_event['text'], before_message)

        event_id = dog.event_with_response('test host and device',
                                           'test host and device',
                                           host='test.host',
                                           device_name='test.device')
        time.sleep(wait_time)
        event = dog.get_event(event_id)

        self.assertEquals(event['host'], 'test.host')
        self.assertEquals(event['device_name'], 'test.device')

        event_id = dog.event_with_response('test event tags',
                                           'test event tags',
                                           tags=['test-tag-1', 'test-tag-2'])
        time.sleep(wait_time)
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
        time.sleep(10)

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

        time.sleep(10)
        event = dog.get_event(event_id)

        self.assertEquals(event.get("title", ""), "Testing git commits")

    def test_comments(self):
        wait_time = 3  # seconds
        now = datetime.datetime.now()
        now_ts = int(time.mktime(now.timetuple()))
        before_ts = int(time.mktime((now - datetime.timedelta(minutes=15)).timetuple()))
        message = 'test message ' + str(now_ts)

        comment_id = dog.comment(TEST_USER, message)
        time.sleep(wait_time)
        event = dog.get_event(comment_id)
        eq(event['text'], message)

        dog.update_comment(TEST_USER, message + ' updated', comment_id)
        time.sleep(wait_time)
        event = dog.get_event(comment_id)
        eq(event['text'], message + ' updated')

        reply_id = dog.comment(TEST_USER, message + ' reply', related_event_id=comment_id)
        time.sleep(wait_time)
        stream = dog.stream(before_ts, now_ts+100)

        ok(stream is not None, msg="No events found in stream")
        ok(isinstance(stream, list), msg="Event stream is not a list")
        ok(len(stream) > 0, msg="No events found in stream")

        comment_ids = [x['id'] for x in stream[0]['comments']]
        ok(reply_id in comment_ids,
           msg="Should find {0} in {1}".format(reply_id, comment_ids))

        # Delete the reply
        dog.delete_comment(reply_id)
        # Then the post itself
        dog.delete_comment(comment_id)
        time.sleep(wait_time)
        try:
            dog.get_event(comment_id)
        except:
            pass
        else:
            assert False

    @attr('dashboards', 'validation')
    def test_dash_validation(self):
        graph = {
            "title": "test metric graph",
            "definition":
                {
                    "requests": [{"q": "testing.metric.1{host:blah.host.1}"}],
                    "viz": "timeseries",
                }
        }

        # No title
        try:
            dog.create_dashboard(None, 'my api dash', [graph])
            assert False, "Should report an api error"
        except ApiError, e:
            exception_msg = e.message['errors'][0]
            eq(exception_msg, "The parameter 'title' is required")

        # No description
        try:
            dog.create_dashboard('api dash', None, [graph])
            assert False, "Should report an api error"
        except ApiError, e:
            exception_msg = e.message['errors'][0]
            eq(exception_msg, "The parameter 'description' is required")

        # No graph
        try:
            dog.create_dashboard('api dash', 'my api dash', None)
            assert False, "Should report an api error"
        except ApiError, e:
            exception_msg = e.message['errors'][0]
            eq(exception_msg, "The parameter 'graphs' is required")

        # Graphs not list
        try:
            dog.create_dashboard('api dash', 'my api dash', graph)
            assert False, "Should report an api error"
        except ApiError, e:
            exception_msg = e.message['errors'][0]
            eq(exception_msg, "The 'graphs' parameter is required to be a list")

        # Empty list of graphs
        try:
            dog.create_dashboard('api dash', 'my api dash', [])
            assert False, "Should report an api error"
        except ApiError, e:
            exception_msg = e.message['errors'][0]
            eq(exception_msg, "The 'graphs' parameter is required")

        # None in the graph list
        try:
            dog.create_dashboard('api dash', 'my api dash', [graph, None])
            assert False, "Should report an api error"
        except ApiError, e:
            exception_msg = e.message['errors'][0]
            eq(exception_msg, "The 'graphs' parameter contains None graphs")

        # Dashboard not found
        try:
            dog.dashboard(999999)
            assert False, "Should report an api error"
        except ApiError, e:
            exception_msg = e.message['errors'][0]
            eq(exception_msg, "No dashboard matches that dash_id.")

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

        eq('api dash', remote_dash['title'])
        eq('my api dash', remote_dash['description'])
        eq(graph['definition']['requests'], remote_dash['graphs'][0]['definition']['requests'])

        graph = {
            "title": "updated test metric graph",
            "definition": {
                "requests": [{"q": "testing.metric.1{host:blah.host.1}"}],
                "viz": "timeseries",
            }
        }

        dash_id = dog.update_dashboard(dash_id, 'updated api dash',
                                       'my updated api dash', [graph],
                                       template_variables=['foo', 'bar'])

        # Query and ensure all is well.
        remote_dash = dog.dashboard(dash_id)

        eq('updated api dash', remote_dash['title'])
        eq('my updated api dash', remote_dash['description'])
        self.assertEqual([
            {'default': None, 'name': 'foo', 'prefix': None},
            {'default': None, 'name': 'bar', 'prefix': None},
        ], remote_dash['template_variables'])

        p = graph['definition']['requests']
        eq(p, remote_dash['graphs'][0]['definition']['requests'])

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
            # the previous get *should* throw an exception
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
        time.sleep(10)
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
        start = end - 60 * 60  # go back 1 hour

        # Test without an event query
        snap = dog.graph_snapshot(metric_query, start, end)
        ok('snapshot_url' in snap, msg=snap)
        ok('metric_query' in snap, msg=snap)
        ok('event_query' not in snap, msg=snap)
        eq(snap['metric_query'], metric_query)
        snapshot_url = snap['snapshot_url']
        while dog.snapshot_status(snapshot_url) != 200:
            time.sleep(2)
        if 'localhost' in dog.api_host:
            snapshot_url = 'http://%s%s' % (dog.api_host, snapshot_url)
        assert_snap_not_blank(snapshot_url)
        assert_snap_has_no_events(snapshot_url)

        # Test with an event query
        snap = dog.graph_snapshot(metric_query, start, end,
                                  event_query=event_query)
        ok('snapshot_url' in snap, msg=snap)
        ok('metric_query' in snap, msg=snap)
        ok('event_query' in snap, msg=snap)
        eq(snap['metric_query'], metric_query)
        eq(snap['event_query'], event_query)
        snapshot_url = snap['snapshot_url']
        while dog.snapshot_status(snapshot_url) != 200:
            time.sleep(2)
        if 'localhost' in dog.api_host:
            snapshot_url = 'http://%s%s' % (dog.api_host, snapshot_url)
        assert_snap_not_blank(snapshot_url)

        # Test with a graph def
        graph_def = {
            "viz": "toplist",
            "requests": [{
                "q": "top(system.disk.free{*} by {device}, 10, 'mean', 'desc')",
                "style": {
                    "palette": "dog_classic"
                },
                "conditional_formats": [{
                    "palette": "red",
                    "comparator": ">",
                    "value": 50000000000
                }, {
                    "palette": "green",
                    "comparator": ">",
                    "value": 30000000000
                }]
            }]
        }
        graph_def = json.dumps(graph_def)
        snap = dog.graph_snapshot_from_def(graph_def, start, end)
        ok('snapshot_url' in snap, msg=snap)
        ok('graph_def' in snap, msg=snap)
        ok('metric_query' not in snap, msg=snap)
        ok('event_query' not in snap, msg=snap)
        eq(snap['graph_def'], graph_def)
        snapshot_url = snap['snapshot_url']
        while dog.snapshot_status(snapshot_url) != 200:
            time.sleep(2)
        if 'localhost' in dog.api_host:
            snapshot_url = 'http://%s%s' % (dog.api_host, snapshot_url)
        assert_snap_not_blank(snapshot_url)

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

    @attr('monitor')
    def test_monitor_crud(self):
        # Metric alerts
        query = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 100"

        options = {
            'silenced': {'*': time.time() + 60 * 60},
            'notify_no_data': False
        }
        monitor_id = dog.monitor('metric alert', query, options=options)
        monitor = dog.get_monitor(monitor_id)

        nt.assert_equal(monitor['query'], query)
        nt.assert_equal(monitor['options']['notify_no_data'],
            options['notify_no_data'])
        nt.assert_equal(monitor['options']['silenced'], options['silenced'])

        query2 = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 200"
        updated_monitor_id = dog.update_monitor(monitor_id, query2, options=options)
        monitor = dog.get_monitor(updated_monitor_id)
        nt.assert_equal(monitor['query'], query2)

        name = 'test_monitors'
        monitor_id = dog.update_monitor(monitor_id, query2, name=name,
            options={'notify_no_data': True})
        monitor = dog.get_monitor(monitor_id)
        nt.assert_equal(monitor['name'], name)
        nt.assert_equal(monitor['options']['notify_no_data'], True)

        dog.delete_monitor(monitor_id)
        try:
            dog.get_monitor(monitor_id)
        except ApiError:
            pass
        else:
            assert False, 'monitor not deleted'

        query1 = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 100"
        query2 = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 200"

        monitor_id1 = dog.monitor('metric alert', query1)
        monitor_id2 = dog.monitor('metric alert', query2)
        monitors = dog.get_all_monitors()
        monitor1 = [m for m in monitors if m['id'] == monitor_id1][0]
        monitor2 = [m for m in monitors if m['id'] == monitor_id2][0]
        assert monitor1['query'] == query1, monitor1
        assert monitor2['query'] == query2, monitor2

        # Service checks
        query = '"ntp.in_sync".over("role:herc").last(3).count_by_status()'
        options = {
            'notify_no_data': False,
            'thresholds': {
                'ok': 3,
                'warning': 2,
                'critical': 1,
                'no data': 3
            }
        }
        monitor_id = dog.monitor('service check', query, options=options)
        monitor = dog.get_monitor(monitor_id)

        nt.assert_equal(monitor['query'], query)
        nt.assert_equal(monitor['options']['notify_no_data'],
            options['notify_no_data'])
        nt.assert_equal(monitor['options']['thresholds'], options['thresholds'])

        query2 = '"ntp.in_sync".over("role:sobotka").last(3).count_by_status()'
        monitor_id = dog.update_monitor(monitor_id, query2)
        monitor = dog.get_monitor(monitor_id)
        nt.assert_equal(monitor['query'], query2)

        dog.delete_monitor(monitor_id)
        try:
            dog.get_monitor(monitor_id)
        except ApiError:
            pass
        else:
            assert False, 'monitor not deleted'

    @attr('monitor')
    def test_monitor_muting(self):
        query = "avg(last_1h):sum:system.net.bytes_rcvd{host:host0} > 100"
        monitor_id = dog.monitor('metric alert', query)
        monitor = dog.get_monitor(monitor_id)
        nt.assert_equal(monitor['query'], query)

        dt = dog.mute_monitors()
        nt.assert_equal(dt['active'], True)
        nt.assert_equal(dt['scope'], ['*'])

        dt = dog.unmute_monitors()
        nt.assert_equal(dt, None) # No response is expected.

        # We shouldn't be able to mute a simple alert on a scope.
        nt.assert_raises(ApiError, dog.mute_monitor, monitor_id, scope='env:staging')

        query2 = "avg(last_1h):sum:system.net.bytes_rcvd{*} by {host} > 100"
        monitor_id = dog.monitor('metric alert', query2)
        monitor = dog.get_monitor(monitor_id)
        nt.assert_equal(monitor['query'], query2)

        dog.mute_monitor(monitor_id, scope='host:foo')
        monitor = dog.get_monitor(monitor_id)
        nt.assert_equal(monitor['options']['silenced'], {'host:foo': None})

        dog.unmute_monitor(monitor_id, scope='host:foo')
        monitor = dog.get_monitor(monitor_id)
        nt.assert_equal(monitor['options']['silenced'], {})

        dog.delete_monitor(monitor_id)

    @attr('monitor')
    def test_downtime(self):
        start = int(time.time())
        end = start + 1000
        downtime_id = dog.schedule_downtime('env:staging', start, end)
        dt = dog.get_downtime(downtime_id)
        nt.assert_equal(dt['start'], start)
        nt.assert_equal(dt['end'], end)
        nt.assert_equal(dt['scope'], ['env:staging'])

        dog.cancel_downtime(downtime_id)

    @attr('monitor')
    def test_service_check(self):
        res = dog.service_check('check_pg', 'host0', int(time.time()), 1,
            message='PG is WARNING', tags=['db:prod_data'])

if __name__ == '__main__':
    unittest.main()
