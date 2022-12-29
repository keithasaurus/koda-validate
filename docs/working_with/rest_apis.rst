REST APIs
=========

Koda Validate is not tightly coupled with specific API types, serialization formats, or web frameworks.
Nonetheless, Koda Validate does not exist in a vacuum, and some thought has put into how to
integrate Koda Validate into common API setups.

Here we'll look at the example of a Contact Form that is submitted through a REST endpoint, and
look at ways to implement this in several web frameworks.


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


Fuller Example with Async
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    from typing import Annotated, Optional, Tuple, TypedDict

    from flask import Flask, jsonify, request
    from flask.typing import ResponseValue

    from koda_validate import *
    from koda_validate.serialization.json_schema import to_json_schema

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
            TypedDictValidator(Captcha, validate_object_async=validate_captcha)
        ]


    contact_validator = TypedDictValidator(ContactForm)

    # if you want to produce a JSON Schema, you can use `to_json_schema()`
    # schema = to_json_schema(contact_validator)
    # hook_into_some_api_definition(schema)


    @app.route("/contact", methods=["POST"])
    async def contact_api() -> Tuple[ResponseValue, int]:
        result = await contact_validator.validate_async(request.json)
        match result:
            case Valid(contact_form):
                print(contact_form)
                return {"success": True}, 200
            case Invalid() as inv:
                return jsonify(to_serializable_errs(inv)), 400


    if __name__ == "__main__":
        app.run()


Django
------
Simple
^^^^^^

