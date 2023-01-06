Maps
=====================

.. module:: koda_validate
    :noindex:

For dictionaries with consistent key/value types, you can use :class:`MapValidator`.

.. testcode:: mapv

    from koda_validate import *

    validator = MapValidator(key=StringValidator(),
                             value=IntValidator(),
                             predicates=[MinKeys(1), MaxKeys(3)])


    assert validator({"a": 1, "b": 2}) == Valid({'a': 1, 'b': 2})

    assert validator({}) == Invalid(PredicateErrs([MinKeys(1)]), {}, validator)

    assert validator({"a": "not an int"}) == Invalid(
        MapErr({'a': KeyValErrs(key=None,
                                val=Invalid(TypeErr(int), 'not an int', IntValidator()))}),
        {'a': 'not an int'},
        validator
    )

Mypy will infer that the type of valid data returned from ``validator`` above will be
``Dict[str, int]``.
