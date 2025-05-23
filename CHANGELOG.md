5.0.0 (May 11, 2025)
**Breaking Changes**
- Remove support for Python 3.8 

4.1.1 (Apr 9, 2024)
**Optimization**
- Use `pattern.match(...)` instead of `re.match(pattern, ...)` in `RegexPredicate` and `EmailPredicate`

4.1.0 (Feb 29, 2024)
**Features**
- `ValidationResult.map()` can be used to succinctly convert data contained within `Valid` objects to some other type or value

4.0.0 (Sep 27, 2023)
**Breaking Changes**
- `to_serializable_errs` produces different text, removing assumption that validation input was deserialized from json

**Improvements**
- Allow `to_serializable_errs` to accept callable for next level

3.1.2 (May 4, 2023)
**Bug Fixes**
- [#30](https://github.com/keithasaurus/koda-validate/issues/30) validate_signature ignores validators' coercion and processors

**Maintenance**
- General updates to dev dependencies

3.1.1 (Jan. 28, 2023)
**Bug Fixes**
- `UnionValidator.typed`'s `@overloads` specify that arguments should be positional-only

**Docs**
- extend docs for `UnionValidator` and `NTupleValidator`

3.1.0 (Jan. 26, 2023)
**Features**
- Runtime type checking via `koda_validate.signature.validate_signature`
- Coercion customizable via `Coercer` (and helper decorator `coercer`)

**Maintenance**
- Minor bug fixes in examples/

3.0.0 (Jan. 5, 2023)
**Features**
- Derived Validators: `TypedDictValidator`, `DataclassValidator`, `NamedTupleValidator`
- `UnionValidator` replaces `OneOf2`, `OneOf3`
- `NTupleValidator` replaces `Tuple2Validator`, `Tuple2Validator`
- `UniformTupleValidator`
- `SetValidator`
- `BytesValidator`
- New `Valid`/`Invalid` types
- `MaybeValidator`
- `CacheValidatorBase`
- Errors decoupled from Serialization
- Fewer Generic Arguments needed for `Validator`s, `Predicate`s and `PrediateAsync`s
- `koda_validate.serialization.to_json_schema`

**Removals**
- `OneOf2`
- `OneOf3`
- `Tuple2Validator`
- `Tuple3Validator`

**Breaking Changes**
- `UnionValidator` replaces `OneOf2`, `OneOf3`
- `NTupleValidator` replaces `Tuple2Validator`, `Tuple2Validator` 
- New `Valid`/`Invalid` types -- need `koda_validate.to_serializable_errs` to produce serializable errors

**Performance**
- Various optimizations in dictionary `Validator`s
- Optimizations in scalar validators (StringValidator, IntValidator, etc.) for common use cases
- Overall speedups of around 30% for common validation cases
- More benchmarks

**Maintenance**
- New Docs Site
- Restructure project layout
  - _internal.py
  - move serialization to koda_validate.serialization
- More benchmarks

2.1.0 (Nov. 9, 2022)
**Features**
- `UUIDValidator`

**Bug Fixes**
- `RecordValidator` allows up-to-16 keys as intended

**Performance**
- Small optimizations for `RecordValidator`, `DictValidatorAny`, `ListValidator` and `DecimalValidator`

2.0.0 (Nov. 8, 2022)
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
- `RecordValidator` accepts up-to 16 keys
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