import asyncio
from dataclasses import dataclass

import pytest

from koda_validate import (
    BoolValidator,
    Invalid,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    Processor,
    TypeErr,
    Valid,
)
from koda_validate._generics import A


class Flip(Processor[bool]):
    def __call__(self, val: bool) -> bool:
        return not val


def test_boolean() -> None:
    b_v = BoolValidator()
    assert b_v("a string") == Invalid(TypeErr(bool), "a string", b_v)

    assert b_v(True) == Valid(True)

    assert b_v(False) == Valid(False)

    @dataclass
    class RequireTrue(Predicate[bool]):
        def __call__(self, val: bool) -> bool:
            return val is True

    assert (true_bool := BoolValidator(RequireTrue()))(False) == Invalid(
        PredicateErrs([RequireTrue()]), False, true_bool
    )

    assert b_v(1) == Invalid(TypeErr(bool), 1, b_v)

    @dataclass
    class IsTrue(Predicate[bool]):
        def __call__(self, val: bool) -> bool:
            return val is True

    assert BoolValidator(IsTrue(), preprocessors=[Flip()])(False) == Valid(True)

    assert (req_true_v := BoolValidator(IsTrue()))(False) == Invalid(
        PredicateErrs([IsTrue()]), False, req_true_v
    )


@pytest.mark.asyncio
async def test_boolean_validator_async() -> None:
    @dataclass
    class IsTrue(PredicateAsync[bool]):
        async def validate_async(self, val: bool) -> bool:
            await asyncio.sleep(0.001)
            return val is True

    result = await (
        require_true_v := BoolValidator(
            preprocessors=[Flip()], predicates_async=[IsTrue()]
        )
    ).validate_async(True)

    assert result == Invalid(PredicateErrs([IsTrue()]), False, require_true_v)
    assert await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(False) == Valid(True)

    b_v = BoolValidator()

    assert await b_v.validate_async("abc") == Invalid(TypeErr(bool), "abc", b_v)


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    bool_validator = BoolValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        bool_validator(True)
