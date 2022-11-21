from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Hashable, List, Protocol, Tuple, Type, Union

from koda_validate._generics import A, InputT, SuccessT
from koda_validate.validated import Invalid, Valid, Validated


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

    compatible_types: List[Type[Any]]
    default_message: str


@dataclass
class DictErrs:
    container: List["_ValidationErr"]
    keys: Dict[Hashable, List["_ValidationErr"]]


@dataclass
class IterableErrs:
    container: List["ValidationErr"]
    items: Dict[int, List["_ValidationErr"]]


@dataclass
class VariantErrs:
    variants: List["ValidationErr"]


_ValidationErr = Union[
    CoercionErr,
    TypeErr,
    "Predicate",
    "PredicateAsync",
    DictErrs,
    IterableErrs,
    VariantErrs,
]
ValidationErr = Union[_ValidationErr, List[_ValidationErr]]


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


# When mypy enables recursive types by default
# Serializable = Union[
#    None, int, str, bool, float,
#    List["Serializable"], Tuple["Serializable", ...], Dict[str, "Serializable"]
# ]
Serializable1 = Union[
    None, int, str, bool, float, List[Any], Tuple[Any, ...], Dict[str, Any]
]
Serializable = Union[
    None,
    int,
    str,
    bool,
    float,
    List[Serializable1],
    Tuple[Serializable1, ...],
    Dict[str, Serializable1],
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
