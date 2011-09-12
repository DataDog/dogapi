from v1.comment import CommentService

class SimpleClient(object):

    def __init__(self):
        self.api_key = None
        self.application_key = None
        self.datadog_host = 'https://app.datadoghq.com'

    def metric(self, name, value):
        pass

    #
    # Comment API

    def comment(self, handle, message, comment_id=None, related_event_id=None):
        if self.api_key is None or self.application_key is None:
            raise Exception("Comment API requires api and application keys")
        s = CommentService(self.api_key, self.application_key, self.datadog_host)
        if comment_id is None:
            return s.post(handle, message, related_event_id)
        else:
            return s.edit(comment_id, handle, message, related_event_id)

    def delete_comment(self, comment_id):
        if self.api_key is None or self.application_key is None:
            raise Exception("Comment API requires api and application keys")
        s = CommentService(self.api_key, self.application_key, self.datadog_host)
        return s.delete(comment_id)
