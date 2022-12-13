import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import (
    Any,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    TypedDict,
    TypeVar,
)

from jsonschema.validators import Draft202012Validator

from koda_validate import (
    BoolValidator,
    BytesValidator,
    Choices,
    DataclassValidator,
    DatetimeValidator,
    DateValidator,
    DecimalValidator,
    EqualsValidator,
    FloatValidator,
    IntValidator,
    Lazy,
    ListValidator,
    Max,
    MaxItems,
    MaxLength,
    Min,
    MinItems,
    MinLength,
    NTupleValidator,
    OptionalValidator,
    TupleHomogenousValidator,
    UnionValidator,
    UniqueItems,
    UUIDValidator,
    Valid,
    unique_items,
)
from koda_validate.dictionary import (
    DictValidatorAny,
    KeyNotRequired,
    MapValidator,
    MaxKeys,
    MinKeys,
    RecordValidator,
    is_dict_validator,
)
from koda_validate.namedtuple import NamedTupleValidator
from koda_validate.openapi import generate_named_schema, generate_schema
from koda_validate.string import (
    EmailPredicate,
    RegexPredicate,
    StringValidator,
    not_blank,
)
from koda_validate.typeddict import TypedDictValidator
from koda_validate.union import UnionValidatorIndexed

A = TypeVar("A")
Ret = TypeVar("Ret")


def validate_schema(schema: Mapping[str, Any]) -> None:
    return Draft202012Validator.check_schema(schema)


def test_recursive_validator() -> None:
    @dataclass
    class Comment:
        name: str
        replies: List["Comment"]  # noqa: F821

    def get_comment_recur() -> RecordValidator[Comment]:
        return comment_validator

    comment_validator: RecordValidator[Comment] = RecordValidator(
        keys=(
            ("name", StringValidator(not_blank)),
            ("replies", ListValidator(Lazy(get_comment_recur))),
        ),
        into=Comment,
    )

    assert generate_named_schema("Comment", comment_validator) == {
        "Comment": {
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string", "pattern": r"^(?!\s*$).+"},
                "replies": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/Comment"},
                },
            },
            "required": ["name", "replies"],
            "type": "object",
        }
    }

    try:
        generate_schema(comment_validator)
    except TypeError as e:
        assert (
            str(e) == "`Lazy` type was not handled -- perhaps "
            "you need to use `generate_named_schema`?"
        )
    else:
        raise AssertionError("should have raised TypeError")


def test_person() -> None:
    @dataclass
    class Person:
        name: str
        email: str
        occupation: str
        country_code: str
        honorifics: List[str]

    person_validator = RecordValidator(
        keys=(
            ("name", StringValidator(not_blank)),
            ("email", StringValidator(EmailPredicate(), MaxLength(50))),
            (
                "occupation",
                StringValidator(Choices({"teacher", "engineer", "musician", "cook"})),
            ),
            ("country_code", StringValidator(MinLength(2), MaxLength(3))),
            (
                "honorifics",
                ListValidator(
                    StringValidator(RegexPredicate(re.compile(r"[A-Z][a-z]+\.]"))),
                    predicates=[unique_items, MinItems(1), MaxItems(3)],
                ),
            ),
        ),
        into=Person,
    )

    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["name", "email", "occupation", "country_code", "honorifics"],
        "properties": {
            "name": {"type": "string", "pattern": r"^(?!\s*$).+"},
            "email": {"type": "string", "format": "email", "maxLength": 50},
            "occupation": {
                "type": "string",
                "enum": ["cook", "engineer", "musician", "teacher"],
            },
            "country_code": {"type": "string", "minLength": 2, "maxLength": 3},
            "honorifics": {
                "uniqueItems": True,
                "type": "array",
                "minItems": 1,
                "maxItems": 3,
                "items": {"type": "string", "pattern": "[A-Z][a-z]+\\.]"},
            },
        },
    }
    # will throw if bad
    validate_schema(schema)
    assert generate_schema(person_validator) == schema

    @dataclass
    class Person2:
        name: str
        email: str
        occupation: str
        country_code: str
        honorifics: Tuple[str, ...]

    person_validator_tuple = RecordValidator(
        keys=(
            ("name", StringValidator(not_blank)),
            ("email", StringValidator(EmailPredicate(), MaxLength(50))),
            (
                "occupation",
                StringValidator(Choices({"teacher", "engineer", "musician", "cook"})),
            ),
            ("country_code", StringValidator(MinLength(2), MaxLength(3))),
            (
                "honorifics",
                TupleHomogenousValidator(
                    StringValidator(RegexPredicate(re.compile(r"[A-Z][a-z]+\.]"))),
                    predicates=[UniqueItems(), MinItems(1), MaxItems(3)],
                ),
            ),
        ),
        into=Person2,
    )

    assert generate_schema(person_validator_tuple) == schema


