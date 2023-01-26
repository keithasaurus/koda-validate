from typing import Any, Hashable, List, Optional, Set, TypeVar, Union

from koda_validate import Coercer
from koda_validate._internal import (
    _async_predicates_warning,
    _repr_helper,
    _ResultTuple,
    _ToTupleValidator,
)
from koda_validate.base import Predicate, PredicateAsync, Validator
from koda_validate.errors import CoercionErr, PredicateErrs, SetErrs, TypeErr
from koda_validate.valid import Invalid

_ItemT = TypeVar("_ItemT", bound=Hashable)


class SetValidator(_ToTupleValidator[Set[_ItemT]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "coerce")

    def __init__(
        self,
        item_validator: Validator[_ItemT],
        *,
        predicates: Optional[List[Predicate[Set[_ItemT]]]] = None,
        predicates_async: Optional[List[PredicateAsync[Set[_ItemT]]]] = None,
        coerce: Optional[Coercer[Set[Any]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.coerce = coerce

        self._item_validator_is_tuple = isinstance(item_validator, _ToTupleValidator)

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[Set[_ItemT]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, set), val, self
                )
            else:
                coerced_val: Set[Any] = coerced.val

        elif type(val) is set:
            coerced_val = val
        else:
            return False, Invalid(TypeErr(set), val, self)

        if self.predicates:
            list_errors: List[
                Union[Predicate[Set[_ItemT]], PredicateAsync[Set[_ItemT]]]
            ] = [pred for pred in self.predicates if not pred(coerced_val)]

            if list_errors:
                return False, Invalid(PredicateErrs(list_errors), coerced_val, self)

        return_set: Set[_ItemT] = set()
        item_errs: List[Invalid] = []
        for i, item in enumerate(coerced_val):
            if self._item_validator_is_tuple:
                is_valid, item_result = self.item_validator._validate_to_tuple(item)  # type: ignore # noqa: E501
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
            return False, Invalid(SetErrs(item_errs), coerced_val, self)
        else:
            return True, return_set

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[Set[_ItemT]]:
        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, set), val, self
                )
            else:
                coerced_val: Set[Any] = coerced.val

        elif type(val) is set:
            coerced_val = val
        else:
            return False, Invalid(TypeErr(set), val, self)

        predicate_errors: List[
            Union[Predicate[Set[_ItemT]], PredicateAsync[Set[_ItemT]]]
        ] = []
        if self.predicates:
            predicate_errors.extend(
                [pred for pred in self.predicates if not pred(coerced_val)]
            )

        if self.predicates_async is not None:
            for pred_async in self.predicates_async:
                if not await pred_async.validate_async(coerced_val):
                    predicate_errors.append(pred_async)

        if predicate_errors:
            return False, Invalid(PredicateErrs(predicate_errors), coerced_val, self)

        return_set: Set[_ItemT] = set()
        item_errs: List[Invalid] = []
        for i, item in enumerate(coerced_val):
            if self._item_validator_is_tuple:
                (
                    is_valid,
                    item_result,
                ) = await self.item_validator._validate_to_tuple_async(  # type: ignore  # noqa: E501
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
            return False, Invalid(SetErrs(item_errs), coerced_val, self)
        else:
            return True, return_set

    def __eq__(self, other: Any) -> bool:
        return (
            type(other) is type(self)
            and self.item_validator == other.item_validator
            and self.predicates == other.predicates
            and self.predicates_async == other.predicates_async
            and self.coerce == other.coerce
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
                    ("coerce", self.coerce),
                ]
                if v
            ],
        )
