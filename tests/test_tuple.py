import asyncio
from dataclasses import dataclass
from typing import Any, Tuple

import pytest

from koda_validate import (
    BoolValidator,
    ExactItemCount,
    FloatValidator,
    IntValidator,
    MaxItems,
    Min,
    MinItems,
    StringValidator,
)
from koda_validate._generics import A
from koda_validate.base import (
    InvalidCoercion,
    InvalidCustom,
    InvalidIterable,
    InvalidType,
    PredicateAsync,
    Processor,
    ValidationResult,
)
from koda_validate.tuple import Tuple2Validator, Tuple3Validator, TupleHomogenousValidator
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


def test_tuple_homogenous_validator() -> None:
    assert TupleHomogenousValidator(FloatValidator())("a string") == Invalid(
        InvalidType(tuple, "expected a tuple")
    )

    assert TupleHomogenousValidator(FloatValidator())((5.5, "something else")) == Invalid(
        InvalidIterable(
            {1: InvalidType(float, "expected a float")},
        )
    )

    assert TupleHomogenousValidator(FloatValidator())((5.5, 10.1)) == Valid((5.5, 10.1))

    assert TupleHomogenousValidator(FloatValidator())(()) == Valid(())

    class RemoveLast(Processor[Tuple[Any, ...]]):
        def __call__(self, val: Tuple[Any, ...]) -> Tuple[Any, ...]:
            return val[:-1]

    assert TupleHomogenousValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
        preprocessors=[RemoveLast()],
    )((10.1, 7.7, 2.2, 5, 0.0)) == Invalid([MaxItems(3)])


@pytest.mark.asyncio
async def test_list_async() -> None:
    assert await TupleHomogenousValidator(FloatValidator()).validate_async(
        "a string"
    ) == Invalid(InvalidType(tuple, "expected a tuple"))

    assert await TupleHomogenousValidator(FloatValidator()).validate_async(
        (5.5, "something else")
    ) == Invalid(
        InvalidIterable(
            {1: InvalidType(float, "expected a float")},
        )
    )

    assert await TupleHomogenousValidator(FloatValidator()).validate_async(
        (5.5, 10.1)
    ) == Valid((5.5, 10.1))

    assert await TupleHomogenousValidator(FloatValidator()).validate_async(()) == Valid(
        ()
    )

    assert await TupleHomogenousValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    ).validate_async((10.1, 7.7, 2.2, 5)) == Invalid([MaxItems(3)])


@pytest.mark.asyncio
async def test_list_validator_with_async_predicate_validator() -> None:
    @dataclass
    class SomeAsyncListCheck(PredicateAsync[Tuple[Any, ...]]):
        err_message = "not len 1"

        async def validate_async(self, val: Tuple[Any, ...]) -> bool:
            await asyncio.sleep(0.001)
            return len(val) == 1

    assert await TupleHomogenousValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    ).validate_async(()) == Invalid([SomeAsyncListCheck()])

    assert await TupleHomogenousValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    ).validate_async(("hooray",)) == Valid(("hooray",))


@pytest.mark.asyncio
async def test_child_validator_async_is_used() -> None:
    @dataclass
    class SomeIntDBCheck(PredicateAsync[int]):
        err_message = "not equal to three"

        async def validate_async(self, val: int) -> bool:
            await asyncio.sleep(0.001)
            return val == 3

    class PopFrontOffList(Processor[Tuple[Any, ...]]):
        def __call__(self, val: Tuple[Any, ...]) -> Tuple[Any, ...]:
            return val[1:]

    l_validator = TupleHomogenousValidator(
        IntValidator(Min(2), predicates_async=[SomeIntDBCheck()]),
        predicates=[MaxItems(1)],
        preprocessors=[PopFrontOffList()],
    )

    assert await l_validator.validate_async((1, 3)) == Valid((3,))

    assert await l_validator.validate_async((1, 1, 1)) == Invalid([MaxItems(1)])


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        err_message = "should always succeed??"

        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    list_validator = TupleHomogenousValidator(
        StringValidator(), predicates_async=[AsyncWait()]
    )
    with pytest.raises(AssertionError):
        list_validator(())
