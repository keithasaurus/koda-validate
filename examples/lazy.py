from typing import Optional

from koda import Ok

from koda_validate.generic import Lazy
from koda_validate.integer import IntValidator
from koda_validate.none import OptionalValidator
from koda_validate.tuple import Tuple2Validator

NonEmptyList = tuple[int, Optional["NonEmptyList"]]


def recur_non_empty_list() -> Tuple2Validator[int, Optional[NonEmptyList]]:
    return non_empty_list_validator


non_empty_list_validator = Tuple2Validator(
    IntValidator(),
    OptionalValidator(Lazy(recur_non_empty_list)),
)

assert non_empty_list_validator((1, (1, (2, (3, (5, None)))))) == Ok(
    (1, (1, (2, (3, (5, None)))))
)
