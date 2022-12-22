import asyncio
from dataclasses import dataclass
from typing import Any, Optional, Tuple

import pytest

from koda_validate import (
    BoolValidator,
    CoercionErr,
    ExactItemCount,
    FloatValidator,
    IndexErrs,
    IntValidator,
    Invalid,
    Max,
    MaxItems,
    MaxLength,
    Min,
    MinItems,
    MinLength,
    NTupleValidator,
    PredicateErrs,
    SerializableErr,
    StringValidator,
    TypeErr,
    UniformTupleValidator,
    Valid,
)
from koda_validate._generics import A
from koda_validate.base import PredicateAsync
from koda_validate.errors import ErrType
from tests.utils import BasicNoneValidator


def test_tuple3() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    b_v = BoolValidator()
    n_v = BasicNoneValidator()
    validator = NTupleValidator.typed(fields=(s_v, i_v, b_v, n_v))
    assert validator({}) == Invalid(CoercionErr({list, tuple}, tuple), {}, validator)

    assert validator([]) == Invalid(PredicateErrs([ExactItemCount(4)]), [], validator)

    assert validator(["a", 1, False, None]) == Valid(("a", 1, False, None))

    assert validator(("a", 1, False, None)) == Valid(("a", 1, False, None))

    assert validator([1, "a", 7.42, 1]) == Invalid(
        IndexErrs(
            {
                0: Invalid(TypeErr(str), 1, s_v),
                1: Invalid(TypeErr(int), "a", i_v),
                2: Invalid(TypeErr(bool), 7.42, b_v),
                3: Invalid(TypeErr(type(None)), 1, n_v),
            },
        ),
        [1, "a", 7.42, 1],
        validator,
    )

    def must_be_a_if_1_and_true(abc: Tuple[str, int, bool]) -> Optional[ErrType]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return None
            else:
                return SerializableErr("must be a if int is 1 and bool is True")
        else:
            return None

    a1_validator = NTupleValidator.typed(
        fields=(s_v, i_v, b_v),
        validate_object=must_be_a_if_1_and_true,
    )

    assert a1_validator(["a", 1, True]) == Valid(("a", 1, True))
    assert a1_validator(["b", 1, True]) == Invalid(
        SerializableErr("must be a if int is 1 and bool is True"),
        ("b", 1, True),
        a1_validator,
    )
    assert a1_validator(["b", 2, False]) == Valid(("b", 2, False))


@pytest.mark.asyncio
async def test_tuple3_async() -> None:
    str_v = StringValidator()
    int_v = IntValidator()
    bool_v = BoolValidator()
    none_v = BasicNoneValidator()
    validator = NTupleValidator.typed(fields=(str_v, int_v, bool_v, none_v))
    assert await validator.validate_async({}) == Invalid(
        CoercionErr({list, tuple}, tuple), {}, validator
    )

    assert await validator.validate_async([]) == Invalid(
        PredicateErrs([ExactItemCount(4)]), [], validator
    )

    assert await validator.validate_async(["a", 1, False, None]) == Valid(
        ("a", 1, False, None)
    )

    assert await validator.validate_async(("a", 1, False, None)) == Valid(
        ("a", 1, False, None)
    )

    assert await validator.validate_async([1, "a", 7.42, 1]) == Invalid(
        IndexErrs(
            {
                0: Invalid(TypeErr(str), 1, str_v),
                1: Invalid(TypeErr(int), "a", int_v),
                2: Invalid(TypeErr(bool), 7.42, bool_v),
                3: Invalid(TypeErr(type(None)), 1, none_v),
            },
        ),
        [1, "a", 7.42, 1],
        validator,
    )

    def must_be_a_if_1_and_true(abc: Tuple[str, int, bool]) -> Optional[ErrType]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return None
            else:
                return SerializableErr("must be a if int is 1 and bool is True")
        else:
            return None

    a1_validator = NTupleValidator.typed(
        fields=(str_v, int_v, bool_v),
        validate_object=must_be_a_if_1_and_true,
    )

    assert await a1_validator.validate_async(["a", 1, True]) == Valid(("a", 1, True))
    assert await a1_validator.validate_async(["b", 1, True]) == Invalid(
        SerializableErr("must be a if int is 1 and bool is True"),
        ("b", 1, True),
        a1_validator,
    )
    assert await a1_validator.validate_async(["b", 2, False]) == Valid(("b", 2, False))


