import inspect
import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    NamedTuple,
    Optional,
    Set,
    Type,
    TypeVar,
    get_type_hints,
)

from koda import Just, Maybe, nothing

from koda_validate._internal import (
    _raise_cannot_define_validate_object_and_validate_object_async,
    _raise_validate_object_async_in_sync_mode,
    _repr_helper,
    _ResultTuple,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import Validator
from koda_validate.coerce import Coercer
from koda_validate.errors import (
    CoercionErr,
    ErrType,
    ExtraKeysErr,
    KeyErrs,
    missing_key_err,
)
from koda_validate.typehints import get_typehint_validator
from koda_validate.valid import Invalid

_NTT = TypeVar("_NTT", bound=NamedTuple)


def namedtuple_no_coerce(nt_cls: Type[_NTT]) -> Coercer[Dict[Any, Any]]:
    def _fn(val: Any) -> Maybe[Dict[Any, Any]]:
        return Just(val._asdict()) if type(val) is nt_cls else nothing

    return Coercer(_fn, {nt_cls})


class NamedTupleValidator(_ToTupleValidator[_NTT]):
    """
    Takes a ``NamedTuple`` subclass as an argument and derives a :class:`Validator`. Will
    validate against an instance of ``self.named_tuple_cls`` *or* a dictionary.
    Regardless of the input type, the result will be an instance of type
    ``self.named_tuple_cls``.

    Optional keys are determined by the presence of a default argument.

    Example:

    .. testcode:: dcexample

        from dataclasses import dataclass
        from typing import List, NamedTuple
        from koda_validate import *

        class Person(NamedTuple):
            name: str
            hobbies: List[str]

        validator = NamedTupleValidator(Person)

    Usage:

    .. doctest:: dcexample

        >>> validator({"name": "Bob", "hobbies": ["eating", "coding", "sleeping"]})
        Valid(val=Person(name='Bob', hobbies=['eating', 'coding', 'sleeping']))


    :param named_tuple_cls: A ``dataclass`` class
    :param overrides: a dict whose keys define explicit validators
    :param validate_object: is run if all keys have been validated individually. If it
        returns ``None``, then there were no errors; otherwise it should return
        ``ErrType``
    :param validate_object_async: same as ``validate_object``, except that is runs
        asynchronously
    :param typehint_resolver: define this to override default inferred validators for
        types
    :param fail_on_unknown_keys: if True, this will fail if any keys not defined by
        ``self.data_cls`` are found. This will fail before any values are validated.
    :param coerce: a function that can control coercion
    :raises TypeError: should raise if non-``NamedTuple`` type is passed for
        ``named_tuple_cls``
    """

    __match_args__ = ("named_tuple_cls", "overrides", "fail_on_unknown_keys", "coerce")

    def __init__(
        self,
        named_tuple_cls: Type[_NTT],
        *,
        overrides: Optional[Dict[str, Validator[Any]]] = None,
        validate_object: Optional[Callable[[_NTT], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[_NTT], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
        typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
        coerce: Optional[Coercer[Dict[Any, Any]]] = None,
    ) -> None:
        self.named_tuple_cls = named_tuple_cls
        self.overrides = overrides
        self.fail_on_unknown_keys = fail_on_unknown_keys
        self.coerce = coerce

        if validate_object and validate_object_async:
            _raise_cannot_define_validate_object_and_validate_object_async()

        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        self._disallow_synchronous = bool(validate_object_async)

        overrides = self.overrides or {}
        if sys.version_info >= (3, 9):
            type_hints = get_type_hints(self.named_tuple_cls, include_extras=True)
        else:
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

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[_NTT]:
        if self._disallow_synchronous:
            _raise_validate_object_async_in_sync_mode(self.__class__)

        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, dict), val, self
                )
            else:
                coerced_val: Dict[Any, Any] = coerced.val

        elif type(val) is dict:
            coerced_val = val
        elif type(val) is self.named_tuple_cls:
            coerced_val = val._asdict()
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
            for key_ in coerced_val:
                if key_ not in self._keys_set:
                    return False, Invalid(self._unknown_keys_err, coerced_val, self)

        success_dict: Dict[Any, Any] = {}
        errs: Dict[Any, Invalid] = {}
        for key_, validator, key_required in self._fast_keys_sync:
            if key_ not in coerced_val:
                if key_required:
                    errs[key_] = Invalid(missing_key_err, coerced_val, self)
            else:
                success, new_val = validator(coerced_val[key_])

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    success_dict[key_] = new_val

        if errs:
            return False, Invalid(KeyErrs(errs), coerced_val, self)
        else:
            obj = self.named_tuple_cls(**success_dict)  # type: ignore[call-overload]
            if self.validate_object and (result := self.validate_object(obj)):
                return False, Invalid(result, obj, self)

            return True, obj

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[_NTT]:
        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, dict), val, self
                )
            else:
                coerced_val: Dict[Any, Any] = coerced.val

        elif type(val) is dict:
            coerced_val = val
        elif type(val) is self.named_tuple_cls:
            coerced_val = val._asdict()
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
            for key_ in coerced_val:
                if key_ not in self._keys_set:
                    return False, Invalid(self._unknown_keys_err, coerced_val, self)

        success_dict: Dict[Any, Any] = {}
        errs: Dict[Any, Invalid] = {}
        for key_, validator, key_required in self._fast_keys_async:
            if key_ not in coerced_val:
                if key_required:
                    errs[key_] = Invalid(missing_key_err, coerced_val, self)
            else:
                success, new_val = await validator(coerced_val[key_])

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    success_dict[key_] = new_val

        if errs:
            return False, Invalid(KeyErrs(errs), coerced_val, self)
        else:
            obj = self.named_tuple_cls(**success_dict)  # type: ignore[call-overload]
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
            and self.named_tuple_cls is other.named_tuple_cls
            and other.validate_object is self.validate_object
            and other.validate_object_async is self.validate_object_async
            and other.schema == self.schema
            and other.fail_on_unknown_keys == self.fail_on_unknown_keys
            and other.coerce == self.coerce
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.named_tuple_cls)]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("overrides", self.overrides),
                    ("validate_object", self.validate_object),
                    ("validate_object_async", self.validate_object_async),
                    ("coerce", self.coerce),
                    # note that this coincidentally works as we want:
                    # by default we don't fail on extra keys, so we don't
                    # show this in the repr if the default is defined
                    ("fail_on_unknown_keys", self.fail_on_unknown_keys),
                ]
                if v
            ],
        )
