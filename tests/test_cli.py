import pytest

from most_active_cookie.cli import main

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


def test_cli_prints_most_active_cookie_for_brief_example(tmp_path, capsys):
    log_file = tmp_path / "cookie_logs.csv"
    log_file.write_text(BRIEF_EXAMPLE_LOG)

    main(["-f", str(log_file), "-d", "2018-12-09"])

    captured = capsys.readouterr()
    assert captured.out == "AtY0laUfhglK3lC7\n"
    assert captured.err == ""


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



