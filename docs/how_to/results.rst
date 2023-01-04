Validation Results
==================

.. module:: koda_validate
    :noindex:

:class:`Validator<koda_validate.Validator>`\s take one generic parameter, which represents the type of the valid data. For example, a ``Validator[int]`` must return an
``int`` if the data it's called with is valid:

.. testsetup:: 1

    from koda_validate import *

.. testcode:: 1

    validator: Validator[int] = IntValidator()

    result = validator(5)
    assert result.is_valid
    assert isinstance(result.val, int)  # mypy also knows ``result.val`` is an ``int``

The full type of ``result`` in the above example is ``ValidationResult[int]`` (this can be de-sugared to
``Union[Valid[int], Invalid]``). As you can see, to do something useful with :data:`ValidationResult`\s, we need to
distinguish between the :class:`Valid` and :class:`Invalid` variants.

``if`` Statements
-----------------
Perhaps the easiest way is to just branch on ``.is_valid``:

.. testcode:: if-statements

    from koda_validate import *

    def result_to_str(result: ValidationResult[str]) -> str:
        if result.is_valid:
            # mypy understands result is Valid[str]
            return result.val
        else:
            # mypy understands result is Invalid
            err_type_cls = result.err_type.__class__.__name__
            return (
                f"Error of type {err_type_cls}, "
                f"while validating {result.value} with {result.validator}"
            )

Let's see how it works

.. doctest:: if-statements

    >>> validator = StringValidator()
    >>> result_to_str(validator("abc123"))
    'abc123'

    >>> result_to_str(validator(0))
    'Error of type TypeErr, while validating 0 with StringValidator()'


Pattern Matching
----------------
Pattern matching can make this more concise in Python 3.10+:

.. testcode:: pattern-matching

    from koda_validate import *

    def result_to_val(result: ValidationResult[str]) -> int | str:
        match result:
            case Valid(valid_val):
                return valid_val
            case Invalid(err_type, val, validator_):
                return (
                    f"Error of type {err_type.__class__.__name__}, "
                    f"while validating {val} with {validator_}"
                )

Let's try it

.. doctest:: pattern-matching

    >>> validator = IntValidator()
    >>> result_to_val(validator(123))
    123

    >>> result_to_val(validator("abc"))
    'Error of type TypeErr, while validating abc with IntValidator()'


Working with ``Invalid``
------------------------
:class:`Invalid` instances provide machine-readable validation failure data. Usually this is not terribly useful on its own.
In most cases you'll want to transform these data in some way before sending it somewhere else. The expectation is that
built-in, or custom, utility functions should handle this. One such built-in function is :data:`to_serializable_errs<koda_validate.serialization.to_serializable_errs>`. It
takes an :class:`Invalid` instance and produces errors objects suitable for JSON / YAML serialization.

.. testcode:: 3

    from koda_validate import *
    from koda_validate.serialization import to_serializable_errs

    validator = StringValidator()

    result = validator(123)
    assert isinstance(result, Invalid)

    print(to_serializable_errs(result))

Outputs

.. testoutput:: 3

    ['expected a string']

Even if it doesn't suit your ultimate purpose, :data:`to_serializable_errs<koda_validate.serializable.to_serializable_errs>` can be useful during
development because the error messages tend to be more readable than the printed representation of
:class:`Invalid` instances.

.. note::
    :data:`to_serializable_errs<koda_validate.serializable.to_serializable_errs>` is only meant to be a basic effort at a general English-language serializable
    utility function. It may be convenient to work with, but please do not feel that you are in any way
    limited to its functionality. Koda Validate's intention is that users should be able to build whatever
    error objects they need by consuming the :class:`Invalid` data.

