"""Utility functions for CSE trading calendar.

Provides:
- is_trading_day(date: datetime.date) -> bool
- next_trading_day(date: datetime.date) -> datetime.date
- add_trading_days(start: datetime.date, n: int) -> datetime.date

Future extensions can load holiday data from a CSV or an API.
"""
import datetime

# Placeholder set of holidays (datetime.date objects). Extend as needed.
HOLIDAYS = set()


def is_trading_day(date: datetime.date) -> bool:
    """Return True if the given date is a CSE trading day.

    Excludes Saturdays, Sundays, and any date present in ``HOLIDAYS``.
    """
    if date.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    if date in HOLIDAYS:
        return False
    return True


def next_trading_day(date: datetime.date) -> datetime.date:
    """Return the next calendar day that is a trading day."""
    next_day = date + datetime.timedelta(days=1)
    while not is_trading_day(next_day):
        next_day += datetime.timedelta(days=1)
    return next_day


def add_trading_days(start: datetime.date, n: int) -> datetime.date:
    """Add ``n`` trading days to ``start`` and return the resulting date."""
    current = start
    added = 0
    while added < n:
        current = next_trading_day(current)
        added += 1
    return current
