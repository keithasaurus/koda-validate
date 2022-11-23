import asyncio
import re
from dataclasses import dataclass

import pytest

from koda_validate import EmailPredicate, PredicateAsync, RegexPredicate
from koda_validate._generics import A
from koda_validate.base import TypeErr
from koda_validate.string import (
    BLANK_STRING_MSG,
    MaxLength,
    MinLength,
    NotBlank,
    StringValidator,
    lower_case,
    not_blank,
    strip,
    upper_case,
)
from koda_validate.validated import Invalid, Valid


def test_strip() -> None:
    assert strip(" x ") == "x"
    assert strip("ok") == "ok"


def test_upper_case() -> None:
    assert upper_case("AbCdE") == "ABCDE"


def test_lower_case() -> None:
    assert lower_case("ZyXwV") == "zyxwv"


def test_string_validator() -> None:
    assert StringValidator()(False) == Invalid(TypeErr(str, "expected a string"))

    assert StringValidator()("abc") == Valid("abc")

    assert StringValidator(MaxLength(3))("something") == Invalid([MaxLength(3)])

    min_len_3_not_blank_validator = StringValidator(MinLength(3), NotBlank())

    assert min_len_3_not_blank_validator("") == Invalid([MinLength(3), not_blank])

    assert min_len_3_not_blank_validator("   ") == Invalid([not_blank])

    assert min_len_3_not_blank_validator("something") == Valid("something")

    assert StringValidator(not_blank, preprocessors=[strip])(" strip me! ") == Valid(
        "strip me!"
    )


def test_max_string_length() -> None:
    assert MaxLength(0)("") is True

    assert MaxLength(5)("abc") is True

    assert MaxLength(5)("something") is False
    assert MaxLength(5).err_message == "maximum allowed length is 5"


def test_min_string_length() -> None:
    assert MinLength(0)("") is True

    assert MinLength(3)("abc") is True

    assert MinLength(3)("zz") is False
    assert MinLength(3).err_message == "minimum allowed length is 3"


def test_regex_validator() -> None:
    v = RegexPredicate(re.compile(r".+"))
    assert v("something") is True
    assert v("") is False
    assert v.err_message == "must match pattern .+"


def test_not_blank() -> None:
    assert NotBlank()("a") is True
    assert NotBlank()("") is False
    assert NotBlank().err_message == BLANK_STRING_MSG
    assert NotBlank()(" ") is False
    assert NotBlank()("\t") is False
    assert NotBlank()("\n") is False


def test_email() -> None:
    assert EmailPredicate()("notanemail") is False
    assert EmailPredicate()("a@b.com") is True
    assert EmailPredicate().err_message == "expected a valid email address"


@pytest.mark.asyncio
async def test_validate_fake_db_async() -> None:
    test_valid_username = "valid_username"

    hit = []

    @dataclass
    class CheckUsername(PredicateAsync[str]):
        def __init__(self) -> None:
            self.err_message = "not in db!"

        async def validate_async(self, val: str) -> bool:
            hit.append("ok")
            # fake db call
            await asyncio.sleep(0.001)
            return val == test_valid_username

    result = await StringValidator(predicates_async=[CheckUsername()]).validate_async(
        "bad username"
    )
    assert hit == ["ok"]
    assert result == Invalid([CheckUsername()])
    assert await StringValidator().validate_async(5) == Invalid(
        TypeErr(str, "expected a string")
    )


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    str_validator = StringValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        str_validator(5)
