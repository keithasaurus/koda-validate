from typing import Any, Dict, List, Optional, Union

from koda._generics import A

from koda_validate.base import (
    InvalidIterable,
    InvalidType,
    Predicate,
    PredicateAsync,
    Processor,
    ValidationErr,
    Validator,
    _async_predicates_warning,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)


class ListValidator(_ToTupleValidatorUnsafe[Any, List[A]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        item_validator: Validator[Any, A],
        *,
        predicates: Optional[List[Predicate[List[A]]]] = None,
        predicates_async: Optional[List[PredicateAsync[List[A]]]] = None,
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

            if self.predicates:
                list_errors: List[Predicate[List[Any]]] = [
                    pred for pred in self.predicates if not pred.__call__(val)
                ]

                if list_errors:
                    return False, list_errors

            return_list: List[A] = []
            index_errs: Dict[int, ValidationErr] = {}
            for i, item in enumerate(val):
                if self._item_validator_is_tuple:
                    is_valid, item_result = self.item_validator.validate_to_tuple(item)  # type: ignore # noqa: E501
                else:
                    _result = self.item_validator(item)
                    is_valid, item_result = (_result.is_valid, _result.val)

                if not is_valid:
                    index_errs[i] = item_result
                elif not index_errs:
                    return_list.append(item_result)

            if index_errs:
                return False, InvalidIterable(self, index_errs)
            else:
                return True, return_list
        else:
            return False, InvalidType(self, list)

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        if isinstance(val, list):
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

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
                return False, predicate_errors

            return_list: List[A] = []
            index_errs = {}
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
                    is_valid, item_result = (_result.is_valid, _result.val)

                if not is_valid:
                    index_errs[i] = item_result
                elif not index_errs:
                    return_list.append(item_result)

            if index_errs:
                return False, InvalidIterable(self, index_errs)
            else:
                return True, return_list
        else:
            return False, InvalidType(self, list)
