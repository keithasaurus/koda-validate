from typing import Any, Callable, Dict, List, Optional, Tuple, Union, overload

from koda_validate._generics import T1, T2, T3, T4, T5, T6, T7, T8, A
from koda_validate._internal import (
    ResultTuple,
    _async_predicates_warning,
    _repr_helper,
    _ToTupleValidator,
)
from koda_validate.base import (
    CoercionErr,
    ErrType,
    IndexErrs,
    Invalid,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    TypeErr,
    Validator,
)
from koda_validate.generic import ExactItemCount


class NTupleValidator(_ToTupleValidator[A]):
    __match_args__ = ("fields",)

    def __init__(
        self,
        *,
        fields: Tuple[Validator[Any], ...],
        validate_object: Optional[Callable[[A], Optional[ErrType]]] = None,
    ) -> None:
        """
        You probably don't want to be using __init__ directly. For type-hinting reasons,
        it's recommended to use either `.typed(...)` or `.untyped(...)`
        """

        self.fields = fields
        self.validate_object = validate_object
        self._len_predicate = ExactItemCount(len(fields))

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[Validator[T1]],
        validate_object: Optional[Callable[[Tuple[T1]], Optional[ErrType]]] = None,
    ) -> "NTupleValidator[Tuple[T1]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[Validator[T1], Validator[T2]],
        validate_object: Optional[Callable[[Tuple[T1, T2]], Optional[ErrType]]] = None,
    ) -> "NTupleValidator[Tuple[T1, T2]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[Validator[T1], Validator[T2], Validator[T3]],
        validate_object: Optional[
            Callable[[Tuple[T1, T2, T3]], Optional[ErrType]]
        ] = None,
    ) -> "NTupleValidator[Tuple[T1, T2, T3]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[Validator[T1], Validator[T2], Validator[T3], Validator[T4]],
        validate_object: Optional[
            Callable[[Tuple[T1, T2, T3, T4]], Optional[ErrType]]
        ] = None,
    ) -> "NTupleValidator[Tuple[T1, T2, T3, T4]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[
            Validator[T1],
            Validator[T2],
            Validator[T3],
            Validator[T4],
            Validator[T5],
        ],
        validate_object: Optional[
            Callable[[Tuple[T1, T2, T3, T4, T5]], Optional[ErrType]]
        ] = None,
    ) -> "NTupleValidator[Tuple[T1, T2, T3, T4, T5]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[
            Validator[T1],
            Validator[T2],
            Validator[T3],
            Validator[T4],
            Validator[T5],
            Validator[T6],
        ],
        validate_object: Optional[
            Callable[[Tuple[T1, T2, T3, T4, T5, T6]], Optional[ErrType]]
        ] = None,
    ) -> "NTupleValidator[Tuple[T1, T2, T3, T4, T5, T6]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[
            Validator[T1],
            Validator[T2],
            Validator[T3],
            Validator[T4],
            Validator[T5],
            Validator[T6],
            Validator[T7],
        ],
        validate_object: Optional[
            Callable[[Tuple[T1, T2, T3, T4, T5, T6, T7]], Optional[ErrType]]
        ] = None,
    ) -> "NTupleValidator[Tuple[T1, T2, T3, T4, T5, T6, T7]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[
            Validator[T1],
            Validator[T2],
            Validator[T3],
            Validator[T4],
            Validator[T5],
            Validator[T6],
            Validator[T7],
            Validator[T8],
        ],
        validate_object: Optional[
            Callable[[Tuple[T1, T2, T3, T4, T5, T6, T7, T8]], Optional[ErrType]]
        ] = None,
    ) -> "NTupleValidator[Tuple[T1, T2, T3, T4, T5, T6, T7, T8]]":
        ...  # pragma: no cover

    @staticmethod
    def typed(
        *,
        fields: Union[
            Tuple[Validator[T1]],
            Tuple[Validator[T1], Validator[T2]],
            Tuple[Validator[T1], Validator[T2], Validator[T3]],
            Tuple[
                Validator[T1],
                Validator[T2],
                Validator[T3],
                Validator[T4],
            ],
            Tuple[
                Validator[T1], Validator[T2], Validator[T3], Validator[T4], Validator[T5]
            ],
            Tuple[
                Validator[T1],
                Validator[T2],
                Validator[T3],
                Validator[T4],
                Validator[T5],
                Validator[T6],
            ],
            Tuple[
                Validator[T1],
                Validator[T2],
                Validator[T3],
                Validator[T4],
                Validator[T5],
                Validator[T6],
                Validator[T7],
            ],
            Tuple[
                Validator[T1],
                Validator[T2],
                Validator[T3],
                Validator[T4],
                Validator[T5],
                Validator[T6],
                Validator[T7],
                Validator[T8],
            ],
        ],
        validate_object: Union[
            Optional[Callable[[Tuple[T1]], Optional[ErrType]]],
            Optional[Callable[[Tuple[T1, T2]], Optional[ErrType]]],
            Optional[Callable[[Tuple[T1, T2, T3]], Optional[ErrType]]],
            Optional[Callable[[Tuple[T1, T2, T3, T4]], Optional[ErrType]]],
            Optional[Callable[[Tuple[T1, T2, T3, T4, T5]], Optional[ErrType]]],
            Optional[Callable[[Tuple[T1, T2, T3, T4, T5, T6]], Optional[ErrType]]],
            Optional[Callable[[Tuple[T1, T2, T3, T4, T5, T6, T7]], Optional[ErrType]]],
            Optional[
                Callable[[Tuple[T1, T2, T3, T4, T5, T6, T7, T8]], Optional[ErrType]]
            ],
        ] = None,
    ) -> Union[
        "NTupleValidator[Tuple[T1]]",
        "NTupleValidator[Tuple[T1, T2]]",
        "NTupleValidator[Tuple[T1, T2, T3]]",
        "NTupleValidator[Tuple[T1, T2, T3, T4]]",
        "NTupleValidator[Tuple[T1, T2, T3, T4, T5]]",
        "NTupleValidator[Tuple[T1, T2, T3, T4, T5, T6]]",
        "NTupleValidator[Tuple[T1, T2, T3, T4, T5, T6, T7]]",
        "NTupleValidator[Tuple[T1, T2, T3, T4, T5, T6, T7, T8]]",
    ]:
        return NTupleValidator(
            fields=fields, validate_object=validate_object
        )  # type: ignore

    @staticmethod
    def untyped(
        *,
        fields: Tuple[Validator[Any], ...],
        validate_object: Optional[Callable[[Tuple[Any, ...]], Optional[ErrType]]] = None,
    ) -> "NTupleValidator[Tuple[Any, ...]]":
        return NTupleValidator(fields=fields, validate_object=validate_object)

    def validate_to_tuple(self, val: Any) -> ResultTuple[A]:
        # we allow list as well because it's common that tuples or tuple-like lists
        # are deserialized to lists
        val_type = type(val)
        if val_type is tuple or val_type is list:
            if not self._len_predicate(val):
                return False, Invalid(PredicateErrs([self._len_predicate]), val, self)
            errs: Dict[int, Invalid] = {}
            vals = []
            for i, (validator, tuple_val) in enumerate(zip(self.fields, val)):
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
                return False, Invalid(IndexErrs(errs), val, self)
            else:
                obj: A = tuple(vals)  # type: ignore
                if self.validate_object is None:
                    return True, obj
                else:
                    obj_result = self.validate_object(obj)
                    if obj_result is None:
                        return True, obj
                    else:
                        return False, Invalid(obj_result, obj, self)
        else:
            return False, Invalid(CoercionErr({list, tuple}, tuple), val, self)

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[A]:
        val_type = type(val)
        if val_type is tuple or val_type is list:
            if not self._len_predicate(val):
                return False, Invalid(PredicateErrs([self._len_predicate]), val, self)
            errs: Dict[int, Invalid] = {}
            vals = []
            for i, (validator, tuple_val) in enumerate(zip(self.fields, val)):
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
                return False, Invalid(IndexErrs(errs), val, self)
            else:
                obj: A = tuple(vals)  # type: ignore
                if self.validate_object is None:
                    return True, obj
                else:
                    obj_result = self.validate_object(obj)
                    if obj_result is None:
                        return True, obj
                    else:
                        return False, Invalid(obj_result, obj, self)

        else:
            return False, Invalid(CoercionErr({list, tuple}, tuple), val, self)

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.fields == other.fields
            and self.validate_object == other.validate_object
        )

    def __repr__(self) -> str:
        fields_str = "(" + ", ".join([repr(f) for f in self.fields]) + ")"
        if self.validate_object is not None:
            fields_str += f", validate_object={repr(self.validate_object)}"

        return f"{self.__class__.__name__}(fields={fields_str})"


