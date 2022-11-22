import asyncio
from dataclasses import dataclass
from decimal import Decimal

import pytest

from koda_validate import DecimalValidator, Max, Min, PredicateAsync, Processor
from koda_validate._generics import A
from koda_validate.base import CoercionErr
from koda_validate.validated import Invalid, Valid


class Add1Decimal(Processor[Decimal]):
    def __call__(self, val: Decimal) -> Decimal:
        return val + 1


def test_decimal() -> None:
    assert DecimalValidator()("a string") == Invalid(
        [
            CoercionErr(
                [str, int, Decimal],
                Decimal,
                "expected a Decimal, or a Decimal-compatible string or integer",
            )
        ]
    )

    assert DecimalValidator()(5.5) == Invalid(
        [
            CoercionErr(
                [str, int, Decimal],
                Decimal,
                "expected a Decimal, or a Decimal-compatible string or integer",
            )
        ]
    )

    assert DecimalValidator()(Decimal("5.5")) == Valid(Decimal("5.5"))

    assert DecimalValidator()(5) == Valid(Decimal(5))

    assert DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))(5) == Valid(Decimal(5))
    assert DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))(Decimal(1)) == Invalid(
        [Min(Decimal(4))]
    )
    assert DecimalValidator(preprocessors=[Add1Decimal()])(Decimal("5.0")) == Valid(
        Decimal("6.0")
    )


@pytest.mark.asyncio
async def test_decimal_async() -> None:
    assert await DecimalValidator().validate_async("abc") == Invalid(
        [
            CoercionErr(
                [str, int, Decimal],
                Decimal,
                "expected a Decimal, or a Decimal-compatible string or integer",
            )
        ]
    )

    assert await DecimalValidator().validate_async(5.5) == Invalid(
        [
            CoercionErr(
                [str, int, Decimal],
                Decimal,
                "expected a Decimal, or a Decimal-compatible string or integer",
            )
        ]
    )

    @dataclass
    class LessThan4(PredicateAsync[Decimal]):
        err_message = "not less than 4!"

        async def validate_async(self, val: Decimal) -> bool:
            await asyncio.sleep(0.001)
            return val < Decimal(4)

    result = await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(3)
    assert result == Invalid([LessThan4()])
    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(2) == Valid(3)

    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(Decimal("2.75")) == Valid(Decimal("3.75"))

    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(Decimal("3.75")) == Invalid([LessThan4()])


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    dec_validator = DecimalValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        dec_validator("whatever")
