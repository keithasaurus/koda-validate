Runtime Type Checking
=====================

.. module:: koda_validate.signature
    :noindex:

Koda Validate supports runtime type-checking via :data:`validate_signature`. :data`validate_signature`
can be used as a decorator that can to validate function arguments and return values at
runtime. By default, it will infer the validation logic to use by inspecting the typehints.

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

Customization
-------------
:data:`validate_signature` is wholly customizable, so it can fit practically any usecase.


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
You can use typing.Annotated to customize how a type signature is validated.

.. testcode:: annotated

    from koda_validate import *
    from koda_validate.signature import *
    from typing import Annotated

    @validate_signature
    def reverse_name(
        name: Annotated[str, StringValidator(MinLength(1), MaxLength(20))]
    ) -> Annotated[str, StringValidator(MinLength(1), MaxLength(20))]:
        return name[::-1]

Usage


.. doctest:: annotated

    >>> reverse_name("Jen")
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
        RETURN_OVERRIDE_KEY: StringValidator(MinLength(1), MaxLength(20))}
    })
    def reverse_name(name: str) -> str:
        return name[::-1]



Async
-----