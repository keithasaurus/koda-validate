from decimal import Decimal

import pytest

from koda_validate import (
    Choices,
    EqualsValidator,
    Invalid,
    Max,
    Min,
    MultipleOf,
    Valid,
    strip,
)
from koda_validate.base import PredicateErrs, TypeErr
from koda_validate.generic import (
    EqualTo,
    ExactItemCount,
    MaxItems,
    MinItems,
    always_valid,
    unique_items,
)


def test_equals_validator() -> None:
    equals_5_validator = EqualsValidator(5)
    assert equals_5_validator(5) == Valid(5)
    assert equals_5_validator(4) == Invalid(
        equals_5_validator, PredicateErrs([EqualTo(5)])
    )
    eq_ok_v = EqualsValidator("ok")
    assert eq_ok_v("ok") == Valid("ok")
    assert EqualsValidator("ok", preprocessors=[strip])(" ok ") == Valid("ok")
    assert eq_ok_v("not ok") == Invalid(eq_ok_v, PredicateErrs([EqualTo("ok")]))
    assert EqualsValidator(Decimal("1.25"))(Decimal("1.25")) == Valid(Decimal("1.25"))
    equals_dec_11 = EqualsValidator(Decimal("1.1"))
    assert equals_dec_11(Decimal("5")) == Invalid(
        equals_dec_11, PredicateErrs([EqualTo(Decimal("1.1"))])
    )
    e_f_v = EqualsValidator(4.4)
    assert e_f_v("5.5") == Invalid(e_f_v, TypeErr(float))
    equals_true_validator = EqualsValidator(True)

    assert equals_true_validator(True) == Valid(True)
    assert EqualsValidator(False)(False) == Valid(False)
    assert equals_true_validator(False) == Invalid(
        equals_true_validator, PredicateErrs([EqualTo(True)])
    )
    e_i_v = EqualsValidator(4)
    assert e_i_v(4.0) == Invalid(e_i_v, TypeErr(int))


@pytest.mark.asyncio
async def test_equals_validator_async() -> None:
    equals_5_validator = EqualsValidator(5)
    assert await equals_5_validator.validate_async(5) == Valid(5)
    assert await equals_5_validator.validate_async(4) == Invalid(
        equals_5_validator, PredicateErrs([EqualTo(5)])
    )
    assert await EqualsValidator("ok").validate_async("ok") == Valid("ok")
    assert await EqualsValidator("ok", preprocessors=[strip]).validate_async(
        " ok "
    ) == Valid("ok")
    eq_ok_v = EqualsValidator("ok")
    assert await eq_ok_v.validate_async("not ok") == Invalid(
        eq_ok_v, PredicateErrs([EqualTo("ok")])
    )
    assert await EqualsValidator(Decimal("1.25")).validate_async(
        Decimal("1.25")
    ) == Valid(Decimal("1.25"))
    equals_dec_11 = EqualsValidator(Decimal("1.1"))
    assert await equals_dec_11.validate_async(Decimal("5")) == Invalid(
        equals_dec_11, PredicateErrs([EqualTo(Decimal("1.1"))])
    )
    e_f_v = EqualsValidator(4.4)
    assert await EqualsValidator(4.4).validate_async("5.5") == Invalid(
        e_f_v, TypeErr(float)
    )
    equals_true_validator = EqualsValidator(True)
    assert await equals_true_validator.validate_async(True) == Valid(True)
    assert await EqualsValidator(False).validate_async(False) == Valid(False)
    assert await equals_true_validator.validate_async(False) == Invalid(
        equals_true_validator, PredicateErrs([EqualTo(True)])
    )
    e_i_v = EqualsValidator(4)
    assert await e_i_v.validate_async(4.0) == Invalid(e_i_v, TypeErr(int))


def test_choices() -> None:
    validator = Choices({"a", "bc", "def"})

    assert validator("bc") is True
    assert validator("not present") is False


def test_multiple_of() -> None:
    assert MultipleOf(5)(10) is True
    assert MultipleOf(5)(11) is False
    assert MultipleOf(2.2)(4.40) is True


def test_min() -> None:
    assert Min(5)(5) is True
    assert Min(5)(4) is False
    assert Min(5, exclusive_minimum=True)(6) is True
    assert Min(5, exclusive_minimum=True)(5) is False


def test_max() -> None:
    assert Max(5)(5) is True
    assert Max(4, exclusive_maximum=True)(3) is True
    assert Max(5)(6) is False
    assert Max(5, exclusive_maximum=True)(5) is False


def test_always_valid() -> None:
    assert always_valid(5) == Valid(5)
    assert always_valid([1, 2, 3]) == Valid([1, 2, 3])
    assert always_valid(False) == Valid(False)


@pytest.mark.asyncio
async def test_always_valid_async() -> None:
    assert always_valid(5) == Valid(5)
    assert always_valid([1, 2, 3]) == Valid([1, 2, 3])
    assert always_valid(False) == Valid(False)


def test_unique_items() -> None:
    assert unique_items([1, 2, 3]) is True
    assert unique_items([1, 1]) is False
    assert unique_items([1, [], []]) is False
    assert unique_items([[], [1], [2]]) is True
    assert unique_items([{"something": {"a": 1}}, {"something": {"a": 1}}]) is False


def test_exact_item_count() -> None:
    assert ExactItemCount(2)([1, 2]) is True
    assert ExactItemCount(1)([1, 2]) is False
    assert ExactItemCount(2)([1]) is False


def test_max_items() -> None:
    assert MaxItems(0)([]) is True

    assert MaxItems(5)([1, 2, 3]) is True

    assert MaxItems(5)(["a", "b", "c", "d", "e", "fghij"]) is False


def test_min_items() -> None:
    assert MinItems(0)([]) is True

    assert MinItems(3)([1, 2, 3]) is True
    assert MinItems(3)([1, 2]) is False
