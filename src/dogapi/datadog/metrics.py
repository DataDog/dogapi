import time, datetime

class MetricApi(object):
    def metric(self, name, points, host=None, device=None):
        """
        Submit a series of data points to the metric API.

        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param values: data series. list of (POSIX timestamp, intever value) tuples. (e.g. ``[(1317652676, 15), (1317652706, 18), ...]``)
        :type values: list

        :param host: optional host to scope the metric (e.g.
        ``"hostA.example.com"``). defaults to local hostname. to submit without
        a host, explicitly set host=None.
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if host is None:
            host = self._default_host
        
        now = time.mktime(datetime.datetime.now().timetuple())
        if isinstance(points, (float, int)):
            points = [(now, points)]
        elif isinstance(points, tuple):
            points = [points]
        
        body = { "series": [
            {
            'metric': name,
            'points': [[x[0], x[1]] for x in points],
            'type': "gauge",
            'host': host,
            'device': device,
            }
            ]
        }
        
        return self.request('POST', '/series', body)

    def batch_metrics(self, values, host=None, device=None):
        """
        Submit a series of metrics with 1 or more data points to the metric API

        :param values A dictionary of names to a list values, in the form of {name: [(POSIX timestamp, integer value), ...], name2: [(POSIX timestamp, integer value), ...]}
        :type values: dict

        :param host: optional host to scope the metric (e.g.
        ``"hostA.example.com"``). to submit without a host, explicitly set
        host=None.
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """        
        mtype = "gauge" # FIXME: expose to client
        body = { "series": [
            {
            'metric': name,
            'points': [[x[0], x[1]] for x in points],
            'type': mtype,
            'host': host,
            'device': device,
            } for name, points in values.items()
            ]
        }
        
        return self.request('POST', '/series', body)
        
 