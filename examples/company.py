from dataclasses import dataclass

from koda import Err, Just, Maybe, Ok, Result, nothing

from koda_validate.dictionary import dict_validator, key, maybe_key
from koda_validate.generic import Max
from koda_validate.integer import IntValidator
from koda_validate.list import ListValidator, MinItems
from koda_validate.none import Noneable
from koda_validate.string import MaxLength, StringValidator, not_blank, strip
from koda_validate.typedefs import JSONValue


@dataclass
class Employee:
    title: str
    name: str


def no_dwight_regional_manager(employee: Employee) -> Result[Employee, JSONValue]:
    if (
        "schrute" in employee.name.lower()
        and employee.title.lower() == "assistant regional manager"
    ):
        return Err("Assistant TO THE Regional Manager!")
    else:
        return Ok(employee)


employee_validator = dict_validator(
    Employee,
    key("title", StringValidator(not_blank, MaxLength(100), preprocessors=[strip])),
    key("name", StringValidator(not_blank, preprocessors=[strip])),
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)


# the fields are valid but the object as a whole is not.
assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Err("Assistant TO THE Regional Manager!")


@dataclass
class Company:
    name: str
    employees: list[Employee]
    year_founded: Maybe[int]
    stock_ticker: Maybe[str]


company_validator = dict_validator(
    Company,
    key("company_name", StringValidator(not_blank, preprocessors=[strip])),
    key(
        "employees",
        ListValidator(
            employee_validator,
            MinItems(1),  # a company has to have at least one person, right??
        ),
    ),
    # maybe_key means the key can be missing
    maybe_key("year_founded", IntValidator(Max(2022))),
    key(
        "stock_ticker",
        Noneable(StringValidator(not_blank, MaxLength(4), preprocessors=[strip])),
    ),
)

dunder_mifflin_data = {
    "company_name": "Dunder Mifflin",
    "employees": [
        {"title": "Regional Manager", "name": "Michael Scott"},
        {"title": " Assistant to the Regional Manager ", "name": "Dwigt Schrute"},
    ],
    "stock_ticker": "DMI",
}

assert company_validator(dunder_mifflin_data) == Ok(
    Company(
        name="Dunder Mifflin",
        employees=[
            Employee(title="Regional Manager", name="Michael Scott"),
            Employee(title="Assistant to the Regional Manager", name="Dwigt Schrute"),
        ],
        year_founded=nothing,
        stock_ticker=Just(val="DMI"),
    )
)

# we could keep nesting, arbitrarily
company_list_validator = ListValidator(company_validator)
