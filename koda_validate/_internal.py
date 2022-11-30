from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Hashable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from koda import nothing

from koda_validate._generics import InputT, SuccessT
from koda_validate.base import (
    InvalidDict,
    InvalidExtraKeys,
    InvalidMissingKey,
    InvalidPredicates,
    InvalidType,
    Predicate,
    PredicateAsync,
    Processor,
    ValidationErr,
    ValidationResult,
    Validator,
    _async_predicates_warning,
    _ResultTupleUnsafe,
)
from koda_validate.validated import Invalid, Valid


class _ToTupleValidatorUnsafe(Validator[InputT, SuccessT]):
    """
    This `Validator` subclass exists for optimization. When we call
    nested validators it's much less computation to deal with simple
    tuples and bools, instead of Valid and Invalid instances.
    This class may go away!

    DO NOT USE THIS UNLESS YOU:
    - ARE OK WITH THIS DISAPPEARING IN A FUTURE RELEASE
    - ARE GOING TO TEST YOUR CODE EXTENSIVELY
    """

    def validate_to_tuple(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError()  # pragma: no cover

    async def validate_to_tuple_async(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError()  # pragma: no cover

    async def validate_async(self, val: InputT) -> ValidationResult[SuccessT]:
        valid, result_val = await self.validate_to_tuple_async(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)

    def __call__(self, val: InputT) -> ValidationResult[SuccessT]:
        valid, result_val = self.validate_to_tuple(val)
        if valid:
            return Valid(result_val)
        else:
            return Invalid(result_val)


def validate_dict_to_tuple(
    source_validator: Validator[Any, Any],
    preprocessors: Optional[List[Processor[Dict[Any, Any]]]],
    fast_keys: List[Tuple[Hashable, Validator[Any, Any], bool, bool]],
    schema: Dict[Any, Validator[Any, Any]],
    unknown_keys_err: Tuple[bool, InvalidExtraKeys],
    data: Any,
) -> _ResultTupleUnsafe:
    if not isinstance(data, dict):
        return False, InvalidType(source_validator, dict)

    if preprocessors:
        for preproc in preprocessors:
            data = preproc(data)

    # this seems to be faster than `for key_ in data.keys()`
    for key_ in data:
        if key_ not in schema:
            return unknown_keys_err

    success_dict: Dict[Hashable, Any] = {}
    errs: Dict[Hashable, ValidationErr] = {}
    for key_, validator, key_required, is_tuple_validator in fast_keys:
        try:
            val = data[key_]
        except KeyError:
            if key_required:
                errs[key_] = InvalidMissingKey(source_validator)
            elif not errs:
                success_dict[key_] = nothing
        else:
            if is_tuple_validator:
                if TYPE_CHECKING:
                    assert isinstance(validator, _ToTupleValidatorUnsafe)
                success, new_val = validator.validate_to_tuple(val)
            else:
                success, new_val = (
                    (True, result_.val)
                    if (result_ := validator(val)).is_valid
                    else (False, result_.val)
                )

            if not success:
                errs[key_] = new_val
            elif not errs:
                success_dict[key_] = new_val

    if errs:
        return False, InvalidDict(source_validator, errs)
    else:
        return True, success_dict


async def validate_dict_to_tuple_async(
    source_validator: Validator[Any, Any],
    preprocessors: Optional[List[Processor[Dict[Any, Any]]]],
    fast_keys: List[Tuple[Hashable, Validator[Any, Any], bool, bool]],
    schema: Dict[Any, Validator[Any, Any]],
    unknown_keys_err: Tuple[bool, InvalidExtraKeys],
    data: Any,
) -> _ResultTupleUnsafe:
    if not isinstance(data, dict):
        return False, InvalidType(source_validator, dict)

    if preprocessors:
        for preproc in preprocessors:
            data = preproc(data)

    # this seems to be faster than `for key_ in data.keys()`
    for key_ in data:
        if key_ not in schema:
            return unknown_keys_err

    success_dict: Dict[Hashable, Any] = {}
    errs: Dict[Hashable, ValidationErr] = {}
    for key_, validator, key_required, is_tuple_validator in fast_keys:
        try:
            val = data[key_]
        except KeyError:
            if key_required:
                errs[key_] = InvalidMissingKey(source_validator)
            elif not errs:
                success_dict[key_] = nothing
        else:
            if is_tuple_validator:
                if TYPE_CHECKING:
                    assert isinstance(validator, _ToTupleValidatorUnsafe)
                success, new_val = await validator.validate_to_tuple_async(val)
            else:
                success, new_val = (
                    (True, result_.val)
                    if (result_ := await validator.validate_async(val)).is_valid
                    else (False, result_.val)
                )

            if not success:
                errs[key_] = new_val
            elif not errs:
                success_dict[key_] = new_val

    if errs:
        return False, InvalidDict(source_validator, errs)
    else:
        return True, success_dict


class _ExactTypeValidator(_ToTupleValidatorUnsafe[Any, SuccessT]):
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
    _type_err: InvalidType

    def __init__(
        self,
        *predicates: Predicate[SuccessT],
        predicates_async: Optional[List[PredicateAsync[SuccessT]]] = None,
        preprocessors: Optional[List[Processor[SuccessT]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors
        self._type_err = InvalidType(self, self._TYPE)

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if type(val) is self._TYPE:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            if self.predicates:
                errors: List[Any] = [pred for pred in self.predicates if not pred(val)]
                if errors:
                    return False, InvalidPredicates(self, errors)
                else:
                    return True, val
            else:
                return True, val
        return False, self._type_err

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
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
                return False, InvalidPredicates(self, errors)
            else:
                return True, val
        return False, self._type_err


class _CoercionValidator(_ToTupleValidatorUnsafe[InputT, SuccessT]):
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

    def coerce_to_type(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError()  # pragma: no cover

    def validate_to_tuple(self, val: InputT) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        succeeded, val_or_type_err = self.coerce_to_type(val)
        if succeeded:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val_or_type_err = proc(val_or_type_err)

            if self.predicates:
                errors: List[Any] = [
                    pred for pred in self.predicates if not pred(val_or_type_err)
                ]
                if errors:
                    return False, InvalidPredicates(self, errors)
                else:
                    return True, val_or_type_err
            else:
                return True, val_or_type_err
        return False, val_or_type_err

    async def validate_to_tuple_async(self, val: InputT) -> _ResultTupleUnsafe:
        succeeded, val_or_type_err = self.coerce_to_type(val)
        if succeeded:
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
                return False, InvalidPredicates(self, errors)
            else:
                return True, val_or_type_err
        return False, val_or_type_err
