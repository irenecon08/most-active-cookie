import datetime as dt

import pytest

from most_active_cookie.main import find_most_active_cookies, main, read_cookie_records

BRIEF_EXAMPLE_LOG = (
    "cookie,timestamp\n"
    "AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00\n"
    "SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00\n"
    "5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00\n"
    "AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00\n"
    "SAZuXPGUrfbcn5UA,2018-12-08T22:03:00+00:00\n"
    "4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00\n"
    "fbcn5UAVanZf6UtG,2018-12-08T09:30:00+00:00\n"
    "4sMM2LxV07bPJzwf,2018-12-07T23:30:00+00:00\n"
)


def test_returns_single_most_active_cookie():
    # Arrange: A appears twice, B once, all on the same day
    records = [
        ("A", dt.date(2018, 12, 9)),
        ("A", dt.date(2018, 12, 9)),
        ("B", dt.date(2018, 12, 9)),
    ]

    # Act
    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    # Assert
    assert result == ["A"]


def test_returns_all_cookies_if_tied():
    records = [
        ("A", dt.date(2018, 12, 9)),
        ("A", dt.date(2018, 12, 9)),
        ("B", dt.date(2018, 12, 9)),
        ("B", dt.date(2018, 12, 9)),
        ("C", dt.date(2018, 12, 9)),
    ]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert sorted(result) == ["A", "B"]


def test_converts_offset_timestamps_to_utc_date(tmp_path):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(
        "cookie,timestamp\nA,2018-12-09T23:30:00-02:00\nB,2018-12-09T00:30:00+01:00\n"
    )

    records = read_cookie_records(log_file)

    assert records == [
        ("A", dt.date(2018, 12, 10)),
        ("B", dt.date(2018, 12, 8)),
    ]


def test_cli_prints_most_active_cookie_for_brief_example(tmp_path, capsys):
    log_file = tmp_path / "cookie_logs.csv"
    log_file.write_text(BRIEF_EXAMPLE_LOG)

    main(["-f", str(log_file), "-d", "2018-12-09"])

    captured = capsys.readouterr()
    assert captured.out == "AtY0laUfhglK3lC7\n"
    assert captured.err == ""


def test_raises_error_for_empty_file(tmp_path):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text("")

    with pytest.raises(ValueError, match="File is empty"):
        read_cookie_records(log_file)


@pytest.mark.parametrize("header", ["id,time", "cookie,time", "id,timestamp"])
def test_raises_error_for_wrong_header(tmp_path, header):
    log_file = tmp_path / "cookie_log.csv"
    log_file.write_text(header + "\n")

    with pytest.raises(ValueError, match="Unexpected header"):
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

    assert records == [("A", dt.date(2018, 12, 9))]
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

    assert records == [("AtY0laUfhglK3lC7", dt.date(2018, 12, 9))]

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
        ("AtY0laUfhglK3lC7", dt.date(2018, 12, 9)),
        ("4sMM2LxV07bPJzwf", dt.date(2018, 12, 8)),
    ]

    warnings = capsys.readouterr().err
    assert "line 3" in warnings
    assert "line 5" in warnings
    assert "Timestamp has no offset" in warnings


def test_cli_exits_with_error_for_invalid_date(tmp_path, capsys):
    log_file = tmp_path / "cookie_logs.csv"
    log_file.write_text(BRIEF_EXAMPLE_LOG)

    with pytest.raises(SystemExit) as exit_info:
        main(["-f", str(log_file), "-d", "09-12-2018"])

    assert exit_info.value.code == 1
    assert "Invalid date" in capsys.readouterr().err


def test_cli_exits_with_error_for_missing_file(tmp_path, capsys):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(SystemExit) as exit_info:
        main(["-f", str(missing_file), "-d", "2018-12-08"])

    assert exit_info.value.code == 1
    assert "File not found" in capsys.readouterr().err


@pytest.mark.parametrize(
    "arguments, missing_option",
    [
        (["-d", "2018-12-09"], "-f"),
        (["-f", "cookie_log.csv"], "-d"),
    ],
)
def test_cli_exits_with_usage_error_when_option_missing(
    capsys, arguments, missing_option
):
    with pytest.raises(SystemExit) as exit_info:
        main(arguments)

    assert exit_info.value.code == 2
    stderr = capsys.readouterr().err
    assert "required" in stderr
    assert missing_option in stderr


def test_ignores_records_on_other_dates():
    records = [
        ("X", dt.date(2018, 12, 10)),
        ("X", dt.date(2018, 12, 10)),
        ("A", dt.date(2018, 12, 9)),
        ("A", dt.date(2018, 12, 9)),
        ("B", dt.date(2018, 12, 9)),
        ("X", dt.date(2018, 12, 8)),
        ("X", dt.date(2018, 12, 8)),
    ]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert result == ["A"]


def test_returns_empty_list_for_no_records():
    assert find_most_active_cookies([], dt.date(2018, 12, 9)) == []


def test_returns_empty_list_when_no_records_on_target_date():
    records = [("A", dt.date(2018, 12, 8))]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert result == []


def test_returns_cookie_from_single_record():
    records = [("A", dt.date(2018, 12, 9))]

    result = find_most_active_cookies(records, dt.date(2018, 12, 9))

    assert result == ["A"]


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
        ("NextDay", dt.date(2018, 12, 10)),
        ("LastSecond", dt.date(2018, 12, 9)),
        ("FirstSecond", dt.date(2018, 12, 9)),
        ("PrevDay", dt.date(2018, 12, 8)),
    ]
