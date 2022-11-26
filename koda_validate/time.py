from datetime import date, datetime
from typing import Any, Final, Literal, Tuple

from koda_validate.base import (
    InvalidCoercion,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)

EXPECTED_DATE_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, InvalidCoercion(
    [str, date], date, "expected date or string formatted as yyyy-mm-dd"
)

EXPECTED_ISO_DATESTRING: Final[
    Tuple[Literal[False], ValidationErr]
] = False, InvalidCoercion(
    [str, datetime], datetime, "expected datetime or iso8601-formatted string"
)


class DateValidator(_ToTupleValidatorUnsafeScalar[Any, date]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is date:
            return True, val
        else:
            try:
                return True, date.fromisoformat(val)
            except (ValueError, TypeError):
                return EXPECTED_DATE_ERR


class DatetimeStringValidator(_ToTupleValidatorUnsafeScalar[Any, datetime]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is datetime:
            return True, val
        else:
            try:
                # note isoparse from dateutil is more flexible if we want
                # to add the dependency at some point
                return True, datetime.fromisoformat(val)
            except (ValueError, TypeError):
                return EXPECTED_ISO_DATESTRING
