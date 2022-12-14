import sys
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Mapping,
    Optional,
    Type,
    TypeVar,
    cast,
    get_type_hints,
)

from koda_validate._internal import (
    ResultTuple,
    _is_typed_dict_cls,
    _repr_helper,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import (
    ErrType,
    ExtraKeysErr,
    Invalid,
    KeyErrs,
    TypeErr,
    Validator,
    missing_key_err,
)
from koda_validate.typehints import get_typehint_validator

_TDT = TypeVar("_TDT", bound=Mapping[str, object])


class TypedDictValidator(_ToTupleValidator[_TDT]):
    """
    This validator _might_ work on non-typed-dict classes (There are challenges
    in defining a TypedDict-like type). *Please* do not intentionally try to use
    it for non-TypedDict datatypes.
    """

    __match_args__ = ("data_cls", "overrides", "fail_on_unknown_keys")

    def __init__(
        self,
        td_cls: Type[_TDT],
        *,
        overrides: Optional[Dict[str, Validator[Any]]] = None,
        validate_object: Optional[Callable[[_TDT], Optional[ErrType]]] = None,
        typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
        fail_on_unknown_keys: bool = False,
    ) -> None:

        if not _is_typed_dict_cls(td_cls):
            raise TypeError("must be a TypedDict subclass")

        self.td_cls = td_cls
        self._input_overrides = overrides  # for repr
        self.fail_on_unknown_keys = fail_on_unknown_keys
        self.overrides = overrides or {}

        type_hints = get_type_hints(self.td_cls)

        if sys.version_info >= (3, 9):
            # Required/NotRequired keys are always present in
            self.required_keys: FrozenSet[str] = getattr(
                td_cls, "__required_keys__", frozenset()
            )
        else:
            # not going to try to handle superclasses
            self.required_keys = (
                frozenset([k for k in td_cls.__annotations__])
                if getattr(td_cls, "__total__", True)
                else frozenset()
            )

        self.schema = {
            field: (
                self.overrides[field]
                if field in self.overrides
                else typehint_resolver(annotations)
            )
            for field, annotations in type_hints.items()
        }

        self.validate_object = validate_object

        self._keys_set = set()
        self._fast_keys_sync = []
        self._fast_keys_async = []
        for key, val in self.schema.items():
            self._keys_set.add(key)
            is_required = key in self.required_keys
            self._fast_keys_sync.append((key, _wrap_sync_validator(val), is_required))
            self._fast_keys_async.append((key, _wrap_async_validator(val), is_required))

        self._unknown_keys_err: ExtraKeysErr = ExtraKeysErr(set(self.schema.keys()))

    def validate_to_tuple(self, data: Any) -> ResultTuple[_TDT]:
        if not type(data) is dict:
            return False, Invalid(TypeErr(dict), data, self)

        if self.fail_on_unknown_keys:
            for key_ in data:
                if key_ not in self._keys_set:
                    return False, Invalid(self._unknown_keys_err, data, self)

        success_dict: Dict[str, object] = {}
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
            if self.validate_object and (
                result := self.validate_object(cast(_TDT, success_dict))
            ):
                return False, Invalid(result, success_dict, self)
            return True, cast(_TDT, success_dict)

    async def validate_to_tuple_async(self, data: Any) -> ResultTuple[_TDT]:
        if not type(data) is dict:
            return False, Invalid(TypeErr(dict), data, self)

        if self.fail_on_unknown_keys:
            for key_ in data:
                if key_ not in self._keys_set:
                    return False, Invalid(self._unknown_keys_err, data, self)

        success_dict: Dict[str, object] = {}
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
            if self.validate_object and (
                result := self.validate_object(cast(_TDT, success_dict))
            ):
                return False, Invalid(result, success_dict, self)
            return True, cast(_TDT, success_dict)

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.schema == other.schema
            and self.validate_object == other.validate_object
            and other.fail_on_unknown_keys == self.fail_on_unknown_keys
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.td_cls)]
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
