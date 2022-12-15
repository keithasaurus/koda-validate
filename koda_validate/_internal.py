from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    List,
    Literal,
    NoReturn,
    Optional,
    Tuple,
    Type,
    Union,
)

from koda_validate._generics import A, SuccessT
from koda_validate.base import (
    Invalid,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    Processor,
    TypeErr,
    UnionErrs,
    Valid,
    ValidationResult,
    Validator,
)

ResultTuple = Union[Tuple[Literal[True], A], Tuple[Literal[False], Invalid]]


class _ToTupleValidator(Validator[SuccessT]):
    """
    This `Validator` subclass exists for optimization. When we call
    nested validators it's much less computation to deal with simple
    tuples and bools, instead of Valid and Invalid instances.
    This class may go away!

    DO NOT USE THIS UNLESS YOU:
    - ARE OK WITH THIS DISAPPEARING IN A FUTURE RELEASE
    - ARE GOING TO TEST YOUR CODE EXTENSIVELY
    """

    def _disallow_synchronous(
        self, raise_fn: Callable[[Type[Validator[Any]]], NoReturn]
    ) -> None:
        def _replacement_validate_to_tuple(val: Any) -> NoReturn:
            raise_fn(self.__class__)

        self.validate_to_tuple = _replacement_validate_to_tuple  # type: ignore[assignment]  # noqa: E501

    def validate_to_tuple(self, val: Any) -> ResultTuple[SuccessT]:
        raise NotImplementedError()  # pragma: no cover

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[SuccessT]:
        raise NotImplementedError()  # pragma: no cover

    async def validate_async(self, val: Any) -> ValidationResult[SuccessT]:
        result = await self.validate_to_tuple_async(val)
        if result[0]:
            return Valid(result[1])
        else:
            return result[1]

    def __call__(self, val: Any) -> ValidationResult[SuccessT]:
        result = self.validate_to_tuple(val)
        if result[0]:
            return Valid(result[1])
        else:
            return result[1]


def _simple_type_validator(
    instance: "_ExactTypeValidator[A]", type_: Type[A], type_err: TypeErr
) -> Callable[[Any], ResultTuple[A]]:
    def inner(val: Any) -> ResultTuple[A]:
        if type(val) is type_:
            return True, val
        else:
            return False, Invalid(type_err, val, instance)

    return inner


def _async_predicates_warning(cls: Type[Any]) -> NoReturn:
    raise AssertionError(
        f"{cls.__name__} cannot run `predicates_async` in synchronous calls. "
        f"Please `await` the `.validate_async` method instead; or remove the "
        f"items in `predicates_async`."
    )


def _raise_validate_object_async_in_sync_mode(cls: Type[Any]) -> NoReturn:
    raise AssertionError(
        f"{cls.__name__} cannot run `validate_object_async` in synchronous calls. "
        f"Please `await` the `.validate_async` method instead."
    )


def _repr_helper(cls: Type[Any], arg_strs: List[str]) -> str:
    return f"{cls.__name__}({', '.join(arg_strs)})"


