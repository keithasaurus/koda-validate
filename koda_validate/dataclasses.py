import sys
import typing
from dataclasses import is_dataclass
from decimal import Decimal

from koda_validate._internal import (
    ResultTuple,
    _ToTupleValidator,
    validate_dict_to_tuple,
    validate_dict_to_tuple_async,
)

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
    ErrorDetail,
    Invalid,
    InvalidCoercion,
    InvalidExtraKeys,
    ValidationResult,
)
from koda_validate.tuple import TupleHomogenousValidator, TupleNValidatorAny
from koda_validate.union import UnionValidatorAny


class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


_DCT = TypeVar("_DCT", bound=DataclassLike)


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


class DataclassValidator(_ToTupleValidator[_DCT]):
    def __init__(
        self,
        data_cls: Type[_DCT],
        *,
        overrides: Optional[Dict[str, Validator[Any]]] = None,
        validate_object: Optional[typing.Callable[[_DCT], Optional[ErrorDetail]]] = None,
    ) -> None:
        self.data_cls = data_cls
        overrides = overrides or {}
        if sys.version_info >= (3, 9):
            type_hints = get_type_hints(self.data_cls, include_extras=True)
        else:
            type_hints = get_type_hints(self.data_cls)

        self.schema = {
            field: (
                overrides[field]
                if field in overrides
                else get_typehint_validator(annotations)
            )
            for field, annotations in type_hints.items()
        }

        self.validate_object = validate_object

        self._fast_keys: List[Tuple[typing.Hashable, Validator[Any], bool, bool]] = [
            (
                key,
                val,
                True,
                isinstance(val, _ToTupleValidator),
            )
            for key, val in self.schema.items()
        ]
        self._unknown_keys_err: Tuple[typing.Literal[False], Invalid] = False, Invalid(
            self, InvalidExtraKeys(set(self.schema.keys()))
        )

    def validate_to_tuple(self, val: Any) -> ResultTuple[_DCT]:
        if isinstance(val, dict):
            data = val
        elif isinstance(val, self.data_cls):
            data = val.__dict__
        else:
            return False, Invalid(
                self,
                InvalidCoercion(
                    [dict, self.data_cls],
                    self.data_cls,
                ),
            )

        result_tup = validate_dict_to_tuple(
            self, None, self._fast_keys, self.schema, self._unknown_keys_err, data
        )

        if not result_tup[0]:
            return False, result_tup[1]
        else:
            obj = self.data_cls(**result_tup[1])
            if self.validate_object:
                result = self.validate_object(obj)
                if result is None:
                    return True, obj
                else:
                    return False, Invalid(self, result)
            else:
                return True, obj

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[_DCT]:
        if isinstance(val, dict):
            data = val
        elif isinstance(val, self.data_cls):
            data = val.__dict__
        else:
            return False, Invalid(
                self,
                InvalidCoercion(
                    [dict, self.data_cls],
                    self.data_cls,
                ),
            )

        result_tup = await validate_dict_to_tuple_async(
            self, None, self._fast_keys, self.schema, self._unknown_keys_err, data
        )

        if not result_tup[0]:
            return False, result_tup[1]
        else:
            obj = self.data_cls(**result_tup[1])
            if self.validate_object:
                result = self.validate_object(obj)
                if result is None:
                    return True, obj
                else:
                    return False, Invalid(self, result)
            else:
                return True, obj
