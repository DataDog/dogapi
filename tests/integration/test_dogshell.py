import json
import os
import random
import re
import subprocess
import time
import tempfile
import unittest
from contextlib import contextmanager 
from configparser import ConfigParser
from hashlib import md5

class TestDogshell(unittest.TestCase):

	# Test init
	def setUp(self):
		# Generate a config file for the dog shell
		self.config_file = tempfile.NamedTemporaryFile()
		config = ConfigParser()
		config.add_section('Connection')
		config.set('Connection', 'apikey', os.environ['DATADOG_API_KEY'])
		config.set('Connection', 'appkey', os.environ['DATADOG_APP_KEY'])
		config.write(self.config_file)
		self.config_file.flush()

	# Tests

	def test_comment(self):
		# Post a new comment
		cmd = ["comment", "post"]
		comment_msg = "yo dudes"
		post_data = {}
		out, err, return_code = self.dogshell(cmd, stdin=comment_msg)
		post_data = self.parse_response(out)
		assert 'id' in post_data, post_data
		assert 'url' in post_data, post_data
		assert 'message' in post_data, post_data
		assert comment_msg in post_data['message']

		# Read that comment from its id
		cmd = ["comment", "show", post_data['id']]
		out, err, return_code = self.dogshell(cmd)
		show_data = self.parse_response(out)
		assert comment_msg in show_data['message']

		# Update the comment
		cmd = ["comment", "update", post_data['id']]
		new_comment = "nothing much"
		out, err, return_code = self.dogshell(cmd, stdin=new_comment)
		update_data = self.parse_response(out)
		self.assertEquals(update_data['id'], post_data['id'])
		assert new_comment in update_data['message']

		# Read the updated comment
		cmd = ["comment", "show", post_data['id']]
		out, err, return_code = self.dogshell(cmd)
		show_data2 = self.parse_response(out)
		assert new_comment in show_data2['message']

		# Delete the comment
		cmd = ["comment", "delete", post_data['id']]
		out, err, return_code = self.dogshell(cmd)
		self.assertEquals(out, '')

		# Shouldn't get anything
		cmd = ["comment", "show", post_data['id']]
		out, err, return_code = self.dogshell(cmd, check_return_code=False)
		self.assertEquals(out, '')
		self.assertEquals(return_code, 1)

	def test_event(self):
		# Post an event
		title =" Testing events from dogshell"
		body = "%%%\n*Cool!*\n%%%\n"""
		tags = "tag:a,tag:b"
		cmd = ["event", "post", title, "--tags", tags]
		event_id = None

		def match_permalink(out):
			match = re.match(r'.*/event/jump_to\?event_id=([0-9]*)', out, re.DOTALL)
			if match:
				return match.group(1)
			else:
				return None

		out, err, return_code = self.dogshell(cmd, stdin=body)
		event_id = match_permalink(out)
		assert event_id, out

		# Retrieve the event
		cmd = ["event", "show", event_id]
		out, err, return_code = self.dogshell(cmd)
		event_id2 = match_permalink(out)
		self.assertEquals(event_id, event_id2)

		# Get a stream of events
		cmd = ["event", "stream", "30m", "--tags", tags]
		out, err, return_code = self.dogshell(cmd)
		event_ids = (match_permalink(l) for l in out.split("\n"))
		event_ids = set([e for e in event_ids if e])
		assert event_id in event_ids

	def test_metrics(self):
		# Submit a unique metric from a unique host
		unique = self.get_unique()
		metric = "test_metric_%s" % unique
		host = "test_host_%s" % unique
		self.dogshell(["metric", "post", "--host", host,  metric, "1"])
		time.sleep(1)

		# Query for the metric, commented out because caching prevents us 
		# from verifying new metrics 
		# out, err, return_code = self.dogshell(["search", "query", 
		# 	"metrics:" + metric])
		# assert metric in out, (metric, out)

		# Query for the host
		out, err, return_code = self.dogshell(["search", "query", 
			"hosts:" + host])
		assert host in out, (host, out)

		# Query for the host and metric
		out, err, return_code = self.dogshell(["search", "query", unique])
		assert host in out, (host, out)
		# Caching prevents us from verifying new metrics 
		# assert metric in out, (metric, out)

		# Give the host some tags
		tags0 = ["t0", "t1"]
		self.dogshell(["tag", "add", host] + tags0)

		# Verify that that host got those tags
		out, err, return_code = self.dogshell(["tag", "show", host])
		for t in tags0:
			assert t in out, (t, out)

		# Replace the tags with a different set
		tags1 = ["t2", "t3"]
		self.dogshell(["tag", "replace", host] + tags1)
		out, err, return_code = self.dogshell(["tag", "show", host])
		for t in tags1:
			assert t in out, (t, out)
		for t in tags0:
			assert t not in out, (t, out)

		# Remove all the tags
		self.dogshell(["tag", "detach", host])
		out, err, return_code = self.dogshell(["tag", "show", host])
		self.assertEquals(out, "")

	def test_dashes(self):
		# Create a dash and write it to a file
		temp0 = tempfile.NamedTemporaryFile()
		self.dogshell(["dashboard", "new_file", temp0.name])
		temp0.seek(0)
		dash = json.load(temp0)
		assert 'id' in dash, dash
		assert 'title' in dash, dash
		assert temp0.name in dash['title']

		# Update the file and push it to the server
		unique = self.get_unique()
		dash['title'] = 'dash title %s' % unique
		temp1 = tempfile.NamedTemporaryFile()
		json.dump(dash, temp1)
		temp1.flush()
		self.dogshell(["dashboard", "push", temp1.name])

		# Query the server to verify the change
		out, _, _ = self.dogshell(["dashboard", "show", str(dash['id'])])

		out = json.loads(out)
		assert "dash" in out, out
		assert "id" in out["dash"], out
		self.assertEquals(out["dash"]["id"], dash["id"])
		assert "title" in out["dash"]
		self.assertEquals(out["dash"]["title"], dash["title"])

		new_title = "new_title"
		new_desc = "new_desc"
		new_dash = [{
					"title": "blerg",
					"definition": {
						"requests": [
							{"q": "avg:system.load.15{web,env:prod}"}
						]
					}
				}]

		# Update a dash directly on the server
		self.dogshell(["dashboard", "update", str(dash["id"]), new_title, new_desc], stdin=json.dumps(new_dash))

		# Query the server to verify the change
		out, _, _ = self.dogshell(["dashboard", "show", str(dash["id"])])
		out = json.loads(out)
		assert "dash" in out, out
		assert "id" in out["dash"], out
		self.assertEquals(out["dash"]["id"], dash["id"])
		assert "title" in out["dash"], out
		self.assertEquals(out["dash"]["title"], new_title)
		assert "description" in out["dash"], out
		self.assertEquals(out["dash"]["description"], new_desc)
		assert "graphs" in out["dash"], out
		self.assertEquals(out["dash"]["graphs"], new_dash)

		# Pull the updated dash to disk
		fd, updated_file = tempfile.mkstemp()
		try:
			self.dogshell(["dashboard", "pull", str(dash["id"]), updated_file])
			updated_dash = {}
			with open(updated_file) as f:
				updated_dash = json.load(f)
			assert "dash" in out
			self.assertEquals(out["dash"], updated_dash)
		finally:
			os.unlink(updated_file)
		
		# Delete the dash 
		self.dogshell(["dashboard", "delete", str(dash["id"])])

		# Verify that it's not on the server anymore
		out, err, return_code = self.dogshell(["dashboard", "show", str(dash['id'])], check_return_code=False)
		self.assertNotEquals(return_code, 0)

	# Test helpers

	def dogshell(self, args, stdin=None, check_return_code=True):
		""" Helper function to call the dog shell command
		"""
		cmd = ["dog", "--config", self.config_file.name] + args
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		try:
			if stdin:
				proc.stdin.write(stdin)
			proc.stdin.close()
			proc.wait()
			out = proc.stdout.read()
			err = proc.stderr.read()
			return_code = proc.returncode
			if check_return_code:
				self.assertEquals(return_code, 0, err)
				self.assertEquals(err, '')
			return out, err, return_code
		finally:
			proc.stdout.close()
			proc.stderr.close()

	def get_unique(self):
		return md5(str(time.time() + random.random())).hexdigest()

	def parse_response(self, out):
		data = {}
		for line in out.split('\n'):
			parts = re.split('\s+', line.strip())
			key = parts[0]
			# Could potentially have errors with other whitespace
			val = " ".join(parts[1:]) 
			if key:
				data[key] = val
		return data

if __name__ == '__main__':
	unittest.main()




