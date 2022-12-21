Processors
==========
``Processor``\s allow us to take a value of a given type and transform it into another value of that type. ``Processor``\s are most useful
*after* type validation, but *before* predicates are checked. They tend to be more common on strings than any other type. Perhaps the
most obvious usages would be trimming whitespace or adjust the case of a string:

.. code-block:: python

    from koda_validate import *

    max_length_3_validator = StringValidator(
      MaxLength(3),
      preprocessors=[strip, upper_case]
    )

    assert max_length_3_validator(" hmm ") == Valid("HMM")

We see that the ``preprocessors`` stripped the whitespace from ``" hmm "`` and then transformed it to upper-case before
it was checked against the ``MaxLength(3)`` ``Predicate``.

Processors are very simple to write -- see [Extension](#extension) for more details.
