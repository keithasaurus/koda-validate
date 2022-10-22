from codegen.utils import add_type_vars, get_type_vars  # type: ignore


def generate_code(num_keys: int) -> str:

    dict_validator_into_signatures: list[str] = []
    dict_validator_fields: list[str] = []
    dict_validator_overloads: list[str] = []
    ret = """from typing import TypeVar, Generic, Any, Callable, Optional, cast, overload, Union, Final

from koda import Err, Maybe, Ok, Result, mapping_get

from koda_validate.utils import expected
from koda_validate.validators.utils import _flat_map_same_type_if_not_none
from koda_validate.typedefs import Validator, ValidatorFunc, JSONValue, Predicate
from koda_validate.validators.validate_and_map import validate_and_map

"""
    type_vars = get_type_vars(num_keys)
    ret += add_type_vars(type_vars)

    ret += """

OBJECT_ERRORS_FIELD: Final[str] = "__container__"


class MapValidator(Validator[Any, dict[T1, T2], JSONValue]):
    \"\""\
    Note that while a key should always be expected to be received as a string,
    it's possible that we may want to validate and cast it to a different
    type (i.e. a date)
    \"\"\"

    def __init__(
        self,
        key_validator: Validator[Any, T1, JSONValue],
        value_validator: Validator[Any, T2, JSONValue],
        *dict_validators: Predicate[dict[T1, T2], JSONValue],
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.dict_validators = dict_validators

    def __call__(self, data: Any) -> Result[dict[T1, T2], JSONValue]:
        if isinstance(data, dict):
            return_dict: dict[T1, T2] = {}
            errors: dict[str, JSONValue] = {}
            for key, val in data.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val)

                if isinstance(key_result, Ok) and isinstance(val_result, Ok):
                    return_dict[key_result.val] = val_result.val
                else:
                    if isinstance(key_result, Err):
                        errors[f"{key} (key)"] = key_result.val

                    if isinstance(val_result, Err):
                        errors[key] = val_result.val

            dict_validator_errors: list[JSONValue] = []
            for validator in self.dict_validators:
                # Note that the expectation here is that validators will likely
                # be doing json like number of keys; they aren't expected
                # to be drilling down into specific keys and values. That may be
                # an incorrect assumption; if so, some minor refactoring is probably
                # necessary.
                result = validator(data)
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
            return Err({"__container__": [expected("a map")]})


class IsDict(Validator[Any, dict[Any, Any], JSONValue]):
    def __call__(self, val: Any) -> Result[dict[Any, Any], JSONValue]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return Err({OBJECT_ERRORS_FIELD: [expected("a dictionary")]})


def _has_no_extra_keys(
    keys: set[str],
) -> ValidatorFunc[dict[T1, T2], dict[T1, T2], JSONValue]:
    def inner(mapping: dict[T1, T2]) -> Result[dict[T1, T2], JSONValue]:
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
    keys: set[str], data: Any
) -> Result[dict[Any, Any], JSONValue]:
    return IsDict()(data).flat_map(_has_no_extra_keys(keys))



def _tuples_to_json_dict(data: tuple[tuple[str, JSONValue], ...]) -> JSONValue:
    return dict(data)


KeyValidator = tuple[str, Callable[[Maybe[Any]], Result[T1, JSONValue]]]


def _validate_with_key(
        r: KeyValidator[T1], data: dict[Any, Any]
) -> Result[T1, tuple[str, JSONValue]]:
    key, fn = r

    def add_key(val: JSONValue) -> tuple[str, JSONValue]:
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

class Dict{i+1}KeysValidator(Generic[{generic_vals}, Ret], Validator[Any, Ret, JSONValue]):
    __match_args__: tuple[str, ...] = ('dv_fields',)
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
                 validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None
                 ) -> None:
        self.into = into
        self.dv_fields = (
            {" ".join([f'field{j+1},' for j in range(i + 1)])}
        )
        self.validate_object = validate_object
"""
        ret += """
    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None
) -> Validator[Any, Ret, JSONValue]:
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
