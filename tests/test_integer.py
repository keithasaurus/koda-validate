import asyncio
from dataclasses import dataclass

import pytest
from koda._generics import A

from koda_validate import (
    IntValidator,
    Invalid,
    Max,
    Min,
    Predicate,
    PredicateAsync,
    Processor,
    Valid,
)
from koda_validate.base import PredicateErrs, TypeErr


class Add1Int(Processor[int]):
    def __call__(self, val: int) -> int:
        return val + 1


def test_integer() -> None:
    i_v = IntValidator()
    assert i_v("a string") == Invalid(TypeErr(int), "a string", i_v)

    assert i_v(5) == Valid(5)

    assert i_v(True) == Invalid(TypeErr(int), True, i_v), (
        "even though `bool`s are subclasses of ints in python, we wouldn't "
        "want to validate incoming data as ints if they are bools"
    )

    assert i_v("5") == Invalid(TypeErr(int), "5", i_v)

    assert i_v(5.0) == Invalid(TypeErr(int), 5.0, i_v)

    @dataclass
    class DivisibleBy2(Predicate[int]):
        def __call__(self, val: int) -> bool:
            return val % 2 == 0

    i_v = IntValidator(Min(2), Max(10), DivisibleBy2())
    assert i_v(11) == Invalid(PredicateErrs([Max(10), DivisibleBy2()]), 11, i_v)

    assert IntValidator(Min(2), preprocessors=[Add1Int()])(1) == Valid(2)

    i_v_add_1 = IntValidator(Min(3), preprocessors=[Add1Int()])
    assert i_v_add_1(1) == Invalid(PredicateErrs([Min(3)]), 2, i_v_add_1)


@pytest.mark.asyncio
async def test_float_async() -> None:
    class Add1Int(Processor[int]):
        def __call__(self, val: int) -> int:
            return val + 1

    @dataclass
    class LessThan4(PredicateAsync[int]):
        async def validate_async(self, val: int) -> bool:
            await asyncio.sleep(0.001)
            return val < 4.0

    validator = IntValidator(preprocessors=[Add1Int()], predicates_async=[LessThan4()])
    result = await validator.validate_async(3)
    assert result == Invalid(PredicateErrs([LessThan4()]), 4, validator)
    assert await IntValidator(
        preprocessors=[Add1Int()], predicates_async=[LessThan4()]
    ).validate_async(2) == Valid(3)


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    int_validator = IntValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        int_validator(5)
