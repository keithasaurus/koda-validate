from typing import Any, Dict, Final, List, Literal, Optional, Set, Tuple, Type

from koda._generics import A

from koda_validate._internals import OBJECT_ERRORS_FIELD, _async_predicates_warning
from koda_validate.base import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
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

EXPECTED_LIST_ERR: Final[Tuple[Literal[False], Serializable]] = False, {
    OBJECT_ERRORS_FIELD: ["expected a list"]
}


class ListValidator(_ToTupleValidatorUnsafe[Any, List[A], Serializable]):
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
        predicates: Optional[List[Predicate[List[A], Serializable]]] = None,
        predicates_async: Optional[List[PredicateAsync[List[A], Serializable]]] = None,
        preprocessors: Optional[List[Processor[List[Any]]]] = None,
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
                if self._item_validator_is_tuple:
                    is_valid, item_result = self.item_validator.validate_to_tuple(item)  # type: ignore # noqa: E501
                else:
                    _result = self.item_validator(item)
                    is_valid, item_result = (_result.is_valid, _result.val)
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
            return EXPECTED_LIST_ERR

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
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
                    if not result.is_valid:
                        list_errors.append(result.val)

            errors: Optional[Dict[str, Serializable]] = None
            if list_errors:
                errors = {OBJECT_ERRORS_FIELD: list_errors}

            for i, item in enumerate(val):
                item_result = await self.item_validator.validate_async(item)
                if item_result.is_valid:
                    if not errors:
                        return_list.append(item_result.val)
                else:
                    if not errors:
                        errors = {str(i): item_result.val}
                    else:
                        errors[str(i)] = item_result.val

            if errors:
                return False, errors
            else:
                return True, return_list
        else:
            return EXPECTED_LIST_ERR
