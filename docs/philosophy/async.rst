Async
=====
Koda Validate aims to allow any kind of validation, including validation that requires IO.
Because of that, Koda Validate supports use of ``asyncio``. Async validation in Koda
Validate is designed with several ergonomics goals:

- requiring minimal changes from synchronous validation
- making async explicit and obvious
- alerting the user in illegal states

Minimal Changes
---------------

All built-in ``Validator``\s in Koda Validate allow for async validation. So, for instance,
you can call the same validator in both contexts.

.. code-block:: python

    from koda_validate import StringValidator

    str_validator = StringValidator()

    # sync
    str_validator("a string")
    # > Valid("a string")

    # async
    await str_validator.validate_async("a string")
    # > Valid("a string")


The one exception to this is that async-only validation can only be called in an async
context (see Alerting below).


Explicit and Obvious
--------------------
It should be difficult to accidentally define or invoke async validation. In places where
``asyncio`` is supported in Koda Validate, there is always "async" in the naming. Some examples:

- ``some_validator.validate_async(...)``
- ``PredicateAsync``
- ``StringValidator(predicates_async=[...])``
- ``TypedDictValidator(SomeTypedDict, validate_object_async=some_async_function)``



Alerting
--------
While ``Validator``\s can be defined to work in both sync and async contexts, once a
``Validator`` is initialized, Koda Validate will raise an exception if the both of the
following are true:

- it is initialized with async-only child validation (e.g. defining ``predicates_sync`` or ``validate_object_async`` on applicable ``Validator``\s)
- it is invoked in a synchronous context


When called in a sync context, Koda Validate does not implicitly skip async-only
validation, and it does not make an attempt to convert async-only validation to
sync validation.

.. code-block:: python

    from koda_validate import *

    async_only_str_validator = StringValidator(predicates_async=[SomeAsyncCheck()])

    await async_only_str_validator.validate_async("hmmm")  # runs normally

    async_only_str_validator("hmmm")  # raises an AssertionError

