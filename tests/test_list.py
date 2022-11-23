import asyncio
from dataclasses import dataclass
from typing import Any, List

import pytest
from koda._generics import A

from koda_validate import (
    IntValidator,
    PredicateAsync,
    Processor,
    Serializable,
    StringValidator,
)
from koda_validate.base import IndexErrs, TypeErr
from koda_validate.float import FloatValidator
from koda_validate.generic import Min
from koda_validate.list import ListValidator, MaxItems, MinItems, unique_items
from koda_validate.validated import Invalid, Valid


def test_list_validator() -> None:
    assert ListValidator(FloatValidator())("a string") == Invalid(
        TypeErr(list, "expected a list")
    )

    assert ListValidator(FloatValidator())([5.5, "something else"]) == Invalid(
        IndexErrs(
            {1: TypeErr(float, "expected a float")},
        )
    )

    assert ListValidator(FloatValidator())([5.5, 10.1]) == Valid([5.5, 10.1])

    assert ListValidator(FloatValidator())([]) == Valid([])

    class RemoveLast(Processor[List[Any]]):
        def __call__(self, val: List[Any]) -> List[Any]:
            return val[:-1]

    assert ListValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
        preprocessors=[RemoveLast()],
    )([10.1, 7.7, 2.2, 5, 0.0]) == Invalid([MaxItems(3)])


@pytest.mark.asyncio
async def test_list_async() -> None:
    assert await ListValidator(FloatValidator()).validate_async("a string") == Invalid(
        TypeErr(list, "expected a list")
    )

    assert await ListValidator(FloatValidator()).validate_async(
        [5.5, "something else"]
    ) == Invalid(
        IndexErrs(
            {1: TypeErr(float, "expected a float")},
        )
    )

    assert await ListValidator(FloatValidator()).validate_async([5.5, 10.1]) == Valid(
        [5.5, 10.1]
    )

    assert await ListValidator(FloatValidator()).validate_async([]) == Valid([])

    assert await ListValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    ).validate_async([10.1, 7.7, 2.2, 5]) == Invalid([MaxItems(3)])


@pytest.mark.asyncio
async def test_list_validator_with_async_predicate_validator() -> None:
    @dataclass
    class SomeAsyncListCheck(PredicateAsync[List[Any]]):
        err_message = "not len 1"

        async def validate_async(self, val: List[Any]) -> bool:
            await asyncio.sleep(0.001)
            return len(val) == 1

    assert await ListValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    ).validate_async([]) == Invalid([SomeAsyncListCheck()])

    assert await ListValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    ).validate_async(["hooray"]) == Valid(["hooray"])


@pytest.mark.asyncio
async def test_child_validator_async_is_used() -> None:
    @dataclass
    class SomeIntDBCheck(PredicateAsync[int]):
        err_message = "not equal to three"

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

    assert await l_validator.validate_async([1, 1, 1]) == Invalid([MaxItems(1)])


def test_max_items() -> None:
    assert MaxItems(0)([]) is True

    assert MaxItems(5)([1, 2, 3]) is True

    assert MaxItems(5)(["a", "b", "c", "d", "e", "fghij"]) is False

    assert MaxItems(5).err_message == "maximum allowed length is 5"


def test_min_items() -> None:
    assert MinItems(0)([]) is True

    assert MinItems(3)([1, 2, 3]) is True
    assert MinItems(3)([1, 2]) is False

    assert MinItems(3).err_message == "minimum allowed length is 3"


def test_unique_items() -> None:
    assert unique_items([1, 2, 3]) is True
    assert unique_items([1, 1]) is False
    assert unique_items.err_message == "all items must be unique"
    assert unique_items([1, [], []]) is False
    assert unique_items([[], [1], [2]]) is True
    assert unique_items([{"something": {"a": 1}}, {"something": {"a": 1}}]) is False


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    list_validator = ListValidator(StringValidator(), predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        list_validator([])
