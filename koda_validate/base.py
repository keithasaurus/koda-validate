from abc import abstractmethod
from functools import partial
from typing import (
    Any,
    Dict,
    Generic,
    Hashable,
    List,
    Literal,
    Tuple,
    TypedDict,
    Union,
    final,
)

from koda_validate._generics import A, FailT, InputT, SuccessT
from koda_validate.validated import Invalid, Valid, Validated


class Validator(Generic[InputT, SuccessT, FailT]):
    """
    Essentially a `Callable[[A], Result[B, FailT]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    def __call__(self, val: InputT) -> Validated[SuccessT, FailT]:
        raise NotImplementedError  # pragma: no cover

    async def validate_async(self, val: InputT) -> Validated[SuccessT, FailT]:
        """
        make it possible for all validators to be async-compatible
        """
        raise NotImplementedError  # pragma: no cover


class Predicate(Generic[InputT, FailT]):
    """
    The important aspect of a `Predicate` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).

    Compatible with Async / but async behavior is _not_ customizable. that's
    why we have PredicateAsync. Any IO needs should probably go there!
    """

    @abstractmethod
    def is_valid(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError

    # potential optimization: allowing for a STATIC_ERR (or similar) class
    # attribute can result in ~3% speedup for predicates,
    # i.e. [pred.STATIC_ERR or pred.err(val) for pred in preds]
    @abstractmethod
    def err(self, val: InputT) -> FailT:  # pragma: no cover
        raise NotImplementedError

    @final
    def __call__(self, val: InputT) -> Validated[InputT, FailT]:
        if self.is_valid(val) is True:
            return Valid(val)
        else:
            return Invalid(self.err(val))


class PredicateAsync(Generic[InputT, FailT]):
    """
    For async-only validation.
    """

    @abstractmethod
    async def is_valid_async(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    async def err_async(self, val: InputT) -> FailT:  # pragma: no cover
        raise NotImplementedError

    @final
    async def validate_async(self, val: InputT) -> Validated[InputT, FailT]:
        if await self.is_valid_async(val) is True:
            return Valid(val)
        else:
            return Invalid(await self.err_async(val))


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

ErrType = Literal["type", "value"]


class ValidationError(TypedDict):
    err_type: ErrType
    code: str
    msg: str
    details: Serializable


def validation_error(
    err_type: ErrType, code: str, msg: str, details: Serializable = None
) -> ValidationError:
    return {"err_type": err_type, "code": code, "msg": msg, "details": details}


type_error = partial(validation_error, "type")
value_error = partial(validation_error, "value")

_Err1 = Union[ValidationError, dict[Any, Any]]
Err = Union[
    ValidationError,
    dict[Any, _Err1],
    # list[int, "Err"]
]


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError


# should look like this, but mypy doesn't understand it as of 0.982
# _ResultTuple = Union[Tuple[Literal[True], A], Tuple[Literal[False], FailT]]
_ResultTupleUnsafe = Tuple[bool, Any]


class _ToTupleValidatorUnsafe(Validator[InputT, SuccessT, FailT]):
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

    def __call__(self, val: InputT) -> Validated[SuccessT, FailT]:
        valid, result_val = self.validate_to_tuple(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)

    async def validate_to_tuple_async(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError  # pragma: no cover

    async def validate_async(self, val: InputT) -> Validated[SuccessT, FailT]:
        valid, result_val = await self.validate_to_tuple_async(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)
