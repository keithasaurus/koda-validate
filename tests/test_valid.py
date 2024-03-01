from copy import copy

from koda_validate import Invalid, StringValidator, TypeErr, Valid


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
