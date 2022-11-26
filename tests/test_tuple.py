from typing import Tuple

import pytest

from koda_validate import BoolValidator, ExactItemCount, IntValidator, StringValidator
from koda_validate.base import (
    InvalidCoercion,
    InvalidCustom,
    InvalidIterable,
    InvalidType,
    ValidationResult,
)
from koda_validate.tuple import Tuple2Validator, Tuple3Validator
from koda_validate.validated import Invalid, Valid


def test_tuple2() -> None:
    assert Tuple2Validator(StringValidator(), IntValidator())({}) == Invalid(
        InvalidCoercion([list, tuple], tuple, "expected a list or tuple")
    )

    assert Tuple2Validator(StringValidator(), IntValidator())([]) == Invalid(
        [ExactItemCount(2)]
    )

    assert Tuple2Validator(StringValidator(), IntValidator())(["a", 1]) == Valid(("a", 1))
    assert Tuple2Validator(StringValidator(), IntValidator())(("a", 1)) == Valid(("a", 1))

    assert Tuple2Validator(StringValidator(), IntValidator())([1, "a"]) == Invalid(
        InvalidIterable(
            {
                0: InvalidType(str, "expected a string"),
                1: InvalidType(int, "expected an integer"),
            }
        )
    )

    def must_be_a_if_integer_is_1(
        ab: Tuple[str, int]
    ) -> ValidationResult[Tuple[str, int]]:
        if ab[1] == 1:
            if ab[0] == "a":
                return Valid(ab)
            else:
                return Invalid(InvalidCustom("must be a if int is 1 and bool is True"))
        else:
            return Valid(ab)

    a1_validator = Tuple2Validator(
        StringValidator(),
        IntValidator(),
        must_be_a_if_integer_is_1,
    )

    assert a1_validator(["a", 1]) == Valid(("a", 1))
    assert a1_validator(["b", 1]) == Invalid(
        InvalidCustom("must be a if int is 1 and bool is True")
    )
    assert a1_validator(["b", 2]) == Valid(("b", 2))


@pytest.mark.asyncio
async def test_tuple2_async() -> None:
    assert await Tuple2Validator(StringValidator(), IntValidator()).validate_async(
        {}
    ) == Invalid(InvalidCoercion([list, tuple], tuple, "expected a list or tuple"))

    assert await Tuple2Validator(StringValidator(), IntValidator()).validate_async(
        []
    ) == Invalid([ExactItemCount(2)])

    assert await Tuple2Validator(StringValidator(), IntValidator()).validate_async(
        ["a", 1]
    ) == Valid(("a", 1))
    assert await Tuple2Validator(StringValidator(), IntValidator()).validate_async(
        ("a", 1)
    ) == Valid(("a", 1))

    assert await Tuple2Validator(StringValidator(), IntValidator()).validate_async(
        [1, "a"]
    ) == Invalid(
        InvalidIterable(
            {
                0: InvalidType(str, "expected a string"),
                1: InvalidType(int, "expected an integer"),
            }
        )
    )

    def must_be_a_if_integer_is_1(
        ab: Tuple[str, int]
    ) -> ValidationResult[Tuple[str, int]]:
        if ab[1] == 1:
            if ab[0] == "a":
                return Valid(ab)
            else:
                return Invalid(InvalidCustom("must be a if int is 1"))
        else:
            return Valid(ab)

    a1_validator = Tuple2Validator(
        StringValidator(),
        IntValidator(),
        must_be_a_if_integer_is_1,
    )

    assert await a1_validator.validate_async(["a", 1]) == Valid(("a", 1))
    assert await a1_validator.validate_async(["b", 1]) == Invalid(
        InvalidCustom("must be a if int is 1")
    )
    assert await a1_validator.validate_async(["b", 2]) == Valid(("b", 2))


def test_tuple3() -> None:
    assert Tuple3Validator(StringValidator(), IntValidator(), BoolValidator())(
        {}
    ) == Invalid(InvalidCoercion([list, tuple], tuple, "expected a list or tuple"))

    assert Tuple3Validator(StringValidator(), IntValidator(), BoolValidator())(
        []
    ) == Invalid([ExactItemCount(3)])

    assert Tuple3Validator(StringValidator(), IntValidator(), BoolValidator())(
        ["a", 1, False]
    ) == Valid(("a", 1, False))

    assert Tuple3Validator(StringValidator(), IntValidator(), BoolValidator())(
        ("a", 1, False)
    ) == Valid(("a", 1, False))

    assert Tuple3Validator(StringValidator(), IntValidator(), BoolValidator())(
        [1, "a", 7.42]
    ) == Invalid(
        InvalidIterable(
            {
                0: InvalidType(str, "expected a string"),
                1: InvalidType(int, "expected an integer"),
                2: InvalidType(bool, "expected a boolean"),
            }
        )
    )

    def must_be_a_if_1_and_true(
        abc: Tuple[str, int, bool]
    ) -> ValidationResult[Tuple[str, int, bool]]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return Valid(abc)
            else:
                return Invalid(InvalidCustom("must be a if int is 1 and bool is True"))
        else:
            return Valid(abc)

    a1_validator = Tuple3Validator(
        StringValidator(),
        IntValidator(),
        BoolValidator(),
        must_be_a_if_1_and_true,
    )

    assert a1_validator(["a", 1, True]) == Valid(("a", 1, True))
    assert a1_validator(["b", 1, True]) == Invalid(
        InvalidCustom("must be a if int is 1 and bool is True")
    )
    assert a1_validator(["b", 2, False]) == Valid(("b", 2, False))


@pytest.mark.asyncio
async def test_tuple3_async() -> None:
    assert await Tuple3Validator(
        StringValidator(), IntValidator(), BoolValidator()
    ).validate_async({}) == Invalid(
        InvalidCoercion([list, tuple], tuple, "expected a list or tuple")
    )

    assert await Tuple3Validator(
        StringValidator(), IntValidator(), BoolValidator()
    ).validate_async([]) == Invalid([ExactItemCount(3)])

    assert await Tuple3Validator(
        StringValidator(), IntValidator(), BoolValidator()
    ).validate_async(["a", 1, False]) == Valid(("a", 1, False))

    assert await Tuple3Validator(
        StringValidator(), IntValidator(), BoolValidator()
    ).validate_async(("a", 1, False)) == Valid(("a", 1, False))

    assert await Tuple3Validator(
        StringValidator(), IntValidator(), BoolValidator()
    ).validate_async([1, "a", 7.42]) == Invalid(
        InvalidIterable(
            {
                0: InvalidType(str, "expected a string"),
                1: InvalidType(int, "expected an integer"),
                2: InvalidType(bool, "expected a boolean"),
            }
        )
    )

    def must_be_a_if_1_and_true(
        abc: Tuple[str, int, bool]
    ) -> ValidationResult[Tuple[str, int, bool]]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return Valid(abc)
            else:
                return Invalid(InvalidCustom("must be a if int is 1 and bool is True"))
        else:
            return Valid(abc)

    a1_validator = Tuple3Validator(
        StringValidator(),
        IntValidator(),
        BoolValidator(),
        must_be_a_if_1_and_true,
    )

    assert await a1_validator.validate_async(["a", 1, True]) == Valid(("a", 1, True))
    assert await a1_validator.validate_async(["b", 1, True]) == Invalid(
        InvalidCustom("must be a if int is 1 and bool is True")
    )
    assert await a1_validator.validate_async(["b", 2, False]) == Valid(("b", 2, False))
