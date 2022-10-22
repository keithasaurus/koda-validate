import re
from dataclasses import dataclass
from typing import Any, Final, List, Optional, Pattern, Tuple

from koda import Err, Result

from koda_validate.typedefs import JSONValue, Predicate, Processor, Validator
from koda_validate.utils import accum_errors_json, expected


@dataclass(init=False, frozen=True)
class StringValidator(Validator[Any, str, JSONValue]):
    predicates: Tuple[Predicate[str, JSONValue], ...]
    preprocessors: Optional[List[Processor[str]]]

    def __init__(
        self,
        *predicates: Predicate[str, JSONValue],
        preprocessors: Optional[List[Processor[str]]] = None,
    ) -> None:
        object.__setattr__(self, "predicates", predicates)
        object.__setattr__(self, "preprocessors", preprocessors)

    def __call__(self, val: Any) -> Result[str, JSONValue]:
        if isinstance(val, str):
            if self.preprocessors is not None:
                for preprocess in self.preprocessors:
                    val = preprocess(val)

            return accum_errors_json(val, self.predicates)
        else:
            return Err([expected("a string")])


@dataclass(frozen=True)
class RegexPredicate(Predicate[str, JSONValue]):
    pattern: Pattern[str]

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message(self, val: str) -> str:
        return rf"must match pattern {self.pattern.pattern}"


@dataclass(frozen=True)
class Email(Predicate[str, JSONValue]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message(self, val: str) -> str:
        return "expected a valid email address"


BLANK_STRING_MSG: Final[str] = "cannot be blank"


class NotBlank(Predicate[str, JSONValue]):
    def is_valid(self, val: str) -> bool:
        return len(val.strip()) != 0

    def err_message(self, val: str) -> JSONValue:
        return BLANK_STRING_MSG


not_blank = NotBlank()


@dataclass(frozen=True)
class MaxLength(Predicate[str, JSONValue]):
    length: int

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err_message(self, val: str) -> JSONValue:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinLength(Predicate[str, JSONValue]):
    length: int

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err_message(self, val: str) -> str:
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
