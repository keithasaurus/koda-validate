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
class InvalidCoercion:
    """
    When one or more types can be coerced to a destination type
    """

    compatible_types: List[Type[Any]]
    dest_type: Type[Any]


class InvalidMissingKey:
    """
    A key is missing from a dictionary
    """

    _instance: ClassVar["InvalidMissingKey"] = None

    def __new__(cls) -> "InvalidMissingKey":
        """
        Make a singleton
        """
        if cls._instance is None:
            cls._instance = super(InvalidMissingKey, cls).__new__(cls)
        return cls._instance


invalid_missing_key = InvalidMissingKey()


@dataclass
class InvalidExtraKeys:
    """
    extra keys were present in a dictionary
    """

    expected_keys: Set[Hashable]


@dataclass
class InvalidDict:
    """
    validation failures for key/value pairs on a record-like
    dictionary
    """

    # todo: add validator, rename
    keys: Dict[Any, "Invalid"]


@dataclass
class InvalidKeyVal:
    """
    key and/or value errors from a single key/value pair
    """

    key: Optional["Invalid"]
    val: Optional["Invalid"]


@dataclass
class InvalidMap:
    """
    errors from key/value pairs of a map-like dictionary
    """

    keys: Dict[Any, InvalidKeyVal]


@dataclass
class InvalidIterable:
    """
    dictionary of validation errors by index
    """

    indexes: Dict[int, "Invalid"]


@dataclass
class InvalidVariants:
    """
    none of these validators was satisfied by a given value
    """

    variants: List["Invalid"]


@dataclass
class InvalidPredicates(Generic[A]):
    """
    A grouping of failed Predicates
    """

    predicates: List[Union["Predicate[A]", "PredicateAsync[A]"]]


@dataclass
class InvalidSimple:
    """
    If all you want to do is produce a message, this can be useful
    """

    err_message: str


@dataclass
class InvalidType:
    """
    A specific type was required but not provided
    """

    expected_type: Type[Any]


class Valid(Generic[A]):
    __match_args__ = ("val",)

    is_valid: ClassVar[Literal[True]] = True

    def __init__(self, val: A) -> None:
        self.val: A = val

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Valid) and other.val == self.val

    def __repr__(self) -> str:
        return f"Valid({repr(self.val)})"


ErrorDetail = Union[
    InvalidCoercion,
    InvalidDict,
    InvalidExtraKeys,
    InvalidIterable,
    InvalidMap,
    InvalidMissingKey,
    InvalidPredicates,
    InvalidSimple,
    InvalidType,
    InvalidVariants,
]


class Invalid:
    __match_args__ = ("val",)

    is_valid: ClassVar[Literal[False]] = False

    def __init__(self, validator: "Validator[Any]", error_detail: ErrorDetail) -> None:
        self.validator = validator
        self.error_detail = error_detail

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Invalid)
            and other.validator == self.validator
            and other.error_detail == self.error_detail
        )

    def __repr__(self) -> str:
        return f"Invalid(validator={repr(self.validator)}, error_detail={repr(self.error_detail)})"


ValidationResult = Union[Valid[A], Invalid]


@dataclass
class ValidatorErrorBase:
    """
    Simple base class which merely includes the originating validator for transparency
    """

    validator: "Validator[Any]"


@dataclass
class ValidatorError(ValidatorErrorBase):
    details: Any


ValidationErr = Union[
    InvalidSimple,
    # todo: add explicit wrapper, consider properly parameterizing
    InvalidPredicates[Any],
    ValidatorErrorBase,
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
