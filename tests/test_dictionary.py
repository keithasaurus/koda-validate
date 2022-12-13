import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Hashable, List, Optional, Protocol

import pytest
from koda import Just, Maybe, nothing

from koda_validate import (
    BoolValidator,
    FloatValidator,
    IntValidator,
    Invalid,
    ListValidator,
    MapValidator,
    MaxKeys,
    MaxLength,
    Min,
    MinKeys,
    Predicate,
    PredicateAsync,
    Processor,
    StringValidator,
    Valid,
    none_validator,
    strip,
)
from koda_validate._generics import A
from koda_validate.base import (
    BasicErr,
    ErrType,
    ExtraKeysErr,
    KeyErrs,
    KeyValErrs,
    MapErr,
    MissingKeyErr,
    PredicateErrs,
    TypeErr,
    Validator,
    missing_key_err,
)
from koda_validate.dictionary import (
    DictValidatorAny,
    IsDictValidator,
    KeyNotRequired,
    RecordValidator,
    is_dict_validator,
)


class PersonLike(Protocol):
    last_name: str
    eye_color: str


_JONES_ERROR_MSG = BasicErr("can't have last_name of jones and eye color of brown")


def test_is_dict() -> None:
    assert is_dict_validator({}) == Valid({})
    assert is_dict_validator(None) == Invalid(TypeErr(dict), None, is_dict_validator)
    assert is_dict_validator({"a": 1, "b": 2, 5: "whatever"}) == Valid(
        {"a": 1, "b": 2, 5: "whatever"}
    )


@pytest.mark.asyncio
async def test_is_dict_async() -> None:
    assert await is_dict_validator.validate_async({}) == Valid({})
    assert await is_dict_validator.validate_async(None) == Invalid(
        TypeErr(dict), None, is_dict_validator
    )
    assert await is_dict_validator.validate_async(
        {"a": 1, "b": 2, 5: "whatever"}
    ) == Valid({"a": 1, "b": 2, 5: "whatever"})


class AddVal(Processor[Dict[Any, Any]]):
    def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
        val["newkey"] = 123
        return val


def test_map_validator() -> None:
    s_v = StringValidator()
    m_v_s_f = MapValidator(key=s_v, value=FloatValidator())

    assert m_v_s_f(None) == Invalid(TypeErr(dict), None, m_v_s_f)

    m_v_s_s = MapValidator(key=s_v, value=s_v)

    assert m_v_s_s(5) == Invalid(TypeErr(dict), 5, m_v_s_s)

    assert MapValidator(key=s_v, value=s_v)({}) == Valid({})

    i_v = IntValidator()
    assert MapValidator(key=s_v, value=i_v)({"a": 5, "b": 22}) == Valid({"a": 5, "b": 22})

    m_s_i_v = MapValidator(key=s_v, value=i_v)
    assert m_s_i_v({5: None}) == Invalid(
        MapErr(
            {
                5: KeyValErrs(
                    key=Invalid(TypeErr(str), 5, s_v),
                    val=Invalid(TypeErr(int), None, i_v),
                )
            },
        ),
        {5: None},
        m_s_i_v,
    )

    @dataclass
    class MaxKeys(Predicate[Dict[Any, Any]]):
        max: int

        def __call__(self, val: Dict[Any, Any]) -> bool:
            return len(val) <= self.max

    complex_validator = MapValidator(
        key=StringValidator(MaxLength(4)),
        value=IntValidator(Min(5)),
        predicates=[MaxKeys(1)],
    )
    assert complex_validator(
        {"key1": 10, "key1a": 2},
    ) == Invalid(PredicateErrs([MaxKeys(1)]), {"key1": 10, "key1a": 2}, complex_validator)

    assert complex_validator({"a": 100}) == Valid({"a": 100})

    map_validator_preprocessor = MapValidator(
        key=s_v, value=i_v, preprocessors=[AddVal()]
    )

    assert map_validator_preprocessor({}) == Valid({"newkey": 123})


