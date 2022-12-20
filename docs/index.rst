.. Koda Validate documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:00:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. highlight:: python

Koda Validate documentation
=========================================

At a glance
-----------
::

   from typing import TypedDict
   from koda_validate import TypedDictValidator


   class Person(TypedDict):
       name: str
       hobbies: list[str]


   person_validator = TypedDictValidator(Person)
   person_validator({"name": "Bob", "hobbies": ["eating", "coding", "sleeping"]})
   # > Valid({'name': 'Bob', 'hobbies': ['eating', 'coding', 'sleeping']})



.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
