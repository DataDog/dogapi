# python
import random, math
import datetime
import unittest
import os

# nose
from nose.plugins.skip import SkipTest

# dogapi
from dogapi import dog
import datetime, time


class TestSimpleClient(unittest.TestCase):

    def setUp(self):
        dog.api_key = os.environ.get('DATADOG_API_KEY')
        dog.application_key = os.environ.get('DATADOG_APP_KEY')
        dog.swallow = False

    def test_tags(self):
        # post a metric to make sure the test host context exists
        hostname = 'test.tag.host'
        dog.metric('test.tag.metric', 1, host=hostname)

        dog.all_tags()

        dog.detach_tags(hostname)
        assert len(dog.host_tags(hostname)) == 0

        dog.add_tags(hostname, 'test.tag.1', 'test.tag.2')
        new_tags = dog.host_tags(hostname)
        assert len(new_tags) == 2
        assert 'test.tag.1' in new_tags
        assert 'test.tag.2' in new_tags

        dog.add_tags(hostname, 'test.tag.3')
        new_tags = dog.host_tags(hostname)
        assert len(new_tags) == 3
        assert 'test.tag.1' in new_tags
        assert 'test.tag.2' in new_tags
        assert 'test.tag.3' in new_tags

        dog.change_tags(hostname, 'test.tag.4')
        new_tags = dog.host_tags(hostname)
        assert len(new_tags) == 1
        assert 'test.tag.4' in new_tags

        dog.detach_tags(hostname)
        assert len(dog.host_tags(hostname)) == 0

    def test_events(self):
        now = datetime.datetime.now()

        now_ts = int(time.mktime(now.timetuple()))
        now_title = 'end test title ' + str(now_ts)
        now_message = 'test message ' + str(now_ts)

        before_ts = int(time.mktime((now - datetime.timedelta(minutes=5)).timetuple()))
        before_title = 'start test title ' + str(before_ts)
        before_message = 'test message ' + str(before_ts)

        now_event_id = dog.event(now_title, now_message, now_ts)
        before_event_id = dog.event(before_title, before_message, before_ts)

        stream = dog.stream(before_ts, now_ts + 2)

        assert stream[-1]['title'] == before_title
        assert stream[0]['title'] == now_title

        now_event = dog.get_event(now_event_id)
        before_event = dog.get_event(before_event_id)

        assert now_event['text'] == now_message
        assert before_event['text'] == before_message

        event_id = dog.event('test host and device', 'test host and device', host='test.host', device_name='test.device')
        event = dog.get_event(event_id)

        assert event['host'] == 'test.host'
        assert event['device_name'] == 'test.device'

        event_id = dog.event('test event tags', 'test event tags', tags=['test-tag-1','test-tag-2'])
        event = dog.get_event(event_id)

        assert 'test-tag-1' in event['tags']
        assert 'test-tag-2' in event['tags']

    def test_comments(self):
        now = datetime.datetime.now()
        now_ts = int(time.mktime(now.timetuple()))
        before_ts = int(time.mktime((now - datetime.timedelta(minutes=5)).timetuple()))
        message = 'test message ' + str(now_ts)

        comment_id = dog.comment('fabian', message)
        event = dog.get_event(comment_id)
        assert event['text'] == message

        dog.comment('fabian', message + ' updated', comment_id)
        event = dog.get_event(comment_id)
        assert event['text'] == message + ' updated'

        reply_id = dog.comment('fabian', message + ' reply', related_event_id=comment_id)
        stream = dog.stream(before_ts, now_ts + 2)

        assert reply_id in [x['id'] for x in stream[0]['comments']]

        dog.delete_comment(comment_id)
        dog.delete_comment(reply_id)
        try:
            dog.get_event(comment_id)
        except:
            pass
        else:
            assert False


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

        dash_id = dog.update_dashboard(dash_id, 'updated api dash', 'my api dash', [graph])
        remote_dash = dog.dashboard(dash_id)

        assert 'updated api dash' == remote_dash['title']

        p = graph['definition']['requests']
        assert graph['definition']['requests'] == remote_dash['graphs'][0]['definition']['requests']

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
        # FIXME: re-enable when LH #554 is fixed
        #assert len(results['metrics']) > 0

    def test_metrics(self):
        now = datetime.datetime.now()
        now_ts = int(time.mktime(now.timetuple()))

        dog.metric('test.metric.' + str(now_ts), 1, host="test.host." + str(now_ts))
        results = dog.search('hosts:test.host.' + str(now_ts))
        assert len(results['hosts']) == 1
        # FIXME: re-enable when LH #554 is fixed
        #results = dog.search('metrics:test.metric.' + str(now_ts))
        #assert len(results['metrics']) == 1

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

        dog.metrics('matt.metric', matt_series, host="matt.metric.host")

    def test_swallow_exceptions(self):
        comment_id = dog.comment('fabian', 'test exception swallowing')
        dog.delete_comment(comment_id)

        # doesn't raise an exception when swallow is True
        dog.swallow = True
        dog.get_event(comment_id)

        # raises an exception when swallow is False
        dog.swallow = False
        try:
            dog.get_event(comment_id)
        except:
            pass
        else:
            assert False


    def test_type_check(self):
        try:
            dog.metric("test.metric", [(time.time() - 3600, 1.0)])
            self.fail()
        except Exception, e:
            assert e.message == ".metric takes a scalar value not a <type 'list'>. You might want to use .metrics instead", e.message
        try:
            dog.metrics("test.metric", 1.0)
            self.fail()
        except Exception, e:
            assert e.message == ".metrics takes a list of pairs not a <type 'float'>. You might want to use .metric instead to send a scalar value", e.message

if __name__ == '__main__':
    unittest.main()
