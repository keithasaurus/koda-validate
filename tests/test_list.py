from koda import Err, Ok

from koda_validate import MaxItems, MinItems, unique_items
from koda_validate.float import FloatValidator
from koda_validate.generic import Min
from koda_validate.list import ListValidator, MaxItems, MinItems


def test_list_validator() -> None:
    assert ListValidator(FloatValidator())("a string") == Err(
        {"__container__": ["expected a list"]}
    )

    assert ListValidator(FloatValidator())([5.5, "something else"]) == Err(
        {"1": ["expected a float"]}
    )

    assert ListValidator(FloatValidator())([5.5, 10.1]) == Ok([5.5, 10.1])

    assert ListValidator(FloatValidator())([]) == Ok([])

    assert ListValidator(FloatValidator(Min(5.5)), MinItems(1), MaxItems(3))(
        [10.1, 7.7, 2.2, 5]
    ) == Err(
        {
            "2": ["minimum allowed value is 5.5"],
            "3": ["expected a float"],
            "__container__": ["maximum allowed length is 3"],
        }
    )


def test_max_items() -> None:
    assert MaxItems(0)([]) == Ok([])

    assert MaxItems(5)([1, 2, 3]) == Ok([1, 2, 3])

    assert MaxItems(5)(["a", "b", "c", "d", "e", "fghij"]) == Err(
        "maximum allowed length is 5"
    )


def test_min_items() -> None:
    assert MinItems(0)([]) == Ok([])

    assert MinItems(3)([1, 2, 3]) == Ok([1, 2, 3])

    assert MinItems(3)([1, 2]) == Err("minimum allowed length is 3")


def test_unique_items() -> None:
    unique_fail = Err("all items must be unique")
    assert unique_items([1, 2, 3]) == Ok([1, 2, 3])
    assert unique_items([1, 1]) == unique_fail
    assert unique_items([1, [], []]) == unique_fail
    assert unique_items([[], [1], [2]]) == Ok([[], [1], [2]])
    assert unique_items([{"something": {"a": 1}}, {"something": {"a": 1}}]) == unique_fail
