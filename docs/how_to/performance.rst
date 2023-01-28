Performance
===========

.. module:: koda_validate
    :noindex:

Koda Validate is reasonably fast (for Python). It tends to be :ref:`significantly faster
than Pydantic <faq/pydantic:Pydantic Comparison>`, for instance. There are several known
things you can do if you really need to eek out every ounce of performance.

Use asyncio for IO
------------------
Use ``asyncio``-based validation wherever you need to do IO during validation. Even if this
is not a common need, it merits mentioning first because:

- switching to async validation in Koda Validate is relatively simple
- the performance gains can be orders of magnitude in some cases

Initialize Validators in Outer Scopes
------------------------------------------------------------------------

Ideally, :class:`Validator`\s should be initialized at the module level. If that's not possible, initializing them
either lazily (once), or as few times as possible (i.e. not for every validated value) is advantageous because:

- often there's no need to initialize a :class:`Validator` for each value being validated; and initialization is not always cheap
- many of the :class:`Validator`\s in Koda Validate are optimized on the assumption they will be initialized less often than they'll be called

Slower
^^^^^^

.. testsetup:: slowinit

    from typing import TypedDict, Any
    from koda_validate import *


.. testcode:: slowinit

    class Book(TypedDict):
        title: str
        author: str


    def some_request_handler(data: Any) -> ValidationResult[Book]:
        # the validator is initialized every time `some_request_handler` is called
        return TypedDictValidator(Book)(data)

Faster
^^^^^^

.. testsetup:: fastinit

    from typing import TypedDict, Any
    from koda_validate import *


.. testcode:: fastinit

    class Book(TypedDict):
        title: str
        author: str

    # the validator is initialized once
    book_validator = TypedDictValidator(Book)


    def some_request_handler(data: Any) -> ValidationResult[Book]:
        return book_validator(data)

--------------------

Use a Cache
-----------

Koda Validate provides :class:`CacheValidatorBase`, a caching layer you can wrap
:class:`Validator`\s with. You will need to subclass :class:`CacheValidatorBase`
to work with whatever caching backend you have.

In this example, we'll use a basic ``dict`` to act as a cache.

.. testcode:: cache

    from dataclasses import dataclass, field
    from typing import Dict, Any, TypeVar
    from koda import Maybe, Just, nothing
    from koda_validate import (CacheValidatorBase, ValidationResult, ListValidator,
                               StringValidator, IntValidator)

    A = TypeVar('A')

    @dataclass
    class DictCacheValidator(CacheValidatorBase[A]):
        _dict_cache: Dict[Any, ValidationResult[A]] = field(default_factory=dict)

        def cache_get_sync(self, val: Any) -> Maybe[ValidationResult[A]]:
            if val in self._dict_cache:
                return Just(self._dict_cache[val])
            else:
                return nothing

        def cache_set_sync(self, val: Any, cache_val: ValidationResult[A]) -> None:
            self._dict_cache[val] = cache_val

.. warning::

    It is generally unwise to use an boundlessly expanding ``dict`` as we have in our
    example -- it will continuously increase its memory footprint. Please don't reuse
    this code for anything in production!


The validator should behave as the wrapped :class:`Validator` normally would:

.. doctest:: cache

    >>> cached_int_validator = DictCacheValidator(IntValidator())
    >>> cached_int_validator(5)  # cache miss
    Valid(val=5)
    >>> cached_int_validator(5)  # cache hit
    Valid(val=5)
    >>> cached_int_validator("a string")  # cache miss
    Invalid(err_type=TypeErr(expected_type=<class 'int'>), ...)
    >>> cached_int_validator("a string")  # cache hit
    Invalid(err_type=TypeErr(expected_type=<class 'int'>), ...)

.. note::

    This example uses a simple :class:`IntValidator` in synchronous mode for simplicity.
    Caching will not offer big gains in all cases. It is probably most useful in async
    contexts, or where validators are performing a lot of computation.

Because we can compose :class:`Validator`\s, caching can be done with as much granularity
as you need. Here we'll only use a cache for the items of the list, but the list in total
will not use a cache.

.. testcode:: cache

    validator = ListValidator(DictCacheValidator(StringValidator()))

.. note::

    Of course, if you want a different API for caching, you're free to write your own
    caching wrapper. It's probably worth taking a look at the :class:`CacheValidatorBase`
    source code. It's not complicated.

---------------------

Look at koda_validate._internals
----------------------------------------------

There are a few classes in ``_internals.py`` that are optimized for speed. For instance,
most of the built-in :class:`Validator`\s subclass ``_ToTupleValidator``.

The contents of ``koda_validate._internals`` may change without notice. You can use some
of the base classes in there at your own risk, or just mimic some of the patterns.

--------------------

Compile Parts of Koda Validate
------------------------------

Koda Validate is not compiled. `mypyc <https://mypyc.readthedocs.io/en/latest/>`_ can
trivially compile parts of the code. It would probably not be incredibly difficult to
alter the source code in a way that facilitates greater speedups from mypyc. Significant
speedups are definitely possible.

.. note::

    Compiling Koda Validate is not in any immediate plans, for a few reasons:

    - Koda Validate is already generally faster than competing libraries
    - Compilation requires a strategy -- especially since some kinds of compilation can complicate extension
    - It's easier to add new features -- and to refactor -- without an extra compilation step
    - CPython itself is getting faster. 3.11 is significantly faster than 3.10. 3.12 is meant to be faster still.

    Depending on how things evolve, this my change.