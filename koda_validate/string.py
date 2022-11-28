import re
from dataclasses import dataclass
from typing import Pattern

from koda_validate.base import Predicate, Processor, _ExactTypeValidator


class StringValidator(_ExactTypeValidator[str]):
    _TYPE = str


@dataclass
class RegexPredicate(Predicate[str]):
    pattern: Pattern[str]

    def __call__(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None


@dataclass
class EmailPredicate(Predicate[str]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def __call__(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None


@dataclass
class NotBlank(Predicate[str]):
    def __call__(self, val: str) -> bool:
        return len(val.strip()) != 0


not_blank = NotBlank()


@dataclass
class MaxLength(Predicate[str]):
    length: int

    def __call__(self, val: str) -> bool:
        return len(val) <= self.length


@dataclass
class MinLength(Predicate[str]):
    length: int

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
