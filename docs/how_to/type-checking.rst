Typehint Troubleshooting
========================

If you happen to run into a problem with type checking Koda Validate, take a minute read through the documentation to
make sure there really is a problem -- some ``Validator``\s require specific ``.typed`` methods to be called for proper
type inference at initialization.

If you run into a *bug*, there a few common workarounds to be aware of:

type: ignore
^^^^^^^^^^^^
.. code-block:: python

    x = some_function()  # type: ignore

This simply tells the type checker to ignore this line.


typing.Any
^^^^^^^^^^

.. code-block:: python

    from typing import Any

    x: Any = some_function()

The Python docs about ``Any`` say:

- Every type is compatible with ``Any``.
- ``Any`` is compatible with every type.

typing.cast
^^^^^^^^^^^

.. code-block:: python

    from typing import cast

    x = cast(str, some_function())  # `str` could be any type you wish to cast to

``cast`` just tells the type checker the value is of the specified type.


The Python typehint ecosystem is still evolving rapidly, and you can expect guidance here to be updated over time.