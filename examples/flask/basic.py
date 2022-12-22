from typing import Annotated, TypedDict

from flask import Flask, request

from koda_validate import (
    EmailPredicate,
    Invalid,
    MaxLength,
    StringValidator,
    TypedDictValidator,
    Valid,
    to_serializable_errs,
)

app = Flask(__name__)


class ContactForm(TypedDict):
    email: Annotated[str, StringValidator(EmailPredicate())]
    message: Annotated[str, StringValidator(MaxLength(500))]


contact_form_validator = TypedDictValidator(ContactForm)


@app.route("/contact", methods=["POST"])
def users_api():
    match contact_form_validator(request.form):
        case Valid(contact_form):
            # send the contact form somewhere
            return {"success": True}
        case Invalid() as inv:
            return to_serializable_errs(inv)
