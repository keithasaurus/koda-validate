from typing import Any, Dict, List, Optional, Union

from koda._generics import A

from koda_validate._internal import (
    ResultTuple,
    _async_predicates_warning,
    _ToTupleValidator,
)
from koda_validate.base import (
    IndexErrs,
    Invalid,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    Processor,
    TypeErr,
    Validator,
)


class ListValidator(_ToTupleValidator[List[A]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        item_validator: Validator[A],
        *,
        predicates: Optional[List[Predicate[List[A]]]] = None,
        predicates_async: Optional[List[PredicateAsync[List[A]]]] = None,
        preprocessors: Optional[List[Processor[List[A]]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

        self._item_validator_is_tuple = isinstance(item_validator, _ToTupleValidator)

    def validate_to_tuple(self, val: Any) -> ResultTuple[List[A]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if type(val) is list:
            if self.preprocessors:
                for processor in self.preprocessors:
                    val = processor(val)

            if self.predicates:
                list_errors: List[Union[Predicate[List[A]], PredicateAsync[List[A]]]] = [
                    pred for pred in self.predicates if not pred.__call__(val)
                ]

                if list_errors:
                    return False, Invalid(self, val, PredicateErrs(list_errors))

            return_list: List[A] = []
            index_errs: Dict[int, Invalid] = {}
            for i, item in enumerate(val):
                if self._item_validator_is_tuple:
                    is_valid, item_result = self.item_validator.validate_to_tuple(item)  # type: ignore # noqa: E501
                else:
                    _result = self.item_validator(item)
                    is_valid, item_result = (
                        (True, _result.val) if _result.is_valid else (False, _result)
                    )

                if not is_valid:
                    index_errs[i] = item_result
                elif not index_errs:
                    return_list.append(item_result)

            if index_errs:
                return False, Invalid(self, val, IndexErrs(index_errs))
            else:
                return True, return_list
        else:
            return False, Invalid(self, val, TypeErr(list))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[List[A]]:
        if type(val) is list:
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
                return False, Invalid(self, val, PredicateErrs(predicate_errors))

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
                    is_valid, item_result = (
                        (True, _result.val) if _result.is_valid else (False, _result)
                    )

                if not is_valid:
                    index_errs[i] = item_result
                elif not index_errs:
                    return_list.append(item_result)

            if index_errs:
                return False, Invalid(self, val, IndexErrs(index_errs))
            else:
                return True, return_list
        else:
            return False, Invalid(self, val, TypeErr(list))

    def __repr__(self) -> str:
        attrs_str = ", ".join(
            [
                f"{k}={repr(v)}"
                for k, v in [
                    ("predicates", self.predicates),
                    ("predicates_async", self.predicates_async),
                    ("preprocessors", self.preprocessors),
                ]
                if v
            ]
        )
        if attrs_str:
            attrs_str = ", " + attrs_str
        return f"ListValidator({repr(self.item_validator)}{attrs_str})"
