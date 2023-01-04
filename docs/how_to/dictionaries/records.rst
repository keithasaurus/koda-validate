Records
=======

.. module:: koda_validate
    :noindex:

We use the term "record" to mean a dictionary where keys may have differing value types.
This is common, for instance, with deserialized JSON ``object``\s. In Python
code, you may see type annotations like ``Dict[str, Any]`` to represent such types.
``TypedDict``\s, ``dataclass``\es, and  ``NamedTuple``\s may also be used to express such
a type. In Koda Validate there are many built-in :class:`Validator`\s to suit these
purposes.

Derived Validators
------------------

:class:`TypedDictValidator`, :class:`DataclassValidator`, and :class:`NamedTupleValidator`
all accept ``dict``\s for validation, and have largely the same API.

.. testcode:: derived1

    from typing import Optional, TypedDict
    from koda_validate import *

    class Image(TypedDict):
        height: int
        width: int
        description: Optional[str]

    validator = TypedDictValidator(Image)

    assert validator({"height": 10, "width": 20, "description": None}) == Valid(
        {"height": 10, "width": 20, "description": None}
    )

Here's an equivalent example with :class:`DataclassValidator`

.. testcode:: derived2

    from typing import Optional
    from dataclasses import dataclass
    from koda_validate import *

    @dataclass
    class Image:
        height: int
        width: int
        description: Optional[str]

    validator = DataclassValidator(Image)

    assert validator({"height": 10, "width": 20, "description": None}) == Valid(
        Image(height=10, width=20, description=None)
    )

:class:`NamedTupleValidator` is almost identical to the example above, and is left as
an exercise for the reader.

The range of typehints that are covered by these validators is fairly extensive, and you
can build complex nested validators, even using things like ``Literal`` and ``Union``
types:

.. testcode:: complex

    from dataclasses import dataclass
    from typing import List, Literal, Optional, TypedDict, Union
    from koda_validate import TypedDictValidator, Valid


    @dataclass
    class Ingredient:
        quantity: Union[int, float]
        unit: Optional[Literal["teaspoon", "tablespoon"]]  # etc...
        name: str


    class Recipe(TypedDict):
        title: str
        ingredients: List[Ingredient]
        instructions: str

    recipe_validator = TypedDictValidator(Recipe)

    result = recipe_validator(
        {
            "title": "Peanut Butter and Jelly Sandwich",
            "ingredients": [
                {"quantity": 2, "unit": None, "name": "slices of bread"},
                {"quantity": 2, "unit": "tablespoon", "name": "peanut butter"},
                {"quantity": 4.5, "unit": "teaspoon", "name": "jelly"},
            ],
            "instructions": "spread the peanut butter and jelly onto the bread",
        }
    )

    assert isinstance(result, Valid)
    assert result.val["title"] == "Peanut Butter and Jelly Sandwich"


Optional Keys
^^^^^^^^^^^^^
Each of these validators allows certain keys to be absent in a dictionary, but the three
:class:`Validators`\s don't all share the same API.

:class:`DataclassValidator` and :class:`NamedTupleValidator` allow keys to be missing if a
default is defined.

.. testcode:: opt1

    from typing import NamedTuple
    from koda_validate import *

    class SomeType(NamedTuple):
        a: str
        b: int = 10

    validator = NamedTupleValidator(SomeType)

    assert validator({"a": "ok"}) == Valid(SomeType("ok", 10))


For :class:`TypedDictValidator`, Koda Validate abides by the contents of the
``__optional_keys__`` attribute. Take a look at the `TypedDict docs <https://docs.python.org/3/library/typing.html#typing.TypedDict>`_ for
information on how to specific optional keys on ``TypedDict``\s.

Extra Keys
^^^^^^^^^^

:class:`TypedDictValidator`, :class:`DataclassValidator`, and :class:`NamedTupleValidator`
can all be made to fail if keys are found that are not in source class's definition.
Simply pass ``fail_on_unknown_keys=True`` at initialization.

.. testcode:: extrakeys

    from dataclasses import dataclass
    from koda_validate import *

    @dataclass
    class Example:
        a: str
        b: float

    test_dict = {"a": "ok", "b": 2.0, "c": None}

    validator_no_unknown_keys = DataclassValidator(Example, fail_on_unknown_keys=True)

    assert isinstance(validator_no_unknown_keys(test_dict), Invalid)

    validator_unknown_keys_ok = DataclassValidator(Example)

    assert isinstance(validator_unknown_keys_ok(test_dict), Valid)


