import re

from koda import Err, Ok

from koda_validate import EmailPredicate, RegexPredicate
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


def test_strip() -> None:
    assert strip(" x ") == "x"
    assert strip("ok") == "ok"


def test_upper_case() -> None:
    assert upper_case("AbCdE") == "ABCDE"


def test_lower_case() -> None:
    assert lower_case("ZyXwV") == "zyxwv"


def test_string_validator() -> None:
    assert StringValidator()(False) == Err(["expected a string"])

    assert StringValidator()("abc") == Ok("abc")

    assert StringValidator(MaxLength(3))("something") == Err(
        ["maximum allowed length is 3"]
    )

    min_len_3_not_blank_validator = StringValidator(MinLength(3), NotBlank())

    assert min_len_3_not_blank_validator("") == Err(
        ["minimum allowed length is 3", "cannot be blank"]
    )

    assert min_len_3_not_blank_validator("   ") == Err(["cannot be blank"])

    assert min_len_3_not_blank_validator("something") == Ok("something")

    assert StringValidator(not_blank, preprocessors=[strip])(" strip me! ") == Ok(
        "strip me!"
    )


def test_max_string_length() -> None:
    assert MaxLength(0)("") == Ok("")

    assert MaxLength(5)("abc") == Ok("abc")

    assert MaxLength(5)("something") == Err("maximum allowed length is 5")


def test_min_string_length() -> None:
    assert MinLength(0)("") == Ok("")

    assert MinLength(3)("abc") == Ok("abc")

    assert MinLength(3)("zz") == Err("minimum allowed length is 3")


def test_regex_validator() -> None:
    assert RegexPredicate(re.compile(r".+"))("something") == Ok("something")
    assert RegexPredicate(re.compile(r".+"))("") == Err("must match pattern .+")


def test_not_blank() -> None:
    assert NotBlank()("a") == Ok("a")
    assert NotBlank()("") == Err(BLANK_STRING_MSG)
    assert NotBlank()(" ") == Err(BLANK_STRING_MSG)
    assert NotBlank()("\t") == Err(BLANK_STRING_MSG)
    assert NotBlank()("\n") == Err(BLANK_STRING_MSG)


def test_email() -> None:
    assert EmailPredicate()("notanemail") == Err("expected a valid email address")
    assert EmailPredicate()("a@b.com") == Ok("a@b.com")

    custom_regex_validator = EmailPredicate(re.compile(r"[a-z.]+@somecompany\.com"))
    assert custom_regex_validator("a.b@somecompany.com") == Ok("a.b@somecompany.com")
    assert custom_regex_validator("a.b@example.com") == Err(
        "expected a valid email address"
    )
