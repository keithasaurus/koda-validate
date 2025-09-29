from copy import copy
from dataclasses import dataclass

from koda import Just

from koda_validate import Invalid, StringValidator, TypeErr, Valid, ListValidator, DataclassValidator, MapValidator, \
    IntValidator, SetValidator, MaxLength, MinLength, ExactLength
from koda_validate.maybe import MaybeValidator
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

    @dataclass
    class Person:
        name: str
        age: int

    v1 = DataclassValidator(Person, fail_on_unknown_keys=True)

    assert repr(v1({})) == """
Invalid(
    err_type=KeyErrs(keys={
        'name': Invalid(
            err_type=MissingKeyErr(),
            value={},
            validator=DataclassValidator(<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>, fail_on_unknown_keys=True)
        ),
        'age': Invalid(
            err_type=MissingKeyErr(),
            value={},
            validator=DataclassValidator(<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>, fail_on_unknown_keys=True)
        ),
    }),
    value={},
    validator=DataclassValidator(<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>, fail_on_unknown_keys=True)
)
""".strip()

    mayv = MaybeValidator(ListValidator(StringValidator()))
    assert repr(mayv(Just([4]))) == """
Invalid(
    err_type=ContainerErr(
        child=Invalid(
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
    ),
    value=Just([4]),
    validator=MaybeValidator(ListValidator(StringValidator()))
)
""".strip()


    assert repr(v1({"name": "John", "age": 10, "favorite_color": "blue"})) == """
Invalid(
    err_type=ExtraKeysErr(
        expected_keys={'age', 'name'},}
    ),
    value={'name': 'John', 'age': 10, 'favorite_color': 'blue'},
    validator=DataclassValidator(<class 'tests.test_valid.test_invalid_repr.<locals>.Person'>, fail_on_unknown_keys=True)
)
""".strip()

    mv = MapValidator(
        key=StringValidator(),
        value=IntValidator()
    )

    assert repr(mv({"ok": "not ok"})) == """
Invalid(
    err_type=MapErr(keys={
        'ok': KeyValErrs(
            key=None,
            val=Invalid(
                err_type=TypeErr(expected_type=<class 'int'>),
                value='not ok',
                validator=IntValidator()
            )
        ),
    }),
    value={'ok': 'not ok'},
    validator=MapValidator(key=StringValidator(), value=IntValidator())
)
""".strip()

    setv = SetValidator(IntValidator())

    assert repr(setv({"not ok"})) == """
Invalid(
    err_type=SetErrs(item_errs=[
        Invalid(
            err_type=TypeErr(expected_type=<class 'int'>),
            value='not ok',
            validator=IntValidator()
        ),
    ]),
    value={'not ok'},
    validator=SetValidator(IntValidator())
)
""".strip()

    pred_v = StringValidator(
        MaxLength(1),
        MinLength(1),
        ExactLength(1),
    )
    assert repr(pred_v("")) == """
Invalid(
    err_type=PredicateErrs(predicates=[
        MinLength(length=1),
        ExactLength(length=1),
    ]),
    value='',
    validator=StringValidator(MaxLength(length=1), MinLength(length=1), ExactLength(length=1))
)
""".strip()