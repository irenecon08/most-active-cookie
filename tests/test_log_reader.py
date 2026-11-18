import datetime as dt

import pytest

from most_active_cookie.exceptions import EmptyLogError, InvalidHeaderError
from most_active_cookie.log_reader import read_cookie_records
from most_active_cookie.models import CookieRecord


def test_converts_offset_timestamps_to_utc_date(tmp_path):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(
        "cookie,timestamp\nA,2018-12-09T23:30:00-02:00\nB,2018-12-09T00:30:00+01:00\n"
    )

    records = read_cookie_records(log_file)

    assert records == [
        CookieRecord(cookie="A", date=dt.date(2018, 12, 10)),
        CookieRecord(cookie="B", date=dt.date(2018, 12, 8)),
    ]


def test_raises_error_for_empty_file(tmp_path):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text("")

    with pytest.raises(EmptyLogError, match="File is empty"):
        read_cookie_records(log_file)


@pytest.mark.parametrize("header", ["id,time", "cookie,time", "id,timestamp"])
def test_raises_error_for_wrong_header(tmp_path, header):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(header + "\n")

    with pytest.raises(InvalidHeaderError, match="Unexpected header"):
        read_cookie_records(log_file)


def test_header_only_file_returns_no_records(tmp_path, capsys):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text("cookie,timestamp\n")

    records = read_cookie_records(log_file)

    assert records == []

    captured = capsys.readouterr()
    assert captured.err == ""


def test_skips_rows_with_missing_values(tmp_path, capsys):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(
        "cookie,timestamp\n"
        "A,2018-12-09T14:00:00+00:00\n"
        ",2018-12-09T13:00:00+00:00\n"
        "C,\n"
    )

    records = read_cookie_records(log_file)

    assert records == [CookieRecord(cookie="A", date=dt.date(2018, 12, 9))]
    warnings = capsys.readouterr().err
    assert "line 3" in warnings
    assert "line 4" in warnings


def test_skips_rows_with_invalid_timestamps(tmp_path, capsys):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(
        "cookie,timestamp\n"
        "AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00\n"
        "Bad1,not-a-timestamp\n"
        "Bad2,2018-13-09T05:00:00+00:00\n"
        "Bad3,08/12/2018 21:45\n"
    )

    records = read_cookie_records(log_file)

    assert records == [
        CookieRecord(cookie="AtY0laUfhglK3lC7", date=dt.date(2018, 12, 9))
    ]

    warnings = capsys.readouterr().err
    assert "line 3" in warnings
    assert "line 4" in warnings
    assert "line 5" in warnings
    assert "Invalid timestamp" in warnings


def test_skips_rows_with_timestamps_with_no_offsets(tmp_path, capsys):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(
        "cookie,timestamp\n"
        "AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00\n"
        "Bad1,2018-12-08T22:03:00\n"
        "4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00\n"
        "Bad2,2018-12-09T10:13:00\n"
    )

    records = read_cookie_records(log_file)

    assert records == [
        CookieRecord(cookie="AtY0laUfhglK3lC7", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="4sMM2LxV07bPJzwf", date=dt.date(2018, 12, 8)),
    ]

    warnings = capsys.readouterr().err
    assert "line 3" in warnings
    assert "line 5" in warnings
    assert "Timestamp has no offset" in warnings


def test_assigns_day_boundary_timestamps_to_correct_date(tmp_path):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(
        "cookie,timestamp\n"
        "NextDay,2018-12-10T00:00:00+00:00\n"
        "LastSecond,2018-12-09T23:59:59+00:00\n"
        "FirstSecond,2018-12-09T00:00:00+00:00\n"
        "PrevDay,2018-12-08T23:59:59+00:00\n"
    )

    records = read_cookie_records(log_file)

    assert records == [
        CookieRecord(cookie="NextDay", date=dt.date(2018, 12, 10)),
        CookieRecord(cookie="LastSecond", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="FirstSecond", date=dt.date(2018, 12, 9)),
        CookieRecord(cookie="PrevDay", date=dt.date(2018, 12, 8)),
    ]
