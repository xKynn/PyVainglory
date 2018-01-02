class VGRequestException(Exception):
    """
    General purpose exception, base class for other request related exceptions.

    .. _aiohttp.ClientResponse : https://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientResponse

    Parameters
    ----------
    response : aiohttp.ClientResponse_
    data : dict
        The json response from the API
    """
    def __init__(self, response, data):
        self.reason = response.reason
        try:
            self.status = response.status
        except AttributeError:
            self.status = response.status_code
        self.error = data.get("errors")
        if self.error is not None:
            self.error = self.error[0]['title']
        super().__init__("{0.status}: {0.reason} - {0.error}".format(self))


class NotFoundException(VGRequestException):
    """
    For the 404s
    """
    pass


class VGServerException(VGRequestException):
    """
    Exception that signifies that the server failed to respond with valid data.
    """
    pass


class VGFilterException(Exception):
    """
    Raised when an invalid filter value is supplied.
    """
    def __init__(self, error):
        super().__init__(error)


class VGPaginationError(Exception):
    """
    Raised when :meth:`pyvainglory.models.MatchPaginator.next` or :meth:`pyvainglory.models.MatchPaginator.prev`
    are called when the paginator is on the last or first page respectively.
    """
    def __init__(self, error):
        super().__init__(error)


class EmptyResponseException(Exception):
    """
    Raised when any request is 200 OK, but the data is empty.
    """
    def __init__(self, error):
        super().__init__(error)