from datetime import date, datetime

from koda import Err, Ok

from koda_validate import DateStringValidator, DatetimeStringValidator


def test_date_validator() -> None:
    assert DateStringValidator()("2021-03-21") == Ok(date(2021, 3, 21))
    assert DateStringValidator()("2021-3-21") == Err(
        ["expected date formatted as yyyy-mm-dd"]
    )


def test_datetime_validator() -> None:
    assert DatetimeStringValidator()("") == Err(["expected iso8601-formatted string"])
    assert DatetimeStringValidator()("2011-11-04") == Ok(datetime(2011, 11, 4, 0, 0))
    assert DatetimeStringValidator()("2011-11-04T00:05:23") == Ok(
        datetime(2011, 11, 4, 0, 5, 23)
    )
