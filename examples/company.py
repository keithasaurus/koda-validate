from dataclasses import dataclass

from koda import Err, Just, Maybe, Ok, Result, nothing

from koda_validate.processors import strip
from koda_validate.typedefs import JSONValue
from koda_validate.validators.dicts import dict_validator
from koda_validate.validators.validators import (
    IntValidator,
    ListValidator,
    Max,
    MaxLength,
    Min,
    MinItems,
    MinLength,
    Noneable,
    StringValidator,
    key,
    maybe_key,
    not_blank,
)


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,
    key("name", StringValidator(MinLength(1))),
    key("age", IntValidator(Min(0))),
)


@dataclass
class Employee:
    title: str
    person: Person


def no_dwight_regional_manager(employee: Employee) -> Result[Employee, JSONValue]:
    if (
        "schrute" in employee.person.name.lower()
        and employee.title.lower() == "assistant regional manager"
    ):
        return Err("Assistant TO THE Regional Manager!")
    else:
        return Ok(employee)


employee_validator = dict_validator(
    Employee,
    key("title", StringValidator(not_blank, MaxLength(100), preprocessors=[strip])),
    # we can nest validators
    key("person", person_validator),
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)


# the fields are valid but the object as a whole is not.
assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "person": {"name": "Dwight Schrute", "age": 39},
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
        {"title": "Regional Manager", "person": {"name": "Michael Scott", "age": 45}},
        {
            "title": " Assistant to the Regional Manager ",
            "person": {"name": "Dwigt Schrute", "age": 39},
        },
    ],
    "stock_ticker": "DMI",
}

assert company_validator(dunder_mifflin_data) == Ok(
    Company(
        name="Dunder Mifflin",
        employees=[
            Employee(
                title="Regional Manager", person=Person(name="Michael Scott", age=45)
            ),
            Employee(
                title="Assistant to the Regional Manager",
                person=Person(name="Dwigt Schrute", age=39),
            ),
        ],
        year_founded=nothing,
        stock_ticker=Just(val="DMI"),
    )
)

# we could keep nesting, arbitrarily
company_list_validator = ListValidator(company_validator)
