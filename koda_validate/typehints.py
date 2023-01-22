import inspect
import sys
from dataclasses import is_dataclass
from datetime import date, datetime
from decimal import Decimal

from koda import Just, Nothing

from .is_type import TypeValidator
from .maybe import MaybeValidator

if sys.version_info >= (3, 9):
    from typing import Annotated

if sys.version_info >= (3, 10):
    from types import UnionType

if sys.version_info >= (3, 11):
    from typing import NotRequired, Required

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Set,
    Tuple,
    Union,
    get_args,
    get_origin,
)
from uuid import UUID

from ._internal import _is_typed_dict_cls
from .base import Validator
from .boolean import BoolValidator
from .bytes import BytesValidator
from .decimal import DecimalValidator
from .dictionary import MapValidator
from .float import FloatValidator
from .generic import Choices, EqualsValidator, always_valid
from .integer import IntValidator
from .list import ListValidator
from .none import NoneValidator, none_validator
from .set import SetValidator
from .string import StringValidator
from .time import DatetimeValidator, DateValidator
from .tuple import NTupleValidator, UniformTupleValidator
from .union import UnionValidator
from .uuid import UUIDValidator


def annotation_is_naked_tuple(annotation: Any) -> bool:
    return annotation is Tuple or annotation is tuple


def annotation_is_naked_list(annotation: Any) -> bool:
    return annotation is List or annotation is list


def annotation_is_namedtuple(annotation: Any) -> bool:
    return bool(
        (bases := getattr(annotation, "__bases__", None))
        and bases == (tuple,)
        and hasattr(annotation, "_fields")
    )


# todo: evolve into general-purpose type-hint driven validator
# will probably need significant changes
def get_typehint_validator_base(
    get_hint_next_depth: Callable[[Any], Validator[Any]], annotation: Any
) -> Validator[Any]:
    """
    get_hint_next_depth allows a developer to wrap this function but still have it
    use their wrapper recursively (otherwise we might simply recur to this function in
    each depth)

    :param get_hint_next_depth: the ``Callable`` that will determine the ``Validator``
        resolution at the next depth (usually this is the same at all depths)
    :param annotation: the type we're using to create a ``Validator``
    :return: a ``Validator`` that expresses the intent of the ``annotations``
    :raises TypeError: on types that are not handled
    """
    if annotation is str:
        return StringValidator()
    elif annotation is int:
        return IntValidator()
    elif annotation is float:
        return FloatValidator()
    elif annotation is None or annotation is type(None):  # noqa: E721
        return NoneValidator()
    elif annotation is UUID:
        return UUIDValidator()
    elif annotation is date:
        return DateValidator()
    elif annotation is datetime:
        return DatetimeValidator()
    elif annotation is bool:
        return BoolValidator()
    elif annotation is Decimal:
        return DecimalValidator()
    elif annotation is bytes:
        return BytesValidator()
    elif annotation is Any:
        return always_valid
    elif annotation_is_naked_list(annotation):
        return ListValidator(always_valid)
    elif annotation is Set or annotation is set:
        return SetValidator(always_valid)
    elif annotation_is_naked_tuple(annotation):
        return UniformTupleValidator(always_valid)
    elif annotation is Dict or annotation is dict:
        return MapValidator(key=always_valid, value=always_valid)
    elif is_dataclass(annotation):
        from .dataclasses import DataclassValidator

        return DataclassValidator(annotation)
    elif annotation_is_namedtuple(annotation):
        from .namedtuple import NamedTupleValidator

        return NamedTupleValidator(annotation)
    elif _is_typed_dict_cls(annotation):
        from .typeddict import TypedDictValidator

        return TypedDictValidator(annotation)
    else:
        origin, args = get_origin(annotation), get_args(annotation)
        if annotation_is_naked_list(origin) and len(args) == 1:
            item_validator = get_hint_next_depth(args[0])
            return ListValidator(item_validator)
        elif (origin is set or origin is Set) and len(args) == 1:
            item_validator = get_hint_next_depth(args[0])
            return SetValidator(item_validator)
        elif (origin is dict or origin is Dict) and len(args) == 2:
            return MapValidator(
                key=get_hint_next_depth(args[0]), value=get_hint_next_depth(args[1])
            )
        elif origin is Union or (sys.version_info >= (3, 10) and origin is UnionType):
            if len(args) == 2 and args[1] is Nothing and get_origin(args[0]) is Just:
                return MaybeValidator(get_hint_next_depth(get_args(args[0])[0]))
            else:
                return UnionValidator(*[get_hint_next_depth(arg) for arg in args])
        elif origin is tuple or origin is Tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return UniformTupleValidator(get_hint_next_depth(args[0]))
            else:
                return NTupleValidator.untyped(
                    fields=tuple(get_hint_next_depth(a) for a in args)
                )

        elif origin is Literal:
            # The common case is that literals will be of the same type. For those
            # cases, we return the relevant type validator (if we have it).
            if len(args) == 0:
                ValueError("Literal types cannot be empty")
            else:
                type_ = type(args[0])
                for a in args[1:]:
                    if type(a) is not type_:
                        break
                else:
                    if type_ is str:
                        return StringValidator(Choices(set(args)))
                    elif type_ is int:
                        return IntValidator(Choices(set(args)))
                    elif type_ is bool:
                        return BoolValidator(Choices(set(args)))
                    elif type_ is bytes:
                        return BytesValidator(Choices(set(args)))
                    elif type_ is type(None) or type_ is None:  # noqa: E721
                        return none_validator

            # ok, we have to use a union because we have multiple types
            # or we haven't defined an explicit validator to use
            return UnionValidator(*[EqualsValidator(a) for a in args])

        elif sys.version_info >= (3, 11) and (
            origin is NotRequired or origin is Required
        ):
            return get_typehint_validator(args[0])

        # not validating with annotations at this point
        elif sys.version_info >= (3, 9) and origin is Annotated:
            if len(args) == 1:
                return get_typehint_validator(args[0])
            else:
                # only return the first annotation validator
                for x in args:
                    if isinstance(x, Validator):
                        return x
        elif inspect.isclass(annotation):
            # fall back to an explicit type checker
            return TypeValidator(annotation)

        raise TypeError(f"Got unhandled annotation: {repr(annotation)}.")


def get_typehint_validator(annotation: Any) -> Validator[Any]:
    """
    The "default" way to convert typehints to `Validator`

    :param annotation: Any valid python annotation.
    :returns: a validator if it finds a match
    """
    return get_typehint_validator_base(get_typehint_validator, annotation)