def test_cities() -> None:
    @dataclass
    class CityInfo:
        population: Optional[int]
        state: str

    state_choices: Set[str] = {"CA", "NY"}

    validate_cities = MapValidator(
        key=StringValidator(),
        value=RecordValidator(
            keys=(
                ("population", OptionalValidator(IntValidator(Min(0), Max(50_000_000)))),
                ("state", StringValidator(Choices(state_choices))),
            ),
            into=CityInfo,
        ),
        predicates=[MaxKeys(3), MinKeys(2)],
    )

    expected_schema = {
        "type": "object",
        "additionalProperties": {
            "additionalProperties": False,
            "type": "object",
            "required": ["population", "state"],
            "properties": {
                "population": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 50000000,
                    "nullable": True,
                },
                "state": {"type": "string", "enum": ["CA", "NY"]},
            },
        },
        "maxProperties": 3,
        "minProperties": 2,
    }

    # sanity check
    assert validate_cities(
        {
            "Oakland": {"population": 450000, "state": "CA"},
            "San Francisco": {"population": None, "state": "CA"},
        }
    ) == Valid(
        {
            "Oakland": CityInfo(450000, "CA"),
            "San Francisco": CityInfo(None, "CA"),
        }
    )

    validate_schema(expected_schema)
    assert generate_schema(validate_cities) == expected_schema


def test_auth_creds() -> None:
    @dataclass
    class UsernameCreds:
        username: str
        password: str

    @dataclass
    class EmailCreds:
        email: str
        password: str

    username_creds_validator = RecordValidator(
        keys=(
            ("username", StringValidator(not_blank)),
            ("password", StringValidator(not_blank)),
        ),
        into=UsernameCreds,
    )

    email_creds_validator = RecordValidator(
        keys=(
            ("email", StringValidator(EmailPredicate())),
            ("password", StringValidator(not_blank)),
        ),
        into=EmailCreds,
    )

    validator_one_of_2 = UnionValidatorIndexed.typed(
        username_creds_validator, email_creds_validator
    )

    # sanity check
    assert validator_one_of_2({"username": "a", "password": "b"}) == Valid(
        (0, UsernameCreds("a", "b"))
    )

    assert validator_one_of_2({"email": "a@example.com", "password": "b"}) == Valid(
        (1, EmailCreds("a@example.com", "b"))
    )

    assert generate_schema(validator_one_of_2) == {
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["username", "password"],
                "properties": {
                    "username": {"type": "string", "pattern": r"^(?!\s*$).+"},
                    "password": {"type": "string", "pattern": r"^(?!\s*$).+"},
                },
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "pattern": r"^(?!\s*$).+"},
                },
            },
        ]
    }

    @dataclass
    class Token:
        token: str

    validator_one_of_3 = UnionValidatorIndexed.typed(
        username_creds_validator,
        email_creds_validator,
        RecordValidator(
            keys=(("token", StringValidator(MinLength(32), MaxLength(32))),), into=Token
        ),
    )

    # sanity
    assert validator_one_of_3({"token": "abcdefghijklmnopqrstuvwxyz123456"}) == Valid(
        (2, Token("abcdefghijklmnopqrstuvwxyz123456"))
    )

    expected_schema = {
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["username", "password"],
                "properties": {
                    "username": {"type": "string", "pattern": r"^(?!\s*$).+"},
                    "password": {"type": "string", "pattern": r"^(?!\s*$).+"},
                },
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "pattern": r"^(?!\s*$).+"},
                },
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["token"],
                "properties": {
                    "token": {"type": "string", "minLength": 32, "maxLength": 32}
                },
            },
        ]
    }

    validate_schema(expected_schema)

    assert generate_schema(validator_one_of_3) == expected_schema

    union_validator = UnionValidator.typed(
        username_creds_validator,
        email_creds_validator,
        RecordValidator(
            keys=(("token", StringValidator(MinLength(32), MaxLength(32))),), into=Token
        ),
    )

    assert generate_schema(union_validator) == expected_schema


def test_forecast() -> None:
    validator = MapValidator(key=DateValidator(), value=FloatValidator())

    # sanity
    assert validator({"2021-04-06": 55.5, "2021-04-07": 57.9}) == Valid(
        {date(2021, 4, 6): 55.5, date(2021, 4, 7): 57.9}
    )

    assert generate_schema(validator) == {
        "type": "object",
        "additionalProperties": {"type": "number"},
    }


def test_tuples() -> None:
    validator = NTupleValidator.typed(
        fields=(
            StringValidator(not_blank),
            NTupleValidator.typed(
                fields=(StringValidator(), IntValidator(), BoolValidator())
            ),
        )
    )

    # sanity check
    assert validator(["ok", ["", 0, False]]) == Valid(("ok", ("", 0, False)))
    schema = generate_schema(validator)

    assert generate_schema(validator) == {
        "type": "array",
        "description": 'a 2-tuple of the fields in "prefixItems"',
        "maxItems": 2,
        "minItems": 2,
        "additionalItems": False,
        "prefixItems": [
            {"type": "string", "pattern": r"^(?!\s*$).+"},
            {
                "type": "array",
                "description": 'a 3-tuple of the fields in "prefixItems"',
                "additionalItems": False,
                "minItems": 3,
                "maxItems": 3,
                "prefixItems": [
                    {"type": "string"},
                    {"type": "integer"},
                    {"type": "boolean"},
                ],
            },
        ],
    }

    # will throw if bad
    validate_schema(schema)


