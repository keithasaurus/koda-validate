from typing import Any, Dict, List, Optional, Union

from koda._generics import A

from koda_validate._internal import (
    ResultTuple,
    _async_predicates_warning,
    _repr_helper,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import Predicate, PredicateAsync, Validator
from koda_validate.errors import IndexErrs, PredicateErrs, TypeErr
from koda_validate.valid import Invalid


class ListValidator(_ToTupleValidator[List[A]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async")

    def __init__(
        self,
        item_validator: Validator[A],
        *,
        predicates: Optional[List[Predicate[List[A]]]] = None,
        predicates_async: Optional[List[PredicateAsync[List[A]]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self._disallow_synchronous = bool(predicates_async)

        self._wrapped_item_validator_sync = _wrap_sync_validator(item_validator)
        self._wrapped_item_validator_async = _wrap_async_validator(item_validator)

    def validate_to_tuple(self, val: Any) -> ResultTuple[List[A]]:
        if self._disallow_synchronous:
            _async_predicates_warning(self.__class__)
        if type(val) is list:
            if self.predicates:
                list_errors: List[Union[Predicate[List[A]], PredicateAsync[List[A]]]] = [
                    pred for pred in self.predicates if not pred.__call__(val)
                ]

                if list_errors:
                    return False, Invalid(PredicateErrs(list_errors), val, self)

            return_list: List[A] = []
            index_errs: Dict[int, Invalid] = {}
            for i, item in enumerate(val):
                is_valid, item_result = self._wrapped_item_validator_sync(item)

                if not is_valid:
                    index_errs[i] = item_result  # type: ignore
                elif not index_errs:
                    return_list.append(item_result)  # type: ignore

            if index_errs:
                return False, Invalid(IndexErrs(index_errs), val, self)
            else:
                return True, return_list
        else:
            return False, Invalid(TypeErr(list), val, self)

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[List[A]]:
        if type(val) is list:
            predicate_errors: List[
                Union[Predicate[List[Any]], PredicateAsync[List[Any]]]
            ] = []
            if self.predicates:
                predicate_errors.extend(
                    [pred for pred in self.predicates if not pred(val)]
                )

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    if not await pred_async.validate_async(val):
                        predicate_errors.append(pred_async)

            if predicate_errors:
                return False, Invalid(PredicateErrs(predicate_errors), val, self)

            return_list: List[A] = []
            index_errs = {}
            for i, item in enumerate(val):
                (
                    is_valid,
                    item_result,
                ) = await self._wrapped_item_validator_async(item)

                if not is_valid:
                    index_errs[i] = item_result
                elif not index_errs:
                    return_list.append(item_result)  # type: ignore

            if index_errs:
                return False, Invalid(IndexErrs(index_errs), val, self)  # type: ignore  # noqa: E501
            else:
                return True, return_list
        else:
            return False, Invalid(TypeErr(list), val, self)

    def __eq__(self, other: Any) -> bool:
        return (
            type(other) is type(self)
            and self.item_validator == other.item_validator
            and self.predicates == other.predicates
            and self.predicates_async == other.predicates_async
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(self.item_validator)]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("predicates", self.predicates),
                    ("predicates_async", self.predicates_async),
                ]
                if v
            ],
        )
