from typing import Annotated

import pytest

from koda_validate import MinLength, StringValidator
from koda_validate.signature import (
    InvalidArgsError,
    InvalidReturnError,
    validate_signature,
)


