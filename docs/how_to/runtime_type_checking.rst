Runtime Type Checking
=====================

.. module:: koda_validate.signature
    :noindex:

Koda Validate supports runtime type-checking via :data:`validate_signature`, a decorator
that can validate function arguments and return values at
runtime. By default, it will infer the validation logic from typehints.

.. testcode:: basic

    from koda_validate.signature import *

    @validate_signature
    def add(x: int, y: int) -> int:
        return x + y

Usage

.. doctest:: basic

    >>> add(1,2)
    3

    >>> add("not", "ints")  # bad types
    Traceback (most recent call last):
    ...
    koda_validate.signature.InvalidArgsError:
    Invalid Argument Values
    -----------------------
    x='not'
        expected <class 'int'>
    y='ints'
        expected <class 'int'>

:data:`validate_signature` raises an :class:`InvalidArgsError` when arguments
are invalid or :class:`InvalidReturnError` when the returned value is invalid.

.. note::

    While the main interface for the developer is usually the formatted output in the traceback,
    :class:`InvalidArgsError` and :class:`InvalidReturnError` both contain all relevant
    :class:`Invalid<koda_validate.Invalid>` objects on ``InvalidArgsError.errs`` or
    ``InvalidReturnError.err``


:data:`validate_signature` works on class methods as well, and with many different kinds of arugments.

.. testcode:: object

    from koda_validate.signature import *

    class Obj:
        @validate_signature
        def some_method(self, a: int, *, b: int = 5) -> int:
            return a + b


Usage

.. doctest:: object

    >>> Obj().some_method(1, b=2)
    3
    >>> Obj().some_method("oops", b=3)
    Traceback (most recent call last):
    ...
    koda_validate.signature.InvalidArgsError:
    Invalid Argument Values
    -----------------------
    a='oops'
        expected <class 'int'>

.. note::

    You can simply decorate the ``__init__`` method of a class with :data:`validate_signature`
    if you want to disable object creation for invalid arguments.



Customization
-------------
:data:`validate_signature` is wholly customizable, so it can fit practically any use case.


Ignoring Arguments and Return Values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Perhaps the simplest customization to
make is to tell :data:`validate_signature` what to ignore. For that you can use ``ignore_args`` and
``ignore_return``.

.. testcode:: ignore

    from koda_validate.signature import *

    @validate_signature(ignore_args={"b"}, ignore_return=True)
    def add_float_to_int(a: int, b: float) -> float:
        return a + b

    assert add_float_to_int(1, 2) == 3

:data:`validate_signature` did not raise an ``Exception`` even though
the argument for ``b`` and the return type were both invalid. `ignore_args` should
work for any parameter in a function signature.

.. note::
    ``ignore_args`` will even work for parameters defined in ``**kwargs`` (not in the signature)

    .. testcode:: ignore2

        from koda_validate.signature import *

        @validate_signature(ignore_args={"violets"})
        def some_func(**descriptions: str) -> None:
            return None

        # didn't raise even though violets is not a string
        assert some_func(roses="red", violets=2) is None

Annotated Validators
^^^^^^^^^^^^^^^^^^^^
You can use ``typing.Annotated`` to customize how the arguments and / or return value are
validated -- using the same kinds of :class:`Validator<koda_validate.Validator>`\s used in data validation.

.. testcode:: annotated

    from koda_validate import *
    from koda_validate.signature import *
    from typing import Annotated

    @validate_signature
    def reverse_name(
        name: Annotated[str, StringValidator(MinLength(1), MaxLength(20))]
    ) -> Annotated[str, StringValidator(MinLength(1), MaxLength(20))]:
        return name[::-1]

Let's try it.


.. doctest:: annotated

    >>> reverse_name("Jen")  # a valid name
    'neJ'

    >>> reverse_name("")  # too short
    Traceback (most recent call last):
    ...
    koda_validate.signature.InvalidArgsError:
    Invalid Argument Values
    -----------------------
    name=''
        PredicateErrs
            MinLength(length=1)

    >>> reverse_name("areallylongnametohave")  # too long
    Traceback (most recent call last):
    ...
    koda_validate.signature.InvalidArgsError:
    Invalid Argument Values
    -----------------------
    name='areallylongnametohave'
        PredicateErrs
            MaxLength(length=20)

