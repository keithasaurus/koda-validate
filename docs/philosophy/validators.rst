Validators
==========
.. module:: koda_validate
    :noindex:

In Koda Validate, :class:`Validator<koda_validate.Validator>` is the fundamental validation building block. It's based on the idea that
any kind of data validation can be represented by a ``Callable`` signature like this:


.. code-block:: python

    ValidType = TypeVar("ValidType")

    Callable[[Any], Union[Valid[ValidType], Invalid]]


In Koda Validate we can abbreviate this with the :data:`ValidationResult` type alias to:

.. code-block:: python

    Callable[[Any], ValidationResult[ValidType]]

The way we actually represent this concept in Koda Validate is even simpler:

.. code-block:: python

    Validator[ValidType]


.. note::

    There are a few differences between ``Validator[ValidType]`` and ``Callable[[Any], ValidationResult[ValidType]]`` that make them not exactly equivalent:

    - :class:`Validator<koda_validate.Validator>`\s are always subclasses of :class:`Validator<koda_validate.Validator>`. Using callable ``class``\es (instead of ``function``\s) makes it easy to branch on validators based on their class name.
    - :class:`Validator<koda_validate.Validator>`\s have a ``validate_async`` method, which allows them to be used in both sync and async contexts.

    In sum, a ``Validator[ValidType]`` can be used in places where ``Callable[[Any], ValidationResult[ValidType]]`` is required, but
    ``Validator[ValidType]`` is fundamentally a richer type.

We can see in the following example how :class:`Validator<koda_validate.Validator>`\s act like simple functions
which return either ``Valid[ValidType]`` or ``Invalid``:

.. testcode:: callable

    from koda_validate import IntValidator

    int_validator = IntValidator()

Usage:

.. doctest:: callable

    >>> int_validator(5)
    Valid(val=5)

    >>> int_validator("not an integer")
    Invalid(err_type=TypeErr(expected_type=<class 'int'>), ...)


Having this simple function signature-based definition for validation is useful, because it means we can *compose*
validators. Perhaps the simplest example of this is how ``ListValidator`` accepts a validator for the items of the ``list``:

.. testcode:: callable

    from koda_validate import ListValidator, StringValidator

    list_str_validator = ListValidator(StringValidator())


Usage:

.. doctest:: callable

    >>> list_str_validator(["ok", "nice"])
    Valid(val=['ok', 'nice'])

    >>> list_str_validator([1,2,3])
    Invalid(...)

Since :class:`Validator<koda_validate.Validator>`\s are essentially functions (packaged as classes),
they are flexible and easy to write. Take a look at :ref:`how_to/extension:Extension` to see how.
