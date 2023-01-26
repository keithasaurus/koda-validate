from koda_validate._internal import _ToTupleStandardValidator


class BytesValidator(_ToTupleStandardValidator[bytes]):
    r"""
    Validate a value is a ``bytes``, and any extra refinement.

    If ``predicates_async`` is supplied, the ``__call__`` method should not be
    called -- only ``.validate_async`` should be used.

    Example:

    >>> from koda_validate import *
    >>> validator = BytesValidator(not_blank, MaxLength(100), preprocessors=[strip])
    >>> validator(b"")
    Invalid(err_type=PredicateErrs(predicates=[NotBlank()]), ...)
    >>> validator("")
    Invalid(err_type=TypeErr(expected_type=<class 'bytes'>), ...)
    >>> validator(b' ok ')
    Valid(val=b'ok')

    :param predicates: any number of ``Predicate[bytes]`` instances
    :param predicates_async: any number of ``PredicateAsync[bytes]`` instances
    :param preprocessors: any number of ``Processor[bytes]``, which will be run before
        :class:`Predicate`\s and :class:`PredicateAsync`\s are checked.
    :param coerce: a function that can control coercion
    """

    _TYPE = bytes
