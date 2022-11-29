from abc import abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Hashable,
    List,
    NoReturn,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from koda_validate._generics import A, InputT, SuccessT
from koda_validate.validated import Invalid, Valid, Validated


class InvalidBase:
    pass


@dataclass
class ValidatorErrorBase(InvalidBase):
    """
    Simple base class which merely includes the originating validator for transparency
    """

    validator: "Validator[Any, Any]"


@dataclass
class InvalidCoercion(ValidatorErrorBase):
    """
    When one or more types can be coerced to a destination type
    """

    compatible_types: List[Type[Any]]
    dest_type: Type[Any]


class InvalidMissingKey:
    """
    A key is missing from a dictionary
    """

    _instance: ClassVar[Optional["InvalidMissingKey"]] = None

    def __new__(cls) -> "InvalidMissingKey":
        """
        A singleton, so we can do `is` checks if we want.
        """
        if cls._instance is None:
            cls._instance = super(InvalidMissingKey, cls).__new__(cls)
        return cls._instance


@dataclass
class InvalidExtraKeys(ValidatorErrorBase):
    """
    extra keys were present in a dictionary
    """

    expected_keys: Set[Hashable]


invalid_missing_key = InvalidMissingKey()


@dataclass
class InvalidDict(ValidatorErrorBase):
    """
    validation failures for key/value pairs on a record-like
    dictionary
    """

    # todo: add validator, rename
    keys: Dict[Hashable, "ValidationErr"]


@dataclass
class InvalidKeyVal:
    """
    key and/or value errors from a single key/value pair
    """

    key: Optional["ValidationErr"]
    val: Optional["ValidationErr"]


@dataclass
class InvalidMap:
    """
    errors from key/value pairs of a map-like dictionary
    """

    keys: Dict[Hashable, InvalidKeyVal]


@dataclass
class InvalidIterable(ValidatorErrorBase):
    """
    dictionary of validation errors by index
    """

    indexes: Dict[int, "ValidationErr"]


@dataclass
class InvalidVariants:
    """
    none of these validators was satisfied by a given value
    """

    variants: List["ValidationErr"]


@dataclass
class InvalidMessage:
    """
    If all you want to do is produce a message, this can be useful
    """

    err_message: str


@dataclass
class InvalidType(ValidatorErrorBase):
    """
    A specific type was required but not provided
    """

    expected_type: Type[Any]


ValidationErr = Union[
    InvalidCoercion,
    InvalidMessage,
    InvalidDict,
    InvalidExtraKeys,
    InvalidIterable,
    InvalidMissingKey,
    InvalidMap,
    InvalidType,
    InvalidVariants,
    # todo: add explicit wrapper, consider properly parameterizing
    List[Union["Predicate[Any]", "PredicateAsync[Any]"]],
]

ValidationResult = Validated[A, ValidationErr]


class Validator(Generic[InputT, SuccessT]):
    """
    Essentially a `Callable[[A], Result[B, ValidationErr]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    async def validate_async(self, val: InputT) -> ValidationResult[SuccessT]:
        """
        make it possible for all validators to be async-compatible
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, val: InputT) -> ValidationResult[SuccessT]:
        raise NotImplementedError()  # pragma: no cover


class Predicate(Generic[InputT]):
    """
    The important aspect of a `Predicate` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).

    Compatible with Async / but async behavior is _not_ customizable. that's
    why we have PredicateAsync. Any IO needs should probably go there!
    """

    @abstractmethod
    def __call__(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover


class PredicateAsync(Generic[InputT]):
    """
    For async-only validation.
    """

    @abstractmethod
    async def validate_async(self, val: InputT) -> bool:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover


# should look like this, but mypy doesn't understand it as of 0.982
# _ResultTuple = Union[Tuple[Literal[True], A], Tuple[Literal[False], FailT]]
_ResultTupleUnsafe = Tuple[bool, Any]


def _async_predicates_warning(cls: Type[Any]) -> NoReturn:
    raise AssertionError(
        f"{cls.__name__} cannot run `predicates_async` in synchronous calls. "
        f"Please `await` the `.validate_async` method instead; or remove the "
        f"items in `predicates_async`."
    )


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
                errors: ValidationErr = [
                    pred for pred in self.predicates if not pred(val)
                ]
                if errors:
                    return False, errors
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
                return False, errors
            else:
                return True, val
        return False, self._type_err


class _ToTupleValidatorUnsafeScalar(_ToTupleValidatorUnsafe[InputT, SuccessT]):
    """
    This `Validator` subclass exists primarily for code cleanliness and standardization.
    It allows us to have very simple Scalar validators.

    This class may go away!

    DO NOT USE THIS UNLESS YOU:
    - ARE OK WITH THIS DISAPPEARING IN A FUTURE RELEASE
    - ARE GOING TO TEST YOUR CODE EXTENSIVELY
    """

    def __init__(
        self,
        *predicates: Predicate[SuccessT],
        predicates_async: Optional[List[PredicateAsync[SuccessT]]] = None,
        preprocessors: Optional[List[Processor[SuccessT]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def check_and_or_coerce_type(self, val: InputT) -> _ResultTupleUnsafe:
        raise NotImplementedError()  # pragma: no cover

    def validate_to_tuple(self, val: InputT) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        succeeded, val_or_type_err = self.check_and_or_coerce_type(val)
        if succeeded:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val_or_type_err = proc(val_or_type_err)

            if self.predicates:
                errors: ValidationErr = [
                    pred for pred in self.predicates if not pred(val_or_type_err)
                ]
                if errors:
                    return False, errors
                else:
                    return True, val_or_type_err
            else:
                return True, val_or_type_err
        return False, val_or_type_err

    async def validate_to_tuple_async(self, val: InputT) -> _ResultTupleUnsafe:
        succeeded, val_or_type_err = self.check_and_or_coerce_type(val)
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
                return False, errors
            else:
                return True, val_or_type_err
        return False, val_or_type_err
