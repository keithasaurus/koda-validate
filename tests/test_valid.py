from copy import copy
from dataclasses import dataclass

from koda_validate import Invalid, StringValidator, TypeErr, Valid, ListValidator
from koda_validate.typehints import get_typehint_validator


def test_valid_map() -> None:
    assert Valid("something").map(lambda x: x.replace("some", "no")) == Valid("nothing")
    assert Valid(5).map(str) == Valid("5")

    inv = Invalid(
        err_type=TypeErr(str),
        value=5,
        validator=StringValidator(),
    )

    mapped = copy(inv).map(lambda x: x.replace("some", "no"))
    assert isinstance(mapped, Invalid)
    assert mapped.value == inv.value
    assert mapped.err_type == inv.err_type
    assert mapped.validator == inv.validator


def test_invalid_repr() -> None:
    lv = get_typehint_validator(list[str])

    print(lv([5]))
    breakpoint()
    assert repr(lv([5])) == """Invalid(err_type=IndexErrs(indexes={0: Invalid(err_type=UnionErrs(variants=[Invalid(err_type=TypeErr(expected_type=<class 'str'>), value=5, validator=StringValidator()), Invalid(err_type=CoercionErr(compatible_types={<class 'dict'>, <class 'tests.test_valid.test_invalid_repr.<locals>.Person'>}, dest_type=<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>), value=5, validator=DataclassValidator(<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>))]), value=5, validator=UnionValidator(StringValidator(), DataclassValidator(<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>)))}), value=[5], validator=ListValidator(UnionValidator(StringValidator(), DataclassValidator(<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>))))"""
