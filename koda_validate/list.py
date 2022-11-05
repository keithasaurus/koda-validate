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
    __slots__ = (
        "_err",
        "length",
    )

    def __init__(self, length: int) -> None:
        self.length = length
        self._err = f"minimum allowed length is {self.length}"

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) >= self.length

    def err(self, val: List[Any]) -> str:
        return self._err


class MaxItems(Predicate[List[Any], Serializable]):
    __match_args__ = ("length",)
    __slots__ = ("length",)

    def __init__(self, length: int) -> None:
        self.length = length
        self._err = f"maximum allowed length is {self.length}"

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) <= self.length

    def err(self, val: List[Any]) -> str:
        return self._err


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

    def coerce_and_check(self, val: Any) -> Tuple[bool, int | Serializable]:
        if isinstance(val, list):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            errors: Optional[Dict[str, Serializable]] = None
            if self.predicates:
                list_errors: List[Serializable] = [
                    pred.err(val) for pred in self.predicates if not pred.is_valid(val)
                ]

                # Not running async validators! They shouldn't be set!
                if list_errors:
                    errors = {OBJECT_ERRORS_FIELD: list_errors}

            return_list: List[A] = []

            for i, item in enumerate(val):
                is_valid, item_result = self.item_validator.coerce_and_check(item)
                if is_valid:
                    if not errors:
                        return_list.append(item_result)
                else:
                    if errors is None:
                        errors = {str(i): item_result}
                    else:
                        errors[str(i)] = item_result

            if errors:
                return False, errors
            else:
                return True, return_list
        else:
            return False, "expected a list"

    def resp(self, valid: bool, val) -> Result[str, Serializable]:
        if valid:
            return Ok(val)
        else:
            return Err(val)

    def __call__(self, val: Any) -> Result[List[A], Serializable]:
        return self.resp(*self.coerce_and_check(val))

    async def validate_async(self, val: Any) -> Result[List[A], Serializable]:
        if isinstance(val, list):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            return_list: List[A] = []
            list_errors: List[Serializable] = []
            if self.predicates:
                list_errors.extend(
                    [pred.err(val) for pred in self.predicates if not pred.is_valid(val)]
                )

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    result = await pred_async.validate_async(val)
                    if not result.is_ok:
                        list_errors.append(result.val)

            errors: Optional[Dict[str, Serializable]] = None
            if list_errors:
                errors = {OBJECT_ERRORS_FIELD: list_errors}

            for i, item in enumerate(val):
                item_result = await self.item_validator.validate_async(item)
                if item_result.is_ok:
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
