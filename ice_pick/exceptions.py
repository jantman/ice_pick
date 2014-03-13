class APIRequestException(Exception):
    def __init__(self, request_method, request_url, status_code):
        msg = '%s request to %s returned status %d' % (request_method,
                                                       request_url,
                                                       status_code)
        super(Exception, self).__init__(msg)
