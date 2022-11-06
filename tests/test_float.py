import asyncio

import pytest

from koda_validate.base import Predicate, PredicateAsync, Processor, Serializable
from koda_validate.float import FloatValidator
from koda_validate.generic import Max, Min
from koda_validate.validated import Invalid, Valid


class Add1Float(Processor[float]):
    def __call__(self, val: float) -> float:
        return val + 1.0


def test_float() -> None:
    assert FloatValidator()("a string") == Invalid(["expected a float"])

    assert FloatValidator()(5.5) == Valid(5.5)

    assert FloatValidator()(4) == Invalid(["expected a float"])

    assert FloatValidator(Max(500.0))(503.0) == Invalid(
        ["maximum allowed value is 500.0"]
    )

    assert FloatValidator(Max(500.0))(3.5) == Valid(3.5)

    assert FloatValidator(Min(5.0))(4.999) == Invalid(["minimum allowed value is 5.0"])

    assert FloatValidator(Min(5.0))(5.0) == Valid(5.0)

    class MustHaveAZeroSomewhere(Predicate[float, Serializable]):
        def is_valid(self, val: float) -> bool:
            for char in str(val):
                if char == "0":
                    return True
            else:
                return False

        def err(self, val: float) -> Serializable:
            return "There should be a zero in the number"

    assert FloatValidator(Min(2.5), Max(4.0), MustHaveAZeroSomewhere())(5.5) == Invalid(
        ["maximum allowed value is 4.0", "There should be a zero in the number"]
    )

    assert FloatValidator(Min(2.5), preprocessors=[Add1Float()])(1.0) == Invalid(
        ["minimum allowed value is 2.5"]
    )


@pytest.mark.asyncio
async def test_float_async() -> None:
    class LessThan4(PredicateAsync[float, Serializable]):
        async def is_valid_async(self, val: float) -> bool:
            await asyncio.sleep(0.001)
            return val < 4.0

        async def err_async(self, val: float) -> Serializable:
            return "not less than 4!"

    result = await FloatValidator(
        preprocessors=[Add1Float()], predicates_async=[LessThan4()]
    ).validate_async(3.5)
    assert result == Invalid(["not less than 4!"])
    assert await FloatValidator(
        preprocessors=[Add1Float()], predicates_async=[LessThan4()]
    ).validate_async(2.5) == Valid(3.5)
