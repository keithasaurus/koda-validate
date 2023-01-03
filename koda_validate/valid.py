from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, Union

from koda_validate._generics import A
from koda_validate.errors import ErrType

if TYPE_CHECKING:
    from koda_validate.base import Validator


@dataclass
class Valid(Generic[A]):
    """
    A wrapper for valid data, e.g. ``Valid("abc")``
    """

    val: A

    is_valid: ClassVar[Literal[True]] = True
    """
    The value that has succeded validation 
    """
    """
    This is always ``True`` on ``Valid`` instances. It's useful for ``if`` statements, 
    and mypy understands it. 
    """


@dataclass
class Invalid:
    err_type: "ErrType"

    value: Any

    validator: "Validator[Any]"

    is_valid: ClassVar[Literal[False]] = False
    """
    Any of a number of classes that contain data about the type of error, e.g. 
    :class:`TypeErr`, :class:`CoercionErr`, :class:`KeyMissingErr`, etc.
    """
    """
    The invalid value that was being validated
    """
    """
    The validator that determined ``value`` to be invalid
    """
    """
    This is always ``False`` on :class:`Invalid` instances.  It’s useful for if 
    statements, and mypy understands it.
    """


ValidationResult = Union[Valid[A], Invalid]
