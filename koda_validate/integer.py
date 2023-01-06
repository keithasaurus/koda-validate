from koda_validate._internal import _ExactTypeValidator


class IntValidator(_ExactTypeValidator[int]):
    r"""
    Validate a value is a ``int``, and any extra refinement.

    If ``predicates_async`` is supplied, the ``__call__`` method should not be
    called -- only ``.validate_async`` should be used.

    :param predicates: any number of ``Predicate[int]`` instances
    :param predicates_async: any number of ``PredicateAsync[int]`` instances
    :param preprocessors: any number of ``Processor[int]``, which will be run before
        :class:`Predicate`\s and :class:`PredicateAsync`\s are checked.
    """

    _TYPE = int
