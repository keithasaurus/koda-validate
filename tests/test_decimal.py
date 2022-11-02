import asyncio
from decimal import Decimal

import pytest
from koda import Err, Ok

from koda_validate import (
    DecimalValidator,
    Max,
    Min,
    PredicateAsync,
    Processor,
    Serializable,
)


def test_decimal() -> None:
    assert DecimalValidator()("a string") == Err(
        ["expected a Decimal, or a Decimal-compatible string or integer"]
    )

    assert DecimalValidator()(5.5) == Err(
        ["expected a Decimal, or a Decimal-compatible string or integer"]
    )

    assert DecimalValidator()(Decimal("5.5")) == Ok(Decimal("5.5"))

    assert DecimalValidator()(5) == Ok(Decimal(5))

    assert DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))(5) == Ok(Decimal(5))


@pytest.mark.asyncio
async def test_decimal_async() -> None:
    assert await DecimalValidator().validate_async("abc") == Err(
        ["expected a Decimal, or a Decimal-compatible string or integer"]
    )

    assert await DecimalValidator().validate_async(5.5) == Err(
        ["expected a Decimal, or a Decimal-compatible string or integer"]
    )

    class Add1Decimal(Processor[Decimal]):
        def __call__(self, val: Decimal) -> Decimal:
            return val + 1

    class LessThan4(PredicateAsync[Decimal, Serializable]):
        async def is_valid_async(self, val: Decimal) -> bool:
            await asyncio.sleep(0.001)
            return val < Decimal(4)

        async def err_async(self, val: Decimal) -> Serializable:
            return "not less than 4!"

    result = await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(3)
    assert result == Err(["not less than 4!"])
    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(2) == Ok(3)

    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(Decimal("2.75")) == Ok(Decimal("3.75"))

    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(Decimal("3.75")) == Err(["not less than 4!"])
