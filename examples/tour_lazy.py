from typing import Any, Optional

from koda_validate import *

# if enable_recursive_aliases = true in mypy
# NonEmptyList = tuple[int, Optional["NonEmptyList"]]
NonEmptyList = tuple[int, Optional[Any]]


def recur_non_empty_list() -> Tuple2Validator[int, Optional[NonEmptyList]]:
    return non_empty_list_validator


non_empty_list_validator = Tuple2Validator(
    IntValidator(),
    OptionalValidator(Lazy(recur_non_empty_list)),
)

assert non_empty_list_validator((1, (1, (2, (3, (5, None)))))) == Valid(
    (1, (1, (2, (3, (5, None)))))
)
