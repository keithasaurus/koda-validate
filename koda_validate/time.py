from datetime import date, datetime
from typing import Any

from koda_validate._internal import _CoercionValidator
from koda_validate.base import InvalidCoercion, _ResultTupleUnsafe


class DateValidator(_CoercionValidator[Any, date]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
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


class DatetimeValidator(_CoercionValidator[Any, datetime]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is datetime:
            return True, val
        else:
            try:
                # note isoparse from dateutil is more flexible if we want
                # to add the dependency at some point
                return True, datetime.fromisoformat(val)
            except (ValueError, TypeError):
                return False, InvalidCoercion(self, [str, datetime], datetime)
