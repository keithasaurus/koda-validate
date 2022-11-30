import asyncio
from dataclasses import dataclass
from typing import Any, List

import pytest
from koda._generics import A

from koda_validate import (
    IntValidator,
    Invalid,
    PredicateAsync,
    Processor,
    StringValidator,
    Valid,
)
from koda_validate.base import InvalidIterable, InvalidPredicates, InvalidType
from koda_validate.float import FloatValidator
from koda_validate.generic import MaxItems, Min, MinItems
from koda_validate.list import ListValidator
from tests.utils import BasicNoneValidator


def test_list_validator() -> None:
    l_f_v = ListValidator(FloatValidator())
    assert l_f_v("a string") == Invalid(InvalidType(l_f_v, list))

    assert l_f_v([5.5, "something else"]) == Invalid(
        InvalidIterable(
            l_f_v,
            {1: InvalidType(l_f_v.item_validator, float)},
        )
    )

    assert ListValidator(FloatValidator())([5.5, 10.1]) == Valid([5.5, 10.1])

    assert ListValidator(FloatValidator())([]) == Valid([])

    class RemoveLast(Processor[List[Any]]):
        def __call__(self, val: List[Any]) -> List[Any]:
            return val[:-1]

    l_validator = ListValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
        preprocessors=[RemoveLast()],
    )
    assert l_validator([10.1, 7.7, 2.2, 5, 0.0]) == Invalid(
        InvalidPredicates(l_validator, [MaxItems(3)])
    )

    n_v = ListValidator(BasicNoneValidator())

    assert n_v([None, None]) == Valid([None, None])

    assert n_v([None, 1]) == Invalid(
        InvalidIterable(n_v, {1: InvalidType(n_v.item_validator, type(None))})
    )


@pytest.mark.asyncio
async def test_list_async() -> None:
    l_f_v = ListValidator(FloatValidator())
    assert await l_f_v.validate_async("a string") == Invalid(InvalidType(l_f_v, list))

    assert await l_f_v.validate_async([5.5, "something else"]) == Invalid(
        InvalidIterable(
            l_f_v,
            {1: InvalidType(l_f_v.item_validator, float)},
        )
    )

    assert await ListValidator(FloatValidator()).validate_async([5.5, 10.1]) == Valid(
        [5.5, 10.1]
    )

    assert await ListValidator(FloatValidator()).validate_async([]) == Valid([])

    l_validator = ListValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    )
    assert await l_validator.validate_async([10.1, 7.7, 2.2, 5]) == Invalid(
        InvalidPredicates(l_validator, [MaxItems(3)])
    )

    n_v = ListValidator(BasicNoneValidator())

    assert await n_v.validate_async([None, None]) == Valid([None, None])

    assert await n_v.validate_async([None, 1]) == Invalid(
        InvalidIterable(n_v, {1: InvalidType(n_v.item_validator, type(None))})
    )


@pytest.mark.asyncio
async def test_list_validator_with_async_predicate_validator() -> None:
    @dataclass
    class SomeAsyncListCheck(PredicateAsync[List[Any]]):
        async def validate_async(self, val: List[Any]) -> bool:
            await asyncio.sleep(0.001)
            return len(val) == 1

    l_validator = ListValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    )
    assert await l_validator.validate_async([]) == Invalid(
        InvalidPredicates(l_validator, [SomeAsyncListCheck()])
    )

    assert await ListValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    ).validate_async(["hooray"]) == Valid(["hooray"])


@pytest.mark.asyncio
async def test_child_validator_async_is_used() -> None:
    @dataclass
    class SomeIntDBCheck(PredicateAsync[int]):
        async def validate_async(self, val: int) -> bool:
            await asyncio.sleep(0.001)
            return val == 3

    class PopFrontOffList(Processor[List[Any]]):
        def __call__(self, val: List[Any]) -> List[Any]:
            return val[1:]

    l_validator = ListValidator(
        IntValidator(Min(2), predicates_async=[SomeIntDBCheck()]),
        predicates=[MaxItems(1)],
        preprocessors=[PopFrontOffList()],
    )

    assert await l_validator.validate_async([1, 3]) == Valid([3])

    assert await l_validator.validate_async([1, 1, 1]) == Invalid(
        InvalidPredicates(l_validator, [MaxItems(1)])
    )


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    list_validator = ListValidator(StringValidator(), predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        list_validator([])