Customization
^^^^^^^^^^^^^
It's common to need to customize the logic of these derived :class:`Validator`\s beyond
simple types. There are a few ways to do that.

Annotated
"""""""""
In Python 3.9+, you can simply use `Annotated` to add a custom :class:`Validator` for a given key.

.. testcode:: annotated

    from dataclasses import dataclass
    from typing import Annotated, Optional
    from koda_validate import *

    @dataclass
    class Image:
        height: Annotated[int, IntValidator(Min(10), Max(1000))]
        width: Annotated[int, IntValidator(Min(10), Max(1000))]
        description: Optional[str] = None

    validator = DataclassValidator(Image)

    assert validator({"height": 50, "width": 100, "description": "wow"}) == Valid(
        Image(50, 100, "wow")
    )

    assert validator({"height": 1, "width": 100, "description": "wow"}) == Invalid(
        KeyErrs({
            'height': Invalid(PredicateErrs([Min(10)]),
                              1,
                              IntValidator(Min(10), Max(1000)))}
        ),
        {'height': 1, 'width': 100, 'description': 'wow'},
        validator
    )


Overrides
"""""""""
If you're using Python3.8 or don't want to add ``Annotated`` to your class annotations,
you can use ``overrides={<key>: <validator>}``. The following will produce the same
:class:`Validator` as in the :ref:`Annotated example<how_to/dictionaries/records:Annotated>`.

.. testcode:: overrides

    from dataclasses import dataclass
    from typing import Annotated, Optional
    from koda_validate import *

    @dataclass
    class Image:
        height: int
        width: int
        description: Optional[str] = None

    validator = DataclassValidator(Image, overrides={
        "height": IntValidator(Min(10), Max(1000)),
        "width": IntValidator(Min(10), Max(1000))
    })

typehint_resolver
"""""""""""""""""

Another way to customize the logic is to specify a ``typehint_resolver``. This will
customize the way Koda Validate processes typehints. This will also produce the same
:class:`Validator` as in the :ref:`Annotated example<how_to/dictionaries/records:Annotated>`.

.. testcode:: typehintresolver

    from dataclasses import dataclass
    from typing import Any, Optional
    from koda_validate import *
    from koda_validate.typehints import get_typehint_validator_base, get_typehint_validator

    @dataclass
    class Image:
        height: int
        width: int
        description: Optional[str] = None

    def custom_resolver(annotations: Any) -> Validator[Any]:
        if annotations is int:
            return IntValidator(Min(10), Max(1000))
        else:
            return get_typehint_validator_base(get_typehint_validator, annotations)

    validator = DataclassValidator(Image, typehint_resolver=custom_resolver)


Derived Validator Caveats
^^^^^^^^^^^^^^^^^^^^^^^^^

Some notable limitations exist with these derived :class:`Validator`\s:

- the keys of the dictionaries must be strings
- the keys must abide by the relevant attribute name restrictions for the classes
- generic and custom types will usually require a custom :class:`Validator`

--------------------------------


RecordValidator
---------------
In many cases :class:`RecordValidator` is more verbose than the :ref:`Derived Validators<how_to/dictionaries/records:Derived Validators>`, but
it comes with greater flexibility.


.. testcode:: recordvalidator

    from dataclasses import dataclass
    from koda import Maybe, Just
    from koda_validate import *


    @dataclass
    class Person:
        name: str
        age: Maybe[int]


    person_validator = RecordValidator(
        into=Person,
        keys=(
            ("full name", StringValidator(not_blank, MaxLength(50))),
            ("age", KeyNotRequired(IntValidator(Min(0), Max(130)))),
        ),
    )


    match person_validator({"full name": "John Doe", "age": 30}):
        case Valid(person):
            match person.age:
                case Just(age):
                    age_message = f"{age} years old"
                case nothing:
                    age_message = "ageless"
            print(f"{person.name} is {age_message}")
        case Invalid(errs):
            print(errs)

Output:

.. testoutput:: recordvalidator

    John Doe is 30 years old

When validation becomes complex, it is sometimes the least verbose, and most direct option.

Record Validator Caveats
^^^^^^^^^^^^^^^^^^^^^^^^
The main caveats with :class:`RecordValidator` are:

- it works on a maximum of 16 keys
- type checkers don't always produces the most readable hints, as it uses ``@overload``\s.
- the target of validation must be defined outside the validator, and the order of arguments matters

DictValidatorAny
^^^^^^^^^^^^^^^^