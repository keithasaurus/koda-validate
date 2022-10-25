from datetime import date, datetime

from koda import Err, Ok

from koda_validate import DatetimeValidator, DateValidator


def test_date_validator() -> None:
    assert DateValidator()("2021-03-21") == Ok(date(2021, 3, 21))
    assert DateValidator()("2021-3-21") == Err(["expected date formatted as yyyy-mm-dd"])


def test_datetime_validator() -> None:
    assert DatetimeValidator()("") == Err(["expected iso8601-formatted string"])
    assert DatetimeValidator()("2011-11-04") == Ok(datetime(2011, 11, 4, 0, 0))
    assert DatetimeValidator()("2011-11-04T00:05:23") == Ok(
        datetime(2011, 11, 4, 0, 5, 23)
    )
