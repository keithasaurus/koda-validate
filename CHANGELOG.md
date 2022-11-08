2.0.0 (Nov. 8 2022)
**Features**
- `asyncio` is supported with `.validate_async` method
- `PredicateAsync` is added
- `RecordValidator` (and `DictValidatorAny`) can now handle any kind of dict key.
- `AlwaysValid` is added
- `Predicate`s and `Processor`s are allowed more extensively across built-in validators.


**Performance**
- speed has improved as much as 60x (Koda Validate is now significantly faster than Pydantic)

**Breaking Changes**
- `Ok` / `Err` / `Result` (from `koda`) -> `Valid` / `Invalid` / `Result` (from `koda_validate`) 
- `dict_validator` -> `RecordValidator`
- `DictNKeysValidator`s are removed. Instead, `RecordValidator` is used.
- `RecordValidator` requires all arguments as keyword-only
- `RecordValidator` accepts up-to 10 keys
- `key` helper is removed
- `maybe_key` helper is replaced by `KeyNotRequired`
- `MapValidator` requires all arguments as keyword-only
- `ListValidator` requires `Predicate`s to be specified as a keyword argument
- the order and number of some `__match_args__` has changed
- most validators are not longer dataclasses; `__repr__`s may differ
- `validate_and_map` is deprecated and removed from `koda_validate` imports.
- file structure has changed
  - typedefs.py -> base.py
  - utils.py -> _internals.py

**Maintenance**
- `bench` folder is added for benchmarks
- `python3.11` added to CI
- `pypy3.9` added to CI
- min coverage bumped to 95%
- lots of tests added

1.0.0 - Initial Release
:)