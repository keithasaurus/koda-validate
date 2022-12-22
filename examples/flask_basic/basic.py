from typing import Annotated, Tuple, TypedDict, cast

from flask import Flask, request
from flask.typing import ResponseValue

from koda_validate import *

app = Flask(__name__)


class ContactForm(TypedDict):
    email: Annotated[str, StringValidator(EmailPredicate())]
    message: Annotated[str, StringValidator(MaxLength(500), MinLength(10))]


def errs_to_response_value(val: Invalid) -> ResponseValue:
    """
    Serializable and Response should be compatible, but mypy doesn't understand that
    just making that explicit here.
    """
    return cast(ResponseValue, to_serializable_errs(val))


@app.route("/contact", methods=["POST"])
def users_api() -> Tuple[ResponseValue, int]:
    result = TypedDictValidator(ContactForm)(request.json)
    match result:
        case Valid(contact_form):
            # send the contact form somewhere
            print(contact_form)
            return {"success": True}, 200
        case Invalid() as inv:
            return errs_to_response_value(inv), 400
