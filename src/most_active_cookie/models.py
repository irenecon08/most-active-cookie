import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class CookieRecord:
    """One cookie occurrence from the log, with its UTC date."""

    cookie: str
    date: dt.date
