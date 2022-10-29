from typing import Tuple

from koda import Err, Ok, Result

from koda_validate import (
    BooleanValidator,
    IntValidator,
    Serializable,
    StringValidator,
    TupleValidator,
)


def test_tuple2() -> None:
    assert TupleValidator(StringValidator(), IntValidator())({}) == Err(
        {"__container__": ["expected list or tuple of length 2"]}
    )

    assert TupleValidator(StringValidator(), IntValidator())([]) == Err(
        {"__container__": ["expected list or tuple of length 2"]}
    )

    assert TupleValidator(StringValidator(), IntValidator())(["a", 1]) == Ok(("a", 1))
    assert TupleValidator(StringValidator(), IntValidator())(("a", 1)) == Ok(("a", 1))

    assert TupleValidator(StringValidator(), IntValidator())([1, "a"]) == Err(
        {"0": ["expected a string"], "1": ["expected an integer"]}
    )

    def must_be_a_if_integer_is_1(
        ab: Tuple[str, int]
    ) -> Result[Tuple[str, int], Serializable]:
        if ab[1] == 1:
            if ab[0] == "a":
                return Ok(ab)
            else:
                return Err({"__container__": ["must be a if int is 1"]})
        else:
            return Ok(ab)

    a1_validator = TupleValidator(
        StringValidator(), IntValidator(), must_be_a_if_integer_is_1
    )

    assert a1_validator(["a", 1]) == Ok(("a", 1))
    assert a1_validator(["b", 1]) == Err({"__container__": ["must be a if int is 1"]})
    assert a1_validator(["b", 2]) == Ok(("b", 2))


def test_tuple3() -> None:
    assert TupleValidator(StringValidator(), IntValidator(), BooleanValidator())(
        {}
    ) == Err({"__container__": ["expected list or tuple of length 3"]})

    assert TupleValidator(StringValidator(), IntValidator(), BooleanValidator())(
        []
    ) == Err({"__container__": ["expected list or tuple of length 3"]})

    assert TupleValidator(StringValidator(), IntValidator(), BooleanValidator())(
        ["a", 1, False]
    ) == Ok(("a", 1, False))

    assert TupleValidator(StringValidator(), IntValidator(), BooleanValidator())(
        ("a", 1, False)
    ) == Ok(("a", 1, False))

    assert TupleValidator(StringValidator(), IntValidator(), BooleanValidator())(
        [1, "a", 7.42]
    ) == Err(
        {
            "0": ["expected a string"],
            "1": ["expected an integer"],
            "2": ["expected a boolean"],
        }
    )

    def must_be_a_if_1_and_true(
        abc: Tuple[str, int, bool]
    ) -> Result[Tuple[str, int, bool], Serializable]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return Ok(abc)
            else:
                return Err({"__container__": ["must be a if int is 1 and bool is True"]})
        else:
            return Ok(abc)

    a1_validator = TupleValidator(
        StringValidator(), IntValidator(), BooleanValidator(), must_be_a_if_1_and_true
    )

    assert a1_validator(["a", 1, True]) == Ok(("a", 1, True))
    assert a1_validator(["b", 1, True]) == Err(
        {"__container__": ["must be a if int is 1 and bool is True"]}
    )
    assert a1_validator(["b", 2, False]) == Ok(("b", 2, False))
