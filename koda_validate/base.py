from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Type, Union

from koda_validate._generics import A, InputT, SuccessT
from koda_validate.validated import Validated


class InvalidBase:
    pass


@dataclass
class ValidatorErrorBase:
    """
    Simple base class which merely includes the originating validator for transparency
    """

    validator: "Validator[Any, Any]"


@dataclass
class InvalidCoercion(ValidatorErrorBase):
    """
    When one or more types can be coerced to a destination type
    """

    compatible_types: List[Type[Any]]
    dest_type: Type[Any]


class InvalidMissingKey(ValidatorErrorBase):
    """
    A key is missing from a dictionary
    """


@dataclass
class InvalidExtraKeys(ValidatorErrorBase):
    """
    extra keys were present in a dictionary
    """

    expected_keys: Set[Hashable]


@dataclass
class InvalidDict(ValidatorErrorBase):
    """
    validation failures for key/value pairs on a record-like
    dictionary
    """

    # todo: add validator, rename
    keys: Dict[Hashable, "ValidationErr"]


@dataclass
class InvalidKeyVal:
    """
    key and/or value errors from a single key/value pair
    """

    key: Optional["ValidationErr"]
    val: Optional["ValidationErr"]


@dataclass
class InvalidMap(ValidatorErrorBase):
    """
    errors from key/value pairs of a map-like dictionary
    """

    keys: Dict[Hashable, InvalidKeyVal]


@dataclass
class InvalidIterable(ValidatorErrorBase):
    """
    dictionary of validation errors by index
    """

    indexes: Dict[int, "ValidationErr"]


@dataclass
class InvalidVariants(ValidatorErrorBase):
    """
    none of these validators was satisfied by a given value
    """

    variants: List["ValidationErr"]


@dataclass
class InvalidPredicates(Generic[A], ValidatorErrorBase):
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
class InvalidType(ValidatorErrorBase):
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

ValidationResult = Validated[A, ValidationErr]


class Validator(Generic[InputT, SuccessT]):
    """
    Essentially a `Callable[[A], Result[B, ValidationErr]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    async def validate_async(self, val: InputT) -> ValidationResult[SuccessT]:
        """
        make it possible for all validators to be async-compatible
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, val: InputT) -> ValidationResult[SuccessT]:
        raise NotImplementedError()  # pragma: no cover


class Predicate(Generic[InputT]):
    """
    The important aspect of a `Predicate` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).

    Compatible with Async / but async behavior is _not_ customizable. that's
    why we have PredicateAsync. Any IO needs should probably go there!
    """

    @abstractmethod
    def __call__(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover


class PredicateAsync(Generic[InputT]):
    """
    For async-only validation.
    """

    @abstractmethod
    async def validate_async(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover
