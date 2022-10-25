from koda import Err, Ok

from koda_validate import BooleanValidator, Predicate, Serializable


def test_boolean() -> None:
    assert BooleanValidator()("a string") == Err(["expected a boolean"])

    assert BooleanValidator()(True) == Ok(True)

    assert BooleanValidator()(False) == Ok(False)

    class RequireTrue(Predicate[bool, Serializable]):
        def is_valid(self, val: bool) -> bool:
            return val is True

        def err(self, val: bool) -> Serializable:
            return "must be true"

    assert BooleanValidator(RequireTrue())(False) == Err(["must be true"])

    assert BooleanValidator()(1) == Err(["expected a boolean"])