def test_dict_validator_any() -> None:
    x = DictValidatorAny(
        {"name": StringValidator(), "age": KeyNotRequired(IntValidator())}
    )

    expected_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }

    validate_schema(expected_schema)
    assert generate_schema(x) == expected_schema


def test_dataclass_validator() -> None:
    @dataclass
    class Example:
        age: int
        name: str = "John Doe"

    x = DataclassValidator(Example)

    expected_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["age"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }

    validate_schema(expected_schema)
    assert generate_schema(x) == expected_schema


def test_namedtuple_validator() -> None:
    class Example(NamedTuple):
        age: int
        name: str = "John Doe"

    x = NamedTupleValidator(Example)

    expected_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["age"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }

    validate_schema(expected_schema)
    assert generate_schema(x) == expected_schema


def test_typeddict_validator() -> None:
    class Example(TypedDict):
        age: int
        name: str

    x = TypedDictValidator(Example)

    expected_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["age", "name"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }

    validate_schema(expected_schema)
    assert generate_schema(x) == expected_schema


def test_isdict_validator() -> None:
    expected_schema = {"type": "object"}

    validate_schema(expected_schema)
    assert generate_schema(is_dict_validator) == expected_schema


def test_equals_validator() -> None:
    expected_schema_int = {"type": "integer", "enum": [5]}

    validate_schema(expected_schema_int)
    assert generate_schema(EqualsValidator(5))

    expected_schema_str = {"type": "string", "enum": ["hooray"]}

    validate_schema(expected_schema_str)

    assert generate_schema(EqualsValidator("hooray")) == expected_schema_str

    expected_schema_str = {"type": "string", "format": "date", "enum": ["2022-12-12"]}

    validate_schema(expected_schema_str)

    assert generate_schema(EqualsValidator(date(2022, 12, 12))) == expected_schema_str

    uu = uuid.uuid4()
    expected_schema_uuid = {"type": "string", "format": "uuid", "enum": [str(uu)]}

    validate_schema(expected_schema_uuid)

    assert generate_schema(EqualsValidator(uu)) == expected_schema_uuid

    now_ = datetime.now()
    expected_schema_datetime = {
        "type": "string",
        "format": "date-time",
        "enum": [now_.isoformat()],
    }

    validate_schema(expected_schema_datetime)

    assert generate_schema(EqualsValidator(now_)) == expected_schema_datetime

    dec = Decimal("3.14")
    expected_schema_dec = {
        "type": "string",
        "format": "number",
        "pattern": r"^(\-|\+)?((\d+(\.\d*)?)|(\.\d+))$",
        "enum": ["3.14"],
    }

    validate_schema(expected_schema_dec)

    assert generate_schema(EqualsValidator(dec)) == expected_schema_dec

    bytes_ = b"abc123def456"
    expected_schema_bytes = {
        "type": "string",
        "format": "byte",
        "enum": [bytes_.decode("utf-8")],
    }

    validate_schema(expected_schema_bytes)

    assert generate_schema(EqualsValidator(bytes_)) == expected_schema_bytes


def test_bytes_validator() -> None:
    expected_schema_bytes = {"type": "string", "format": "byte", "maxLength": 12}

    validate_schema(expected_schema_bytes)

    assert generate_schema(BytesValidator(MaxLength(12))) == expected_schema_bytes


def test_decimal_validator() -> None:
    expected_schema_dec = {
        "type": "string",
        "format": "number",
        "pattern": r"^(\-|\+)?((\d+(\.\d*)?)|(\.\d+))$",
        "formatMaximum": "345.678",
        "formatExclusiveMinimum": "111.2",
    }

    validate_schema(expected_schema_dec)

    assert (
        generate_schema(
            DecimalValidator(
                Max(Decimal("345.678")), Min(Decimal("111.2"), exclusive_minimum=True)
            )
        )
        == expected_schema_dec
    )


def test_float_validator() -> None:
    expected_schema_float = {
        "type": "number",
        "exclusiveMaximum": 345.678,
    }

    validate_schema(expected_schema_float)

    assert generate_schema(FloatValidator(Max(345.678, True))) == expected_schema_float


def test_date_validator() -> None:
    min_date = date(2022, 12, 11)
    expected_schema_date = {
        "type": "string",
        "format": "date",
        "formatExclusiveMinimum": "2022-12-11",
    }

    validate_schema(expected_schema_date)

    assert (
        generate_schema(DateValidator(Min(min_date, exclusive_minimum=True)))
        == expected_schema_date
    )


def test_datetime_validator() -> None:
    max_dt = datetime.now()
    expected_schema_datetime = {
        "type": "string",
        "format": "date-time",
        "formatMaximum": max_dt.isoformat(),
    }

    validate_schema(expected_schema_datetime)

    assert generate_schema(DatetimeValidator(Max(max_dt))) == expected_schema_datetime


def test_uuid_validator() -> None:
    expected_schema_datetime = {
        "type": "string",
        "format": "uuid",
    }

    validate_schema(expected_schema_datetime)

    assert generate_schema(UUIDValidator()) == expected_schema_datetime
