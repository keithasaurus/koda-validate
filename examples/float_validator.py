# from typing import Any
#
# from koda_validate.typedefs import Invalid, Valid, Result#
# from koda_validate import Predicate, Serializable, Validator
# from koda_validate.utils import accum_errors
#
#
# class FloatValidator(Validator[Any, float, Serializable]):
#     def __init__(self, *predicates: Predicate[float, Serializable]) -> None:
#         self.predicates = predicates
#
#     def __call__(self, val: Any) -> Result[float, Serializable]:
#         if isinstance(val, float):
#             if len(self.predicates) > 0:
#                 return accum_errors(val, self.predicates)
#             else:
#                 return Valid(val)
#         else:
#             return Invalid(["expected a float"])
