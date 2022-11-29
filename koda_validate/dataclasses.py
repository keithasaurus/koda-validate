import sys
import typing
from dataclasses import is_dataclass
from decimal import Decimal

if sys.version_info >= (3, 10):
    from types import UnionType

from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from uuid import UUID

from koda_validate import (
    BoolValidator,
    DecimalValidator,
    DictValidatorAny,
    FloatValidator,
    IntValidator,
    ListValidator,
    MapValidator,
    NoneValidator,
    StringValidator,
    UUIDValidator,
    Validator,
    always_valid,
)
from koda_validate.base import (
    InvalidCoercion,
    ValidationResult,
    ValidatorErrorBase,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)
from koda_validate.tuple import TupleHomogenousValidator, TupleNValidatorAny
from koda_validate.union import UnionValidatorAny


class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


_DCT = TypeVar("_DCT", bound=DataclassLike)


# todo: evolve into general-purpose type-hint driven validator
def get_typehint_validator(annotations: Any) -> Validator[Any, Any]:
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
    elif annotations is bool:
        return BoolValidator()
    elif annotations is Decimal:
        return DecimalValidator()
    elif annotations is Any:
        return always_valid
    elif annotations is List or annotations is list:
        return ListValidator(always_valid)
    elif annotations is Tuple or annotations is tuple:
        return TupleHomogenousValidator(always_valid)
    elif annotations is Dict or annotations is dict:
        return MapValidator(key=always_valid, value=always_valid)
    elif is_dataclass(annotations):
        return DataclassValidator(annotations)
    else:
        origin, args = get_origin(annotations), get_args(annotations)
        if (origin is list or origin is List) and len(args) == 1:
            item_validator = get_typehint_validator(args[0])
            return ListValidator(item_validator)
        if (origin is dict or origin is Dict) and len(args) == 2:
            return MapValidator(
                key=get_typehint_validator(args[0]), value=get_typehint_validator(args[1])
            )
        if origin is Union or (sys.version_info >= (3, 10) and origin is UnionType):
            return UnionValidatorAny(*[get_typehint_validator(arg) for arg in args])
        if origin is tuple or origin is Tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return TupleHomogenousValidator(get_typehint_validator(args[0]))
            else:
                return TupleNValidatorAny(*[get_typehint_validator(a) for a in args])
        raise TypeError(f"got unhandled annotation: {type(annotations)}")


class DataclassValidator(_ToTupleValidatorUnsafe[Any, _DCT]):
    def __init__(
        self,
        data_cls: Type[_DCT],
        *,
        overrides: Optional[Dict[str, Validator[Any, Any]]] = None,
        validate_object: Optional[typing.Callable[[_DCT], ValidationResult[_DCT]]] = None,
    ) -> None:
        self.data_cls = data_cls
        overrides = overrides or {}
        if sys.version_info >= (3, 9):
            type_hints = get_type_hints(self.data_cls, include_extras=True)
        else:
            type_hints = get_type_hints(self.data_cls)

        self.validator = DictValidatorAny(
            {
                field: (
                    overrides[field]
                    if field in overrides
                    else get_typehint_validator(annotations)
                )
                for field, annotations in type_hints.items()
            }
        )
        self.validate_object = validate_object

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if isinstance(val, dict):
            success, new_val = self.validator.validate_to_tuple(val)
            if success:
                obj = self.data_cls(**new_val)
                if self.validate_object:
                    result = self.validate_object(obj)
                    if result.is_valid:
                        return True, result.val
                    else:
                        return False, result.val
                else:
                    return True, obj
            else:
                if isinstance(new_val, ValidatorErrorBase):
                    new_val.validator = self
                return False, new_val

        elif isinstance(val, self.data_cls):
            success, new_val = self.validator.validate_to_tuple(val.__dict__)

            if success:
                obj = self.data_cls(**new_val)
                if self.validate_object:
                    result = self.validate_object(obj)
                    if result.is_valid:
                        return True, result.val
                    else:
                        return False, result.val
                else:
                    return True, obj
            else:
                if isinstance(new_val, ValidatorErrorBase):
                    new_val.validator = self
                return False, new_val

        else:
            return False, InvalidCoercion(
                self,
                [dict, self.data_cls],
                self.data_cls,
            )