@pytest.mark.asyncio
async def test_map_validator_async() -> None:
    s_v = StringValidator()
    m_v_s_f = MapValidator(key=s_v, value=FloatValidator())

    assert await m_v_s_f.validate_async(None) == Invalid(TypeErr(dict), None, m_v_s_f)

    m_v_s_s = MapValidator(key=s_v, value=s_v)

    assert await m_v_s_s.validate_async(5) == Invalid(TypeErr(dict), 5, m_v_s_s)

    assert await MapValidator(
        key=StringValidator(), value=StringValidator()
    ).validate_async({}) == Valid({})

    assert await MapValidator(key=StringValidator(), value=IntValidator()).validate_async(
        {"a": 5, "b": 22}
    ) == Valid({"a": 5, "b": 22})

    i_v = IntValidator()
    m_s_i_v = MapValidator(key=s_v, value=i_v)

    assert await m_s_i_v.validate_async({5: None}) == Invalid(
        MapErr(
            {
                5: KeyValErrs(
                    key=Invalid(TypeErr(str), 5, s_v),
                    val=Invalid(TypeErr(int), None, i_v),
                )
            },
        ),
        {5: None},
        m_s_i_v,
    )

    @dataclass
    class MaxKeys(Predicate[Dict[Any, Any]]):
        max: int

        def __call__(self, val: Dict[Any, Any]) -> bool:
            return len(val) <= self.max

    complex_validator = MapValidator(
        key=StringValidator(MaxLength(4)),
        value=IntValidator(Min(5)),
        predicates=[MaxKeys(1)],
    )
    assert await complex_validator.validate_async({"key1": 10, "key1a": 2}) == Invalid(
        PredicateErrs([MaxKeys(1)]), {"key1": 10, "key1a": 2}, complex_validator
    )

    assert await complex_validator.validate_async({"a": 100}) == Valid({"a": 100})

    class AddVal(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            val["newkey"] = 123
            return val

    map_validator_preprocessor = MapValidator(
        key=StringValidator(), value=IntValidator(), preprocessors=[AddVal()]
    )

    assert map_validator_preprocessor({}) == Valid({"newkey": 123})


@dataclass
class AsyncWait(PredicateAsync[A]):
    async def validate_async(self, val: A) -> bool:
        await asyncio.sleep(0.001)
        return True


def test_map_validator_sync_call_with_async_predicates_raises_assertion_error() -> None:
    map_validator = MapValidator(
        key=StringValidator(), value=StringValidator(), predicates_async=[AsyncWait()]
    )
    with pytest.raises(AssertionError):
        map_validator([])


def test_max_keys() -> None:
    assert MaxKeys(0)({}) is True

    assert MaxKeys(5)({"a": 1, "b": 2, "c": 3}) is True

    assert MaxKeys(1)({"a": 1, "b": 2}) is False


def test_min_keys() -> None:
    assert MinKeys(0)({}) is True

    assert MinKeys(3)({"a": 1, "b": 2, "c": 3}) is True

    assert MinKeys(3)({"a": 1, "b": 2}) is False


def test_record_1() -> None:
    @dataclass
    class Person:
        name: str

    s_v = StringValidator()

    validator = RecordValidator(
        into=Person, keys=(("name", s_v),), fail_on_unknown_keys=True
    )

    assert validator("not a dict") == Invalid(TypeErr(dict), "not a dict", validator)

    assert validator({}) == Invalid(
        KeyErrs(
            {
                "name": Invalid(
                    missing_key_err,
                    {},
                    validator,
                )
            }
        ),
        {},
        validator,
    )

    assert validator({"name": 5}) == Invalid(
        KeyErrs(keys={"name": Invalid(TypeErr(str), 5, s_v)}), {"name": 5}, validator
    )

    assert validator({"name": "bob", "age": 50}) == Invalid(
        ExtraKeysErr({"name"}), {"name": "bob", "age": 50}, validator
    )

    assert validator({"name": "bob"}) == Valid(Person("bob"))


def test_record_2() -> None:
    @dataclass
    class Person:
        name: str
        age: Maybe[int]

    s_v = StringValidator()
    i_v = IntValidator()

    validator = RecordValidator(
        into=Person,
        keys=(("name", s_v), ("age", KeyNotRequired(i_v))),
        fail_on_unknown_keys=True,
    )

    assert validator("not a dict") == Invalid(TypeErr(dict), "not a dict", validator)

    assert validator({}) == Invalid(
        KeyErrs({"name": Invalid(missing_key_err, {}, validator)}), {}, validator
    )

    assert validator({"name": 5, "age": "50"}) == Invalid(
        KeyErrs(
            {
                "name": Invalid(TypeErr(str), 5, s_v),
                "age": Invalid(TypeErr(int), "50", i_v),
            },
        ),
        {"name": 5, "age": "50"},
        validator,
    )

    assert validator({"name": "bob", "age": 50, "eye_color": "brown"}) == Invalid(
        ExtraKeysErr({"name", "age"}),
        {"name": "bob", "age": 50, "eye_color": "brown"},
        validator,
    )

    assert validator({"name": "bob", "age": 50}) == Valid(Person("bob", Just(50)))
    assert validator({"name": "bob"}) == Valid(Person("bob", nothing))


def test_record_3() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int

    s_v_1 = StringValidator()
    s_v_2 = StringValidator()
    i_v = IntValidator()

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", s_v_1),
            ("last_name", s_v_2),
            ("age", i_v),
        ),
    )

    assert validator({"first_name": "bob", "last_name": "smith", "age": 50}) == Valid(
        Person("bob", "smith", 50)
    )

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def _nobody_named_jones_has_brown_eyes(
    person: PersonLike,
) -> Optional[ErrType]:
    if person.last_name.lower() == "jones" and person.eye_color == "brown":
        return _JONES_ERROR_MSG
    return None


