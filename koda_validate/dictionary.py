from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Final,
    FrozenSet,
    Generic,
    Hashable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from koda import Err, Just, Maybe, Ok, Result, mapping_get, nothing

from koda_validate._generics import A
from koda_validate._internals import _ToTupleValidator
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)

OBJECT_ERRORS_FIELD: Final[str] = "__container__"

EXPECTED_DICT_ERR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected a dictionary"]}
)

EXPECTED_MAP_ERR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected a map"]}
)

OK_NOTHING: Final[Result[Maybe[Any], Any]] = Ok(nothing)

KEY_MISSING_MSG: Final[Serializable] = ["key missing"]
KEY_MISSING_ERR: Final[Err[Serializable]] = Err(KEY_MISSING_MSG)


class KeyNotRequired(Generic[A]):
    """
    For complex type reasons in the KeyValidator defintion,
    this does not subclass Validator (even though it probably should)
    """

    def __init__(self, validator: Validator[Any, A, Serializable]):
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], Serializable]:
        if not maybe_val.is_just:
            return Ok(maybe_val)
        else:
            return self.validator(maybe_val.val).map(Just)

    async def validate_async(
        self, maybe_val: Maybe[Any]
    ) -> Result[Maybe[A], Serializable]:
        if not maybe_val.is_just:
            return Ok(maybe_val)
        else:
            return (await self.validator.validate_async(maybe_val.val)).map(Just)


KeyValidator = Tuple[
    Hashable,
    Union[
        Validator[Any, A, Serializable],
        # this is NOT a validator intentionally; for typing reasons
        # ONLY intended for using KeyNotRequired
        Callable[[Maybe[Any]], Result[A, Serializable]],
    ],
]

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")
T10 = TypeVar("T10")
T11 = TypeVar("T11")
T12 = TypeVar("T12")
T13 = TypeVar("T13")
T14 = TypeVar("T14")
T15 = TypeVar("T15")
Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


class MapValidator(Validator[Any, Dict[T1, T2], Serializable]):
    __slots__ = (
        "key_validator",
        "value_validator",
        "predicates",
        "predicates_async",
        "preprocessors",
    )
    __match_args__ = (
        "key_validator",
        "value_validator",
        "predicates",
        "predicates_async",
        "preprocessors",
    )

    def __init__(
        self,
        key_validator: Validator[Any, T1, Serializable],
        value_validator: Validator[Any, T2, Serializable],
        *,
        predicates: Optional[List[Predicate[Dict[T1, T2], Serializable]]] = None,
        predicates_async: Optional[
            List[PredicateAsync[Dict[T1, T2], Serializable]]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Result[Dict[T1, T2], Serializable]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}
            for key, val_ in val.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val_)

                if key_result.is_ok and val_result.is_ok:
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if not key_result.is_ok:
                        errors[err_key] = {"key_error": key_result.val}

                    if not val_result.is_ok:
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if errs.is_just and isinstance(errs.val, dict):
                            errs.val.update(err_dict)
                        else:
                            errors[err_key] = err_dict

            dict_validator_errors: List[Serializable] = []
            if self.predicates is not None:
                for predicate in self.predicates:
                    # Note that the expectation here is that validators will likely
                    # be doing json like number of keys; they aren't expected
                    # to be drilling down into specific keys and values. That may be
                    # an incorrect assumption; if so, some minor refactoring is probably
                    # necessary.
                    result = predicate(val)
                    if not result.is_ok:
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Err(errors)
            else:
                return Ok(return_dict)
        else:
            return EXPECTED_MAP_ERR

    async def validate_async(self, val: Any) -> Result[Dict[T1, T2], Serializable]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}

            for key, val_ in val.items():
                key_result = await self.key_validator.validate_async(key)
                val_result = await self.value_validator.validate_async(val_)

                if key_result.is_ok and val_result.is_ok:
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if not key_result.is_ok:
                        errors[err_key] = {"key_error": key_result.val}

                    if not val_result.is_ok:
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if errs.is_just and isinstance(errs.val, dict):
                            errs.val.update(err_dict)
                        else:
                            errors[err_key] = err_dict

            dict_validator_errors: List[Serializable] = []
            if self.predicates is not None:
                for predicate in self.predicates:
                    # Note that the expectation here is that validators will likely
                    # be doing json like number of keys; they aren't expected
                    # to be drilling down into specific keys and values. That may be
                    # an incorrect assumption; if so, some minor refactoring is probably
                    # necessary.
                    result = predicate(val)
                    if not result.is_ok:
                        dict_validator_errors.append(result.val)

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    result = await pred_async.validate_async(val)
                    if not result.is_ok:
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Err(errors)
            else:
                return Ok(return_dict)
        else:
            return EXPECTED_MAP_ERR


