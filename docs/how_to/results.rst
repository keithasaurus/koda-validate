Validation Results
==================

``Validator``\s take one generic parameter, which represents the type of that ``Validator``\'s valid data. For example, a ``Validator[int]`` must return an
``int`` if valid when called:

.. code-block:: python

    validator: Validator[int] = ...

    result = validator(5)
    assert result.is_valid
    reveal_type(result.val)  # mypy knows this is an int because of the assertion


The full type of result in the above example is ``ValidationResult[int]`` (this can be de-sugared to
``Union[Valid[int], Invalid]``). As you can see, to do something useful with ``ValidationResult``\s, we need to
distinguish between the ``Valid`` and ``Invalid`` variants.

``if`` Statements
-----------------
Perhaps the easiest way is to just branch on ``.is_valid``:


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

Pattern Matching
----------------
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

Working with ``Invalid``
------------------------
``Invalid`` instances provide machine-readable validation failure data. Usually this is not terribly useful on its own.
In most cases you'll want to transform these data in some way before sending it somewhere else. The expectation is that
built-in, or custom, utility functions should handle this. One such built-in function is ``to_serializable_errs``. It
takes an ``Invalid`` instance and produces errors objects suitable for JSON / YAML serialization.

.. code-block:: python

    from koda_validate import *

    validator = StringValidator()

    result = validator(123)
    assert isinstance(result, Invalid)

    print(to_serializable_errs(result))



Even if it doesn't suit your ultimate purpose, ``to_serializable_errs`` can be useful in
development because the error messages tend to be more readable than the printed representation of
``Invalid`` instances.

.. note::
    ``to_serializable_errs`` is only meant to be a basic effort at a general English-language serializable
    utility function. It may be convenient to work with, but please do not feel that you are in any way
    limited to its functionality. Koda Validate's intention is that users should be able to build whatever
    error objects they need by consuming the ``Invalid`` data.

