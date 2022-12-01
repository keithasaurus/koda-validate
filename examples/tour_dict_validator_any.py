from typing import Any, Dict, Hashable

from koda_validate import *
from koda_validate.base import InvalidSimple, ValidationResult


def no_dwight_regional_manager(
    employee: Dict[Hashable, Any]
) -> ValidationResult[Dict[Hashable, Any]]:
    if (
        "schrute" in employee["name"].lower()
        and employee["title"].lower() == "assistant regional manager"
    ):
        return Invalid(InvalidSimple("Assistant TO THE Regional Manager!"))
    else:
        return Valid(employee)


employee_validator = DictValidatorAny(
    {
        "title": StringValidator(not_blank, MaxLength(100), preprocessors=[strip]),
        "name": StringValidator(not_blank, preprocessors=[strip]),
    },
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)

assert employee_validator(
    {"name": "Jim Halpert", "title": "Sales Representative"}
) == Valid({"name": "Jim Halpert", "title": "Sales Representative"})

assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Invalid(InvalidSimple("Assistant TO THE Regional Manager!"))
