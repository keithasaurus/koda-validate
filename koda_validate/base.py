from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generic

from koda_validate._generics import A, SuccessT

if TYPE_CHECKING:
    from koda_validate.valid import ValidationResult


class Validator(Generic[SuccessT]):
    """
    Essentially a `Callable[[Any], Result[SuccessT, ValidationErr]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    async def validate_async(self, val: Any) -> "ValidationResult[SuccessT]":
        """
        this must be implemented for asynchronous validation

        :param val: the value being validated
        :raises NotImplementedError: if not implemented on subclasses
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, val: Any) -> "ValidationResult[SuccessT]":
        """
        this must be implemented for synchronous validation

        :param val: the value being validated
        :raises NotImplementedError: if not implemented on subclasses
        """

        raise NotImplementedError()  # pragma: no cover


class Predicate(Generic[A]):
    """
    The important aspect of a `Predicate` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).

    Compatible with Async / but async behavior is _not_ customizable. that's
    why we have PredicateAsync. Any IO needs should probably go there!
    """

    @abstractmethod
    def __call__(self, val: A) -> bool:  # pragma: no cover
        """
        This must be implemented on ``Predicate`` subclasses

        :param val: the value being validated
        :raises NotImplementedError: if not defined in subclass
        """
        raise NotImplementedError()  # pragma: no cover


class PredicateAsync(Generic[A]):
    """
    For async-only validation.
    """

    @abstractmethod
    async def validate_async(self, val: A) -> bool:  # pragma: no cover
        """
        This must be implemented on ``PredicateAsync`` subclasses

        :param val: the value being validated
        :return: a bool indicating whether the condition is ``True`` for the value
        """
        raise NotImplementedError()  # pragma: no cover


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover
