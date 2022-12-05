import asyncio
import re
from dataclasses import dataclass

import pytest

from koda_validate import EmailPredicate, Invalid, PredicateAsync, RegexPredicate, Valid
from koda_validate._generics import A
from koda_validate.base import PredicateErrs, TypeErr
from koda_validate.string import (
    MaxLength,
    MinLength,
    NotBlank,
    StringValidator,
    lower_case,
    not_blank,
    strip,
    upper_case,
)


def test_strip() -> None:
    assert strip(" x ") == "x"
    assert strip("ok") == "ok"


def test_upper_case() -> None:
    assert upper_case("AbCdE") == "ABCDE"


def test_lower_case() -> None:
    assert lower_case("ZyXwV") == "zyxwv"


def test_string_validator() -> None:
    s_v = StringValidator()
    assert s_v(False) == Invalid(s_v, False, TypeErr(str))

    assert StringValidator()("abc") == Valid("abc")

    s_min_3_v = StringValidator(MaxLength(3))
    assert s_min_3_v("something") == Invalid(
        s_min_3_v, "something", PredicateErrs([MaxLength(3)])
    )

    min_len_3_not_blank_validator = StringValidator(MinLength(3), NotBlank())

    assert min_len_3_not_blank_validator("") == Invalid(
        min_len_3_not_blank_validator, "", PredicateErrs([MinLength(3), not_blank])
    )

    assert min_len_3_not_blank_validator("   ") == Invalid(
        min_len_3_not_blank_validator, "   ", PredicateErrs([not_blank])
    )

    assert min_len_3_not_blank_validator("something") == Valid("something")

    assert StringValidator(not_blank, preprocessors=[strip])(" strip me! ") == Valid(
        "strip me!"
    )


def test_max_string_length() -> None:
    assert MaxLength(0)("") is True

    assert MaxLength(5)("abc") is True

    assert MaxLength(5)("something") is False


def test_min_string_length() -> None:
    assert MinLength(0)("") is True

    assert MinLength(3)("abc") is True

    assert MinLength(3)("zz") is False


def test_regex_validator() -> None:
    v = RegexPredicate(re.compile(r".+"))
    assert v("something") is True
    assert v("") is False


def test_not_blank() -> None:
    assert NotBlank()("a") is True
    assert NotBlank()("") is False
    assert NotBlank()(" ") is False
    assert NotBlank()("\t") is False
    assert NotBlank()("\n") is False


def test_email() -> None:
    assert EmailPredicate()("notanemail") is False
    assert EmailPredicate()("a@b.com") is True


@pytest.mark.asyncio
async def test_validate_fake_db_async() -> None:
    test_valid_username = "valid_username"

    hit = []

    @dataclass
    class CheckUsername(PredicateAsync[str]):
        async def validate_async(self, val: str) -> bool:
            hit.append("ok")
            # fake db call
            await asyncio.sleep(0.001)
            return val == test_valid_username

    validator = StringValidator(predicates_async=[CheckUsername()])
    result = await validator.validate_async("bad username")
    assert hit == ["ok"]
    assert result == Invalid(validator, "bad username", PredicateErrs([CheckUsername()]))
    s_v = StringValidator()
    assert await s_v.validate_async(5) == Invalid(s_v, 5, TypeErr(str))


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    str_validator = StringValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        str_validator(5)


@dataclass
class StrAsyncPred(PredicateAsync[str]):
    async def validate_async(self, val: str) -> bool:
        return True


def test_repr() -> None:
    s = StringValidator()
    assert repr(s) == "StringValidator()"

    s_len = StringValidator(MinLength(1), MaxLength(5))
    assert repr(s_len) == "StringValidator(MinLength(length=1), MaxLength(length=5))"

    s_all = StringValidator(
        MinLength(1), predicates_async=[StrAsyncPred()], preprocessors=[strip]
    )

    assert (
        repr(s_all) == "StringValidator(MinLength(length=1), "
        "predicates_async=[StrAsyncPred()], preprocessors=[Strip()])"
    )


def test_equivalence() -> None:
    s_1 = StringValidator()
    s_2 = StringValidator()
    assert s_1 == s_2

    s_pred_1 = StringValidator(MaxLength(1))
    assert s_pred_1 != s_1
    s_pred_2 = StringValidator(MaxLength(1))
    assert s_pred_2 == s_pred_1

    s_pred_async_1 = StringValidator(MaxLength(1), predicates_async=[StrAsyncPred()])
    assert s_pred_async_1 != s_pred_1
    s_pred_async_2 = StringValidator(MaxLength(1), predicates_async=[StrAsyncPred()])
    assert s_pred_async_1 == s_pred_async_2

    s_preproc_1 = StringValidator(
        MaxLength(1), predicates_async=[StrAsyncPred()], preprocessors=[strip]
    )
    assert s_preproc_1 != s_pred_async_1

    s_preproc_2 = StringValidator(
        MaxLength(1), predicates_async=[StrAsyncPred()], preprocessors=[strip]
    )
    assert s_preproc_1 == s_preproc_2
