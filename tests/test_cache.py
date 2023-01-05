from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import pytest
from koda import Just, Maybe, nothing

from koda_validate import (
    Invalid,
    StringValidator,
    TypeErr,
    Valid,
    ValidationResult,
    not_blank,
)
from koda_validate._generics import A
from koda_validate.base import CacheValidatorBase


def test_cache_validator_sync() -> None:
    hits: List[Tuple[Any, Any]] = []

    @dataclass
    class DictCacheValidator(CacheValidatorBase[A]):
        _dict_cache: Dict[Any, ValidationResult[A]] = field(default_factory=dict)

        def cache_get_sync(self, val: Any) -> Maybe[ValidationResult[A]]:
            if val in self._dict_cache:
                cached_val = self._dict_cache[val]
                hits.append((val, cached_val))
                return Just(cached_val)
            else:
                return nothing

        def cache_set_sync(self, val: Any, cache_val: ValidationResult[A]) -> None:
            self._dict_cache[val] = cache_val

    cache_str_validator = DictCacheValidator(StringValidator(not_blank))

    assert cache_str_validator("ok") == Valid("ok")
    assert hits == []

    # should hit
    assert cache_str_validator("ok") == Valid("ok")
    assert hits == [("ok", Valid("ok"))]

    assert cache_str_validator("ok") == Valid("ok")
    assert hits == [
        ("ok", Valid("ok")),
        ("ok", Valid("ok")),
    ]

    assert cache_str_validator(5) == Invalid(
        TypeErr(str), 5, cache_str_validator.validator
    )

    assert hits == [
        ("ok", Valid("ok")),
        ("ok", Valid("ok")),
    ]

    assert cache_str_validator(5) == Invalid(
        TypeErr(str), 5, cache_str_validator.validator
    )

    assert hits == [
        ("ok", Valid("ok")),
        ("ok", Valid("ok")),
        (5, Invalid(TypeErr(str), 5, cache_str_validator.validator)),
    ]


@pytest.mark.asyncio
async def test_cache_validator_sync() -> None:
    hits: List[Tuple[Any, Any]] = []

    @dataclass
    class DictCacheValidator(CacheValidatorBase[A]):
        _dict_cache: Dict[Any, ValidationResult[A]] = field(default_factory=dict)

        async def cache_get_async(self, val: Any) -> Maybe[ValidationResult[A]]:
            if val in self._dict_cache:
                cached_val = self._dict_cache[val]
                hits.append((val, cached_val))
                return Just(cached_val)
            else:
                return nothing

        async def cache_set_async(self, val: Any, cache_val: ValidationResult[A]) -> None:
            self._dict_cache[val] = cache_val

    cache_str_validator = DictCacheValidator(StringValidator(not_blank))

    assert await cache_str_validator.validate_async("ok") == Valid("ok")
    assert hits == []

    # should hit
    assert await cache_str_validator.validate_async("ok") == Valid("ok")
    assert hits == [("ok", Valid("ok"))]

    assert await cache_str_validator.validate_async("ok") == Valid("ok")
    assert hits == [
        ("ok", Valid("ok")),
        ("ok", Valid("ok")),
    ]

    assert await cache_str_validator.validate_async(5) == Invalid(
        TypeErr(str), 5, cache_str_validator.validator
    )

    assert hits == [
        ("ok", Valid("ok")),
        ("ok", Valid("ok")),
    ]

    assert await cache_str_validator.validate_async(5) == Invalid(
        TypeErr(str), 5, cache_str_validator.validator
    )

    assert hits == [
        ("ok", Valid("ok")),
        ("ok", Valid("ok")),
        (5, Invalid(TypeErr(str), 5, cache_str_validator.validator)),
    ]
