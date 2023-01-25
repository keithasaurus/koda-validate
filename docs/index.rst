.. Koda Validate documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:00:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Koda Validate
=========================================

.. module:: koda_validate
   :noindex:

Build typesafe validators :ref:`automatically<index:Derived Validators>`
or explicitly -- or :ref:`write your own<how_to/extension:Extension>`. Combine them to
for arbitrarily complex validation logic. Koda Validate is async-friendly, pure
Python, and 1.5x - 12x faster :ref:`than Pydantic<faq/pydantic:Pydantic Comparison>`.

New in 3.1: :ref:`how_to/runtime_type_checking:Runtime Type Checking`


Basic Usage
^^^^^^^^^^^

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
are raised.

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

   from typing import List, TypedDict
   from koda_validate import *

   class Person(TypedDict):
       name: str
       hobbies: List[str]

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

   print(validator("abc123"))

Outputs:

.. testoutput:: refinement

   Valid(val='abc123')

.. note::

   ``MinLength(5)``, ``MaxLength(10)``, and ``StartsWith("a")`` are all :ref:`philosophy/predicates:Predicates`.


----------------


Nested Validators
^^^^^^^^^^^^^^^^^

We can build complex nested :class:`Validator`\s with ease.

.. testcode:: nested

   from typing import Annotated, Union, TypedDict, Literal, List
   from koda_validate import *


   class Group(TypedDict):
       name: str
       members: List[str]

   class Song(TypedDict):
       artist: Union[List[str], Group, Literal["unknown"]]
       title: str
       duration_seconds: int

   song_validator = TypedDictValidator(Song)

   stonehenge = {
       "artist": {
           "name": "Spinal Tap",
           "members": ["David St. Hubbins", "Nigel Tufnel", "Derek Smalls"]
       },
       "title": "Stonehenge",
       "duration_seconds": 276
   }

   drinkinstein = {
       "artist": ["Sylvester Stallone", "Dolly Parton"],
       "title": "Drinkin' Stein",
       "duration_seconds": 215
   }


Usage:

.. doctest:: nested

   >>> song_validator(stonehenge)
   Valid(...)

   >>> song_validator(drinkinstein)
   Valid(...)

   >>> song_validator({
   ...     "artist": "unknown",
   ...     "title": "druids chanting, archival recording number 10",
   ...     "duration_seconds": 4_000
   ... })
   Valid(...)



It's easy to keep nesting validators:

.. testcode:: nested

   # a list of songs
   songs_validator = ListValidator(song_validator, predicates=[MinItems(2)])

   class Playlist(TypedDict):
      title: str
      songs: Annotated[List[Song], songs_validator]
   
   playlist_validator = TypedDictValidator(Playlist)

.. note::

   :class:`TypedDictValidator`, :class:`DataclassValidator` and :class:`NamedTupleValidator` will :ref:`use Annotated Validators<how_to/dictionaries/derived:Annotated>` if found.

Usage:

.. doctest:: nested

   >>> playlist_validator({
   ...    "title": "My Favorite Songs",
   ...    "songs": [stonehenge, drinkinstein]
   ... })
   Valid(...)

---------------------

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
needs. As long as you obey the typing rules when building custom :class:`Validator`\s,
you should be able to combine them with built-in :class:`Validator`\s, however you wish.
For guidance, take a look at :ref:`how_to/extension:Extension`.

-----------------

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   setup/installation
   setup/type-checking


.. toctree::
   :maxdepth: 3
   :caption: Examples and Guides


   how_to/results
   how_to/dictionaries
   how_to/rest_apis
   how_to/runtime_type_checking
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
   api/koda_validate.signature


.. toctree::
   :maxdepth: 3
   :caption: Philosophy

   philosophy/overview
   philosophy/validators
   philosophy/predicates
   philosophy/processors
   philosophy/coercion
   philosophy/async
   philosophy/errors


.. toctree::
   :maxdepth: 3
   :caption: FAQ

   faq/pydantic
