from __future__ import annotations

from abc import abstractmethod
from typing import Any, Generic, Union, final

from koda import Err, Ok, Result

from koda_validate._cruft import _ValidatorFunc
from koda_validate._generics import A, B, FailT

ValidatorFunc = _ValidatorFunc[A, B, FailT]


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


_JSONValue1 = Union[None, int, str, bool, float, list[Any], dict[str, Any]]
JSONValue = Union[None, int, str, bool, float, list[_JSONValue1], dict[str, _JSONValue1]]


class PredicateJson(Predicate[A, JSONValue]):
    """
    This class only exists as a convenience. If the error
    messages you're writing are `str`, you can override
    `err_message_str` method and simply return a string.

    Otherwise you can override the `err_message` method
    and return any kind of `Jsonish`
    """

    @abstractmethod
    def err_message_str(self, val: A) -> str:
        raise NotImplementedError

    def err_message(self, val: A) -> JSONValue:
        return self.err_message_str(val)
