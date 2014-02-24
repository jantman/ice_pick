class APIRequestException(Exception):
    def __init__(self, request_method, request_url, status_code):
        self.request_method = request_method
        self.request_url = request_url
        self.status_code = status_code

    def str(self):
        return '%s request to %s returned status %d' % (self.request_method,
                                                        self.request_url,
                                                        self.status_code)
