class ApiError:
    def __init__(self, error_code, error_message, timestamp):
        self.error_code = error_code
        self.error_message = error_message
        self.timestamp = timestamp
