from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Hashable, Optional, Type, Union

from koda_validate._generics import A
from koda_validate.base import Predicate, PredicateAsync

if TYPE_CHECKING:
    from koda_validate.valid import Invalid


@dataclass
class CoercionErr:
    """
    Similar to a TypeErr, but when one or more types can be
    coerced to a destination type
    """

    compatible_types: set[Type[Any]]
    dest_type: Type[Any]


@dataclass
class ContainerErr:
    """
    This is for simple containers like `Maybe` or `Result`
    """

    child: "Invalid"


@dataclass
class ExtraKeysErr:
    """
    extra keys were present in a dictionary
    """

    expected_keys: set[Hashable]


@dataclass
class KeyErrs:
    """
    validation failures for key/value pairs on a record-like
    dictionary
    """

    keys: dict[Any, "Invalid"]


@dataclass
class KeyValErrs:
    """
    Key and/or value errors from a single key/value pair. This
    is useful for mapping collections.
    """

    key: Optional["Invalid"]
    val: Optional["Invalid"]


@dataclass
class MapErr:
    """
    errors from key/value pairs of a map-like dictionary
    """

    keys: dict[Any, KeyValErrs]


class MissingKeyErr:
    """
    A key is missing from a dictionary
    """

    _instance: ClassVar[Optional["MissingKeyErr"]] = None

    def __new__(cls) -> "MissingKeyErr":
        # make a singleton
        if cls._instance is None:
            cls._instance = super(MissingKeyErr, cls).__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


missing_key_err = MissingKeyErr()


@dataclass
class IndexErrs:
    """
    dictionary of validation errors by index
    """

    indexes: dict[int, "Invalid"]


@dataclass
class SetErrs:
    """
    Errors from items in a set.
    """

    item_errs: list["Invalid"]


@dataclass
class UnionErrs:
    """
    Errors from each variant of a union.
    """

    variants: list["Invalid"]


@dataclass
class PredicateErrs(Generic[A]):
    """
    A grouping of failed Predicates
    """

    predicates: list[Union["Predicate[A]", "PredicateAsync[A]"]]


class ValidationErrBase:
    """
    This class exists only to provide a class to subclass
    for custom error types
    """

    pass


@dataclass
class TypeErr:
    """
    A specific type was required but not found
    """

    expected_type: Type[Any]


ErrType = Union[
    CoercionErr,
    ContainerErr,
    ExtraKeysErr,
    IndexErrs,
    KeyErrs,
    MapErr,
    MissingKeyErr,
    # This seems like a type exception worth making..., but that might change in the
    # future. This is backwards compatible with existing code
    PredicateErrs[Any],
    SetErrs,
    TypeErr,
    ValidationErrBase,
    UnionErrs,
]
