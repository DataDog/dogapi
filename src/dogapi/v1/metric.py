"""
Full client-side comment client
See facade.py for a simpler wrapper
"""
import logging
import simplejson

from dogapi.common import APIService

API_VERSION="v1"

class MetricService(APIService):
    """
    Low level wrapper for dealing directly with the metrics API.

    :param api_key: your org's API key
    :type api_key: string

    :param application_key: your application key
    :type application_key: string
    """

    def post(self, name, points, mtype="gauge", host=None, device=None):
        """
        Submit a series of data points.

        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param points: data series. list of (POSIX timestamp, intever value) tuples. (e.g. ``[(1317652676, 15), (1317652706, 18), ...]``)
        :type points: list

        :param mtype: metric type. for now, only ``"gauge"`` is accepted
        :type mtype: string

        :param host: optional host to scope the metric (e.g. ``"hostA.example.com"``)
        :type host: string
        
        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :returns: empty dict on success. errors and warnings are reported as for the HTTP API (see the `HTTP API Documentation <https://github.com/DataDog/dogapi/wiki/Errors-and-Warnings>`_)
        :rtype: dict
        """

        params = {
            'api_key':         self.api_key,
            'application_key': self.application_key,
        }

        body = { "series": [
            {
            'metric': name,
            'points': [[int(x[0]), int(x[1])] for x in points],
            'type': mtype,
            'host': host,
            'device': device,
            }
            ]
        }

        return self.request('POST', '/api/' + API_VERSION + '/series', params, body, send_json=True)
