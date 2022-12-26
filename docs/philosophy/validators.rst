Validators
==========
In Koda Validate, ``Validator`` is the fundamental validation building block. It's based on the idea that
any kind of data validation can be represented by a ``Callable`` signature like this:


.. code-block:: python

    ValidType = TypeVar("ValidType")

    Callable[[Any], Union[Valid[ValidType], Invalid]]


In Koda Validate we can abbreviate this with the ``ValidationResult`` type alias to:

.. code-block:: python

    Callable[[Any], ValidationResult[ValidType]]

The way we actually represent this concept in Koda Validate is even simpler:

.. code-block:: python

    Validator[ValidType]


.. note::

    There are a few differences between ``Validator[ValidType]`` and ``Callable[[Any], ValidationResult[ValidType]]`` that make them not exactly equivalent:

    - ``Validator``\s are always subclasses of ``Validator``. Using callable ``class``\es (instead of ``function``\s) makes it easy to branch on validators based on their class name.
    - ``Validator``\s have a ``validate_async`` method, which allows them to be used in both sync and async contexts.

    In sum, a ``Validator[ValidType]`` can be used in places where ``Callable[[Any], ValidationResult[ValidType]]`` is required, but
    ``Validator[ValidType]`` is fundamentally a richer type.

We can see in the following example how ``Validator``\s act like simple functions
which return either ``Valid[ValidType]`` or ``Invalid``:

.. code-block:: python

    from koda_validate import *

    int_validator = IntValidator()

    int_validator(5)
    # > Valid(5)

    int_validator("not an integer")
    # > Invalid(TypeErr(int), ...)


Having this simple function signature-based definition for validation is useful, because it means we can *compose*
validators. Perhaps the simplest example of this is how ``ListValidator`` accepts a validator for the items of the ``list``:

.. code-block:: python

    list_str_validator = ListValidator(StringValidator())

    list_str_validator(["ok", "nice"])
    # > Valid(["ok", "nice"])

    list_str_validator([1,2,3])
    # > Invalid(...)

Since ``Validator``\s are essentially functions (packaged as classes), they are easy to write and very flexible. Take a look at
Extension to see how.
