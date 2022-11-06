from typing import Any

from koda_validate.typedefs import Invalid, Validated


def assert_same_error_type_with_same_message(
    error_1: Validated[Any, Exception], error_2: Validated[Any, Exception]
) -> None:
    """
    There may be a better/more concise way to compare exceptions
    """
    assert isinstance(error_1, Invalid)
    assert isinstance(error_2, Invalid)
    assert type(error_1.val) == type(error_2.val)  # noqa: E721
    assert error_1.val.args == error_2.val.args
