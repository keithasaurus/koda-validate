from typing import Any

from koda import Either, Either3, First, Second, Third
from koda._generics import A, B, C

from koda_validate import Invalid, Valid
from koda_validate.base import InvalidVariants, ValidationResult, Validator


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
                return Invalid(InvalidVariants([v1_result.val, v2_result.val]))

    def __call__(self, val: Any) -> ValidationResult[Either[A, B]]:
        if (v1_result := self.variant_1(val)).is_valid:
            return Valid(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_valid:
                return Valid(Second(v2_result.val))
            else:
                return Invalid(InvalidVariants([v1_result.val, v2_result.val]))


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
                        InvalidVariants(
                            self,
                            [
                                v1_result.val,
                                v2_result.val,
                                v3_result.val,
                            ],
                        )
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
                        InvalidVariants(
                            self,
                            [
                                v1_result.val,
                                v2_result.val,
                                v3_result.val,
                            ],
                        )
                    )
