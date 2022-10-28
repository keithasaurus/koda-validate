from typing import List

from codegen.utils import add_type_vars, get_type_vars  # type: ignore


def generate_code(num_keys: int) -> str:

    dict_validator_into_signatures: List[str] = []
    dict_validator_fields: List[str] = []
    ret = """from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    overload, 
    Final,
    TYPE_CHECKING,
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

"""
    type_vars = get_type_vars(num_keys)
    ret += add_type_vars(type_vars)

    ret += """

class MapValidator(Validator[Any, Dict[T1, T2], Serializable]):
    __slots__ = ('key_validator', 'value_validator', 'predicates')
    __match_args__ = ('key_validator', 'value_validator', 'predicates')

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


def _dict_without_extra_keys(
        keys: Set[str], data: Any
) -> Optional[Err[Serializable]]:
    \"""
    We're returning Optional here because it's faster than Ok/Err,
    and this is just a private function
    \"""
    if isinstance(data, dict):
        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in keys:
                return Err({
                    OBJECT_ERRORS_FIELD: [
                        f"Received unknown keys. Only expected {sorted(keys)}"
                    ]
                })
        return None
    else:
        return _is_dict_validation_err


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


"""
    for i in range(num_keys):
        key_type_vars = type_vars[: i + 1]
        generic_vals = ", ".join(key_type_vars)
        dict_validator_into_signatures.append(f"Callable[[{generic_vals}], Ret]")

        dict_validator_fields.append(
            f"field{i+1}: KeyValidator[{type_vars[i]}]"
            if i == 0
            else f"field{i+1}: Optional[KeyValidator[{type_vars[i]}]] = None"
        )

    ret += """

class DictValidator(
    Generic[Ret],
    Validator[Any, Ret, Serializable]
):
    \"""
    unfortunately, we have to have this be `Any` until
    we're using variadic generics -- or we could generate lots of classes
    \"""
    __slots__ = ('into', 'fields', 'validate_object')
    __match_args__ = ('into', 'fields', 'validate_object')
    
"""
    for i in range(num_keys):
        ret += f"""
    @overload
    def __init__(self,
                 into: Callable[[{",".join(type_vars[:i+1])}], Ret],
"""
        for j in range(i + 1):
            ret += f"                 {dict_validator_fields[j]},\n"
        ret += """                 *,
                 validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
                 ) -> None: 
        ...  # pragma: no cover

"""

    dv_fields_2: str = ",\n".join([f"        {f}" for f in dict_validator_fields])
    tuple_fields = ", ".join([f"field{i+1}" for i in range(num_keys)])

    ret += f"""

    def __init__( 
        self,
        into: Union[
            {", ".join(dict_validator_into_signatures)}
        ],
    {dv_fields_2},
        *non_typed_fields: KeyValidator[Any],
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
    ) -> None:
        self.into = into
        self.fields: Tuple[KeyValidator[Any], ...] = tuple(
            f for f in (
                {tuple_fields},\n
            ) + non_typed_fields if f is not None)
        self.validate_object = validate_object
"""
    ret += """   
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

    """

    return ret


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="generate code.")
    parser.add_argument("--max_keys", type=int, default=20)
    args = parser.parse_args()

    print(generate_code(args.max_keys))
