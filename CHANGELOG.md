2.0.0 (Nov. 8 2022)
**Features**
- `asyncio` is supported with `.validate_async` method

**Performance**
- speed has improved as much as 60x (Koda Validate is now significantly faster than Pydantic)

**Breaking Changes**
- `Ok` / `Err` / `Result` -> `Valid` / `Invalid` / `Result` as validator return types
- `dict_validator` -> `RecordValidator`
- `DictNKeysValidator`s are removed. Instead, `RecordValidator` is used.
- `RecordValidator` requires all arguments as keyword-only
- `RecordValidator` accepts up-to 10 keys
- `key` helper is removed
- `maybe_key` helper is replaced by `KeyNotRequired`
- `MapValidator` requires all arguments as keyword-only
- `ListValidator` requires `Predicate`s to be specified as a keyword argument
- the order and number of some `__match_args__` has changed 

1.0.0 - Initial Release
:)