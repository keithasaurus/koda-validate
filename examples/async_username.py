import asyncio

from koda_validate import *


class IsActiveUsername(PredicateAsync[str, Serializable]):
    async def is_valid_async(self, val: str) -> bool:
        # add some latency to pretend we're calling the db
        await asyncio.sleep(0.01)

        return val in {"michael", "gob", "lindsay", "buster"}

    async def err_async(self, val: str) -> Serializable:
        return "invalid username"


username_validator = StringValidator(
    MinLength(1), MaxLength(100), predicates_async=[IsActiveUsername()]
)

assert asyncio.run(username_validator.validate_async("michael")) == Valid("michael")
assert asyncio.run(username_validator.validate_async("tobias")) == Invalid(
    ["invalid username"]
)

# calling in sync mode raises an AssertionError!
try:
    username_validator("michael")
except AssertionError as e:
    print(e)


username_list_validator = ListValidator(username_validator)

assert asyncio.run(
    username_list_validator.validate_async(["michael", "gob", "lindsay", "buster"])
) == Valid(["michael", "gob", "lindsay", "buster"])
