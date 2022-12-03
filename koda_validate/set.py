from typing import Any, List, Optional, Set, Union

from koda_validate import Invalid, Predicate, PredicateAsync, Processor, Validator
from koda_validate._generics import A
from koda_validate._internal import (
    ResultTuple,
    _async_predicates_warning,
    _ToTupleValidator,
)
from koda_validate.base import PredicateErrs, SetErrs, TypeErr


class SetValidator(_ToTupleValidator[Set[A]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        item_validator: Validator[A],
        *,
        predicates: Optional[List[Predicate[Set[A]]]] = None,
        predicates_async: Optional[List[PredicateAsync[Set[A]]]] = None,
        preprocessors: Optional[List[Processor[Set[A]]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

        self._item_validator_is_tuple = isinstance(item_validator, _ToTupleValidator)

    def validate_to_tuple(self, val: Any) -> ResultTuple[Set[A]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if isinstance(val, set):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            if self.predicates:
                list_errors: List[Union[Predicate[Set[A]], PredicateAsync[Set[A]]]] = [
                    pred for pred in self.predicates if not pred.__call__(val)
                ]

                if list_errors:
                    return False, Invalid(self, val, PredicateErrs(list_errors))

            return_set: Set[A] = set()
            item_errs: List[Invalid] = []
            for i, item in enumerate(val):
                if self._item_validator_is_tuple:
                    is_valid, item_result = self.item_validator.validate_to_tuple(item)  # type: ignore # noqa: E501
                else:
                    _result = self.item_validator(item)
                    is_valid, item_result = (
                        (True, _result.val) if _result.is_valid else (False, _result)
                    )

                if not is_valid:
                    item_errs.append(item_result)
                elif not item_errs:
                    return_set.add(item_result)

            if item_errs:
                return False, Invalid(self, val, SetErrs(item_errs))
            else:
                return True, return_set
        else:
            return False, Invalid(self, val, TypeErr(set))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Set[A]]:
        if isinstance(val, set):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            predicate_errors: List[Union[Predicate[Set[A]], PredicateAsync[Set[A]]]] = []
            if self.predicates:
                predicate_errors.extend(
                    [pred for pred in self.predicates if not pred(val)]
                )

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    if not await pred_async.validate_async(val):
                        predicate_errors.append(pred_async)

            if predicate_errors:
                return False, Invalid(self, val, PredicateErrs(predicate_errors))

            return_set: Set[A] = set()
            item_errs: List[Invalid] = []
            for i, item in enumerate(val):
                if self._item_validator_is_tuple:
                    (
                        is_valid,
                        item_result,
                    ) = await self.item_validator.validate_to_tuple_async(  # type: ignore  # noqa: E501
                        item
                    )
                else:
                    _result = await self.item_validator.validate_async(item)
                    is_valid, item_result = (
                        (True, _result.val) if _result.is_valid else (False, _result)
                    )

                if not is_valid:
                    item_errs.append(item_result)
                elif not item_errs:
                    return_set.add(item_result)

            if item_errs:
                return False, Invalid(self, val, SetErrs(item_errs))
            else:
                return True, return_set
        else:
            return False, Invalid(self, val, TypeErr(set))
