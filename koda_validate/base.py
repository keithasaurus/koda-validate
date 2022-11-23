from abc import abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Hashable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from koda_validate._generics import A, InputT, SuccessT
from koda_validate.validated import Invalid, Valid, Validated


@dataclass
class InvalidCoercion:
    """
    When an exact type is required but not found
    """

    compatible_types: List[Type[Any]]
    dest_type: Type[Any]
    message: str


@dataclass
class InvalidType:
    expected_type: Type[Any]
    message: str


class InvalidKeyMissing:
    _instance: ClassVar[Optional["InvalidKeyMissing"]] = None

    def __new__(cls) -> "InvalidKeyMissing":
        """
        Make `KeyMissingErr` a singleton, so we can do `is` checks if we want.
        """
        if cls._instance is None:
            cls._instance = super(InvalidKeyMissing, cls).__new__(cls)
        return cls._instance


@dataclass
class InvalidExtraKeys:
    expected_keys: Set[Hashable]


invalid_key_missing = InvalidKeyMissing()


@dataclass
class InvalidDict:
    keys: Dict[Hashable, "ValidationErr"]


@dataclass
class InvalidKeyVal:
    key: Optional["ValidationErr"]
    val: Optional["ValidationErr"]


@dataclass
class InvalidMap:
    keys: Dict[Hashable, InvalidKeyVal]


@dataclass
class InvalidIterable:
    indexes: Dict[int, "ValidationErr"]


@dataclass
class InvalidVariants:
    variants: List["ValidationErr"]


@dataclass
class InvalidCustom:
    message: str


ValidationErr = Union[
    InvalidCoercion,
    InvalidCustom,
    InvalidDict,
    InvalidExtraKeys,
    InvalidIterable,
    InvalidKeyMissing,
    InvalidMap,
    InvalidType,
    InvalidVariants,
    # to: consider properly parameterizing
    List[Union["Predicate[Any]", "PredicateAsync[Any]"]],
]


ValidationResult = Validated[A, ValidationErr]


class Validator(Generic[InputT, SuccessT]):
    """
    Essentially a `Callable[[A], Result[B, ValidationErr]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    def __call__(self, val: InputT) -> ValidationResult[SuccessT]:
        raise NotImplementedError  # pragma: no cover

    async def validate_async(self, val: InputT) -> ValidationResult[SuccessT]:
        """
        make it possible for all validators to be async-compatible
        """
        raise NotImplementedError  # pragma: no cover


class Predicate(Generic[InputT]):
    """
    The important aspect of a `Predicate` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).

    Compatible with Async / but async behavior is _not_ customizable. that's
    why we have PredicateAsync. Any IO needs should probably go there!
    """

    err_message: str

    @abstractmethod
    def __call__(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError


class PredicateAsync(Generic[InputT]):
    """
    For async-only validation.
    """

    err_message: str

    @abstractmethod
    async def validate_async(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError


Serializable = Union[
    None,
    int,
    str,
    bool,
    float,
    List["Serializable"],
    Tuple["Serializable", ...],
    Dict[str, "Serializable"],
]


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError


# should look like this, but mypy doesn't understand it as of 0.982
# _ResultTuple = Union[Tuple[Literal[True], A], Tuple[Literal[False], FailT]]
_ResultTupleUnsafe = Tuple[bool, Any]


class _ToTupleValidatorUnsafe(Validator[InputT, SuccessT]):
    """
    This `Validator` subclass exists for optimization. When we call
    nested validators it's much less computation to deal with simple
    tuples and bools, instead of Valid and Invalid instances.
    This class may go away!

    DO NOT USE THIS UNLESS YOU:
    - ARE OK WITH THIS DISAPPEARING IN A FUTURE RELEASE
    - ARE GOING TO TEST YOUR CODE EXTENSIVELY
    """

    def validate_to_tuple(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError  # pragma: no cover

    def __call__(self, val: InputT) -> ValidationResult[SuccessT]:
        valid, result_val = self.validate_to_tuple(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)

    async def validate_to_tuple_async(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError  # pragma: no cover

    async def validate_async(self, val: InputT) -> ValidationResult[SuccessT]:
        valid, result_val = await self.validate_to_tuple_async(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)
