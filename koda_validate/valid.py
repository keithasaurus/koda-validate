from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, Literal, Union

from koda_validate._generics import A, B
from koda_validate.errors import ErrType

if TYPE_CHECKING:
    from koda_validate.base import Validator


@dataclass
class Valid(Generic[A]):
    """
    A wrapper for valid data, e.g. ``Valid("abc")``
    """

    val: A
    """
    The value that has succeeded validation
    """

    is_valid: ClassVar[Literal[True]] = True
    """
    This is always ``True`` on :class:`Valid` instances. It's useful for ``if``
    statements. Mypy understands it as a tag for a tagged union.
    """

    def map(self, func: Callable[[A], B]) -> "ValidationResult[B]":
        return Valid(func(self.val))


@dataclass
class Invalid:
    """
    Represents validation failure. Contains relevant failure data so use case-specific
    error objects (or other data) can be produced.
    """

    err_type: "ErrType"
    """
    Any of a number of classes that contain data about the type of error, e.g.
    :class:`TypeErr`, :class:`CoercionErr`, :class:`KeyMissingErr`, etc.
    """

    value: Any
    """
    The invalid value that was being validated
    """

    validator: "Validator[Any]"
    """
    The validator that determined ``value`` to be invalid
    """

    is_valid: ClassVar[Literal[False]] = False
    """
    This is always ``False`` on :class:`Invalid` instances. It’s useful for ``if``
    statements. Mypy understands it as a tag for a tagged union.
    """

    def map(self, func: Callable[[Any], B]) -> "ValidationResult[B]":
        return self


ValidationResult = Union[Valid[A], Invalid]
