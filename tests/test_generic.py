import datetime
from decimal import Decimal

from koda import Err, Ok

from koda_validate import ExactValidator


def test_exactly() -> None:
    assert ExactValidator(5)(5) == Ok(5)
    assert ExactValidator(5)(4) == Err(["expected exactly 5 (int)"])
    assert ExactValidator("ok")("ok") == Ok("ok")
    assert ExactValidator("ok")("not ok") == Err(['expected exactly "ok" (str)'])
    assert ExactValidator(Decimal("1.25"))(Decimal("1.25")) == Ok(Decimal("1.25"))
    assert ExactValidator(Decimal("1.1"))(Decimal("5")) == Err(
        ["expected exactly 1.1 (Decimal)"]
    )
    assert ExactValidator(4.4)("5.5") == Err(["expected exactly 4.4 (float)"])
    assert ExactValidator(True)(True) == Ok(True)
    assert ExactValidator(False)(False) == Ok(False)
    assert ExactValidator(True)(False) == Err(["expected exactly True (bool)"])
