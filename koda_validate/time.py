from datetime import date, datetime
from typing import Any

from koda_validate._internal import _CoercingValidator, _ResultTuple
from koda_validate.errors import CoercionErr
from koda_validate.valid import Invalid


class DateValidator(_CoercingValidator[date]):
    def coerce_to_type(self, val: Any) -> _ResultTuple[date]:
        if type(val) is date:
            return True, val
        else:
            try:
                return True, date.fromisoformat(val)
            except (ValueError, TypeError):
                return False, Invalid(
                    CoercionErr(
                        {str, date},
                        date,
                    ),
                    val,
                    self,
                )


class DatetimeValidator(_CoercingValidator[datetime]):
    def coerce_to_type(self, val: Any) -> _ResultTuple[datetime]:
        if type(val) is datetime:
            return True, val
        else:
            try:
                # note isoparse from dateutil is more flexible if we want
                # to add the dependency at some point
                return True, datetime.fromisoformat(val)
            except (ValueError, TypeError):
                return False, Invalid(CoercionErr({str, datetime}, datetime), val, self)
