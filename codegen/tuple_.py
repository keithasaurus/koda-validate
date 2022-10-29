from typing import List

from codegen.utils import add_type_vars, get_type_vars  # type: ignore


def generate_code(num_keys: int) -> str:
    tuple_into_signatures: List[str] = []
    dict_validator_fields: List[str] = []
    ret = """from typing import (
    Any,
    Callable,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from koda import Err, Ok, Result

from koda_validate.typedefs import Serializable, Validator

"""
    type_vars = get_type_vars(num_keys)
    ret += add_type_vars(type_vars)

    for i in range(num_keys):
        key_type_vars = type_vars[: i + 1]
        generic_vals = ", ".join(key_type_vars)
        tuple_into_signatures.append(f"Callable[[{generic_vals}], Ret]")

        dict_validator_fields.append(
            f"field{i + 1}: Validator[Any, {type_vars[i]}, Serializable]"
            if i == 0
            else f"field{i + 1}: Optional[Validator[Any, {type_vars[i]}, Serializable]] = None"
        )

    ret += """

class TupleValidator(
    Generic[Ret],
    Validator[Any, Ret, Serializable]
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
            ret += f"                 {dict_validator_fields[j]},\n"
        ret += """                 *,
                 validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
                 ) -> None: 
        ...  # pragma: no cover

"""

    dv_fields_2: str = ",\n".join([f"        {f}" for f in dict_validator_fields])
    tuple_fields = ", ".join([f"field{i + 1}" for i in range(num_keys)])

    ret += f"""

    def __init__( 
        self,
        into: Union[
            {", ".join(tuple_into_signatures)}
        ],
    {dv_fields_2},
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None
    ) -> None:
        self.into = into
        self.fields: Tuple[Validator[Any, Any, Serializable], ...] = tuple(
            f for f in (
                {tuple_fields},\n
            ) if f is not None)
        self.validate_object = validate_object
"""
    ret += """
    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        if not isinstance(data, (tuple, list)) or len(data) != len(self.fields):
            return Err([f'expected a tuple or list of length {len(self.fields)}'])

        args = []
        errs: List[Serializable] = []
        # we know that self.fields and data are tuples / lists of the same length
        for value, validator in zip(data, self.fields):
            result = validator(value)
            if isinstance(result, Err):
                errs.append(result.val)
            elif errs is None:
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
