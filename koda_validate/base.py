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


class ErrorDetail:
    pass


class Valid(Generic[A]):
    __match_args__ = ("val",)

    is_valid: ClassVar[Literal[True]] = True

    def __init__(self, val: A) -> None:
        self.val: A = val

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Valid) and other.val == self.val

    def __repr__(self) -> str:
        return f"Valid({repr(self.val)})"


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


Validated = Union[Valid[A], Invalid]


@dataclass
class ValidatorErrorBase:
    """
    Simple base class which merely includes the originating validator for transparency
    """

    validator: "Validator[Any]"


@dataclass
class ValidatorError(ValidatorErrorBase):
    details: Any


@dataclass
class InvalidCoercion(ErrorDetail):
    """
    When one or more types can be coerced to a destination type
    """

    compatible_types: List[Type[Any]]
    dest_type: Type[Any]


class InvalidMissingKey(ErrorDetail):
    """
    A key is missing from a dictionary
    """


@dataclass
class InvalidExtraKeys(ErrorDetail):
    """
    extra keys were present in a dictionary
    """

    expected_keys: Set[Hashable]


@dataclass
class InvalidDict(ErrorDetail):
    """
    validation failures for key/value pairs on a record-like
    dictionary
    """

    # todo: add validator, rename
    keys: Dict[Hashable, "ValidationErr"]


@dataclass
class InvalidKeyVal(ErrorDetail):
    """
    key and/or value errors from a single key/value pair
    """

    key: Optional["ValidationErr"]
    val: Optional["ValidationErr"]


@dataclass
class InvalidMap(ErrorDetail):
    """
    errors from key/value pairs of a map-like dictionary
    """

    keys: Dict[Hashable, InvalidKeyVal]


@dataclass
class InvalidIterable(ErrorDetail):
    """
    dictionary of validation errors by index
    """

    indexes: Dict[int, "ValidationErr"]


@dataclass
class InvalidVariants(ErrorDetail):
    """
    none of these validators was satisfied by a given value
    """

    variants: List[Invalid]


@dataclass
class InvalidPredicates(Generic[A], ErrorDetail):
    """
    A grouping of failed Predicates
    """

    predicates: List[Union["Predicate[A]", "PredicateAsync[A]"]]


@dataclass
class InvalidSimple(ErrorDetail):
    """
    If all you want to do is produce a message, this can be useful
    """

    err_message: str


@dataclass
class InvalidType(ErrorDetail):
    """
    A specific type was required but not provided
    """

    expected_type: Type[Any]


ValidationErr = Union[
    InvalidSimple,
    # todo: add explicit wrapper, consider properly parameterizing
    InvalidPredicates[Any],
    ValidatorErrorBase,
]

ValidationResult = Validated[A]


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
