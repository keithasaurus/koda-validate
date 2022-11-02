from dataclasses import dataclass

from koda import Just, Maybe, Ok, nothing

from koda_validate import IntValidator, Lazy
from koda_validate.dictionary import DictValidator, KeyNotRequired


def test_lazy() -> None:
    @dataclass
    class TestNonEmptyList:
        val: int
        next: Maybe["TestNonEmptyList"]  # noqa: F821

    def recur_tnel() -> DictValidator[TestNonEmptyList]:
        return nel_validator

    nel_validator: DictValidator[TestNonEmptyList] = DictValidator(
        into=TestNonEmptyList,
        keys=(("val", IntValidator()), ("next", KeyNotRequired(Lazy(recur_tnel)))),
    )

    assert nel_validator({"val": 5, "next": {"val": 6, "next": {"val": 7}}}) == Ok(
        TestNonEmptyList(5, Just(TestNonEmptyList(6, Just(TestNonEmptyList(7, nothing)))))
    )
