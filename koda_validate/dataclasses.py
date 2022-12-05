import inspect
import sys
from dataclasses import is_dataclass
from decimal import Decimal

from koda_validate._internal import (
    ResultTuple,
    _ToTupleValidator,
    validate_dict_to_tuple,
    validate_dict_to_tuple_async,
)
from koda_validate.set import SetValidator

if sys.version_info >= (3, 10):
    from types import UnionType

from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    Annotated: Any = None

from uuid import UUID

from koda_validate import (
    BoolValidator,
    DecimalValidator,
    EqualsValidator,
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
from koda_validate.base import CoercionErr, ErrType, ExtraKeysErr, Invalid
from koda_validate.tuple import NTupleValidator, TupleHomogenousValidator
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
    elif annotations is Set or annotations is set:
        return SetValidator(always_valid)
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
        if (origin is set or origin is Set) and len(args) == 1:
            item_validator = get_typehint_validator(args[0])
            return SetValidator(item_validator)
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
                return NTupleValidator.untyped(
                    fields=tuple(get_typehint_validator(a) for a in args)
                )
        if sys.version_info >= (3, 9) and origin is Annotated:
            return get_typehint_validator(args[0])
        if origin is Literal:
            return UnionValidatorAny(*[EqualsValidator(a) for a in args])

        raise TypeError(
            f"There was an error handling annotation of type {type(annotations)}. "
            f"This can possibly be resolved by using the `overrides` parameter "
            f"to explicitly define a `Validator` for the related key."
        )


class DataclassValidator(_ToTupleValidator[_DCT]):
    def __init__(
        self,
        data_cls: Type[_DCT],
        *,
        overrides: Optional[Dict[str, Validator[Any]]] = None,
        validate_object: Optional[Callable[[_DCT], Optional[ErrType]]] = None,
    ) -> None:
        self.data_cls = data_cls
        overrides = overrides or {}
        if sys.version_info >= (3, 9):
            type_hints = get_type_hints(self.data_cls, include_extras=True)
        else:
            type_hints = get_type_hints(self.data_cls)

        keys_with_defaults: Set[str] = {
            k
            for k, v in inspect.signature(self.data_cls).parameters.items()
            if v.default != inspect.Parameter.empty
        }

        self.schema = {
            field: (
                overrides[field]
                if field in overrides
                else get_typehint_validator(annotations)
            )
            for field, annotations in type_hints.items()
        }

        self.validate_object = validate_object

        self._fast_keys: List[Tuple[Any, Validator[Any], bool, bool]] = [
            (
                key,
                val,
                key not in keys_with_defaults,
                isinstance(val, _ToTupleValidator),
            )
            for key, val in self.schema.items()
        ]
        self._unknown_keys_err: ExtraKeysErr = ExtraKeysErr(set(self.schema.keys()))

    def validate_to_tuple(self, val: Any) -> ResultTuple[_DCT]:
        if isinstance(val, dict):
            data = val
        elif isinstance(val, self.data_cls):
            data = val.__dict__
        else:
            return False, Invalid(
                self,
                val,
                CoercionErr(
                    {dict, self.data_cls},
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
                    return False, Invalid(self, obj, result)
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
                val,
                CoercionErr(
                    {dict, self.data_cls},
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
                    return False, Invalid(self, obj, result)
            else:
                return True, obj
