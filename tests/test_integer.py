from koda import Err, Ok

from koda_validate import IntValidator, Max, Min, Predicate, Serializable


def test_integer() -> None:
    assert IntValidator()("a string") == Err(["expected an integer"])

    assert IntValidator()(5) == Ok(5)

    assert IntValidator()(True) == Err(["expected an integer"]), (
        "even though `bool`s are subclasses of ints in python, we wouldn't "
        "want to validate incoming data as ints if they are bools"
    )

    assert IntValidator()("5") == Err(["expected an integer"])

    assert IntValidator()(5.0) == Err(["expected an integer"])

    class DivisibleBy2(Predicate[int, Serializable]):
        def is_valid(self, val: int) -> bool:
            return val % 2 == 0

        def err(self, val: int) -> Serializable:
            return "must be divisible by 2"

    assert IntValidator(Min(2), Max(10), DivisibleBy2(),)(
        11
    ) == Err(["maximum allowed value is 10", "must be divisible by 2"])
