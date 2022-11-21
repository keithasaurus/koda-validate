import asyncio
from uuid import UUID

import pytest

from koda_validate import Predicate, PredicateAsync, Processor, Serializable
from koda_validate._generics import A
from koda_validate.uuid import UUIDValidator
from koda_validate.validated import Invalid, Valid


class ReverseUUID(Processor[UUID]):
    def __call__(self, val: UUID) -> UUID:
        return UUID(val.hex[::-1])


def test_UUID() -> None:
    assert UUIDValidator()("a string") == Invalid(
        ["expected a UUID, or a UUID-compatible string"]
    )

    assert UUIDValidator()(5.5) == Invalid(
        ["expected a UUID, or a UUID-compatible string"]
    )

    assert UUIDValidator()(UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222")) == Valid(
        UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222")
    )

    assert UUIDValidator()("a22acebe-60ba-11ed-9c95-4f52af693eb2") == Valid(
        UUID("a22acebe-60ba-11ed-9c95-4f52af693eb2")
    )

    assert UUIDValidator(preprocessors=[ReverseUUID()])(
        UUID("37fb0187-0f45-45f3-a352-a8277b7b9038")
    ) == Valid(UUID("8309b7b7-728a-253a-3f54-54f07810bf73"))

    class HexStartsWithD(Predicate[UUID, Serializable]):
        def __call__(self, val: UUID) -> bool:
            return val.hex.startswith("d")

        def err(self, val: UUID) -> Serializable:
            return "doesn't start with d!"

    assert UUIDValidator(HexStartsWithD(), preprocessors=[ReverseUUID()])(
        UUID("8309b7b7-728a-253a-3f54-54f07810bf73")
    ) == Invalid(["doesn't start with d!"])

    assert UUIDValidator(HexStartsWithD(), preprocessors=[ReverseUUID()])(
        UUID("f309b7b7-728a-253a-3f54-54f07810bf7d")
    ) == Valid(UUID("d7fb0187-0f45-45f3-a352-a8277b7b903f"))


@pytest.mark.asyncio
async def test_UUID_async() -> None:
    assert await UUIDValidator().validate_async("abc") == Invalid(
        ["expected a UUID, or a UUID-compatible string"]
    )

    assert await UUIDValidator().validate_async(5.5) == Invalid(
        ["expected a UUID, or a UUID-compatible string"]
    )

    assert await UUIDValidator().validate_async(
        UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222")
    ) == Valid(UUID("e348c1b4-60bd-11ed-a6e9-6ffb14046222"))

    class HexStartsWithF(PredicateAsync[UUID, Serializable]):
        async def validate_async(self, val: UUID) -> bool:
            await asyncio.sleep(0.001)
            return val.hex.startswith("f")

        async def err_async(self, val: UUID) -> Serializable:
            return "doesn't start with f!"

    result = await UUIDValidator(
        preprocessors=[ReverseUUID()], predicates_async=[HexStartsWithF()]
    ).validate_async("e348c1b4-60bd-11ed-a6e9-6ffb14046222")
    assert result == Invalid(["doesn't start with f!"])


def test_sync_call_with_async_predicates_raises_assertion_error() -> None:
    class AsyncWait(PredicateAsync[A, Serializable]):
        async def validate_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

        async def err_async(self, val: A) -> Serializable:
            return "should always succeed??"

    uu_validator = UUIDValidator(predicates_async=[AsyncWait()])
    with pytest.raises(AssertionError):
        uu_validator("whatever")
