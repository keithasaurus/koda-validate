from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generic

from koda_validate._generics import A, SuccessT

if TYPE_CHECKING:
    from koda_validate.valid import ValidationResult


class Validator(Generic[SuccessT]):
    """
    Base class for all ``Validator``\s. It's little more than a
    ``Callable[[Any], Result[SuccessT, ValidationErr]]``, with two notable differences:

    - constructing ``Callable`` ``class``\es allows us to more easily make metadata
        from the validator available (as opposed to data being hidden inside a closure)
    - a ``.validate_async`` method is allowed, meaning a :class:`Validator` can be made
        to work in both sync and async contexts.

    Depending on your use case, you may want to implement the ``__call__`` method, the
    ``async_validate`` method, or both.
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
    A predicate just returns ``True`` or ``False`` for some condition.

    :class:`Predicate`\s  can be used during async validation, but
    :class:`PredicateAsync` should be used for any validation that *requires*
    ``asyncio``.

    Example :class:`Predicate`:

    .. testcode:: predsubclass

        from koda_validate import Predicate

        class GreaterThan(Predicate[int]):
            def __init__(self, limit: int) -> None:
                self.limit = limit

            def __call__(self, val: int) -> bool:
                return val > self.limit

    Usage

    .. doctest:: predsubclass

        >>> gt = GreaterThan(5)
        >>> gt(6)
        True
        >>> gt(1)
        False
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
    The async-only sibling of :class:`Predicate`.

    Example :class:`PredicateAsync`

    .. testcode:: predasyncsubclass

        import asyncio
        from koda_validate import PredicateAsync

        class UsernameInDB(PredicateAsync[str]):
            async def validate_async(self, val: str) -> bool:
                # pretend to call db
                await asyncio.sleep(.001)
                # dummy logic for example
                return len(val) == 3

    Usage

    .. doctest:: predasyncsubclass

        >>> asyncio.run(UsernameInDB().validate_async("abc"))
        True
        >>> asyncio.run(UsernameInDB().validate_async("abcdef"))
        False
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
    """
    Base class for ``Processor``\s: ``Callable``\s that can transform a value of one type
    to another value of the same type. Useful for things like ``strip``\-ping strings:

    .. testcode:: strip

        from dataclasses import dataclass
        from koda_validate import Processor

        @dataclass
        class Strip(Processor[str]):
            def __call__(self, val: str) -> str:
                return val.strip()


    Usage:

    .. doctest:: strip

        >>> strip = Strip()
        >>> strip(" abc ")
        'abc'
        >>> strip("def")
        'def'
    """

    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover
