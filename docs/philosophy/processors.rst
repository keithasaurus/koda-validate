Processors
==========
.. module:: koda_validate
    :noindex:

:class:`Processor<koda_validate.Processor>`\s allow us to take a value of a given type and transform it into another value of that type. :class:`Processor<koda_validate.Processor>`\s are most useful
*after* type validation, but *before* predicates are checked. They tend to be more common on strings than any other type. Perhaps the
most obvious use cases would be trimming whitespace or adjusting the case of a string:

.. testcode:: python

    from koda_validate import StringValidator, MaxLength, strip, upper_case, Valid

    max_length_3_validator = StringValidator(
      MaxLength(3),
      preprocessors=[strip, upper_case]
    )

    assert max_length_3_validator(" hmm ") == Valid("HMM")

We see that the ``preprocessors`` stripped the whitespace from ``" hmm "`` and then transformed it to upper-case *before*
the resulting value was checked against the ``MaxLength(3)`` :class:`Predicate<koda_validate.Predicate>`.

:class:`Processor`\s are very simple to write -- see :ref:`how_to/extension:Extension` for more details.