def test_record_4() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {"first_name": "bob", "last_name": "smith", "age": 50, "eye color": "brown"}
    ) == Valid(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", "last_name": "Jones", "age": 50, "eye color": "brown"}
    ) == Invalid(_JONES_ERROR_MSG, Person("bob", "Jones", 50, "brown"), validator)

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_4_mix_and_match_key_types() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            (5, StringValidator()),
            (("age", "field"), IntValidator()),
            (Decimal(6), StringValidator()),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
        fail_on_unknown_keys=True,
    )

    assert validator(
        {"first_name": "bob", 5: "smith", ("age", "field"): 50, Decimal(6): "brown"}
    ) == Valid(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", 5: "Jones", ("age", "field"): 50, Decimal(6): "brown"}
    ) == Invalid(_JONES_ERROR_MSG, Person("bob", "Jones", 50, "brown"), validator)

    assert validator({"bad field": 1}) == Invalid(
        ExtraKeysErr(
            {
                "first_name",
                5,
                ("age", "field"),
                Decimal(6),
            },
        ),
        {"bad field": 1},
        validator,
    )

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_5() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True))

    assert validator(
        {
            "first_name": "bob",
            "last_name": "Jones",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
        }
    ) == Invalid(
        _JONES_ERROR_MSG,
        Person(
            "bob",
            "Jones",
            50,
            "brown",
            True,
        ),
        validator,
    )

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_6() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
        ),
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5))

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_7() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
        ),
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8))

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_8() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float
        favorite_color: Maybe[str]

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
            ("favorite_color", KeyNotRequired(StringValidator())),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, Just("blue")))

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, nothing))

    assert validator(
        {
            "first_name": "bob",
            "last_name": "jones",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
        }
    ) == Invalid(
        _JONES_ERROR_MSG,
        Person("bob", "jones", 50, "brown", True, 6.5, 9.8, Just("blue")),
        validator,
    )

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_9() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float
        favorite_color: Maybe[str]
        requires_none: None

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
            ("favorite_color", KeyNotRequired(StringValidator())),
            ("requires_none", none_validator),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
            "requires_none": None,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, Just("blue"), None))

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_10() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float
        favorite_color: Maybe[str]
        requires_none: None
        something_else: List[str]

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
            ("favorite_color", KeyNotRequired(StringValidator())),
            ("requires_none", none_validator),
            ("favorite_books", ListValidator(StringValidator())),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
            "requires_none": None,
            "favorite_books": ["war and peace", "pale fire"],
        }
    ) == Valid(
        Person(
            "bob",
            "smith",
            50,
            "brown",
            True,
            6.5,
            9.8,
            Just("blue"),
            None,
            ["war and peace", "pale fire"],
        )
    )

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_record_int_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Optional[ErrType]:
        assert p.age == test_age
        assert p.name == test_name
        return None

    dv = RecordValidator(
        into=Person,
        keys=(
            (22, StringValidator()),
            (10, IntValidator()),
        ),
        validate_object=asserted_ok,
    )
    assert dv({10: test_age, 22: test_name}) == Valid(Person(test_name, test_age))


