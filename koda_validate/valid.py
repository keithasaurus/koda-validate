from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, Union

from koda_validate._generics import A
from koda_validate.errors import ErrType

if TYPE_CHECKING:
    from koda_validate.base import Validator


@dataclass
class Valid(Generic[A]):
    """
    All validators will wrap valid results with this case, e.g. `Valid("abc")`
    """

    val: A
    is_valid: ClassVar[Literal[True]] = True


@dataclass
class Invalid:
    err_type: "ErrType"
    value: Any
    validator: "Validator[Any]"

    is_valid: ClassVar[Literal[False]] = False


ValidationResult = Union[Valid[A], Invalid]
