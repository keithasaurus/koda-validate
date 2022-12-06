import asyncio
from dataclasses import dataclass
from typing import Any, Optional, Tuple

import pytest

from koda_validate import (
    BoolValidator,
    ExactItemCount,
    FloatValidator,
    IntValidator,
    Invalid,
    Max,
    MaxItems,
    Min,
    MinItems,
    NTupleValidator,
    StringValidator,
    TupleHomogenousValidator,
    Valid,
)
from koda_validate._generics import A
from koda_validate.base import (
    BasicErr,
    CoercionErr,
    ErrType,
    IndexErrs,
    PredicateAsync,
    PredicateErrs,
    Processor,
    TypeErr,
)
from tests.utils import BasicNoneValidator


def test_tuple3() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    b_v = BoolValidator()
    n_v = BasicNoneValidator()
    validator = NTupleValidator.typed(fields=(s_v, i_v, b_v, n_v))
    assert validator({}) == Invalid(validator, {}, CoercionErr({list, tuple}, tuple))

    assert validator([]) == Invalid(validator, [], PredicateErrs([ExactItemCount(4)]))

    assert validator(["a", 1, False, None]) == Valid(("a", 1, False, None))

    assert validator(("a", 1, False, None)) == Valid(("a", 1, False, None))

    assert validator([1, "a", 7.42, 1]) == Invalid(
        validator,
        [1, "a", 7.42, 1],
        IndexErrs(
            {
                0: Invalid(s_v, 1, TypeErr(str)),
                1: Invalid(i_v, "a", TypeErr(int)),
                2: Invalid(b_v, 7.42, TypeErr(bool)),
                3: Invalid(n_v, 1, TypeErr(type(None))),
            },
        ),
    )

    def must_be_a_if_1_and_true(abc: Tuple[str, int, bool]) -> Optional[ErrType]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return None
            else:
                return BasicErr("must be a if int is 1 and bool is True")
        else:
            return None

    a1_validator = NTupleValidator.typed(
        fields=(s_v, i_v, b_v),
        validate_object=must_be_a_if_1_and_true,
    )

    assert a1_validator(["a", 1, True]) == Valid(("a", 1, True))
    assert a1_validator(["b", 1, True]) == Invalid(
        a1_validator, ("b", 1, True), BasicErr("must be a if int is 1 and bool is True")
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
        validator, {}, CoercionErr({list, tuple}, tuple)
    )

    assert await validator.validate_async([]) == Invalid(
        validator, [], PredicateErrs([ExactItemCount(4)])
    )

    assert await validator.validate_async(["a", 1, False, None]) == Valid(
        ("a", 1, False, None)
    )

    assert await validator.validate_async(("a", 1, False, None)) == Valid(
        ("a", 1, False, None)
    )

    assert await validator.validate_async([1, "a", 7.42, 1]) == Invalid(
        validator,
        [1, "a", 7.42, 1],
        IndexErrs(
            {
                0: Invalid(str_v, 1, TypeErr(str)),
                1: Invalid(int_v, "a", TypeErr(int)),
                2: Invalid(bool_v, 7.42, TypeErr(bool)),
                3: Invalid(none_v, 1, TypeErr(type(None))),
            },
        ),
    )

    def must_be_a_if_1_and_true(abc: Tuple[str, int, bool]) -> Optional[ErrType]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return None
            else:
                return BasicErr("must be a if int is 1 and bool is True")
        else:
            return None

    a1_validator = NTupleValidator.typed(
        fields=(str_v, int_v, bool_v),
        validate_object=must_be_a_if_1_and_true,
    )

    assert await a1_validator.validate_async(["a", 1, True]) == Valid(("a", 1, True))
    assert await a1_validator.validate_async(["b", 1, True]) == Invalid(
        a1_validator, ("b", 1, True), BasicErr("must be a if int is 1 and bool is True")
    )
    assert await a1_validator.validate_async(["b", 2, False]) == Valid(("b", 2, False))


