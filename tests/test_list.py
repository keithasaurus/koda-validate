import asyncio
from dataclasses import dataclass
from typing import Any, List

import pytest
from koda._generics import A

from koda_validate import (
    IntValidator,
    Invalid,
    MaxLength,
    MinLength,
    PredicateAsync,
    Processor,
    StringValidator,
    Valid,
)
from koda_validate.base import IndexErrs, PredicateErrs, TypeErr
from koda_validate.float import FloatValidator
from koda_validate.generic import MaxItems, Min, MinItems
from koda_validate.list import ListValidator
from tests.utils import BasicNoneValidator


@dataclass
class RemoveLast(Processor[List[Any]]):
    def __call__(self, val: List[Any]) -> List[Any]:
        return val[:-1]


def test_list_validator() -> None:
    l_f_v = ListValidator(FloatValidator())
    assert l_f_v("a string") == Invalid(l_f_v, "a string", TypeErr(list))

    assert l_f_v([5.5, "something else"]) == Invalid(
        l_f_v,
        [5.5, "something else"],
        IndexErrs(
            {1: Invalid(l_f_v.item_validator, "something else", TypeErr(float))},
        ),
    )

    assert ListValidator(FloatValidator())([5.5, 10.1]) == Valid([5.5, 10.1])

    assert ListValidator(FloatValidator())([]) == Valid([])

    l_validator = ListValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
        preprocessors=[RemoveLast()],
    )
    assert l_validator([10.1, 7.7, 2.2, 5, 0.0]) == Invalid(
        l_validator, [10.1, 7.7, 2.2, 5], PredicateErrs([MaxItems(3)])
    )

    n_v = ListValidator(BasicNoneValidator())

    assert n_v([None, None]) == Valid([None, None])

    assert n_v([None, 1]) == Invalid(
        n_v,
        [None, 1],
        IndexErrs({1: Invalid(n_v.item_validator, 1, TypeErr(type(None)))}),
    )


@pytest.mark.asyncio
async def test_list_async() -> None:
    l_f_v = ListValidator(FloatValidator())
    assert await l_f_v.validate_async("a string") == Invalid(
        l_f_v, "a string", TypeErr(list)
    )

    assert await l_f_v.validate_async([5.5, "something else"]) == Invalid(
        l_f_v,
        [5.5, "something else"],
        IndexErrs(
            {1: Invalid(l_f_v.item_validator, "something else", TypeErr(float))},
        ),
    )

    assert await ListValidator(FloatValidator()).validate_async([5.5, 10.1]) == Valid(
        [5.5, 10.1]
    )

    assert await ListValidator(FloatValidator()).validate_async([]) == Valid([])

    l_validator = ListValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    )
    assert await l_validator.validate_async([10.1, 7.7, 2.2, 5]) == Invalid(
        l_validator, [10.1, 7.7, 2.2, 5], PredicateErrs([MaxItems(3)])
    )

    n_v = ListValidator(BasicNoneValidator())

    assert await n_v.validate_async([None, None]) == Valid([None, None])

    assert await n_v.validate_async([None, 1]) == Invalid(
        n_v,
        [None, 1],
        IndexErrs({1: Invalid(n_v.item_validator, 1, TypeErr(type(None)))}),
    )


@dataclass
class SomeAsyncListCheck(PredicateAsync[List[Any]]):
    async def validate_async(self, val: List[Any]) -> bool:
        await asyncio.sleep(0.001)
        return len(val) == 1


@pytest.mark.asyncio
async def test_list_validator_with_async_predicate_validator() -> None:
    l_validator = ListValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    )
    assert await l_validator.validate_async([]) == Invalid(
        l_validator, [], PredicateErrs([SomeAsyncListCheck()])
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
        l_validator, [1, 1], PredicateErrs([MaxItems(1)])
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


def test_list_repr() -> None:
    s = ListValidator(StringValidator())
    assert repr(s) == "ListValidator(StringValidator())"

    s_len = ListValidator(StringValidator(MinLength(1), MaxLength(5)))
    assert (
        repr(s_len)
        == "ListValidator(StringValidator(MinLength(length=1), MaxLength(length=5)))"
    )

    s_all = ListValidator(
        IntValidator(),
        predicates=[MinItems(5)],
        predicates_async=[SomeAsyncListCheck()],
        preprocessors=[RemoveLast()],
    )

    assert (
        repr(s_all)
        == "ListValidator(IntValidator(), predicates=[MinItems(item_count=5)], "
        "predicates_async=[SomeAsyncListCheck()], preprocessors=[RemoveLast()])"
    )
