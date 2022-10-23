from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple, Type

from koda import Err, Ok, Result
from koda._generics import A

from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import expected


@dataclass(frozen=True)
class MinItems(Predicate[List[Any], JSONValue]):
    length: int

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) >= self.length

    def err_message(self, val: List[Any]) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MaxItems(Predicate[List[Any], JSONValue]):
    length: int

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) <= self.length

    def err_message(self, val: List[Any]) -> str:
        return f"maximum allowed length is {self.length}"


class UniqueItems(Predicate[List[Any], JSONValue]):
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

    def err_message(self, val: List[Any]) -> str:
        return "all items must be unique"


@dataclass(frozen=True, init=False)
class ListValidator(Validator[Any, List[A], JSONValue]):
    item_validator: Validator[Any, A, JSONValue]
    list_validators: Tuple[Predicate[List[A], JSONValue], ...]

    def __init__(
        self,
        item_validator: Validator[Any, A, JSONValue],
        *list_validators: Predicate[List[A], JSONValue],
    ) -> None:
        object.__setattr__(self, "item_validator", item_validator)
        object.__setattr__(self, "list_validators", list_validators)

    def __call__(self, val: Any) -> Result[List[A], JSONValue]:
        if isinstance(val, list):
            return_list: List[A] = []
            errors: Dict[str, JSONValue] = {}

            list_errors: List[JSONValue] = []
            for validator in self.list_validators:
                result = validator(val)

                if isinstance(result, Err):
                    list_errors.append(result.val)

            if len(list_errors) > 0:
                errors["__container__"] = list_errors

            for i, item in enumerate(val):
                item_result = self.item_validator(item)
                if isinstance(item_result, Ok):
                    return_list.append(item_result.val)
                else:
                    errors[str(i)] = item_result.val

            if len(errors) > 0:
                return Err(errors)
            else:
                return Ok(return_list)
        else:
            return Err({"__container__": [expected("a list")]})


unique_items = UniqueItems()