import asyncio
from dataclasses import dataclass
from typing import Any, Set

import pytest

from koda_validate import (
    IntValidator,
    MaxItems,
    MaxLength,
    MinItems,
    MinLength,
    StringValidator,
    Valid,
)
from koda_validate.base import (
    Invalid,
    PredicateAsync,
    PredicateErrs,
    Processor,
    SetErrs,
    TypeErr,
)
from koda_validate.set import SetValidator
from tests.utils import BasicNoneValidator


@dataclass
class Add1ToSet(Processor[Set[Any]]):
    def __call__(self, val: Set[Any]) -> Set[Any]:
        val.add(1)
        return val


@dataclass
class AsyncSetPred(PredicateAsync[Set[Any]]):
    async def validate_async(self, val: Set[Any]) -> bool:
        await asyncio.sleep(0.001)
        return False


def test_set_validator() -> None:
    set_str_v = SetValidator(StringValidator())
    assert set_str_v(set()) == Valid(set())
    assert set_str_v(None) == Invalid(set_str_v, None, TypeErr(set))
    assert set_str_v({"cool", "neat"}) == Valid({"cool", "neat"})
    assert set_str_v({"bad", 1}) == Invalid(
        set_str_v,
        {"bad", 1},
        SetErrs([Invalid(set_str_v.item_validator, 1, TypeErr(str))]),
    )

    set_int_v_2 = SetValidator(
        IntValidator(), predicates=[MaxItems(2)], preprocessors=[Add1ToSet()]
    )

    assert set_int_v_2({0}) == Valid({0, 1})
    assert set_int_v_2({0, 2}) == Invalid(
        set_int_v_2, {0, 1, 2}, PredicateErrs([MaxItems(2)])
    )

    set_none_v = SetValidator(BasicNoneValidator())

    assert set_none_v({None}) == Valid({None})
    assert set_none_v({1}) == Invalid(
        set_none_v,
        {1},
        SetErrs([Invalid(set_none_v.item_validator, 1, TypeErr(type(None)))]),
    )

    set_async_v = SetValidator(IntValidator(), predicates_async=[AsyncSetPred()])
    with pytest.raises(AssertionError):
        set_async_v({1, 2, 3})


@pytest.mark.asyncio
async def test_set_validator_async() -> None:
    set_str_v = SetValidator(StringValidator())
    assert await set_str_v.validate_async(set()) == Valid(set())
    assert await set_str_v.validate_async(None) == Invalid(set_str_v, None, TypeErr(set))
    assert await set_str_v.validate_async({"cool", "neat"}) == Valid({"cool", "neat"})
    assert await set_str_v.validate_async({"bad", 1}) == Invalid(
        set_str_v,
        {"bad", 1},
        SetErrs([Invalid(set_str_v.item_validator, 1, TypeErr(str))]),
    )

    set_int_v_2 = SetValidator(
        IntValidator(), predicates=[MaxItems(2)], preprocessors=[Add1ToSet()]
    )

    assert await set_int_v_2.validate_async({0}) == Valid({0, 1})
    assert await set_int_v_2.validate_async({0, 2}) == Invalid(
        set_int_v_2, {0, 1, 2}, PredicateErrs([MaxItems(2)])
    )

    set_none_v = SetValidator(BasicNoneValidator())

    assert await set_none_v.validate_async({None}) == Valid({None})
    assert await set_none_v.validate_async({1}) == Invalid(
        set_none_v,
        {1},
        SetErrs([Invalid(set_none_v.item_validator, 1, TypeErr(type(None)))]),
    )

    set_async_v = SetValidator(IntValidator(), predicates_async=[AsyncSetPred()])
    assert await set_async_v.validate_async({1, 2, 3}) == Invalid(
        set_async_v, {1, 2, 3}, PredicateErrs([AsyncSetPred()])
    )


def test_set_repr() -> None:
    s = SetValidator(StringValidator())
    assert repr(s) == "SetValidator(StringValidator())"

    s_len = SetValidator(StringValidator(MinLength(1), MaxLength(5)))
    assert (
        repr(s_len)
        == "SetValidator(StringValidator(MinLength(length=1), MaxLength(length=5)))"
    )

    s_all = SetValidator(
        IntValidator(),
        predicates=[MinItems(5)],
        predicates_async=[AsyncSetPred()],
        preprocessors=[Add1ToSet()],
    )

    assert (
        repr(s_all)
        == "SetValidator(IntValidator(), predicates=[MinItems(item_count=5)], "
        "predicates_async=[AsyncSetPred()], preprocessors=[Add1ToSet()])"
    )


def test_list_validator_equivalence() -> None:
    s_1 = SetValidator(StringValidator())
    s_2 = SetValidator(StringValidator())
    assert s_1 == s_2
    s_3 = SetValidator(IntValidator())
    assert s_2 != s_3

    s_pred_1 = SetValidator(StringValidator(), predicates=[MaxItems(1)])
    assert s_pred_1 != s_1
    s_pred_2 = SetValidator(StringValidator(), predicates=[MaxItems(1)])
    assert s_pred_2 == s_pred_1

    s_pred_async_1 = SetValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[AsyncSetPred()],
    )
    assert s_pred_async_1 != s_pred_1
    s_pred_async_2 = SetValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[AsyncSetPred()],
    )
    assert s_pred_async_1 == s_pred_async_2

    s_preproc_1 = SetValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[AsyncSetPred()],
        preprocessors=[Add1ToSet()],
    )
    assert s_preproc_1 != s_pred_async_1

    s_preproc_2 = SetValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[AsyncSetPred()],
        preprocessors=[Add1ToSet()],
    )
    assert s_preproc_1 == s_preproc_2
