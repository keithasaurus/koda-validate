import asyncio
from dataclasses import dataclass
from typing import Any, List

import pytest
from koda import Err, Ok, Result

from koda_validate import Predicate, Validator
from koda_validate.typedefs import PredicateAsync, ValidatorAsync


@pytest.mark.asyncio
async def test_async_defaults_to_call_for_validator() -> None:
    class ExampleStringValidator(Validator[Any, str, List[str]]):
        def __call__(self, val: Any) -> Result[str, List[str]]:
            if isinstance(val, str):
                return Ok(val)
            else:
                return Err(["expected a string"])

    obj = ExampleStringValidator()
    assert obj("neat") == Ok("neat")
    assert obj(5) == Err(["expected a string"])
    assert await obj.validate_async("neat") == Ok("neat")
    assert await obj.validate_async(None) == Err(["expected a string"])


@pytest.mark.asyncio
async def test_async_defaults_to_call_for_predicate() -> None:
    @dataclass
    class ExampleStartsWithPredicate(Predicate[str, str]):
        prefix: str

        def is_valid(self, val: str) -> bool:
            return val.startswith(self.prefix)

        def err(self, val: str) -> str:
            return f"did not start with {self.prefix}"

    obj = ExampleStartsWithPredicate("abc")
    assert obj("def") == Err("did not start with abc")
    assert obj("abc123") == Ok("abc123")
    assert await obj.validate_async("def") == Err("did not start with abc")
    assert await obj.validate_async("abc123") == Ok("abc123")


@pytest.mark.asyncio
async def test_async_validator_works_as_expected() -> None:
    class ExampleStringValidator(ValidatorAsync[Any, str, List[str]]):
        async def validate_async(self, val: Any) -> Result[str, List[str]]:
            await asyncio.sleep(0.001)
            if isinstance(val, str):
                return Ok(val)
            else:
                return Err(["expected a string"])

    obj = ExampleStringValidator()
    assert await obj.validate_async("neat") == Ok("neat")
    assert await obj.validate_async(5) == Err(["expected a string"])


@pytest.mark.asyncio
async def test_async_predicate_works_as_expected() -> None:
    @dataclass
    class ExampleStartsWithPredicate(PredicateAsync[str, str]):
        prefix: str

        async def is_valid_async(self, val: str) -> bool:
            await asyncio.sleep(0.001)
            return val.startswith(self.prefix)

        async def err_async(self, val: str) -> str:
            return f"did not start with {self.prefix}"

    obj = ExampleStartsWithPredicate("abc")
    assert await obj.validate_async("def") == Err("did not start with abc")
    assert await obj.validate_async("abc123") == Ok("abc123")
