from koda import Err, Ok

from koda_validate.float import FloatValidator
from koda_validate.generic import Max, Min
from koda_validate.typedefs import Predicate, Serializable


def test_float() -> None:
    assert FloatValidator()("a string") == Err(["expected a float"])

    assert FloatValidator()(5.5) == Ok(5.5)

    assert FloatValidator()(4) == Err(["expected a float"])

    assert FloatValidator(Max(500.0))(503.0) == Err(["maximum allowed value is 500.0"])

    assert FloatValidator(Max(500.0))(3.5) == Ok(3.5)

    assert FloatValidator(Min(5.0))(4.999) == Err(["minimum allowed value is 5.0"])

    assert FloatValidator(Min(5.0))(5.0) == Ok(5.0)

    class MustHaveAZeroSomewhere(Predicate[float, Serializable]):
        def is_valid(self, val: float) -> bool:
            for char in str(val):
                if char == "0":
                    return True
            else:
                return False

        def err_message(self, val: float) -> Serializable:
            return "There should be a zero in the number"

    assert FloatValidator(Min(2.5), Max(4.0), MustHaveAZeroSomewhere())(5.5) == Err(
        ["maximum allowed value is 4.0", "There should be a zero in the number"]
    )
