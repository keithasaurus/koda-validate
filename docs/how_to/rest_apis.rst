REST APIs
=========

Koda Validate is not tightly coupled with specific web frameworks, serialization formats,
or types of APIs. Nonetheless, Koda Validate does not exist in a vacuum, and some thought
has put into how to integrate into common API setups.

Here we'll explore the example of a Contact Form that is posted to a REST endpoint, and
see how it could be implemented in several web frameworks.

.. toctree::
    :maxdepth: 3

    rest_apis/flask
    rest_apis/django
