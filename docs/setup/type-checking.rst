Type Checking
=============
Koda Validate is meant to aid developers by leveraging type hints. It's recommended that you
use the most up-to-date version of `mypy <https://pypi.org/project/mypy/>`_ to take full advantage of type hints. Koda
Validate can work with other type checkers, and other versions of mypy, but it
is tested against mypy 0.990+.

.. note::

    Whether or not you are using a specific type checker with Koda Validate, the functionality will remain the same, as type hints have no runtime effects in Python.

pip
---

.. code-block:: bash

    pip install mypy

Poetry
------

Because mypy doesn't do anything at runtime, it's common to only install it for specific non-production groups.

.. code-block:: bash

    poetry add mypy --group test

