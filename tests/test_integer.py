import asyncio

import pytest
from koda import Err, Ok

from koda_validate import (
    IntValidator,
    Max,
    Min,
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
)


class Add1Int(Processor[int]):
    def __call__(self, val: int) -> int:
        return val + 1


def test_integer() -> None:
    assert IntValidator()("a string") == Err(["expected an integer"])

    assert IntValidator()(5) == Ok(5)

    assert IntValidator()(True) == Err(["expected an integer"]), (
        "even though `bool`s are subclasses of ints in python, we wouldn't "
        "want to validate incoming data as ints if they are bools"
    )

    assert IntValidator()("5") == Err(["expected an integer"])

    assert IntValidator()(5.0) == Err(["expected an integer"])

    class DivisibleBy2(Predicate[int, Serializable]):
        def is_valid(self, val: int) -> bool:
            return val % 2 == 0

        def err(self, val: int) -> Serializable:
            return "must be divisible by 2"

    assert IntValidator(Min(2), Max(10), DivisibleBy2(),)(
        11
    ) == Err(["maximum allowed value is 10", "must be divisible by 2"])

    assert IntValidator(Min(2), preprocessors=[Add1Int()])(1) == Ok(2)

    assert IntValidator(Min(3), preprocessors=[Add1Int()])(1) == Err(
        ["minimum allowed value is 3"]
    )


@pytest.mark.asyncio
async def test_float_async() -> None:
    class Add1Int(Processor[int]):
        def __call__(self, val: int) -> int:
            return val + 1

    class LessThan4(PredicateAsync[int, Serializable]):
        async def is_valid_async(self, val: int) -> bool:
            await asyncio.sleep(0.001)
            return val < 4.0

        async def err_async(self, val: int) -> Serializable:
            return "not less than 4!"

    result = await IntValidator(
        preprocessors=[Add1Int()], predicates_async=[LessThan4()]
    ).validate_async(3)
    assert result == Err(["not less than 4!"])
    assert await IntValidator(
        preprocessors=[Add1Int()], predicates_async=[LessThan4()]
    ).validate_async(2) == Ok(3)
