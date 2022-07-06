import re
from dataclasses import dataclass
from datetime import date
from typing import List, Set, TypeVar

from koda.either import First, Second, Third
from koda.maybe import Just, Maybe, nothing
from koda.result import Ok

from koda_validate.openapi import generate_schema
from koda_validate.validation import (
    BooleanValidator,
    DateValidator,
    Dict1KeyValidator,
    Dict2KeysValidator,
    Dict5KeysValidator,
    Email,
    Enum,
    FloatValidator,
    IntValidator,
    Lazy,
    ListValidator,
    MapValidator,
    MaxItems,
    MaxLength,
    MaxProperties,
    Minimum,
    MinLength,
    MinProperties,
    Nullable,
    OneOf2,
    OneOf3,
    RegexValidator,
    StringValidator,
    Tuple2Validator,
    Tuple3Validator,
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

    def get_comment_recur() -> Dict2KeysValidator[str, List[Comment], Comment]:
        return comment_validator

    comment_validator: Dict2KeysValidator[
        str, List[Comment], Comment
    ] = Dict2KeysValidator(
        prop("name", StringValidator(not_blank)),
        prop("replies", ListValidator(Lazy(get_comment_recur))),
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

    person_validator = Dict5KeysValidator(
        prop("name", StringValidator(not_blank)),
        prop("email", StringValidator(Email(), MaxLength(50))),
        prop(
            "occupation",
            StringValidator(Enum({"teacher", "engineer", "musician", "cook"})),
        ),
        prop("country_code", StringValidator(MinLength(2), MaxLength(3))),
        prop(
            "honorifics",
            ListValidator(
                StringValidator(RegexValidator(re.compile(r"[A-Z][a-z]+\.]"))),
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

    validate_cities = MapValidator(
        StringValidator(),
        Dict2KeysValidator(
            prop("population", Nullable(IntValidator(Minimum(0)))),
            prop("state", StringValidator(Enum(state_choices))),
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
    ) == Ok(
        {
            "Oakland": CityInfo(Just(450000), "CA"),
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

    username_creds_validator = Dict2KeysValidator(
        prop("username", StringValidator(not_blank)),
        prop("password", StringValidator(not_blank)),
        into=UsernameCreds,
    )

    email_creds_validator = Dict2KeysValidator(
        prop("email", StringValidator(Email())),
        prop("password", StringValidator(not_blank)),
        into=EmailCreds,
    )

    validator_one_of_2 = OneOf2(username_creds_validator, email_creds_validator)

    # sanity check
    assert validator_one_of_2({"username": "a", "password": "b"}) == Ok(
        First(UsernameCreds("a", "b"))
    )

    assert validator_one_of_2({"email": "a@example.com", "password": "b"}) == Ok(
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
        Dict1KeyValidator(
            prop("token", StringValidator(MinLength(32), MaxLength(32))), into=Token
        ),
    )

    # sanity
    assert validator_one_of_3({"token": "abcdefghijklmnopqrstuvwxyz123456"}) == Ok(
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
    validator = MapValidator(DateValidator(), FloatValidator())

    # sanity
    assert validator({"2021-04-06": 55.5, "2021-04-07": 57.9}) == Ok(
        {date(2021, 4, 6): 55.5, date(2021, 4, 7): 57.9}
    )

    assert generate_schema("Forecast", validator) == {
        "Forecast": {"type": "object", "additionalProperties": {"type": "number"}}
    }


def test_tuples() -> None:
    validator = Tuple2Validator(
        StringValidator(not_blank),
        Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator()),
    )

    # sanity check
    assert validator(["ok", ["", 0, False]]) == Ok(("ok", ("", 0, False)))

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
