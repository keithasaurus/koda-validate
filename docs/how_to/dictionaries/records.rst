RecordValidator
===============

.. module:: koda_validate
    :noindex:


In many cases :class:`RecordValidator` is more verbose than the :ref:`Derived Validators<how_to/dictionaries/derived:Derived Validators>`, but
it comes with greater flexibility. It can handle any kind of ``Hashable`` key. Optional keys are
handled explicitly with :class:`KeyNotRequired`, which returns ``Maybe`` values. The ``into`` parameter
can be any ``Callable`` with the correct type signature -- ``dataclass``\es are convenient, but it could
just as well be an arbitrary function.



.. testcode:: recordvalidator

    from dataclasses import dataclass
    from koda import Maybe, Just
    from koda_validate import (RecordValidator, StringValidator, not_blank, MaxLength,
                               Min, Max, IntValidator, KeyNotRequired, Invalid, Valid)


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

Here's a more complex example of mixing and matching different kinds of keys.

.. testcode::

    from dataclasses import dataclass
    from koda import Maybe, Just
    from koda_validate import (
        RecordValidator, StringValidator, KeyNotRequired, IntValidator, Valid, ListValidator
    )


    @dataclass
    class Person:
        name: str
        age: Maybe[int]
        hobbies: list[str]


    person_validator = RecordValidator(
        into=Person,
        keys=(
            (1, StringValidator()),
            (False, KeyNotRequired(IntValidator())),
            (("abc", 123), ListValidator(StringValidator()))
        ),
    )

    assert person_validator({
        1: "John Doe",
        False: 30,
        ("abc", 123): ["reading", "cooking"]
    }) == Valid(Person(
        "John Doe",
        Just(30),
        ["reading", "cooking"]
    ))


Caveats
^^^^^^^
The main caveats with :class:`RecordValidator` are:

- it works on a maximum of 16 keys
- type checkers don't always produce the most readable hints and errors for :class:`RecordValidator`, as it uses ``@overload``\s.
- the target of validation must be defined outside the :class:`RecordValidator`, and the order of arguments matters
