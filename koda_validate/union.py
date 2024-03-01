from typing import Any, List, Optional, Tuple, Union, overload

from koda_validate._generics import T1, T2, T3, T4, T5, T6, T7, T8, A
from koda_validate._internal import (
    _repr_helper,
    _ResultTuple,
    _ToTupleValidator,
    _union_validator,
    _union_validator_async,
)
from koda_validate.base import Validator


class UnionValidator(_ToTupleValidator[A]):
    __match_args__ = ("validators",)

    def __init__(
        self,
        # just a way to enforce at least one validator is defined
        validator_1: Validator[Any],
        *validators: Validator[Any],
    ) -> None:
        """
        You probably do not want to call the ``__init__`` method directly. Instead,
        look to UnionValidator.typed and UnionValidator.untyped. They are thin wrappers
        around the `__init__` method, but they allow more explicit control over types.

        :param validator_1: the first variant of the union. This is specified on its own,
            so we have at least one variant specified
        :param validators: the rest of the variants of the union
        """
        self.validators: Tuple[Validator[Any], ...] = (validator_1,) + validators

    @overload
    @staticmethod
    def typed(validator_1: Validator[T1], /) -> "UnionValidator[T1]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        /,
    ) -> "UnionValidator[Union[T1, T2]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        /,
    ) -> "UnionValidator[Union[T1, T2, T3]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        validator_4: Validator[T4],
        /,
    ) -> "UnionValidator[Union[T1, T2, T3, T4]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        validator_4: Validator[T4],
        validator_5: Validator[T5],
        /,
    ) -> "UnionValidator[Union[T1, T2, T3, T4, T5]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        validator_4: Validator[T4],
        validator_5: Validator[T5],
        validator_6: Validator[T6],
        /,
    ) -> "UnionValidator[Union[T1, T2, T3, T4, T5, T6]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        validator_4: Validator[T4],
        validator_5: Validator[T5],
        validator_6: Validator[T6],
        validator_7: Validator[T7],
        /,
    ) -> "UnionValidator[Union[T1, T2, T3, T4, T5, T6, T7]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        validator_4: Validator[T4],
        validator_5: Validator[T5],
        validator_6: Validator[T6],
        validator_7: Validator[T7],
        validator_8: Validator[T8],
        /,
    ) -> "UnionValidator[Union[T1, T2, T3, T4, T5, T6, T7, T8]]":
        ...  # pragma: no cover

    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Optional[Validator[T2]] = None,
        validator_3: Optional[Validator[T3]] = None,
        validator_4: Optional[Validator[T4]] = None,
        validator_5: Optional[Validator[T5]] = None,
        validator_6: Optional[Validator[T6]] = None,
        validator_7: Optional[Validator[T7]] = None,
        validator_8: Optional[Validator[T8]] = None,
    ) -> Union[
        "UnionValidator[T1]",
        "UnionValidator[Union[T1, T2]]",
        "UnionValidator[Union[T1, T2, T3]]",
        "UnionValidator[Union[T1, T2, T3, T4]]",
        "UnionValidator[Union[T1, T2, T3, T4, T5]]",
        "UnionValidator[Union[T1, T2, T3, T4, T5, T6]]",
        "UnionValidator[Union[T1, T2, T3, T4, T5, T6, T7]]",
        "UnionValidator[Union[T1, T2, T3, T4, T5, T6, T7, T8]]",
    ]:
        """
        Can be used for up to 8 typed variants. For more than 8 variants,
        use ``UnionValidator.untyped``. Arguments should be positional only.
        (``@overloads`` specify that arguments should be positional-only.)

        :param validator_1: the first variant
        :param validator_2: the second variant (if defined)
        :param validator_3: the third variant (if defined)
        :param validator_4: the fourth variant (if defined)
        :param validator_5: the fifth variant (if defined)
        :param validator_6: the sixth variant (if defined)
        :param validator_7: the seventh variant (if defined)
        :param validator_8: the eighth variant (if defined)
        :return: UnionValidator with the variants defined above.
        """
        validators: List[Validator[Any]] = [
            v
            for v in [
                validator_2,
                validator_3,
                validator_4,
                validator_5,
                validator_6,
                validator_7,
                validator_8,
            ]
            if v
        ]
        return UnionValidator(validator_1, *validators)

    @staticmethod
    def untyped(
        validator_1: Validator[Any], *validators: Validator[Any]
    ) -> "UnionValidator[Any]":
        r"""
        Can handle any number of variant :class:`Validator<koda_validate.Validator>``\s
        (as opposed to ``UnionValidator.typed``), but does not retain type information.

        :param validator_1: the first variant of the union. This is specified on its own,
            so we have at least one variant specified
        :param validators: the rest of the variants of the union
        :return: UnionValidator with the variants defined above.
        """
        return UnionValidator(validator_1, *validators)

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[A]:
        return _union_validator(self, self.validators, val)

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[A]:
        return await _union_validator_async(self, self.validators, val)

    def __eq__(self, other: Any) -> bool:
        return type(self) == type(other) and self.validators == other.validators

    def __repr__(self) -> str:
        return _repr_helper(self.__class__, [repr(v) for v in self.validators])
