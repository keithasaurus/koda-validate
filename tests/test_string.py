import asyncio
import re

import pytest

from koda_validate import EmailPredicate, PredicateAsync, RegexPredicate, Serializable
from koda_validate._generics import A
from koda_validate.errors import (
    MaxStrLenErr,
    MinStrLenErr,
    TypeErr,
    ValidationErr,
    ValueErr,
)
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
    assert StringValidator()(False) == Invalid([TypeErr(str, "expected a string")])

    assert StringValidator()("abc") == Valid("abc")

    assert StringValidator(MaxLength(3))("something") == Invalid(
        [
            MaxStrLenErr(
                default_message="maximum allowed length is 3",
                limit=3,
            )
        ]
    )

    min_len_3_not_blank_validator = StringValidator(MinLength(3), NotBlank())

    assert min_len_3_not_blank_validator("") == Invalid(
        [MinStrLenErr("minimum allowed length is 3", 3), "cannot be blank"]
    )

    assert min_len_3_not_blank_validator("   ") == Invalid(["cannot be blank"])

    assert min_len_3_not_blank_validator("something") == Valid("something")

    assert StringValidator(not_blank, preprocessors=[strip])(" strip me! ") == Valid(
        "strip me!"
    )


def test_max_string_length() -> None:
    assert MaxLength(0)("") == Valid("")

    assert MaxLength(5)("abc") == Valid("abc")

    assert MaxLength(5)("something") == Invalid(
        MaxStrLenErr("maximum allowed length is 5", 5)
    )


def test_min_string_length() -> None:
    assert MinLength(0)("") == Valid("")

    assert MinLength(3)("abc") == Valid("abc")

    assert MinLength(3)("zz") == Invalid(MinStrLenErr("minimum allowed length is 3", 3))


def test_regex_validator() -> None:
    assert RegexPredicate(re.compile(r".+"))("something") == Valid("something")
    assert RegexPredicate(re.compile(r".+"))("") == Invalid("must match pattern .+")


def test_not_blank() -> None:
    assert NotBlank()("a") == Valid("a")
    assert NotBlank()("") == Invalid(BLANK_STRING_MSG)
    assert NotBlank()(" ") == Invalid(BLANK_STRING_MSG)
    assert NotBlank()("\t") == Invalid(BLANK_STRING_MSG)
    assert NotBlank()("\n") == Invalid(BLANK_STRING_MSG)


def test_email() -> None:
    assert EmailPredicate()("notanemail") == Invalid("expected a valid email address")
    assert EmailPredicate()("a@b.com") == Valid("a@b.com")


@pytest.mark.asyncio
async def test_validate_fake_db_async() -> None:
    test_valid_username = "valid_username"

    hit = []

    class CheckUsername(PredicateAsync[str, ValidationErr]):
        async def is_valid_async(self, val: str) -> bool:
            hit.append("ok")
            # fake db call
            await asyncio.sleep(0.001)
            return val == test_valid_username

        async def err_async(self, val: str) -> ValidationErr:
            return ValueErr("not in db!")

    result = await StringValidator(predicates_async=[CheckUsername()]).validate_async(
        "bad username"
    )
    assert hit == ["ok"]
    assert result == Invalid([ValueErr("not in db!")])
    assert await StringValidator().validate_async(5) == Invalid(
        [TypeErr(str, "expected a string")]
    )


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    class AsyncWait(PredicateAsync[A, Serializable]):
        async def is_valid_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

        async def err_async(self, val: A) -> Serializable:
            return "should always succeed??"

    str_validator = StringValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        str_validator(5)
