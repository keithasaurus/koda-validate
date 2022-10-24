from typing import List

from codegen.utils import add_type_vars, get_type_vars  # type: ignore


def generate_code(num_keys: int) -> str:

    dict_validator_into_signatures: List[str] = []
    dict_validator_fields: List[str] = []
    dict_validator_overloads: List[str] = []
    ret = """from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, TypeVar, Generic, Any, Callable, Optional, cast, overload, Union, Final

from koda import Err, Maybe, Ok, Result, mapping_get, Nothing, Just

from koda_validate._generics import A
from koda_validate.utils import expected, _flat_map_same_type_if_not_none, OBJECT_ERRORS_FIELD
from koda_validate.typedefs import Validator, ValidatorFunc, Serializable, Predicate
from koda_validate.validate_and_map import validate_and_map

"""
    type_vars = get_type_vars(num_keys)
    ret += add_type_vars(type_vars)

    ret += """

KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, Serializable]]]


_KEY_MISSING: Final[str] = "key missing"


@dataclass(frozen=True)
class RequiredField(Generic[A]):
    validator: Validator[Any, A, Serializable]

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, Serializable]:
        if isinstance(maybe_val, Nothing):
            return Err([_KEY_MISSING])
        else:
            return self.validator(maybe_val.val)


@dataclass(frozen=True)
class MaybeField(Generic[A]):
    validator: Validator[Any, A, Serializable]

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], Serializable]:
        if isinstance(maybe_val, Just):
            result: Result[Maybe[A], Serializable] = self.validator(maybe_val.val).map(Just)
        else:
            result = Ok(maybe_val)
        return result



def key(
        prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[A, Serializable]]]:
    return prop_, RequiredField(validator)


def maybe_key(
        prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[Maybe[A], Serializable]]]:
    return prop_, MaybeField(validator)


@dataclass(frozen=True, init=False)
class MapValidator(Validator[Any, Dict[T1, T2], Serializable]):
    key_validator: Validator[Any, T1, Serializable]
    value_validator: Validator[Any, T2, Serializable]
    predicates: Tuple[Predicate[Dict[T1, T2], Serializable], ...]

    def __init__(
        self,
        key_validator: Validator[Any, T1, Serializable],
        value_validator: Validator[Any, T2, Serializable],
        *predicates: Predicate[Dict[T1, T2], Serializable],
    ) -> None:
        object.__setattr__(self, "key_validator", key_validator)
        object.__setattr__(self, "value_validator", value_validator)
        object.__setattr__(self, "predicates", predicates)

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
            return Err({OBJECT_ERRORS_FIELD: [expected("a map")]})


class IsDictValidator(Validator[Any, Dict[Any, Any], Serializable]):
    def __call__(self, val: Any) -> Result[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return Err({OBJECT_ERRORS_FIELD: [expected("a dictionary")]})


is_dict_validator = IsDictValidator()

def _has_no_extra_keys(
    keys: Set[str],
) -> ValidatorFunc[Dict[T1, T2], Dict[T1, T2], Serializable]:
    def inner(mapping: Dict[T1, T2]) -> Result[Dict[T1, T2], Serializable]:
        if len(mapping.keys() - keys) > 0:
            return Err(
                {
                    OBJECT_ERRORS_FIELD: [
                        f"Received unknown keys. Only expected {sorted(keys)}"
                    ]
                }
            )
        else:
            return Ok(mapping)

    return inner


def _dict_without_extra_keys(
    keys: Set[str], data: Any
) -> Result[Dict[Any, Any], Serializable]:
    return is_dict_validator(data).flat_map(_has_no_extra_keys(keys))



@dataclass(frozen=True)
class MinKeys(Predicate[Dict[Any, Any], Serializable]):
    size: int

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err_output(self, val: Dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


@dataclass(frozen=True)
class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
    size: int

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err_output(self, val: Dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


def _tuples_to_json_dict(data: Tuple[Tuple[str, Serializable], ...]) -> Serializable:
    return dict(data)


def _validate_with_key(
        r: KeyValidator[T1], data: Dict[Any, Any]
) -> Result[T1, Tuple[str, Serializable]]:
    key, fn = r

    def add_key(val: Serializable) -> Tuple[str, Serializable]:
        return key, val

    return fn(mapping_get(data, key)).map_err(add_key)
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

        ret += f"""

class Dict{i+1}KeysValidator(Generic[{generic_vals}, Ret], Validator[Any, Ret, Serializable]):
    __match_args__: Tuple[str, ...] = ('dv_fields',)
"""
        ret += f"""    def __init__(self,
                 into: {dict_validator_into_signatures[-1]},"""
        ret += "".join(
            [
                f"\n                 field{j+1}: KeyValidator[{type_var}],"
                for j, type_var in enumerate(key_type_vars)
            ]
        )
        ret += f"""
                 *,
                 validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
                 ) -> None:
        self.into = into
        self.dv_fields = (
            {" ".join([f'field{j+1},' for j in range(i + 1)])}
        )
        self.validate_object = validate_object
"""
        ret += """
    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        result = _dict_without_extra_keys(
    """
        ret += "        {"
        ret += ", ".join([f"self.dv_fields[{j}][0]" for j in range(i + 1)])
        ret += "},"
        ret += "\n            data"
        ret += """
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
"""
        ret += "\n".join(
            [
                f"                _validate_with_key(self.dv_fields[{j}], result.val),"
                for j in range(i + 1)
            ]
        )
        ret += """
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )
"""

        # overload for dict_validator
        dv_overload = f"""

@overload
def dict_validator(
    into: {dict_validator_into_signatures[-1]},"""
        dv_overload += "".join(
            [
                f"\n    field{j+1}: KeyValidator[{type_var}],"
                for j, type_var in enumerate(key_type_vars)
            ]
        )
        dv_overload += """
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...
"""
        dict_validator_overloads.append(dv_overload)

    ret += "\n".join(dict_validator_overloads)

    dv_fields: str = ",\n".join([f"    {f}" for f in dict_validator_fields])

    ret += f"""

def dict_validator(
    into: Union[
        {", ".join(dict_validator_into_signatures)}
    ],
{dv_fields},
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
) -> Validator[Any, Ret, Serializable]:
"""
    for i in range(1, num_keys + 1):
        dv_fields = ", ".join([f"field{j}" for j in range(1, i + 1)])
        ret_stmt = f"        return Dict{i}KeysValidator(cast({dict_validator_into_signatures[i-1]}, into), {dv_fields}, validate_object=validate_object)"
        if i == 1:
            ret += f"""
    if field{i + 1} is None:
{ret_stmt}"""
        elif i == num_keys:
            ret += f"""
    else:
{ret_stmt}
"""
        else:
            ret += f"""
    elif field{i+1} is None:
{ret_stmt}
"""

    return ret


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="generate code.")
    parser.add_argument("--max_keys", type=int, default=20)
    args = parser.parse_args()

    print(generate_code(args.max_keys))
