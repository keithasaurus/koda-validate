from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, TypedDict, Union

from koda_validate import *


class ErrCode(Enum):
    TYPE_ERR = 0
    KEY_MISSING = 1


@dataclass
class FlatError:
    location: List[Union[int, str]]
    err_code: ErrCode
    extra: Any = None


def to_flat_errs(
    invalid: Invalid, location: Optional[List[Union[str, int]]] = None
) -> List[FlatError]:
    loc = location or []
    err_type = invalid.err_type
    if isinstance(err_type, TypeErr):
        return [FlatError(loc, ErrCode.TYPE_ERR, err_type.expected_type)]
    elif isinstance(err_type, MissingKeyErr):
        return [FlatError(loc, ErrCode.KEY_MISSING)]
    elif isinstance(err_type, KeyErrs):
        errs = []
        for k, inv_v in err_type.keys.items():
            errs.extend(to_flat_errs(inv_v, loc + [k]))
        return errs
    elif isinstance(err_type, IndexErrs):
        errs = []
        for i, inv_item in err_type.indexes.items():
            errs.extend(to_flat_errs(inv_item, loc + [i]))
        return errs
    else:
        raise TypeError("unhandled type")


class Person(TypedDict):
    name: str
    age: int


validator = ListValidator(TypedDictValidator(Person))

simple_result = validator({})
assert isinstance(simple_result, Invalid)
assert to_flat_errs(simple_result) == [
    FlatError(location=[], err_code=ErrCode.TYPE_ERR, extra=list)
]

complex_result = validator([None, {}, {"name": "Bob", "age": "not an int"}])
assert isinstance(complex_result, Invalid)
assert to_flat_errs(complex_result) == [
    FlatError(location=[0], err_code=ErrCode.TYPE_ERR, extra=dict),
    FlatError(location=[1, "name"], err_code=ErrCode.KEY_MISSING, extra=None),
    FlatError(location=[1, "age"], err_code=ErrCode.KEY_MISSING, extra=None),
    FlatError(location=[2, "age"], err_code=ErrCode.TYPE_ERR, extra=int),
]
