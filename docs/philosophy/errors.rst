Errors
======

In Koda Validate, validation errors are represented by the ``Invalid`` class. ``Invalid`` has three
public instance attributes:

- ``err_type``: the specific kind of error (``ErrType``)
- ``value``: the value that was being validated
- ``validator``: a reference to the ``Validator`` itself

``Invalid`` does not contain any sort of message or error code ontology. Instead, the intent of ``Invalid`` is to
provide enough context to produce any kind of derivative data data, whether human- or machine-readable. Koda Validate
does exactly this with ``serialization.errors.to_serializable_errs``, which produces human-readble error messages
suitable for JSON or YAML serialization.

.. code-block:: python

    class Person(TypedDict):
        name: str
        age: int

    validator = TypedDictValidator(Person)

    result = validator({"age": False})

    to_serializable_errs(result)
    # > {'age': ['expected an integer'], 'name': ['key missing']}

You could write your own interpreter for errors:

.. code-block:: python

    to_some_other_format(result)

The way you might go about writing this code (and how it's done in ``to_serializable_errs`` is simply to branch
on the types of errors, validators, and value. This can be surprisingly straightforward and powerful. Here's a stub of how you
might build up a list of "flat" errors:

.. code-block:: python

    from dataclasses import dataclass
    from enum import Enum
    from typing import TypedDict, List, Union, Any, Optional

    from koda_validate import *


    class ErrCode(Enum):
        TYPE_ERR = 0
        KEY_MISSING = 1


    @dataclass
    class FlatError:
        location: List[Union[int, str]]
        err_code: ErrCode
        extra: Any = None


    def to_flat_errs(
        invalid: Invalid,
        location: Optional[List[Union[str, int]]] = None
    ) -> List[FlatError]:
        loc = location or []
        err_type = invalid.err_type
        if isinstance(err_type, TypeErr):
            return [FlatError(loc, ErrCode.TYPE_ERR, err_type.expected_type)]
        elif isinstance(err_type, MissingKeyErr):
            return [FlatError(loc, ErrCode.KEY_MISSING)]
        elif isinstance(err_type, KeyErrs):
            errs = []
            for k, inv_v in err_type.keys.items():
                errs.extend(to_flat_errs(inv_v, loc + [k]))
            return errs
        elif isinstance(err_type, IndexErrs):
            errs = []
            for i, inv_item in err_type.indexes.items():
                errs.extend(to_flat_errs(inv_item, loc + [i]))
            return errs


Note that the only thing we really checked in the above was the ``err_type``, but we could have also branched on the Validator being used or the value (especially if the value is something we want to use). Let's
see how our interpreter works:

.. code-block:: python

    class Person(TypedDict):
        name: str
        age: int


    validator = ListValidator(TypedDictValidator(Person))

    simple_result = validator({})
    assert isinstance(simple_result, Invalid)
    assert to_flat_errs(simple_result) == [
        FlatError(location=[], err_code=ErrCode.TYPE_ERR, extra=list)
    ]

    complex_result = validator([None, {}, {"name": "Bob", "age": "not an int"}])
    assert isinstance(complex_result, Invalid)
    assert to_flat_errs(complex_result) == [
        FlatError(location=[0], err_code=ErrCode.TYPE_ERR, extra=dict),
        FlatError(location=[1, 'name'], err_code=ErrCode.KEY_MISSING, extra=None),
        FlatError(location=[1, 'age'], err_code=ErrCode.KEY_MISSING, extra=None),
        FlatError(location=[2, 'age'], err_code=ErrCode.TYPE_ERR, extra=int)
    ]

The only thing we really checked in the above was the ``err_type``, but we could have also branched on the
``Validator`` being used or the value (especially if the value is something we want to use).