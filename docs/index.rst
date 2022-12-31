.. Koda Validate documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:00:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Koda Validate
=========================================

Koda Validate is a library focused on composable, type-safe data validation. It supplies a wide array of
validators out-of-the-box, but it also encourages users to build their own validators.


Scalars
^^^^^^^

.. code-block:: python

   from koda_validate import *

   validator = StringValidator()

   result = validator("a string")

   print(result)
   # > Valid("a string")

   print(result.val)
   # > "a string"


Collections
^^^^^^^^^^^

.. code-block:: python

   from koda_validate import *

   list_int_validator = ListValidator(IntValidator())

   list_int_validator([1,2,3])
   # > Valid([1,2,3])



Derived Validators
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from typing import TypedDict
   from koda_validate import *

   class Person(TypedDict):
       name: str
       hobbies: list[str]

   validator = TypedDictValidator(Person)

   validator({"name": "Bob",
              "hobbies": ["eating", "coding", "sleeping"]})
   # > Valid({'name': 'Bob',
   #          'hobbies': ['eating', 'coding', 'sleeping']})


Refinement
^^^^^^^^^^

.. code-block:: python

   from koda_validate import *

   validator = StringValidator(MinLength(5),
                               MaxLength(10),
                               StartsWith("a"))

   validator("abc123")
   # > Valid("abc123")

   validator("abc")
   # > Invalid(...)  # too short


Writing your own
^^^^^^^^^^^^^^^^

.. code-block:: python

   from typing import Any
   from koda_validate import *


   class IntegerValidator(Validator[int]):
      def __call__(val: Any) -> ValidationResult[int]:
         if isinstance(val, int):
            return Valid(val)
         else:
            return Invalid(TypeErr(int), val, self)

   validator = IntegerValidator()

   validator(5)
   # > Valid(5)

   validator("not an integer")
   # > Invalid(...)

.. toctree::
   :maxdepth: 2
   :caption: Setup

   setup/installation
   setup/type-checking


.. toctree::
   :maxdepth: 3
   :caption: Examples and Guides

   how_to/rest_apis
   how_to/results
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

