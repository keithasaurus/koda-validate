import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Set, Tuple, TypeVar

from koda import First, Second, Third
from openapi_spec_validator import validate_spec

from koda_validate import (
    BoolValidator,
    Choices,
    DateValidator,
    FloatValidator,
    IntValidator,
    Lazy,
    ListValidator,
    Max,
    MaxItems,
    Min,
    MinItems,
    NTupleValidator,
    OneOf2,
    OneOf3,
    OptionalValidator,
    Serializable,
    TupleHomogenousValidator,
    UnionValidator,
    UniqueItems,
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
)
from koda_validate.openapi import generate_named_schema, generate_schema
from koda_validate.string import (
    EmailPredicate,
    MaxLength,
    MinLength,
    RegexPredicate,
    StringValidator,
    not_blank,
)

A = TypeVar("A")
Ret = TypeVar("Ret")


def validate_schema(schema: Serializable) -> None:
    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "hmm",
            "version": "1.1.1",
        },
        "paths": {
            "/board": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {"application/json": {"schema": schema}},
                        }
                    }
                }
            }
        },
    }
    return validate_spec(spec)  # type: ignore


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

    schema: Serializable = {
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
                    "exclusiveMinimum": False,
                    "exclusiveMaximum": False,
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

    validate_schema(expected_schema)  # type: ignore
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

    validator_one_of_2 = OneOf2(username_creds_validator, email_creds_validator)

    # sanity check
    assert validator_one_of_2({"username": "a", "password": "b"}) == Valid(
        First(UsernameCreds("a", "b"))
    )

    assert validator_one_of_2({"email": "a@example.com", "password": "b"}) == Valid(
        Second(EmailCreds("a@example.com", "b"))
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

    validator_one_of_3 = OneOf3(
        username_creds_validator,
        email_creds_validator,
        RecordValidator(
            keys=(("token", StringValidator(MinLength(32), MaxLength(32))),), into=Token
        ),
    )

    # sanity
    assert validator_one_of_3({"token": "abcdefghijklmnopqrstuvwxyz123456"}) == Valid(
        Third(Token("abcdefghijklmnopqrstuvwxyz123456"))
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

    validate_schema(expected_schema)  # type: ignore

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
