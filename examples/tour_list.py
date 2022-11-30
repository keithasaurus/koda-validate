from koda_validate import *
from koda_validate.base import InvalidIterable, InvalidPredicates, InvalidType

binary_int_validator = IntValidator(Choices({0, 1}))
binary_list_validator = ListValidator(binary_int_validator, predicates=[MinItems(2)])

assert binary_list_validator([1, 0, 0, 1, 0]) == Valid([1, 0, 0, 1, 0])

assert binary_list_validator([1]) == Invalid(
    InvalidPredicates(binary_list_validator, [MinItems(2)])
)

assert binary_list_validator([0, 1.0, "0"]) == Invalid(
    InvalidIterable(
        binary_list_validator,
        {
            1: InvalidType(binary_int_validator, int),
            2: InvalidType(binary_int_validator, int),
        },
    )
)
