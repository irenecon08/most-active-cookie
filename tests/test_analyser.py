import datetime as dt

from most_active_cookie.analyser import find_most_active_cookies
from most_active_cookie.models import CookieRecord


def test_returns_single_most_active_cookie():
    # Arrange: A appears twice, B once, all on the same day
    records = [
        CookieRecord(cookie="A", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="A", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="B", date=dt.date(2018, 12, 9)),
    ]

    # Act
    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    # Assert
    assert result == ["A"]


def test_returns_all_cookies_if_tied():
    records = [
        CookieRecord(cookie="A", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="A", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="B", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="B", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="C", date=dt.date(2018, 12, 9)),
    ]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert sorted(result) == ["A", "B"]


def test_ignores_records_on_other_dates():
    records = [
        CookieRecord(cookie="X", date=dt.date(2018, 12, 10)),
        CookieRecord(cookie="X", date=dt.date(2018, 12, 10)),
        CookieRecord(cookie="A", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="A", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="B", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="X", date=dt.date(2018, 12, 8)),
        CookieRecord(cookie="X", date=dt.date(2018, 12, 8)),
    ]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert result == ["A"]


def test_returns_empty_list_for_no_records():
    assert find_most_active_cookies([], dt.date(2018, 12, 9)) == []


def test_returns_empty_list_when_no_records_on_target_date():
    records = [CookieRecord(cookie="A", date=dt.date(2018, 12, 8))]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert result == []


def test_returns_cookie_from_single_record():
    records = [CookieRecord(cookie="A", date=dt.date(2018, 12, 9))]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert result == ["A"]
