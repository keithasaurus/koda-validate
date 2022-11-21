from dataclasses import dataclass
from typing import Any, Dict, Generic, Hashable, List, Protocol, Type, Union
from uuid import UUID

from koda_validate._generics import A


@dataclass
class CoercionErr:
    """
    When one or more types might be valid for a given destination type
    """

    allowed_types: List[Type[Any]]
    dest_type: Type[Any]
    default_message: str


@dataclass
class TypeErr:
    """
    When an exact type is required but not found
    """

    expected_type: Type[Any]
    default_message: str


@dataclass
class ValueErr:
    default_message: str


@dataclass
class LimitErr(ValueErr):
    limit: int


@dataclass
class MaxStrLenErr(LimitErr):
    pass


@dataclass
class MinStrLenErr(LimitErr):
    pass


@dataclass
class DictErrs:
    container: List["_ValidationErr"]
    keys: Dict[Hashable, List["_ValidationErr"]]


@dataclass
class IterableErrs:
    container: List["_ValidationErr"]
    items: Dict[int, List["_ValidationErr"]]


@dataclass
class VariantErrs:
    variants: List["_ValidationErr"]


_ValidationErr = Union[
    CoercionErr,
    TypeErr,
    ValueErr,
    DictErrs,
    IterableErrs,
    VariantErrs,
    List["_ValidationErr"],
]

ValidationErr = Union[_ValidationErr, List[_ValidationErr]]
