Derived Validators
==================

.. module:: koda_validate
    :noindex:

:class:`TypedDictValidator`, :class:`DataclassValidator`, and :class:`NamedTupleValidator`
all accept ``dict``\s for validation, and largely share the same API. Here's a quick
example of using :class:`TypedDictValidator`:

.. testcode:: derived1

    from typing import Optional, TypedDict
    from koda_validate import TypedDictValidator, Valid

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
    from koda_validate import DataclassValidator, Valid

    @dataclass
    class Image:
        height: int
        width: int
        description: Optional[str]

    validator = DataclassValidator(Image)

    assert validator({"height": 10, "width": 20, "description": None}) == Valid(
        Image(height=10, width=20, description=None)
    )

.. note::
    A similar example for :class:`NamedTupleValidator` would be nearly identical to the
    :class:`DataclassValidator` example directly above. As such, it's left as an exercise
    for the reader.

Supported Typehints
-------------------

The range of typehints that are automatically converted to :class:`Validator`\s is fairly
extensive, and you can build complex nested validators, even using things like
``Literal`` and ``Union`` types:

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

If a typehint is not supported, an exception will be thrown. You can handle unhandled
typehints a with custom :ref:`how_to/dictionaries/derived:typehint_resolver` function.


Optional Keys
-------------

Each of these validators allows for the specification of optional keys, but the three
:class:`Validator`\s don't all share the same API. For :class:`DataclassValidator` and
:class:`NamedTupleValidator` keys are understood to be optional if a default value is defined
for a given attribute.

.. testcode:: opt1

    from typing import NamedTuple
    from koda_validate import NamedTupleValidator, Valid

    class SomeType(NamedTuple):
        a: str
        b: int = 10

    validator = NamedTupleValidator(SomeType)

    assert validator({"a": "ok"}) == Valid(SomeType("ok", 10))


For :class:`TypedDictValidator`, Koda Validate simply abides by the contents of the
``__optional_keys__`` attribute. Take a look at the `TypedDict docs <https://docs.python.org/3/library/typing.html#typing.TypedDict>`_ for
information on how to specific optional keys on ``TypedDict``\s.

Extra Keys
----------

:class:`TypedDictValidator`, :class:`DataclassValidator`, and :class:`NamedTupleValidator`
can all be configured to fail if extra keys are found -- simply pass
``fail_on_unknown_keys=True`` at initialization.

.. testcode:: extrakeys

    from dataclasses import dataclass
    from koda_validate import DataclassValidator, Valid, Invalid

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
-------------
It's common to need custom logic for derived :class:`Validator`\s. There are several ways
to achieve that.

Annotated
^^^^^^^^^
In Python 3.9+, you can use `Annotated <https://docs.python.org/3/library/typing.html#typing.Annotated>`_
to add a custom :class:`Validator` for a given key.

.. testcode:: annotated

    from dataclasses import dataclass
    from typing import Annotated, Optional
    from koda_validate import (IntValidator, DataclassValidator, PredicateErrs,
                               Min, Max, Valid, Invalid, KeyErrs)

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
^^^^^^^^^
If you're using Python3.8, or don't want to add ``Annotated`` to your class annotations,
you can use ``overrides={<key>: <validator>}``. The following will produce the same
:class:`Validator` as in the :ref:`Annotated example<how_to/dictionaries/derived:Annotated>` above.

.. testcode:: overrides

    from dataclasses import dataclass
    from typing import Annotated, Optional
    from koda_validate import DataclassValidator, IntValidator, Min, Max

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
^^^^^^^^^^^^^^^^^

The ``typehint_resolver`` parameter controls how :ref:`how_to/dictionaries/derived:Derived Validators`
resolve typehints into :class:`Validator`\s. This example will produce the same :class:`Validator` as in
the :ref:`Annotated example<how_to/dictionaries/derived:Annotated>`.

.. testcode:: typehintresolver

    from dataclasses import dataclass
    from typing import Any, Optional
    from koda_validate import Validator, IntValidator, Min, Max, DataclassValidator
    from koda_validate.typehints import get_typehint_validator

    @dataclass
    class Image:
        height: int
        width: int
        description: Optional[str] = None

    def custom_resolver(annotations: Any) -> Validator[Any]:
        # we're only customizing how `int`s are handled
        if annotations is int:
            return IntValidator(Min(10), Max(1000))
        else:
            return get_typehint_validator(annotations)

    validator = DataclassValidator(Image, typehint_resolver=custom_resolver)

It often makes sense to wrap :data:`get_typehint_validator`, as in the example
above, but it's OK to completely rewrite how this works if it suits you.


``validate_object`` and ``validate_object_async``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can pass either ``validate_object`` or ``validate_object_async`` to :ref:`how_to/dictionaries/derived:Derived Validators`,
which will run after the individual attributes have been validated:

.. testcode::

    from dataclasses import dataclass
    from typing import Optional
    from koda_validate import (DataclassValidator, Invalid, Valid,
                               ValidationErrBase, ErrType)

    @dataclass
    class QA:
        question_id: int
        answer: str

    @dataclass
    class WrongAnswerErr(ValidationErrBase):
        pass

    def answer_is_valid(obj: QA) -> Optional[ErrType]:
        # really sophisticated logic here!
        if obj.question_id == 100 and obj.answer == "the right answer":
            # success
            return None
        else:
            return WrongAnswerErr()

    validator = DataclassValidator(QA, validate_object=answer_is_valid)

    assert validator(
        {"question_id": 100, "answer": "wrong answer :("}
    ) == Invalid(WrongAnswerErr(), QA(100, 'wrong answer :('), validator)

    assert validator(
        {"question_id": 100, "answer": "the right answer"}
    ) == Valid(QA(100, 'the right answer'))



Caveats
-------

Some notable limitations exist with derived dictionary :class:`Validator`\s:

- the keys of the dictionaries must be strings
- the keys must abide by the relevant attribute name restrictions for the classes
- generic and custom types will often require a custom :class:`Validator`