def test_record_tuple_str_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Optional[ErrType]:
        assert p.age == test_age
        assert p.name == test_name
        return None

    dv = RecordValidator(
        into=Person,
        keys=((("ok",), StringValidator()), (("neat", "cool"), IntValidator())),
        validate_object=asserted_ok,
    )
    assert dv({("ok",): test_name, ("neat", "cool"): test_age}) == Valid(
        Person(test_name, test_age)
    )


def test_record_decimal_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Optional[ErrType]:
        assert p.age == test_age
        assert p.name == test_name
        return None

    dv = RecordValidator(
        into=Person,
        keys=((Decimal(22), StringValidator()), (Decimal("1.111"), IntValidator())),
        validate_object=asserted_ok,
    )
    assert dv({Decimal("1.111"): test_age, Decimal(22): test_name}) == Valid(
        Person(test_name, test_age)
    )


def test_dict_validator_preprocessors() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    @dataclass
    class Person:
        name: str

    dv = RecordValidator(
        into=Person, keys=(("name", StringValidator()),), preprocessors=[RemoveKey()]
    )

    assert dv({"a": 123, "name": "bob"}) == Valid(Person("bob"))


def test_dict_validator_any_empty() -> None:
    empty_dict_validator = DictValidatorAny({})

    empty_result = empty_dict_validator({})
    assert isinstance(empty_result, Valid)
    assert empty_result.val == {}

    assert empty_dict_validator({"oops": 5}) == Invalid(
        ExtraKeysErr(set()), {"oops": 5}, empty_dict_validator
    )


def _nobody_named_jones_has_first_name_alice_dict(
    person: Dict[Hashable, Any],
) -> Optional[ErrType]:
    if person["last_name"].lower() == "jones" and person.get("first_name") == "alice":
        return _JONES_ERROR_MSG
    else:
        return None


def test_dict_validator_any() -> None:
    validator = DictValidatorAny(
        dict(
            (
                ("first_name", StringValidator(preprocessors=[strip])),
                ("last_name", StringValidator()),
                ("age", IntValidator()),
                ("eye color", StringValidator()),
                ("can-fly", BoolValidator()),
                ("number_of_fingers", FloatValidator()),
                ("number of toes", FloatValidator()),
                ("favorite_color", KeyNotRequired(StringValidator())),
                ("requires_none", none_validator),
                ("favorite_books", ListValidator(StringValidator())),
                ("aaa", StringValidator()),
                ("owbwohe", IntValidator()),
                ("something else", FloatValidator()),
                (12, BoolValidator()),
            )
        ),
        validate_object=_nobody_named_jones_has_first_name_alice_dict,
    )

    assert validator(
        {
            "first_name": " bob ",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
            "requires_none": None,
            "favorite_books": ["war and peace", "pale fire"],
            "aaa": "bla",
            "owbwohe": 4,
            "something else": 4.4,
            12: False,
        }
    ) == Valid(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
            "requires_none": None,
            "favorite_books": ["war and peace", "pale fire"],
            "aaa": "bla",
            "owbwohe": 4,
            "something else": 4.4,
            12: False,
        }
    )

    assert validator("") == Invalid(TypeErr(dict), "", validator)


def test_dict_validator_any_key_missing() -> None:
    s_v = StringValidator()
    s_v_1 = StringValidator(preprocessors=[strip])
    validator = DictValidatorAny(
        {"first_name": KeyNotRequired(s_v_1), "last_name": s_v},
        validate_object=_nobody_named_jones_has_first_name_alice_dict,
    )

    assert validator({"first_name": " bob ", "last_name": "smith"}) == Valid(
        {
            "first_name": "bob",
            "last_name": "smith",
        }
    )

    assert validator({"last_name": "smith"}) == Valid({"last_name": "smith"})

    assert validator({"first_name": 5}) == Invalid(
        KeyErrs(
            {
                "last_name": Invalid(MissingKeyErr(), {"first_name": 5}, validator),
                "first_name": Invalid(TypeErr(str), 5, s_v_1),
            },
        ),
        {"first_name": 5},
        validator,
    )


