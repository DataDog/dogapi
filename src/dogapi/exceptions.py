""" Module containing all the possible exceptions that dogapi can raise.
	It should be safe to do a `from dogapi.exceptions import *`
"""

import socket

__all__ = [
	'DatadogException',
	'UnknownDelivery',
	'ClientError',
	'HttpTimeout',
	'HttpBackoff',
	'ApiError',
	'timeout_exceptions',
]

class DatadogException(Exception): pass
class UnknownDelivery(DatadogException): pass

class ClientError(DatadogException): pass
class HttpTimeout(DatadogException): pass
class HttpBackoff(DatadogException): pass
class ApiError(DatadogException): pass
timeout_exceptions = (socket.timeout, )

try:
	import ssl
	timeout_exceptions += (ssl.SSLError, )
except ImportError:
	pass
