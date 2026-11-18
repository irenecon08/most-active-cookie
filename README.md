# Most Active Cookie

A command-line program that reads a cookie log (CSV) and prints the most active cookie(s) for a given UTC date, i.e. the cookie(s) seen most often on that day.

## Requirements

- Python 3.9 or later
- No third-party libraries are needed to run the program (only the standard library).
  `pytest`, `ruff` and `mypy` are used for development.

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

## Development

```
pytest              # run the tests
ruff check .        # lint, including import order
ruff format .       # format the code
mypy                # type-check src/ in strict mode
```

The tests cover the example from the brief, edge cases (ties, no matching cookies, empty and header-only files, day boundaries, time-zone offsets) and error handling (malformed rows, wrong header, invalid date, missing file, missing options).

## Project structure

```
src/most_active_cookie/
├── cli.py          # command-line interface: parses -f/-d, reports errors, prints results
├── log_reader.py   # reads and validates the CSV log, returns CookieRecords
├── analyser.py     # finds the most active cookie(s) for a date
├── models.py       # CookieRecord data class shared by the reader and analyser
└── exceptions.py   # custom exceptions for invalid log files
tests/
├── test_cli.py
├── test_log_reader.py
└── test_analyser.py
```

## Design

The program is split into modules by responsibility, so each part can be understood, tested and changed on its own:

- **`log_reader.py`** turns the CSV file into a list of `CookieRecord`s (cookie and UTC date). It validates the header and each row, skipping malformed rows with a logged warning. It only reports problems (by raising exceptions or logging warnings) and never decides how they are shown to the user.
- **`analyser.py`** contains the core logic: counting how often each cookie appears on the target date and returning every cookie with the highest count. It has no knowledge of files or the command line, so it works on records from any source.
- **`cli.py`** is the only module that deals with the user: it parses the arguments, configures logging, turns errors into messages and exit codes, and prints the result.
- **`models.py`** holds `CookieRecord`, a frozen data class that replaces bare `(cookie, date)` tuples. Named, typed fields make the data's meaning explicit. It lives in its own module because both the reader and the analyser use it, so neither depends on the other.
- **`exceptions.py`** defines `CookieLogError` and its subclasses `EmptyLogError` and `InvalidHeaderError`. The CLI catches only `CookieLogError`, so expected problems with the input produce a clear message, while unexpected errors (bugs) are not hidden and surface with a full traceback.

Each test file covers one module.

## Assumptions and decisions

- The `-d` date is interpreted as a UTC calendar day.
- Log timestamps may have any UTC offset, so they are converted to UTC before comparing dates.
- Malformed rows (missing value, invalid timestamp, or timestamp with no UTC offset, since its time zone is ambiguous) are skipped with a warning that includes the line number. Log files are machine-generated and can contain the occasional corrupt line, so a single bad row does not fail the whole run. If strict validation were needed, raising an exception on the first malformed row would be a simple change.
- A file with only a header returns no output, since it is a valid cookie log with no data. A completely empty file or a wrong header is reported as an error, since the file cannot be confirmed to be a cookie log.
- Tied cookies are printed in the order they first appear in the file.
- Results are printed to stdout. Warnings and errors go through Python's `logging` module, configured in `cli.py` to write to stderr in the form `WARNING: ...` / `ERROR: ...`.
- Exit codes: 0 on success (including when no cookies match the date), 1 for an invalid date, missing file or invalid file, 2 for missing or invalid command-line options.
- Counting is implemented directly rather than with `collections.Counter`, as the brief asks for the core logic to be written without helper libraries.
- Timestamps must include an explicit offset such as `+00:00`. The `Z` suffix is only supported on Python 3.11+.
- `CookieRecord` is created with keyword arguments throughout. `kw_only=True` would enforce this, but requires Python 3.10+, and the project supports 3.9.
