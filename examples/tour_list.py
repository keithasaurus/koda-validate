from koda_validate import *
from koda_validate.base import IndexErrs, PredicateErrs, TypeErr

binary_int_validator = IntValidator(Choices({0, 1}))
binary_list_validator = ListValidator(binary_int_validator, predicates=[MinItems(2)])

assert binary_list_validator([1, 0, 0, 1, 0]) == Valid([1, 0, 0, 1, 0])

assert binary_list_validator([1]) == Invalid(
    binary_list_validator, [1], PredicateErrs([MinItems(2)])
)

assert binary_list_validator([0, 1.0, "0"]) == Invalid(
    binary_list_validator,
    [0, 1.0, "0"],
    IndexErrs(
        {
            1: Invalid(binary_int_validator, 1.0, TypeErr(int)),
            2: Invalid(binary_int_validator, "0", TypeErr(int)),
        },
    ),
)
