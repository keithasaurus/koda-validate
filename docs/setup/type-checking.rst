Type Checking
=============
Koda Validate is built with typehint compatibility at its core. It is meant to aid
developers by leveraging type hints to increase readability and reliability.

It is recommended to use the most up-to-date version of `mypy <https://pypi.org/project/mypy/>`_
to take full advantage of type hints. Koda Validate can work with other type checkers, but it is
tested against the most recent stable version of mypy.

.. note::

    Whether or not you are using a specific type checker with Koda Validate, the functionality will remain the same, as type hints have no runtime effects in Python.

pip
---

.. code-block::

    pip install mypy

Poetry
------

.. code-block::

    poetry add mypy

Dependency Group
^^^^^^^^^^^^^^^^
Because mypy doesn't do anything at runtime, it's common to only install it for specific
non-production groups, such as "test" or "dev":

.. code-block::

    poetry add mypy --group test

