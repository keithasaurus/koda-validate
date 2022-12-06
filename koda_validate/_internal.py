from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Hashable,
    List,
    Literal,
    NoReturn,
    Optional,
    Tuple,
    Type,
    Union,
)

from koda_validate import Invalid, Valid
from koda_validate._generics import A, SuccessT
from koda_validate.base import (
    ExtraKeysErr,
    KeyErrs,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    Processor,
    TypeErr,
    ValidationResult,
    Validator,
    VariantErrs,
    missing_key_err,
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


def validate_dict_to_tuple(
    source_validator: Validator[Any],
    preprocessors: Optional[List[Processor[Dict[Any, Any]]]],
    fast_keys: List[Tuple[Hashable, Validator[Any], bool, bool]],
    schema: Dict[Any, Validator[Any]],
    unknown_keys_err: ExtraKeysErr,
    data: Any,
) -> ResultTuple[Dict[Any, Any]]:
    if not type(data) is dict:
        return False, Invalid(source_validator, data, TypeErr(dict))

    if preprocessors:
        for preproc in preprocessors:
            data = preproc(data)

    # this seems to be faster than `for key_ in data.keys()`
    for key_ in data:
        if key_ not in schema:
            return False, Invalid(source_validator, data, unknown_keys_err)

    success_dict: Dict[Any, Any] = {}
    errs: Dict[Any, Invalid] = {}
    for key_, validator, key_required, is_tuple_validator in fast_keys:
        if key_ not in data:
            if key_required:
                errs[key_] = Invalid(source_validator, data, missing_key_err)
        else:
            if is_tuple_validator:
                success, new_val = validator.validate_to_tuple(data[key_])  # type: ignore
            else:
                success, new_val = (
                    (True, result_.val)
                    if (result_ := validator(data[key_])).is_valid
                    else (False, result_)
                )

            if not success:
                errs[key_] = new_val
            elif not errs:
                success_dict[key_] = new_val

    if errs:
        return False, Invalid(source_validator, data, KeyErrs(errs))
    else:
        return True, success_dict


async def validate_dict_to_tuple_async(
    source_validator: Validator[Any],
    preprocessors: Optional[List[Processor[Dict[Any, Any]]]],
    fast_keys: List[Tuple[Hashable, Validator[Any], bool, bool]],
    schema: Dict[Any, Validator[Any]],
    unknown_keys_err: ExtraKeysErr,
    data: Any,
) -> ResultTuple[Dict[Any, Any]]:
    if not type(data) is dict:
        return False, Invalid(source_validator, data, TypeErr(dict))

    if preprocessors:
        for preproc in preprocessors:
            data = preproc(data)

    # this seems to be faster than `for key_ in data.keys()`
    for key_ in data:
        if key_ not in schema:
            return False, Invalid(source_validator, data, unknown_keys_err)

    success_dict: Dict[Any, Any] = {}
    errs: Dict[Any, Invalid] = {}
    for key_, validator, key_required, is_tuple_validator in fast_keys:
        if key_ not in data:
            if key_required:
                errs[key_] = Invalid(source_validator, data, missing_key_err)
        else:
            if is_tuple_validator:
                success, new_val = await validator.validate_to_tuple_async(  # type: ignore  # noqa: E501
                    data[key_]
                )
            else:
                success, new_val = (
                    (True, result_.val)
                    if (result_ := await validator.validate_async(data[key_])).is_valid
                    else (False, result_)
                )

            if not success:
                errs[key_] = new_val
            elif not errs:
                success_dict[key_] = new_val

    if errs:
        return False, Invalid(source_validator, data, KeyErrs(errs))
    else:
        return True, success_dict


def _simple_type_validator(
    instance: "_ExactTypeValidator[A]", type_: Type[A], type_err: TypeErr
) -> Callable[[Any], ResultTuple[A]]:
    def inner(val: Any) -> ResultTuple[A]:
        if type(val) is type_:
            return True, val
        else:
            return False, Invalid(instance, val, type_err)

    return inner


def _async_predicates_warning(cls: Type[Any]) -> NoReturn:
    raise AssertionError(
        f"{cls.__name__} cannot run `predicates_async` in synchronous calls. "
        f"Please `await` the `.validate_async` method instead; or remove the "
        f"items in `predicates_async`."
    )


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

    def validate_to_tuple(self, val: Any) -> ResultTuple[SuccessT]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if type(val) is self._TYPE:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            if self.predicates:
                errors: List[Any] = [pred for pred in self.predicates if not pred(val)]
                if errors:
                    return False, Invalid(self, val, PredicateErrs(errors))
                else:
                    return True, val
            else:
                return True, val
        return False, Invalid(self, val, self._type_err)

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
                return False, Invalid(self, val, PredicateErrs(errors))
            else:
                return True, val
        return False, Invalid(self, val, self._type_err)

    def __eq__(self, other: Any) -> bool:
        return (
            type(other) is type(self)
            and self.predicates == other.predicates
            and self.predicates_async == other.predicates_async
            and self.preprocessors == other.preprocessors
        )

    def __repr__(self) -> str:
        attrs_str = (
            "" if not self.predicates else ", ".join([repr(p) for p in self.predicates])
        )
        attrs_str = ", ".join(
            [attrs_str]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("predicates_async", self.predicates_async),
                    ("preprocessors", self.preprocessors),
                ]
                if v
            ]
        )
        return f"{self.__class__.__name__}({attrs_str})"


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

    def coerce_to_type(self, val: Any) -> ResultTuple[SuccessT]:
        raise NotImplementedError()  # pragma: no cover

    def validate_to_tuple(self, val: Any) -> ResultTuple[SuccessT]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

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
                    return False, Invalid(self, val_or_type_err, PredicateErrs(errors))
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
                return False, Invalid(self, val_or_type_err, PredicateErrs(errors))
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
        attrs_str = (
            "" if not self.predicates else ", ".join([repr(p) for p in self.predicates])
        )
        attrs_str = ", ".join(
            [attrs_str]
            + [
                f"{k}={repr(v)}"
                for k, v in [
                    ("predicates_async", self.predicates_async),
                    ("preprocessors", self.preprocessors),
                ]
                if v
            ]
        )
        return f"{self.__class__.__name__}({attrs_str})"


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
    return False, Invalid(source_validator, val, VariantErrs(errs))


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
    return False, Invalid(source_validator, val, VariantErrs(errs))
