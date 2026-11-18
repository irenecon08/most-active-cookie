from __future__ import annotations

import argparse
import datetime as dt
import logging
import sys

from most_active_cookie.analyser import find_most_active_cookies
from most_active_cookie.exceptions import CookieLogError
from most_active_cookie.log_reader import read_cookie_records

logger = logging.getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the -f and -d command-line options."""
    parser = argparse.ArgumentParser(
        description="Find the most active cookie(s) for a given UTC date."
    )
    parser.add_argument(
        "-f", "--filename", required=True, help="path to the cookie log CSV file"
    )
    parser.add_argument(
        "-d", "--date", required=True, help="UTC date in 'YYYY-MM-DD' format"
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the command-line program: read the log and print the most active cookie(s)."""

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        target_date = dt.date.fromisoformat(args.date)
    except ValueError:
        logger.error(
            "Invalid date %r, expected 'YYYY-MM-DD' format. For example, '2019-06-18'",
            args.date,
        )
        sys.exit(1)

    try:
        records = read_cookie_records(args.filename)
    except FileNotFoundError:
        logger.error("File not found: %r", args.filename)
        sys.exit(1)

    except CookieLogError as e:
        logger.error("%s", e)
        sys.exit(1)

    most_active_cookies = find_most_active_cookies(records, target_date)

    for cookie in most_active_cookies:
        print(cookie)


if __name__ == "__main__":
    main()
