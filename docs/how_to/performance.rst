Performance
===========

Koda Validate is not typically slow, but there are some things you can do if you really need to eek out every ounce of
performance.

asyncio
-------
Use ``asyncio``-based validation wherever you need to do IO during validation. This is not likely to be a common case,
but it merits mentioning first because:

- switching to async validation in Koda Validate is relatively simple
- the gains you can get can be orders of magnitude faster in some cases

Initialize ``Validator``\s in Outer Scopes
------------------------------------------

Ideally, we want to initialize validators at the module. If that's not possible, we want to try to initialize it in
the outer-most scope possible level because:

- often there's no need to initialize them for every value being validated
- many of the ``Validators`` in Koda Validate assume that validators will not be initialized as often as they are called, so they perform optimization
during initialization

Slower:

.. code-block:: python

    class Book(TypedDict):
        title: str
        author: str


    def some_request_handler(data: Any) -> ValidationResult[Book]:
        return TypedDictValidator(Book)(data)

Faster:

.. code-block:: python

    class Book(TypedDict):
        title: str
        author: str

    book_validator = TypedDictValidator(Book)


    def some_request_handler(data: Any) -> ValidationResult[Book]:
        return book_validator(data)


