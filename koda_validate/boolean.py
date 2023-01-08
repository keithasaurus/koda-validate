from koda_validate._internal import _ToTupleScalarValidator


class BoolValidator(_ToTupleScalarValidator[bool]):
    r"""
    Validate a value is a ``bool``, and any extra refinement.

    If ``predicates_async`` is supplied, the ``__call__`` method should not be
    called -- only ``.validate_async`` should be used.

    :param predicates: any number of ``Predicate[bool]`` instances
    :param predicates_async: any number of ``PredicateAsync[bool]`` instances
    :param preprocessors: any number of ``Processor[bool]``, which will be run before
        :class:`Predicate`\s and :class:`PredicateAsync`\s are checked.
    """

    _TYPE = bool
