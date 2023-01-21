import asyncio
from dataclasses import dataclass
from typing import Any, List

import pytest
from koda import Just, Maybe, nothing

from koda_validate import (
    IndexErrs,
    IntValidator,
    Invalid,
    MaxLength,
    MinLength,
    PredicateAsync,
    PredicateErrs,
    StringValidator,
    TypeErr,
    Valid,
)
from koda_validate._generics import A
from koda_validate.base import Coercer
from koda_validate.float import FloatValidator
from koda_validate.generic import MaxItems, Min, MinItems
from koda_validate.list import ListValidator
from tests.utils import BasicNoneValidator


def test_list_validator() -> None:
    l_f_v = ListValidator(FloatValidator())
    assert l_f_v("a string") == Invalid(TypeErr(list), "a string", l_f_v)

    assert l_f_v([5.5, "something else"]) == Invalid(
        IndexErrs(
            {1: Invalid(TypeErr(float), "something else", l_f_v.item_validator)},
        ),
        [5.5, "something else"],
        l_f_v,
    )

    assert ListValidator(FloatValidator())([5.5, 10.1]) == Valid([5.5, 10.1])

    assert ListValidator(FloatValidator())([]) == Valid([])

    l_validator = ListValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
    )
    assert l_validator([10.1, 7.7, 2.2, 5, 0.0]) == Invalid(
        PredicateErrs([MaxItems(3)]), [10.1, 7.7, 2.2, 5, 0.0], l_validator
    )

    n_v = ListValidator(BasicNoneValidator())

    assert n_v([None, None]) == Valid([None, None])

    assert n_v([None, 1]) == Invalid(
        IndexErrs({1: Invalid(TypeErr(type(None)), 1, n_v.item_validator)}),
        [None, 1],
        n_v,
    )


@pytest.mark.asyncio
async def test_list_async() -> None:
    l_f_v = ListValidator(FloatValidator())
    assert await l_f_v.validate_async("a string") == Invalid(
        TypeErr(list), "a string", l_f_v
    )

    assert await l_f_v.validate_async([5.5, "something else"]) == Invalid(
        IndexErrs(
            {1: Invalid(TypeErr(float), "something else", l_f_v.item_validator)},
        ),
        [5.5, "something else"],
        l_f_v,
    )

    assert await ListValidator(FloatValidator()).validate_async([5.5, 10.1]) == Valid(
        [5.5, 10.1]
    )

    assert await ListValidator(FloatValidator()).validate_async([]) == Valid([])

    l_validator = ListValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    )
    assert await l_validator.validate_async([10.1, 7.7, 2.2, 5]) == Invalid(
        PredicateErrs([MaxItems(3)]), [10.1, 7.7, 2.2, 5], l_validator
    )

    n_v = ListValidator(BasicNoneValidator())

    assert await n_v.validate_async([None, None]) == Valid([None, None])

    assert await n_v.validate_async([None, 1]) == Invalid(
        IndexErrs({1: Invalid(TypeErr(type(None)), 1, n_v.item_validator)}),
        [None, 1],
        n_v,
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
        PredicateErrs([SomeAsyncListCheck()]), [], l_validator
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

    l_validator = ListValidator(
        IntValidator(Min(2), predicates_async=[SomeIntDBCheck()]),
        predicates=[MaxItems(1)],
    )

    assert await l_validator.validate_async([3]) == Valid([3])

    assert await l_validator.validate_async([1, 1]) == Invalid(
        PredicateErrs([MaxItems(1)]), [1, 1], l_validator
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
    )

    assert (
        repr(s_all)
        == "ListValidator(IntValidator(), predicates=[MinItems(item_count=5)], "
        "predicates_async=[SomeAsyncListCheck()])"
    )


def test_list_validator_equivalence() -> None:
    l_1 = ListValidator(StringValidator())
    l_2 = ListValidator(StringValidator())
    assert l_1 == l_2
    l_3 = ListValidator(IntValidator())
    assert l_2 != l_3

    l_pred_1 = ListValidator(StringValidator(), predicates=[MaxItems(1)])
    assert l_pred_1 != l_1
    l_pred_2 = ListValidator(StringValidator(), predicates=[MaxItems(1)])
    assert l_pred_2 == l_pred_1

    l_pred_async_1 = ListValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[SomeAsyncListCheck()],
    )
    assert l_pred_async_1 != l_pred_1
    l_pred_async_2 = ListValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[SomeAsyncListCheck()],
    )
    assert l_pred_async_1 == l_pred_async_2


def test_coerce_to_list() -> None:
    class TupleToList(Coercer[List[Any]]):
        compatible_types = {tuple}

        def __call__(self, val: Any) -> Maybe[List[Any]]:
            if type(val) is tuple:
                return Just(list(val))
            else:
                return nothing

    validator = ListValidator(StringValidator(), coerce=TupleToList())
    assert validator(("ok", "tuple")) == Valid(["ok", "tuple"])
    assert isinstance(validator(["list", "no", "longer", "accepted"]), Invalid)


@pytest.mark.asyncio
async def test_coerce_to_list_async() -> None:
    class TupleToList(Coercer[List[Any]]):
        compatible_types = {tuple}

        def __call__(self, val: Any) -> Maybe[List[Any]]:
            if type(val) is tuple:
                return Just(list(val))
            else:
                return nothing

    validator = ListValidator(StringValidator(), coerce=TupleToList())
    assert await validator.validate_async(("ok", "tuple")) == Valid(["ok", "tuple"])
    assert isinstance(
        await validator.validate_async(["list", "no", "longer", "accepted"]), Invalid
    )
