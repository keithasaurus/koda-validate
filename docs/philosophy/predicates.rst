Predicates
----------
In the world of validation, predicates are simply expressions that return a ``True`` or ``False`` for a given condition.
In Python type hints, predicates can be expressed like this:

.. code-block:: python

    A = TypeVar('A')

    PredicateFunc = Callable[[A], bool]

Koda Validate has a ``Predicate`` class based on this concept. In Koda Validate, ``Predicate``\s are used to *enrich* ``validator``\s
by performing additional validation *after* the data has been verified to be of a specific type or shape.

.. code-block:: python

    from koda_validate import *

    int_validator = IntValidator(Min(5))  # `Min` is a `Predicate`

    int_validator(6)
    # > Valid(6)

    int_validator("a string")
    # > Invalid(TypeErr(int), ...)

    int_validator(4)
    # > Invalid(PredicateErrs([Min(5)]), ...)

As you can see the value ``4`` passes the ``int`` type check but fails to pass the ``Min(5)`` predicate.

Because we know that predicates don't change the type or value of their inputs, we can
sequence an arbitrary number of them together, and validate them all.

.. code-block:: python

    from koda_validate import *

    int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

    int_validator(12)
    # > Valid(12)

    int_validator(23)
    # > Invalid(PredicateErrs([Max(20), MultipleOf(4)]), ...)

Here ``int_validator`` has 3 ``Predicate``\s, but we could have as many as we want. Note
that ``Predicate``\s for which a value is invalid are returned within a ``PredicateErrs`` instance. We are only able
to return all the failing ``Predicate``\s because we know that each `Predicate` will not be able to change the value.

``Predicate``\s are easy to write -- take a look at [Extension](#extension) for more details.
