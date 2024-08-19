from typing import Any, Callable, Dict, List, Optional, Tuple, Union, overload

from koda import Just, Maybe, nothing

from koda_validate._generics import T1, T2, T3, T4, T5, T6, T7, T8, A
from koda_validate._internal import (
    _async_predicates_warning,
    _repr_helper,
    _ResultTuple,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import Predicate, PredicateAsync, Validator
from koda_validate.coerce import Coercer, coercer
from koda_validate.errors import CoercionErr, ErrType, IndexErrs, PredicateErrs, TypeErr
from koda_validate.generic import ExactItemCount
from koda_validate.valid import Invalid


@coercer(list, tuple)
def tuple_or_list_to_tuple(val: Any) -> Maybe[Tuple[Any, ...]]:
    if (val_type := type(val)) is tuple:
        return Just(val)
    elif val_type is list:
        return Just(tuple(val))
    else:
        return nothing


class NTupleValidator(_ToTupleValidator[A]):
    __match_args__ = ("fields", "coerce")

    def __init__(
        self,
        *,
        fields: Tuple[Validator[Any], ...],
        validate_object: Optional[Callable[[A], Optional[ErrType]]] = None,
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
    ) -> None:
        """
        You probably don't want to be using __init__ directly. For type-hinting reasons,
        it's recommended to use either `.typed(...)` or `.untyped(...)`

        :param fields: the validators that correspond with the respective indexes in the
            tuple
        :param validate_object: if all the slots of the tuple are valid, this can be used
            to validate among all the fields.
        :param coerce: control if an how values are coerced for this validator
        """

        self.fields = fields
        self.validate_object = validate_object
        self.coerce = coerce
        self._len_predicate: Predicate[Tuple[Any, ...]] = ExactItemCount(len(fields))
        self._wrapped_fields_sync = [_wrap_sync_validator(v) for v in fields]
        self._wrapped_fields_async = [_wrap_async_validator(v) for v in fields]

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[Validator[T1]],
        validate_object: Optional[Callable[[Tuple[T1]], Optional[ErrType]]] = None,
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
    ) -> "NTupleValidator[Tuple[T1]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        *,
        fields: Tuple[Validator[T1], Validator[T2]],
        validate_object: Optional[Callable[[Tuple[T1, T2]], Optional[ErrType]]] = None,
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
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
        """
        Can be used for up to 8 typed tuple slots. For more than 8 slots,
        use ``NTupleValidator.untyped``.

        :param fields: a tuple the validators to be used, whose types will reflect
            the resulting tuple
        :param validate_object: a function which can be used to validate the tuple after
            individual slots have been validated
        :param coerce: control coercion prior to validation
        :return: ``NTupleValidator`` with the ``fields`` as defined by the ``fields``
            parameter
        """
        return NTupleValidator(
            fields=fields, validate_object=validate_object, coerce=coerce
        )  # type: ignore

    @staticmethod
    def untyped(
        *,
        fields: Tuple[Validator[Any], ...],
        validate_object: Optional[Callable[[Tuple[Any, ...]], Optional[ErrType]]] = None,
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
    ) -> "NTupleValidator[Tuple[Any, ...]]":
        """
        Identical to NTupleValidator.typed except that it can be used for an
        arbitrary number of slots. Does not retain type information.

        :param fields: a tuple the validators to be used, whose types will reflect
            the resulting tuple
        :param validate_object: a function which can be used to validate the tuple after
            individual slots have been validated
        :param coerce: control coercion prior to validation
        :return: ``NTupleValidator`` with the ``fields`` as defined by the ``fields``
            parameter
        """
        return NTupleValidator(
            fields=fields, validate_object=validate_object, coerce=coerce
        )

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[A]:
        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, list), val, self
                )
            else:
                coerced_val: Tuple[Any, ...] = coerced.val
        elif type(val) is tuple:
            coerced_val = val
        else:
            return False, Invalid(TypeErr(tuple), val, self)

        # we allow list as well because it's common that tuples or tuple-like lists
        # are deserialized to lists
        if not self._len_predicate(coerced_val):
            return False, Invalid(PredicateErrs([self._len_predicate]), coerced_val, self)
        errs: Dict[int, Invalid] = {}
        vals = []
        for i, (validator, tuple_val) in enumerate(
            zip(self._wrapped_fields_sync, coerced_val)
        ):
            succeeded, new_val = validator(tuple_val)
            if succeeded:
                vals.append(new_val)
            else:
                errs[i] = new_val

        if errs:
            return False, Invalid(IndexErrs(errs), coerced_val, self)
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

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[A]:
        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, list), val, self
                )
            else:
                coerced_val: Tuple[Any, ...] = coerced.val
        elif type(val) is tuple:
            coerced_val = val
        else:
            return False, Invalid(TypeErr(tuple), val, self)

        if not self._len_predicate(val):
            return False, Invalid(PredicateErrs([self._len_predicate]), val, self)

        errs: Dict[int, Invalid] = {}
        vals = []
        for i, (validator, tuple_val) in enumerate(
            zip(self._wrapped_fields_async, coerced_val)
        ):
            succeeded, new_val = await validator(tuple_val)
            if succeeded:
                vals.append(new_val)
            else:
                errs[i] = new_val

        if errs:
            return False, Invalid(IndexErrs(errs), coerced_val, self)
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

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.fields == other.fields
            and self.validate_object == other.validate_object
            and self.coerce == other.coerce
        )

    def __repr__(self) -> str:
        fields_str = "(" + ", ".join([repr(f) for f in self.fields]) + ")"
        if self.validate_object is not None:
            fields_str += f", validate_object={repr(self.validate_object)}"

        if self.coerce is not None:
            fields_str += f", coerce={repr(self.coerce)}"

        return f"{self.__class__.__name__}(fields={fields_str})"


