from typing import NotRequired, Required, TypedDict

from koda_validate import IntValidator, StringValidator, TypedDictValidator


def test_not_required_typeddict_annotation() -> None:
    class A(TypedDict):
        x: NotRequired[str]

    v = TypedDictValidator(A)
    assert v.schema["x"] == StringValidator()


def test_required_typeddict_annotation() -> None:
    class A(TypedDict):
        x: Required[int]

    v = TypedDictValidator(A)
    assert v.schema["x"] == IntValidator()
