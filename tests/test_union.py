from typing import Any

import pytest

from koda_validate import FloatValidator, IntValidator, Invalid, StringValidator, Valid
from koda_validate.base import TypeErr, UnionErrs, ValidationResult, Validator
from koda_validate.union import UnionValidator


def test_union_validator_typed() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    f_v = FloatValidator()
    str_int_float_validator = UnionValidator.typed(s_v, i_v, f_v)

    assert str_int_float_validator("abc") == Valid("abc")
    assert str_int_float_validator(5) == Valid(5)
    assert str_int_float_validator(5.5) == Valid(5.5)
    assert str_int_float_validator(None) == Invalid(
        UnionErrs(
            [
                Invalid(TypeErr(str), None, s_v),
                Invalid(TypeErr(int), None, i_v),
                Invalid(TypeErr(float), None, f_v),
            ],
        ),
        None,
        str_int_float_validator,
    )

    assert str_int_float_validator(False) == Invalid(
        UnionErrs(
            [
                Invalid(TypeErr(str), False, s_v),
                Invalid(TypeErr(int), False, i_v),
                Invalid(TypeErr(float), False, f_v),
            ],
        ),
        False,
        str_int_float_validator,
    )


@pytest.mark.asyncio
async def test_union_validator_any_async() -> None:
    class TestNoneValidator(Validator[None]):
        async def validate_async(self, val: Any) -> ValidationResult[None]:
            return self(val)

        def __call__(self, val: Any) -> ValidationResult[None]:
            if val is None:
                return Valid(None)
            else:
                return Invalid(TypeErr(type(None)), val, self)

    s_v = StringValidator()
    i_v = IntValidator()
    f_v = FloatValidator()
    n_v = TestNoneValidator()
    str_int_float_validator = UnionValidator.untyped(s_v, i_v, f_v, n_v)

    assert await str_int_float_validator.validate_async("abc") == Valid("abc")
    assert await str_int_float_validator.validate_async(5) == Valid(5)
    assert await str_int_float_validator.validate_async(None) == Valid(None)
    result = await str_int_float_validator.validate_async([])
    assert result == Invalid(
        UnionErrs(
            [
                Invalid(TypeErr(str), [], s_v),
                Invalid(TypeErr(int), [], i_v),
                Invalid(TypeErr(float), [], f_v),
                Invalid(TypeErr(type(None)), [], n_v),
            ]
        ),
        [],
        str_int_float_validator,
    )

    assert await str_int_float_validator.validate_async(False) == Invalid(
        UnionErrs(
            [
                Invalid(TypeErr(str), False, s_v),
                Invalid(TypeErr(int), False, i_v),
                Invalid(TypeErr(float), False, f_v),
                Invalid(TypeErr(type(None)), False, n_v),
            ],
        ),
        False,
        str_int_float_validator,
    )


def test_union_repr() -> None:
    assert repr(UnionValidator(StringValidator())) == "UnionValidator(StringValidator())"
    assert (
        repr(UnionValidator(IntValidator(), StringValidator(), FloatValidator()))
        == "UnionValidator(IntValidator(), StringValidator(), FloatValidator())"
    )


def test_union_eq() -> None:
    assert UnionValidator(StringValidator()) == UnionValidator(StringValidator())
    assert UnionValidator(StringValidator(), IntValidator()) != UnionValidator(
        StringValidator()
    )
    assert UnionValidator(StringValidator(), IntValidator()) == UnionValidator(
        StringValidator(), IntValidator()
    )
