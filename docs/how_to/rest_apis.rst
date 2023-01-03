REST APIs
=========

Koda Validate is not tightly coupled with specific web frameworks, serialization formats,
or types of APIs. Nonetheless, Koda Validate does not exist in a vacuum, and some thought
has put into how to integrate into common API setups.

Here we'll explore the example of a Contact Form that is posted to a REST endpoint, and
see how it could be implemented in several web frameworks.


Flask
-----
Basic
^^^^^^

.. code-block:: python

    from dataclasses import dataclass
    from typing import Annotated, Optional, Tuple

    from flask import Flask, jsonify, request
    from flask.typing import ResponseValue

    from koda_validate import *

    app = Flask(__name__)


    @dataclass
    class ContactForm:
        name: str
        message: str
        # `Annotated` `Validator`s are used if found
        email: Annotated[str, StringValidator(EmailPredicate())]
        subject: Optional[str] = None


    @app.route("/contact", methods=["POST"])
    def contact_api() -> Tuple[ResponseValue, int]:
        result = DataclassValidator(ContactForm)(request.json)
        match result:
            case Valid(contact_form):
                print(contact_form)  # do something with the valid data
                return {"success": True}, 200
            case Invalid() as inv:
                return jsonify(to_serializable_errs(inv)), 400


    if __name__ == "__main__":
        app.run()


.. note::

    In the example above, ``ContactForm`` is a ``dataclass``, so we use a ``DataclassValidator``. We could have used a
    ``TypedDict`` and ``TypedDictValidator`` or a ``NamedTuple`` and ``NamedTupleValidator``, and the code would have been
    essentially the same.

Fuller Example (with Async)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    from typing import Annotated, Optional, Tuple, TypedDict

    from flask import Flask, jsonify, request
    from flask.typing import ResponseValue

    from koda_validate import *

    app = Flask(__name__)


    class Captcha(TypedDict):
        seed: Annotated[str, StringValidator(ExactLength(16))]
        response: Annotated[str, StringValidator(MaxLength(16))]


    async def validate_captcha(captcha: Captcha) -> Optional[ErrType]:
        """
        after we validate that the seed and response on their own,
        we need to check our database to make sure the response is correct
        """

        async def pretend_check_captcha_service(seed: str, response: str) -> bool:
            await asyncio.sleep(0.01)  # pretend to call
            return seed == response[::-1]

        if await pretend_check_captcha_service(captcha["seed"], captcha["response"]):
            # everything's valid
            return None
        else:
            return SerializableErr({"response": "bad captcha response"})


    class ContactForm(TypedDict):
        email: Annotated[str, StringValidator(EmailPredicate())]
        message: Annotated[str, StringValidator(MaxLength(500), MinLength(10))]
        captcha: Annotated[
            Captcha,
            # explicitly adding some extra validation
            TypedDictValidator(Captcha, validate_object_async=validate_captcha),
        ]


    contact_validator = TypedDictValidator(ContactForm)


    @app.route("/contact", methods=["POST"])
    async def contact_api() -> Tuple[ResponseValue, int]:
        result = await contact_validator.validate_async(request.json)
        match result:
            case Valid(contact_form):
                print(contact_form)
                return {"success": True}, 200
            case Invalid() as inv:
                return jsonify(to_serializable_errs(inv)), 400


    # if you want a JSON Schema from a ``Validator``, there's `to_json_schema()`
    # schema = to_json_schema(contact_validator)
    # hook_into_some_api_definition(schema)


    if __name__ == "__main__":
        app.run()



Django
------
Simple
^^^^^^

.. code-block:: python

    import json
    from dataclasses import dataclass
    from typing import Annotated, Optional

    from django.http import HttpRequest, JsonResponse, HttpResponse

    from koda_validate import *


    @dataclass
    class ContactForm:
        name: str
        message: str
        # Annotated `Validator`s are used if defined -- instead
        # of Koda Validate's default for the type)
        email: Annotated[str, StringValidator(EmailPredicate())]
        subject: Optional[str] = None


    def contact(request: HttpRequest) -> HttpResponse:
        if request.method != "POST":
            return HttpResponse("HTTP method not allowed", status=405)

        try:
            posted_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"_root_": "expected json"}, status=400)
        else:
            result = DataclassValidator(ContactForm)(posted_json)
            match result:
                case Valid(contact_form):
                    print(contact_form)
                    return JsonResponse({"success": True})
                case Invalid() as inv:
                    return JsonResponse(to_serializable_errs(inv), status=400, safe=False)


Fuller Example (with Async)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    import json
    from typing import Annotated, Optional, TypedDict

    from django.http import HttpRequest, HttpResponse, JsonResponse

    from koda_validate import *


    class Captcha(TypedDict):
        seed: Annotated[str, StringValidator(ExactLength(16))]
        response: Annotated[str, StringValidator(MaxLength(16))]


    async def validate_captcha(captcha: Captcha) -> Optional[ErrType]:
        """
        after we validate that the seed and response both conform to the types/shapes we want,
        we need to check our database to make sure the response is correct
        """
        await asyncio.sleep(0.01)  # pretend to ask db
        if captcha["seed"] != captcha["response"][::-1]:
            return SerializableErr({"response": "bad captcha response"})
        else:
            return None


    class ContactForm(TypedDict):
        email: Annotated[str, StringValidator(EmailPredicate())]
        message: Annotated[str, StringValidator(MaxLength(500), MinLength(10))]
        # we only need to explicitly define the TypedDictValidator here because we want
        # to include additional validation in validate_captcha
        captcha: Annotated[
            Captcha, TypedDictValidator(Captcha, validate_object_async=validate_captcha)
        ]


    contact_validator = TypedDictValidator(ContactForm)


    async def contact_async(request: HttpRequest) -> HttpResponse:
        if request.method != "POST":
            return HttpResponse("HTTP method not allowed", status=405)

        try:
            posted_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"__container__": "expected json"}, status=400)
        else:
            result = await TypedDictValidator(ContactForm).validate_async(posted_json)
            match result:
                case Valid(contact_form):
                    print(contact_form)
                    return JsonResponse({"success": True})
                case Invalid() as inv:
                    return JsonResponse(to_serializable_errs(inv), status=400, safe=False)


    # if you want a JSON Schema from a ``Validator``, there's `to_json_schema()`
    # schema = to_json_schema(contact_validator)
    # hook_into_some_api_definition(schema)
