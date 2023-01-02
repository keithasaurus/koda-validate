import asyncio
import json
from typing import Annotated, Optional, TypedDict

from django.http import HttpRequest, HttpResponse, JsonResponse

from koda_validate import *
from koda_validate.serialization.json_schema import to_json_schema


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

# if you want to produce a JSON Schema, you can use `to_json_schema()`
# schema = to_json_schema(contact_validator)
# hook_into_some_api_definition(schema)


async def contact_async(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse("HTTP method not allowed", status=405)

    try:
        posted_json = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"__container__": "expected json"}, status=400)
    else:
        result = await TypedDictValidator(ContactForm).validate_async(posted_json)
        match result:
            case Valid(contact_form):
                print(contact_form)
                return JsonResponse({"success": True})
            case Invalid() as inv:
                return JsonResponse(to_serializable_errs(inv), status=400, safe=False)
