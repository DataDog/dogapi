__all__ = [
    'ScreenboardApi',
]

class ScreenboardApi(object):

    def create_screenboard(self, description):
        """
        Create a new Screenboard.

        See the `screenboard API documentation <http://docs.datadoghq.com/api/screenboard>`_
        for the Screenboard `description` format.
        """
        return self.http_request('POST', '/screen', description)

    def get_screenboard(self, board_id):
        """
        Get the Screenboard with the given id.

        See the `screenboard API documentation <http://docs.datadoghq.com/api/screenboard>`_
        for the Screenboard `description` format.
        """
        return self.http_request('GET', '/screen/' + str(board_id))

    def update_screenboard(self, board_id, description):
        """
        Update the Screenboard with the given id.

        See the `screenboard API documentation <http://docs.datadoghq.com/api/screenboard>`_
        for the Screenboard `description` format.
        """
        return self.http_request('PUT', '/screen/' + str(board_id), description)

    def delete_screenboard(self, board_id):
        """
        Delete the Screenboard with the given id.
        """
        return self.http_request('DELETE', '/screen/' + str(board_id))

    def share_screenboard(self, board_id):
        """
        Share the screenboard with given id. Returns the structure:

        >>> dog_http_api.share_screenboard(1234)
        {
            "board_id": 1234,
            "public_url": "https://p.datadoghq.com/sb/48f234f"
        }
        """
        return self.http_request('GET', '/screen/share/' + str(board_id))


