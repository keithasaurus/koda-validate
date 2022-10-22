from koda import Err, Ok

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
