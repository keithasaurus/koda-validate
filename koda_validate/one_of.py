from typing import Any

from koda import Either, Either3, First, Second, Third
from koda._generics import A, B, C

from koda_validate.base import Serializable, ValidationErr, Validator
from koda_validate.validated import Invalid, Valid, Validated


class OneOf2(Validator[Any, Either[A, B]]):
    __slots__ = ("variant_1", "variant_2")
    __match_args__ = ("variant_1", "variant_2")

    def __init__(
        self,
        variant_1: Validator[Any, A],
        variant_2: Validator[Any, B],
    ) -> None:
        self.variant_1 = variant_1
        self.variant_2 = variant_2

    def __call__(self, val: Any) -> Validated[Either[A, B], ValidationErr]:
        if (v1_result := self.variant_1(val)).is_valid:
            return Valid(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_valid:
                return Valid(Second(v2_result.val))
            else:
                return Invalid(
                    {
                        "variant 1": v1_result.val,
                        "variant 2": v2_result.val,
                    }
                )

    async def validate_async(self, val: Any) -> Validated[Either[A, B], Serializable]:
        if (v1_result := await self.variant_1.validate_async(val)).is_valid:
            return Valid(First(v1_result.val))
        else:
            if (v2_result := await self.variant_2.validate_async(val)).is_valid:
                return Valid(Second(v2_result.val))
            else:
                return Invalid(
                    {
                        "variant 1": v1_result.val,
                        "variant 2": v2_result.val,
                    }
                )


class OneOf3(Validator[Any, Either3[A, B, C]]):
    __match_args__ = ("variant_1", "variant_2", "variant_3")
    __slots__ = ("variant_1", "variant_2", "variant_3")

    def __init__(
        self,
        variant_1: Validator[Any, A],
        variant_2: Validator[Any, B],
        variant_3: Validator[Any, C],
    ) -> None:
        self.variant_1 = variant_1
        self.variant_2 = variant_2
        self.variant_3 = variant_3

    def __call__(self, val: Any) -> Validated[Either3[A, B, C], ValidationErr]:
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
                        {
                            "variant 1": v1_result.val,
                            "variant 2": v2_result.val,
                            "variant 3": v3_result.val,
                        }
                    )

    async def validate_async(
        self, val: Any
    ) -> Validated[Either3[A, B, C], ValidationErr]:
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
                        {
                            "variant 1": v1_result.val,
                            "variant 2": v2_result.val,
                            "variant 3": v3_result.val,
                        }
                    )
