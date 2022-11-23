import asyncio
from dataclasses import dataclass

import pytest
from koda._generics import A

from koda_validate.base import Predicate, PredicateAsync, Processor, TypeErr
from koda_validate.float import FloatValidator
from koda_validate.generic import Max, Min
from koda_validate.validated import Invalid, Valid


class Add1Float(Processor[float]):
    def __call__(self, val: float) -> float:
        return val + 1.0


def test_float() -> None:
    assert FloatValidator()("a string") == Invalid(TypeErr(float, "expected a float"))

    assert FloatValidator()(5.5) == Valid(5.5)

    assert FloatValidator()(4) == Invalid(TypeErr(float, "expected a float"))

    assert FloatValidator(Max(500.0))(503.0) == Invalid([Max(500.0)])

    assert FloatValidator(Max(500.0))(3.5) == Valid(3.5)

    assert FloatValidator(Min(5.0))(4.999) == Invalid([Min(5.0)])

    assert FloatValidator(Min(5.0))(5.0) == Valid(5.0)

    @dataclass
    class MustHaveAZeroSomewhere(Predicate[float]):
        err_message = "There should be a zero in the number"

        def __call__(self, val: float) -> bool:
            for char in str(val):
                if char == "0":
                    return True
            else:
                return False

    assert FloatValidator(Min(2.5), Max(4.0), MustHaveAZeroSomewhere())(5.5) == Invalid(
        [Max(4.0), MustHaveAZeroSomewhere()]
    )

    assert FloatValidator(Min(2.5), preprocessors=[Add1Float()])(1.0) == Invalid(
        [Min(2.5)]
    )


@pytest.mark.asyncio
async def test_float_async() -> None:
    @dataclass
    class LessThan4(PredicateAsync[float]):
        err_message = "not less than 4!"

        async def validate_async(self, val: float) -> bool:
            await asyncio.sleep(0.001)
            return val < 4.0

    result = await FloatValidator(
        preprocessors=[Add1Float()], predicates_async=[LessThan4()]
    ).validate_async(3.5)
    assert result == Invalid([LessThan4()])
    assert await FloatValidator(
        preprocessors=[Add1Float()], predicates_async=[LessThan4()]
    ).validate_async(2.5) == Valid(3.5)


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    float_validator = FloatValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        float_validator(5)
