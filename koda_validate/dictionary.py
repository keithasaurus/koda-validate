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

from koda import Just, Maybe, mapping_get, nothing

from koda_validate._generics import A
from koda_validate.base import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)
from koda_validate.validated import Invalid, Valid, Validated

OBJECT_ERRORS_FIELD: Final[str] = "__container__"

EXPECTED_DICT_ERR: Final[Invalid[Serializable]] = Invalid(
    {OBJECT_ERRORS_FIELD: ["expected a dictionary"]}
)

EXPECTED_MAP_ERR: Final[Invalid[Serializable]] = Invalid(
    {OBJECT_ERRORS_FIELD: ["expected a map"]}
)

OK_NOTHING: Final[Validated[Maybe[Any], Any]] = Valid(nothing)

KEY_MISSING_MSG: Final[Serializable] = ["key missing"]
KEY_MISSING_ERR: Final[Invalid[Serializable]] = Invalid(KEY_MISSING_MSG)


class KeyNotRequired(Generic[A]):
    """
    For complex type reasons in the KeyValidator defintion,
    this does not subclass Validator (even though it probably should)
    """

    def __init__(self, validator: Validator[Any, A, Serializable]):
        self.validator = validator

    def __call__(self, val: Any) -> Validated[Maybe[A], Serializable]:
        return self.validator(val).map(Just)

    async def validate_async(self, val: Any) -> Validated[Maybe[A], Serializable]:
        return (await self.validator.validate_async(val)).map(Just)


KeyValidator = Tuple[
    Hashable,
    Union[
        Validator[Any, A, Serializable],
        # this is NOT a validator intentionally; for typing reasons
        # ONLY intended for using KeyNotRequired
        Callable[[Maybe[Any]], Validated[A, Serializable]],
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

    def __call__(self, val: Any) -> Validated[Dict[T1, T2], Serializable]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}
            for key, val_ in val.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val_)

                if key_result.is_valid and val_result.is_valid:
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if not key_result.is_valid:
                        errors[err_key] = {"key_error": key_result.val}

                    if not val_result.is_valid:
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
                    if not result.is_valid:
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Invalid(errors)
            else:
                return Valid(return_dict)
        else:
            return EXPECTED_MAP_ERR

    async def validate_async(self, val: Any) -> Validated[Dict[T1, T2], Serializable]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}

            for key, val_ in val.items():
                key_result = await self.key_validator.validate_async(key)
                val_result = await self.value_validator.validate_async(val_)

                if key_result.is_valid and val_result.is_valid:
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if not key_result.is_valid:
                        errors[err_key] = {"key_error": key_result.val}

                    if not val_result.is_valid:
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
                    if not result.is_valid:
                        dict_validator_errors.append(result.val)

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    result = await pred_async.validate_async(val)
                    if not result.is_valid:
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Invalid(errors)
            else:
                return Valid(return_dict)
        else:
            return EXPECTED_MAP_ERR


class IsDictValidator(Validator[Any, Dict[Any, Any], Serializable]):
    def __call__(self, val: Any) -> Validated[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Valid(val)
        else:
            return EXPECTED_DICT_ERR

    async def validate_async(self, val: Any) -> Validated[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Valid(val)
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


def _make_keys_Invalid(keys: FrozenSet[Hashable]) -> Invalid[Serializable]:
    return Invalid(
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
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
        ],
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[
            Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:

        self.into = into
        self.keys = keys
        # so we don't need to calculate each time we validate
        _key_set = frozenset(k for k, _ in keys)
        self._key_set = _key_set
        self._fast_keys = [
            (key, val, not isinstance(val, KeyNotRequired), str(key)) for key, val in keys
        ]

        self._unknown_keys_err = _make_keys_Invalid(_key_set)

        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async
        self.preprocessors = preprocessors

    def __call__(self, data: Any) -> Validated[Ret, Serializable]:

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
        for key_, validator, key_required, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs.append((str_key, KEY_MISSING_MSG))
                else:
                    args.append(nothing)
            else:
                result = validator(val)

                if not result.is_valid:
                    errs.append((str_key, result.val))
                else:
                    args.append(result.val)

        if errs:
            return Invalid(dict(errs))
        else:
            # we know this should be ret
            obj = self.into(*args)
            if self.validate_object is None:
                return Valid(obj)
            else:
                return self.validate_object(obj)

    async def validate_async(self, data: Any) -> Validated[Ret, Serializable]:

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
        for key_, validator, key_required, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs.append((str_key, KEY_MISSING_MSG))
                else:
                    args.append(nothing)
            else:
                result = await validator.validate_async(val)  # type: ignore

                if not result.is_valid:
                    errs.append((str_key, result.val))
                else:
                    args.append(result.val)

        if errs:
            return Invalid(dict(errs))
        else:
            # we know this should be ret
            obj = self.into(*args)
            if self.validate_object is not None:
                return self.validate_object(obj)
            elif self.validate_object_async is not None:
                return await self.validate_object_async(obj)
            else:
                return Valid(obj)


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
            Callable[[Dict[Hashable, Any]], Validated[Dict[Hashable, Any], Serializable]]
        ] = None,
        validate_object_async: Optional[
            Callable[
                [Dict[Hashable, Any]],
                Awaitable[Validated[Dict[Hashable, Any], Serializable]],
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

        self._unknown_keys_err = _make_keys_Invalid(_key_set)

        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.preprocessors = preprocessors

    def __call__(self, data: Any) -> Validated[Dict[Hashable, Any], Serializable]:

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
                result = validator(val)

                if not result.is_valid:
                    errs.append((str_key, result.val))
                elif not errs:
                    success_dict[key_] = result.val

        if errs:
            return Invalid(dict(errs))
        else:
            if self.validate_object is None:
                return Valid(success_dict)
            else:
                return self.validate_object(success_dict)

    async def validate_async(
        self, data: Any
    ) -> Validated[Dict[Hashable, Any], Serializable]:

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
                result = await validator.validate_async(val)  # type: ignore

                if not result.is_valid:
                    errs.append((str_key, result.val))
                elif not errs:
                    success_dict[key_] = result.val

        if errs:
            return Invalid(dict(errs))
        else:
            if self.validate_object is not None:
                return self.validate_object(success_dict)
            elif self.validate_object_async is not None:
                return await self.validate_object_async(success_dict)
            else:
                return Valid(success_dict)
