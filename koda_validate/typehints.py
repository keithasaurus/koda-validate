import sys
from dataclasses import is_dataclass
from datetime import date, datetime
from decimal import Decimal

from koda import Just, Nothing

from .maybe import MaybeValidator

if sys.version_info >= (3, 10):
    from types import UnionType
from typing import Any, Dict, List, Literal, Set, Tuple, Union, get_args, get_origin
from uuid import UUID

from ._internal import _is_typed_dict_cls
from .base import Validator
from .boolean import BoolValidator
from .bytes import BytesValidator
from .decimal import DecimalValidator
from .dictionary import MapValidator
from .float import FloatValidator
from .generic import EqualsValidator, always_valid
from .integer import IntValidator
from .list import ListValidator
from .none import NoneValidator
from .set import SetValidator
from .string import StringValidator
from .time import DatetimeValidator, DateValidator
from .tuple import NTupleValidator, UniformTupleValidator
from .union import UnionValidator
from .uuid import UUIDValidator


# todo: evolve into general-purpose type-hint driven validator
# will probably need significant changes
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
        return UniformTupleValidator(always_valid)
    elif annotations is Dict or annotations is dict:
        return MapValidator(key=always_valid, value=always_valid)
    elif is_dataclass(annotations):
        from .dataclasses import DataclassValidator

        return DataclassValidator(annotations)
    elif (
        (bases := getattr(annotations, "__bases__", None))
        and bases == (tuple,)
        and hasattr(annotations, "_fields")
    ):
        from .namedtuple import NamedTupleValidator

        return NamedTupleValidator(annotations)
    elif _is_typed_dict_cls(annotations):
        from .typeddict import TypedDictValidator

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
            if len(args) == 2 and args[1] is Nothing and get_origin(args[0]) is Just:
                return MaybeValidator(get_typehint_validator(get_args(args[0])[0]))
            else:
                return UnionValidator(*[get_typehint_validator(arg) for arg in args])
        if origin is tuple or origin is Tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return UniformTupleValidator(get_typehint_validator(args[0]))
            else:
                return NTupleValidator.untyped(
                    fields=tuple(get_typehint_validator(a) for a in args)
                )
        # not validating with annotations at this point
        # if sys.version_info >= (3, 9) and origin is Annotated:
        #     return get_typehint_validator(args[0])
        if origin is Literal:
            return UnionValidator(*[EqualsValidator(a) for a in args])

        raise TypeError(f"Got unhandled annotation: {repr(annotations)}.")
