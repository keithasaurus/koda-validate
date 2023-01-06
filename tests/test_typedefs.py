import asyncio
from dataclasses import dataclass

import pytest

from koda_validate.base import PredicateAsync


@pytest.mark.asyncio
async def test_async_predicate_works_as_expected() -> None:
    @dataclass
    class ExampleStartsWithPredicate(PredicateAsync[str]):
        prefix: str

        async def validate_async(self, val: str) -> bool:
            await asyncio.sleep(0.001)
            return val.startswith(self.prefix)

    obj = ExampleStartsWithPredicate("abc")
    assert await obj.validate_async("def") is False
    assert await obj.validate_async("abc123") is True
