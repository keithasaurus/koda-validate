from dataclasses import dataclass
from typing import Annotated, Optional, Tuple, cast

from flask import Flask, request
from flask.typing import ResponseValue

from koda_validate import *

app = Flask(__name__)


@dataclass
class ContactForm:
    name: str
    message: str
    # Annotated `Validator`s are used if defined -- instead
    # of Koda Validate's default for the type)
    email: Annotated[str, StringValidator(EmailPredicate())]
    subject: Optional[str] = None


def errs_to_response_value(val: Invalid) -> ResponseValue:
    """
    Serializable and Response should be compatible, but mypy doesn't understand that --
    just making that explicit here.
    """
    return cast(ResponseValue, to_serializable_errs(val))


@app.route("/contact", methods=["POST"])
def contact_api() -> Tuple[ResponseValue, int]:
    result = DataclassValidator(ContactForm)(request.json)
    match result:
        case Valid(contact_form):
            print(contact_form)
            return {"success": True}, 200
        case Invalid() as inv:
            return errs_to_response_value(inv), 400


if __name__ == "__main__":
    app.run()
