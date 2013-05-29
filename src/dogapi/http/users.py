__all__ = [
    'UserApi',
]

class UserApi(object):

    def invite(self, emails):
        """
        Send an invite to join datadog to each of the email addresses in the
        *emails* list. If *emails* is a string, it will be wrapped in a list and
        sent. Returns a list of email addresses for which an email was sent.

        >>> dog_http_api.invite(["user1@mydomain.com", "user2@mydomain.com"])
        """
        if not isinstance(emails, list):
            emails = [emails]

        body = {
            'emails':  emails,
        }

        return self.http_request('POST', '/invite_users', body,
            response_formatter=lambda x: x['emails'],
        )
