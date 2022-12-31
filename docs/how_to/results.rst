Validation Results
==================

The result from calling a ``Validator[SomeType]`` of a given type will be ``Union[Valid[SomeType], Invalid]``. This means that
we need to distinguish between the valid and invalid results to do something useful with the result. Perhaps the
easiest way is to just branch on i``<some_result>.is_valid``:

Branching on Validity
---------------------

.. code-block:: python

    from koda_validate import StringValidator

    validator = StringValidator()

    result = some_validator("abc123")

    if result.is_valid:
        # mypy understands `result` is Valid[str]
        print(result.val)
    else:
        # mypy understands `result` is Invalid
        print(f"Error of type {type(result.err_type)} "
              f"while validating {result.value} "
              f"with validator {result.validator}")

Pattern matching can make this more concise in Python 3.10+:

.. code-block:: python

    from koda_validate import StringValidator

    validator = StringValidator()

    match some_validator("abc123"):
        case Valid(valid_str):
            print(valid_str)
        case Invalid(err_type, value, validator_):
            print(f"Error of type {type(err_type)} "
                  f"while validating {value} "
                  f"with validator {validator_}")

Working with Errors
-------------------
``Invalid`` instances provide machine-readable failure data. In many cases you'll want to transform
these data in some way. The expectation is that you simply use utility functions to do this. One such function built
into Koda Validate is ``to_serializable_errs``, which takes the raw errors and
produces human-readable errors suitable for JSON / YAML serialization.

.. code-block:: python

    from koda_validate import *

    validator = StringValidator()

    match some_validator(123):
        case Valid(valid_str):
            print(valid_str)
        case Invalid() as inv:
            print(to_serializable_errs(inv))

Even if it doesn't fit your ultimate use case, ``to_serializable_errs`` can be useful in
development because the error messages tend to be more readable than the printed representation of
``Invalid`` instances.

.. note::
    ``to_serializable_errs`` is only meant to be a basic effort at a general English-language serializable
    utility function. It may be convenient to work with, but please do not feel that you are in any way
    limited to its functionality. Koda Validate's intention is that users should be able to build whatever
    error objects they need by consuming the ``Invalid`` data.

