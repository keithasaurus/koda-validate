import pytest

from koda_validate import (
    BoolValidator,
    DictValidatorAny,
    ExtraKeysErr,
    FloatValidator,
    IndexErrs,
    IntValidator,
    Invalid,
    KeyErrs,
    KeyValErrs,
    ListValidator,
    MapErr,
    MapValidator,
    Min,
    MultipleOf,
    PredicateErrs,
    StringValidator,
    TypeErr,
)
from koda_validate.decorators.signature import (
    INVALID_ARGS_MESSAGE_HEADER,
    InvalidArgsError,
    InvalidReturnError,
    get_arg_fail_message,
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
    with pytest.raises(InvalidArgsError) as exc_info:
        identity_int("abc")  # type: ignore[arg-type]

    result = str(exc_info.value)
    expected = INVALID_ARGS_MESSAGE_HEADER + get_args_fail_msg(
        {"x": Invalid(TypeErr(int), "abc", IntValidator())}
    )
    assert result == expected

    @validate_signature
    def identity_str(x: str) -> str:
        return x

    assert identity_str("abc") == "abc"
    with pytest.raises(InvalidArgsError) as exc_info:
        identity_str(123)  # type: ignore[arg-type]

    assert str(exc_info.value) == INVALID_ARGS_MESSAGE_HEADER + get_args_fail_msg(
        {"x": Invalid(TypeErr(str), 123, IntValidator())}
    )


def test_catches_bad_return_type() -> None:
    @validate_signature
    def some_func() -> str:
        return 5  # type: ignore[return-value]

    with pytest.raises(InvalidReturnError) as exc_info:
        assert some_func()

    assert str(exc_info.value) == get_arg_fail_message(
        Invalid(TypeErr(str), 5, StringValidator())
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

    with pytest.raises(InvalidArgsError):
        some_func(x=1)  # type: ignore[arg-type]


def test_handles_var_args() -> None:
    @validate_signature
    def some_func(a: str, *b: int) -> str:
        return f"{a}, {b}"

    assert some_func("empty") == "empty, ()"

    assert some_func("ok", 1, 2, 3) == "ok, (1, 2, 3)"

    with pytest.raises(InvalidArgsError):
        some_func("bad", 1, "hmm")  # type: ignore[arg-type]


def test_succeeds_for_zero_errors_on_all_kinds_of_args() -> None:
    @validate_signature
    def some_func(
        aa: int, /, a: int, *b: int, c: float, d: bool = False, **kwargs: int
    ) -> str:
        return f"{aa} {a} {b} {c} {d} {kwargs}"

    assert some_func(0, 1, 2, 3, 4, c=2.2, x=10) == "0 1 (2, 3, 4) 2.2 False {'x': 10}"


def test_fails_for_all_failures() -> None:
    @validate_signature
    def some_func(
        aa: int, /, a: int, *b: int, c: float, d: bool = False, **kwargs: int
    ) -> str:
        return f"{a} {b} {c} {d} {kwargs}"

    with pytest.raises(InvalidArgsError) as exc_info:
        some_func("zz", "b", "c", "d", "e", c="x", d="hmm", x=None)  # type: ignore[arg-type]  # noqa: E501

    assert exc_info.value.errs == {
        "aa": Invalid(
            err_type=TypeErr(expected_type=int), value="zz", validator=IntValidator()
        ),
        "a": Invalid(
            err_type=TypeErr(expected_type=int), value="b", validator=IntValidator()
        ),
        "b": Invalid(
            err_type=IndexErrs(
                indexes={
                    0: Invalid(
                        err_type=TypeErr(expected_type=int),
                        value="c",
                        validator=IntValidator(),
                    ),
                    1: Invalid(
                        err_type=TypeErr(expected_type=int),
                        value="d",
                        validator=IntValidator(),
                    ),
                    2: Invalid(
                        err_type=TypeErr(expected_type=int),
                        value="e",
                        validator=IntValidator(),
                    ),
                }
            ),
            value=("c", "d", "e"),
            validator=IntValidator(),
        ),
        "c": Invalid(
            err_type=TypeErr(expected_type=float), value="x", validator=FloatValidator()
        ),
        "d": Invalid(
            err_type=TypeErr(expected_type=bool), value="hmm", validator=BoolValidator()
        ),
        "x": Invalid(
            err_type=TypeErr(expected_type=int), value=None, validator=IntValidator()
        ),
    }


def test_works_with_methods() -> None:
    class Obj:
        @validate_signature
        def some_method(self, a: int, *, b: int) -> int:
            return a + b

    assert Obj().some_method(1, b=2) == 3


def test_error_render_simple_typeerr() -> None:
    assert (
        get_arg_fail_message(Invalid(TypeErr(str), 5, StringValidator()))
        == "expected <class 'str'>"
    )

    assert (
        get_arg_fail_message(
            Invalid(TypeErr(int), "ok" * 50, IntValidator()), indent="    - "
        )
        == "    - expected <class 'int'>"
    )


def test_error_render_dict_errs() -> None:
    result = get_arg_fail_message(
        Invalid(
            KeyErrs(
                {
                    "abc": Invalid(TypeErr(str), 5, StringValidator()),
                    "def": Invalid(TypeErr(int), "abc", IntValidator()),
                }
            ),
            {"abc": 5, "def": "abc"},
            DictValidatorAny({"abc": StringValidator(), "def": IntValidator()}),
        )
    )
    expected = """KeyErrs
    'abc': expected <class 'str'>
    'def': expected <class 'int'>"""
    assert result == expected


def test_error_render_predicate_errors() -> None:
    result = get_arg_fail_message(
        Invalid(
            PredicateErrs([Min(5), MultipleOf(3)]), 4, IntValidator(Min(5), MultipleOf(3))
        )
    )

    expected = f"""PredicateErrs
    {repr(Min(5))}
    {repr(MultipleOf(3))}"""

    assert result == expected


def test_error_render_extra_keys() -> None:
    result = get_arg_fail_message(
        Invalid(
            ExtraKeysErr({1, 2, "3"}),
            {"a": 5},
            DictValidatorAny(
                {1: StringValidator(), 2: StringValidator(), "3": StringValidator()}
            ),
        )
    )
    expected = """ExtraKeysErr
    only expected keys ['3', 1, 2]"""

    assert result == expected


def test_error_render_index_errs() -> None:
    result = get_arg_fail_message(
        Invalid(
            IndexErrs(
                {
                    1: Invalid(TypeErr(int), False, IntValidator()),
                    3: Invalid(TypeErr(int), "bad", IntValidator()),
                }
            ),
            [0, False, 4, "bad"],
            ListValidator(IntValidator()),
        )
    )
    expected = """IndexErrs
    1: expected <class 'int'>
    3: expected <class 'int'>"""

    assert result == expected


def test_error_render_keyvalerrs_errs() -> None:
    result = get_arg_fail_message(
        Invalid(
            MapErr(
                {
                    "a": KeyValErrs(
                        key=Invalid(TypeErr(int), "a", IntValidator()),
                        val=Invalid(TypeErr(int), "bad", IntValidator()),
                    ),
                    2: KeyValErrs(
                        val=Invalid(TypeErr(int), False, IntValidator()), key=None
                    ),
                }
            ),
            {"a": "b", 2: False},
            MapValidator(key=IntValidator(), value=IntValidator()),
        )
    )
    expected = """MapErr
    'a' (key): expected <class 'int'>
    'a' (val): expected <class 'int'>
    2 (val): expected <class 'int'>"""

    assert result == expected
