import asyncio
from dataclasses import dataclass

import pytest

from koda_validate.base import PredicateAsync
from koda_validate.validated import Invalid, Valid


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
    assert await obj.validate_async("def") == Invalid("did not start with abc")
    assert await obj.validate_async("abc123") == Valid("abc123")