class UniformTupleValidator(_ToTupleValidator[Tuple[A, ...]]):
    __match_args__ = ("item_validator", "predicates", "predicates_async", "coerce")

    def __init__(
        self,
        item_validator: Validator[A],
        *,
        predicates: Optional[List[Predicate[Tuple[A, ...]]]] = None,
        predicates_async: Optional[List[PredicateAsync[Tuple[A, ...]]]] = None,
        coerce: Optional[Coercer[Tuple[Any, ...]]] = tuple_or_list_to_tuple,
    ) -> None:
        self.item_validator = item_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.coerce = coerce

        self._item_validator_is_tuple = isinstance(item_validator, _ToTupleValidator)

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[Tuple[A, ...]]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, list), val, self
                )
            else:
                coerced_val: Tuple[Any, ...] = coerced.val

        elif type(val) is tuple:
            coerced_val = val
        else:
            return False, Invalid(TypeErr(tuple), val, self)

        if self.predicates:
            tuple_errors: List[
                Union[Predicate[Tuple[A, ...]], PredicateAsync[Tuple[A, ...]]]
            ] = [pred for pred in self.predicates if not pred(coerced_val)]

            # Not running async validators! They shouldn't be set!
            if tuple_errors:
                return False, Invalid(PredicateErrs(tuple_errors), coerced_val, self)

        return_list: List[A] = []
        index_errors: Dict[int, Invalid] = {}
        for i, item in enumerate(coerced_val):
            if self._item_validator_is_tuple:
                is_valid, item_result = self.item_validator._validate_to_tuple(item)  # type: ignore # noqa: E501
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
            return False, Invalid(IndexErrs(index_errors), coerced_val, self)
        else:
            return True, tuple(return_list)

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[Tuple[A, ...]]:
        if self.coerce:
            if not (coerced := self.coerce(val)).is_just:
                return False, Invalid(
                    CoercionErr(self.coerce.compatible_types, list), val, self
                )
            else:
                coerced_val: Tuple[Any, ...] = coerced.val

        elif type(val) is tuple:
            coerced_val = val
        else:
            return False, Invalid(TypeErr(tuple), val, self)

        tuple_errors: List[
            Union[Predicate[Tuple[A, ...]], PredicateAsync[Tuple[A, ...]]]
        ] = []
        if self.predicates:
            tuple_errors.extend(
                [pred for pred in self.predicates if not pred(coerced_val)]
            )
        if self.predicates_async:
            for pred_async in self.predicates_async:
                if not await pred_async.validate_async(coerced_val):
                    tuple_errors.append(pred_async)

        # Not running async validators! They shouldn't be set!
        if tuple_errors:
            return False, Invalid(PredicateErrs(tuple_errors), coerced_val, self)

        return_list: List[A] = []
        index_errors: Dict[int, Invalid] = {}
        for i, item in enumerate(coerced_val):
            if self._item_validator_is_tuple:
                (
                    is_valid,
                    item_result,
                ) = await self.item_validator._validate_to_tuple_async(  # type: ignore # noqa: E501
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
            return False, Invalid(IndexErrs(index_errors), coerced_val, self)
        else:
            return True, tuple(return_list)

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
