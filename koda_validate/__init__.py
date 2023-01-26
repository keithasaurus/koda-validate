import importlib.metadata

__version__ = importlib.metadata.version("koda_validate")

__all__ = (
    # base.py
    "Validator",
    "Predicate",
    "PredicateAsync",
    "Processor",
    # boolean.py
    "BoolValidator",
    # bytes.py
    # coerce.py
    "Coercer",
    "coercer",
    "BytesValidator",
    # dataclasses.py
    "DataclassValidator",
    # decimal.py
    "DecimalValidator",
    # dictionary.py
    "KeyNotRequired",
    "MapValidator",
    "is_dict_validator",
    "IsDictValidator",
    "MinKeys",
    "MaxKeys",
    "RecordValidator",
    "DictValidatorAny",
    # errors.py
    "CoercionErr",
    "ContainerErr",
    "ExtraKeysErr",
    "ErrType",
    "IndexErrs",
    "KeyErrs",
    "KeyValErrs",
    "MapErr",
    "MissingKeyErr",
    "missing_key_err",
    "PredicateErrs",
    "SetErrs",
    "TypeErr",
    "UnionErrs",
    "ValidationErrBase",
    # float.py
    "FloatValidator",
    # generic.py
    "Lazy",
    "Choices",
    "Min",
    "Max",
    "MinItems",
    "MaxItems",
    "ExactItemCount",
    "unique_items",
    "UniqueItems",
    "MultipleOf",
    "EqualsValidator",
    "EqualTo",
    "always_valid",
    "AlwaysValid",
    "MinLength",
    "MaxLength",
    "ExactLength",
    "StartsWith",
    "EndsWith",
    "strip",
    "not_blank",
    "NotBlank",
    "upper_case",
    "UpperCase",
    "lower_case",
    "LowerCase",
    "CacheValidatorBase",
    # integer.py
    "IntValidator",
    # list.py
    "ListValidator",
    # namedtuple.py
    "NamedTupleValidator",
    # none.py
    "OptionalValidator",
    "NoneValidator",
    "none_validator",
    # set.py
    "SetValidator",
    # string.py
    "StringValidator",
    "RegexPredicate",
    "EmailPredicate",
    # time.py
    "DateValidator",
    "DatetimeValidator",
    # tuple.py
    "NTupleValidator",
    "UniformTupleValidator",
    # typeddict.py
    "TypedDictValidator",
    # uuid.py
    "UUIDValidator",
    # union.py
    "UnionValidator",
    # valid.py
    "Valid",
    "Invalid",
    "ValidationResult",
)

from koda_validate.base import (
    CacheValidatorBase,
    Predicate,
    PredicateAsync,
    Processor,
    Validator,
)
from koda_validate.boolean import BoolValidator
from koda_validate.bytes import BytesValidator
from koda_validate.coerce import Coercer, coercer
from koda_validate.dataclasses import DataclassValidator
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import (
    DictValidatorAny,
    IsDictValidator,
    KeyNotRequired,
    MapValidator,
    MaxKeys,
    MinKeys,
    RecordValidator,
    is_dict_validator,
)
from koda_validate.errors import (
    CoercionErr,
    ContainerErr,
    ErrType,
    ExtraKeysErr,
    IndexErrs,
    KeyErrs,
    KeyValErrs,
    MapErr,
    MissingKeyErr,
    PredicateErrs,
    SetErrs,
    TypeErr,
    UnionErrs,
    ValidationErrBase,
    missing_key_err,
)
from koda_validate.float import FloatValidator
from koda_validate.generic import (
    AlwaysValid,
    Choices,
    EndsWith,
    EqualsValidator,
    EqualTo,
    ExactItemCount,
    ExactLength,
    Lazy,
    LowerCase,
    Max,
    MaxItems,
    MaxLength,
    Min,
    MinItems,
    MinLength,
    MultipleOf,
    NotBlank,
    StartsWith,
    UniqueItems,
    UpperCase,
    always_valid,
    lower_case,
    not_blank,
    strip,
    unique_items,
    upper_case,
)
from koda_validate.integer import IntValidator
from koda_validate.list import ListValidator
from koda_validate.namedtuple import NamedTupleValidator
from koda_validate.none import NoneValidator, OptionalValidator, none_validator
from koda_validate.set import SetValidator
from koda_validate.string import EmailPredicate, RegexPredicate, StringValidator
from koda_validate.time import DatetimeValidator, DateValidator
from koda_validate.tuple import NTupleValidator, UniformTupleValidator
from koda_validate.typeddict import TypedDictValidator
from koda_validate.union import UnionValidator
from koda_validate.uuid import UUIDValidator
from koda_validate.valid import Invalid, Valid, ValidationResult
