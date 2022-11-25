import asyncio
from dataclasses import dataclass
from datetime import date, datetime

import pytest

from koda_validate import DatetimeStringValidator, DateValidator, PredicateAsync
from koda_validate._generics import A
from koda_validate.base import InvalidCoercion
from koda_validate.validated import Invalid, Valid


def test_date_validator() -> None:
    assert DateValidator()("2021-03-21") == Valid(date(2021, 3, 21))
    assert DateValidator()("2021-3-21") == Invalid(
        InvalidCoercion(
            [str, date], date, "expected date or string formatted as yyyy-mm-dd"
        )
    )


@pytest.mark.asyncio
async def test_date_validator_async() -> None:
    assert await DateValidator().validate_async("2021-03-21") == Valid(date(2021, 3, 21))
    assert await DateValidator().validate_async("2021-3-21") == Invalid(
        InvalidCoercion(
            [str, date], date, "expected date or string formatted as yyyy-mm-dd"
        )
    )


def test_datetime_validator() -> None:
    assert DatetimeStringValidator()("") == Invalid(
        InvalidCoercion(
            [str, datetime], datetime, "expected datetime or iso8601-formatted string"
        )
    )
    assert DatetimeStringValidator()("2011-11-04") == Valid(datetime(2011, 11, 4, 0, 0))
    assert DatetimeStringValidator()("2011-11-04T00:05:23") == Valid(
        datetime(2011, 11, 4, 0, 5, 23)
    )


@pytest.mark.asyncio
async def test_datetime_validator_async() -> None:
    assert await DatetimeStringValidator().validate_async("") == Invalid(
        InvalidCoercion(
            [str, datetime], datetime, "expected datetime or iso8601-formatted string"
        )
    )
    assert await DatetimeStringValidator().validate_async("2011-11-04") == Valid(
        datetime(2011, 11, 4, 0, 0)
    )
    assert await DatetimeStringValidator().validate_async("2011-11-04T00:05:23") == Valid(
        datetime(2011, 11, 4, 0, 5, 23)
    )


def test_sync_call_with_async_predicates_raises_assertion_error_date() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    date_validator = DateValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        date_validator("123")


def test_sync_call_with_async_predicates_raises_assertion_error_datetime() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    datetime_validator = DatetimeStringValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        datetime_validator("123")
