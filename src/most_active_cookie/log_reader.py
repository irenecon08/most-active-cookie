import csv
import datetime as dt
import sys

from most_active_cookie.exceptions import EmptyLogError, InvalidHeaderError
from most_active_cookie.models import CookieRecord


def read_cookie_records(file_path):
    """Read the cookie log and return CookieRecords."""

    records = []

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
                print(
                    f"Warning: Skipping line {reader.line_num}: Missing cookie or timestamp.",
                    file=sys.stderr,
                )

                continue

            try:
                datetime_cookie = dt.datetime.fromisoformat(timestamp)
            except ValueError:
                print(
                    f"Warning: Skipping line {reader.line_num}: Invalid timestamp, '{timestamp}'.",
                    file=sys.stderr,
                )
                continue

            if datetime_cookie.tzinfo is None:
                print(
                    f"Warning: Skipping line {reader.line_num}: Timestamp has no offset, '{timestamp}'.",
                    file=sys.stderr,
                )
                continue

            # Convert to UTC so dates match the -d argument, which is a UTC date.
            datetime_cookie_utc = datetime_cookie.astimezone(dt.timezone.utc)
            date_cookie = datetime_cookie_utc.date()

            records.append(CookieRecord(cookie=cookie, date=date_cookie))

    return records
