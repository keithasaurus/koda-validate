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
