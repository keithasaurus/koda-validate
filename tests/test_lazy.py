from dataclasses import dataclass

from koda import Just, Maybe, Ok, nothing

from koda_validate import IntValidator, Lazy, key, maybe_key
from koda_validate.dictionary import Dict2KeysValidator


def test_lazy() -> None:
    @dataclass
    class TestNonEmptyList:
        val: int
        next: Maybe["TestNonEmptyList"]  # noqa: F821

    def recur_tnel() -> Dict2KeysValidator[
        int, Maybe[TestNonEmptyList], TestNonEmptyList
    ]:
        return nel_validator

    nel_validator: Dict2KeysValidator[
        int, Maybe[TestNonEmptyList], TestNonEmptyList
    ] = Dict2KeysValidator(
        TestNonEmptyList,
        key("val", IntValidator()),
        maybe_key("next", Lazy(recur_tnel)),
    )

    assert nel_validator({"val": 5, "next": {"val": 6, "next": {"val": 7}}}) == Ok(
        TestNonEmptyList(5, Just(TestNonEmptyList(6, Just(TestNonEmptyList(7, nothing)))))
    )
