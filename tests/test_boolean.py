import asyncio
from dataclasses import dataclass

import pytest

from koda_validate import BoolValidator, Predicate, PredicateAsync, Processor
from koda_validate._generics import A
from koda_validate.base import TypeErr
from koda_validate.boolean import EXPECTED_BOOL_ERR
from koda_validate.validated import Invalid, Valid


class Flip(Processor[bool]):
    def __call__(self, val: bool) -> bool:
        return not val


def test_boolean() -> None:
    assert BoolValidator()("a string") == Invalid([TypeErr(bool, "expected a boolean")])

    assert BoolValidator()(True) == Valid(True)

    assert BoolValidator()(False) == Valid(False)

    @dataclass
    class RequireTrue(Predicate[bool]):
        err_message = "must be true"

        def __call__(self, val: bool) -> bool:
            return val is True

    assert BoolValidator(RequireTrue())(False) == Invalid([RequireTrue()])

    assert BoolValidator()(1) == Invalid([TypeErr(bool, "expected a boolean")])

    @dataclass
    class IsTrue(Predicate[bool]):
        err_message = "should be True"

        def __call__(self, val: bool) -> bool:
            return val is True

    assert BoolValidator(IsTrue(), preprocessors=[Flip()])(False) == Valid(True)

    assert BoolValidator(IsTrue())(False) == Invalid([IsTrue()])


@pytest.mark.asyncio
async def test_boolean_validator_async() -> None:
    @dataclass
    class IsTrue(PredicateAsync[bool]):
        err_message = "not True"

        async def validate_async(self, val: bool) -> bool:
            await asyncio.sleep(0.001)
            return val is True

    result = await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(True)

    assert result == Invalid([IsTrue()])
    assert await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(False) == Valid(True)

    assert await BoolValidator().validate_async("abc") == EXPECTED_BOOL_ERR


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    bool_validator = BoolValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        bool_validator(True)
