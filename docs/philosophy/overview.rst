Overview
========
At it's core, Koda Validate is little more than a few function signatures (see Validators,
Predicates, and Processors), which can be combined to build validators of arbitrary
complexity. This simplicity also provides straightforward
paths for optimization -- Koda Validate tends to be fast (for Python).

Validation in Koda Validate naturally forms into graph structures -- usually
a tree (a notable exception would be the use of ``Lazy``). It is an
aim of this library to facilitate the re-purposing of such validation structures for other
purposes, such as documentation, customized error types, and so on (see Metadata for more
details).

