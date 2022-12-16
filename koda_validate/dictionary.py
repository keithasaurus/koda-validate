import dataclasses
from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Dict,
    Hashable,
    List,
    Optional,
    Tuple,
    Union,
    overload,
)

from koda import Just, Maybe, nothing

from koda_validate import Invalid, Valid
from koda_validate._generics import (
    T1,
    T2,
    T3,
    T4,
    T5,
    T6,
    T7,
    T8,
    T9,
    T10,
    T11,
    T12,
    T13,
    T14,
    T15,
    T16,
    A,
    Ret,
)
from koda_validate._internal import (
    ResultTuple,
    _async_predicates_warning,
    _raise_cannot_define_validate_object_and_validate_object_async,
    _raise_validate_object_async_in_sync_mode,
    _repr_helper,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import (
    ErrType,
    ExtraKeysErr,
    KeyErrs,
    KeyValErrs,
    MapErr,
    MissingKeyErr,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    TypeErr,
    ValidationResult,
    Validator,
    missing_key_err,
)


class KeyNotRequired(Validator[Maybe[A]]):
    """
    For complex type reasons in the KeyValidator definition,
    this does not subclass Validator (even though it probably should)
    """

    def __init__(self, validator: Validator[A]):
        self.validator = validator

    async def validate_async(self, val: Any) -> ValidationResult[Maybe[A]]:
        result = await self.validator.validate_async(val)
        if result.is_valid:
            return Valid(Just(result.val))
        else:
            return result

    def __call__(self, val: Any) -> ValidationResult[Maybe[A]]:
        result = self.validator(val)
        if result.is_valid:
            return Valid(Just(result.val))
        else:
            return result

    def __eq__(self, other: Any) -> bool:
        return type(self) == type(other) and self.validator == other.validator

    def __repr__(self) -> str:
        return f"KeyNotRequired({repr(self.validator)})"


KeyValidator = Tuple[
    Hashable,
    Validator[A],
]


class MapValidator(Validator[Dict[T1, T2]]):
    __match_args__ = (
        "key_validator",
        "value_validator",
        "predicates",
        "predicates_async",
    )

    def __init__(
        self,
        *,
        key: Validator[T1],
        value: Validator[T2],
        predicates: Optional[List[Predicate[Dict[T1, T2]]]] = None,
        predicates_async: Optional[List[PredicateAsync[Dict[T1, T2]]]] = None,
    ) -> None:
        self.key_validator = key
        self.value_validator = value
        self.predicates = predicates
        self.predicates_async = predicates_async

    async def validate_async(self, val: Any) -> ValidationResult[Dict[T1, T2]]:
        if isinstance(val, dict):
            predicate_errors: List[
                Union[Predicate[Dict[Any, Any]], PredicateAsync[Dict[Any, Any]]]
            ] = []
            if self.predicates is not None:
                for predicate in self.predicates:
                    # Note that the expectation here is that validators will likely
                    # be doing json like number of keys; they aren't expected
                    # to be drilling down into specific keys and values. That may be
                    # an incorrect assumption; if so, some minor refactoring is probably
                    # necessary.
                    if not predicate(val):
                        predicate_errors.append(predicate)

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    if not await pred_async.validate_async(val):
                        predicate_errors.append(pred_async)

            if predicate_errors:
                return Invalid(PredicateErrs(predicate_errors), val, self)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[Any, KeyValErrs] = {}

            for key, val_ in val.items():
                key_result = await self.key_validator.validate_async(key)
                val_result = await self.value_validator.validate_async(val_)

                if key_result.is_valid and val_result.is_valid:
                    return_dict[key_result.val] = val_result.val
                else:
                    errors[key] = KeyValErrs(
                        key=None if key_result.is_valid else key_result,
                        val=None if val_result.is_valid else val_result,
                    )

            if errors:
                return Invalid(MapErr(errors), val, self)
            else:
                return Valid(return_dict)
        else:
            return Invalid(TypeErr(dict), val, self)

    def __call__(self, val: Any) -> ValidationResult[Dict[T1, T2]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if isinstance(val, dict):
            predicate_errors: List[
                Union[Predicate[Dict[Any, Any]], PredicateAsync[Dict[Any, Any]]]
            ] = []
            if self.predicates is not None:
                for predicate in self.predicates:
                    # Note that the expectation here is that validators will likely
                    # be doing json like number of keys; they aren't expected
                    # to be drilling down into specific keys and values. That may be
                    # an incorrect assumption; if so, some minor refactoring is probably
                    # necessary.
                    if not predicate(val):
                        predicate_errors.append(predicate)

            if predicate_errors:
                return Invalid(PredicateErrs(predicate_errors), val, self)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[Any, KeyValErrs] = {}
            for key, val_ in val.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val_)

                if key_result.is_valid and val_result.is_valid:
                    return_dict[key_result.val] = val_result.val
                else:
                    errors[key] = KeyValErrs(
                        key=None if key_result.is_valid else key_result,
                        val=None if val_result.is_valid else val_result,
                    )

            if errors:
                return Invalid(MapErr(errors), val, self)
            else:
                return Valid(return_dict)
        else:
            return Invalid(TypeErr(dict), val, self)

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.key_validator == other.key_validator
            and self.value_validator == other.value_validator
            and self.predicates == other.predicates
            and self.predicates_async == other.predicates_async
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [
                f"key={repr(self.key_validator)}",
                f"value={repr(self.value_validator)}",
            ]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("predicates", self.predicates),
                    ("predicates_async", self.predicates_async),
                ]
                if v
            ],
        )


