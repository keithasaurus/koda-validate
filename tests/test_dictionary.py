import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Hashable, List, Protocol

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
    InvalidDict,
    InvalidExtraKeys,
    InvalidKeyVal,
    InvalidMap,
    InvalidMissingKey,
    InvalidPredicates,
    InvalidSimple,
    InvalidType,
    ValidationErr,
    ValidationResult,
)
from koda_validate.dictionary import (
    DictValidatorAny,
    KeyNotRequired,
    RecordValidator,
    is_dict_validator,
)


class PersonLike(Protocol):
    last_name: str
    eye_color: str


_JONES_ERROR_MSG: ValidationErr = InvalidSimple(
    "can't have last_name of jones and eye color of brown"
)


def test_is_dict() -> None:
    assert is_dict_validator({}) == Valid({})
    assert is_dict_validator(None) == Invalid(InvalidType(is_dict_validator, dict))
    assert is_dict_validator({"a": 1, "b": 2, 5: "whatever"}) == Valid(
        {"a": 1, "b": 2, 5: "whatever"}
    )


@pytest.mark.asyncio
async def test_is_dict_async() -> None:
    assert await is_dict_validator.validate_async({}) == Valid({})
    assert await is_dict_validator.validate_async(None) == Invalid(
        InvalidType(is_dict_validator, dict)
    )
    assert await is_dict_validator.validate_async(
        {"a": 1, "b": 2, 5: "whatever"}
    ) == Valid({"a": 1, "b": 2, 5: "whatever"})


