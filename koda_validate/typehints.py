import sys
from dataclasses import is_dataclass
from datetime import date, datetime
from decimal import Decimal
from types import UnionType
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Set,
    Tuple,
    Union,
    _TypedDictMeta,
    get_args,
    get_origin,
)
from uuid import UUID

from .base import Validator
from .boolean import BoolValidator
from .bytes import BytesValidator
from .dataclasses import DataclassValidator
from .decimal import DecimalValidator
from .dictionary import MapValidator
from .float import FloatValidator
from .generic import EqualsValidator, always_valid
from .integer import IntValidator
from .list import ListValidator
from .namedtuple import NamedTupleValidator
from .none import NoneValidator
from .set import SetValidator
from .string import StringValidator
from .time import DatetimeValidator, DateValidator
from .tuple import NTupleValidator, TupleHomogenousValidator
from .typeddict import TypedDictValidator
from .union import UnionValidator
from .uuid import UUIDValidator


# todo: evolve into general-purpose type-hint driven validator
def get_typehint_validator(annotations: Any) -> Validator[Any]:
    if annotations is str:
        return StringValidator()
    elif annotations is int:
        return IntValidator()
    elif annotations is float:
        return FloatValidator()
    elif annotations is None or annotations is type(None):  # noqa: E721
        return NoneValidator()
    elif annotations is UUID:
        return UUIDValidator()
    elif annotations is date:
        return DateValidator()
    elif annotations is datetime:
        return DatetimeValidator()
    elif annotations is bool:
        return BoolValidator()
    elif annotations is Decimal:
        return DecimalValidator()
    elif annotations is bytes:
        return BytesValidator()
    elif annotations is Any:
        return always_valid
    elif annotations is List or annotations is list:
        return ListValidator(always_valid)
    elif annotations is Set or annotations is set:
        return SetValidator(always_valid)
    elif annotations is Tuple or annotations is tuple:
        return TupleHomogenousValidator(always_valid)
    elif annotations is Dict or annotations is dict:
        return MapValidator(key=always_valid, value=always_valid)
    elif is_dataclass(annotations):
        return DataclassValidator(annotations)
    elif (
        (bases := getattr(annotations, "__bases__", None))
        and bases == (tuple,)
        and hasattr(annotations, "_fields")
    ):
        return NamedTupleValidator(annotations)
    elif (
        hasattr(annotations, "__annotations__")
        and hasattr(annotations, "__total__")
        and hasattr(annotations, "keys")
    ):
        return TypedDictValidator(annotations)
    else:
        origin, args = get_origin(annotations), get_args(annotations)
        if (origin is list or origin is List) and len(args) == 1:
            item_validator = get_typehint_validator(args[0])
            return ListValidator(item_validator)
        if (origin is set or origin is Set) and len(args) == 1:
            item_validator = get_typehint_validator(args[0])
            return SetValidator(item_validator)
        if (origin is dict or origin is Dict) and len(args) == 2:
            return MapValidator(
                key=get_typehint_validator(args[0]), value=get_typehint_validator(args[1])
            )
        if origin is Union or (sys.version_info >= (3, 10) and origin is UnionType):
            return UnionValidator(*[get_typehint_validator(arg) for arg in args])
        if origin is tuple or origin is Tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return TupleHomogenousValidator(get_typehint_validator(args[0]))
            else:
                return NTupleValidator.untyped(
                    fields=tuple(get_typehint_validator(a) for a in args)
                )
        # not validating with annotations at this point
        # if sys.version_info >= (3, 9) and origin is Annotated:
        #     return get_typehint_validator(args[0])
        if origin is Literal:
            return UnionValidator(*[EqualsValidator(a) for a in args])

        # todo: change message (allow as parameter?)
        raise TypeError(
            f"There was an error handling annotation of type {type(annotations)}. "
            f"This can possibly be resolved by using the `overrides` parameter "
            f"to explicitly define a `Validator` for the related key."
        )