class IsDictValidator(_ToTupleValidator[Dict[Any, Any]]):
    _instance: ClassVar[Optional["IsDictValidator"]] = None

    def __new__(cls) -> "IsDictValidator":
        """
        Make a singleton
        """
        if cls._instance is None:
            cls._instance = super(IsDictValidator, cls).__new__(cls)
        return cls._instance

    def validate_to_tuple(self, val: Any) -> ResultTuple[Dict[Any, Any]]:
        if isinstance(val, dict):
            return True, val
        else:
            return False, Invalid(TypeErr(dict), val, self)

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Dict[Any, Any]]:
        return self.validate_to_tuple(val)

    def __repr__(self) -> str:
        return "IsDictValidator()"


is_dict_validator = IsDictValidator()


@dataclasses.dataclass
class MinKeys(Predicate[Dict[Any, Any]]):
    size: int

    def __call__(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size


@dataclasses.dataclass
class MaxKeys(Predicate[Dict[Any, Any]]):
    size: int

    def __call__(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size


class RecordValidator(_ToTupleValidator[Ret]):
    __match_args__ = (
        "keys",
        "into",
        "validate_object",
        "validate_object_async",
    )

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1], Ret],
        keys: Tuple[
            KeyValidator[T1],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
            KeyValidator[T10],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
            KeyValidator[T10],
            KeyValidator[T11],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
            KeyValidator[T10],
            KeyValidator[T11],
            KeyValidator[T12],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
            KeyValidator[T10],
            KeyValidator[T11],
            KeyValidator[T12],
            KeyValidator[T13],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret
        ],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
            KeyValidator[T10],
            KeyValidator[T11],
            KeyValidator[T12],
            KeyValidator[T13],
            KeyValidator[T14],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret
        ],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
            KeyValidator[T10],
            KeyValidator[T11],
            KeyValidator[T12],
            KeyValidator[T13],
            KeyValidator[T14],
            KeyValidator[T15],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        *,
        into: Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16], Ret
        ],
        keys: Tuple[
            KeyValidator[T1],
            KeyValidator[T2],
            KeyValidator[T3],
            KeyValidator[T4],
            KeyValidator[T5],
            KeyValidator[T6],
            KeyValidator[T7],
            KeyValidator[T8],
            KeyValidator[T9],
            KeyValidator[T10],
            KeyValidator[T11],
            KeyValidator[T12],
            KeyValidator[T13],
            KeyValidator[T14],
            KeyValidator[T15],
            KeyValidator[T16],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        ...  # pragma: no cover

    def __init__(
        self,
        into: Union[
            Callable[[T1], Ret],
            Callable[[T1, T2], Ret],
            Callable[[T1, T2, T3], Ret],
            Callable[[T1, T2, T3, T4], Ret],
            Callable[[T1, T2, T3, T4, T5], Ret],
            Callable[[T1, T2, T3, T4, T5, T6], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret],
            Callable[
                [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret
            ],
            Callable[
                [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16],
                Ret,
            ],
        ],
        keys: Union[
            Tuple[KeyValidator[T1]],
            Tuple[KeyValidator[T1], KeyValidator[T2]],
            Tuple[KeyValidator[T1], KeyValidator[T2], KeyValidator[T3]],
            Tuple[KeyValidator[T1], KeyValidator[T2], KeyValidator[T3], KeyValidator[T4]],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
                KeyValidator[T10],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
                KeyValidator[T10],
                KeyValidator[T11],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
                KeyValidator[T10],
                KeyValidator[T11],
                KeyValidator[T12],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
                KeyValidator[T10],
                KeyValidator[T11],
                KeyValidator[T12],
                KeyValidator[T13],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
                KeyValidator[T10],
                KeyValidator[T11],
                KeyValidator[T12],
                KeyValidator[T13],
                KeyValidator[T14],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
                KeyValidator[T10],
                KeyValidator[T11],
                KeyValidator[T12],
                KeyValidator[T13],
                KeyValidator[T14],
                KeyValidator[T15],
            ],
            Tuple[
                KeyValidator[T1],
                KeyValidator[T2],
                KeyValidator[T3],
                KeyValidator[T4],
                KeyValidator[T5],
                KeyValidator[T6],
                KeyValidator[T7],
                KeyValidator[T8],
                KeyValidator[T9],
                KeyValidator[T10],
                KeyValidator[T11],
                KeyValidator[T12],
                KeyValidator[T13],
                KeyValidator[T14],
                KeyValidator[T15],
                KeyValidator[T16],
            ],
        ],
        validate_object: Optional[Callable[[Ret], Optional[ErrType]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Optional[ErrType]]]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:

        self.into = into
        # needs to be `Any` until we have variadic generics presumably
        self.keys: Tuple[KeyValidator[Any], ...] = keys
        if validate_object is not None and validate_object_async is not None:
            _raise_cannot_define_validate_object_and_validate_object_async()
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async
        self.fail_on_unknown_keys = fail_on_unknown_keys

        self._disallow_synchronous = bool(validate_object_async)

        # so we don't need to calculate each time we validate
        self._key_set = set()
        self._fast_keys_sync: List[
            Tuple[Hashable, Callable[[Any], ResultTuple[Any]], bool]
        ] = []

        self._fast_keys_async: List[
            Tuple[Hashable, Callable[[Any], Awaitable[ResultTuple[Any]]], bool]
        ] = []

        for key, val in keys:
            is_required = not isinstance(val, KeyNotRequired)
            self._fast_keys_sync.append((key, _wrap_sync_validator(val), is_required))  # type: ignore  # noqa: E501
            self._fast_keys_async.append((key, _wrap_async_validator(val), is_required))  # type: ignore  # noqa: E501
            self._key_set.add(key)

        self._unknown_keys_err: ExtraKeysErr = ExtraKeysErr(self._key_set)

    def validate_to_tuple(self, data: Any) -> ResultTuple[Ret]:
        if self._disallow_synchronous:
            _raise_validate_object_async_in_sync_mode(self.__class__)
        if not isinstance(data, dict):
            return False, Invalid(TypeErr(dict), data, self)

        if self.fail_on_unknown_keys:
            for key_ in data:
                if key_ not in self._key_set:
                    return False, Invalid(self._unknown_keys_err, data, self)

        args: List[Any] = []
        errs: Dict[Any, Invalid] = {}
        for key_, validator, key_required in self._fast_keys_sync:
            if key_ not in data:
                if key_required:
                    errs[key_] = Invalid(MissingKeyErr(), data, self)
                elif not errs:
                    args.append(nothing)
            else:
                success, new_val = validator(data[key_])

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    args.append(new_val)

        if errs:
            return False, Invalid(KeyErrs(errs), data, self)
        else:
            obj = self.into(*args)
            if self.validate_object and (result := self.validate_object(obj)):
                return False, Invalid(result, obj, self)
            return True, obj

    async def validate_to_tuple_async(self, data: Any) -> ResultTuple[Ret]:
        if not isinstance(data, dict):
            return False, Invalid(TypeErr(dict), data, self)

        if self.fail_on_unknown_keys:
            for key_ in data:
                if key_ not in self._key_set:
                    return False, Invalid(self._unknown_keys_err, data, self)

        args: List[Any] = []
        errs: Dict[Any, Invalid] = {}
        for key_, async_validator, key_required in self._fast_keys_async:
            if key_ not in data:
                if key_required:
                    errs[key_] = Invalid(MissingKeyErr(), data, self)
                else:
                    args.append(nothing)
            else:
                success, new_val = await async_validator(data[key_])

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    args.append(new_val)

        if errs:
            return False, Invalid(KeyErrs(errs), data, self)
        else:
            obj = self.into(*args)
            if self.validate_object and (result := self.validate_object(obj)):
                return False, Invalid(result, obj, self)
            elif self.validate_object_async and (
                async_result := await self.validate_object_async(obj)
            ):
                return False, Invalid(async_result, obj, self)

            return True, obj

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.into == other.into
            and self.keys == other.keys
            and self.validate_object == other.validate_object
            and self.validate_object_async == other.validate_object_async
            and self.fail_on_unknown_keys == other.fail_on_unknown_keys
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [f"keys={repr(self.keys)}", f"into={repr(self.into)}"]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("validate_object", self.validate_object),
                    ("validate_object_async", self.validate_object_async),
                    # note that this coincidentally works as we want:
                    # by default we don't fail on extra keys, so we don't
                    # show this in the repr if the default is defined
                    ("fail_on_unknown_keys", self.fail_on_unknown_keys),
                ]
                if v
            ],
        )


