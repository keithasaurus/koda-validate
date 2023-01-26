from typing import Annotated

import pytest

from koda_validate import MinLength, StringValidator
from koda_validate.signature import (
    InvalidArgsError,
    InvalidReturnError,
    validate_signature,
)


def test_annotated() -> None:
    @validate_signature
    def something(
        a: Annotated[str, StringValidator(MinLength(2))]
    ) -> Annotated[str, StringValidator(MinLength(2))]:
        # the function signature here can be regarded as somewhat of a mistake
        # because the return minlength should be 1, since we remove one character. It just
        # serves to allow us to test both the argument and return validators.
        return a[:-1]

    assert something("abc") == "ab"
    with pytest.raises(InvalidArgsError):
        something("")

    with pytest.raises(InvalidReturnError):
        something("ab")
