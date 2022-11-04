from typing import Any, Dict, Final, List, Optional, Set, Tuple, Type

from koda import Err, Ok, Result
from koda._generics import A

from koda_validate._internals import OBJECT_ERRORS_FIELD
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)


class MinItems(Predicate[List[Any], Serializable]):
    __match_args__ = ("length",)
    __slots__ = ("length",)

    def __init__(self, length: int) -> None:
        self.length = length

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) >= self.length

    def err(self, val: List[Any]) -> str:
        return f"minimum allowed length is {self.length}"


class MaxItems(Predicate[List[Any], Serializable]):
    __match_args__ = ("length",)
    __slots__ = ("length",)

    def __init__(self, length: int) -> None:
        self.length = length

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) <= self.length

    def err(self, val: List[Any]) -> str:
        return f"maximum allowed length is {self.length}"


class UniqueItems(Predicate[List[Any], Serializable]):
    def is_valid(self, val: List[Any]) -> bool:
        hashable_items: Set[Tuple[Type[Any], Any]] = set()
        # slower lookups for unhashables
        unhashable_items: List[Tuple[Type[Any], Any]] = []
        for item in val:
            # needed to tell difference between things like
            # ints and bools
            typed_lookup = (type(item), item)
            try:
                if typed_lookup in hashable_items:
                    return False
                else:
                    hashable_items.add(typed_lookup)
            except TypeError:  # not hashable!
                if typed_lookup in unhashable_items:
                    return False
                else:
                    unhashable_items.append(typed_lookup)
        else:
            return True

    def err(self, val: List[Any]) -> str:
        return "all items must be unique"


unique_items = UniqueItems()

EXPECTED_LIST_ERR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected a list"]}
)


class ListValidator(Validator[Any, List[A], Serializable]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "preprocessors")
    __slots__ = ("item_validator", "predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        item_validator: Validator[Any, A, Serializable],
        *,
        predicates: Optional[List[Predicate[List[A], Serializable]]] = None,
        predicates_async: Optional[List[PredicateAsync[List[A], Serializable]]] = None,
        preprocessors: Optional[List[Processor[List[Any]]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Result[List[A], Serializable]:
        if isinstance(val, list):
            if self.preprocessors is not None:
                for processor in self.preprocessors:
                    val = processor(val)

            errors: Optional[Dict[str, Serializable]] = None
            if self.predicates is not None:
                list_errors: List[Serializable] = [
                    result.val
                    for pred in self.predicates
                    if isinstance(result := pred(val), Err)
                ]

                # Not running async validators! They shouldn't be set!
                if len(list_errors) != 0:
                    errors = {OBJECT_ERRORS_FIELD: list_errors}

            return_list: List[A] = []

            for i, item in enumerate(val):
                item_result = self.item_validator(item)
                if item_result.is_ok:
                    if not errors:
                        return_list.append(item_result.val)
                else:
                    if errors is None:
                        errors = {str(i): item_result.val}
                    else:
                        errors[str(i)] = item_result.val

            if errors:
                return Err(errors)
            else:
                return Ok(return_list)
        else:
            return EXPECTED_LIST_ERR

    async def validate_async(self, val: Any) -> Result[List[A], Serializable]:
        if isinstance(val, list):
            if self.preprocessors is not None:
                for processor in self.preprocessors:
                    val = processor(val)
            return_list: List[A] = []
            list_errors: List[Serializable] = []
            if self.predicates is not None:
                for pred in self.predicates:
                    if not (result := pred(val)).is_ok:
                        list_errors.append(result.val)

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    result = await pred_async.validate_async(val)
                    if not result.is_ok:
                        list_errors.append(result.val)

            errors: Optional[Dict[str, Serializable]] = None
            if len(list_errors) > 0:
                errors = {OBJECT_ERRORS_FIELD: list_errors}

            for i, item in enumerate(val):
                item_result = await self.item_validator.validate_async(item)
                if isinstance(item_result, Ok):
                    if not errors:
                        return_list.append(item_result.val)
                else:
                    if not errors:
                        errors = {str(i): item_result.val}
                    else:
                        errors[str(i)] = item_result.val

            if errors:
                return Err(errors)
            else:
                return Ok(return_list)
        else:
            return EXPECTED_LIST_ERR
