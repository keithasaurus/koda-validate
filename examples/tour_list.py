from koda_validate import *

binary_list_validator = ListValidator(
    IntValidator(Choices({0, 1})), predicates=[MinItems(2)]
)

assert binary_list_validator([1, 0, 0, 1, 0]) == Valid([1, 0, 0, 1, 0])

assert binary_list_validator([1]) == Invalid(
    {"__container__": ["minimum allowed length is 2"]}
)

assert binary_list_validator([0, 1.0, "0"]) == Invalid(
    {"1": ["expected an integer"], "2": ["expected an integer"]}
)
