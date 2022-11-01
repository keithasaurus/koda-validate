from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Final,
    Generic,
    Hashable,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from koda import Err, Just, Maybe, Ok, Result, mapping_get, nothing

from koda_validate._generics import A
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)

DictKey = Hashable


OBJECT_ERRORS_FIELD: Final[str] = "__container__"

EXPECTED_DICT_ERR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected a dictionary"]}
)


def _tuples_to_json_dict(data: List[Tuple[str, Serializable]]) -> Serializable:
    return dict(data)


# extracted into constant to optimize
KEY_MISSING_ERR: Final[Err[Serializable]] = Err(["key missing"])


class RequiredField(Generic[A]):
    __slots__ = ("validator",)

    def __init__(self, validator: Validator[Any, A, Serializable]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, Serializable]:
        if maybe_val is nothing:
            return KEY_MISSING_ERR
        else:
            # we use the `is nothing` comparison above because `nothing`
            # is a singleton; but mypy doesn't know that this _must_ be a Just now
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(maybe_val, Just)
            return self.validator(maybe_val.val)

    async def validate_async(self, maybe_val: Maybe[Any]) -> Result[A, Serializable]:
        if maybe_val is nothing:
            return KEY_MISSING_ERR
        else:
            # we use the `is nothing` comparison above because `nothing`
            # is a singleton; but mypy doesn't know that this _must_ be a Just now
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(maybe_val, Just)
            return self.validator(maybe_val.val)


class MaybeField(Generic[A]):
    __slots__ = ("validator",)

    def __init__(self, validator: Validator[Any, A, Serializable]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], Serializable]:
        if maybe_val is nothing:
            return Ok(maybe_val)
        else:
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(maybe_val, Just)
            return self.validator(maybe_val.val).map(Just)

    async def validate_async(
        self, maybe_val: Maybe[Any]
    ) -> Result[Maybe[A], Serializable]:
        if maybe_val is nothing:
            return Ok(maybe_val)
        else:
            # we use the `is nothing` comparison above because `nothing`
            # is a singleton; but mypy doesn't know that this _must_ be a Just now
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(maybe_val, Just)
            return self.validator(maybe_val.val).map(Just)


KeyValidator = Tuple[DictKey, Union[RequiredField[A], MaybeField[A]]]


def key(
    key_: DictKey, validator: Validator[Any, A, Serializable]
) -> Tuple[DictKey, RequiredField[A]]:
    return key_, RequiredField(validator)


def maybe_key(
    key_: DictKey, validator: Validator[Any, A, Serializable]
) -> Tuple[DictKey, MaybeField[A]]:
    return key_, MaybeField(validator)


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

EXPECTED_MAP_ERR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected a map"]}
)


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

                if isinstance(key_result, Ok) and isinstance(val_result, Ok):
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if isinstance(key_result, Err):
                        errors[err_key] = {"key_error": key_result.val}

                    if isinstance(val_result, Err):
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if isinstance(errs, Just) and isinstance(errs.val, dict):
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
                    if isinstance(result, Err):
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

                if isinstance(key_result, Ok) and isinstance(val_result, Ok):
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if isinstance(key_result, Err):
                        errors[err_key] = {"key_error": key_result.val}

                    if isinstance(val_result, Err):
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if isinstance(errs, Just) and isinstance(errs.val, dict):
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
                    if isinstance(result, Err):
                        dict_validator_errors.append(result.val)

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    result = await pred_async.validate_async(val)
                    if isinstance(result, Err):
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


def _dict_without_extra_keys(
    keys: Set[Hashable], data: Any
) -> Optional[Err[Serializable]]:
    """
    We're returning Optional here because it's faster than Ok/Err,
    and this is just a private function
    """
    if isinstance(data, dict):
        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in keys:
                if len(keys) == 0:
                    key_msg = "Expected empty dictionary"
                else:
                    key_msg = "Only expected " + ", ".join(
                        sorted([repr(k) for k in keys])
                    )
                return Err({OBJECT_ERRORS_FIELD: [f"Received unknown keys. {key_msg}."]})
        return None
    else:
        return EXPECTED_DICT_ERR


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


