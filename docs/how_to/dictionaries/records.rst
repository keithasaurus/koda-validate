RecordValidator
===============

.. module:: koda_validate
    :noindex:

We use the term "record" to mean a dictionary where keys may have differing value types.
This is common, for instance, with deserialized JSON ``object``\s. In Python
code, you may see type annotations like ``Dict[str, Any]`` to represent such types.
``TypedDict``\s, ``dataclass``\es, and  ``NamedTuple``\s may also be used to express such
a type. In Koda Validate there are many built-in :class:`Validator`\s to suit these
purposes.

In many cases :class:`RecordValidator` is more verbose than the :ref:`Derived Validators<how_to/dictionaries/derived:Derived Validators>`, but
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

When validation becomes complex, :class:`RecordValidator` is sometimes the most direct, and concise, option.

Caveats
^^^^^^^
The main caveats with :class:`RecordValidator` are:

- it works on a maximum of 16 keys
- type checkers don't always produce the most readable hints and errors for :class:`RecordValidator`, as it uses ``@overload``\s.
- the target of validation must be defined outside the :class:`RecordValidator`, and the order of arguments matters
