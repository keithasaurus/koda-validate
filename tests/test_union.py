from typing import Any

import pytest

from koda_validate import FloatValidator, IntValidator, Invalid, StringValidator, Valid
from koda_validate.base import TypeErr, ValidationResult, Validator, VariantErrs
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
        str_int_float_validator,
        None,
        VariantErrs(
            [
                Invalid(s_v, None, TypeErr(str)),
                Invalid(i_v, None, TypeErr(int)),
                Invalid(f_v, None, TypeErr(float)),
            ],
        ),
    )

    assert str_int_float_validator(False) == Invalid(
        str_int_float_validator,
        False,
        VariantErrs(
            [
                Invalid(s_v, False, TypeErr(str)),
                Invalid(i_v, False, TypeErr(int)),
                Invalid(f_v, False, TypeErr(float)),
            ],
        ),
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
                return Invalid(self, val, TypeErr(type(None)))

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
        str_int_float_validator,
        [],
        VariantErrs(
            [
                Invalid(s_v, [], TypeErr(str)),
                Invalid(i_v, [], TypeErr(int)),
                Invalid(f_v, [], TypeErr(float)),
                Invalid(n_v, [], TypeErr(type(None))),
            ]
        ),
    )

    assert await str_int_float_validator.validate_async(False) == Invalid(
        str_int_float_validator,
        False,
        VariantErrs(
            [
                Invalid(s_v, False, TypeErr(str)),
                Invalid(i_v, False, TypeErr(int)),
                Invalid(f_v, False, TypeErr(float)),
                Invalid(n_v, False, TypeErr(type(None))),
            ],
        ),
    )
