from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Final,
    Generic,
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
from koda_validate.typedefs import Predicate, Serializable, Validator

KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, Serializable]]]


OBJECT_ERRORS_FIELD: Final[str] = "__container__"

_is_dict_validation_err: Final[Err[Serializable]] = Err(
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


def key(
    prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[A, Serializable]]]:
    return prop_, RequiredField(validator)


def maybe_key(
    prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[Maybe[A], Serializable]]]:
    return prop_, MaybeField(validator)


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
Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


class MapValidator(Validator[Any, Dict[T1, T2], Serializable]):
    def __init__(
        self,
        key_validator: Validator[Any, T1, Serializable],
        value_validator: Validator[Any, T2, Serializable],
        *predicates: Predicate[Dict[T1, T2], Serializable],
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.predicates = predicates

    def __call__(self, data: Any) -> Result[Dict[T1, T2], Serializable]:
        if isinstance(data, dict):
            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}
            for key, val in data.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val)

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
            for predicate in self.predicates:
                # Note that the expectation here is that validators will likely
                # be doing json like number of keys; they aren't expected
                # to be drilling down into specific keys and values. That may be
                # an incorrect assumption; if so, some minor refactoring is probably
                # necessary.
                result = predicate(data)
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
            return Err({OBJECT_ERRORS_FIELD: ["expected a map"]})


class IsDictValidator(Validator[Any, Dict[Any, Any], Serializable]):
    def __call__(self, val: Any) -> Result[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return _is_dict_validation_err


is_dict_validator = IsDictValidator()


def _dict_without_extra_keys(keys: Set[str], data: Any) -> Optional[Err[Serializable]]:
    """
    We're returning Optional here because it's faster than Ok/Err,
    and this is just a private function
    """
    if isinstance(data, dict):
        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in keys:
                return Err(
                    {
                        OBJECT_ERRORS_FIELD: [
                            f"Received unknown keys. Only expected {sorted(keys)}"
                        ]
                    }
                )
        return None
    else:
        return _is_dict_validation_err


class MinKeys(Predicate[Dict[Any, Any], Serializable]):
    def __init__(self, size: int) -> None:
        self.size = size

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
    def __init__(self, size: int) -> None:
        self.size = size

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


class DictValidator(Generic[Ret], Validator[Any, Ret, Serializable]):
    """
    unfortunately, we have to have this be `Any` until
    we're using variadic generics -- or we could generate lots of classes
    """

    __slots__ = ("fields",)
    __match_args__ = ("fields",)
    fields: Tuple[KeyValidator[Any], ...]

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

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
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
        field11: Optional[KeyValidator[T11]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
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
        field11: Optional[KeyValidator[T11]] = None,
        field12: Optional[KeyValidator[T12]] = None,
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
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
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
        field11: Optional[KeyValidator[T11]] = None,
        field12: Optional[KeyValidator[T12]] = None,
        *non_typed_fields: KeyValidator[Any],
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.fields = tuple(
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
                field11,
                field12,
            )
            + non_typed_fields
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
                if errs is None:
                    errs = [(key_, result.val)]
                else:
                    errs.append((key_, result.val))
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
