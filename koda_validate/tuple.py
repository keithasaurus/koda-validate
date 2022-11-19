"""
We should replace Tuple2Validator and Tuple3Validator
with a generic TupleValidator... (2 and 3 can still use the new one
under the hood, if needed)
"""

from typing import Any, Callable, Dict, Final, List, Literal, Optional, Tuple

from koda_validate._cruft import _typed_tuple
from koda_validate._generics import A, B, C
from koda_validate._internals import (
    OBJECT_ERRORS_FIELD,
    _async_predicates_warning,
    _variant_errors,
)
from koda_validate._validate_and_map import validate_and_map
from koda_validate.base import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)
from koda_validate.validated import Invalid, Validated


def _tuple_to_dict_errors(errs: Tuple[Serializable, ...]) -> Dict[str, Serializable]:
    return {str(i): err for i, err in enumerate(errs)}


EXPECTED_TUPLE_TWO_ERROR: Final[Invalid[Serializable]] = Invalid(
    {OBJECT_ERRORS_FIELD: ["expected list or tuple of length 2"]}
)

EXPECTED_TUPLE_THREE_ERROR: Final[Invalid[Serializable]] = Invalid(
    {OBJECT_ERRORS_FIELD: ["expected list or tuple of length 3"]}
)


# todo: auto-generate
class Tuple2Validator(Validator[Any, Tuple[A, B], Serializable]):
    required_length: int = 2

    __match_args__ = ("slot1_validator", "slot2_validator", "tuple_validator")
    __slots__ = __match_args__

    def __init__(
        self,
        slot1_validator: Validator[Any, A, Serializable],
        slot2_validator: Validator[Any, B, Serializable],
        tuple_validator: Optional[
            Callable[[Tuple[A, B]], Validated[Tuple[A, B], Serializable]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Validated[Tuple[A, B], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Validated[Tuple[A, B], Tuple[Serializable, ...]] = validate_and_map(
                _typed_tuple,
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
            )

            if not result.is_valid:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_TWO_ERROR

    async def validate_async(self, data: Any) -> Validated[Tuple[A, B], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Validated[Tuple[A, B], Tuple[Serializable, ...]] = validate_and_map(
                _typed_tuple,
                await self.slot1_validator.validate_async(data[0]),
                await self.slot2_validator.validate_async(data[1]),
            )

            if not result.is_valid:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_TWO_ERROR


class Tuple3Validator(Validator[Any, Tuple[A, B, C], Serializable]):
    required_length: int = 3
    __match_args__ = (
        "slot1_validator",
        "slot2_validator",
        "slot3_validator",
        "tuple_validator",
    )
    __slots__ = __match_args__

    def __init__(
        self,
        slot1_validator: Validator[Any, A, Serializable],
        slot2_validator: Validator[Any, B, Serializable],
        slot3_validator: Validator[Any, C, Serializable],
        tuple_validator: Optional[
            Callable[[Tuple[A, B, C]], Validated[Tuple[A, B, C], Serializable]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.slot3_validator = slot3_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Validated[Tuple[A, B, C], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Validated[
                Tuple[A, B, C], Tuple[Serializable, ...]
            ] = validate_and_map(
                _typed_tuple,
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
                self.slot3_validator(data[2]),
            )

            if not result.is_valid:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_THREE_ERROR

    async def validate_async(self, data: Any) -> Validated[Tuple[A, B, C], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Validated[
                Tuple[A, B, C], Tuple[Serializable, ...]
            ] = validate_and_map(
                _typed_tuple,
                await self.slot1_validator.validate_async(data[0]),
                await self.slot2_validator.validate_async(data[1]),
                await self.slot3_validator.validate_async(data[2]),
            )

            if not result.is_valid:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_THREE_ERROR


EXPECTED_TUPLE_ERR: Final[Tuple[Literal[False], Serializable]] = False, [
    "expected a tuple"
]


class TupleHomogenousValidator(_ToTupleValidatorUnsafe[Any, Tuple[A, ...], Serializable]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "preprocessors")
    __slots__ = (
        "_item_validator_is_tuple",
        "item_validator",
        "predicates",
        "predicates_async",
        "preprocessors",
    )

    def __init__(
        self,
        item_validator: Validator[Any, A, Serializable],
        *,
        predicates: Optional[List[Predicate[Tuple[A, ...], Serializable]]] = None,
        predicates_async: Optional[
            List[PredicateAsync[Tuple[A, ...], Serializable]]
        ] = None,
        preprocessors: Optional[List[Processor[Tuple[Any, ...]]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

        self._item_validator_is_tuple = isinstance(
            item_validator, _ToTupleValidatorUnsafe
        )

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if isinstance(val, tuple):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            errors: Optional[Dict[str, Serializable]] = None
            if self.predicates:
                tuple_errors: List[Serializable] = [
                    pred.err(val) for pred in self.predicates if not pred.is_valid(val)
                ]

                # Not running async validators! They shouldn't be set!
                if tuple_errors:
                    errors = {OBJECT_ERRORS_FIELD: tuple_errors}

            return_list: List[A] = []

            for i, item in enumerate(val):
                if self._item_validator_is_tuple:
                    is_valid, item_result = self.item_validator.validate_to_tuple(item)  # type: ignore # noqa: E501
                else:
                    _result = self.item_validator(item)
                    is_valid, item_result = (_result.is_valid, _result.val)

                if not is_valid:
                    if errors is None:
                        errors = {str(i): item_result}
                    else:
                        errors[str(i)] = item_result
                elif not errors:
                    return_list.append(item_result)

            if errors:
                return False, errors
            else:
                return True, tuple(return_list)
        else:
            return EXPECTED_TUPLE_ERR


class TupleNValidatorAny(_ToTupleValidatorUnsafe[Any, Tuple[Any, ...], Serializable]):
    """
    Will be type-safe when we have variadic args available generally
    """

    def __init__(self, *validators: Validator[Any, Any, Serializable]) -> None:
        self.validators = validators
        self.tuple_len = len(validators)

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        val_type = type(val)
        if val_type is tuple or val_type is list:
            if len(val) != self.tuple_len:
                return False, f"expected tuple of length {self.tuple_len}"
            else:
                errs = []
                vals = []
                for validator, tuple_val in zip(self.validators, val):
                    if isinstance(validator, _ToTupleValidatorUnsafe):
                        succeeded, new_val = validator.validate_to_tuple(tuple_val)
                        if succeeded:
                            vals.append(new_val)
                        else:
                            errs.append(new_val)
                    else:
                        result = validator(tuple_val)
                        if result.is_valid:
                            vals.append(result.val)
                        else:
                            errs.append(result.val)
                if errs:
                    return False, _variant_errors(errs)
                else:
                    return True, tuple(vals)

        else:
            return False, EXPECTED_TUPLE_ERR
