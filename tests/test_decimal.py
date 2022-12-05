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


@dataclass
class Add1Decimal(Processor[Decimal]):
    def __call__(self, val: Decimal) -> Decimal:
        return val + 1


def test_decimal() -> None:
    d_v = DecimalValidator()
    assert d_v("a string") == Invalid(
        d_v,
        "a string",
        CoercionErr(
            {str, int, Decimal},
            Decimal,
        ),
    )

    assert d_v(5.5) == Invalid(
        d_v,
        5.5,
        CoercionErr(
            {str, int, Decimal},
            Decimal,
        ),
    )

    assert DecimalValidator()(Decimal("5.5")) == Valid(Decimal("5.5"))

    assert DecimalValidator()(5) == Valid(Decimal(5))

    assert DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))(5) == Valid(Decimal(5))
    dec_min_max_v = DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))
    assert dec_min_max_v(Decimal(1)) == Invalid(
        dec_min_max_v, Decimal(1), PredicateErrs([Min(Decimal(4))])
    )
    assert DecimalValidator(preprocessors=[Add1Decimal()])(Decimal("5.0")) == Valid(
        Decimal("6.0")
    )


@pytest.mark.asyncio
async def test_decimal_async() -> None:
    d_v = DecimalValidator()
    assert await d_v.validate_async("abc") == Invalid(
        d_v,
        "abc",
        CoercionErr(
            {str, int, Decimal},
            Decimal,
        ),
    )

    assert await d_v.validate_async(5.5) == Invalid(
        d_v,
        5.5,
        CoercionErr(
            {str, int, Decimal},
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
    assert result == Invalid(add_1_dec_v, Decimal(4), PredicateErrs([LessThan4()]))
    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(2) == Valid(Decimal(3))

    assert await DecimalValidator(
        preprocessors=[Add1Decimal()], predicates_async=[LessThan4()]
    ).validate_async(Decimal("2.75")) == Valid(Decimal("3.75"))

    assert await add_1_dec_v.validate_async(Decimal("3.75")) == Invalid(
        add_1_dec_v, Decimal("4.75"), PredicateErrs([LessThan4()])
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


@dataclass
class DecAsyncPred(PredicateAsync[Decimal]):
    async def validate_async(self, val: Decimal) -> bool:
        return True


def test_repr() -> None:
    s = DecimalValidator()
    assert repr(s) == "DecimalValidator()"

    s_len = DecimalValidator(Min(Decimal(1)), Max(Decimal(5)))
    assert (
        repr(s_len)
        == "DecimalValidator(Min(minimum=Decimal('1'), exclusive_minimum=False), "
        "Max(maximum=Decimal('5'), exclusive_maximum=False))"
    )

    s_all = DecimalValidator(
        Min(Decimal(1)), predicates_async=[DecAsyncPred()], preprocessors=[Add1Decimal()]
    )

    assert (
        repr(s_all)
        == "DecimalValidator(Min(minimum=Decimal('1'), exclusive_minimum=False), "
        "predicates_async=[DecAsyncPred()], preprocessors=[Add1Decimal()])"
    )


def test_equivalence() -> None:
    d_1 = DecimalValidator()
    d_2 = DecimalValidator()
    assert d_1 == d_2

    d_pred_1 = DecimalValidator(Max(Decimal(1)))
    assert d_pred_1 != d_1
    d_pred_2 = DecimalValidator(Max(Decimal(1)))
    assert d_pred_2 == d_pred_1

    d_pred_async_1 = DecimalValidator(Max(Decimal(1)), predicates_async=[DecAsyncPred()])
    assert d_pred_async_1 != d_pred_1
    d_pred_async_2 = DecimalValidator(Max(Decimal(1)), predicates_async=[DecAsyncPred()])
    assert d_pred_async_1 == d_pred_async_2

    d_preproc_1 = DecimalValidator(
        Max(Decimal(1)), predicates_async=[DecAsyncPred()], preprocessors=[Add1Decimal()]
    )
    assert d_preproc_1 != d_pred_async_1

    d_preproc_2 = DecimalValidator(
        Max(Decimal(1)), predicates_async=[DecAsyncPred()], preprocessors=[Add1Decimal()]
    )
    assert d_preproc_1 == d_preproc_2
