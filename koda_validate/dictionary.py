import dataclasses
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Hashable,
    List,
    Literal,
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
    _ToTupleValidator,
    validate_dict_to_tuple,
    validate_dict_to_tuple_async,
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
    Processor,
    TypeErr,
    ValidationResult,
    Validator,
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
        "preprocessors",
    )

    def __init__(
        self,
        *,
        key: Validator[T1],
        value: Validator[T2],
        predicates: Optional[List[Predicate[Dict[T1, T2]]]] = None,
        predicates_async: Optional[List[PredicateAsync[Dict[T1, T2]]]] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.key_validator = key
        self.value_validator = value
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    async def validate_async(self, val: Any) -> ValidationResult[Dict[T1, T2]]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

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
                return Invalid(self, PredicateErrs(predicate_errors))

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
                return Invalid(self, MapErr(errors))
            else:
                return Valid(return_dict)
        else:
            return Invalid(self, TypeErr(dict))

    def __call__(self, val: Any) -> ValidationResult[Dict[T1, T2]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

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
                return Invalid(self, PredicateErrs(predicate_errors))

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
                return Invalid(self, MapErr(errors))
            else:
                return Valid(return_dict)
        else:
            return Invalid(self, TypeErr(dict))


class IsDictValidator(_ToTupleValidator[Dict[Any, Any]]):
    def validate_to_tuple(self, val: Any) -> ResultTuple[Dict[Any, Any]]:
        if isinstance(val, dict):
            return True, val
        else:
            return False, Invalid(self, TypeErr(dict))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Dict[Any, Any]]:
        return self.validate_to_tuple(val)


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
        "preprocessors",
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:

        self.into = into
        # needs to be `Any` until we have variadic generics presumably
        self.keys: Tuple[KeyValidator[Any], ...] = keys
        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async
        self.preprocessors = preprocessors

        # so we don't need to calculate each time we validate
        _key_set = {k for k, _ in keys}
        self._key_set = _key_set
        self._fast_keys = [
            (
                key,
                val,
                not isinstance(val, KeyNotRequired),
                isinstance(val, _ToTupleValidator),
            )
            for key, val in keys
        ]
        self._unknown_keys_err: Tuple[Literal[False], Invalid] = False, Invalid(
            self, ExtraKeysErr(_key_set)
        )

    def validate_to_tuple(self, data: Any) -> ResultTuple[Ret]:
        if not isinstance(data, dict):
            return False, Invalid(self, TypeErr(dict))

        if self.preprocessors:
            for preproc in self.preprocessors:
                data = preproc(data)

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self._key_set:
                return False, Invalid(self, ExtraKeysErr(self._key_set))

        args: List[Any] = []
        errs: Dict[Hashable, Invalid] = {}
        for key_, validator, key_required, is_tuple_validator in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs[key_] = Invalid(self, MissingKeyErr())
                else:
                    args.append(nothing)
            else:
                if is_tuple_validator:
                    success, new_val = validator.validate_to_tuple(val)  # type: ignore
                else:
                    success, new_val = (
                        (True, result_.val)
                        if (result_ := validator(val)).is_valid  # type: ignore
                        else (False, result_)
                    )

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    args.append(new_val)

        if errs:
            return False, Invalid(self, KeyErrs(errs))
        else:
            # we know this should be ret
            obj = self.into(*args)
            if self.validate_object is None:
                return True, obj
            else:
                result = self.validate_object(obj)
                if result is None:
                    return True, obj
                else:
                    return False, Invalid(self, result)

    async def validate_to_tuple_async(self, data: Any) -> ResultTuple[Ret]:
        if not isinstance(data, dict):
            return False, Invalid(self, TypeErr(dict))

        if self.preprocessors:
            for preproc in self.preprocessors:
                data = preproc(data)

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self._key_set:
                return self._unknown_keys_err

        args: List[Any] = []
        errs: Dict[Any, Invalid] = {}
        for key_, validator, key_required, is_tuple_validator in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs[key_] = Invalid(self, MissingKeyErr())
                else:
                    args.append(nothing)
            else:
                if is_tuple_validator:
                    success, new_val = await validator.validate_to_tuple_async(val)  # type: ignore  # noqa: E501
                else:
                    success, new_val = (
                        (True, result_.val)
                        if (result_ := await validator.validate_async(val)).is_valid  # type: ignore  # noqa: E501
                        else (False, result_)
                    )

                if not success:
                    errs[key_] = new_val
                elif not errs:
                    args.append(new_val)

        if errs:
            return False, Invalid(self, KeyErrs(errs))
        else:
            obj = self.into(*args)
            if self.validate_object is not None:
                result = self.validate_object(obj)
                if result is None:
                    return True, obj
                else:
                    return False, Invalid(self, result)
            elif self.validate_object_async is not None:
                result = await self.validate_object_async(obj)
                if result is None:
                    return True, obj
                else:
                    return False, Invalid(self, result)
            else:
                return True, obj


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
        "preprocessors",
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
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.schema: Dict[Any, Validator[Any]] = schema
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.preprocessors = preprocessors

        # so we don't need to calculate each time we validate
        self._fast_keys = [
            (
                key,
                val,
                not isinstance(val, KeyNotRequired),
                isinstance(val, _ToTupleValidator),
            )
            for key, val in schema.items()
        ]

        self._unknown_keys_err: Tuple[Literal[False], Invalid] = False, Invalid(
            self, ExtraKeysErr(set(schema.keys()))
        )

    def validate_to_tuple(self, data: Any) -> ResultTuple[Dict[Any, Any]]:
        result_tup = validate_dict_to_tuple(
            self,
            self.preprocessors,
            self._fast_keys,
            self.schema,
            self._unknown_keys_err,
            data,
        )
        if not result_tup[0]:
            return False, result_tup[1]
        else:
            if self.validate_object is not None:
                result = self.validate_object(result_tup[1])
                if result is None:
                    return True, result_tup[1]
                else:
                    return False, Invalid(self, result)
            else:
                return True, result_tup[1]

    async def validate_to_tuple_async(self, data: Any) -> ResultTuple[Dict[Any, Any]]:
        result_tup = await validate_dict_to_tuple_async(
            self,
            self.preprocessors,
            self._fast_keys,
            self.schema,
            self._unknown_keys_err,
            data,
        )
        if not result_tup[0]:
            return False, result_tup[1]
        else:
            if self.validate_object is not None:
                result = self.validate_object(result_tup[1])
                if result is None:
                    return True, result_tup[1]
                else:
                    return False, Invalid(self, result)
            elif self.validate_object_async is not None:
                result = await self.validate_object_async(result_tup[1])
                if result is None:
                    return True, result_tup[1]
                else:
                    return False, Invalid(self, result)
            else:
                return True, result_tup[1]
