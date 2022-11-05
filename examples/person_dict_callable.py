from koda import Ok

from koda_validate import *


def reverse_person_args_tuple(a: str, b: int) -> tuple[int, str]:
    return b, a


person_validator_2 = DictValidator(
    keys=(("name", StringValidator(MinLength(1))), ("age", IntValidator(Min(0)))),
    into=reverse_person_args_tuple,
)

assert person_validator_2({"name": "John Doe", "age": 30}) == Ok((30, "John Doe"))
