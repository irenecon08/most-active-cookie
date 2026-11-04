# Most Active Cookie

A command-line program that reads a cookie log (CSV) and prints the most active cookie(s) for a given UTC date, i.e. the cookie(s) seen most often on that day.

## Requirements

- Python 3.9 or later
- No third-party libraries are needed to run the program (only the standard library).
  `pytest` and `ruff` are used for development.

## Installation

```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

## Usage

```
most-active-cookie -f <path-to-log.csv> -d <YYYY-MM-DD>
```

Example:

```
$ most-active-cookie -f cookie_log.csv -d 2018-12-09
AtY0laUfhglK3lC7
```

If several cookies are tied, each is printed on its own line.

## Running the tests

```
pytest
```

The tests cover the example from the brief, edge cases (ties, no matching cookies, empty and header-only files, day boundaries, time-zone offsets) and error handling (malformed rows, wrong header, invalid date, missing file, missing options).

## Design

The program is split into three functions:

- `read_cookie_records`: reads and validates the log file and returns a list of (cookie, UTC date) records. It skips malformed rows and raises a `ValueError` if the file is empty or the header is wrong.
- `find_most_active_cookies`: counts how often each cookie appears on the target date and returns every cookie with the highest count (an empty list if none).
- `main`: handles the command line: it parses `-f` and `-d`, calls the two functions above, prints the results, and turns errors into clear messages and exit codes.

The split follows the program's two core tasks, reading the log and finding the most active cookie(s), with `main` handling everything to do with the command line. This also means each task can be tested separately.

## Assumptions and decisions

- The `-d` date is interpreted as a UTC calendar day.
- Log timestamps may have any UTC offset, therefore they are converted to UTC before comparing dates.
- Malformed rows (missing value, invalid timestamp, or timestamp with no UTC offset, since its time zone is ambiguous) are skipped with a warning on stderr that includes the line number. Log files are machine-generated and can contain the occasional corrupt line, so a single bad row does not fail the whole run. The warnings make every skipped line visible. If strict validation were needed, failing on the first malformed row would be a simple change.
- A file with only a header returns no output, since it is a valid cookie log with no data. A completely empty file or a wrong header is reported as an error, since the file cannot be confirmed to be a cookie log.
- Tied cookies are printed in the order they first appear in the file.
- Results go to stdout, and warnings and errors go to stderr.
- Exit codes: 0 on success (including when no cookies match the date), 1 for an invalid date, missing file or invalid file, 2 for missing or invalid command-line options.
- Timestamps must include an explicit offset such as `+00:00`. The `Z` suffix is only supported on Python 3.11+.