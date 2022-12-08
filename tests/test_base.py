from koda_validate import StringValidator
from koda_validate.base import Invalid, TypeErr


def test_invalid_repr() -> None:
    assert (
        repr(Invalid(TypeErr(str), 10, StringValidator()))
        == """Invalid(
    err_type: TypeErr(expected=<class 'str'>),
    value: 10,
    validator: StringValidator() 
)"""
    )
