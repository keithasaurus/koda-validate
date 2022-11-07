import asyncio

from koda_validate import *

short_string_validator = StringValidator(MaxLength(10))

assert short_string_validator("sync") == Valid("sync")

# we're not in an async context, so we can't use `await` here
assert asyncio.run(short_string_validator.validate_async("async")) == Valid("async")
