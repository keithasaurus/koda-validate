from koda_validate._internal import _ExactTypeValidator


class FloatValidator(_ExactTypeValidator[float]):
    """
    Validate a value is a ``float``, and any extra refinement.

    If ``predicates_async`` is supplied, the ``__call__`` method should not be
    called -- only ``.validate_async`` should be used.

    :param predicates: any number of ``Predicate[float]`` instances
    :param predicates_async: any number of ``PredicateAsync[float]`` instances
    :param preprocessors: any number of ``Processor[float]``, which will be run before
        :class:`Predicate`\s and :class:`PredicateAsync`\s are checked.
    """

    _TYPE = float
