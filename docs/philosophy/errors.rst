Errors
======

In Koda Validate, validation errors are represented by the ``Invalid`` class. ``Invalid`` has three
public instance attributes:

- ``err_type``: the specific kind of error
- ``value``: the value that was being validated
- ``validator``: a reference to the ``Validator`` where the error occurred

``Invalid`` does not contain any sort of message, nor does it conform to needs of specific serialiation formats.
Instead, the intent of ``Invalid`` is to provide enough context to produce any kind of derivative data, whether
human- or machine-readable.

Producing Useful Information
----------------------------
In Koda Validate, ``Invalid`` errors typically form into trees. For example, the error type ``KeyErrs``
contains a dictionary, of which the keys serve as edges and the values as the child nodes:

.. code-block:: python

    Invalid(
        KeyErrs({
            "name": Invalid(TypeErr(str), ...),
            "address": Invalid(
                KeyErrs({
                    "city": Invalid(MissingKeyErr(), ...)
                })
            )
        }),
        ...
    )

We can process these errors in the same we might process any tree, accumulating information as we visits nodes. The is
how ``koda_validate.serialization.errors.to_serializable_errs`` works:

.. code-block:: python

    class Person(TypedDict):
        name: str
        age: int

    validator = TypedDictValidator(Person)

    result = validator({"age": False})

    assert isinstance(result, Invalid)

    to_serializable_errs(result)
    # > {'age': ['expected an integer'], 'name': ['key missing']}

Of course, the point of Koda Validate's error design is that we can produce arbitrary output formats, so we'll build
something a little different. We'll assume we need a "flat" representation of errors. A simple way to do this is just to
recursively branch on the error types. Here's how we could do that:

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
        invalid: Invalid, location: Optional[List[Union[str, int]]] = None
    ) -> List[FlatError]:
        """
        recursively add errors to a flat list
        """
        loc = location or []
        err_type = invalid.err_type

        if err_type is TypeErr:
            return [FlatError(loc, ErrCode.TYPE_ERR, err_type.expected_type)]

        elif err_type is MissingKeyErr:
            return [FlatError(loc, ErrCode.KEY_MISSING)]

        elif err_type is KeyErrs:
            errs = []
            for k, inv_v in err_type.keys.items():
                errs.extend(to_flat_errs(inv_v, loc + [k]))
            return errs

        elif err_type is IndexErrs:
            errs = []
            for i, inv_item in err_type.indexes.items():
                errs.extend(to_flat_errs(inv_item, loc + [i]))
            return errs

        else:
            raise TypeError("unhandled type")


.. note::

    The only thing we really checked in the above was the ``err_type``, but we could have also branched on
    the ``invalid.value`` or ``invalid.validator`` if we wanted to produce richer output.


Let's see how this works:

.. code-block:: python

    class Person(TypedDict):
        name: str
        age: int

    validator = ListValidator(TypedDictValidator(Person))

    root_error_result = validator({})

    assert isinstance(root_error_result, Invalid)

    assert to_flat_errs(root_error_result) == [
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

As you can see, it's relatively easy to use to produce practically any kind of structure for any target format.

Error Types
-----------
The ``err_type`` attribute of an ``Invalid`` instance corresponds to a specific type: ``ErrType``. ``ErrType`` is a
``Union`` type that looks like this:

.. code-block:: python

    ErrType = Union[
        CoercionErr,
        ContainerErr,
        ExtraKeysErr,
        IndexErrs,
        KeyErrs,
        MapErr,
        MissingKeyErr,
        PredicateErrs,
        SetErrs,
        TypeErr,
        ValidationErrBase,
        UnionErrs,
    ]


Each of the ``ErrType`` variants represents some distinct use case (have a look over them!), with one exception: ``ValidationErrBase``. ``ValidationErrBase``
is explicitly intended to be subclassed for any need not covered by the core ``ErrType``\s. One example of such a subclass
is ``koda_validate.serialization.errors.SerializableErr``, but you can feel free to define any custom error as a subclass
of ``ValidationErrBase`` and type checks should succeed.