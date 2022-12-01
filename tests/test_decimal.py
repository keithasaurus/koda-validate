import asyncio
from dataclasses import dataclass
from decimal import Decimal

import pytest

from koda_validate import (
    DecimalValidator,
    Invalid,
    Max,
    Min,
    PredicateAsync,
    Processor,
    Valid,
)
from koda_validate._generics import A
from koda_validate.base import CoercionErr, PredicateErrs


class Add1Decimal(Processor[Decimal]):
    def __call__(self, val: Decimal) -> Decimal:
        return val + 1


def test_decimal() -> None:
    d_v = DecimalValidator()
    assert d_v("a string") == Invalid(
        d_v,
        CoercionErr(
            [str, int, Decimal],
            Decimal,
        ),
    )

    assert d_v(5.5) == Invalid(
        d_v,
        CoercionErr(
            [str, int, Decimal],
            Decimal,
        ),
    )

    assert DecimalValidator()(Decimal("5.5")) == Valid(Decimal("5.5"))

    assert DecimalValidator()(5) == Valid(Decimal(5))

    assert DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))(5) == Valid(Decimal(5))
    dec_min_max_v = DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))
    assert dec_min_max_v(Decimal(1)) == Invalid(
        dec_min_max_v, PredicateErrs([Min(Decimal(4))])
    )
    assert DecimalValidator(preprocessors=[Add1Decimal()])(Decimal("5.0")) == Valid(
        Decimal("6.0")
    )


@pytest.mark.asyncio
async def test_decimal_async() -> None:
    d_v = DecimalValidator()
    assert await d_v.validate_async("abc") == Invalid(
        d_v,
        CoercionErr(
            [str, int, Decimal],
            Decimal,
        ),
    )

    assert await d_v.validate_async(5.5) == Invalid(
        d_v,
        CoercionErr(
            [str, int, Decimal],
            Decimal,
        ),
    )

    @dataclass
    class LessThan4(PredicateAsync[Decimal]):
        async def validate_async(self, val: Decimal) -> bool:
            await asyncio.sleep(0.001)
            return val < Decimal(4)

    add_1_dec_v = DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    )
    result = await add_1_dec_v.validate_async(3)
    assert result == Invalid(add_1_dec_v, PredicateErrs([LessThan4()]))
    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(2) == Valid(3)

    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(Decimal("2.75")) == Valid(Decimal("3.75"))

    assert await add_1_dec_v.validate_async(Decimal("3.75")) == Invalid(
        add_1_dec_v, PredicateErrs([LessThan4()])
    )


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    dec_validator = DecimalValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        dec_validator("whatever")
