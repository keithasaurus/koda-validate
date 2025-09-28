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
    sv = StringValidator()

    assert repr(sv(5)) == """
Invalid(
    err_type=TypeErr(expected_type=<class 'str'>),
    value=5,
    validator=StringValidator()
)
""".strip()

    lv = get_typehint_validator(list[str])

    assert repr(lv([4])) == """
Invalid(
    err_type=IndexErrs(index_errs={
        0: Invalid(
            err_type=TypeErr(expected_type=<class 'str'>),
            value=4,
            validator=StringValidator()
        ),
    }),
    value=[4],
    validator=ListValidator(StringValidator())
)
""".strip()

    # @dataclass
    # class Person:
    #     name: str
    #     age: int
    #
    # v1 = DataclassValidator(Person, fail_on_unknown_keys=True)
    #
    # print(v1({}))
    #
    # mayv = MaybeValidator(ListValidator(StringValidator()))
    # print(mayv(Just([4])))
    #
    # print(v1({"name": "John", "age": 10, "favorite_color": "blue"}))
    #
    # mv = MapValidator(
    #     key=StringValidator(),
    #     value=IntValidator()
    # )
    #
    # print(mv({"ok": "not ok"}))
    #
    # setv = SetValidator(IntValidator())
    #
    # print(setv({"ok", "not ok"}))
    #
    # pred_v = StringValidator(
    #     MaxLength(1),
    #     MinLength(1),
    #     ExactLength(1),
    # )
    # print(pred_v(""))