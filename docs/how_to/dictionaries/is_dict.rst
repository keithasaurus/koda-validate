IsDictValidator
===============

.. module:: koda_validate
    :noindex:

All :class:`IsDictValidator` does is check if an object is a dictionary. You
don't need to initialize it, you can just load :data:`is_dict_validator`.

.. doctest::

    >>> from koda_validate import is_dict_validator

    >>> is_dict_validator(None)
    Invalid(TypeErr(dict), ...)

    >>> is_dict_validator({})
    Valid({})

    >>> is_dict_validator({"a": 1, "b": None})
    Valid({'a': 1, 'b': None})
