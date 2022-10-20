from typing import Callable

from koda_validate._generics import A

Processor = Callable[[A], A]


def strip(val: str) -> str:
    return val.strip()
