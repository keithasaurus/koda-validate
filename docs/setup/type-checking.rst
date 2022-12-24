Type Checking
=============
Koda Validate is meant to aid developers by working well with type hints. It is tested against `mypy
<http://mypy-lang.org/>`_ 0.990+.

While Koda Validate does work with other type checkers, the safest path for continual compatibility
would be to use an up-to-date version of mypy. (Whether or not you are using a specific type
checker with Koda Validate, the functionality will remain the same, as type hints have no runtime effects in Python.)
If you happen to run into a problem with type checking, there a few common workarounds:

**type: ignore**

.. code-block:: python

    x = some_function()  # type: ignore

This simply tells the type checker to ignore this line.


**Any**

.. code-block:: python

    from typing import Any

    x: Any = some_function()

The Python docs about ``Any`` say:

- Every type is compatible with ``Any``.
- ``Any`` is compatible with every type.

**cast**

.. code-block:: python

    from typing import cast

    x = cast(str, some_function())  # `str` could be any type you wish to cast to

``cast`` just tells the type checker the value is of the specified type.


The Python typehint ecosystem is still evolving rapidly, and you can expect guidance here to be updated over time.