Performance
===========

.. module:: koda_validate

Koda Validate is reasonably fast (for Python). It tends to be :ref:`significantly faster
than Pydantic <faq/pydantic:Pydantic Comparison>`, for instance. There are several known
things you can do if you really need to eek out every ounce of performance.

Use asyncio for IO
------------------
Use ``asyncio``-based validation wherever you need to do IO during validation. This is not likely to be a common case,
but it merits mentioning first because:

- switching to async validation in Koda Validate is relatively simple
- the performance gains can be orders of magnitude in some cases

Initialize Validators in Outer Scopes
------------------------------------------------------------------------

Ideally, :class:`Validator`\s should be initialized at the module level. If that's not possible, we want to try to initialize them
either lazily (once), or as few times as possible (i.e. not for every validated value) because:

- often there's no need to initialize them for every value being validated, and initialization is not always cheap
- many of the :class:`Validator`\s in Koda Validate are optimized on the assumption they will be initialized less often than they'll be called

Slower
^^^^^^

.. code-block:: python

    class Book(TypedDict):
        title: str
        author: str


    def some_request_handler(data: Any) -> ValidationResult[Book]:
        # the validator is initialized every time this function is called
        return TypedDictValidator(Book)(data)

Faster
^^^^^^

.. code-block:: python

    class Book(TypedDict):
        title: str
        author: str

    # the validator is initialized once
    book_validator = TypedDictValidator(Book)


    def some_request_handler(data: Any) -> ValidationResult[Book]:
        return book_validator(data)


Look at koda_validate._internals
----------------------------------------------

There are a few classes in ``_internals.py`` that are optimized for speed. For instance,
most of the built-in :class:`Validator`\s subclass ``_ToTupleValidator``.

The contents of ``koda_validate._internals`` may change without notice. You can use some
of the base classes in there at your own risk, or just mimic some of the patterns.


Compile Parts of Koda Validate
------------------------------

Koda Validate is not compiled. `mypyc <https://mypyc.readthedocs.io/en/latest/>`_ can
trivially compile parts of the code. It would probably not be incredibly difficult to
alter the source code in a way that facilitates greater speedups from mypyc. Significant
speedups are definitely possible.
