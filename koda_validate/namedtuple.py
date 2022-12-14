import inspect
from typing import (
    Any,
    Callable,
    Dict,
    NamedTuple,
    Optional,
    Set,
    Type,
    TypeVar,
    get_type_hints,
)

from koda_validate._internal import (
    ResultTuple,
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

_NTT = TypeVar("_NTT", bound=NamedTuple)


class NamedTupleValidator(_ToTupleValidator[_NTT]):
    __match_args__ = ("data_cls", "overrides", "fail_on_unknown_keys")

    def __init__(
        self,
        named_tuple_cls: Type[_NTT],
        *,
        overrides: Optional[Dict[str, Validator[Any]]] = None,
        validate_object: Optional[Callable[[_NTT], Optional[ErrType]]] = None,
        typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
        fail_on_unknown_keys: bool = False,
    ) -> None:

        self.named_tuple_cls = named_tuple_cls
        self._input_overrides = overrides  # for repr
        self.fail_on_unknown_keys = fail_on_unknown_keys

        overrides = overrides or {}
        type_hints = get_type_hints(self.named_tuple_cls)

        keys_with_defaults: Set[str] = {
            k
            for k, v in inspect.signature(self.named_tuple_cls).parameters.items()
            if v.default != inspect.Parameter.empty
        }

        self.schema = {
            field: (
                overrides[field] if field in overrides else typehint_resolver(annotations)
            )
            for field, annotations in type_hints.items()
        }

        self.validate_object = validate_object

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

    def validate_to_tuple(self, val: Any) -> ResultTuple[_NTT]:
        if isinstance(val, dict):
            data = val
        elif isinstance(val, self.named_tuple_cls):
            data = val._asdict()
        else:
            return False, Invalid(
                CoercionErr(
                    {dict, self.named_tuple_cls},
                    self.named_tuple_cls,
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
            obj = self.named_tuple_cls(**success_dict)
            if self.validate_object and (result := self.validate_object(obj)):
                return False, Invalid(result, obj, self)

            return True, obj

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[_NTT]:
        if isinstance(val, dict):
            data = val
        elif isinstance(val, self.named_tuple_cls):
            data = val._asdict()
        else:
            return False, Invalid(
                CoercionErr(
                    {dict, self.named_tuple_cls},
                    self.named_tuple_cls,
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
            obj = self.named_tuple_cls(**success_dict)
            if self.validate_object and (result := self.validate_object(obj)):
                return False, Invalid(result, obj, self)

            return True, obj

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.named_tuple_cls is other.named_tuple_cls
            and other.validate_object is self.validate_object
            and other.schema == self.schema
            and other.fail_on_unknown_keys == self.fail_on_unknown_keys
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.named_tuple_cls)]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("overrides", self._input_overrides),
                    ("validate_object", self.validate_object),
                    # note that this coincidentally works as we want:
                    # by default we don't fail on extra keys, so we don't
                    # show this in the repr if the default is defined
                    ("fail_on_unknown_keys", self.fail_on_unknown_keys),
                ]
                if v
            ],
        )