class DictValidatorAny(_ToTupleValidator[Dict[Any, Any]]):
    """
    This differs from RecordValidator in a few ways:
    - if valid, it returns a dict; it does not allow another target to be specified
    - it does not narrow the types of keys / values. It always returns
    `Dict[Hashable, Any]`
    - it allows for any number of `KeyValidator`s

    This class exists for two reasons:
    - because the overloads we use to define `RecordValidator` get very slow
    for type checkers beyond a certain point, sa we have a max number of
    type-checkable keys
    - if you don't care about the types in the target object

    VALIDATION WILL STILL WORK PROPERLY, but there won't be much type hinting
    assistance.
    """

    __match_args__ = (
        "schema",
        "validate_object",
        "validate_object_async",
    )

    def __init__(
        self,
        schema: Dict[Any, Validator[Any]],
        *,
        validate_object: Optional[
            Callable[[Dict[Hashable, Any]], Optional[ErrType]]
        ] = None,
        validate_object_async: Optional[
            Callable[
                [Dict[Any, Any]],
                Awaitable[Optional[ErrType]],
            ]
        ] = None,
        fail_on_unknown_keys: bool = False,
    ) -> None:
        self.schema: Dict[Any, Validator[Any]] = schema
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        if validate_object is not None and validate_object_async is not None:
            _raise_cannot_define_validate_object_and_validate_object_async()
        self.fail_on_unknown_keys = fail_on_unknown_keys

        self._disallow_synchronous = bool(validate_object_async)

        # so we don't need to calculate each time we validate
        self._fast_keys_sync = []
        self._fast_keys_async = []
        self._keys_set = set()
        for key, val in schema.items():
            self._keys_set.add(key)
            vldtr = (
                val.validator
                if (is_not_required := isinstance(val, KeyNotRequired))
                else val
            )
            self._fast_keys_sync.append(
                (key, _wrap_sync_validator(vldtr), not is_not_required)
            )
            self._fast_keys_async.append(
                (key, _wrap_async_validator(vldtr), not is_not_required)
            )

        self._unknown_keys_err = ExtraKeysErr(set(schema.keys()))

    def validate_to_tuple(self, data: Any) -> ResultTuple[Dict[Any, Any]]:
        if self._disallow_synchronous:
            _raise_validate_object_async_in_sync_mode(self.__class__)

        if not type(data) is dict:
            return False, Invalid(TypeErr(dict), data, self)

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
        elif self.validate_object and (result := self.validate_object(success_dict)):
            return False, Invalid(result, success_dict, self)

        return True, success_dict

    async def validate_to_tuple_async(self, data: Any) -> ResultTuple[Dict[Any, Any]]:
        if not type(data) is dict:
            return False, Invalid(TypeErr(dict), data, self)

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
        elif self.validate_object and (result := self.validate_object(success_dict)):
            return False, Invalid(result, success_dict, self)
        elif self.validate_object_async and (
            result := await self.validate_object_async(success_dict)
        ):
            return False, Invalid(result, success_dict, self)

        return True, success_dict

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.schema == other.schema
            and self.validate_object == other.validate_object
            and self.validate_object_async == other.validate_object_async
            and self.fail_on_unknown_keys == other.fail_on_unknown_keys
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.schema)]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("validate_object", self.validate_object),
                    ("validate_object_async", self.validate_object_async),
                    # note that this coincidentally works as we want:
                    # by default we don't fail on extra keys, so we don't
                    # show this in the repr if the default is defined
                    ("fail_on_unknown_keys", self.fail_on_unknown_keys),
                ]
                if v
            ],
        )
