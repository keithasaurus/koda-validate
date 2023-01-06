import json
from dataclasses import dataclass
from typing import Annotated, Optional

from django.http import HttpRequest, HttpResponse, JsonResponse

from koda_validate import *
from koda_validate.serialization import to_serializable_errs


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
