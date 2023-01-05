Pydantic Comparison
===================

.. module:: koda_validate
    :noindex:

Comparing Koda Validate and Pydantic is not exactly apples-to-apples, since Koda Validate is more narrowly
aimed at *just* validation. Nonetheless, this is one of the most common questions, and there are a number of noteworthy differences:

- Koda Validate is built around a simple, composable definition of validation.
- Koda Validate treats validation as part of normal control flow. It does not raise exceptions for invalid data.
- Koda Validate treats validation explicitly. It does not coerce types or mutate values in surprising ways.
- Koda Validate is ~1.5 - 12x faster. You can run the suite on your system with ``python -m bench.run``
- Koda Validate is fully asyncio-compatible.
- Koda Validate is pure Python.
- Koda Validate requires no plugins for mypy compatibility.