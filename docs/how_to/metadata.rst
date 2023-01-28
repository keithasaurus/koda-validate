Metadata
========

.. module:: koda_validate
    :noindex:

:class:`Validator`\s in Koda Validate naturally forms into graph structures, usually
trees (a notable exception would be the use of :class:`Lazy`, which can create cycles). It is an
aim of this library to facilitate the re-purposing of such validation structures for other
purposes, such as schemas, HTML, documentation, customized error types, and so on.

Because it's easy to branch on the type of a :class:`Validator`, it's straightforward to
write functions that transform arbitrary :class:`Validator`\s into other structures.
Some examples of this exist within Koda Validate:

- :data:`to_json_schema<koda_validate.serialization.to_json_schema>` converts :class:`Validator`\s into JSON Schema objects
- :data:`to_serializable_errs<koda_validate.serialization.to_serializable_errs>` converts :class:`Invalid` objects in human-readable serializable structures (discussed in :ref:`Errors <flaterrs-example>`)
- :data:`koda_validate.signature._get_arg_fail_message` converts ``Invalid`` objects to human-readable traceback messages.

Pattern Matching
----------------

The recommended approach to branching on validation graphs is to use pattern matching
against the type of :class:`Validator`. For example, if you wanted to generate a markdown description
from a :class:`Validator`, you could start with something like this:

.. testcode:: markdown

    from typing import Union, Any
    from koda_validate import (Validator, Predicate, PredicateAsync,
                               ListValidator, StringValidator)

    def to_markdown_description(obj: Union[Validator[Any],
                                           Predicate[Any],
                                           PredicateAsync[Any]]) -> str:
        match obj:
            case StringValidator():
                return "string validator"
            case ListValidator(item_validator):
                return f"list validator\n- {to_markdown_description(item_validator)}"
            case _:
                ...

    print(to_markdown_description(ListValidator(StringValidator())))

Outputs:

.. testoutput:: markdown

    list validator
    - string validator

Here we generated a very simple output with code that supports a tiny subset of
:class:`Validator`\s, but it's easy to expand the same approach to produce arbitrary
outputs for a wide range of validators.