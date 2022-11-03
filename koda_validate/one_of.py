from typing import Any

from koda import Either, Either3, Err, First, Ok, Result, Second, Third
from koda._generics import A, B, C

from koda_validate.typedefs import Serializable, Validator


class OneOf2(Validator[Any, Either[A, B], Serializable]):
    __slots__ = ("variant_1", "variant_2")
    __match_args__ = ("variant_1", "variant_2")

    def __init__(
        self,
        variant_1: Validator[Any, A, Serializable],
        variant_2: Validator[Any, B, Serializable],
    ) -> None:
        self.variant_1 = variant_1
        self.variant_2 = variant_2

    def __call__(self, val: Any) -> Result[Either[A, B], Serializable]:
        if (v1_result := self.variant_1(val)).is_ok:
            return Ok(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_ok:
                return Ok(Second(v2_result.val))
            else:
                return Err(
                    {
                        "variant 1": v1_result.val,
                        "variant 2": v2_result.val,
                    }
                )

    async def validate_async(self, val: Any) -> Result[Either[A, B], Serializable]:
        if (v1_result := await self.variant_1.validate_async(val)).is_ok:
            return Ok(First(v1_result.val))
        else:
            if (v2_result := await self.variant_2.validate_async(val)).is_ok:
                return Ok(Second(v2_result.val))
            else:
                return Err(
                    {
                        "variant 1": v1_result.val,
                        "variant 2": v2_result.val,
                    }
                )


class OneOf3(Validator[Any, Either3[A, B, C], Serializable]):
    __match_args__ = ("variant_1", "variant_2", "variant_3")
    __slots__ = ("variant_1", "variant_2", "variant_3")

    def __init__(
        self,
        variant_1: Validator[Any, A, Serializable],
        variant_2: Validator[Any, B, Serializable],
        variant_3: Validator[Any, C, Serializable],
    ) -> None:
        self.variant_1 = variant_1
        self.variant_2 = variant_2
        self.variant_3 = variant_3

    def __call__(self, val: Any) -> Result[Either3[A, B, C], Serializable]:
        if (v1_result := self.variant_1(val)).is_ok:
            return Ok(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_ok:
                return Ok(Second(v2_result.val))
            else:
                if (v3_result := self.variant_3(val)).is_ok:
                    return Ok(Third(v3_result.val))
                else:
                    return Err(
                        {
                            "variant 1": v1_result.val,
                            "variant 2": v2_result.val,
                            "variant 3": v3_result.val,
                        }
                    )

    async def validate_async(self, val: Any) -> Result[Either3[A, B, C], Serializable]:
        if (v1_result := self.variant_1(val)).is_ok:
            return Ok(First(v1_result.val))
        else:
            if (v2_result := self.variant_2(val)).is_ok:
                return Ok(Second(v2_result.val))
            else:
                if (v3_result := self.variant_3(val)).is_ok:
                    return Ok(Third(v3_result.val))
                else:
                    return Err(
                        {
                            "variant 1": v1_result.val,
                            "variant 2": v2_result.val,
                            "variant 3": v3_result.val,
                        }
                    )
