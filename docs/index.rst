.. Koda Validate documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:00:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Koda Validate
=========================================

Koda Validate aims to make validation flexible, easy-to-maintain, and fast -- in both
performance and development velocity. It does this with a type-safe and composable
definition of validation.

A wide array of validators are provided out-of-the-box, but Koda Validate also attempts
allows for straightforward extension to suit whatever validation needs you have.


Scalars
^^^^^^^

.. testcode:: scalars

   from koda_validate import *

   validator = StringValidator()

   result = validator("a string")

   print(result)

Outputs

.. testoutput:: scalars

   Valid(val='a string')


Collections
^^^^^^^^^^^

.. testcode:: collections

   from koda_validate import *

   list_int_validator = ListValidator(IntValidator())

   list_int_validator([1,2,3])

Outputs

.. testoutput::

   Valid(val=[1,2,3])



Derived Validators
^^^^^^^^^^^^^^^^^^

.. testcode:: derived

   from typing import TypedDict
   from koda_validate import *

   class Person(TypedDict):
       name: str
       hobbies: list[str]

   validator = TypedDictValidator(Person)

   result = validator({"name": "Bob",
                       "hobbies": ["eating", "coding", "sleeping"]})

   print(result)

Outputs

.. testoutput:: derived

   Valid(val={'name': 'Bob', 'hobbies': ['eating', 'coding', 'sleeping']})


Refinement
^^^^^^^^^^

.. testcode:: refinement

   from koda_validate import *

   validator = StringValidator(MinLength(5),
                               MaxLength(10),
                               StartsWith("a"))

   validator("abc123")

Outputs

.. testoutput::

   Valid(val="abc123")


Writing your own
^^^^^^^^^^^^^^^^

.. testcode:: own1

   from typing import Any
   from koda_validate import *


   class IntegerValidator(Validator[int]):
      def __call__(self, val: Any) -> ValidationResult[int]:
         if isinstance(val, int):
            return Valid(val)
         else:
            return Invalid(TypeErr(int), val, self)

Let's use it.

.. doctest:: own1

   >>> validator = IntegerValidator()
   >>> validator(5)
   Valid(val=5)

   >>> invalid_result = validator("not an integer")
   >>> invalid_result.err_type
   TypeErr(expected_type=<class 'int'>)

.. toctree::
   :maxdepth: 2
   :caption: Setup

   setup/installation
   setup/type-checking


.. toctree::
   :maxdepth: 3
   :caption: Examples and Guides


   how_to/results
   how_to/rest_apis
   how_to/async
   how_to/performance
   how_to/extension
   how_to/metadata
   how_to/type-checking


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
   :caption: API Reference

   api_reference/typeddictvalidator
