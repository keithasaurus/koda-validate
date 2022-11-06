import asyncio
from typing import Any, List

import pytest

from koda_validate import (
    IntValidator,
    PredicateAsync,
    Processor,
    Serializable,
    StringValidator,
)
from koda_validate.float import FloatValidator
from koda_validate.generic import Min
from koda_validate.list import ListValidator, MaxItems, MinItems, unique_items
from koda_validate.typedefs import Err, Ok


def test_list_validator() -> None:
    assert ListValidator(FloatValidator())("a string") == Err(
        {"__container__": ["expected a list"]}
    )

    assert ListValidator(FloatValidator())([5.5, "something else"]) == Err(
        {"1": ["expected a float"]}
    )

    assert ListValidator(FloatValidator())([5.5, 10.1]) == Ok([5.5, 10.1])

    assert ListValidator(FloatValidator())([]) == Ok([])

    class RemoveLast(Processor[List[Any]]):
        def __call__(self, val: List[Any]) -> List[Any]:
            return val[:-1]

    assert ListValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
        preprocessors=[RemoveLast()],
    )([10.1, 7.7, 2.2, 5, 0.0]) == Err(
        {
            "2": ["minimum allowed value is 5.5"],
            "3": ["expected a float"],
            "__container__": ["maximum allowed length is 3"],
        }
    )


@pytest.mark.asyncio
async def test_list_async() -> None:
    assert await ListValidator(FloatValidator()).validate_async("a string") == Err(
        {"__container__": ["expected a list"]}
    )

    assert await ListValidator(FloatValidator()).validate_async(
        [5.5, "something else"]
    ) == Err({"1": ["expected a float"]})

    assert await ListValidator(FloatValidator()).validate_async([5.5, 10.1]) == Ok(
        [5.5, 10.1]
    )

    assert await ListValidator(FloatValidator()).validate_async([]) == Ok([])

    assert await ListValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    ).validate_async([10.1, 7.7, 2.2, 5]) == Err(
        {
            "2": ["minimum allowed value is 5.5"],
            "3": ["expected a float"],
            "__container__": ["maximum allowed length is 3"],
        }
    )


@pytest.mark.asyncio
async def test_list_validator_with_async_predicate_validator() -> None:
    class SomeAyncListCheck(PredicateAsync[List[Any], Serializable]):
        async def is_valid_async(self, val: List[Any]) -> bool:
            await asyncio.sleep(0.001)
            return len(val) == 1

        async def err_async(self, val: List[Any]) -> Serializable:
            return "not len 1"

    assert await ListValidator(
        StringValidator(), predicates_async=[SomeAyncListCheck()]
    ).validate_async([]) == Err({"__container__": ["not len 1"]})

    assert await ListValidator(
        StringValidator(), predicates_async=[SomeAyncListCheck()]
    ).validate_async(["hooray"]) == Ok(["hooray"])


@pytest.mark.asyncio
async def test_child_validator_async_is_used() -> None:
    class SomeIntDBCheck(PredicateAsync[int, Serializable]):
        async def is_valid_async(self, val: int) -> bool:
            await asyncio.sleep(0.001)
            return val == 3

        async def err_async(self, val: int) -> Serializable:
            await asyncio.sleep(0.001)
            return "not equal to three"

    class PopFrontOffList(Processor[List[Any]]):
        def __call__(self, val: List[Any]) -> List[Any]:
            return val[1:]

    l_validator = ListValidator(
        IntValidator(Min(2), predicates_async=[SomeIntDBCheck()]),
        predicates=[MaxItems(1)],
        preprocessors=[PopFrontOffList()],
    )

    assert await l_validator.validate_async([1, 3]) == Ok([3])

    assert await l_validator.validate_async([1, 1, 1]) == Err(
        {
            "0": ["minimum allowed value is 2", "not equal to three"],
            "1": ["minimum allowed value is 2", "not equal to three"],
            "__container__": ["maximum allowed length is 1"],
        }
    )


def test_max_items() -> None:
    assert MaxItems(0)([]) == Ok([])

    assert MaxItems(5)([1, 2, 3]) == Ok([1, 2, 3])

    assert MaxItems(5)(["a", "b", "c", "d", "e", "fghij"]) == Err(
        "maximum allowed length is 5"
    )


def test_min_items() -> None:
    assert MinItems(0)([]) == Ok([])

    assert MinItems(3)([1, 2, 3]) == Ok([1, 2, 3])

    assert MinItems(3)([1, 2]) == Err("minimum allowed length is 3")


def test_unique_items() -> None:
    unique_fail = Err("all items must be unique")
    assert unique_items([1, 2, 3]) == Ok([1, 2, 3])
    assert unique_items([1, 1]) == unique_fail
    assert unique_items([1, [], []]) == unique_fail
    assert unique_items([[], [1], [2]]) == Ok([[], [1], [2]])
    assert unique_items([{"something": {"a": 1}}, {"something": {"a": 1}}]) == unique_fail
