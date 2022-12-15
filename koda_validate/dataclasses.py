import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Dict,
    Optional,
    Protocol,
    Set,
    Type,
    TypeVar,
    get_type_hints,
)

from koda_validate._internal import (
    ResultTuple,
    _raise_cannot_define_validate_object_and_validate_object_async,
    _raise_validate_object_async_in_sync_mode,
    _repr_helper,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import (
    CoercionErr,
    ErrType,
    ExtraKeysErr,
    Invalid,
    KeyErrs,
    Validator,
    missing_key_err,
)
from koda_validate.typehints import get_typehint_validator


class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


_DCT = TypeVar("_DCT", bound=DataclassLike)


class DataclassValidator(_ToTupleValidator[_DCT]):
    __match_args__ = ("data_cls", "overrides", "fail_on_unknown_keys")

    def __init__(
        self,
        data_cls: Type[_DCT],
        *,
        overrides: Optional[Dict[str, Validator[Any]]] = None,
        validate_object: Optional[Callable[[_DCT], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[_DCT], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
        typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
    ) -> None:
        self.data_cls = data_cls
        self.fail_on_unknown_keys = fail_on_unknown_keys
        self.overrides = overrides or {}
        if validate_object and validate_object_async:
            _raise_cannot_define_validate_object_and_validate_object_async()

        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        type_hints = get_type_hints(self.data_cls)

        keys_with_defaults: Set[str] = {
            k
            for k, v in inspect.signature(self.data_cls).parameters.items()
            if v.default != inspect.Parameter.empty
        }

        self.schema = {
            field: (
                self.overrides[field]
                if field in self.overrides
                else typehint_resolver(annotations)
            )
            for field, annotations in type_hints.items()
        }

        self.required_fields = []

        self._keys_set = set()
        self._fast_keys_sync = []
        self._fast_keys_async = []
        for key, val in self.schema.items():
            self._keys_set.add(key)
            is_required = key not in keys_with_defaults
            if is_required:
                self.required_fields.append(key)
            self._fast_keys_sync.append((key, _wrap_sync_validator(val), is_required))
            self._fast_keys_async.append((key, _wrap_async_validator(val), is_required))

        self._unknown_keys_err: ExtraKeysErr = ExtraKeysErr(set(self.schema.keys()))
        if self.validate_object_async:
            self._disallow_synchronous(_raise_validate_object_async_in_sync_mode)

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

        if self.fail_on_unknown_keys:
            for key_ in data:
                if key_ not in self._keys_set:
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
            if self.validate_object and (result := self.validate_object(obj)):
                return False, Invalid(result, obj, self)

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

        if self.fail_on_unknown_keys:
            # this seems to be faster than `for key_ in data.keys()`
            for key_ in data:
                if key_ not in self._keys_set:
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
            if self.validate_object and (result := self.validate_object(obj)):
                return False, Invalid(result, obj, self)
            elif self.validate_object_async and (
                result_async := await self.validate_object_async(obj)
            ):
                return False, Invalid(result_async, obj, self)
            return True, obj

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.data_cls is other.data_cls
            and other.validate_object is self.validate_object
            and other.schema == self.schema
            and other.fail_on_unknown_keys == self.fail_on_unknown_keys
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.data_cls)]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("overrides", self.overrides),
                    ("validate_object", self.validate_object),
                    # note that this coincidentally works as we want:
                    # by default we don't fail on extra keys, so we don't
                    # show this in the repr if the default is defined
                    ("fail_on_unknown_keys", self.fail_on_unknown_keys),
                ]
                if v
            ],
        )
