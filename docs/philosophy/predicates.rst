Predicates
----------

.. module:: koda_validate
    :noindex:

In the world of validation, predicates are simply expressions that return a ``True`` or ``False`` for a given condition.
In Python type hints, predicates can be expressed like this:

.. code-block:: python

    A = TypeVar('A')

    PredicateFunc = Callable[[A], bool]

Koda Validate has a :class:`Predicate<koda_validate.Predicate>` class based on this concept. In Koda Validate, :class:`Predicate<koda_validate.Predicate>`\s are used to *enrich* :class:`Validator<koda_validate.Validator>`\s
by performing additional validation *after* the data has been verified to be of a specific type or shape.

.. testcode:: intpred

    from koda_validate import IntValidator, Min

    int_validator = IntValidator(Min(5))  # `Min` is a `Predicate`

Usage:

.. doctest:: intpred

    >>> int_validator(6)
    Valid(val=6)

    >>> int_validator("a string")
    Invalid(err_type=TypeErr(expected_type=<class 'int'>), ...)

    >>> int_validator(4)
    Invalid(err_type=PredicateErrs(predicates=[Min(minimum=5, exclusive_minimum=False)]), ...)

As you can see the value ``4`` passes the ``int`` type check but fails to pass the ``Min(5)`` predicate.

Because we know that predicates don't change the type or value of their inputs, we can
sequence an arbitrary number of :class:`Predicate`\s together, and validate them all.

.. testcode:: intpred2

    from koda_validate import (IntValidator, Min, Max, MultipleOf, Invalid,
                               Valid, PredicateErrs)

    int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

    assert int_validator(12) == Valid(12)

    invalid_result = int_validator(23)
    assert isinstance(invalid_result, Invalid)
    assert invalid_result.err_type == PredicateErrs([Max(20), MultipleOf(4)])


Here ``int_validator`` has 3 :class:`Predicate<koda_validate.Predicate>`\s, but we could have as many as we want. Note
that failing :class:`Predicate<koda_validate.Predicate>`\s are returned within a :class:`PredicateErrs` instance. We are only able
to return all the failing :class:`Predicate<koda_validate.Predicate>`\s because we know that each :class:`Predicate` will not be able to change the value.

:class:`Predicate<koda_validate.Predicate>`\s are easy to write -- take a look at [Extension](#extension) for more details.
