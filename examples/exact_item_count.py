from koda_validate import (
    ExactItemCount,
    ListValidator,
    StringValidator,
    UniformTupleValidator,
)

list_validator = ListValidator(StringValidator(), predicates=[ExactItemCount(1)])
u_tuple_validator = UniformTupleValidator(
    StringValidator(), predicates=[ExactItemCount(1)]
)
