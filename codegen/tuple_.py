"""
NOT READY YET
"""

from typing import List

from codegen.utils import add_type_vars, get_type_vars


def generate_code(num_keys: int) -> str:
    ret = """from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from koda_validate.typedefs import Err, Ok, Result

from koda_validate._generics import A
from koda_validate.typedefs import Serializable, Validator
from koda_validate.utils import OBJECT_ERRORS_FIELD


class _NotSet:
    pass


_not_set = _NotSet()

_Settable = Union[A, _NotSet]
"""
    tuple_into_signatures: List[str] = []
    tuple_validator_fields: List[str] = []
    typed_tuple_args: List[str] = []
    typed_tuple_ret: List[str] = []
    type_vars_at_indices: List[List[str]] = []

    type_vars = get_type_vars(num_keys)
    ret += add_type_vars(type_vars)

    for i in range(num_keys):
        type_vars_at_index = type_vars[: i + 1]
        type_vars_at_indices.append(type_vars_at_index)
        generic_vals = ", ".join(type_vars_at_index)
        tuple_into_signatures.append(f"Callable[[{generic_vals}], Ret]")

        tuple_validator_fields.append(
            f"field{i + 1}: Validator[{type_vars[i]}]"
            if i == 0
            else f"field{i + 1}: Optional[Validator[{type_vars[i]}]] = None"
        )

        typed_tuple_args.append(
            ", ".join([f"{t_.lower()}: {t_}" for t_ in type_vars_at_index])
        )
        typed_tuple_ret.append(generic_vals)

        ret += f"""
@overload
def typed_tuple({typed_tuple_args[i]}) -> Tuple[{typed_tuple_ret[i]}]:
    ...  # pragma: no cover
    
"""

    tt_fields: str = ",\n".join(
        [
            (
                f"    {tv.lower()}:{tv}"
                if i == 0
                else f"    {tv.lower()}: Union[{tv}, _NotSet] = _not_set"
            )
            for i, tv in enumerate(type_vars)
        ]
    )
    tt_return_fields: str = "\n    ".join([f"Tuple[{t}]," for t in typed_tuple_ret])
    ret += f"""
def typed_tuple(
{tt_fields}
) -> Union[
{tt_return_fields}
]:
"""
    for i, type_vars_ in enumerate(type_vars_at_indices):
        return_line = f"""return {", ".join([t.lower() for t in type_vars_])},"""
        if i == 0:
            ret += f"""
    if isinstance({type_vars_at_indices[i+1][-1].lower()}, _NotSet):
        {return_line} 
"""
        elif i < num_keys - 1:
            ret += f"""
    elif isinstance({type_vars_at_indices[i+1][-1].lower()}, _NotSet):
        {return_line}
"""
        else:
            ret += f"""
    else:
        {return_line}
"""

    ret += """

class TupleValidator(
    Generic[Ret],
    Validator[Ret]
):
    __slots__ = ('into', 'fields', 'validate_object')
    __match_args__ = ('into', 'fields', 'validate_object')
    
"""
    for i in range(num_keys):
        ret += f"""
    @overload
    def __init__(self,
                 into: Callable[[{",".join(type_vars[:i + 1])}], Ret],
"""
        for j in range(i + 1):
            ret += f"                 {tuple_validator_fields[j]},\n"
        ret += """                 *,
                 validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
                 ) -> None: 
        ...  # pragma: no cover

"""

    dv_fields_2: str = ",\n".join([f"        {f}" for f in tuple_validator_fields])
    tuple_fields = ", ".join([f"field{i + 1}" for i in range(num_keys)])

    ret += f"""

    def __init__( 
        self,
        into: Union[
            {", ".join(tuple_into_signatures)}
        ],
    {dv_fields_2},
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
    ) -> None:
        self.into = into
        self.fields: Tuple[Validator[Any], ...] = tuple(
            f for f in (
                {tuple_fields},\n
            ) if f is not None)
        self.validate_object = validate_object
"""
    ret += """
    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        if not isinstance(data, (tuple, list)) or len(data) != len(self.fields):
            return Err({OBJECT_ERRORS_FIELD: [f'expected list or tuple of length {len(self.fields)}']})

        args = []
        errs: Dict[str, Serializable] = {}
        # we know that self.fields and data are tuples / lists of the same length
        for i, (value, validator) in enumerate(zip(data, self.fields)):
            result = validator(value)
            if isinstance(result, Err):
                errs[str(i)] = result.val
            else:
                args.append(result.val)

        if len(errs) > 0:
            return Err(errs)
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
