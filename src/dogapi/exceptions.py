""" Module containing all the possible exceptions that dogapi can raise.
	It should be safe to do a `from dogapi.exceptions import *`
"""

import socket
import ssl

__all__ = [
	'DatadogException',
	'UnknownDelivery',
	'ClientError',
	'HttpTimeout',
	'HttpBackoff',
	'timeout_exceptions',
]

class DatadogException(Exception): pass
class UnknownDelivery(DatadogException): pass

class ClientError(DatadogException): pass
class HttpTimeout(DatadogException): pass
class HttpBackoff(DatadogException): pass
timeout_exceptions = (socket.timeout, ssl.SSLError)

