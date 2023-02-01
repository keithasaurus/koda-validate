Async
=====
Koda Validate aims to allow any kind of validation, including validation that requires IO.
For IO, Koda Validate supports, and encourages, the use of ``asyncio``. Async validation in Koda
Validate is designed with several ergonomics goals:

- minimal changes should be required when switching from synchronous to asynchronous validation
- usage of ``asyncio`` should be explicit and obvious
- the user should be alerted when illegal states are encountered

Minimal Changes
---------------

All built-in :class:`Validator<koda_validate.Validator>`\s in Koda Validate allow for async validation, so
the same :class:`Validator<koda_validate.Validator>` can be called in both contexts.

.. testcode:: syncandasync

    import asyncio
    from koda_validate import StringValidator

    str_validator = StringValidator()

Synchronous:

.. doctest:: syncandasync

    >>> str_validator("a string")
    Valid(val='a string')

Asynchronous:

.. doctest:: syncandasync

    >>> asyncio.run(str_validator.validate_async("a string"))
    Valid(val='a string')


.. note::

    Synchronous validation logic can be called in both synchronous and asynchronous contexts, but async-only
    validation can only be called in an async context -- see Alerting below.


Making Async Explicit and Obvious
---------------------------------
It should be difficult to accidentally define or invoke async validation. In places where
``asyncio`` is supported in Koda Validate, there is always "async" in the naming. Some examples:

- ``some_validator.validate_async(...)``
- :class:`PredicateAsync<koda_validate.PredicateAsync>`
- ``StringValidator(predicates_async=[...])``
- ``TypedDictValidator(SomeTypedDict, validate_object_async=some_async_function)``



Alerting on Illegal States
--------------------------
While :class:`Validator<koda_validate.Validator>`\s can be defined to work in both sync and async contexts, once a
:class:`Validator<koda_validate.Validator>` is initialized, Koda Validate will raise an exception if the both of the
following are true:

1. it is initialized with async-only validation (e.g. defining ``predicates_async`` or ``validate_object_async`` on applicable :class:`Validator<koda_validate.Validator>`\s)
2. it is invoked synchronously -- i.e. ``some_async_validator(123)`` instead of ``await some_async_validator.validate_async(123)``


The reason Koda Validate alerts in this context is because it does not want to guess at what the intended behavior is. It does
neither of the following:

- implicitly skip async-only validation
- try to run async validation synchronously

Here you can see how async-only validators alert:

.. code-block:: python

    from koda_validate import *

    async_only_str_validator = StringValidator(predicates_async=[SomeAsyncCheck()])

    asyncio.run(async_only_str_validator.validate_async("hmmm"))  # runs normally

    async_only_str_validator("hmmm")  # raises an AssertionError
