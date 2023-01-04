Async
=====
.. module:: koda_validate

All the built-in :class:`Validator<koda_validate.base.Validator>`\s in Koda Validate are asyncio-compatible, and there
is a simple, consistent way to run async validation:

.. code-block:: python

    await validator.validate_async("abc")


Instead of:

.. code-block:: python

    validator("abc")

Alternating between Sync and Async
----------------------------------

In many cases, you can use the same :class:`Validator` instance in sync and async contexts:

.. testcode:: python

    import asyncio
    from koda_validate import *


    validator = StringValidator(MaxLength(10))

    # sync mode
    assert validator("sync") == Valid("sync")

    # async mode (we're not in an async context, so we can't use `await` here)
    assert asyncio.run(validator.validate_async("async")) == Valid("async")

While this :class:`StringValidator` works in async mode,
it isn't yielding any benefit for IO. It would be much more useful if we were doing something like querying a database
asynchronously:


.. testcode:: predasync

    import asyncio
    from koda_validate import *


    class IsActiveUsername(PredicateAsync[str]):
        async def validate_async(self, val: str) -> bool:
            # add some latency to pretend we're calling the db
            await asyncio.sleep(.01)

            return val in {"michael", "gob", "lindsay", "buster"}


    username_validator = StringValidator(MinLength(1),
                                         predicates_async=[(is_active_username := IsActiveUsername())])

    assert asyncio.run(username_validator.validate_async("michael")) == Valid("michael")

    assert asyncio.run(username_validator.validate_async("tobias")) == Invalid(PredicateErrs([is_active_username]), "tobias", username_validator)

    # calling in sync mode raises an AssertionError
    try:
        username_validator("michael")
    except AssertionError:
        print("expected error raised")

.. testoutput:: predasync
    :hide:

    expected error raised

.. note::
    :class:`PredicateAsync`\s are specified in the ``predicates_async`` keyword argument
    -- separately from :class:`Predicate`\s. The call signature is designed this way to
    be explicit -- we don't want to be confused about whether a validator requires
    ``asyncio``. If you try to run this validator in synchronous mode, it will raise an
    ``AssertionError`` -- instead make sure you call it like
    ``await username_validator.validate_async("buster")``.

Like other validators, you can nest async :class:`Validator`\s. Again, the only
difference is calling the ``.validate_async`` method of the outer-most validator.

.. code-block:: python

    # continued from previous example

    username_list_validator = ListValidator(username_validator)

    users = ["michael", "gob", "lindsay", "buster"]
    assert asyncio.run(username_list_validator.validate_async(users)) == Valid(users)

You can run async validation on nested lists, dictionaries, tuples, strings, etc. All :class:`Validator<koda_validate.Validator>`\s built into to Koda Validate
understand the ``.validate_async`` method.

.. note::
    **Concurrency**

    Koda Validate makes no assumptions about running async :class:`Validator`\s or :class:`PredicateAsync`\s concurrently; it is
    expected that that is handled by the surrounding context. That is to say, async validators will not block when performing IO -- as is normal -- but if you had, say, 10 async
    predicates, they would not be run in parallel by default. This is simply because that is too much of an assumption for this library to make -- we don't
    want to accidentally send N simultaneous requests to some other service without the intent being explicitly defined. If you'd like to have :class:`Validator`\s
    or :class:`Predicate`\s run in parallel _within_ the validation step, all you should need to do is write a simple wrapper class based on either :class:`Validator`
    or :class:`Predicate`, implementing whatever concurrency needs you have.


Custom Async Validators
-----------------------

For custom async :class:`Validator`\s, all you need to do is implement the ``validate_async`` method on a :class:`Validator` class. There is no
separate async-only :class:`Validator` class. This is because we might want to re-use synchronous validators in either synchronous
or asynchronous contexts. Here's an example of making a ``SimpleFloatValidator`` async-compatible:

.. testcode:: customasync

    import asyncio
    from typing import Any

    from koda_validate import *


    class SimpleFloatValidator(Validator[float]):
        def __call__(self, val: Any) -> ValidationResult[float]:
            if isinstance(val, float):
                return Valid(val)
            else:
                return Invalid(TypeErr(float), val, self)

        # this validator doesn't do any IO, so we can just use the `__call__` method
        async def validate_async(self, val: Any) -> ValidationResult[float]:
            return self(val)


    float_validator = SimpleFloatValidator()

    test_val = 5.5

    assert asyncio.run(float_validator.validate_async(test_val)) == Valid(test_val)

    assert asyncio.run(float_validator.validate_async(5)) == Invalid(TypeErr(float), 5, float_validator)


If your :class:`Validator` only makes sense in an async context, then you probably don't need to implement the ``__call__`` method.
Instead, you'd just implement the ``.validate_async`` method and make sure that validator is always called by ``await``-ing
the ``.validate_async`` method. A ``NotImplementedError`` will be raised if you try to use the ``__call__`` method on an
async-only :class:`Validator`.
