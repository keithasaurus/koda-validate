IsDictValidator
===============

.. module:: koda_validate
    :noindex:

All :class:`IsDictValidator` does is check if an object is a dictionary. You
don't need to initialize it, you can just load :data:`is_dict_validator`.

.. doctest::

    >>> from koda_validate import is_dict_validator

    >>> is_dict_validator({})
    Valid(val={})

    >>> is_dict_validator({"a": 1, "b": None})
    Valid(val={'a': 1, 'b': None})

    >>> is_dict_validator(None)
    Invalid(err_type=TypeErr(expected_type=<class 'dict'>), value=None, validator=IsDictValidator())

