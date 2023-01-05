from koda_validate._internal import _ExactTypeValidator


class BytesValidator(_ExactTypeValidator[bytes]):
    r"""
    Validate a value is a ``bytes``, and any extra refinement.

    If ``predicates_async`` is supplied, the ``__call__`` method should not be
    called -- only ``.validate_async`` should be used.

    :param predicates: any number of ``Predicate[bytes]`` instances
    :param predicates_async: any number of ``PredicateAsync[bytes]`` instances
    :param preprocessors: any number of ``Processor[bytes]``, which will be run before
        :class:`Predicate`\s and :class:`PredicateAsync`\s are checked.
    """

    _TYPE = bytes