def test_tuple_homogenous_validator() -> None:
    f_v = FloatValidator()
    tuple_v = UniformTupleValidator(f_v)
    assert tuple_v("a string") == Invalid(TypeErr(tuple), "a string", tuple_v)

    assert tuple_v((5.5, "something else")) == Invalid(
        IndexErrs(
            {1: Invalid(TypeErr(float), "something else", f_v)},
        ),
        (5.5, "something else"),
        tuple_v,
    )

    assert tuple_v((5.5, 10.1)) == Valid((5.5, 10.1))

    assert tuple_v(()) == Valid(())

    t_p_p_validator = UniformTupleValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
    )
    assert t_p_p_validator((10.1, 7.7, 2.2, 5, 0.0)) == Invalid(
        PredicateErrs([MaxItems(3)]), (10.1, 7.7, 2.2, 5, 0.0), t_p_p_validator
    )

    n_v = UniformTupleValidator(BasicNoneValidator())

    assert n_v((None, None)) == Valid((None, None))

    assert n_v((None, 1)) == Invalid(
        IndexErrs({1: Invalid(TypeErr(type(None)), 1, n_v.item_validator)}),
        (None, 1),
        n_v,
    )


@pytest.mark.asyncio
async def test_tuple_homogenous_async() -> None:
    float_validator = FloatValidator()
    validator = UniformTupleValidator(float_validator)
    assert await validator.validate_async("a string") == Invalid(
        TypeErr(tuple), "a string", validator
    )

    assert await validator.validate_async((5.5, "something else")) == Invalid(
        IndexErrs(
            {1: Invalid(TypeErr(float), "something else", float_validator)},
        ),
        (5.5, "something else"),
        validator,
    )

    assert await validator.validate_async((5.5, 10.1)) == Valid((5.5, 10.1))

    assert await validator.validate_async(()) == Valid(())

    t_validator = UniformTupleValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    )
    assert await t_validator.validate_async((10.1, 7.7, 2.2, 5)) == Invalid(
        PredicateErrs([MaxItems(3)]), (10.1, 7.7, 2.2, 5), t_validator
    )

    n_v = UniformTupleValidator(BasicNoneValidator())

    assert await n_v.validate_async((None, None)) == Valid((None, None))

    assert await n_v.validate_async((None, 1)) == Invalid(
        IndexErrs({1: Invalid(TypeErr(type(None)), 1, n_v.item_validator)}),
        (None, 1),
        n_v,
    )


@dataclass
class SomeAsyncTupleHCheck(PredicateAsync[Tuple[Any, ...]]):
    async def validate_async(self, val: Tuple[Any, ...]) -> bool:
        await asyncio.sleep(0.001)
        return len(val) == 1


@pytest.mark.asyncio
async def test_tuple_h_validator_with_async_predicate_validator() -> None:

    t_validator = UniformTupleValidator(
        StringValidator(), predicates_async=[SomeAsyncTupleHCheck()]
    )
    assert await t_validator.validate_async(()) == Invalid(
        PredicateErrs([SomeAsyncTupleHCheck()]), (), t_validator
    )

    assert await t_validator.validate_async(("hooray",)) == Valid(("hooray",))


@pytest.mark.asyncio
async def test_child_validator_async_is_used() -> None:
    @dataclass
    class SomeIntDBCheck(PredicateAsync[int]):
        async def validate_async(self, val: int) -> bool:
            await asyncio.sleep(0.001)
            return val == 3

    l_validator = UniformTupleValidator(
        IntValidator(Min(2), predicates_async=[SomeIntDBCheck()]),
        predicates=[MaxItems(1)],
    )

    assert await l_validator.validate_async((3,)) == Valid((3,))

    assert await l_validator.validate_async((1,)) == Invalid(
        IndexErrs(
            {
                0: Invalid(
                    PredicateErrs([Min(2), SomeIntDBCheck()]),
                    1,
                    l_validator.item_validator,
                )
            }
        ),
        (1,),
        l_validator,
    )


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    tuple_h_validator = UniformTupleValidator(
        StringValidator(), predicates_async=[AsyncWait()]
    )
    with pytest.raises(AssertionError):
        tuple_h_validator(())


