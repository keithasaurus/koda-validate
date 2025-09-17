from koda_validate.typehints import get_typehint_validator
from koda_validate import Valid


def test_get_typehint_validator_readonly_typeddict() -> None:
    from typing import ReadOnly, TypedDict

    class UserInfo(TypedDict):
        name: ReadOnly[str]  # Read-only field
        age: int  # Mutable field
        email: ReadOnly[str]  # Another read-only field

    validator = get_typehint_validator(UserInfo)

    # Should create a TypedDictValidator that handles ReadOnly fields
    from koda_validate.typeddict import TypedDictValidator
    assert isinstance(validator, TypedDictValidator)

    # Test validation works normally
    result = validator({
        "name": "John",
        "age": 30,
        "email": "john@example.com"
    })
    assert isinstance(result, Valid)
