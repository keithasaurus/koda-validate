from typing import List


def get_type_vars(num_vars: int) -> List[str]:
    return [f"T{i}" for i in range(1, num_vars + 1)]


def add_type_vars(type_vars: List[str]) -> str:
    ret = ""
    for type_var in type_vars:
        ret += f'{type_var} = TypeVar("{type_var}")\n'

    ret += 'Ret = TypeVar("Ret")\n'
    ret += 'FailT = TypeVar("FailT")\n'

    return ret