def test_repr_n_tuple() -> None:
    v = NTupleValidator.typed(fields=(StringValidator(), IntValidator(Max(5))))
    assert repr(v) == (
        "NTupleValidator(fields=(StringValidator(), IntValidator(Max(maximum=5, "
        "exclusive_maximum=False))))"
    )

    def validate_function(t: Tuple[str, int]) -> Optional[ErrType]:
        return None

    v_2 = NTupleValidator.typed(
        fields=(StringValidator(), IntValidator(Max(5))),
        validate_object=validate_function,
    )
    assert repr(v_2) == (
        "NTupleValidator(fields=(StringValidator(), IntValidator(Max(maximum=5, "
        f"exclusive_maximum=False))), validate_object={repr(validate_function)})"
    )


def test_eq() -> None:
    v_0 = NTupleValidator.typed(fields=(StringValidator(), IntValidator()))
    v_1 = NTupleValidator.typed(fields=(StringValidator(), IntValidator(Max(5))))
    assert v_0 != v_1
    v_2 = NTupleValidator.typed(fields=(StringValidator(), IntValidator(Max(5))))
    assert v_1 == v_2

    def fn1(t: Tuple[str, int]) -> Optional[ErrType]:
        return None

    def fn2(t: Tuple[str, int]) -> Optional[ErrType]:
        return None

    v_3 = NTupleValidator.typed(
        fields=(StringValidator(), IntValidator(Max(5))), validate_object=fn1
    )
    assert v_2 != v_3
    v_4 = NTupleValidator.typed(
        fields=(StringValidator(), IntValidator(Max(5))), validate_object=fn2
    )
    assert v_3 != v_4
    v_5 = NTupleValidator.typed(
        fields=(StringValidator(), IntValidator(Max(5))), validate_object=fn2
    )
    assert v_4 == v_5


def test_tuple_homogenous_repr() -> None:
    s = UniformTupleValidator(StringValidator())
    assert repr(s) == "UniformTupleValidator(StringValidator())"

    s_len = UniformTupleValidator(StringValidator(MinLength(1), MaxLength(5)))
    assert (
        repr(s_len) == "UniformTupleValidator(StringValidator("
        "MinLength(length=1), MaxLength(length=5)))"
    )

    s_all = UniformTupleValidator(
        IntValidator(),
        predicates=[MinItems(5)],
        predicates_async=[SomeAsyncTupleHCheck()],
    )

    assert (
        repr(s_all) == "UniformTupleValidator(IntValidator(), "
        "predicates=[MinItems(item_count=5)], "
        "predicates_async=[SomeAsyncTupleHCheck()])"
    )


def test_tuple_h_tuple_homogenous_equivalence() -> None:
    l_1 = UniformTupleValidator(StringValidator())
    l_2 = UniformTupleValidator(StringValidator())
    assert l_1 == l_2
    l_3 = UniformTupleValidator(IntValidator())
    assert l_2 != l_3

    l_pred_1 = UniformTupleValidator(StringValidator(), predicates=[MaxItems(1)])
    assert l_pred_1 != l_1
    l_pred_2 = UniformTupleValidator(StringValidator(), predicates=[MaxItems(1)])
    assert l_pred_2 == l_pred_1

    l_pred_async_1 = UniformTupleValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[SomeAsyncTupleHCheck()],
    )
    assert l_pred_async_1 != l_pred_1
    l_pred_async_2 = UniformTupleValidator(
        StringValidator(),
        predicates=[MaxItems(1)],
        predicates_async=[SomeAsyncTupleHCheck()],
    )
    assert l_pred_async_1 == l_pred_async_2
