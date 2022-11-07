import asyncio

import pytest

from koda_validate import (
    BoolValidator,
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
)
from koda_validate._generics import A
from koda_validate.boolean import EXPECTED_BOOL_ERR
from koda_validate.validated import Invalid, Valid


class Flip(Processor[bool]):
    def __call__(self, val: bool) -> bool:
        return not val


def test_boolean() -> None:
    assert BoolValidator()("a string") == Invalid(["expected a boolean"])

    assert BoolValidator()(True) == Valid(True)

    assert BoolValidator()(False) == Valid(False)

    class RequireTrue(Predicate[bool, Serializable]):
        def is_valid(self, val: bool) -> bool:
            return val is True

        def err(self, val: bool) -> Serializable:
            return "must be true"

    assert BoolValidator(RequireTrue())(False) == Invalid(["must be true"])

    assert BoolValidator()(1) == Invalid(["expected a boolean"])

    class IsTrue(Predicate[bool, Serializable]):
        def is_valid(self, val: bool) -> bool:
            return val is True

        def err(self, val: bool) -> Serializable:
            return "should be True"

    assert BoolValidator(IsTrue(), preprocessors=[Flip()])(False) == Valid(True)

    assert BoolValidator(IsTrue(),)(
        False
    ) == Invalid(["should be True"])


@pytest.mark.asyncio
async def test_boolean_validator_async() -> None:
    class IsTrue(PredicateAsync[bool, Serializable]):
        async def is_valid_async(self, val: bool) -> bool:
            await asyncio.sleep(0.001)
            return val is True

        async def err_async(self, val: float) -> Serializable:
            return "not True"

    result = await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(True)

    assert result == Invalid(["not True"])
    assert await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(False) == Valid(True)

    assert await BoolValidator().validate_async("abc") == EXPECTED_BOOL_ERR


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    class AsyncWait(PredicateAsync[A, Serializable]):
        async def is_valid_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

        async def err_async(self, val: A) -> Serializable:
            return "should always succeed??"

    bool_validator = BoolValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        bool_validator(True)
