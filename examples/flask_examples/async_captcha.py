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
