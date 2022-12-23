import json
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Annotated, Optional

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from koda_validate import *


@dataclass
class ContactForm:
    name: str
    message: str
    # Annotated `Validator`s are used if defined -- instead
    # of Koda Validate's default for the type)
    email: Annotated[str, StringValidator(EmailPredicate())]
    subject: Optional[str] = None


@csrf_exempt
@require_POST
def contact(request: HttpRequest) -> HttpResponse:
    try:
        posted_json = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({"_root_": "expected json"}, status=400)
    else:
        result = DataclassValidator(ContactForm)(posted_json)
        match result:
            case Valid(contact_form):
                print(contact_form)
                return JsonResponse({"success": True})
            case Invalid() as inv:
                return JsonResponse(to_serializable_errs(inv), status=400, safe=False)
