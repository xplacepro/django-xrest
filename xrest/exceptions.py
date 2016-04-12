
class ResponseException(Exception):
    def __init__(self, error_dict, status):
        self.error_dict = error_dict
        self.status = status