def test_dict_validator_any_preprocessors() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    dv = DictValidatorAny({"name": StringValidator()}, preprocessors=[RemoveKey()])

    assert dv({"a": 123, "name": "bob"}) == Valid({"name": "bob"})


@pytest.mark.asyncio
async def test_validate_dictionary_any_async() -> None:
    s_v = StringValidator(preprocessors=[strip])
    validator = DictValidatorAny(
        {
            "first_name": KeyNotRequired(s_v),
            "last_name": StringValidator(),
        },
        validate_object=_nobody_named_jones_has_first_name_alice_dict,
    )

    assert await validator.validate_async(None) == Invalid(TypeErr(dict), None, validator)

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(
        {
            "first_name": "bob",
            "last_name": "smith",
        }
    )

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        {"last_name": "smith"}
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        KeyErrs(
            {
                "last_name": Invalid(missing_key_err, {"first_name": 5}, validator),
                "first_name": Invalid(TypeErr(str), 5, s_v),
            },
        ),
        {"first_name": 5},
        validator,
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Invalid(
        ExtraKeysErr({"first_name", "last_name"}),
        {"last_name": "smith", "a": 123.45},
        validator,
    )


@pytest.mark.asyncio
async def test_dict_validator_any_async_processor() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    validator = DictValidatorAny(
        {
            "first_name": KeyNotRequired(StringValidator(preprocessors=[strip])),
            "last_name": StringValidator(),
        },
        preprocessors=[RemoveKey()],
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Valid(
        {"last_name": "smith"}
    )


@pytest.mark.asyncio
async def test_dict_validator_any_with_validate_object_async() -> None:
    async def val_obj_async(obj: Dict[Hashable, Any]) -> Optional[ErrType]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_has_first_name_alice_dict(obj)

    s_v = StringValidator(preprocessors=[strip])

    validator = DictValidatorAny(
        {
            "first_name": KeyNotRequired(s_v),
            "last_name": StringValidator(),
        },
        validate_object_async=val_obj_async,
    )

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(
        {
            "first_name": "bob",
            "last_name": "smith",
        }
    )

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        {"last_name": "smith"}
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        KeyErrs(
            {
                "last_name": Invalid(missing_key_err, {"first_name": 5}, validator),
                "first_name": Invalid(TypeErr(str), 5, s_v),
            },
        ),
        {"first_name": 5},
        validator,
    )

    assert await validator.validate_async(
        {"last_name": "jones", "first_name": "alice"}
    ) == Invalid(
        _JONES_ERROR_MSG, {"last_name": "jones", "first_name": "alice"}, validator
    )


@pytest.mark.asyncio
async def test_dict_validator_any_no_validate_object() -> None:
    validator = DictValidatorAny(
        {
            "first_name": KeyNotRequired(StringValidator(preprocessors=[strip])),
            "last_name": StringValidator(),
        }
    )
    assert await validator.validate_async(
        {"last_name": "jones", "first_name": "alice"}
    ) == Valid({"last_name": "jones", "first_name": "alice"})


def test_dict_validator_any_cannot_have_validate_object_and_validate_object_async() -> None:  # noqa:m E501
    async def val_obj_async(obj: Dict[Hashable, Any]) -> Optional[ErrType]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_has_first_name_alice_dict(obj)

    with pytest.raises(AssertionError):
        DictValidatorAny(
            schema={
                "first_name": KeyNotRequired(StringValidator(preprocessors=[strip])),
                "last_name": StringValidator(),
            },
            validate_object=_nobody_named_jones_has_first_name_alice_dict,
            validate_object_async=val_obj_async,
        )


def test_dict_validator_cannot_have_validate_object_and_validate_object_async() -> None:  # noqa:m E501
    @dataclass
    class Person:
        name: str
        age: int

    def _nobody_named_jones_is_100(
        person: Person,
    ) -> Optional[ErrType]:
        if person.name.lower() == "jones" and person.age == 100:
            return BasicErr("Cannot be jones and 100")
        else:
            return None

    async def val_obj_async(obj: Person) -> Optional[ErrType]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_is_100(obj)

    with pytest.raises(AssertionError):
        RecordValidator(
            into=Person,
            keys=(
                ("first_name", StringValidator(preprocessors=[strip])),
                ("age", IntValidator()),
            ),
            validate_object=_nobody_named_jones_is_100,
            validate_object_async=val_obj_async,
        )


