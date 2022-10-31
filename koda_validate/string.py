import re
from typing import Any, Final, List, Optional, Pattern

from koda import Err, Result

from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)
from koda_validate.utils import (
    _handle_processors_and_predicates,
    _handle_processors_and_predicates_async,
)

EXPECTED_STR_ERR: Final[Err[Serializable]] = Err(["expected a string"])


class StringValidator(Validator[Any, str, Serializable]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[str, Serializable],
        predicates_async: Optional[List[PredicateAsync[str, Serializable]]] = None,
        preprocessors: Optional[List[Processor[str]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Result[str, Serializable]:
        if isinstance(val, str):
            return _handle_processors_and_predicates(
                val, self.preprocessors, self.predicates
            )
        return EXPECTED_STR_ERR

    async def validate_async(self, val: Any) -> Result[str, Serializable]:
        if isinstance(val, str):
            return await _handle_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_STR_ERR


class RegexPredicate(Predicate[str, Serializable]):
    __slots__ = ("pattern",)
    __match_args__ = ("pattern",)

    def __init__(self, pattern: Pattern[str]) -> None:
        self.pattern: Pattern[str] = pattern

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err(self, val: str) -> str:
        return rf"must match pattern {self.pattern.pattern}"


class EmailPredicate(Predicate[str, Serializable]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err(self, val: str) -> str:
        return "expected a valid email address"


BLANK_STRING_MSG: Final[str] = "cannot be blank"


class NotBlank(Predicate[str, Serializable]):
    def is_valid(self, val: str) -> bool:
        return len(val.strip()) != 0

    def err(self, val: str) -> Serializable:
        return BLANK_STRING_MSG


not_blank = NotBlank()


class MaxLength(Predicate[str, Serializable]):
    __match_args__ = ("length",)
    __slots__ = ("length",)

    def __init__(self, length: int):
        self.length = length

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err(self, val: str) -> Serializable:
        return f"maximum allowed length is {self.length}"


class MinLength(Predicate[str, Serializable]):
    __match_args__ = ("length",)
    __slots__ = ("length",)

    def __init__(self, length: int):
        self.length = length

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err(self, val: str) -> str:
        return f"minimum allowed length is {self.length}"


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
