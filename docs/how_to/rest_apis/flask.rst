Flask
=====

Basic
^^^^^

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

    In the example above, ``ContactForm`` is a ``dataclass``, so we use a
    :class:`DataclassValidator<koda_validate.DataclassValidator>`. We could have used a
    ``TypedDict`` and :class:`TypedDictValidator<koda_validate.TypedDictValidator>`, or a
    ``NamedTuple`` and :class:`NamedTupleValidator<koda_validate.NamedTupleValidator>`,
    and the code would have been essentially the same.

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


    # if you want a JSON Schema from a :class:`Validator<koda_validate.Validator>`, there's `to_json_schema()`
    # schema = to_json_schema(contact_validator)
    # hook_into_some_api_definition(schema)


    if __name__ == "__main__":
        app.run()
