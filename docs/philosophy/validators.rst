Validators
==========
In Koda Validate, ``Validator`` is the fundamental validation building block. It's based on the idea that
any kind of data validation can be represented by the function signature:

.. code-block:: python

    Callable[[Any], Union[Valid[ValidType], Invalid]]


In Koda Validate we shorten this with the ``ValidationResult`` type alias:

.. code-block:: python

    Callable[[Any], ValidationResult[ValidType]]

A quick example:

.. code-block:: python

    from koda_validate import IntValidator, Valid, Invalid, TypeErr

    int_validator = IntValidator()

    int_validator(5)
    # > Valid(5)

    int_validator("not an integer")
    # > Invalid(TypeErr(int), ...)


This is a useful model to have for validation, because it means we can compose validators. Perhaps the
simplest example of this is how ``ListValidator`` requires a separate validator for the items of
the ``list``.

Take a look at Extension to see how to build custom ``Validator``\s.