def test_map_validator() -> None:
    s_v = StringValidator()
    m_v_s_f = MapValidator(key=s_v, value=FloatValidator())

    assert m_v_s_f(None) == Invalid(InvalidType(m_v_s_f, dict))

    m_v_s_s = MapValidator(key=s_v, value=s_v)

    assert m_v_s_s(5) == Invalid(InvalidType(m_v_s_s, dict))

    assert MapValidator(key=s_v, value=s_v)({}) == Valid({})

    i_v = IntValidator()
    assert MapValidator(key=s_v, value=i_v)({"a": 5, "b": 22}) == Valid({"a": 5, "b": 22})

    m_s_i_v = MapValidator(key=s_v, value=i_v)
    assert m_s_i_v({5: None}) == Invalid(
        InvalidMap(
            m_s_i_v,
            {
                5: InvalidKeyVal(
                    key=InvalidType(s_v, str),
                    val=InvalidType(i_v, int),
                )
            },
        )
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
    ) == Invalid(complex_validator, InvalidPredicates([MaxKeys(1)]))

    assert complex_validator({"a": 100}) == Valid({"a": 100})

    class AddVal(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            val["newkey"] = 123
            return val

    map_validator_preprocessor = MapValidator(
        key=s_v, value=i_v, preprocessors=[AddVal()]
    )

    assert map_validator_preprocessor({}) == Valid({"newkey": 123})


@pytest.mark.asyncio
async def test_map_validator_async() -> None:
    s_v = StringValidator()
    m_v_s_f = MapValidator(key=s_v, value=FloatValidator())

    assert await m_v_s_f.validate_async(None) == Invalid(InvalidType(m_v_s_f, dict))

    m_v_s_s = MapValidator(key=s_v, value=s_v)

    assert await m_v_s_s.validate_async(5) == Invalid(InvalidType(m_v_s_s, dict))

    assert await MapValidator(
        key=StringValidator(), value=StringValidator()
    ).validate_async({}) == Valid({})

    assert await MapValidator(key=StringValidator(), value=IntValidator()).validate_async(
        {"a": 5, "b": 22}
    ) == Valid({"a": 5, "b": 22})

    i_v = IntValidator()
    m_s_i_v = MapValidator(key=s_v, value=i_v)

    assert await m_s_i_v.validate_async({5: None}) == Invalid(
        InvalidMap(
            m_s_i_v,
            {
                5: InvalidKeyVal(
                    key=InvalidType(s_v, str),
                    val=InvalidType(i_v, int),
                )
            },
        )
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
        complex_validator, InvalidPredicates([MaxKeys(1)])
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


def test_map_validator_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

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

    validator = RecordValidator(into=Person, keys=(("name", s_v),))

    assert validator("not a dict") == Invalid(InvalidType(validator, dict))

    assert validator({}) == Invalid(
        InvalidDict(validator, {"name": InvalidMissingKey(validator)})
    )

    assert validator({"name": 5}) == Invalid(
        InvalidDict(validator, keys={"name": InvalidType(s_v, str)})
    )

    assert validator({"name": "bob", "age": 50}) == Invalid(
        InvalidExtraKeys(validator, {"name"})
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
    )

    assert validator("not a dict") == Invalid(InvalidType(validator, dict))

    assert validator({}) == Invalid(
        InvalidDict(validator, {"name": InvalidMissingKey(validator)})
    )

    assert validator({"name": 5, "age": "50"}) == Invalid(
        InvalidDict(
            validator,
            {
                "name": InvalidType(s_v, str),
                "age": InvalidType(i_v, int),
            },
        )
    )

    assert validator({"name": "bob", "age": 50, "eye_color": "brown"}) == Invalid(
        InvalidExtraKeys(validator, {"name", "age"}),
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

    assert validator("") == Invalid(InvalidType(validator, dict))


def _nobody_named_jones_has_brown_eyes(
    person: PersonLike,
) -> ValidationResult[PersonLike]:
    if person.last_name.lower() == "jones" and person.eye_color == "brown":
        return Invalid(_JONES_ERROR_MSG)
    else:
        return Valid(person)


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
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator("") == Invalid(InvalidType(validator, dict))


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
    )

    assert validator(
        {"first_name": "bob", 5: "smith", ("age", "field"): 50, Decimal(6): "brown"}
    ) == Valid(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", 5: "Jones", ("age", "field"): 50, Decimal(6): "brown"}
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator({"bad field": 1}) == Invalid(
        InvalidExtraKeys(
            validator,
            {
                "first_name",
                5,
                ("age", "field"),
                Decimal(6),
            },
        )
    )

    assert validator("") == Invalid(InvalidType(validator, dict))


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
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator("") == Invalid(InvalidType(validator, dict))


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

    assert validator("") == Invalid(InvalidType(validator, dict))


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

    assert validator("") == Invalid(InvalidType(validator, dict))


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
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator("") == Invalid(InvalidType(validator, dict))


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

    assert validator("") == Invalid(InvalidType(validator, dict))


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

    assert validator("") == Invalid(InvalidType(validator, dict))


def test_record_int_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> ValidationResult[Person]:
        assert p.age == test_age
        assert p.name == test_name
        return Valid(p)

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

    def asserted_ok(p: Person) -> ValidationResult[Person]:
        assert p.age == test_age
        assert p.name == test_name
        return Valid(p)

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

    def asserted_ok(p: Person) -> ValidationResult[Person]:
        assert p.age == test_age
        assert p.name == test_name
        return Valid(p)

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

    assert empty_dict_validator({}).val == {}

    assert empty_dict_validator({"oops": 5}) == Invalid(
        InvalidExtraKeys(empty_dict_validator, set())
    )


def _nobody_named_jones_has_first_name_alice_dict(
    person: Dict[Hashable, Any],
) -> ValidationResult[Dict[Hashable, Any]]:
    if person["last_name"].lower() == "jones" and person["first_name"] == Just("alice"):
        return Invalid(_JONES_ERROR_MSG)
    else:
        return Valid(person)


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
            "favorite_color": Just("blue"),
            "requires_none": None,
            "favorite_books": ["war and peace", "pale fire"],
            "aaa": "bla",
            "owbwohe": 4,
            "something else": 4.4,
            12: False,
        }
    )

    assert validator("") == Invalid(InvalidType(validator, dict))


def test_dict_validator_any_key_missing() -> None:
    s_v = StringValidator()
    s_v_1 = StringValidator(preprocessors=[strip])
    validator = DictValidatorAny(
        {"first_name": KeyNotRequired(s_v_1), "last_name": s_v},
        validate_object=_nobody_named_jones_has_first_name_alice_dict,
    )

    assert validator({"first_name": " bob ", "last_name": "smith"}) == Valid(
        {
            "first_name": Just("bob"),
            "last_name": "smith",
        }
    )

    assert validator({"last_name": "smith"}) == Valid(
        {"first_name": nothing, "last_name": "smith"}
    )

    assert validator({"first_name": 5}) == Invalid(
        InvalidDict(
            validator,
            {
                "last_name": InvalidMissingKey(validator),
                "first_name": InvalidType(s_v_1, str),
            },
        )
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

    assert await validator.validate_async(None) == Invalid(InvalidType(validator, dict))

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(
        {
            "first_name": Just("bob"),
            "last_name": "smith",
        }
    )

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        {"first_name": nothing, "last_name": "smith"}
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        InvalidDict(
            validator,
            {
                "last_name": InvalidMissingKey(validator),
                "first_name": InvalidType(s_v, str),
            },
        )
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Invalid(
        InvalidExtraKeys(validator, {"first_name", "last_name"})
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
        {"first_name": nothing, "last_name": "smith"}
    )


@pytest.mark.asyncio
async def test_dict_validator_any_with_validate_object_async() -> None:
    async def val_obj_async(
        obj: Dict[Hashable, Any]
    ) -> ValidationResult[Dict[Hashable, Any]]:
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
            "first_name": Just("bob"),
            "last_name": "smith",
        }
    )

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        {"first_name": nothing, "last_name": "smith"}
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        InvalidDict(
            validator,
            {
                "last_name": InvalidMissingKey(validator),
                "first_name": InvalidType(s_v, str),
            },
        )
    )

    assert await validator.validate_async(
        {"last_name": "jones", "first_name": "alice"}
    ) == Invalid(_JONES_ERROR_MSG)


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
    ) == Valid({"last_name": "jones", "first_name": Just("alice")})


def test_dict_validator_any_cannot_have_validate_object_and_validate_object_async() -> None:  # noqa:m E501
    async def val_obj_async(
        obj: Dict[Hashable, Any]
    ) -> ValidationResult[Dict[Hashable, Any]]:
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
    ) -> ValidationResult[Person]:
        if person.name.lower() == "jones" and person.age == 100:
            return Invalid(InvalidSimple("Cannot be jones and 100"))
        else:
            return Valid(person)

    async def val_obj_async(obj: Person) -> ValidationResult[Person]:
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
    ) -> ValidationResult[Person]:
        if person.name.lower() == "jones" and person.age == 100:
            return Invalid(InvalidSimple("Cannot be jones and 100"))
        else:
            return Valid(person)

    async def val_obj_async(obj: Person) -> ValidationResult[Person]:
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
        InvalidSimple("Cannot be jones and 100")
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
        InvalidSimple("Cannot be jones and 100")
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

    assert await validator.validate_async(None) == Invalid(InvalidType(validator, dict))

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(Person(Just("bob"), "smith"))

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        Person(nothing, "smith")
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        InvalidDict(
            validator,
            {
                "last_name": InvalidMissingKey(validator),
                "first_name": InvalidType(s_v, str),
            },
        )
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Invalid(
        InvalidExtraKeys(validator, {"first_name", "last_name"})
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