class _ExactTypeValidator(_ToTupleValidator[SuccessT]):
    """
    This `Validator` subclass exists primarily for code cleanliness and standardization.
    It allows us to have very simple Scalar validators.

    This class may go away!

    DO NOT USE THIS UNLESS YOU:
    - ARE OK WITH THIS DISAPPEARING IN A FUTURE RELEASE
    - ARE GOING TO TEST YOUR CODE EXTENSIVELY
    """

    __match_args__ = ("predicates", "predicates_async", "preprocessors")

    # SHOULD BE THE SAME AS SuccessT but mypy can't handle that...? v0.991
    _TYPE: ClassVar[Type[Any]]
    _type_err: TypeErr

    def __init__(
        self,
        *predicates: Predicate[SuccessT],
        predicates_async: Optional[List[PredicateAsync[SuccessT]]] = None,
        preprocessors: Optional[List[Processor[SuccessT]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors
        _type_err = TypeErr(self._TYPE)
        self._type_err = _type_err

        # optimization for simple  validators. can speed up by ~15%
        if not predicates and not predicates_async and not preprocessors:
            self.validate_to_tuple = _simple_type_validator(  # type: ignore
                self, self._TYPE, _type_err
            )
        elif predicates_async:
            self._disallow_synchronous(_async_predicates_warning)

    def validate_to_tuple(self, val: Any) -> ResultTuple[SuccessT]:
        if type(val) is self._TYPE:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            if self.predicates:
                errors: List[Any] = [pred for pred in self.predicates if not pred(val)]
                if errors:
                    return False, Invalid(PredicateErrs(errors), val, self)
                else:
                    return True, val
            else:
                return True, val
        return False, Invalid(self._type_err, val, self)

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[SuccessT]:
        if type(val) is self._TYPE:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            errors: List[Union[Predicate[SuccessT], PredicateAsync[SuccessT]]] = [
                pred for pred in self.predicates if not pred(val)
            ]

            if self.predicates_async:
                errors.extend(
                    [
                        pred
                        for pred in self.predicates_async
                        if not await pred.validate_async(val)
                    ]
                )
            if errors:
                return False, Invalid(PredicateErrs(errors), val, self)
            else:
                return True, val
        return False, Invalid(self._type_err, val, self)

    def __eq__(self, other: Any) -> bool:
        return (
            type(other) is type(self)
            and self.predicates == other.predicates
            and self.predicates_async == other.predicates_async
            and self.preprocessors == other.preprocessors
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            ([] if not self.predicates else [repr(p) for p in self.predicates])
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("predicates_async", self.predicates_async),
                    ("preprocessors", self.preprocessors),
                ]
                if v
            ],
        )


class _CoercingValidator(_ToTupleValidator[SuccessT]):
    """
    This `Validator` subclass exists primarily for code cleanliness and standardization.
    It allows us to have very simple Scalar validators.

    This class may go away!

    DO NOT USE THIS UNLESS YOU:
    - ARE OK WITH THIS DISAPPEARING IN A FUTURE RELEASE
    - ARE GOING TO TEST YOUR CODE EXTENSIVELY
    """

    __match_args__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[SuccessT],
        predicates_async: Optional[List[PredicateAsync[SuccessT]]] = None,
        preprocessors: Optional[List[Processor[SuccessT]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

        if predicates_async:
            self._disallow_synchronous(_async_predicates_warning)

    def coerce_to_type(self, val: Any) -> ResultTuple[SuccessT]:
        raise NotImplementedError()  # pragma: no cover

    def validate_to_tuple(self, val: Any) -> ResultTuple[SuccessT]:
        result = self.coerce_to_type(val)
        if result[0]:
            val_or_type_err = result[1]
            if self.preprocessors:
                for proc in self.preprocessors:
                    val_or_type_err = proc(val_or_type_err)

            if self.predicates:
                errors: List[Any] = [
                    pred for pred in self.predicates if not pred(val_or_type_err)
                ]
                if errors:
                    return False, Invalid(PredicateErrs(errors), val_or_type_err, self)
                else:
                    return True, val_or_type_err
            else:
                return True, val_or_type_err
        return False, result[1]

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[SuccessT]:
        result = self.coerce_to_type(val)
        if result[0]:
            val_or_type_err = result[1]
            if self.preprocessors:
                for proc in self.preprocessors:
                    val_or_type_err = proc(val_or_type_err)

            errors: List[Union[Predicate[SuccessT], PredicateAsync[SuccessT]]] = [
                pred for pred in self.predicates if not pred(val_or_type_err)
            ]

            if self.predicates_async:
                errors.extend(
                    [
                        pred
                        for pred in self.predicates_async
                        if not await pred.validate_async(val_or_type_err)
                    ]
                )
            if errors:
                return False, Invalid(PredicateErrs(errors), val_or_type_err, self)
            else:
                return True, val_or_type_err
        return False, result[1]

    def __eq__(self, other: Any) -> bool:
        return (
            type(other) is type(self)
            and self.predicates == other.predicates
            and self.predicates_async == other.predicates_async
            and self.preprocessors == other.preprocessors
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            ([] if not self.predicates else [repr(p) for p in self.predicates])
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("predicates_async", self.predicates_async),
                    ("preprocessors", self.preprocessors),
                ]
                if v
            ],
        )


def _union_validator(
    source_validator: Validator[A], validators: Tuple[Validator[Any], ...], val: Any
) -> ResultTuple[A]:
    errs = []
    for validator in validators:
        if isinstance(validator, _ToTupleValidator):
            result_tup = validator.validate_to_tuple(val)
            if result_tup[0]:
                return True, result_tup[1]
            else:
                errs.append(result_tup[1])
        else:
            result = validator(val)
            if result.is_valid:
                return True, result.val
            else:
                errs.append(result)
    return False, Invalid(UnionErrs(errs), val, source_validator)


async def _union_validator_async(
    source_validator: Validator[A], validators: Tuple[Validator[Any], ...], val: Any
) -> ResultTuple[A]:
    errs = []
    for validator in validators:
        if isinstance(validator, _ToTupleValidator):
            result_tup = await validator.validate_to_tuple_async(val)
            if result_tup[0]:
                return True, result_tup[1]
            else:
                errs.append(result_tup[1])
        else:
            result = await validator.validate_async(val)
            if result.is_valid:
                return True, result.val
            else:
                errs.append(result)
    return False, Invalid(UnionErrs(errs), val, source_validator)


def _wrap_sync_validator(obj: Validator[A]) -> Callable[[Any], ResultTuple[A]]:
    if isinstance(obj, _ToTupleValidator):
        return obj.validate_to_tuple
    else:

        def inner(v: Any) -> ResultTuple[A]:
            result = obj(v)
            if result.is_valid:
                return True, result.val
            else:
                return False, result

        return inner


def _wrap_async_validator(
    obj: Validator[A],
) -> Callable[[Any], Awaitable[ResultTuple[A]]]:
    if isinstance(obj, _ToTupleValidator):
        return obj.validate_to_tuple_async
    else:
        async_validator = obj.validate_async

        async def inner(v: Any) -> ResultTuple[A]:
            result = await async_validator(v)
            if result.is_valid:
                return True, result.val
            else:
                return False, result

        return inner


def _is_typed_dict_cls(t: Type[Any]) -> bool:
    return (
        hasattr(t, "__annotations__") and hasattr(t, "__total__") and hasattr(t, "keys")
    )


def _raise_cannot_define_validate_object_and_validate_object_async() -> None:
    raise AssertionError(
        "validate_object and validate_object_async cannot both be defined"
    )
