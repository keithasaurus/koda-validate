import inspect
import sys
from dataclasses import is_dataclass
from decimal import Decimal

from koda_validate._internal import (
    ResultTuple,
    _repr_helper,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.boolean import BoolValidator
from koda_validate.bytes import BytesValidator
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import MapValidator
from koda_validate.float import FloatValidator
from koda_validate.generic import EqualsValidator, always_valid
from koda_validate.integer import IntValidator
from koda_validate.list import ListValidator
from koda_validate.none import NoneValidator
from koda_validate.set import SetValidator
from koda_validate.string import StringValidator
from koda_validate.uuid import UUIDValidator

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

from koda_validate.base import (
    CoercionErr,
    ErrType,
    ExtraKeysErr,
    Invalid,
    KeyErrs,
    Validator,
    missing_key_err,
)
from koda_validate.tuple import NTupleValidator, TupleHomogenousValidator
from koda_validate.union import UnionValidator


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
        if sys.version_info >= (3, 9) and origin is Annotated:
            return get_typehint_validator(args[0])
        if origin is Literal:
            return UnionValidator(*[EqualsValidator(a) for a in args])

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
        self._input_overrides = overrides  # for repr
        overrides = overrides or {}
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

        self._fast_keys_sync = []
        self._fast_keys_async = []
        for key, val in self.schema.items():
            is_required = key not in keys_with_defaults
            self._fast_keys_sync.append((key, _wrap_sync_validator(val), is_required))
            self._fast_keys_async.append((key, _wrap_async_validator(val), is_required))

        self._unknown_keys_err: ExtraKeysErr = ExtraKeysErr(set(self.schema.keys()))

    def validate_to_tuple(self, val: Any) -> ResultTuple[_DCT]:
        if isinstance(val, dict):
            data = val
        elif isinstance(val, self.data_cls):
            data = val.__dict__
        else:
            return False, Invalid(
                CoercionErr(
                    {dict, self.data_cls},
                    self.data_cls,
                ),
                val,
                self,
            )

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self.schema:
                return False, Invalid(self._unknown_keys_err, data, self)

        success_dict: Dict[Any, Any] = {}
        errs: Dict[Any, Invalid] = {}
        for key_, validator, key_required in self._fast_keys_sync:
            if key_ not in data:
                if key_required:
                    errs[key_] = Invalid(missing_key_err, data, self)
            else:
                success, new_val = validator(data[key_])

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    success_dict[key_] = new_val

        if errs:
            return False, Invalid(KeyErrs(errs), data, self)
        else:
            obj = self.data_cls(**success_dict)
            if self.validate_object:
                result = self.validate_object(obj)
                if result is None:
                    return True, obj
                else:
                    return False, Invalid(result, obj, self)
            else:
                return True, obj

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[_DCT]:
        if isinstance(val, dict):
            data = val
        elif isinstance(val, self.data_cls):
            data = val.__dict__
        else:
            return False, Invalid(
                CoercionErr(
                    {dict, self.data_cls},
                    self.data_cls,
                ),
                val,
                self,
            )

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self.schema:
                return False, Invalid(self._unknown_keys_err, data, self)

        success_dict: Dict[Any, Any] = {}
        errs: Dict[Any, Invalid] = {}
        for key_, validator, key_required in self._fast_keys_async:
            if key_ not in data:
                if key_required:
                    errs[key_] = Invalid(missing_key_err, data, self)
            else:
                success, new_val = await validator(data[key_])

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    success_dict[key_] = new_val

        if errs:
            return False, Invalid(KeyErrs(errs), data, self)
        else:
            obj = self.data_cls(**success_dict)
            if self.validate_object:
                result = self.validate_object(obj)
                if result is None:
                    return True, obj
                else:
                    return False, Invalid(result, obj, self)
            else:
                return True, obj

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.data_cls is other.data_cls
            and other.validate_object is self.validate_object
            and other._input_overrides == self._input_overrides
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.data_cls)]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("overrides", self._input_overrides),
                    ("validate_object", self.validate_object),
                ]
                if v
            ],
        )
