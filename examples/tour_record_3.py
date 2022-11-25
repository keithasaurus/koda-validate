from dataclasses import dataclass

from koda_validate import *
from koda_validate.base import InvalidCustom, ValidationResult


@dataclass
class Employee:
    title: str
    name: str


def no_dwight_regional_manager(employee: Employee) -> ValidationResult[Employee]:
    if (
        "schrute" in employee.name.lower()
        and employee.title.lower() == "assistant regional manager"
    ):
        return Invalid(InvalidCustom("Assistant TO THE Regional Manager!"))
    else:
        return Valid(employee)


employee_validator = RecordValidator(
    into=Employee,
    keys=(
        ("title", StringValidator(not_blank, MaxLength(100), preprocessors=[strip])),
        ("name", StringValidator(not_blank, preprocessors=[strip])),
    ),
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)


# The fields are valid but the object as a whole is not.
assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Invalid(InvalidCustom("Assistant TO THE Regional Manager!"))
