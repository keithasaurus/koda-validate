from typing import List, TypedDict

import pytest

from koda_validate import IntValidator, ListValidator, StringValidator
from koda_validate.base import (
    IndexErrs,
    Invalid,
    KeyErrs,
    TypeErr,
    Valid,
    missing_key_err,
)
from koda_validate.typeddict import TypedDictValidator


class PersonSimpleTD(TypedDict):
    name: str
    age: int


def test_valid_dict_returns_dataclass_result() -> None:
    assert TypedDictValidator(PersonSimpleTD)({"name": "bob", "age": 100}) == Valid(
        {"name": "bob", "age": 100}
    )


def test_nested_typeddict() -> None:
    class Group(TypedDict):
        group_name: str
        people: List[PersonSimpleTD]

    valid_dict = {
        "group_name": "some_group",
        "people": [
            {"name": "alice", "age": 1},
            {"name": "bob", "age": 10},
        ],
    }
    v = TypedDictValidator(Group)

    assert v(valid_dict) == Valid(valid_dict)
    assert v({}) == Invalid(
        err_type=KeyErrs(
            keys={
                "group_name": Invalid(err_type=missing_key_err, value={}, validator=v),
                "people": Invalid(missing_key_err, value={}, validator=v),
            }
        ),
        value={},
        validator=v,
    )
    assert v(
        {"group_name": "something", "people": ["bad", {"name": 1, "age": "2"}]}
    ) == Invalid(
        err_type=KeyErrs(
            keys={
                "people": Invalid(
                    IndexErrs(
                        {
                            0: Invalid(
                                TypeErr(dict), "bad", TypedDictValidator(PersonSimpleTD)
                            ),
                            1: Invalid(
                                KeyErrs(
                                    keys={
                                        "age": Invalid(
                                            TypeErr(expected_type=int),
                                            "2",
                                            IntValidator(),
                                        ),
                                        "name": Invalid(
                                            TypeErr(expected_type=str),
                                            1,
                                            StringValidator(),
                                        ),
                                    }
                                ),
                                {"age": "2", "name": 1},
                                TypedDictValidator(PersonSimpleTD),
                            ),
                        }
                    ),
                    ["bad", {"age": "2", "name": 1}],
                    ListValidator(TypedDictValidator(PersonSimpleTD)),
                )
            }
        ),
        value={"group_name": "something", "people": ["bad", {"age": "2", "name": 1}]},
        validator=v,
    )


@pytest.mark.asyncio
async def test_valid_dict_returns_dataclass_result_async() -> None:
    assert await TypedDictValidator(PersonSimpleTD).validate_async(
        {"name": "bob", "age": 100}
    ) == Valid({"name": "bob", "age": 100})
