from typing import List

from codegen.utils import add_type_vars, get_type_vars  # type: ignore


def generate_code(num_fields: int) -> str:
    into_signatures: List[str] = []
    vm_validator_fields: List[str] = []
    vm_overloads: List[str] = []
    type_vars = get_type_vars(num_fields)

    ret = """from functools import partial
from typing import Dict, List, Tuple, Set, TypeVar, Callable, Optional, overload, Union, cast

from koda import Result, Err, Ok

from koda_validate.validators.utils import _flat_map_same_type_if_not_none
"""
    ret += add_type_vars(type_vars)

    for i in range(num_fields):
        key_type_vars = type_vars[: i + 1]
        generic_vals = ", ".join(key_type_vars)
        into_signatures.append(f"Callable[[{generic_vals}], Ret]")

        vh_fields = ",\n".join(
            [
                f"    r{j + 1}: Result[{type_var}, FailT]"
                for j, type_var in enumerate(key_type_vars)
            ]
        )
        vh_next_step_params = ", ".join([f"r{i + 1}" for i in range(1, i + 1)])
        if i == 0:
            ret += """
def _validate1_helper(
    state: Result[Callable[[T1], Ret], Tuple[FailT, ...]], r: Result[T1, FailT]
) -> Result[Ret, Tuple[FailT, ...]]:
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
            next_state_call_sig_params = ", ".join(key_type_vars[1:])
            ret += f"""
def _validate{i + 1}_helper(
    state: Result[{into_signatures[-1]}, Tuple[FailT, ...]],
{vh_fields},
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[{next_state_call_sig_params}], Ret], Tuple[FailT, ...]] = Err(
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
        vm_validator_fields.append(
            f"r{i + 1}: Result[{type_vars[i]}, FailT]"
            if i == 0
            else f"r{i + 1}: Optional[Result[{type_vars[i]}, FailT]] = None"
        )

        vm_overload = f"""

@overload
def validate_and_map(
    into: {into_signatures[-1]},"""
        vm_overload += "".join(
            [
                f"\n    r{j + 1}: Result[{type_var}, FailT],"
                for j, type_var in enumerate(key_type_vars)
            ]
        )
        vm_overload += """
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...

"""
        vm_overloads.append(vm_overload)

    ret += """
def _tupled(a: T1) -> Tuple[T1, ...]:
    return a,


def tupled_err_func(validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]]) -> Callable[
    [Ret], Result[Ret, Tuple[FailT, ...]]]:

    def inner(obj: Ret) -> Result[Ret, Tuple[FailT, ...]]:
        if validate_object is None:
            return Ok(obj)
        else:
            return validate_object(obj).map_err(_tupled)

    return inner

"""

    ret += "\n".join(vm_overloads)

    vm_field_lines: str = ",\n".join([f"    {f}" for f in vm_validator_fields])

    ret += f"""
def validate_and_map(
    into: Union[
        {", ".join(into_signatures)}
    ],
{vm_field_lines},
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None
) -> Result[Ret, Tuple[FailT, ...]]:
    """
    for i in range(1, num_fields + 1):
        r_params = ", ".join([f"r{j}" for j in range(1, i + 1)])
        ret_stmt = f"""
            return _flat_map_same_type_if_not_none(
                tupled_err_func(validate_object),
                _validate{i}_helper(Ok(cast({into_signatures[i - 1]}, into)), {r_params})
            )"""
        if i == 1:
            ret += f"""
        if r{i + 1} is None:
    {ret_stmt}"""
        elif i == num_fields:
            ret += f"""
        else:
    {ret_stmt}
    """
        else:
            ret += f"""
        elif r{i + 1} is None:
    {ret_stmt}
    """

    return ret
