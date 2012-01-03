class BotException(Exception):
    """
    Base Exception that all Bot Exceptions originate from
    """
    pass

class BotConnectionException(BotException):
    """
    Error occurred during connection
    """
    pass

class BotAuthenticationException(BotException):
    """
    Error during authentication
    """
    pass
