Runtime Type Checking
=====================

.. module:: koda_validate.signature
    :noindex:

:data:`validate_signature` is a decorator that can for validating function arguments and
return values at runtime. If you don't pass any arguments arguments, it will infer the validation
to by inspecting the typehints.

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

:data:`validate_signature` will ``raise`` a :data:`InvalidArgsErr` when arguments
are invalid or :data:`InvalidReturnError` when the returned value is invalid.

Customization
-------------

Async
-----