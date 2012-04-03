# python
import random, math
import datetime
import unittest
import os

# nose
from nose.plugins.skip import SkipTest

# dogapi
import dogapi
import datetime, time


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

        now_event_id = dog.event_with_response(now_title, now_message, now_ts)
        before_event_id = dog.event_with_response(before_title, before_message, before_ts)

        stream = dog.stream(before_ts, now_ts + 2)

        assert stream[-1]['title'] == before_title
        assert stream[0]['title'] == now_title

        now_event = dog.get_event(now_event_id)
        before_event = dog.get_event(before_event_id)

        assert now_event['text'] == now_message
        assert before_event['text'] == before_message

        event_id = dog.event_with_response('test host and device', 'test host and device', host='test.host', device_name='test.device')
        event = dog.get_event(event_id)

        assert event['host'] == 'test.host'
        assert event['device_name'] == 'test.device'

        event_id = dog.event_with_response('test event tags', 'test event tags', tags=['test-tag-1','test-tag-2'])
        event = dog.get_event(event_id)

        assert 'test-tag-1' in event['tags']
        assert 'test-tag-2' in event['tags']

    def test_git_commits(self):
        """Pretend to send git commits"""
        event_id = dog.event_with_response("Testing git commits", """$$$
eac54655 *   Merge pull request #2 from DataDog/alq-add-arg-validation (alq@datadoghq.com)
         |\
760735ef | * origin/alq-add-arg-validation Simple typechecking between metric and metrics (matt@datadoghq.com)
         |/
f7a5a23d * missed version number in docs (matt@datadoghq.com)
$$$""", event_type="commit", source_type_name="git", event_object="0xdeadbeef")


        event = dog.get_event(event_id)

        assert event.get("title", "") == "Testing git commits", event

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
        stream = dog.stream(before_ts, now_ts + 10)

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


if __name__ == '__main__':
    unittest.main()