@pytest.mark.asyncio
async def test_dict_validator_handles_validate_object_async_or_validate_object() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    def _nobody_named_jones_is_100(
        person: Person,
    ) -> Optional[ErrType]:
        if person.name.lower() == "jones" and person.age == 100:
            return BasicErr("Cannot be jones and 100")
        return None

    async def val_obj_async(obj: Person) -> Optional[ErrType]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_is_100(obj)

    validator_sync = RecordValidator(
        into=Person,
        keys=(
            ("name", StringValidator(preprocessors=[strip])),
            ("age", IntValidator()),
        ),
        validate_object=_nobody_named_jones_is_100,
    )

    # calling sync validate_object, even within async context
    assert await validator_sync.validate_async({"name": "jones", "age": 100}) == Invalid(
        BasicErr("Cannot be jones and 100"), Person("jones", 100), validator_sync
    )

    validator_async = RecordValidator(
        into=Person,
        keys=(
            ("name", StringValidator(preprocessors=[strip])),
            ("age", IntValidator()),
        ),
        validate_object_async=val_obj_async,
    )

    # calling sync validate_object_async within async context
    assert await validator_async.validate_async({"name": "jones", "age": 100}) == Invalid(
        BasicErr("Cannot be jones and 100"), Person("jones", 100), validator_async
    )

    # calling sync validate_object_async within async context
    assert await validator_async.validate_async({"name": "other", "age": 100}) == Valid(
        Person("other", 100)
    )


@pytest.mark.asyncio
async def test_validate_dictionary_async() -> None:
    @dataclass
    class Person:
        first_name: Maybe[str]
        last_name: str

    s_v = StringValidator(preprocessors=[strip])

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", KeyNotRequired(s_v)),
            ("last_name", StringValidator()),
        ),
    )

    assert await validator.validate_async(None) == Invalid(TypeErr(dict), None, validator)

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(Person(Just("bob"), "smith"))

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        Person(nothing, "smith")
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        KeyErrs(
            {
                "last_name": Invalid(missing_key_err, {"first_name": 5}, validator),
                "first_name": Invalid(TypeErr(str), 5, s_v),
            },
        ),
        {"first_name": 5},
        validator,
    )

    assert await validator.validate_async(
        {"last_name": "smith", "first_name": "bob", "a": 123.45}
    ) == Valid(Person(Just("bob"), "smith"))

    validator_no_extra_keys = RecordValidator(
        into=Person,
        keys=(
            ("first_name", KeyNotRequired(s_v)),
            ("last_name", StringValidator()),
        ),
        fail_on_unknown_keys=True,
    )

    assert await validator_no_extra_keys.validate_async(
        {"last_name": "smith", "a": 123.45}
    ) == Invalid(
        ExtraKeysErr({"first_name", "last_name"}),
        {"last_name": "smith", "a": 123.45},
        validator_no_extra_keys,
    )


