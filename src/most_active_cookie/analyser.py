def find_most_active_cookies(records, target_date):
    """Return the cookie(s) seen most often on the target date (empty list if none)."""

    cookie_counts = {}

    for record in records:
        if record.date == target_date:
            cookie_counts[record.cookie] = cookie_counts.get(record.cookie, 0) + 1

    most_active_cookies = []

    if len(cookie_counts) != 0:
        max_count = max(cookie_counts.values())

        for cookie, count in cookie_counts.items():
            if count == max_count:
                most_active_cookies.append(cookie)

    return most_active_cookies
