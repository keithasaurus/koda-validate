from abc import abstractmethod
from typing import Callable, Generic, final

from koda_validate._cruft import _chain, _validate_and_map, _Validator
from koda.result import Err, Result, Ok


__all__ = (
    "chain",
    "PredicateValidator",
    "validate_and_map",
    "TransformableValidator",
    "Validator",
    "Predicate"
)

from koda_validate._generics import A, B, FailT

Validator = _Validator[A, B, FailT]

Predicate = Callable[[A], bool]


class TransformableValidator(Generic[A, B, FailT]):
    """
    A Callable exactly as the `Validator` type alias requires, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.

    Not using protocol because we want it to be runtime checkable without
    being implicit or a false positive.
    """

    @abstractmethod
    def __call__(self, val: A) -> Result[B, FailT]:
        raise NotImplementedError


class PredicateValidator(Generic[A, FailT]):
    """
    The important aspect of a `PredicateValidator` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).
    """

    @abstractmethod
    def is_valid(self, val: A) -> bool:
        raise NotImplementedError

    @abstractmethod
    def err_message(self, val: A) -> FailT:
        raise NotImplementedError

    @final
    def __call__(self, val: A) -> Result[A, FailT]:
        if self.is_valid(val) is True:
            return Ok(val)
        else:
            return Err(self.err_message(val))


chain = _chain

validate_and_map = _validate_and_map
