import asyncio
from dataclasses import dataclass

import pytest
from koda._generics import A

from koda_validate import Invalid, Valid
from koda_validate.base import (
    Predicate,
    PredicateAsync,
    PredicateErrs,
    Processor,
    TypeErr,
)
from koda_validate.float import FloatValidator
from koda_validate.generic import Max, Min


class Add1Float(Processor[float]):
    def __call__(self, val: float) -> float:
        return val + 1.0


def test_float() -> None:
    f_v = FloatValidator()
    assert f_v("a string") == Invalid(TypeErr(float), "a string", f_v)

    assert f_v(5.5) == Valid(5.5)

    assert f_v(4) == Invalid(TypeErr(float), 4, f_v)

    f_max_500_v = FloatValidator(Max(500.0))
    assert f_max_500_v(503.0) == Invalid(PredicateErrs([Max(500.0)]), 503.0, f_max_500_v)

    assert FloatValidator(Max(500.0))(3.5) == Valid(3.5)

    f_max_5_v = FloatValidator(Min(5.0))
    assert f_max_5_v(4.999) == Invalid(PredicateErrs([Min(5.0)]), 4.999, f_max_5_v)

    assert FloatValidator(Min(5.0))(5.0) == Valid(5.0)

    @dataclass
    class MustHaveAZeroSomewhere(Predicate[float]):
        def __call__(self, val: float) -> bool:
            for char in str(val):
                if char == "0":
                    return True
            else:
                return False

    f_min_max_v = FloatValidator(Min(2.5), Max(4.0), MustHaveAZeroSomewhere())
    assert f_min_max_v(5.5) == Invalid(
        PredicateErrs([Max(4.0), MustHaveAZeroSomewhere()]), 5.5, f_min_max_v
    )

    f_min_25_v = FloatValidator(Min(2.5), preprocessors=[Add1Float()])
    assert f_min_25_v(1.0) == Invalid(PredicateErrs([Min(2.5)]), 2.0, f_min_25_v)


@pytest.mark.asyncio
async def test_float_async() -> None:
    @dataclass
    class LessThan4(PredicateAsync[float]):
        async def validate_async(self, val: float) -> bool:
            await asyncio.sleep(0.001)
            return val < 4.0

    f_v = FloatValidator(preprocessors=[Add1Float()], predicates_async=[LessThan4()])
    result = await f_v.validate_async(3.5)
    assert result == Invalid(PredicateErrs([LessThan4()]), 4.5, f_v)
    assert await FloatValidator(
        preprocessors=[Add1Float()], predicates_async=[LessThan4()]
    ).validate_async(2.5) == Valid(3.5)


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    float_validator = FloatValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        float_validator(5)
