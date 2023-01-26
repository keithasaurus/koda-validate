Coercion
========

.. module:: koda_validate
    :noindex:

Coercion is a fundamental part of validation, and Koda Validate allows users
to customize how it works. For example, if we want to allow an :class:`IntValidator`
instance to coerce strings into integers, we can simply define a :class:`Coercer` to
do this.

.. testcode:: coerce

    from koda_validate import *
    from koda.maybe import *

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

The decorator :data:`coercer` requires the types that are potentially valid. In this example,
all ``int``\s are and some ``str``\s can be coerced, so the two types passed as arguments
are ``str`` and ``int``. These types are just metadata: they allow us to be able to communicate
which types can be coerced; they have no effect on validation.
