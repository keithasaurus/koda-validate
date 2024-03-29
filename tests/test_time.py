import asyncio
from dataclasses import dataclass
from datetime import date, datetime

import pytest

from koda_validate import (
    CoercionErr,
    DatetimeValidator,
    DateValidator,
    Invalid,
    PredicateAsync,
    Valid,
)
from koda_validate._generics import A


def test_date_validator() -> None:
    d_v = DateValidator()
    assert d_v("2021-03-21") == Valid(date(2021, 3, 21))
    assert d_v("2021-3-21") == Invalid(CoercionErr({str, date}, date), "2021-3-21", d_v)

    assert d_v(date(2022, 10, 1)) == Valid(date(2022, 10, 1))


@pytest.mark.asyncio
async def test_date_validator_async() -> None:
    d_v = DateValidator()
    assert await d_v.validate_async("2021-03-21") == Valid(date(2021, 3, 21))
    assert await d_v.validate_async("2021-3-21") == Invalid(
        CoercionErr(
            {str, date},
            date,
        ),
        "2021-3-21",
        d_v,
    )


def test_datetime_validator() -> None:
    dt_v = DatetimeValidator()
    assert dt_v("") == Invalid(CoercionErr({str, datetime}, datetime), "", dt_v)
    assert dt_v("2011-11-04") == Valid(datetime(2011, 11, 4, 0, 0))
    assert dt_v("2011-11-04T00:05:23") == Valid(datetime(2011, 11, 4, 0, 5, 23))

    now_ = datetime.now()
    assert dt_v(now_) == Valid(now_)


@pytest.mark.asyncio
async def test_datetime_validator_async() -> None:
    dt_v = DatetimeValidator()
    assert await dt_v.validate_async("") == Invalid(
        CoercionErr({str, datetime}, datetime), "", dt_v
    )
    assert await dt_v.validate_async("2011-11-04") == Valid(datetime(2011, 11, 4, 0, 0))
    assert await dt_v.validate_async("2011-11-04T00:05:23") == Valid(
        datetime(2011, 11, 4, 0, 5, 23)
    )


def test_sync_call_with_async_predicates_raises_assertion_error_date() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    date_validator = DateValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        date_validator("123")


def test_sync_call_with_async_predicates_raises_assertion_error_datetime() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    datetime_validator = DatetimeValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        datetime_validator("123")
