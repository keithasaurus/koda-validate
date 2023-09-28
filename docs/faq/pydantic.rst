Pydantic Comparison
===================

.. module:: koda_validate
    :noindex:

Comparing Koda Validate and Pydantic is not exactly apples-to-apples, since Koda Validate is more narrowly
aimed at *just* validation. Nonetheless, this is one of the most common questions, and there are a number of noteworthy differences:

- Koda Validate is built around a simple, composable definition of validation.
- Koda Validate is fully asyncio-compatible.
- Koda Validate allows the user to control coercion.
- Koda Validate requires no plugins for mypy compatibility.
- Koda Validate is competitive with rust-compiled Pydantic 2.x in speed of synchronous validation (despite being pure Python). You can run the benchmark suite on your system with ``python -m bench.run``
