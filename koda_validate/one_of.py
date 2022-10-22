from dataclasses import dataclass
from typing import Any

from koda import Either, Either3, Err, First, Ok, Result, Second, Third
from koda._generics import A, B, C

from koda_validate.typedefs import JSONValue, Validator


@dataclass(frozen=True, init=False)
class OneOf2(Validator[Any, Either[A, B], JSONValue]):
    variant_one: Validator[Any, A, JSONValue]
    variant_two: Validator[Any, B, JSONValue]

    def __init__(
        self,
        variant_one: Validator[Any, A, JSONValue],
        variant_two: Validator[Any, B, JSONValue],
    ) -> None:
        object.__setattr__(self, "variant_one", variant_one)
        object.__setattr__(self, "variant_two", variant_two)

    def __call__(self, val: Any) -> Result[Either[A, B], JSONValue]:
        v1_result = self.variant_one(val)

        if isinstance(v1_result, Ok):
            return Ok(First(v1_result.val))
        else:
            v2_result = self.variant_two(val)

            if isinstance(v2_result, Ok):
                return Ok(Second(v2_result.val))
            else:
                return Err(
                    {
                        "variant 1": v1_result.val,
                        "variant 2": v2_result.val,
                    }
                )


@dataclass(init=False, frozen=True)
class OneOf3(Validator[Any, Either3[A, B, C], JSONValue]):
    variant_one: Validator[Any, A, JSONValue]
    variant_two: Validator[Any, B, JSONValue]
    variant_three: Validator[Any, C, JSONValue]

    def __init__(
        self,
        variant_one: Validator[Any, A, JSONValue],
        variant_two: Validator[Any, B, JSONValue],
        variant_three: Validator[Any, C, JSONValue],
    ) -> None:
        object.__setattr__(self, "variant_one", variant_one)
        object.__setattr__(self, "variant_two", variant_two)
        object.__setattr__(self, "variant_three", variant_three)

    def __call__(self, val: Any) -> Result[Either3[A, B, C], JSONValue]:
        v1_result = self.variant_one(val)

        if isinstance(v1_result, Ok):
            return Ok(First(v1_result.val))
        else:
            v2_result = self.variant_two(val)

            if isinstance(v2_result, Ok):
                return Ok(Second(v2_result.val))
            else:
                v3_result = self.variant_three(val)

                if isinstance(v3_result, Ok):
                    return Ok(Third(v3_result.val))
                else:
                    return Err(
                        {
                            "variant 1": v1_result.val,
                            "variant 2": v2_result.val,
                            "variant 3": v3_result.val,
                        }
                    )
