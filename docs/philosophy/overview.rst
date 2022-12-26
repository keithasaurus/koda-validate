Overview
========
At it's core, Koda Validate is little more than a few function signatures (see Validators,
Predicates, and Processors), which can be combined to build validators of arbitrary
complexity. This simplicity also provides straightforward
paths for:

- optimization: Koda Validate tends to be fast (for Python)
- extension: Koda Validate can be extended to Validate essentially anything, even asynchronusly.

.. note::

    If you've run into edge cases that you can't work around in other validation libraries, please
    take a look at Extension. The simplest way to work around Validator quirks in Koda Validate
    is often to write your own -- it's easy.s

Context Free
------------
Validators, Predicates and Processors in Koda Validate are not coupled with any specific framework,
serialization format, or language. Instead Koda Validate aims to make it straightforward to contextualize
validation outputs and artifacts. This effectively makes Koda Validate just as easy to work with in
any framework, format or langauge.

See Metadata for more info.