class DictValidator(Generic[Ret], Validator[Any, Ret, Serializable]):
    __slots__ = ("into", "fields", "validate_object")
    __match_args__ = ("into", "fields", "validate_object")

    @overload
    def __init__(
        self,
        into: Callable[[T1], Ret],
        field1: KeyValidator[T1],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        field5: Optional[KeyValidator[T5]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        field5: Optional[KeyValidator[T5]] = None,
        field6: Optional[KeyValidator[T6]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        field5: Optional[KeyValidator[T5]] = None,
        field6: Optional[KeyValidator[T6]] = None,
        field7: Optional[KeyValidator[T7]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        field5: Optional[KeyValidator[T5]] = None,
        field6: Optional[KeyValidator[T6]] = None,
        field7: Optional[KeyValidator[T7]] = None,
        field8: Optional[KeyValidator[T8]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        field5: Optional[KeyValidator[T5]] = None,
        field6: Optional[KeyValidator[T6]] = None,
        field7: Optional[KeyValidator[T7]] = None,
        field8: Optional[KeyValidator[T8]] = None,
        field9: Optional[KeyValidator[T9]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        field5: Optional[KeyValidator[T5]] = None,
        field6: Optional[KeyValidator[T6]] = None,
        field7: Optional[KeyValidator[T7]] = None,
        field8: Optional[KeyValidator[T8]] = None,
        field9: Optional[KeyValidator[T9]] = None,
        field10: Optional[KeyValidator[T10]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
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
        field1: KeyValidator[T1],
        field2: Optional[KeyValidator[T2]] = None,
        field3: Optional[KeyValidator[T3]] = None,
        field4: Optional[KeyValidator[T4]] = None,
        field5: Optional[KeyValidator[T5]] = None,
        field6: Optional[KeyValidator[T6]] = None,
        field7: Optional[KeyValidator[T7]] = None,
        field8: Optional[KeyValidator[T8]] = None,
        field9: Optional[KeyValidator[T9]] = None,
        field10: Optional[KeyValidator[T10]] = None,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        """
        unfortunately, we have to have this be `Any` until
        we're using variadic generics -- or we could generate lots of classes
        """
        self.fields: Tuple[KeyValidator[Any], ...] = tuple(
            f
            for f in (
                field1,
                field2,
                field3,
                field4,
                field5,
                field6,
                field7,
                field8,
                field9,
                field10,
            )
            if f is not None
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        if (
            keys_result := _dict_without_extra_keys({k for k, _ in self.fields}, data)
        ) is not None:
            return keys_result

        args = []
        errs: Optional[List[Tuple[str, Serializable]]] = None
        for key_, validator in self.fields:
            # optimized away the call to `koda.mapping_get`
            if key_ in data:
                result = validator(Just(data[key_]))
            else:
                result = validator(nothing)

            # (slightly) optimized; can be simplified if needed
            if isinstance(result, Err):
                err = (str(key_), result.val)
                if errs is None:
                    errs = [err]
                else:
                    errs.append(err)
            elif errs is None:
                args.append(result.val)

        if errs and len(errs) > 0:
            return Err(_tuples_to_json_dict(errs))
        else:
            obj = self.into(*args)
            if self.validate_object is None:
                return Ok(obj)
            else:
                return self.validate_object(obj)


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

    __slots__ = ("fields", "validate_object")
    __match_args__ = ("fields", "validate_object")

    def __init__(
        self,
        *fields: KeyValidator[Any],
        validate_object: Optional[
            Callable[[Dict[Hashable, Any]], Result[Dict[Hashable, Any], Serializable]]
        ] = None,
    ) -> None:
        self.fields: Tuple[KeyValidator[Any], ...] = fields
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Dict[Hashable, Any], Serializable]:
        if (
            keys_result := _dict_without_extra_keys({k for k, _ in self.fields}, data)
        ) is not None:
            return keys_result

        success_dict: Dict[Hashable, Any] = {}
        errs: Optional[List[Tuple[str, Serializable]]] = None
        for key_, validator in self.fields:
            # optimized away the call to `koda.mapping_get`
            if key_ in data:
                result = validator(Just(data[key_]))
            else:
                result = validator(nothing)

            # (slightly) optimized; can be simplified if needed
            if isinstance(result, Err):
                err = (str(key_), result.val)
                if errs is None:
                    errs = [err]
                else:
                    errs.append(err)
            elif errs is None:
                success_dict[key_] = result.val

        if errs and len(errs) > 0:
            return Err(_tuples_to_json_dict(errs))
        else:
            if self.validate_object is None:
                return Ok(success_dict)
            else:
                return self.validate_object(success_dict)
