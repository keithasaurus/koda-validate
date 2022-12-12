import re
from dataclasses import dataclass
from typing import ClassVar, Optional, Pattern

from koda_validate._internal import _ExactTypeValidator
from koda_validate.base import Predicate, Processor


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
    _instance: ClassVar[Optional["NotBlank"]] = None

    def __new__(cls) -> "NotBlank":
        """
        Make a singleton
        """
        if cls._instance is None:
            cls._instance = super(NotBlank, cls).__new__(cls)
        return cls._instance

    def __call__(self, val: str) -> bool:
        return len(val.strip()) != 0


not_blank = NotBlank()


@dataclass
class Strip(Processor[str]):
    def __call__(self, val: str) -> str:
        return val.strip()


strip = Strip()


@dataclass
class UpperCase(Processor[str]):
    def __call__(self, val: str) -> str:
        return val.upper()


upper_case = UpperCase()


@dataclass
class LowerCase(Processor[str]):
    def __call__(self, val: str) -> str:
        return val.lower()


lower_case = LowerCase()
