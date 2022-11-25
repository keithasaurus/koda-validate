import re
from dataclasses import dataclass
from typing import Any, Final, Literal, Pattern, Tuple

from koda_validate.base import (
    InvalidType,
    Predicate,
    Processor,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)

STRING_TYPE_ERR: Final[InvalidType] = InvalidType(str, "expected a string")

EXPECTED_STR_ERR: Final[Tuple[Literal[False], ValidationErr]] = (False, STRING_TYPE_ERR)


class StringValidator(_ToTupleValidatorUnsafe[Any, str]):
    def coerce_to_type(self, val: str) -> _ResultTupleUnsafe:
        if type(val) is str:
            return True, val
        else:
            return False, STRING_TYPE_ERR


@dataclass(init=False)
class RegexPredicate(Predicate[str]):
    pattern: Pattern[str]

    def __init__(self, pattern: Pattern[str]) -> None:
        self.err_message = rf"must match pattern {pattern.pattern}"
        self.pattern: Pattern[str] = pattern

    def __call__(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None


EXPECTED_EMAIL_ADDRESS: Final[str] = "expected a valid email address"


@dataclass
class EmailPredicate(Predicate[str]):
    err_message = EXPECTED_EMAIL_ADDRESS
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def __call__(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None


BLANK_STRING_MSG: Final[str] = "cannot be blank"


@dataclass
class NotBlank(Predicate[str]):
    err_message: str = BLANK_STRING_MSG

    def __call__(self, val: str) -> bool:
        return len(val.strip()) != 0


not_blank = NotBlank()


@dataclass(init=False)
class MaxLength(Predicate[str]):
    length: int

    def __init__(self, length: int) -> None:
        self.err_message = f"maximum allowed length is {length}"
        self.length: int = length

    def __call__(self, val: str) -> bool:
        return len(val) <= self.length


@dataclass(init=False)
class MinLength(Predicate[str]):
    length: int

    def __init__(self, length: int) -> None:
        self.err_message = f"minimum allowed length is {length}"
        self.length = length

    def __call__(self, val: str) -> bool:
        return len(val) >= self.length


class Strip(Processor[str]):
    def __call__(self, val: str) -> str:
        return val.strip()


strip = Strip()


class UpperCase(Processor[str]):
    def __call__(self, val: str) -> str:
        return val.upper()


upper_case = UpperCase()


class LowerCase(Processor[str]):
    def __call__(self, val: str) -> str:
        return val.lower()


lower_case = LowerCase()
