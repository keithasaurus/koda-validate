from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, List, NamedTuple, Optional, Tuple, TypedDict
from uuid import UUID

import pytest
from _decimal import Decimal
from koda import Just

from koda_validate import (
    BoolValidator,
    CoercionErr,
    ContainerErr,
    DecimalValidator,
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
    MaxLength,
    Min,
    MinLength,
    MultipleOf,
    PredicateErrs,
    SetErrs,
    SetValidator,
    StringValidator,
    TypeErr,
    UnionErrs,
    UnionValidator,
    Validator,
)
from koda_validate.maybe import MaybeValidator
from koda_validate.signature import (
    _INVALID_ARGS_MESSAGE_HEADER,
    _INVALID_RETURN_MESSAGE_HEADER,
    RETURN_OVERRIDE_KEY,
    InvalidArgsError,
    InvalidReturnError,
    _get_arg_fail_message,
    _get_args_fail_msg,
    validate_signature,
)
from koda_validate.typehints import get_typehint_validator


def test_empty_signature_is_fine() -> None:
    @validate_signature
    def constant():  # type: ignore[no-untyped-def]
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
    expected = _INVALID_ARGS_MESSAGE_HEADER + _get_args_fail_msg(
        {"x": Invalid(TypeErr(int), "abc", IntValidator())}
    )
    assert result == expected

    @validate_signature
    def identity_str(x: str) -> str:
        return x

    assert identity_str("abc") == "abc"
    with pytest.raises(InvalidArgsError) as exc_info:
        identity_str(123)  # type: ignore[arg-type]

    assert str(exc_info.value) == _INVALID_ARGS_MESSAGE_HEADER + _get_args_fail_msg(
        {"x": Invalid(TypeErr(str), 123, IntValidator())}
    )


def test_catches_bad_return_type() -> None:
    @validate_signature
    def some_func() -> str:
        return 5  # type: ignore[return-value]

    with pytest.raises(InvalidReturnError) as exc_info:
        assert some_func()

    assert str(exc_info.value) == _INVALID_RETURN_MESSAGE_HEADER + _get_arg_fail_message(
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
        _get_arg_fail_message(Invalid(TypeErr(str), 5, StringValidator()))
        == "expected <class 'str'>"
    )

    assert (
        _get_arg_fail_message(
            Invalid(TypeErr(int), "ok" * 50, IntValidator()), indent="    - "
        )
        == "    - expected <class 'int'>"
    )


