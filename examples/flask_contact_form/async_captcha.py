import asyncio
from typing import Annotated, Optional, Tuple, TypedDict, cast

from flask import Flask, request
from flask.typing import ResponseValue

from koda_validate import *

app = Flask(__name__)


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


def errs_to_response_value(val: Invalid) -> ResponseValue:
    """
    Serializable and Response should be compatible, but mypy doesn't understand that --
    just making that explicit here.
    """
    return cast(ResponseValue, to_serializable_errs(val))


@app.route("/contact", methods=["POST"])
async def contact_api() -> Tuple[ResponseValue, int]:
    result = await contact_validator.validate_async(request.json)
    match result:
        case Valid(contact_form):
            print(contact_form)
            return {"success": True}, 200
        case Invalid() as inv:
            return errs_to_response_value(inv), 400


if __name__ == "__main__":
    app.run()