class IsDictValidator(Validator[Any, Dict[Any, Any], Serializable]):
    def __call__(self, val: Any) -> Result[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return EXPECTED_DICT_ERR

    async def validate_async(self, val: Any) -> Result[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return EXPECTED_DICT_ERR


is_dict_validator = IsDictValidator()


class MinKeys(Predicate[Dict[Any, Any], Serializable]):
    __slots__ = ("size",)
    __match_args__ = ("size",)

    def __init__(self, size: int) -> None:
        self.size = size

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
    __slots__ = ("size",)
    __match_args__ = ("size",)

    def __init__(self, size: int) -> None:
        self.size = size

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


def _make_keys_err(keys: FrozenSet[Hashable]) -> Err[Serializable]:
    return Err(
        {
            OBJECT_ERRORS_FIELD: [
                "Received unknown keys. "
                + (
                    "Expected empty dictionary."
                    if len(keys) == 0
                    else "Only expected "
                    + ", ".join(sorted([repr(k) for k in keys]))
                    + "."
                )
            ]
        }
    )


class DictValidator(Validator[Any, Ret, Serializable]):
    __slots__ = (
        "_fast_keys",
        "_key_set",
        "keys",
        "into",
        "preprocessors",
        "validate_object",
        "validate_object_async",
    )
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
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
        ],
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Result[Ret, Serializable]]]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:

        self.into = into
        self.keys = keys
        # so we don't need to calculate each time we validate
        _key_set = frozenset(k for k, _ in keys)
        self._key_set = _key_set
        self._fast_keys = [
            (
                key,
                validator,
                # 1: _ToTupleValidator and key required
                # 2: (basic) Validator and key required
                # 3: _ToTupleValidator and key not required
                # 4: (basic) Validator and key not required
                (
                    (1 if isinstance(validator, _ToTupleValidator) else 2)
                    if not isinstance(validator, KeyNotRequired)
                    else (3 if isinstance(validator.validator, _ToTupleValidator) else 4)
                ),
                str(key),
            )
            for key, validator in keys
        ]

        self._unknown_keys_err = _make_keys_err(_key_set)

        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async
        self.preprocessors = preprocessors

    def __call__(self, data: Any) -> Result[Ret, Serializable]:

        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR

        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self._key_set:
                return self._unknown_keys_err

        args: List[Any] = []
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, validation_type, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if validation_type == 1 or validation_type == 2:
                    errs.append((str_key, KEY_MISSING_MSG))
                else:
                    args.append(nothing)
            else:
                if validation_type == 1:
                    success, new_val = validator.validate_to_tuple(val)
                elif validation_type == 2:
                    result = validator(val)
                    success, new_val = (result.is_ok, result.val)
                elif validation_type == 3:
                    success, new_val = validator.validate_to_tuple(Just(val))
                else:
                    result = validator(Just(val))
                    success, new_val = (result.is_ok, result.val)

                if not success:
                    errs.append((str_key, new_val))
                elif not errs:
                    args.append(new_val)

        if errs:
            return Err(dict(errs))
        else:
            # we know this should be ret
            obj = self.into(*args)
            if self.validate_object is None:
                return Ok(obj)
            else:
                return self.validate_object(obj)

    async def validate_async(self, data: Any) -> Result[Ret, Serializable]:

        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR

        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self._key_set:
                return self._unknown_keys_err

        args: List[Any] = []
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, validation_type, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if validation_type == 1 or validation_type == 2:
                    errs.append((str_key, KEY_MISSING_MSG))
                else:
                    args.append(nothing)
            else:
                if validation_type == 1:
                    success, new_val = await validator.validate_to_tuple_async(val)
                elif validation_type == 2:
                    result = validator(val)
                    success, new_val = (result.is_ok, result.val)
                elif validation_type == 3:
                    success, new_val = await validator.validate_to_tuple_async(Just(val))
                else:
                    result = validator(Just(val))
                    success, new_val = (result.is_ok, result.val)

                if not success:
                    errs.append((str_key, new_val))
                elif not errs:
                    args.append(new_val)

        if errs:
            return Err(dict(errs))
        else:
            # we know this should be ret
            obj = self.into(*args)
            if self.validate_object is not None:
                return self.validate_object(obj)
            elif self.validate_object_async is not None:
                return await self.validate_object_async(obj)
            else:
                return Ok(obj)


