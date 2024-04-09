import re
from dataclasses import dataclass
from typing import Pattern

from koda_validate._internal import _ToTupleStandardValidator
from koda_validate.base import Predicate


class StringValidator(_ToTupleStandardValidator[str]):
    r"""
    Validate a value is a ``str``, and any extra refinement.

    If ``predicates_async`` is supplied, the ``__call__`` method should not be
    called -- only ``.validate_async`` should be used.

    Example:

    >>> from koda_validate import *
    >>> validator = StringValidator(not_blank, MaxLength(100), preprocessors=[strip])
    >>> validator("")
    Invalid(err_type=PredicateErrs(predicates=[NotBlank()]), ...)
    >>> validator(None)
    Invalid(err_type=TypeErr(expected_type=<class 'str'>), ...)
    >>> validator(" ok ")
    Valid(val='ok')

    :param predicates: any number of ``Predicate[str]`` instances
    :param predicates_async: any number of ``PredicateAsync[str]`` instances
    :param preprocessors: any number of ``Processor[str]``, which will be run before
        :class:`Predicate`\s and :class:`PredicateAsync`\s are checked.
    """

    _TYPE = str


@dataclass
class RegexPredicate(Predicate[str]):
    pattern: Pattern[str]

    def __call__(self, val: str) -> bool:
        return self.pattern.match(val) is not None


@dataclass
class EmailPredicate(Predicate[str]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def __call__(self, val: str) -> bool:
        return self.pattern.match(val) is not None
