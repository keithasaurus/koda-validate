Errors
======

In Koda Validate, validation errors are represented by the ``Invalid`` class. ``Invalid`` has three
public instance attributes:

- ``err_type``: the specific kind of error
- ``value``: the value that was being validated
- :class:`Validator<koda_validate.Validator>`: a reference to the :class:`Validator<koda_validate.Validator>` where the error occurred

``Invalid`` does not contain any sort of message, nor does it attempt to accommodate any specific serialization format.
Instead, the intent of ``Invalid`` is to provide enough context to produce any kind of derivative data, whether
human- or machine-readable.


Error Types
-----------
The ``err_type`` attribute of an ``Invalid`` instance corresponds to a specific type: :class:`ErrType<koda_validate.ErrType>`. :class:`ErrType<koda_validate.ErrType>` is a
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


Each of the :class:`ErrType<koda_validate.ErrType>` variants represents some distinct use case (have a look over them!), with one exception: ``ValidationErrBase``. ``ValidationErrBase``
is explicitly intended to be subclassed for any need not covered by the core :class:`ErrType<koda_validate.ErrType>`\s. One example of such a subclass
is ``koda_validate.serialization.errors.SerializableErr``, but you can feel free to define any custom error as a subclass
of ``ValidationErrBase`` and type checks should succeed.

.. _flaterrs-example:

Converting ``Invalid`` to Other Formats
---------------------------------------
In Koda Validate, ``Invalid`` objects are not usually the final form you'll want for errors;
you'll usually want to convert them to something more useful for your specific
use case.

It's helpful to understand that ``Invalid`` errors typically form into trees (which mirror
the structure of the :class:`Validator<koda_validate.Validator>` they come from):

.. code-block:: python

    Invalid(
        KeyErrs({
            "name": Invalid(TypeErr(str), ...),
            "address": Invalid(
                ## any amount of nesting can be defined
                KeyErrs({
                    "city": Invalid(MissingKeyErr(), ...)
                })
            )
        }),
        ...
    )

We can process these errors in the same way we might process any tree: by accumulating
information as we visit all the nodes. For an example, let's assume we need a "flat"
list of human-readable errors. A simple way to do this is just to recursively
branch on the error types. Here's how we could do that:

.. testcode:: flaterrs

    from dataclasses import dataclass
    from enum import Enum
    from typing import TypedDict, List, Union, Any, Optional

    from koda_validate import *


    @dataclass
    class FlatError:
        location: List[Union[int, str]]
        message: str

    def to_flat_errs(
        invalid: Invalid, location: Optional[List[Union[str, int]]] = None
    ) -> List[FlatError]:
        """
        recursively add errors to a flat list
        """
        loc = location or []
        err_type = invalid.err_type

        if isinstance(err_type, TypeErr):
            return [FlatError(loc, f"expected type {err_type.expected_type}")]

        elif isinstance(err_type, MissingKeyErr):
            return [FlatError(loc, "missing key!")]

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

        else:
            raise TypeError(f"unhandled type {err_type}")


.. note::

    The only thing we really checked in the above was the ``err_type``, but we could have also branched on
    the ``invalid.value`` or ``invalid.validator`` if we wanted to produce richer output.


Let's see how this works:

.. testcode:: flaterrs

    class Person(TypedDict):
        name: str
        age: int


    validator = ListValidator(TypedDictValidator(Person))

    simple_result = validator({})
    assert isinstance(simple_result, Invalid)
    assert to_flat_errs(simple_result) == [
        FlatError(location=[], message=f"expected type <class 'list'>")
    ]

    complex_result = validator([None, {}, {"name": "Bob", "age": "not an int"}])
    assert isinstance(complex_result, Invalid)
    assert to_flat_errs(complex_result) == [
        FlatError(location=[0], message="expected type <class 'dict'>"),
        FlatError(location=[1, 'name'], message='missing key!'),
        FlatError(location=[1, 'age'], message='missing key!'),
        FlatError(location=[2, 'age'], message="expected type <class 'int'>")
    ]



One thing that we notably are *not* doing here is adding representation logic to ``Invalid``
or :class:`ErrType<koda_validate.ErrType>` instances; nor are we subclassing those objects and adding methods or data
there. This is because we don't want to couple our errors with any specific output format.
Instead the process to compute the final error output is always more-or-less the same:
just write a function (or use an existing one). There are a few advantages to this approach:

- it's easy to have many different output functions (different languages, formats, etc)
- it's easy to keep error outputs consistent -- you don't have to jump around from
  class to class in your codebase.

.. note::

    If you'd like to see a fuller example in the, take a look at the source code for
    ``koda_validate.serialization.errors.to_serializable_errs``