def test_tuple_homogenous_validator() -> None:
    f_v = FloatValidator()
    tuple_v = TupleHomogenousValidator(f_v)
    assert tuple_v("a string") == Invalid(tuple_v, "a string", TypeErr(tuple))

    assert tuple_v((5.5, "something else")) == Invalid(
        tuple_v,
        (5.5, "something else"),
        IndexErrs(
            {1: Invalid(f_v, "something else", TypeErr(float))},
        ),
    )

    assert tuple_v((5.5, 10.1)) == Valid((5.5, 10.1))

    assert tuple_v(()) == Valid(())

    class RemoveLast(Processor[Tuple[Any, ...]]):
        def __call__(self, val: Tuple[Any, ...]) -> Tuple[Any, ...]:
            return val[:-1]

    t_p_p_validator = TupleHomogenousValidator(
        FloatValidator(Min(5.5)),
        predicates=[MinItems(1), MaxItems(3)],
        preprocessors=[RemoveLast()],
    )
    assert t_p_p_validator((10.1, 7.7, 2.2, 5, 0.0)) == Invalid(
        t_p_p_validator, (10.1, 7.7, 2.2, 5), PredicateErrs([MaxItems(3)])
    )

    n_v = TupleHomogenousValidator(BasicNoneValidator())

    assert n_v((None, None)) == Valid((None, None))

    assert n_v((None, 1)) == Invalid(
        n_v,
        (None, 1),
        IndexErrs({1: Invalid(n_v.item_validator, 1, TypeErr(type(None)))}),
    )


@pytest.mark.asyncio
async def test_tuple_homogenous_async() -> None:
    float_validator = FloatValidator()
    validator = TupleHomogenousValidator(float_validator)
    assert await validator.validate_async("a string") == Invalid(
        validator, "a string", TypeErr(tuple)
    )

    assert await validator.validate_async((5.5, "something else")) == Invalid(
        validator,
        (5.5, "something else"),
        IndexErrs(
            {1: Invalid(float_validator, "something else", TypeErr(float))},
        ),
    )

    assert await validator.validate_async((5.5, 10.1)) == Valid((5.5, 10.1))

    assert await validator.validate_async(()) == Valid(())

    t_validator = TupleHomogenousValidator(
        FloatValidator(Min(5.5)), predicates=[MinItems(1), MaxItems(3)]
    )
    assert await t_validator.validate_async((10.1, 7.7, 2.2, 5)) == Invalid(
        t_validator, (10.1, 7.7, 2.2, 5), PredicateErrs([MaxItems(3)])
    )

    n_v = TupleHomogenousValidator(BasicNoneValidator())

    assert await n_v.validate_async((None, None)) == Valid((None, None))

    assert await n_v.validate_async((None, 1)) == Invalid(
        n_v,
        (None, 1),
        IndexErrs({1: Invalid(n_v.item_validator, 1, TypeErr(type(None)))}),
    )


@pytest.mark.asyncio
async def test_list_validator_with_async_predicate_validator() -> None:
    @dataclass
    class SomeAsyncListCheck(PredicateAsync[Tuple[Any, ...]]):
        async def validate_async(self, val: Tuple[Any, ...]) -> bool:
            await asyncio.sleep(0.001)
            return len(val) == 1

    t_validator = TupleHomogenousValidator(
        StringValidator(), predicates_async=[SomeAsyncListCheck()]
    )
    assert await t_validator.validate_async(()) == Invalid(
        t_validator, (), PredicateErrs([SomeAsyncListCheck()])
    )

    assert await t_validator.validate_async(("hooray",)) == Valid(("hooray",))


@pytest.mark.asyncio
async def test_child_validator_async_is_used() -> None:
    @dataclass
    class SomeIntDBCheck(PredicateAsync[int]):
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

    assert await l_validator.validate_async((1, 1, 1)) == Invalid(
        l_validator, (1, 1), PredicateErrs([MaxItems(1)])
    )


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    list_validator = TupleHomogenousValidator(
        StringValidator(), predicates_async=[AsyncWait()]
    )
    with pytest.raises(AssertionError):
        list_validator(())


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
