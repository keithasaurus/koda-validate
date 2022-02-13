from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, final, Union, Tuple, List, Dict

from koda_validate._cruft import _Validator
from koda.result import Err, Result, Ok

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


@dataclass(frozen=True)
class JO:
    """
    JO => "Json Object" -- brief for less visual disruption. "Jsonable"
    or "JSONObj" may be good candidates if explicitness is needed at some point.

    We need to specifically define validators whose error messages can be
    serialized into json. Because of a lack of feasibility recursive types
    in both pyright and mypy (currently), as well as some issues working
    with unions, we are currently defining This Jsonable type type.
    """

    val: Union[
        str,
        int,
        float,
        bool,
        None,
        Tuple["JO", ...],
        List["JO"],
        Dict[str, "JO"],
    ]


class PredicateValidatorJO(PredicateValidator[A, JO]):
    """
    This class only exists as a convenience. If the error
    messages you're writing are `str`, you can override
    `err_message_str` method and simply return a string.

    Otherwise you can override the `err_message` method
    and return any kind of `JO`
    """
    @abstractmethod
    def err_message_str(self, val: A) -> str:
        raise NotImplementedError

    def err_message(self, val: A) -> JO:
        return JO(self.err_message_str(val))
