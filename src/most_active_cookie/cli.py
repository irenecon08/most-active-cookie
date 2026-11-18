import argparse
import datetime as dt
import sys

from most_active_cookie.analyser import find_most_active_cookies
from most_active_cookie.exceptions import CookieLogError
from most_active_cookie.log_reader import read_cookie_records


def build_arg_parser():
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


def main(argv=None):
    """Run the command-line program: read the log and print the most active cookie(s)."""

    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        target_date = dt.date.fromisoformat(args.date)
    except ValueError:
        print(
            f"Error: Invalid date '{args.date}', expected 'YYYY-MM-DD' format. For example, '2019-06-18'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        records = read_cookie_records(args.filename)
    except FileNotFoundError:
        print(f"Error: File not found: '{args.filename}'", file=sys.stderr)
        sys.exit(1)
    except CookieLogError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    most_active_cookies = find_most_active_cookies(records, target_date)

    for cookie in most_active_cookies:
        print(cookie)


if __name__ == "__main__":
    main()
