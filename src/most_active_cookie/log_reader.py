from __future__ import annotations

import csv
import datetime as dt
import logging
from pathlib import Path

from most_active_cookie.exceptions import EmptyLogError, InvalidHeaderError
from most_active_cookie.models import CookieRecord

logger = logging.getLogger(__name__)


def read_cookie_records(file_path: str | Path) -> list[CookieRecord]:
    """Read the cookie log and return one CookieRecord per valid row, logging a warning for each skipped row."""

    records: list[CookieRecord] = []

    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise EmptyLogError("File is empty: no header row found.")

        elif "cookie" not in reader.fieldnames or "timestamp" not in reader.fieldnames:
            raise InvalidHeaderError(
                f"Unexpected header: {reader.fieldnames}, expected 'cookie,timestamp'"
            )

        for row in reader:
            cookie = row["cookie"]
            timestamp = row["timestamp"]

            if not cookie or not timestamp:
                logger.warning(
                    "Skipping line %d: Missing cookie or timestamp.", reader.line_num
                )
                continue

            try:
                datetime_cookie = dt.datetime.fromisoformat(timestamp)
            except ValueError:
                logger.warning(
                    "Skipping line %d: Invalid timestamp, %r.",
                    reader.line_num,
                    timestamp,
                )
                continue

            if datetime_cookie.tzinfo is None:
                logger.warning(
                    "Skipping line %d: Timestamp has no offset, %r.",
                    reader.line_num,
                    timestamp,
                )
                continue

            # Convert to UTC so dates match the -d argument, which is a UTC date.
            datetime_cookie_utc = datetime_cookie.astimezone(dt.timezone.utc)
            date_cookie = datetime_cookie_utc.date()

            records.append(CookieRecord(cookie=cookie, date=date_cookie))

    return records
