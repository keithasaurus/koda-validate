import re
from functools import partial
from typing import Any, Final, List, Optional, Pattern

from koda import Err, Ok, Result

from koda_validate._internals import (
    _handle_scalar_predicates,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)

EXPECTED_STR_ERR: Final[Err[Serializable]] = Err(["expected a string"])


class StringValidator(Validator[Any, str, Serializable]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("_fast_pred", "predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[str, Serializable],
        predicates_async: Optional[List[PredicateAsync[str, Serializable]]] = None,
        preprocessors: Optional[List[Processor[str]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors
        self._fast_pred = (
            partial(_handle_scalar_predicates, predicates) if self.predicates else Ok
        )

    def __call__(self, val: Any) -> Result[str, Serializable]:
        if isinstance(val, str):
            if self.preprocessors is not None:
                for proc in self.preprocessors:
                    val = proc(val)

            return self._fast_pred(val)  # type: ignore

        return EXPECTED_STR_ERR

    async def validate_async(self, val: Any) -> Result[str, Serializable]:
        if isinstance(val, str):
            # todo: make this faster, like sync?
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_STR_ERR


class RegexPredicate(Predicate[str, Serializable]):
    __slots__ = ("pattern",)
    __match_args__ = ("pattern", "_err")

    def __init__(self, pattern: Pattern[str]) -> None:
        self.pattern: Pattern[str] = pattern
        self._err = rf"must match pattern {self.pattern.pattern}"

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err(self, val: str) -> str:
        return self._err


EXPECTED_EMAIL_ADDRESS: Final[str] = "expected a valid email address"


class EmailPredicate(Predicate[str, Serializable]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err(self, val: str) -> str:
        return EXPECTED_EMAIL_ADDRESS


BLANK_STRING_MSG: Final[str] = "cannot be blank"


class NotBlank(Predicate[str, Serializable]):
    def is_valid(self, val: str) -> bool:
        return len(val.strip()) != 0

    def err(self, val: str) -> Serializable:
        return BLANK_STRING_MSG


not_blank = NotBlank()


class MaxLength(Predicate[str, Serializable]):
    __match_args__ = ("length",)
    __slots__ = ("length", "_err")

    def __init__(self, length: int):
        self.length = length
        self._err = f"maximum allowed length is {self.length}"

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err(self, val: str) -> Serializable:
        return self._err


class MinLength(Predicate[str, Serializable]):
    __match_args__ = ("length",)
    __slots__ = ("length", "_err")

    def __init__(self, length: int):
        self.length = length
        self._err = f"minimum allowed length is {self.length}"

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err(self, val: str) -> str:
        return self._err


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
