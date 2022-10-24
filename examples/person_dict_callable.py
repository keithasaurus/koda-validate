from koda import Ok

from koda_validate import *


def reverse_person_args_tuple(a: str, b: int) -> tuple[int, str]:
    return b, a


person_validator_2 = dict_validator(
    reverse_person_args_tuple,
    key("name", StringValidator(MinLength(1))),
    key("age", IntValidator(Min(0))),
)

assert person_validator_2({"name": "John Doe", "age": 30}) == Ok((30, "John Doe"))
