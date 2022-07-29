from pathlib import Path


def generate_code(num_keys: int):
    type_vars = [f"T{i}" for i in range(1, num_keys + 1)]
    dict_validator_into_signatures: list[str] = []
    dict_validator_fields: list[str] = []
    vm_validator_fields: list[str] = []
    ret = """from functools import partial
from typing import TypeVar, Generic, Any, Callable, Optional, cast, overload, Union

from koda import Err, Maybe, Ok, Result, mapping_get

from koda_validate._cruft import _flat_map_same_type_if_not_none
from koda_validate.typedefs import Validator, JSONValue
from koda_validate.validators import _dict_without_extra_keys, _validate_with_key


"""
    for type_var in type_vars:
        ret += f'{type_var} = TypeVar("{type_var}")\n'

    ret += 'Ret = TypeVar("Ret")\n'
    ret += 'FailT = TypeVar("FailT")\n'

    ret += """

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
            else f"field{i+1}: Optional[KeyValidator[{type_vars[i]}]]"
        )
        vm_validator_fields.append(
            f"r{i + 1}: Result[{type_vars[i]}, FailT]"
            if i == 0
            else f"r{i + 1}: Optional[Result[{type_vars[i]}, FailT]]"
        )

        ret += f"""

class Dict{i+1}KeysValidator(Generic[{generic_vals}, Ret], Validator[Any, Ret, JSONValue]):
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
        self.dv_field_lines = (
            {" ".join([f'field{j+1},' for j in range(i + 1)])}
        )
        self.validate_object = validate_object
"""
        ret += f"""
    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
    """
        ret += "        {"
        ret += ", ".join([f"self.dv_field_lines[{j}][0]" for j in range(i + 1)])
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
                f"                _validate_with_key(self.dv_field_lines[{j}], result.val),"
                for j in range(i + 1)
            ]
        )
        ret += """ 
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )
"""

        # overload for _dict_validator
        ret += f"""

@overload
def _dict_validator(
    into: {dict_validator_into_signatures[-1]},"""
        ret += "".join(
            [
                f"\n    field{j+1}: KeyValidator[{type_var}],"
                for j, type_var in enumerate(key_type_vars)
            ]
        )
        ret += """
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
    ...
"""
        ret += f"""

@overload
def validate_and_map(
    into: {dict_validator_into_signatures[-1]},"""
        ret += "".join(
            [
                f"\n    r{j+1}: Result[{type_var}, FailT],"
                for j, type_var in enumerate(key_type_vars)
            ]
        )
        ret += f"""
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...

"""
        vh_fields = ",\n".join(
            [
                f"    r{j+1}: Result[{type_var}, FailT]"
                for j, type_var in enumerate(key_type_vars)
            ]
        )
        vh_next_step_params = ", ".join([f"r{i + 1}" for i in range(1, i + 1)])
        if i == 0:
            ret += f"""
def _validate1_helper(
    state: Result[Callable[[T1], Ret], tuple[FailT, ...]], r: Result[T1, FailT]
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r, Err):
        if isinstance(state, Err):
            return Err(state.val + (r.val,))
        else:
            return Err((r.val,))
    else:
        if isinstance(state, Err):
            return state
        else:
            return Ok(state.val(r.val))
"""
        else:
            ret += f"""
def _validate{i+1}_helper(
    state: Result[{dict_validator_into_signatures[-1]}, tuple[FailT, ...]],
{vh_fields},
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[{dict_validator_into_signatures[-1]}, tuple[FailT, ...]] = Err(
                state.val + (r1.val,)
            )
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate{i}_helper(next_state, {vh_next_step_params})

"""
    dv_field_lines: str = ",\n".join([f"    {f}" for f in dict_validator_fields])

    ret += f"""

def _dict_validator(
    into: Union[
        {", ".join(dict_validator_into_signatures)}
    ],
{dv_field_lines},
    *,
    validate_object: Callable[[Ret], Result[Ret, JSONValue]]
) -> Validator[Any, Ret, JSONValue]: 
"""
    for i in range(1, num_keys + 1):
        dv_field_lines = ", ".join([f"field{j}" for j in range(1, i + 1)])
        ret_stmt = f"        return Dict{i}KeysValidator(into, {dv_field_lines}, validate_object=validate_object)"
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

    vm_field_lines: str = ",\n".join([f"    {f}" for f in vm_validator_fields])

    ret += f"""
def validate_and_map(
    into: Union[
        {", ".join(dict_validator_into_signatures)}
    ],
{vm_field_lines},
    *,
    validate_object: Callable[[Ret], Result[Ret, JSONValue]]
) -> Result[Ret, tuple[FailT, ...]]: 
"""
    for i in range(1, num_keys + 1):
        r_params = ", ".join([f"r{j}" for j in range(1, i + 1)])
        ret_stmt = f"""
        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate{i}_helper(Ok(cast({dict_validator_into_signatures[i - 1]}, into)), {r_params})
        )"""
        if i == 1:
            ret += f"""
    if r{i + 1} is None:
{ret_stmt}"""
        elif i == num_keys:
            ret += f"""
    else:
{ret_stmt}    
"""
        else:
            ret += f"""
    elif r{i+1} is None:
{ret_stmt} 
"""

    return ret


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="generate code.")
    parser.add_argument("--max_keys", type=int, default=20)
    args = parser.parse_args()

    print(generate_code(args.max_keys))
