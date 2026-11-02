"""Find the most active cookie(s) for a given UTC date in a cookie log file."""

import csv 
import datetime as dt


def main():
    """Run the command-line program: read the log and print the most active cookie(s)."""

    target_date = dt.date.fromisoformat('2018-12-09')
    records = read_cookie_records('cookie_log.csv')
    most_active_cookies = find_most_active_cookies(records, target_date)

    for cookie in most_active_cookies:
        print(cookie)




def read_cookie_records(file_path):
    """Read the cookie log and return a list of cookie, UTC date pairs."""

    records = []

    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cookie = row['cookie']
            timestamp = row['timestamp']

            datetime_cookie = dt.datetime.fromisoformat(timestamp) 
            datetime_cookie_utc = datetime_cookie.astimezone(dt.timezone.utc) # Convert to UTC so dates match the -d argument, which is a UTC date.
            date_cookie = datetime_cookie_utc.date() 

            records.append((cookie, date_cookie))

    return records
    

def find_most_active_cookies(records, target_date):
    """Return the cookie(s) seen most often on the target date (empty list if none)."""

    cookie_counts = {}

    for cookie, record_date in records:
        if record_date == target_date:
            if cookie in cookie_counts:
                cookie_counts[cookie] +=1
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

