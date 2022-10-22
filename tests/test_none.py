from koda import Err, Ok

from koda_validate.none import none_validator


def test_null() -> None:
    assert none_validator("a string") == Err(["expected null"])

    assert none_validator(None) == Ok(None)

    assert none_validator(False) == Err(["expected null"])
