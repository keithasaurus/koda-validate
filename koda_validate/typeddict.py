import sys
from typing import (
    Any,
    Awaitable,
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
    _is_typed_dict_cls,
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
    TypeErr,
    missing_key_err,
)
from koda_validate.typehints import get_typehint_validator
from koda_validate.valid import Invalid

_TDT = TypeVar("_TDT", bound=Mapping[str, object])


class TypedDictValidator(_ToTupleValidator[_TDT]):
    """
    Takes a ``TypedDict`` subclass as an argument and derives a :class:`Validator`.

    Optional keys are determined by the ``__optional_keys__`` and ``__required_keys__``
    attributes.

    .. note::

        This validator _might_ work on non-typed-dict classes (There are challenges
        in defining a TypedDict-like type). *Please* do not intentionally try to use
        it for non-TypedDict datatypes.

    Example:

    .. testcode:: tdexample

        from typing import List, TypedDict
        from koda_validate import *

        class Person(TypedDict):
            name: str
            hobbies: List[str]

        validator = TypedDictValidator(Person)

    Usage:

    .. doctest:: tdexample

        >>> validator({"name": "Bob", "hobbies": ["eating", "coding", "sleeping"]})
        Valid(val={'name': 'Bob', 'hobbies': ['eating', 'coding', 'sleeping']})


    :param td_cls: A ``TypedDict`` subclass
    :param overrides: a dict whose keys define explicit validators
    :param validate_object: is run if all keys have been validated individually. If it
        returns ``None``, then there were no errors; otherwise it should return
        ``ErrType``
    :param validate_object_async: same as ``validate_object``, except that is runs
        asynchronously
    :param typehint_resolver: define this to override default inferred validators for
        types
    :param coerce: this can be set to create any kind of custom coercion
    :param fail_on_unknown_keys: if True, this will fail if any keys not defined by the
        ``TypedDict`` are found. This will fail before any values are validated.
    :raises TypeError: should raise if non-``TypedDict`` type is passed for ``td_cls``
    """

    __match_args__ = ("td_cls", "overrides", "fail_on_unknown_keys", "coerce")

    def __init__(
        self,
        td_cls: Type[_TDT],
        *,
        overrides: Optional[Dict[str, Validator[Any]]] = None,
        validate_object: Optional[Callable[[_TDT], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[
                [_TDT],
                Awaitable[Optional[ErrType]],
            ]
        ] = None,
        coerce: Optional[Coercer[Dict[Any, Any]]] = None,
        typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        if not _is_typed_dict_cls(td_cls):
            raise TypeError("must be a TypedDict subclass")

        self.td_cls = td_cls
        self.overrides = overrides  # for repr
        self.fail_on_unknown_keys = fail_on_unknown_keys
        self.coerce = coerce

        if validate_object is not None and validate_object_async is not None:
            _raise_cannot_define_validate_object_and_validate_object_async()

        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        self._disallow_synchronous = bool(validate_object_async)

        if sys.version_info >= (3, 9):
            # Required/NotRequired keys are always present in
            self.required_keys: FrozenSet[str] = getattr(
                td_cls, "__required_keys__", frozenset()
            )
            type_hints = get_type_hints(self.td_cls, include_extras=True)
        else:
            # not going to try to handle superclasses
            self.required_keys = (
                frozenset([k for k in td_cls.__annotations__])
                if getattr(td_cls, "__total__", True)
                else frozenset()
            )
            type_hints = get_type_hints(self.td_cls)

        overrides = self.overrides or {}
        self.schema = {
            field: (
                overrides[field] if field in overrides else typehint_resolver(annotations)
            )
            for field, annotations in type_hints.items()
        }

        self._keys_set = set()
        self._fast_keys_sync = []
        self._fast_keys_async = []
        for key, val in self.schema.items():
            self._keys_set.add(key)
            is_required = key in self.required_keys
            self._fast_keys_sync.append((key, _wrap_sync_validator(val), is_required))
            self._fast_keys_async.append((key, _wrap_async_validator(val), is_required))

        self._unknown_keys_err: ExtraKeysErr = ExtraKeysErr(set(self.schema.keys()))

    def _validate_to_tuple(self, data: Any) -> _ResultTuple[_TDT]:
        if self._disallow_synchronous:
            _raise_validate_object_async_in_sync_mode(self.__class__)

        if self.coerce:
            if not (coerced := self.coerce(data)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, dict), data, self
                )
            else:
                coerced_val: Dict[Any, Any] = coerced.val

        elif type(data) is dict:
            coerced_val = data
        else:
            return False, Invalid(TypeErr(dict), data, self)

        if self.fail_on_unknown_keys:
            for key_ in coerced_val:
                if key_ not in self._keys_set:
                    return False, Invalid(self._unknown_keys_err, coerced_val, self)

        success_dict: Dict[str, object] = {}
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
            if self.validate_object and (
                result := self.validate_object(cast(_TDT, success_dict))
            ):
                return False, Invalid(result, success_dict, self)
            return True, cast(_TDT, success_dict)

    async def _validate_to_tuple_async(self, data: Any) -> _ResultTuple[_TDT]:
        if self.coerce:
            if not (coerced := self.coerce(data)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, dict), data, self
                )
            else:
                coerced_val: Dict[Any, Any] = coerced.val

        elif type(data) is dict:
            coerced_val = data
        else:
            return False, Invalid(TypeErr(dict), data, self)

        if self.fail_on_unknown_keys:
            for key_ in coerced_val:
                if key_ not in self._keys_set:
                    return False, Invalid(self._unknown_keys_err, data, self)

        success_dict: Dict[str, object] = {}
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
            if self.validate_object and (
                result := self.validate_object(cast(_TDT, success_dict))
            ):
                return False, Invalid(result, success_dict, self)
            elif self.validate_object_async and (
                result_async := await self.validate_object_async(cast(_TDT, success_dict))
            ):
                return False, Invalid(result_async, success_dict, self)
            return True, cast(_TDT, success_dict)

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.schema == other.schema
            and self.validate_object == other.validate_object
            and self.validate_object_async == other.validate_object_async
            and self.fail_on_unknown_keys == other.fail_on_unknown_keys
            and self.coerce == other.coerce
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.td_cls)]
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
