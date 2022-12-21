Overview
========
At it's core, Koda Validate is little more than a few function signatures (see Validators,
Predicates, and Processors), which can be combined to build validators of arbitrary
complexity -- via composition and extension. Additionally it provides straightforward
paths for optimization -- Koda Validate tends to be fast (for Python).

Validators in Koda Validate naturally form into graph structures -- usually
Directed, Acyclical Graphs (a notable exception would be the use of ``Lazy``). It is an
aim of this library to facilitate the re-purposing of such validation structures for other
purposes, such as documentation, customized error types, and so on. See Metadata for more
details.