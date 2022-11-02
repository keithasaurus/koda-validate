import asyncio

import pytest
from koda import Err, Ok

from koda_validate import (
    BoolValidator,
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
)
from koda_validate.boolean import EXPECTED_BOOL_ERR


def test_boolean() -> None:
    assert BoolValidator()("a string") == Err(["expected a boolean"])

    assert BoolValidator()(True) == Ok(True)

    assert BoolValidator()(False) == Ok(False)

    class RequireTrue(Predicate[bool, Serializable]):
        def is_valid(self, val: bool) -> bool:
            return val is True

        def err(self, val: bool) -> Serializable:
            return "must be true"

    assert BoolValidator(RequireTrue())(False) == Err(["must be true"])

    assert BoolValidator()(1) == Err(["expected a boolean"])


@pytest.mark.asyncio
async def test_boolean_validator_async() -> None:
    class Flip(Processor[bool]):
        def __call__(self, val: bool) -> bool:
            return not val

    class IsTrue(PredicateAsync[bool, Serializable]):
        async def is_valid_async(self, val: bool) -> bool:
            await asyncio.sleep(0.001)
            return val is True

        async def err_async(self, val: float) -> Serializable:
            return "not True"

    result = await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(True)

    assert result == Err(["not True"])
    assert await BoolValidator(
        preprocessors=[Flip()], predicates_async=[IsTrue()]
    ).validate_async(False) == Ok(True)

    assert await BoolValidator().validate_async("abc") == EXPECTED_BOOL_ERR
