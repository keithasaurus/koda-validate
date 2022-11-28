import asyncio
from dataclasses import dataclass

import pytest
from koda._generics import A

from koda_validate import IntValidator, Max, Min, Predicate, PredicateAsync, Processor
from koda_validate.base import InvalidType
from koda_validate.validated import Invalid, Valid


class Add1Int(Processor[int]):
    def __call__(self, val: int) -> int:
        return val + 1


def test_integer() -> None:
    i_v = IntValidator()
    assert i_v("a string") == Invalid(InvalidType(int, i_v))

    assert i_v(5) == Valid(5)

    assert i_v(True) == Invalid(InvalidType(int, i_v)), (
        "even though `bool`s are subclasses of ints in python, we wouldn't "
        "want to validate incoming data as ints if they are bools"
    )

    assert i_v("5") == Invalid(InvalidType(int, i_v))

    assert i_v(5.0) == Invalid(InvalidType(int, i_v))

    @dataclass
    class DivisibleBy2(Predicate[int]):
        err_message = "must be divisible by 2"

        def __call__(self, val: int) -> bool:
            return val % 2 == 0

    assert IntValidator(Min(2), Max(10), DivisibleBy2(),)(
        11
    ) == Invalid([Max(10), DivisibleBy2()])

    assert IntValidator(Min(2), preprocessors=[Add1Int()])(1) == Valid(2)

    assert IntValidator(Min(3), preprocessors=[Add1Int()])(1) == Invalid([Min(3)])


@pytest.mark.asyncio
async def test_float_async() -> None:
    class Add1Int(Processor[int]):
        def __call__(self, val: int) -> int:
            return val + 1

    @dataclass
    class LessThan4(PredicateAsync[int]):
        err_message = "not less than 4!"

        async def validate_async(self, val: int) -> bool:
            await asyncio.sleep(0.001)
            return val < 4.0

    result = await IntValidator(
        preprocessors=[Add1Int()], predicates_async=[LessThan4()]
    ).validate_async(3)
    assert result == Invalid([LessThan4()])
    assert await IntValidator(
        preprocessors=[Add1Int()], predicates_async=[LessThan4()]
    ).validate_async(2) == Valid(3)


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    int_validator = IntValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        int_validator(5)
