from koda_validate import *
from koda_validate.base import IndexErrs, TypeErr

binary_list_validator = ListValidator(
    IntValidator(Choices({0, 1})), predicates=[MinItems(2)]
)

assert binary_list_validator([1, 0, 0, 1, 0]) == Valid([1, 0, 0, 1, 0])

assert binary_list_validator([1]) == Invalid([MinItems(2)])

assert binary_list_validator([0, 1.0, "0"]) == Invalid(
    IndexErrs(
        {1: TypeErr(int, "expected an integer"), 2: TypeErr(int, "expected an integer")}
    )
)
