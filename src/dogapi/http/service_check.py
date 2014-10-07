__all__ = [
    'ServiceCheckApi',
]

import logging
from dogapi.constants import CheckStatus
from dogapi.exceptions import ApiError

logger = logging.getLogger('dd.dogapi')


class ServiceCheckApi(object):
    def service_check(self, check, host, timestamp, status, message=None, tags=None):
        if status not in CheckStatus.ALL:
            raise ApiError('Invalid status, expected one of: %s' \
                % ', '.join(CheckStatus.ALL))

        body = {
            'check': check,
            'host': host,
            'timestamp': timestamp,
            'status': status
        }
        if message:
            body['message'] = message
        if tags:
            body['tags'] = tags
        return self.http_request('POST', '/check_run', body)