Overrides
^^^^^^^^^
If you are using Python 3.8, or if you don't like the ``Annotated`` syntax, you can achieve
the same thing with ``overrides``. This is equivalent to the ``Annotated`` example above`:

.. testcode:: overrides

    from koda_validate import *
    from koda_validate.signature import *

    @validate_signature(overrides={
        "name": StringValidator(MinLength(1), MaxLength(20)),
        RETURN_OVERRIDE_KEY: StringValidator(MinLength(1), MaxLength(20))
    })
    def reverse_name(name: str) -> str:
        return name[::-1]

.. note::

    ``RETURN_OVERRIDE_KEY`` is a special key that allows us to override the default
    :class:`Validator<koda_validate.Validator>` for the return value. It's the only
    non-string key allowed in ``overrides``.

Typehint Resolution
-------------------

You can define your own typehint resolution logic by passing a function as the argument
for ``typehint_resolver``. One situation in which this can be useful is when defining ``NewType``\s.

.. testcode:: resolver

    from typing import NewType
    from koda_validate import *
    from koda_validate.signature import *

    Email = NewType('Email', str)

    def custom_resolve_typehint(annotation: Any) -> Validator[Any]:
        if annotation is Email:
            return StringValidator(EmailPredicate())
        else:
            return resolve_signature_typehint_default(annotation)

    @validate_signature(typehint_resolver=custom_resolve_typehint)
    def message_someone(email: Email, message: str) -> str:
        # send the message
        return f"sent {message} to {email}"

Usage

.. doctest:: resolver

    >>> message_someone(Email("abc@example.com"), "hi!")
    'sent hi! to abc@example.com'

    >>> message_someone(Email("abc"), "hello!")
    Traceback (most recent call last):
    ...
    koda_validate.signature.InvalidArgsError:
    Invalid Argument Values
    -----------------------
    email='abc'
        PredicateErrs
            EmailPredicate(pattern=re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+'))


Overriding typehint resolution can also be helpful in places where Koda Validate cannot
fully infer the correct resolver, such as with Generics.

Async
-----

Remaining consistent with the rest of Koda Validate :data:`validate_signature` also
supports ``async`` functions.

.. testcode:: async1

    from koda_validate.signature import *

    @validate_signature
    async def save_data(version: int, data: dict[str, str]) -> None:
        # do some async saving logic
        return None

When used on async functions, the validators assigned by :data:`validate_signature`
run asynchronously. This means you can have any kind of async validation taking place. For instance,
if we want to change this code to check an external service to make sure we're using the latest
version, we could do something like this:


.. testcode:: async2

    from typing import Annotated
    from koda_validate import *
    from koda_validate.signature import *

    class CheckLatestVersion(PredicateAsync[int]):
        async def validate_async(self, val: int) -> bool:
            # should be something like
            # latest_version = await get_latest_version(val)

            # for simplicity, we'll pretend the service returned 5
            latest_version = 5
            return val == latest_version

    @validate_signature
    async def save_data(
        version: Annotated[int,
                           IntValidator(predicates_async=[CheckLatestVersion()])],
        data: dict[str, str]
    ) -> None:
        # do some async saving logic
        return None

Usage:

.. doctest:: async2

    >>> import asyncio
    >>> asyncio.run(save_data(5, {"name": "Bob Loblaw"}))  # returns None
    >>> asyncio.run(save_data(4, {"name": "Bob Loblaw"}))
    Traceback (most recent call last):
    ...
    koda_validate.signature.InvalidArgsError:
    Invalid Argument Values
    -----------------------
    version=4
        PredicateErrs
            <CheckLatestVersion object at 0x1059a2e90>


Caveats
-------

As with data validation, type inference is limited. If Koda Validate cannot
infer a specific validator for a type, it will fallback to a class instance check
-- if the type is a class. The most obvious cases this fails to cover are generics. In these
cases, it's usually best to provide your own :class:`Validator` through
:ref:`how_to/runtime_type_checking:Annotated Validators` or
:ref:`how_to/runtime_type_checking:Overrides`.