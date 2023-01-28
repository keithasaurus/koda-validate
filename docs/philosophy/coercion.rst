Coercion
========

.. module:: koda_validate
    :noindex:

Coercion is a fundamental part of validation that happens at the start. In Koda Validate
coercion is expressed through the function signature:

.. testsetup:: coercer

    from typing import TypeVar, Callable, Any
    from koda import Maybe

.. testcode:: coercer

    A = TypeVar('A')

    Callable[[Any], Maybe[A]]

Where ``A`` corresponds to the generic parameter of a some ``Validator[A]``. Koda Validate
allows users to customize how coercion works. For example, to allow an :class:`IntValidator`
instance to coerce strings into integers, we can simply define a :class:`Coercer` to
do this.

.. testcode:: coerce

    from typing import Any
    from koda_validate import coercer, Valid, Invalid, IntValidator
    from koda.maybe import Maybe, Just, nothing

    @coercer(int, str)
    def allow_coerce_str_to_int(val: Any) -> Maybe[int]:
        if type(val) is int:
            return Just(val)
        elif type(val) is str:
            try:
                return Just(int(val))
            except ValueError:
                return nothing
        else:
            return nothing


    validator = IntValidator(coerce=allow_coerce_str_to_int)

    # ints work
    assert validator(5) == Valid(5)

    # valid int strings work
    assert validator("5") == Valid(5)

    # invalid strings fail
    assert isinstance(validator("abc"), Invalid)

.. note::

    :data:`coercer` is a convenience wrapper for :class:`Coercer`

The decorator :data:`coercer` accepts the types that are potentially valid. In this example,
all ``int``\s are and some ``str``\s can be coerced, so the two types passed as arguments
are ``str`` and ``int``. These types are just metadata: they allow us to be able to communicate
which types can be coerced; they have no effect on validation.
