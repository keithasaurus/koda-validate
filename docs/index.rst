.. Koda Validate documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:00:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Koda Validate
=========================================

.. module:: koda_validate
   :noindex:

- :ref:`type-driven<setup/type-checking:Type Checking>`
- :ref:`composable<philosophy/validators:Validators>`
- :ref:`extensible<how_to/extension:Extension>`
- :ref:`async-compatible<how_to/async:Async>`

Build validators :ref:`automatically<index:Derived Validators>`
or explicitly. Combine them to build validators of arbitrary complexity.


At a Glance
-----------

Scalars
^^^^^^^

.. testcode:: scalars

   from koda_validate import *

   my_first_validator = StringValidator()

Easy enough. Let's see how it works:

.. doctest:: scalars

   >>> my_first_validator("a string")
   Valid(val='a string')

   >>> my_first_validator(0)
   Invalid(err_type=TypeErr(expected_type=<class 'str'>), ...)

For both valid and invalid cases, we can see that we get a result back -- no exceptions
are thrown (note that we truncated the representation of the :class:`Invalid` instance for brevity).

Working with :class:`Valid` and :class:`Invalid` types is covered more in
:ref:`how_to/results:Validation Results`.

----------------


Collections
^^^^^^^^^^^

.. testcode:: collections

   from koda_validate import *

   list_int_validator = ListValidator(IntValidator())

Nesting validators works as one might expect.

.. doctest:: collections

   >>> list_int_validator([1,2,3])
   Valid(val=[1, 2, 3])

----------------


Derived Validators
^^^^^^^^^^^^^^^^^^

Koda Validate can inspect typehints and build :class:`Validator<koda_validate.Validator>`\s automatically.

.. testcode:: derived

   from typing import TypedDict
   from koda_validate import *

   class Person(TypedDict):
       name: str
       hobbies: list[str]

   validator = TypedDictValidator(Person)

Usage:

.. doctest:: derived

   >>> validator({"name": "Bob", "hobbies": ["eating", "coding", "sleeping"]})
   Valid(val={'name': 'Bob', 'hobbies': ['eating', 'coding', 'sleeping']})

See :ref:`how_to/dictionaries/derived:Derived Validators` for more.


----------------


Refinement
^^^^^^^^^^

.. testcode:: refinement

   from koda_validate import *

   validator = StringValidator(MinLength(5),
                               MaxLength(10),
                               StartsWith("a"))

   validator("abc123")

Outputs:

.. testoutput::

   Valid(val="abc123")

``MinLength(5)`` and ``MaxLength(10)`` are examples of :ref:`philosophy/predicates:Predicates`.
``StartsWith("a")`` is a :ref:`Processor<philosophy/processors:Processors>`.

----------------


Custom Validators
^^^^^^^^^^^^^^^^^

.. testcode:: own1

   from typing import Any
   from koda_validate import *


   class IntegerValidator(Validator[int]):
      def __call__(self, val: Any) -> ValidationResult[int]:
         if isinstance(val, int):
            return Valid(val)
         else:
            return Invalid(TypeErr(int), val, self)

Usage:

.. doctest:: own1

   >>> validator = IntegerValidator()
   >>> validator(5)
   Valid(val=5)

   >>> invalid_result = validator("not an integer")
   >>> invalid_result.err_type
   TypeErr(expected_type=<class 'int'>)

In Koda Validate, you are encouraged to write your own :class:`Validator`\s for custom
needs. For more guidance, take a look at :ref:`how_to/extension:Extension`.

-----------------

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Setup

   setup/installation
   setup/type-checking


.. toctree::
   :maxdepth: 3
   :caption: Examples and Guides


   how_to/results
   how_to/dictionaries
   how_to/rest_apis
   how_to/async
   how_to/extension
   how_to/metadata
   how_to/performance
   how_to/type-checking

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/koda_validate
   api/koda_validate.serialization


.. toctree::
   :maxdepth: 3
   :caption: Philosophy

   philosophy/overview
   philosophy/validators
   philosophy/predicates
   philosophy/processors
   philosophy/async
   philosophy/errors


.. toctree::
   :maxdepth: 3
   :caption: FAQ

   faq/pydantic
