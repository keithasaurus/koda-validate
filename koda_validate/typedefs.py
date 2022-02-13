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
class Jsonable:
    """
    We need to specifically define validators that work insofar as the
    error messages they produce can be serialized into json. Because of
    a lack of recursive types (currently), as well as some issues working
    with unions, we are currently defining a Jsonable type.
    """

    val: Union[
        str,
        int,
        float,
        bool,
        None,
        Tuple["Jsonable", ...],
        List["Jsonable"],
        Dict[str, "Jsonable"],
    ]