class DictValidatorAny(Validator[Any, Any, Serializable]):
    """
    This differs from DictValidator in a few ways:
    - if valid, it returns a dict; it does not allow another target to be specified
    - it does not narrow the types of keys / values. It always returns
    `Dict[Hashable, Any]`
    - it allows for any number of `KeyValidator`s

    This class exists for two reasons:
    - because the overloads we use to define `DictValidator` get very slow
    for type checkers beyond a certain point, sa we have a max number of
    type-checkable keys
    - if you don't care about the types in the target object

    VALIDATION WILL STILL WORK PROPERLY, but there won't be much type hinting
    assistance.
    """

    __slots__ = (
        "keys",
        "_key_set",
        "_fast_keys",
        "_unknown_keys_err",
        "preprocessors",
        "validate_object",
        "validate_object_async",
    )
    __match_args__ = ("keys", "preprocessors", "validate_object", "validate_object_async")

    def __init__(
        self,
        *,
        keys: Tuple[KeyValidator[Any], ...],
        validate_object: Optional[
            Callable[[Dict[Hashable, Any]], Result[Dict[Hashable, Any], Serializable]]
        ] = None,
        validate_object_async: Optional[
            Callable[
                [Dict[Hashable, Any]],
                Awaitable[Result[Dict[Hashable, Any], Serializable]],
            ]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.keys: Tuple[KeyValidator[Any], ...] = keys
        # so we don't need to calculate each time we validate
        _key_set = frozenset(k for k, _ in keys)
        self._key_set = _key_set
        self._fast_keys = [
            (key, val, not isinstance(val, KeyNotRequired), str(key)) for key, val in keys
        ]

        self._unknown_keys_err = _make_keys_err(_key_set)

        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.preprocessors = preprocessors

    def __call__(self, data: Any) -> Result[Dict[Hashable, Any], Serializable]:

        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR

        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self._key_set:
                return self._unknown_keys_err

        success_dict: Dict[Hashable, Any] = {}
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, key_required, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs.append((str_key, KEY_MISSING_MSG))
                elif not errs:
                    success_dict[key_] = nothing
            else:
                if key_required:
                    result = validator(val)
                else:
                    result = validator(Just(val))

                if not result.is_ok:
                    errs.append((str_key, result.val))
                elif not errs:
                    success_dict[key_] = result.val

        if errs:
            return Err(dict(errs))
        else:
            if self.validate_object is None:
                return Ok(success_dict)
            else:
                return self.validate_object(success_dict)

    async def validate_async(
        self, data: Any
    ) -> Result[Dict[Hashable, Any], Serializable]:

        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR

        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self._key_set:
                return self._unknown_keys_err

        success_dict: Dict[Hashable, Any] = {}
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, key_required, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs.append((str_key, KEY_MISSING_MSG))
                elif not errs:
                    success_dict[key_] = nothing
            else:
                if key_required:
                    result = await validator.validate_async(val)  # type: ignore
                else:
                    result = await validator.validate_async(Just(val))  # type: ignore

                if not result.is_ok:
                    errs.append((str_key, result.val))
                elif not errs:
                    success_dict[key_] = result.val

        if errs:
            return Err(dict(errs))
        else:
            if self.validate_object is not None:
                return self.validate_object(success_dict)
            elif self.validate_object_async is not None:
                return await self.validate_object_async(success_dict)
            else:
                return Ok(success_dict)
