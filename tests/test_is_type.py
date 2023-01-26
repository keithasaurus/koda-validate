from dataclasses import dataclass

import pytest

from koda_validate import Invalid, Predicate, PredicateErrs, Processor, TypeErr, Valid
from koda_validate.is_type import TypeValidator


def test_type_simple() -> None:
    class Person:
        def __init__(self, name: str) -> None:
            self.name = name

    validator = TypeValidator(Person)

    assert validator(p := Person("bob")) == Valid(p)

    assert validator("bob") == Invalid(TypeErr(Person), "bob", validator)


def test_type_complex() -> None:
    @dataclass
    class Dog:
        name: str
        breed: str

    @dataclass
    class IsBeagle(Predicate[Dog]):
        def __call__(self, val: Dog) -> bool:
            return val.breed == "beagle"

    class LowerDogBreed(Processor[Dog]):
        def __call__(self, val: Dog) -> Dog:
            return Dog(
                val.name,
                val.breed.lower(),
            )

    validator = TypeValidator(
        Dog, predicates=[IsBeagle()], preprocessors=[LowerDogBreed()]
    )

    assert validator(Dog("sparky", "Beagle")) == Valid(Dog("sparky", "beagle"))

    assert validator(Dog("spot", "terrier")) == Invalid(
        PredicateErrs([IsBeagle()]), Dog("spot", "terrier"), validator
    )


@pytest.mark.asyncio
async def test_type_simple_async() -> None:
    class Person:
        def __init__(self, name: str) -> None:
            self.name = name

    validator = TypeValidator(Person)

    assert await validator.validate_async(p := Person("bob")) == Valid(p)

    assert await validator.validate_async("bob") == Invalid(
        TypeErr(Person), "bob", validator
    )