@pytest.mark.asyncio
async def test_dict_validator_async_processor() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    @dataclass
    class Person:
        first_name: Maybe[str]
        last_name: str

    validator = RecordValidator(
        into=Person,
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
        preprocessors=[RemoveKey()],
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Valid(
        Person(nothing, "smith")
    )


def test_key_not_required_repr() -> None:
    assert repr(KeyNotRequired(none_validator)) == "KeyNotRequired(NoneValidator())"


def test_key_not_required_eq() -> None:
    assert KeyNotRequired(StringValidator()) == KeyNotRequired(StringValidator())
    assert KeyNotRequired(StringValidator()) != KeyNotRequired(IntValidator())


def test_map_validator_repr() -> None:
    assert repr(MapValidator(key=StringValidator(), value=IntValidator())) == (
        "MapValidator(key=StringValidator(), value=IntValidator())"
    )

    assert (
        repr(
            MapValidator(
                key=StringValidator(),
                value=IntValidator(),
                predicates=[MaxKeys(1)],
                predicates_async=[AsyncWait()],
                preprocessors=[(add_val := AddVal())],
            )
        )
        == f"MapValidator(key=StringValidator(), value=IntValidator(), "
        f"predicates=[MaxKeys(size=1)], predicates_async=[AsyncWait()], "
        f"preprocessors=[{repr(add_val)}])"
    )


def test_map_validator_eq() -> None:
    assert MapValidator(key=StringValidator(), value=IntValidator()) == MapValidator(
        key=StringValidator(), value=IntValidator()
    )
    assert MapValidator(key=IntValidator(), value=IntValidator()) != MapValidator(
        key=StringValidator(), value=IntValidator()
    )

    assert MapValidator(
        key=StringValidator(),
        value=IntValidator(),
        predicates=[MaxKeys(1)],
        predicates_async=[AsyncWait()],
        preprocessors=[AddVal()],
    ) != MapValidator(key=StringValidator(), value=IntValidator())

    add_val = AddVal()
    assert MapValidator(
        key=StringValidator(),
        value=IntValidator(),
        predicates=[MaxKeys(1)],
        predicates_async=[AsyncWait()],
        preprocessors=[add_val],
    ) == MapValidator(
        key=StringValidator(),
        value=IntValidator(),
        predicates=[MaxKeys(1)],
        predicates_async=[AsyncWait()],
        preprocessors=[add_val],
    )


def test_is_dict_repr() -> None:
    assert repr(is_dict_validator) == "IsDictValidator()"


def test_is_dict_eq() -> None:
    assert is_dict_validator == IsDictValidator()


def test_record_validator_eq() -> None:
    @dataclass
    class Abc:
        name: str

    rv = RecordValidator(keys=(("name", StringValidator()),), into=Abc)
    assert rv == RecordValidator(keys=(("name", StringValidator()),), into=Abc)

    def fn_1(data: Abc) -> Optional[ErrType]:
        return None

    rvov = RecordValidator(
        keys=(("name", StringValidator()),), into=Abc, validate_object=fn_1
    )
    assert rvov != rv

    assert rvov == RecordValidator(
        keys=(("name", StringValidator()),), into=Abc, validate_object=fn_1
    )


def test_record_validator_repr() -> None:
    @dataclass
    class Abc:
        name: str

    keys = (("name", StringValidator()),)
    assert (
        repr(
            RecordValidator(
                keys=keys,
                into=Abc,
            )
        )
        == f"RecordValidator(keys=(('name', StringValidator()),), into={repr(Abc)})"
    )

    assert (
        repr(RecordValidator(keys=keys, into=Abc, fail_on_unknown_keys=True))
        == f"RecordValidator(keys=(('name', StringValidator()),), into={repr(Abc)}, "
        f"fail_on_unknown_keys=True)"
    )

    def fn_1(data: Abc) -> Optional[ErrType]:
        return None

    assert (
        repr(RecordValidator(keys=keys, into=Abc, validate_object=fn_1))
        == f"RecordValidator(keys=(('name', StringValidator()),), "
        f"into={repr(Abc)}, validate_object={repr(fn_1)})"
    )


def test_dict_validator_any_eq() -> None:
    dva_1 = DictValidatorAny({"name": StringValidator()})
    assert dva_1 == DictValidatorAny({"name": StringValidator()})
    assert dva_1 != DictValidatorAny({})

    def fn_1(data: Dict[Any, Any]) -> Optional[ErrType]:
        return None

    dva_2 = DictValidatorAny({"name": StringValidator()}, validate_object=fn_1)
    assert dva_2 != dva_1

    assert dva_2 == DictValidatorAny({"name": StringValidator()}, validate_object=fn_1)

    add_val = AddVal()
    dva_3 = DictValidatorAny(
        {"name": StringValidator()}, preprocessors=[add_val], validate_object=fn_1
    )
    assert dva_3 != dva_2

    assert dva_3 == DictValidatorAny(
        {"name": StringValidator()}, preprocessors=[add_val], validate_object=fn_1
    )


def test_dict_validator_any_repr() -> None:
    schema: Dict[Any, Validator[Any]] = {"name": StringValidator()}
    assert repr(DictValidatorAny(schema)) == f"DictValidatorAny({repr(schema)})"

    def fn_1(data: Dict[Any, Any]) -> Optional[ErrType]:
        return None

    assert (
        repr(DictValidatorAny(schema, validate_object=fn_1))
        == f"DictValidatorAny({repr(schema)}, "
        f"validate_object={repr(fn_1)})"
    )
