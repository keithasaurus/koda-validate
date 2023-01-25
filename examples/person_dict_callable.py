from koda_validate import *
from typing import Tuple


def reverse_person_args_tuple(a: str, b: int) -> Tuple[int, str]:
    return b, a


person_validator_2 = RecordValidator(
    into=reverse_person_args_tuple,
    keys=(("name", StringValidator(MinLength(1))), ("age", IntValidator(Min(0)))),
)

assert person_validator_2({"name": "John Doe", "age": 30}) == Valid((30, "John Doe"))
