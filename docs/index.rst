.. Koda Validate documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:00:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Koda Validate
=========================================

Koda Validate is a library focused on composable, type-safe data validation.


At a glance
^^^^^^^^^^^

**Scalars**

.. code-block:: python

   from koda_validate import *

   str_validator = StringValidator(MinLength(5))

   result = str_validator("long enough")

   print(result)
   # > Valid("long enough")

   print(result.val)
   # > "long enough"


**Collections**

.. code-block:: python

   from koda_validate import *

   list_int_validator = ListValidator(IntValidator())

   list_int_validator([1,2,3])
   # > Valid([1,2,3])


**Derived Validators**

.. code-block:: python

   from typing import TypedDict
   from koda_validate import *

   class Person(TypedDict):
       name: str
       hobbies: list[str]

   person_validator = TypedDictValidator(Person)

   person_validator({"name": "Bob",
                     "hobbies": ["eating", "coding", "sleeping"]})
   # > Valid({'name': 'Bob',
   #          'hobbies': ['eating', 'coding', 'sleeping']})

Koda Validate can validate based on explicit definition, or by inspecting typehints. Even when
validators are derived, Koda Validate allows for user overrides to customize behavior.

.. toctree::
   :maxdepth: 2
   :caption: Setup

   setup/installation
   setup/type-checking

.. toctree::
   :maxdepth: 3
   :caption: Philosophy

   philosophy/overview
   philosophy/validators
   philosophy/predicates
   philosophy/processors
   philosophy/extension
   philosophy/metadata
   philosophy/async


.. toctree::
   :maxdepth: 3
   :caption: Working with Koda Validate

   working_with/api
