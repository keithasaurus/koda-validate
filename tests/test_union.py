from koda_validate import FloatValidator, IntValidator, Invalid, StringValidator, Valid
from koda_validate.base import InvalidType, InvalidVariants
from koda_validate.union import UnionValidatorAny


def test_union_validator_any() -> None:
    str_int_float_validator = UnionValidatorAny(
        StringValidator(), IntValidator(), FloatValidator()
    )

    assert str_int_float_validator("abc") == Valid("abc")
    assert str_int_float_validator(5) == Valid(5)
    assert str_int_float_validator(5.5) == Valid(5.5)
    assert str_int_float_validator(None) == Invalid(
        InvalidVariants(
            [
                InvalidType(str, "expected a string"),
                InvalidType(int, "expected an integer"),
                InvalidType(float, "expected a float"),
            ]
        )
    )

    assert str_int_float_validator(False) == Invalid(
        InvalidVariants(
            [
                InvalidType(str, "expected a string"),
                InvalidType(int, "expected an integer"),
                InvalidType(float, "expected a float"),
            ]
        )
    )
