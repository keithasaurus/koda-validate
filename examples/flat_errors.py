from dataclasses import dataclass
from typing import List, Optional, TypedDict, Union

from koda_validate import *


@dataclass
class FlatError:
    location: List[Union[int, str]]
    message: str


def to_flat_errs(
    invalid: Invalid, location: Optional[List[Union[str, int]]] = None
) -> List[FlatError]:
    """
    recursively add errors to a flat list
    """
    loc = location or []
    err_type = invalid.err_type

    if isinstance(err_type, TypeErr):
        return [FlatError(loc, f"expected type {err_type.expected_type}")]

    elif isinstance(err_type, MissingKeyErr):
        return [FlatError(loc, "missing key!")]

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
        raise TypeError(f"unhandled type {err_type}")


class Person(TypedDict):
    name: str
    age: int


validator = ListValidator(TypedDictValidator(Person))

simple_result = validator({})
assert isinstance(simple_result, Invalid)
assert to_flat_errs(simple_result) == [
    FlatError(location=[], message=f"expected type <class 'list'>")
]

complex_result = validator([None, {}, {"name": "Bob", "age": "not an int"}])
assert isinstance(complex_result, Invalid)
assert to_flat_errs(complex_result) == [
    FlatError(location=[0], message="expected type <class 'dict'>"),
    FlatError(location=[1, "name"], message="missing key!"),
    FlatError(location=[1, "age"], message="missing key!"),
    FlatError(location=[2, "age"], message="expected type <class 'int'>"),
]
