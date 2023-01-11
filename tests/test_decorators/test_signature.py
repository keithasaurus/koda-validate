import pytest

from koda_validate import IntValidator, Invalid, StringValidator, TypeErr
from koda_validate.decorators.signature import (
    InvalidArgs,
    get_args_fail_msg,
    validate_signature,
)


def test_empty_signature_is_fine() -> None:
    @validate_signature
    def constant():  # type: ignore
        return 5

    assert constant() == 5  # type: ignore[no-untyped-call]


def test_one_arg_simple_scalars() -> None:
    @validate_signature
    def identity_int(x: int) -> int:
        return x

    assert identity_int(123) == 123
    with pytest.raises(InvalidArgs) as exc_info:
        identity_int("abc")  # type: ignore[arg-type]

        assert str(exc_info) == get_args_fail_msg(
            {"x": Invalid(TypeErr(int), "abc", IntValidator())}
        )

    @validate_signature
    def identity_str(x: str) -> str:
        return x

    assert identity_str("abc") == "abc"
    with pytest.raises(InvalidArgs) as exc_info:
        identity_str(123)  # type: ignore[arg-type]

        assert str(exc_info) == get_args_fail_msg(
            {"x": Invalid(TypeErr(str), 123, IntValidator())}
        )


def test_catches_bad_return_type() -> None:
    @validate_signature
    def some_func() -> str:
        return 5  # type: ignore[return-value]

    with pytest.raises(InvalidArgs) as exc_info:
        assert some_func()

        assert str(exc_info) == get_args_fail_msg(
            {"_RETURN_VALUE_": Invalid(TypeErr(str), 5, StringValidator())}
        )


def test_ignores_return_type() -> None:
    @validate_signature(ignore_return=True)
    def some_func() -> str:
        return 5  # type: ignore[return-value]

    assert some_func() == 5  # type: ignore[comparison-overlap]


def test_multiple_args_custom_type() -> None:
    class Person:
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    @validate_signature
    def fn(a: int, b: Person) -> None:
        return None

    assert fn(5, Person("abc", 123)) is None


def test_handles_kwargs() -> None:
    @validate_signature
    def some_func(**kwargs: str) -> str:
        return "neat"

    assert some_func(x="1") == "neat"

    assert some_func() == "neat"

    with pytest.raises(InvalidArgs):
        some_func(x=1)
