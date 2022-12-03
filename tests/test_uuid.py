import asyncio
from dataclasses import dataclass
from uuid import UUID

import pytest

from koda_validate import Invalid, Predicate, PredicateAsync, Processor, Valid
from koda_validate._generics import A
from koda_validate.base import CoercionErr, PredicateErrs
from koda_validate.uuid import UUIDValidator


class ReverseUUID(Processor[UUID]):
    def __call__(self, val: UUID) -> UUID:
        return UUID(val.hex[::-1])


def test_UUID() -> None:
    uuid_validator = UUIDValidator()
    assert uuid_validator("a string") == Invalid(
        uuid_validator, "a string", CoercionErr({str, UUID}, UUID)
    )

    assert uuid_validator(5.5) == Invalid(
        uuid_validator, 5.5, CoercionErr({str, UUID}, UUID)
    )

    assert uuid_validator(UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222")) == Valid(
        UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222")
    )

    assert uuid_validator("a22acebe-60ba-11ed-9c95-4f52af693eb2") == Valid(
        UUID("a22acebe-60ba-11ed-9c95-4f52af693eb2")
    )

    assert UUIDValidator(preprocessors=[ReverseUUID()])(
        UUID("37fb0187-0f45-45f3-a352-a8277b7b9038")
    ) == Valid(UUID("8309b7b7-728a-253a-3f54-54f07810bf73"))

    @dataclass
    class HexStartsWithD(Predicate[UUID]):
        def __call__(self, val: UUID) -> bool:
            return val.hex.startswith("d")

    validator = UUIDValidator(HexStartsWithD(), preprocessors=[ReverseUUID()])
    assert validator(UUID("8309b7b7-728a-253a-3f54-54f07810bf73")) == Invalid(
        validator,
        UUID("37fb0187-0f45-45f3-a352-a8277b7b9038"),
        PredicateErrs([HexStartsWithD()]),
    )

    assert UUIDValidator(HexStartsWithD(), preprocessors=[ReverseUUID()])(
        UUID("f309b7b7-728a-253a-3f54-54f07810bf7d")
    ) == Valid(UUID("d7fb0187-0f45-45f3-a352-a8277b7b903f"))


@pytest.mark.asyncio
async def test_UUID_async() -> None:
    uuid_validator = UUIDValidator()
    assert await uuid_validator.validate_async("abc") == Invalid(
        uuid_validator,
        "abc",
        CoercionErr(
            {str, UUID},
            UUID,
        ),
    )

    assert await uuid_validator.validate_async(5.5) == Invalid(
        uuid_validator, 5.5, CoercionErr({str, UUID}, UUID)
    )

    assert await uuid_validator.validate_async(
        UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222")
    ) == Valid(UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222"))

    @dataclass
    class HexStartsWithF(PredicateAsync[UUID]):
        async def validate_async(self, val: UUID) -> bool:
            await asyncio.sleep(0.001)
            return val.hex.startswith("f")

    v = UUIDValidator(preprocessors=[ReverseUUID()], predicates_async=[HexStartsWithF()])
    result = await v.validate_async("e348c1b4-60bd-11ed-a6e9-6ffb14046222")
    assert result == Invalid(
        v, UUID("22264041-bff6-9e6a-de11-db064b1c843e"), PredicateErrs([HexStartsWithF()])
    )


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    @dataclass
    class AsyncWait(PredicateAsync[A]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

    uu_validator = UUIDValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        uu_validator("whatever")
