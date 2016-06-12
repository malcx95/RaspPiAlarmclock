# I will probably use these sometime, deal with it.

class InvalidMenuException(Exception):
    def __init__(self, message):
        super(self, message)

class InvalidMenuOptionsException(InvalidMenuException):
    def __init__(self, message, options):
        self.options = options
        super(self, message)


