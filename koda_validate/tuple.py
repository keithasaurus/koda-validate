"""
We should replace Tuple2Validator and Tuple3Validator
with a generic TupleValidator... (2 and 3 can still use the new one
under the hood, if needed)
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from koda_validate import ExactItemCount
from koda_validate._generics import A, B, C
from koda_validate._internal import (
    ResultTuple,
    _async_predicates_warning,
    _ToTupleValidator,
)
from koda_validate.base import (
    CoercionErr,
    ErrType,
    Invalid,
    IterableErr,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    Processor,
    TypeErr,
    Validator,
)


class TupleNValidatorAny(_ToTupleValidator[Tuple[Any, ...]]):
    """
    Will be type-safe when we have variadic args available generally
    """

    def __init__(self, *validators: Validator[Any]) -> None:
        self.validators = validators
        self._len_predicate = ExactItemCount(len(validators))

    def validate_to_tuple(self, val: Any) -> ResultTuple[Tuple[Any, ...]]:
        val_type = type(val)
        if val_type is tuple or val_type is list:
            if not self._len_predicate(val):
                return False, Invalid(self, PredicateErrs([self._len_predicate]))
            errs: Dict[int, Invalid] = {}
            vals = []
            for i, (validator, tuple_val) in enumerate(zip(self.validators, val)):
                if isinstance(validator, _ToTupleValidator):
                    succeeded, new_val = validator.validate_to_tuple(tuple_val)
                    if succeeded:
                        vals.append(new_val)
                    else:
                        errs[i] = new_val
                else:
                    result = validator(tuple_val)
                    if result.is_valid:
                        vals.append(result.val)
                    else:
                        errs[i] = result
            if errs:
                return False, Invalid(self, IterableErr(errs))
            else:
                return True, tuple(vals)

        else:
            return False, Invalid(self, CoercionErr({list, tuple}, tuple))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Tuple[Any, ...]]:
        val_type = type(val)
        if val_type is tuple or val_type is list:
            if not self._len_predicate(val):
                return False, Invalid(self, PredicateErrs([self._len_predicate]))
            errs: Dict[int, Invalid] = {}
            vals = []
            for i, (validator, tuple_val) in enumerate(zip(self.validators, val)):
                if isinstance(validator, _ToTupleValidator):
                    succeeded, new_val = await validator.validate_to_tuple_async(
                        tuple_val
                    )
                    if succeeded:
                        vals.append(new_val)
                    else:
                        errs[i] = new_val
                else:
                    result = await validator.validate_async(tuple_val)
                    if result.is_valid:
                        vals.append(result.val)
                    else:
                        errs[i] = result
            if errs:
                return False, Invalid(self, IterableErr(errs))
            else:
                return True, tuple(vals)

        else:
            return False, Invalid(self, CoercionErr({list, tuple}, tuple))


# todo: auto-generate
class Tuple2Validator(_ToTupleValidator[Tuple[A, B]]):
    __match_args__ = ("slot1_validator", "slot2_validator", "tuple_validator")
    required_length: int = 2

    def __init__(
        self,
        slot1_validator: Validator[A],
        slot2_validator: Validator[B],
        tuple_validator: Optional[Callable[[Tuple[A, B]], Optional[ErrType]]] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.tuple_validator = tuple_validator

        self._validator = TupleNValidatorAny(slot1_validator, slot2_validator)

    async def validate_to_tuple_async(self, data: Any) -> ResultTuple[Tuple[A, B]]:
        result = await self._validator.validate_to_tuple_async(data)
        if result[0]:
            new_val = cast(Tuple[A, B], result[1])
            if self.tuple_validator is None:
                return True, new_val
            else:
                tup_result = self.tuple_validator(new_val)
                if tup_result is None:
                    return True, new_val
                else:
                    return False, Invalid(self, tup_result)
        else:
            err_val = result[1]
            if isinstance(err_val, Invalid):
                err_val.validator = self
            return False, err_val

    def validate_to_tuple(self, data: Any) -> ResultTuple[Tuple[A, B]]:
        result = self._validator.validate_to_tuple(data)
        if result[0]:
            new_val = cast(Tuple[A, B], result[1])
            if self.tuple_validator is None:
                return True, new_val
            else:
                tup_result = self.tuple_validator(new_val)
                if tup_result is None:
                    return True, new_val
                else:
                    return False, Invalid(self, tup_result)
        else:
            err_val = result[1]
            if isinstance(err_val, Invalid):
                err_val.validator = self
            return False, err_val


class Tuple3Validator(_ToTupleValidator[Tuple[A, B, C]]):
    __match_args__ = (
        "slot1_validator",
        "slot2_validator",
        "slot3_validator",
        "tuple_validator",
    )
    required_length: int = 3

    def __init__(
        self,
        slot1_validator: Validator[A],
        slot2_validator: Validator[B],
        slot3_validator: Validator[C],
        tuple_validator: Optional[Callable[[Tuple[A, B, C]], Optional[ErrType]]] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.slot3_validator = slot3_validator
        self.tuple_validator = tuple_validator
        self._validator = TupleNValidatorAny(
            slot1_validator, slot2_validator, slot3_validator
        )

    async def validate_to_tuple_async(self, data: Any) -> ResultTuple[Tuple[A, B, C]]:
        result = await self._validator.validate_to_tuple_async(data)
        if result[0]:
            new_val = cast(Tuple[A, B, C], result[1])
            if self.tuple_validator is None:
                return True, new_val
            else:
                tup_result = self.tuple_validator(new_val)
                if tup_result is None:
                    return True, new_val
                else:
                    return False, Invalid(self, tup_result)
        else:
            err_val = result[1]
            if isinstance(err_val, Invalid):
                err_val.validator = self
            return False, err_val

    def validate_to_tuple(self, data: Any) -> ResultTuple[Tuple[A, B, C]]:
        result = self._validator.validate_to_tuple(data)
        if result[0]:
            new_val = cast(Tuple[A, B, C], result[1])
            if self.tuple_validator is None:
                return True, new_val
            else:
                tup_result = self.tuple_validator(new_val)
                if tup_result is None:
                    return True, new_val
                else:
                    return False, Invalid(self, tup_result)
        else:
            err_val = result[1]
            if isinstance(err_val, Invalid):
                err_val.validator = self
            return False, err_val


class TupleHomogenousValidator(_ToTupleValidator[Tuple[A, ...]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        item_validator: Validator[A],
        *,
        predicates: Optional[List[Predicate[Tuple[A, ...]]]] = None,
        predicates_async: Optional[List[PredicateAsync[Tuple[A, ...]]]] = None,
        preprocessors: Optional[List[Processor[Tuple[Any, ...]]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

        self._item_validator_is_tuple = isinstance(item_validator, _ToTupleValidator)

    def validate_to_tuple(self, val: Any) -> ResultTuple[Tuple[A, ...]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if isinstance(val, tuple):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            if self.predicates:
                tuple_errors: List[
                    Union[Predicate[Tuple[A, ...]], PredicateAsync[Tuple[A, ...]]]
                ] = [pred for pred in self.predicates if not pred(val)]

                # Not running async validators! They shouldn't be set!
                if tuple_errors:
                    return False, Invalid(self, PredicateErrs(tuple_errors))

            return_list: List[A] = []
            index_errors: Dict[int, Invalid] = {}
            for i, item in enumerate(val):
                if self._item_validator_is_tuple:
                    is_valid, item_result = self.item_validator.validate_to_tuple(item)  # type: ignore # noqa: E501
                else:
                    _result = self.item_validator(item)
                    is_valid, item_result = (
                        (True, _result.val) if _result.is_valid else (False, _result)
                    )

                if not is_valid:
                    index_errors[i] = item_result
                elif not index_errors:
                    return_list.append(item_result)

            if index_errors:
                return False, Invalid(self, IterableErr(index_errors))
            else:
                return True, tuple(return_list)
        else:
            return False, Invalid(self, TypeErr(tuple))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Tuple[A, ...]]:
        if isinstance(val, tuple):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            tuple_errors: List[
                Union[Predicate[Tuple[A, ...]], PredicateAsync[Tuple[A, ...]]]
            ] = []
            if self.predicates:
                tuple_errors.extend([pred for pred in self.predicates if not pred(val)])
            if self.predicates_async:
                for pred_async in self.predicates_async:
                    if not await pred_async.validate_async(val):
                        tuple_errors.append(pred_async)

            # Not running async validators! They shouldn't be set!
            if tuple_errors:
                return False, Invalid(self, PredicateErrs(tuple_errors))

            return_list: List[A] = []
            index_errors: Dict[int, Invalid] = {}
            for i, item in enumerate(val):
                if self._item_validator_is_tuple:
                    (
                        is_valid,
                        item_result,
                    ) = await self.item_validator.validate_to_tuple_async(  # type: ignore # noqa: E501
                        item
                    )
                else:
                    _result = await self.item_validator.validate_async(item)
                    is_valid, item_result = (
                        (True, _result.val) if _result.is_valid else (False, _result)
                    )

                if not is_valid:
                    index_errors[i] = item_result
                elif not index_errors:
                    return_list.append(item_result)

            if index_errors:
                return False, Invalid(self, IterableErr(index_errors))
            else:
                return True, tuple(return_list)
        else:
            return False, Invalid(self, TypeErr(tuple))
