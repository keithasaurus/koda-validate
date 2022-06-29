import re
from dataclasses import dataclass
from datetime import date
from typing import List, Set, TypeVar

from koda import First, Maybe, Second, Third, err, just, nothing, ok

from koda_validate.openapi import generate_schema
from koda_validate.validation import (
    ArrayOf,
    Boolean,
    Date,
    Email,
    Enum,
    Float,
    Integer,
    Lazy,
    MapOf,
    MaxItems,
    MaxLength,
    MaxProperties,
    Minimum,
    MinLength,
    MinProperties,
    Nullable,
    Obj1Prop,
    Obj2Props,
    Obj5Props,
    OneOf2,
    OneOf3,
    RegexValidator,
    String,
    Tuple2,
    Tuple3,
    not_blank,
    prop,
    unique_items,
)

A = TypeVar("A")
Ret = TypeVar("Ret")


def test_recursive_validator() -> None:
    @dataclass
    class Comment:
        name: str
        replies: List["Comment"]  # noqa: F821

    def get_comment_recur() -> Obj2Props[str, List[Comment], Comment]:
        return comment_validator

    comment_validator: Obj2Props[str, List[Comment], Comment] = Obj2Props(
        prop("name", String(not_blank)),
        prop("replies", ArrayOf(Lazy(get_comment_recur))),
        into=Comment,
    )

    assert generate_schema("Comment", comment_validator) == {
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

    person_validator = Obj5Props(
        prop("name", String(not_blank)),
        prop("email", String(Email(), MaxLength(50))),
        prop("occupation", String(Enum({"teacher", "engineer", "musician", "cook"}))),
        prop("country_code", String(MinLength(2), MaxLength(3))),
        prop(
            "honorifics",
            ArrayOf(
                String(RegexValidator(re.compile(r"[A-Z][a-z]+\.]"))),
                unique_items,
                MaxItems(3),
            ),
        ),
        into=Person,
    )

    assert generate_schema("Person", person_validator) == {
        "Person": {
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
                    "maxItems": 3,
                    "items": {"type": "string", "pattern": "[A-Z][a-z]+\\.]"},
                },
            },
        }
    }


def test_cities() -> None:
    @dataclass
    class CityInfo:
        population: Maybe[int]
        state: str

    state_choices: Set[str] = {"CA", "NY"}

    validate_cities = MapOf(
        String(),
        Obj2Props(
            prop("population", Nullable(Integer(Minimum(0)))),
            prop("state", String(Enum(state_choices))),
            into=CityInfo,
        ),
        MaxProperties(3),
        MinProperties(2),
    )

    # sanity check
    assert validate_cities(
        {
            "Oakland": {"population": 450000, "state": "CA"},
            "San Francisco": {"population": None, "state": "CA"},
        }
    ) == ok(
        {
            "Oakland": CityInfo(just(450000), "CA"),
            "San Francisco": CityInfo(nothing, "CA"),
        }
    )

    assert generate_schema("City", validate_cities) == {
        "City": {
            "type": "object",
            "additionalProperties": {
                "additionalProperties": False,
                "type": "object",
                "required": ["population", "state"],
                "properties": {
                    "population": {
                        "type": "integer",
                        "minimum": 0,
                        "exclusiveMinimum": False,
                        "nullable": True,
                    },
                    "state": {"type": "string", "enum": ["CA", "NY"]},
                },
            },
            "maxProperties": 3,
            "minProperties": 2,
        }
    }


def test_auth_creds() -> None:
    @dataclass
    class UsernameCreds:
        username: str
        password: str

    @dataclass
    class EmailCreds:
        email: str
        password: str

    username_creds_validator = Obj2Props(
        prop("username", String(not_blank)),
        prop("password", String(not_blank)),
        into=UsernameCreds,
    )

    email_creds_validator = Obj2Props(
        prop("email", String(Email())),
        prop("password", String(not_blank)),
        into=EmailCreds,
    )

    validator_one_of_2 = OneOf2(username_creds_validator, email_creds_validator)

    # sanity check
    assert validator_one_of_2({"username": "a", "password": "b"}) == ok(
        First(UsernameCreds("a", "b"))
    )

    assert validator_one_of_2({"email": "a@example.com", "password": "b"}) == ok(
        Second(EmailCreds("a@example.com", "b"))
    )

    assert generate_schema("AuthCreds", validator_one_of_2) == {
        "AuthCreds": {
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
    }

    @dataclass
    class Token:
        token: str

    validator_one_of_3 = OneOf3(
        username_creds_validator,
        email_creds_validator,
        Obj1Prop(prop("token", String(MinLength(32), MaxLength(32))), into=Token),
    )

    # sanity
    assert validator_one_of_3({"token": "abcdefghijklmnopqrstuvwxyz123456"}) == ok(
        Third(Token("abcdefghijklmnopqrstuvwxyz123456"))
    )

    assert generate_schema("AuthCreds", validator_one_of_3) == {
        "AuthCreds": {
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
    }


def test_forecast() -> None:
    validator = MapOf(Date(), Float())

    # sanity
    assert validator({"2021-04-06": 55.5, "2021-04-07": 57.9}) == ok(
        {date(2021, 4, 6): 55.5, date(2021, 4, 7): 57.9}
    )

    assert generate_schema("Forecast", validator) == {
        "Forecast": {"type": "object", "additionalProperties": {"type": "number"}}
    }


def test_tuples() -> None:
    validator = Tuple2(String(not_blank), Tuple3(String(), Integer(), Boolean()))

    # sanity check
    assert validator(["ok", ["", 0, False]]) == ok(("ok", ("", 0, False)))

    assert generate_schema("Tuples", validator) == {
        "Tuples": {
            "description": "a 2-tuple; schemas for slots are "
            'listed in order in "items" > "anyOf"',
            "type": "array",
            "maxItems": 2,
            "items": {
                "anyOf": [
                    {"type": "string", "pattern": r"^(?!\s*$).+"},
                    {
                        "description": "a 3-tuple; schemas for slots are "
                        'listed in order in "items" > "anyOf"',
                        "type": "array",
                        "maxItems": 3,
                        "items": {
                            "anyOf": [
                                {"type": "string"},
                                {"type": "integer"},
                                {"type": "boolean"},
                            ]
                        },
                    },
                ]
            },
        }
    }
