from typing import Any

from koda_validate import MaxLength, MinLength, Predicate, StringValidator, Validator


def describe_validator(validator: Validator[Any, Any, Any] | Predicate[Any, Any]) -> str:
    match validator:
        case StringValidator(predicates):
            predicate_descriptions = [
                f"- {describe_validator(pred)}" for pred in predicates
            ]
            return "\n".join(["validates a string"] + predicate_descriptions)
        case MinLength(length):
            return f"minimum length {length}"
        case MaxLength(length):
            return f"maximum length {length}"
        # ...etc
        case _:
            raise TypeError(f"unhandled validator type. got {type(validator)}")


print(describe_validator(StringValidator()))
# > validates a string
print(describe_validator(StringValidator(MinLength(5))))
# > validates a string
# > - minimum length 5
print(describe_validator(StringValidator(MinLength(3), MaxLength(8))))
# > validates a string
# > - minimum length 3
# > - maximum length 8