def test_error_render_dict_errs() -> None:
    result = _get_arg_fail_message(
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
    result = _get_arg_fail_message(
        Invalid(
            PredicateErrs([Min(5), MultipleOf(3)]), 4, IntValidator(Min(5), MultipleOf(3))
        )
    )

    expected = f"""PredicateErrs
    {repr(Min(5))}
    {repr(MultipleOf(3))}"""

    assert result == expected


def test_error_render_extra_keys() -> None:
    result = _get_arg_fail_message(
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


def test_error_render_union_errors() -> None:
    result = _get_arg_fail_message(
        Invalid(
            UnionErrs(
                [
                    Invalid(TypeErr(str), 5, StringValidator()),
                    Invalid(TypeErr(float), 5, FloatValidator()),
                ]
            ),
            5,
            UnionValidator(StringValidator(), FloatValidator()),
        )
    )

    expected = """UnionErrs
    variant 1: expected <class 'str'>
    variant 2: expected <class 'float'>"""

    assert result == expected


def test_error_render_index_errs() -> None:
    result = _get_arg_fail_message(
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
    result = _get_arg_fail_message(
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


def test_ignore_args() -> None:
    @validate_signature(ignore_args={"b", "c", "d", "e", "f", "kwargs"})
    def fn(
        checked: str,
        b: int,
        /,
        c: float,
        *d: int,
        e: bool = False,
        f: Optional[str] = None,
        **kwargs: int,
    ) -> str:
        return f"{checked} {b} {c} {d} {e} {f} {kwargs}"

    assert (
        fn(
            "ok",
            "bi1",  # type: ignore[arg-type]
            "bf1",  # type: ignore[arg-type]
            "bi2",  # type: ignore[arg-type]
            "bi3",  # type: ignore[arg-type]
            "bb1",  # type: ignore[arg-type]
            e=3,  # type: ignore[arg-type]
            f="badbad",
            kw_other="xyz",  # type: ignore[arg-type]
        )
        == "ok bi1 bf1 ('bi2', 'bi3', 'bb1') 3 badbad {'kw_other': 'xyz'}"
    )


def test_ignore_non_defined_kwarg() -> None:
    @validate_signature(ignore_args={"extra_arg"})
    def fn(
        **kwargs: int,
    ) -> str:
        return str(kwargs["extra_arg"])

    assert fn(extra_arg="extra_arg_val") == "extra_arg_val"  # type: ignore[arg-type]


def test_error_render_coercion_errors() -> None:
    result = _get_arg_fail_message(
        Invalid(CoercionErr({int, str, Decimal}, Decimal), 1.2, DecimalValidator())
    )

    expected = (
        "expected any of [<class 'decimal.Decimal'>, <class 'int'>, <class 'str'>]"
        " to coerce to <class 'decimal.Decimal'>"
    )
    assert result == expected


def test_error_render_container_err() -> None:
    child_err = Invalid(TypeErr(str), -123, StringValidator())
    result = _get_arg_fail_message(
        Invalid(ContainerErr(child_err), Just(-123), MaybeValidator(StringValidator()))
    )

    assert result == _get_arg_fail_message(child_err)


def test_error_render_set_errs() -> None:
    set_errors = Invalid(
        SetErrs(
            [
                Invalid(TypeErr(int), 2.2, IntValidator()),
                Invalid(TypeErr(int), "abc" * 100, IntValidator()),
            ]
        ),
        {1, 2.2, "abc" * 100},
        SetValidator(IntValidator()),
    )

    result = _get_arg_fail_message(set_errors)
    truncated = repr("abc" * 100)[:27] + "..."
    expected = f"""SetErrs
    expected <class 'int'> :: 2.2
    expected <class 'int'> :: {truncated}"""
    assert expected == result


def test_overrides() -> None:
    @validate_signature(
        overrides={
            "a": StringValidator(MinLength(2)),
            RETURN_OVERRIDE_KEY: StringValidator(MinLength(2)),
        }
    )
    def something(
        a: str,
    ) -> str:
        # the function signature here can be regarded as somewhat of a mistake
        # because the return minlength should be 1, since we remove one character. It just
        # serves to allow us to test both the argument and return validators.
        return a[:-1]

    assert something("abc") == "ab"
    with pytest.raises(InvalidArgsError):
        something("")

    with pytest.raises(InvalidReturnError):
        something("ab")


def test_typehint_resolver() -> None:
    def custom_resolver(annotation: Any) -> Validator[Any]:
        if annotation is str:
            return StringValidator(MaxLength(2))
        else:
            return get_typehint_validator(annotation)

    @validate_signature(typehint_resolver=custom_resolver)
    def some_func(a: str, b: int) -> str:
        return str(b**2)

    assert some_func("aa", 2) == "4"

    with pytest.raises(InvalidArgsError):
        some_func(a="abc", b=2)

    with pytest.raises(InvalidReturnError):
        some_func("aa", 11)


def test_error_message_format() -> None:
    assert (
        str(InvalidReturnError(inv := Invalid(TypeErr(str), 5, StringValidator())))
        == f"""
Invalid Return Value
--------------------
{_get_arg_fail_message(inv)}"""
    )


@pytest.mark.asyncio
async def test_empty_signature_is_fine_async() -> None:
    @validate_signature
    async def constant():  # type: ignore[no-untyped-def]
        return 5

    assert await constant() == 5  # type: ignore[no-untyped-call]


@pytest.mark.asyncio
async def test_one_arg_simple_scalars_async() -> None:
    @validate_signature
    async def identity_int(x: int) -> int:
        return x

    assert await identity_int(123) == 123
    with pytest.raises(InvalidArgsError) as exc_info:
        await identity_int("abc")  # type: ignore[arg-type]

    result = str(exc_info.value)
    expected = _INVALID_ARGS_MESSAGE_HEADER + _get_args_fail_msg(
        {"x": Invalid(TypeErr(int), "abc", IntValidator())}
    )
    assert result == expected

    @validate_signature
    async def identity_str(x: str) -> str:
        return x

    assert await identity_str("abc") == "abc"
    with pytest.raises(InvalidArgsError) as exc_info:
        await identity_str(123)  # type: ignore[arg-type]

    assert str(exc_info.value) == _INVALID_ARGS_MESSAGE_HEADER + _get_args_fail_msg(
        {"x": Invalid(TypeErr(str), 123, IntValidator())}
    )


@pytest.mark.asyncio
async def test_catches_bad_return_type_async() -> None:
    @validate_signature
    async def some_func() -> str:
        return 5  # type: ignore[return-value]

    with pytest.raises(InvalidReturnError) as exc_info:
        assert await some_func()

    assert str(exc_info.value) == _INVALID_RETURN_MESSAGE_HEADER + _get_arg_fail_message(
        Invalid(TypeErr(str), 5, StringValidator())
    )


@pytest.mark.asyncio
async def test_ignores_return_type_async() -> None:
    @validate_signature(ignore_return=True)
    async def some_func() -> str:
        return 5  # type: ignore[return-value]

    assert await some_func() == 5  # type: ignore[comparison-overlap]


@pytest.mark.asyncio
async def test_multiple_args_custom_type_async() -> None:
    class Person:
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    # @validate_signature
    async def fn(a: int, b: Person) -> int:
        return 1

    assert await fn(5, Person("abc", 123)) == 1


@pytest.mark.asyncio
async def test_handles_kwargs_async() -> None:
    @validate_signature
    async def some_func(**kwargs: str) -> str:
        return "neat"

    assert await some_func(x="1") == "neat"

    assert await some_func() == "neat"

    with pytest.raises(InvalidArgsError):
        await some_func(x=1)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_handles_var_args_async() -> None:
    @validate_signature
    async def some_func(a: str, *b: int) -> str:
        return f"{a}, {b}"

    assert await some_func("empty") == "empty, ()"

    assert await some_func("ok", 1, 2, 3) == "ok, (1, 2, 3)"

    with pytest.raises(InvalidArgsError):
        await some_func("bad", 1, "hmm")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_succeeds_for_zero_errors_on_all_kinds_of_args_async() -> None:
    @validate_signature
    async def some_func(
        aa: int, /, a: int, *b: int, c: float, d: bool = False, **kwargs: int
    ) -> str:
        return f"{aa} {a} {b} {c} {d} {kwargs}"

    assert (
        await some_func(0, 1, 2, 3, 4, c=2.2, x=10) == "0 1 (2, 3, 4) 2.2 False {'x': 10}"
    )


@pytest.mark.asyncio
async def test_fails_for_all_failures_async() -> None:
    @validate_signature
    async def some_func(
        aa: int, /, a: int, *b: int, c: float, d: bool = False, **kwargs: int
    ) -> str:
        return f"{a} {b} {c} {d} {kwargs}"

    with pytest.raises(InvalidArgsError) as exc_info:
        await some_func("zz", "b", "c", "d", "e", c="x", d="hmm", x=None)  # type: ignore[arg-type]  # noqa: E501

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


@pytest.mark.asyncio
async def test_works_with_methods_async() -> None:
    class Obj:
        @validate_signature
        async def some_method(self, a: int, *, b: int) -> int:
            return a + b

    assert await Obj().some_method(1, b=2) == 3


@pytest.mark.asyncio
async def test_obj_works() -> None:
    class Obj:
        async def __call__(self, a: int, *, b: int) -> int:
            return a + b

    f = validate_signature(Obj())

    assert await f(1, b=2) == 3


def test_works_on_init() -> None:
    class Obj:
        @validate_signature
        def __init__(self, a: str, b: int) -> None:
            self.a = a
            self.b = b

    # doesn't raise
    obj = Obj("ok", 123)
    assert obj.a == "ok"
    assert obj.b == 123

    with pytest.raises(InvalidArgsError):
        Obj(123, "ok")  # type: ignore[arg-type]


def test_decimal_does_not_coerce_by_default_in_validate_signature() -> None:
    @validate_signature
    def fn(d: Decimal) -> Decimal:
        return d

    with pytest.raises(InvalidArgsError):
        fn(1)  # type: ignore[arg-type]

    with pytest.raises(InvalidArgsError):
        fn("1.0")  # type: ignore[arg-type]


def test_uuid_does_not_coerce() -> None:
    @validate_signature
    def fn(d: UUID) -> UUID:
        return d

    with pytest.raises(InvalidArgsError):
        fn("e024cf82-9623-11ed-bbcb-bf1b0be19baa")  # type: ignore[arg-type]

    with pytest.raises(InvalidArgsError):
        fn("1.0")  # type: ignore[arg-type]


def test_date_does_not_coerce() -> None:
    @validate_signature
    def fn(d: date) -> date:
        return d

    with pytest.raises(InvalidArgsError):
        fn("2023-01-01")  # type: ignore[arg-type]


def test_datetime_does_not_coerce() -> None:
    @validate_signature
    def fn(d: datetime) -> datetime:
        return d

    with pytest.raises(InvalidArgsError):
        fn(datetime.now().isoformat())  # type: ignore[arg-type]


def test_naked_tuple_does_not_coerce() -> None:
    @validate_signature
    def fn(d: Tuple) -> Tuple:  # type: ignore[type-arg]
        return d

    with pytest.raises(InvalidArgsError):
        fn(["frown"])  # type: ignore[arg-type]


def test_adorned_tuple_does_not_coerce() -> None:
    @validate_signature
    def fn(d: Tuple[str]) -> Tuple[str]:
        return d

    with pytest.raises(InvalidArgsError):
        fn(["frown"])  # type: ignore[arg-type]


def test_naked_list_does_not_coerce() -> None:
    @validate_signature
    def fn(d: List) -> List:  # type: ignore[type-arg]
        return d

    with pytest.raises(InvalidArgsError):
        fn(("frown",))  # type: ignore[arg-type]


def test_adorned_list_does_not_coerce() -> None:
    @validate_signature
    def fn(d: List[str]) -> List[str]:
        return d

    with pytest.raises(InvalidArgsError):
        fn(("frown",))  # type: ignore[arg-type]


def test_typeddict_does_not_coerce() -> None:
    class ABC(TypedDict):
        a: str
        b: int
        c: float

    @validate_signature
    def some_func(obj: ABC) -> ABC:
        return obj

    with pytest.raises(InvalidArgsError):
        some_func([("a", "hmm"), ("b", 5), ("c", 3.14)])  # type: ignore[arg-type]


def test_dataclass_does_not_coerce() -> None:
    @dataclass
    class ABC:
        a: str
        b: int
        c: float

    @validate_signature
    def some_func(obj: ABC) -> ABC:
        return obj

    with pytest.raises(InvalidArgsError):
        some_func({"a": "hmm", "b": 5, "c": 3.14})  # type: ignore[arg-type]

    assert some_func(ABC("ok", 1, 2.3)) == ABC("ok", 1, 2.3)


def test_namedtuple_does_not_coerce() -> None:
    class ABC(NamedTuple):
        a: str
        b: int
        c: float

    @validate_signature
    def some_func(obj: ABC) -> ABC:
        return obj

    with pytest.raises(InvalidArgsError):
        some_func({"a": "hmm", "b": 5, "c": 3.14})  # type: ignore[arg-type]

    assert some_func(ABC("ok", 1, 2.3)) == ABC("ok", 1, 2.3)
