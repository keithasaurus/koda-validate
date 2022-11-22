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
    Protocol,
    Set,
    Tuple,
    Type,
    Union,
)

from koda_validate._generics import A, InputT, SuccessT
from koda_validate.validated import Invalid, Valid, Validated


@dataclass
class CoercionErr:
    """
    When an exact type is required but not found
    """

    compatible_types: List[Type[Any]]
    dest_type: Type[Any]
    message: str


@dataclass
class TypeErr:
    type: Type[Any]
    message: str


class KeyMissingErr:
    _instance: ClassVar[Optional["KeyMissingErr"]] = None

    def __new__(cls) -> "KeyMissingErr":
        """
        Make `KeyMissingErr` a singleton, so we can do `is` checks if we want.
        """
        if cls._instance is None:
            cls._instance = super(KeyMissingErr, cls).__new__(cls)
        return cls._instance


@dataclass
class ExtraKeysErr:
    expected_keys: Set[Hashable]


key_missing_err = KeyMissingErr()


@dataclass
class DictErrs:
    keys: Dict[Hashable, "ValidationErr"]


@dataclass
class KeyValErrs:
    key: Optional["ValidationErr"]
    val: Optional["ValidationErr"]


@dataclass
class MapErrs:
    container: "ValidationErr"
    keys: Dict[Hashable, KeyValErrs]


@dataclass
class IterableErrs:
    container: "ValidationErr"
    items: Dict[int, "ValidationErr"]


@dataclass
class VariantErrs:
    variants: List["ValidationErr"]


@dataclass
class CustomErr:
    message: str


ValidationErr = Union[
    CoercionErr,
    CustomErr,
    DictErrs,
    ExtraKeysErr,
    IterableErrs,
    KeyMissingErr,
    MapErrs,
    TypeErr,
    VariantErrs,
    List[Union["Predicate", "PredicateAsync"]],
]


class Validator(Generic[InputT, SuccessT]):
    """
    Essentially a `Callable[[A], Result[B, ValidationErr]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    def __call__(self, val: InputT) -> Validated[SuccessT, ValidationErr]:
        raise NotImplementedError  # pragma: no cover

    async def validate_async(self, val: InputT) -> Validated[SuccessT, ValidationErr]:
        """
        make it possible for all validators to be async-compatible
        """
        raise NotImplementedError  # pragma: no cover


class Predicate(Protocol[InputT]):
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

    def __init__(self, err_message: str) -> None:
        self.err_message = err_message

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

    def __call__(self, val: InputT) -> Validated[SuccessT, ValidationErr]:
        valid, result_val = self.validate_to_tuple(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)

    async def validate_to_tuple_async(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError  # pragma: no cover

    async def validate_async(self, val: InputT) -> Validated[SuccessT, ValidationErr]:
        valid, result_val = await self.validate_to_tuple_async(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)
