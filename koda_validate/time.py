from datetime import date, datetime
from typing import Any

from koda_validate.base import (
    InvalidCoercion,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)


class DateValidator(_ToTupleValidatorUnsafeScalar[Any, date]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is date:
            return True, val
        else:
            try:
                return True, date.fromisoformat(val)
            except (ValueError, TypeError):
                return False, InvalidCoercion(
                    self,
                    [str, date],
                    date,
                )


class DatetimeValidator(_ToTupleValidatorUnsafeScalar[Any, datetime]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is datetime:
            return True, val
        else:
            try:
                # note isoparse from dateutil is more flexible if we want
                # to add the dependency at some point
                return True, datetime.fromisoformat(val)
            except (ValueError, TypeError):
                return False, InvalidCoercion(self, [str, datetime], datetime)
