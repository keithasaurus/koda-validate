from typing import Any, List, Optional, Tuple, Union, overload

from koda import Either, Either3, First, Second, Third
from koda._generics import A, B, C

from koda_validate import Invalid, Valid
from koda_validate._generics import T1, T2, T3, T4, T5, T6, T7, T8
from koda_validate._internal import (
    ResultTuple,
    _repr_helper,
    _ToTupleValidator,
    _union_validator,
    _union_validator_async,
)
from koda_validate.base import ValidationResult, Validator, VariantErrs


class OneOf2(Validator[Either[A, B]]):
    __match_args__ = ("variant_1", "variant_2")

    def __init__(
        self,
        variant_1: Validator[A],
        variant_2: Validator[B],
    ) -> None:
        self.variant_1 = variant_1
        self.variant_2 = variant_2

    async def validate_async(self, val: Any) -> ValidationResult[Either[A, B]]:
        if (v1_result := await self.variant_1.validate_async(val)).is_valid:
            return Valid(First(v1_result.val))
        else:
            if (v2_result := await self.variant_2.validate_async(val)).is_valid:
                return Valid(Second(v2_result.val))
            else:
                return Invalid(VariantErrs([v1_result, v2_result]), val, self)

    def __call__(self, val: Any) -> ValidationResult[Either[A, B]]:
        if (v1_result := self.variant_1(val)).is_valid:
            return Valid(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_valid:
                return Valid(Second(v2_result.val))
            else:
                return Invalid(VariantErrs([v1_result, v2_result]), val, self)

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.variant_1 == other.variant_1
            and self.variant_2 == other.variant_2
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__, [repr(x) for x in [self.variant_1, self.variant_2]]
        )


class OneOf3(Validator[Either3[A, B, C]]):
    __match_args__ = ("variant_1", "variant_2", "variant_3")

    def __init__(
        self,
        variant_1: Validator[A],
        variant_2: Validator[B],
        variant_3: Validator[C],
    ) -> None:
        self.variant_1 = variant_1
        self.variant_2 = variant_2
        self.variant_3 = variant_3

    async def validate_async(self, val: Any) -> ValidationResult[Either3[A, B, C]]:
        if (v1_result := self.variant_1(val)).is_valid:
            return Valid(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_valid:
                return Valid(Second(v2_result.val))
            else:
                if (v3_result := self.variant_3(val)).is_valid:
                    return Valid(Third(v3_result.val))
                else:
                    return Invalid(
                        VariantErrs(
                            [
                                v1_result,
                                v2_result,
                                v3_result,
                            ],
                        ),
                        val,
                        self,
                    )

    def __call__(self, val: Any) -> ValidationResult[Either3[A, B, C]]:
        if (v1_result := self.variant_1(val)).is_valid:
            return Valid(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_valid:
                return Valid(Second(v2_result.val))
            else:
                if (v3_result := self.variant_3(val)).is_valid:
                    return Valid(Third(v3_result.val))
                else:
                    return Invalid(
                        VariantErrs(
                            [
                                v1_result,
                                v2_result,
                                v3_result,
                            ],
                        ),
                        val,
                        self,
                    )

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.variant_1 == other.variant_1
            and self.variant_2 == other.variant_2
            and self.variant_3 == other.variant_3
        )

    def __repr__(self) -> str:
        return _repr_helper(
            self.__class__,
            [repr(x) for x in [self.variant_1, self.variant_2, self.variant_3]],
        )


class OneOfValidator(_ToTupleValidator[Tuple[int, A]]):
    """
    Until we're comfortable using variadic args, we'll just keep this private
    """

    __match_args__ = ("validators",)

    def __init__(
        self,
        # just a way to enforce at least one validator is defined
        validator_1: Validator[Any],
        *validators: Validator[Any],
    ) -> None:
        self.validators: Tuple[Validator[Any], ...] = (validator_1,) + validators

    @overload
    @staticmethod
    def typed(validator_1: Validator[T1]) -> "OneOfValidator[T1]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1], validator_2: Validator[T2]
    ) -> "OneOfValidator[Union[T1, T2]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1], validator_2: Validator[T2], validator_3: Validator[T3]
    ) -> "OneOfValidator[Union[T1, T2, T3]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        validator_4: Validator[T4],
    ) -> "OneOfValidator[Union[T1, T2, T3, T4]]":
        ...  # pragma: no cover

    @overload
    @staticmethod
    def typed(
        validator_1: Validator[T1],
        validator_2: Validator[T2],
        validator_3: Validator[T3],
        validator_4: Validator[T4],
        validator_5: Validator[T5],
    ) -> "OneOfValidator[Union[T1, T2, T3, T4, T5]]":
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
    ) -> "OneOfValidator[Union[T1, T2, T3, T4, T5, T6]]":
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
    ) -> "OneOfValidator[Union[T1, T2, T3, T4, T5, T6, T7]]":
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
    ) -> "OneOfValidator[Union[T1, T2, T3, T4, T5, T6, T7, T8]]":
        ...

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
        "OneOfValidator[T1]",
        "OneOfValidator[Union[T1, T2]]",
        "OneOfValidator[Union[T1, T2, T3]]",
        "OneOfValidator[Union[T1, T2, T3, T4]]",
        "OneOfValidator[Union[T1, T2, T3, T4, T5]]",
        "OneOfValidator[Union[T1, T2, T3, T4, T5, T6]]",
        "OneOfValidator[Union[T1, T2, T3, T4, T5, T6, T7]]",
        "OneOfValidator[Union[T1, T2, T3, T4, T5, T6, T7, T8]]",
    ]:
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
        return OneOfValidator(validator_1, *validators)  # type: ignore

    @staticmethod
    def untyped(
        validator_1: Validator[Any], *validators: Validator[Any]
    ) -> "OneOfValidator[Any]":
        return OneOfValidator(validator_1, *validators)

    def validate_to_tuple(self, val: Any) -> ResultTuple[Tuple[int, A]]:
        return _union_validator(self, self.validators, val)  # type: ignore

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Tuple[int, A]]:
        return await _union_validator_async(self, self.validators, val)  # type: ignore

    def __eq__(self, other: Any) -> bool:
        return type(self) == type(other) and self.validators == other.validators

    def __repr__(self) -> str:
        return _repr_helper(self.__class__, [repr(v) for v in self.validators])
