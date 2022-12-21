Validators
==========
In Koda Validate, `Validator` is the fundamental validation building block. It's based on the idea that
validation can be universally represented by the function signature (pseudocode):

.. code-block::

    InputType -> ValidType | InvalidType

In Koda Validate (and Python) this looks more like:

.. code-block:: python

    Callable[[Any], Union[Valid[ValidType], Invalid]]

    # it's shorter when using the ValidationResult type alias
    Callable[[Any], ValidationResult[ValidType]]


A quick example:

.. code-block:: python

    from koda_validate import IntValidator, Valid, Invalid, TypeErr

    int_validator = IntValidator()

    assert int_validator(5) == Valid(5)
    assert int_validator("not an integer") == Invalid(TypeErr(int), 5, IntValidator())


This is a useful model to have for validation, because it means we can combine
validators in different ways (i.e. nesting them), and have our model of validation be consistent throughout.

Take a look at Extension to see how to build custom `Validator`s.
