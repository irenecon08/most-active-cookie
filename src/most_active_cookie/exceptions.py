class CookieLogError(Exception):
    """Base class for problems with the cookie log file."""


class EmptyLogError(CookieLogError):
    """Raised when the log file has no header row."""


class InvalidHeaderError(CookieLogError):
    """Raised when the header is not 'cookie,timestamp'."""
