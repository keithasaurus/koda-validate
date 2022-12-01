import asyncio
from dataclasses import dataclass

import pytest

from koda_validate import (
    BoolValidator,
    Invalid,
    Predicate,
    PredicateAsync,
    Processor,
    Valid,
)
from koda_validate._generics import A
from koda_validate.base import PredicateErrs, TypeErr


class Flip(Processor[bool]):
    def __call__(self, val: bool) -> bool:
        return not val


def test_boolean() -> None:
    b_v = BoolValidator()
    assert b_v("a string") == Invalid(b_v, TypeErr(bool))

    assert b_v(True) == Valid(True)

    assert b_v(False) == Valid(False)

    @dataclass
    class RequireTrue(Predicate[bool]):
        def __call__(self, val: bool) -> bool:
            return val is True

    assert (true_bool := BoolValidator(RequireTrue()))(False) == Invalid(
        true_bool, PredicateErrs([RequireTrue()])
    )

    assert b_v(1) == Invalid(b_v, TypeErr(bool))

    @dataclass
    class IsTrue(Predicate[bool]):
        def __call__(self, val: bool) -> bool:
            return val is True

    assert BoolValidator(IsTrue(), preprocessors=[Flip()])(False) == Valid(True)

    assert (req_true_v := BoolValidator(IsTrue()))(False) == Invalid(
        req_true_v, PredicateErrs([IsTrue()])
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

    assert result == Invalid(require_true_v, PredicateErrs([IsTrue()]))
    assert await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(False) == Valid(True)

    b_v = BoolValidator()

    assert await b_v.validate_async("abc") == Invalid(b_v, TypeErr(bool))


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    bool_validator = BoolValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        bool_validator(True)
