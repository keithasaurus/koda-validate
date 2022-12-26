APIs
====

Koda Validate is principally aimed exclusively at validation. That is to say, Koda
Validate is not tightly coupled with specific web frameworks, serialization formats, etc.
However, Koda Validate does not exist in a vacuum and some thought has put into how to
integrate Koda Validate into common API setups.

Basic Usage
-----------
The general means in which Koda Validate is expected to be used -- regardless of
framework -- is as follows
.. code-block:: python

    def some_resolver(request):