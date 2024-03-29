from typing import Any, Optional, Tuple

from koda_validate import *

# if enable_recursive_aliases = true in mypy
# NonEmptyList = Tuple[int, Optional["NonEmptyList"]]
NonEmptyList = Tuple[int, Optional[Any]]


def recur_non_empty_list() -> NTupleValidator[Tuple[int, Optional[NonEmptyList]]]:
    return non_empty_list_validator


non_empty_list_validator = NTupleValidator.typed(
    fields=(IntValidator(), OptionalValidator(Lazy(recur_non_empty_list)))
)

assert non_empty_list_validator((1, (1, (2, (3, (5, None)))))) == Valid(
    (1, (1, (2, (3, (5, None)))))
)
