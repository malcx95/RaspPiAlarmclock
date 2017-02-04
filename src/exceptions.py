# I will probably use these sometime, deal with it.


class InvalidMenuException(Exception):
    def __init__(self, message):
        super(InvalidMenuException, self).__init__(message)


class InvalidMenuOptionsException(InvalidMenuException):
    def __init__(self, message, options):
        super(InvalidMenuOptionsException, self).__init__(message)
        self.options = options
