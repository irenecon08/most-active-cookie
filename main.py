"""Find the most active cookie(s) for a given UTC date in a cookie log file.

Usage:
    python main.py -f <path-to-log.csv> -d <YYYY-MM-DD>
"""

import argparse
import csv
import datetime as dt
import sys


def main(argv=None):
    """Run the command-line program: read the log and print the most active cookie(s)."""

    parser = argparse.ArgumentParser(
        description="Find the most active cookie(s) for a given UTC date."
    )
    parser.add_argument("-f", "--filename", required=True,
                        help="path to the cookie log CSV file")
    parser.add_argument("-d", "--date", required=True,
                        help="UTC date in 'YYYY-MM-DD' format")
    
    args = parser.parse_args(argv)

    try: 
        target_date = dt.date.fromisoformat(args.date)
    except ValueError:
        print(f"Error: Invalid date '{args.date}', expected 'YYYY-MM-DD' format. For example, '2019-06-18'", file=sys.stderr)
        sys.exit(1)

    try: 
        records = read_cookie_records(args.filename)
    except FileNotFoundError: 
        print(f"Error: File not found: '{args.filename}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    most_active_cookies = find_most_active_cookies(records, target_date)

    for cookie in most_active_cookies:
        print(cookie)


def read_cookie_records(file_path):
    """Read the cookie log and return a list of cookie, UTC date pairs."""

    records = []
    
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("File is empty: no header row found.")

        elif ('cookie' not in reader.fieldnames 
                or 'timestamp' not in reader.fieldnames):
            raise ValueError(f"Unexpected header: {reader.fieldnames}, expected 'cookie,timestamp'")
        
        for row in reader:
            cookie = row['cookie']
            timestamp = row['timestamp']

            if not cookie or not timestamp:
                print(f"Warning: Skipping line {reader.line_num}: Missing cookie or timestamp.",
                      file=sys.stderr)
                
                continue

            try: 
                datetime_cookie = dt.datetime.fromisoformat(timestamp) 
            except ValueError:
                print(f"Warning: Skipping line {reader.line_num}: Invalid timestamp, '{timestamp}'.",
                      file=sys.stderr)
                continue
            
            if datetime_cookie.tzinfo is None:
                print(f"Warning: Skipping line {reader.line_num}: Timestamp has no offset, '{timestamp}'.",
                      file=sys.stderr)
                continue

            # Convert to UTC so dates match the -d argument, which is a UTC date.
            datetime_cookie_utc = datetime_cookie.astimezone(dt.timezone.utc) 
            date_cookie = datetime_cookie_utc.date() 

            records.append((cookie, date_cookie))

    return records
    

def find_most_active_cookies(records, target_date):
    """Return the cookie(s) seen most often on the target date (empty list if none)."""

    cookie_counts = {}

    for cookie, record_date in records:
        if record_date == target_date:
            if cookie in cookie_counts:
                cookie_counts[cookie] += 1
            else:
                cookie_counts[cookie] = 1
    
    most_active_cookies = []

    if len(cookie_counts) != 0: 
        max_count = max(cookie_counts.values())

        for cookie, count in cookie_counts.items():
            if count == max_count:
                most_active_cookies.append(cookie) 

    return most_active_cookies


if __name__ == "__main__":
    main()

