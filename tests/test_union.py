from typing import Any

import pytest

from koda_validate import FloatValidator, IntValidator, Invalid, StringValidator, Valid
from koda_validate.base import InvalidType, InvalidVariants, ValidationResult, Validator
from koda_validate.union import UnionValidatorAny


def test_union_validator_any() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    f_v = FloatValidator()
    str_int_float_validator = UnionValidatorAny(s_v, i_v, f_v)

    assert str_int_float_validator("abc") == Valid("abc")
    assert str_int_float_validator(5) == Valid(5)
    assert str_int_float_validator(5.5) == Valid(5.5)
    assert str_int_float_validator(None) == Invalid(
        InvalidVariants(
            str_int_float_validator,
            [
                InvalidType(s_v, str),
                InvalidType(i_v, int),
                InvalidType(f_v, float),
            ],
        )
    )

    assert str_int_float_validator(False) == Invalid(
        InvalidVariants(
            str_int_float_validator,
            [
                InvalidType(s_v, str),
                InvalidType(i_v, int),
                InvalidType(f_v, float),
            ],
        )
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
                return Invalid(InvalidType(self, type(None)))

    s_v = StringValidator()
    i_v = IntValidator()
    f_v = FloatValidator()
    n_v = TestNoneValidator()
    str_int_float_validator = UnionValidatorAny(s_v, i_v, f_v, n_v)

    assert await str_int_float_validator.validate_async("abc") == Valid("abc")
    assert await str_int_float_validator.validate_async(5) == Valid(5)
    assert await str_int_float_validator.validate_async(None) == Valid(None)
    assert await str_int_float_validator.validate_async([]) == Invalid(
        InvalidVariants(
            str_int_float_validator,
            [
                InvalidType(s_v, str),
                InvalidType(i_v, int),
                InvalidType(f_v, float),
                InvalidType(n_v, type(None)),
            ],
        )
    )

    assert await str_int_float_validator.validate_async(False) == Invalid(
        InvalidVariants(
            str_int_float_validator,
            [
                InvalidType(s_v, str),
                InvalidType(i_v, int),
                InvalidType(f_v, float),
                InvalidType(n_v, type(None)),
            ],
        )
    )
