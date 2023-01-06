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

   validator("abc123")

Outputs:

.. testoutput::

   Valid(val="abc123")

``MinLength(5)`` and ``MaxLength(10)`` are examples of :ref:`philosophy/predicates:Predicates`.
``StartsWith("a")`` is a :ref:`Processor<philosophy/processors:Processors>`.

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


.. note::

   We excluded the :class:`Valid` contents for brevity.



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
needs. For guidance, take a look at :ref:`how_to/extension:Extension`.

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
