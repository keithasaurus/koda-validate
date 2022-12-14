from abc import abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Hashable,
    List,
    Literal,
    Optional,
    Set,
    Type,
    Union,
)

from koda_validate._generics import A, SuccessT


@dataclass
class CoercionErr:
    """
    When one or more types can be coerced to a destination type
    """

    compatible_types: Set[Type[Any]]
    dest_type: Type[Any]


@dataclass
class ContainerErr:
    child: "Invalid"


class MissingKeyErr:
    """
    A key is missing from a dictionary
    """

    _instance: ClassVar[Optional["MissingKeyErr"]] = None

    def __new__(cls) -> "MissingKeyErr":
        """
        Make a singleton
        """
        if cls._instance is None:
            cls._instance = super(MissingKeyErr, cls).__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


missing_key_err = MissingKeyErr()


@dataclass
class ExtraKeysErr:
    """
    extra keys were present in a dictionary
    """

    expected_keys: Set[Hashable]


@dataclass
class KeyErrs:
    """
    validation failures for key/value pairs on a record-like
    dictionary
    """

    keys: Dict[Any, "Invalid"]


@dataclass
class KeyValErrs:
    """
    key and/or value errors from a single key/value pair
    """

    key: Optional["Invalid"]
    val: Optional["Invalid"]


@dataclass
class MapErr:
    """
    errors from key/value pairs of a map-like dictionary
    """

    keys: Dict[Any, KeyValErrs]


@dataclass
class IndexErrs:
    """
    dictionary of validation errors by index
    """

    indexes: Dict[int, "Invalid"]


@dataclass
class SetErrs:
    item_errs: List["Invalid"]


@dataclass
class VariantErrs:
    """
    none of these validators was satisfied by a given value
    """

    variants: List["Invalid"]


@dataclass
class PredicateErrs(Generic[A]):
    """
    A grouping of failed Predicates
    """

    predicates: List[Union["Predicate[A]", "PredicateAsync[A]"]]


@dataclass
class BasicErr:
    """
    If all you want to do is produce a message, this can be useful
    """

    err_message: str


class ValidationErrBase:
    """
    This class exists only to provide a class to subclass if desired
    """

    pass


@dataclass
class TypeErr:
    """
    A specific type was required but not provided
    """

    expected_type: Type[Any]


@dataclass
class Valid(Generic[A]):
    val: A
    is_valid: ClassVar[Literal[True]] = True


@dataclass
class Invalid:
    err_type: "ErrType"
    value: Any
    validator: "Validator[Any]"

    is_valid: ClassVar[Literal[False]] = False


ValidationResult = Union[Valid[A], Invalid]

ErrType = Union[
    BasicErr,
    CoercionErr,
    ContainerErr,
    ExtraKeysErr,
    IndexErrs,
    KeyErrs,
    MapErr,
    MissingKeyErr,
    PredicateErrs,
    SetErrs,
    TypeErr,
    ValidationErrBase,
    VariantErrs,
]


class Validator(Generic[SuccessT]):
    """
    Essentially a `Callable[[Any], Result[SuccessT, ValidationErr]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    async def validate_async(self, val: Any) -> ValidationResult[SuccessT]:
        """
        make it possible for all validators to be async-compatible
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, val: Any) -> ValidationResult[SuccessT]:
        raise NotImplementedError()  # pragma: no cover


class Predicate(Generic[A]):
    """
    The important aspect of a `Predicate` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).

    Compatible with Async / but async behavior is _not_ customizable. that's
    why we have PredicateAsync. Any IO needs should probably go there!
    """

    @abstractmethod
    def __call__(self, val: A) -> bool:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover


class PredicateAsync(Generic[A]):
    """
    For async-only validation.
    """

    @abstractmethod
    async def validate_async(self, val: A) -> bool:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover
