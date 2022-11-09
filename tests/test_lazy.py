from dataclasses import dataclass

import pytest
from koda import Just, Maybe, nothing

from koda_validate import IntValidator, Lazy
from koda_validate.dictionary import KeyNotRequired, RecordValidator
from koda_validate.validated import Valid


def test_lazy() -> None:
    @dataclass
    class TestNonEmptyList:
        val: int
        next: Maybe["TestNonEmptyList"]  # noqa: F821

    def recur_tnel() -> RecordValidator[TestNonEmptyList]:
        return nel_validator

    nel_validator: RecordValidator[TestNonEmptyList] = RecordValidator(
        into=TestNonEmptyList,
        keys=(("val", IntValidator()), ("next", KeyNotRequired(Lazy(recur_tnel)))),
    )

    assert nel_validator({"val": 5, "next": {"val": 6, "next": {"val": 7}}}) == Valid(
        TestNonEmptyList(5, Just(TestNonEmptyList(6, Just(TestNonEmptyList(7, nothing)))))
    )


@pytest.mark.asyncio
async def test_lazy_async() -> None:
    @dataclass
    class TestNonEmptyList:
        val: int
        next: Maybe["TestNonEmptyList"]  # noqa: F821

    def recur_tnel() -> RecordValidator[TestNonEmptyList]:
        return nel_validator

    nel_validator: RecordValidator[TestNonEmptyList] = RecordValidator(
        into=TestNonEmptyList,
        keys=(("val", IntValidator()), ("next", KeyNotRequired(Lazy(recur_tnel)))),
    )

    assert await nel_validator.validate_async(
        {"val": 5, "next": {"val": 6, "next": {"val": 7}}}
    ) == Valid(
        TestNonEmptyList(5, Just(TestNonEmptyList(6, Just(TestNonEmptyList(7, nothing)))))
    )