class TupleHomogenousValidator(_ToTupleValidator[Tuple[A, ...]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async")

    def __init__(
        self,
        item_validator: Validator[A],
        *,
        predicates: Optional[List[Predicate[Tuple[A, ...]]]] = None,
        predicates_async: Optional[List[PredicateAsync[Tuple[A, ...]]]] = None,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async

        self._item_validator_is_tuple = isinstance(item_validator, _ToTupleValidator)

    def validate_to_tuple(self, val: Any) -> ResultTuple[Tuple[A, ...]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if isinstance(val, tuple):
            if self.predicates:
                tuple_errors: List[
                    Union[Predicate[Tuple[A, ...]], PredicateAsync[Tuple[A, ...]]]
                ] = [pred for pred in self.predicates if not pred(val)]

                # Not running async validators! They shouldn't be set!
                if tuple_errors:
                    return False, Invalid(PredicateErrs(tuple_errors), val, self)

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
                return False, Invalid(IndexErrs(index_errors), val, self)
            else:
                return True, tuple(return_list)
        else:
            return False, Invalid(TypeErr(tuple), val, self)

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Tuple[A, ...]]:
        if isinstance(val, tuple):
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
                return False, Invalid(PredicateErrs(tuple_errors), val, self)

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
                return False, Invalid(IndexErrs(index_errors), val, self)
            else:
                return True, tuple(return_list)
        else:
            return False, Invalid(TypeErr(tuple), val, self)

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
