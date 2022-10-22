from __future__ import annotations

from abc import abstractmethod
from typing import Callable, Generic, List, Union, final

from koda import Err, Ok, Result

from koda_validate._generics import A, B, FailT

ValidatorFunc = Callable[[A], Result[B, FailT]]


class Validator(Generic[A, B, FailT]):
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


class Predicate(Generic[A, FailT]):
    """
    The important aspect of a `Predicate` is that it is not
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


JSONValue = Union[None, int, str, bool, float, List["JSONValue"], dict[str, "JSONValue"]]


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:
        raise NotImplementedError
